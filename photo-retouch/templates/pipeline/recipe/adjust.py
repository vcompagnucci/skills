"""Luz y color del editor: la referencia en numpy que el shader del navegador copia linea por linea.

Los ajustes van de -100 a 100, salvo la exposicion (de -2 a 2 pasos), y en 0 no hacen nada. Con todos
en 0 el servidor no pasa por aca: la exportacion sale identica a la maestra.

El orden, el mismo en el shader (ADJUST en recipe/viewer_template.html):
1. Temperatura y tinte: una ganancia por canal en luz lineal, normalizada para que un gris no cambie de luz.
2. Exposicion: 2^EV en luz lineal.
3. La curva de tono, sobre L*/100 de cada canal y con el tono (hue) protegido: se calcula para el canal
   mas alto y el mas bajo, y el del medio queda en la misma proporcion entre los dos (el RGB tone del
   DNG SDK). Si un canal puede pasar de 1, un hombro suave lo deja justo en 1 en vez de quemarlo.
   Despues: contraste (una S con pivote en L* 50), altas luces y sombras (lomas suaves), blancos y
   negros (mueven las puntas) y brillo (medios tonos). Cada curva es monotona: nunca invierte un tono.
4. Saturacion y vibrancia: escalan el croma en Oklab; la vibrancia empuja mas lo que tiene poco color.
5. Lo que quede fuera del gamut se acerca al gris de su misma luminancia, sin cambiar el tono.
"""

import math
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from common import LUMA, linear_to_srgb

KEYS = ("exposure", "brightness", "contrast", "highlights", "shadows", "whites", "blacks",
        "temperature", "tint", "vibrance", "saturation")
TONE = ("brightness", "contrast", "highlights", "shadows", "whites", "blacks")
EXPOSURE = 2.0  # pasos para cada lado; el resto va de -100 a 100

TEMP = 0.2  # a +-100 el rojo y el azul ganan e^(+-0.2): el rojo sobre el azul cambia x1.49
TINT = 0.1  # a +-100 el verde gana e^(-+0.1); + es magenta, como en Lightroom
KNEE = 0.6  # el hombro: cuanto baja la rodilla cuando un canal puede pasar de 1
CONTRAST = 0.55  # pendiente de la S en L* 50: 1.55 a +100, 0.45 a -100
BUMP = 0.15  # altas luces y sombras: cuanto sube o baja la cima de la loma, en L*/100
SHADOWS_TO, HIGHLIGHTS_FROM = 0.6, 0.4  # las sombras van de 0 a 0.6; las altas luces, de 0.4 a 1
ENDS = 0.15  # blancos y negros: cuanto se mueve cada punta
VIBRANCE_C = 0.25  # croma de Oklab desde el que la vibrancia ya no empuja
STRIP = 128  # filas por tanda en la exportacion: la foto entera en float32 son 300 MB

TO_LINEAR = (lambda v: np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4))(
    np.arange(65536, dtype=np.float64) / 65535
).astype(np.float32)  # de uint16 sRGB a luz lineal, sin temporales de 26 MP

_LMS = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                 [0.2119034982, 0.6806995451, 0.1073969566],
                 [0.0883024619, 0.2817188376, 0.6299787005]], np.float32)
_LAB = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                 [1.9779984951, -2.4285922050, 0.4505937099],
                 [0.0259040371, 0.7827717662, -0.8086757660]], np.float32)
_LAB_INV = np.array([[1.0, 0.3963377774, 0.2158037573],
                     [1.0, -0.1055613458, -0.0638541728],
                     [1.0, -0.0894841775, -1.2914855480]], np.float32)
_LMS_INV = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                     [-1.2684380046, 2.6097574011, -0.3413193965],
                     [-0.0041960863, -0.7034186147, 1.7076147010]], np.float32)


def parse(raw) -> dict[str, float]:
    """Lo que manda el navegador, validado. Lo que falta vale 0; fuera de rango o no numerico, ValueError."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict) or set(raw) - set(KEYS):
        raise ValueError("ajustes invalidos")
    out = {}
    for k in KEYS:
        v = raw.get(k, 0)
        limit = EXPOSURE if k == "exposure" else 100
        if type(v) not in (int, float) or not math.isfinite(v) or not -limit <= v <= limit:  # True no pasa
            raise ValueError("ajustes invalidos")
        out[k] = float(v)
    return out


def is_neutral(params: dict) -> bool:
    return all(not params.get(k) for k in KEYS)


def unit(params: dict) -> dict[str, float]:
    """A -1..1; la exposicion queda en pasos."""
    return {k: float(params.get(k) or 0) / (1 if k == "exposure" else 100) for k in KEYS}


def gains(temperature: float, tint: float) -> np.ndarray:
    """Ganancias de temperatura y tinte (-1..1), normalizadas: un gris sale con la misma luminancia."""
    g = np.exp(np.array([TEMP * temperature, -TINT * tint, -TEMP * temperature]))
    return (g / (LUMA.astype(np.float64) @ g)).astype(np.float32)


def to_x(v):
    """Luz lineal de un canal -> L*/100."""
    v = np.maximum(v, 0)
    return np.where(v > 216 / 24389, 1.16 * np.cbrt(v) - 0.16, v * (24389 / 2700))


def from_x(x):
    """L*/100 -> luz lineal."""
    return np.where(x > 0.08, ((x + 0.16) / 1.16) ** 3, x * (2700 / 24389))


def smoothstep(a: float, b: float, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def bump(u):
    """La loma: 0 en las puntas, 1 en el medio, sin quiebres."""
    u = np.clip(u, 0, 1)
    return 16 * u * u * (1 - u) * (1 - u)


def tone(x, p: dict, top: float):
    """La curva de tono sobre L*/100. top: L*/100 del canal mas alto posible; si pasa de 1, el hombro
    lo trae a 1 sin quiebre (pendiente 1 en la rodilla)."""
    if top > 1:
        k = 1 - KNEE * (top - 1) / top
        s = (top - k) / (1 - k)
        u = np.clip((x - k) / (top - k), 0, 1)
        x = np.where(x > k, k + (1 - k) * (1 - (1 - u) ** s), x)
    if p["contrast"]:
        x = x - p["contrast"] * CONTRAST * np.sin(2 * np.pi * x) / (2 * np.pi)
    if p["highlights"]:
        x = x + p["highlights"] * BUMP * bump((x - HIGHLIGHTS_FROM) / (1 - HIGHLIGHTS_FROM))
    if p["shadows"]:
        x = x + p["shadows"] * BUMP * bump(x / SHADOWS_TO)
    if p["whites"]:
        x = x + p["whites"] * ENDS * smoothstep(0.5, 1, x)
    if p["blacks"]:
        x = x + p["blacks"] * ENDS * (1 - smoothstep(0, 0.5, x))
    x = np.clip(x, 0, 1)
    r = 2 ** p["brightness"]
    if r != 1:
        x = x * r / (1 + (r - 1) * x)
    return x


def oklab(c: np.ndarray) -> np.ndarray:
    return np.cbrt(c @ _LMS.T) @ _LAB.T


def oklab_to_linear(lab: np.ndarray) -> np.ndarray:
    return ((lab @ _LAB_INV.T) ** 3) @ _LMS_INV.T


def chroma(c: np.ndarray, saturation: float, vibrance: float) -> np.ndarray:
    lab = oklab(c)
    f = np.float32(1 + saturation)
    if vibrance:
        C = np.hypot(lab[..., 1], lab[..., 2])
        f = f * (1 + vibrance * np.clip(1 - C / VIBRANCE_C, 0, 1) ** 2)
        f = f[..., None]
    lab[..., 1:] *= f
    return oklab_to_linear(lab)


def gamut(c: np.ndarray) -> np.ndarray:
    """Lo que se sale de 0..1 se acerca al gris de su misma luminancia, lo justo para entrar."""
    y = np.clip(c @ LUMA, 0, 1)[..., None]
    d = c - y
    with np.errstate(divide="ignore", invalid="ignore"):
        up = np.where(d > 1e-7, (1 - y) / d, np.inf)
        down = np.where(d < -1e-7, y / -d, np.inf)
    t = np.minimum(1, np.minimum(up, down).min(-1, keepdims=True))
    return np.clip(y + d * t, 0, 1)


def adjust(lin: np.ndarray, params: dict) -> np.ndarray:
    """lin: float32 (..., 3), luz lineal en 0..1. Devuelve lo mismo, con los ajustes y dentro de 0..1."""
    p = unit(params)
    g = gains(p["temperature"], p["tint"]) * np.float32(2 ** p["exposure"])
    c = (lin * g).astype(np.float32)
    top = float(g.max())
    if top > 1 or any(p[k] for k in TONE):
        top_x = float(to_x(top))
        hi, lo = c.max(-1, keepdims=True), c.min(-1, keepdims=True)
        hi2, lo2 = from_x(tone(to_x(hi), p, top_x)), from_x(tone(to_x(lo), p, top_x))
        span = hi - lo
        t = np.where(span > 1e-7, (c - lo) / np.maximum(span, 1e-7), 1)
        c = (lo2 + (hi2 - lo2) * t).astype(np.float32)
    if p["saturation"] or p["vibrance"]:
        c = chroma(c, p["saturation"], p["vibrance"])
    return gamut(c).astype(np.float32)


def _tables(p: dict, g: np.ndarray, tone_on: bool) -> tuple[np.ndarray, np.ndarray | None]:
    """Por canal, de codigo uint16 a luz lineal con la ganancia (la misma cuenta que adjust) y, si hay
    curva, a luz lineal ya tonada. La curva es monotona, asi que la del canal mas alto es la mas alta de
    las tres: alcanza con buscar cada canal en su tabla."""
    val = TO_LINEAR[None, :] * g[:, None]
    if not tone_on:
        return val, None
    top_x = float(to_x(float(g.max())))
    ton = np.stack([from_x(tone(to_x(v), p, top_x)) for v in val]).astype(np.float32)
    assert (np.diff(ton, axis=1) >= -1e-6).all(), "la curva de tono dejo de ser monotona"
    return val, ton


def _out_table() -> np.ndarray:
    """De la raiz de la luz lineal (0..1, en OUT_N pasos) al codigo uint16 sRGB ya redondeado. La raiz
    reparte los pasos donde la curva sRGB es empinada: el error queda bajo 1 nivel de 65535."""
    s = np.arange(OUT_N, dtype=np.float64) / (OUT_N - 1)
    return (linear_to_srgb(s * s).astype(np.float64) * 65535 + 0.5).astype(np.uint16)


OUT_N = 1 << 18
_OUT = None


def _combo(m: np.ndarray, a, b, c) -> tuple:
    """m @ (a, b, c) por planos: sin el producto matricial sobre (H, W, 3)."""
    return tuple(m[i, 0] * a + m[i, 1] * b + m[i, 2] * c for i in range(3))


def _strip(src: np.ndarray, dst: np.ndarray, p: dict, val, ton) -> None:
    """Una tanda de filas: lo mismo que adjust, por planos y con tablas."""
    idx = [src[..., i] for i in range(3)]
    c = [val[i][idx[i]] for i in range(3)]
    if ton is not None:
        hi, lo = np.maximum(np.maximum(c[0], c[1]), c[2]), np.minimum(np.minimum(c[0], c[1]), c[2])
        t = [ton[i][idx[i]] for i in range(3)]
        hi2, lo2 = np.maximum(np.maximum(t[0], t[1]), t[2]), np.minimum(np.minimum(t[0], t[1]), t[2])
        del t
        span = hi - lo
        flat = span <= 1e-7  # gris: los tres canales van a la curva del mas alto
        np.maximum(span, np.float32(1e-7), out=span)
        hi2 -= lo2
        for i in range(3):  # las mismas cuentas que adjust, en el mismo orden: el gamut estira cualquier diferencia
            x = c[i] - lo
            x /= span
            np.copyto(x, 1, where=flat)
            x *= hi2
            x += lo2
            c[i] = x
        del hi, lo, hi2, lo2, span, flat
    if p["saturation"] or p["vibrance"]:
        before = c
        lms = [np.cbrt(v) for v in _combo(_LMS, *c)]
        L, A, B = _combo(_LAB, *lms)
        del lms
        f = np.float32(1 + p["saturation"])
        if p["vibrance"]:
            C = np.hypot(A, B)
            C *= np.float32(-1 / VIBRANCE_C)
            C += 1
            np.clip(C, 0, 1, out=C)
            C *= C
            C *= np.float32(p["vibrance"])
            C += 1
            C *= f
            f = C
        A *= f
        B *= f
        cubes = [v * v * v for v in _combo(_LAB_INV, L, A, B)]
        del L, A, B, f
        c = list(_combo(_LMS_INV, *cubes))
        del cubes
        # fuera del gamut: esos pixeles se rehacen con chroma() y gamut(), en las mismas cuentas que adjust;
        # gamut() estira el error de redondeo de float32 y por planos se iria a 8 niveles. El resto ya esta en 0..1
        out = (np.minimum(np.minimum(c[0], c[1]), c[2]) < 0) | (np.maximum(np.maximum(c[0], c[1]), c[2]) > 1)
        if out.any():
            fixed = gamut(chroma(np.stack([v[out] for v in before], -1), p["saturation"], p["vibrance"]))
            for i in range(3):
                c[i][out] = fixed[:, i]
        del before
    for i in range(3):
        x = np.clip(c[i], 0, 1, out=c[i])
        np.sqrt(x, out=x)
        x *= np.float32(OUT_N - 1)
        x += np.float32(0.5)
        dst[..., i] = _OUT[x.astype(np.int32)]


def adjust_uint16(img: np.ndarray, params: dict) -> np.ndarray:
    """img: uint16 RGB en sRGB (la maestra o un recorte). Devuelve uint16 sRGB con los ajustes, por tandas de
    filas en dos hilos (numpy suelta el GIL). Neutro: la misma imagen, sin tocar un bit.

    Es adjust() mas linear_to_srgb, a 2 niveles de 65535 como mucho (1 en las fotos; 2 en pixeles al azar,
    por redondeo de float32): la ganancia y la curva van en tablas de 65536 por canal, los productos 3x3 por
    planos y la salida a sRGB por la tabla de _out_table. La foto entera, con todo movido: ~1.2 s."""
    global _OUT
    if is_neutral(params):
        return img
    if _OUT is None:
        _OUT = _out_table()
    p = unit(params)
    g = gains(p["temperature"], p["tint"]) * np.float32(2 ** p["exposure"])
    val, ton = _tables(p, g, float(g.max()) > 1 or any(p[k] for k in TONE))
    out = np.empty_like(img)
    rows = range(0, img.shape[0], STRIP)
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda y: _strip(img[y : y + STRIP], out[y : y + STRIP], p, val, ton), rows))
    return out
