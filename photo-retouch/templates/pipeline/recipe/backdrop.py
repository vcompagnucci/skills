"""El fondo con parametros: la carpeta Background del editor, aplicada solo a la pared.

El fotografo (2026-10-15): el fondo de un estilo no se pinta, sale de mover parametros como la temperatura o el
brillo. Es lo que hace un retocador en Lightroom con "Select background" y un ajuste local: la mascara
la da el matting (matte.py) y seis controles dicen que hacerle a la pared.

- Exposure, de -2 a 2 pasos: como el de la foto, en luz lineal.
- Evenness, de 0 a 100: cuanto se aplana la luz de la pared hacia su parte mas clara (el p98 de la luz).
  En 100, la pared queda pareja.
- Smoothing, de 0 a 100: cuanto se aplanan las franjas y arrugas del papel (el fotografo, 2026-10-17: "noto una linea"). La
  pared de atras es la pared pura promediada a 12 px y la luz de la pared a ~170: su cociente, en la parte de pared,
  saca lo que hay entre esas dos escalas y deja el grano, que es mas chico (papel_piloto.py: grano 0,43 L* antes y
  despues). En 100, el papel queda sin franjas; la luz ancha (Evenness, Falloff) no la toca.
- Falloff, de 0 a 100: cuanto cae la pared hacia la derecha, lejos de la luz principal (las cuatro la
  tienen a la izquierda). En 100, la caida que mide la de Apple: hasta 64 L* en el borde, desde el 35 %
  del ancho y con potencia 1,82 (78, 49 y 25 L* de la luz a la sombra).
- Temperature y Tint, de -100 a 100: las mismas ganancias que la temperatura y el tinte de la foto
  (adjust.gains), relativas al color que ya tiene la pared.
- Saturation, de -100 a 100: el color propio de la pared. En -100 queda gris neutro, y Temperature y Tint
  le dan el color desde ahi: abajo, cerca del piso, la pared de estas fotos es tibia (el rebote del piso),
  y sin esto el blanco salia crema en esa zona (piloto de los parametros).

El orden, el mismo en el shader (backdrop() en recipe/viewer_template.html): primero la foto entera con
los ajustes del panel (adjust.py) y despues el fondo, sobre la foto ya ajustada. El alpha, la pared de
atras y la luz de la pared salen una sola vez de la maestra sin ajustar (make_layers); en cada render
pasan por los mismos ajustes que la foto:

    c = adjust(I)                         la foto con sus ajustes
    W = min((1 - a) adjust(B), c)         la parte de pared del pixel; en la pared pura, c entero
    L = L*(adjust(luz))                   la luz de la pared, ajustada como la foto
    L -> exposicion -> parejo -> caida    el L* buscado
    g *= (Y luz / Y atras) ** suavizado   las franjas del papel (Smoothing)
    g = Y buscado / Y luz * (luz con su saturacion / luz) * ganancias(temperatura, tinte)
    salida = c + (g - 1) W                (Smith y Blinn 1996: la ganancia va solo a la parte de pared)

Donde a = 1 la salida es c: la gente queda como la deja el panel, y la pared no la toca.

Las capas, en editadas/fondo/:
- <foto>-capa.png: PNG RGBA de 16 bits al tamano nativo. RGB, la pared de atras (sRGB); A, el alpha. A = 0
  marca la pared pura, donde la pared de atras es el pixel mismo, con su grano; todo pixel a RING px o
  menos de la gente lleva A >= 257, asi el navegador, que lo lee a 8 bits, ve el mismo limite.
- <foto>-luz.png: la luz de la pared a LO del tamano, RGB de 16 bits.
El editor lee ademas editadas/pantalla/<foto>-capa.png: la misma capa a la escala de pantalla, a 8 bits.
"""

import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from adjust import TO_LINEAR, adjust, adjust_uint16, from_x, gains, to_x
from adjust import is_neutral as tone_neutral
from common import EDITED, LUMA, linear_to_srgb, to_uint16
from matte import NATIVE

KEYS = ("exposure", "evenness", "smoothing", "falloff", "temperature", "tint", "saturation")
RANGE = {"exposure": (-2.0, 2.0), "evenness": (0.0, 100.0), "smoothing": (0.0, 100.0), "falloff": (0.0, 100.0),
         "temperature": (-100.0, 100.0), "tint": (-100.0, 100.0), "saturation": (-100.0, 100.0)}
FALL_FROM, FALL_POW, FALL_MAX = 0.35, 1.82, 64.0
TOP = 98  # percentil de la luz de la pared que Evenness deja quieto
L_MIN = 1.0  # L* minimo de la pared: la caida no la lleva a negro puro

LO = 1 / 16  # la luz de la pared se mide a esta escala: es suave por construccion
WALL_SIGMA = 0.04  # escala de la luz de la pared, en fraccion del lado corto (~170 px nativos)
WALL_MARGIN = 0.01  # margen alrededor de la gente que no cuenta para medirla
EDGE = 0.02  # alpha desde el que un pixel tiene gente
RING = 2  # px nativos alrededor de la gente donde la pared de atras es la de al lado, no el pixel
STRIP = 128  # filas por tanda: la foto entera en float32 son 300 MB por imagen
THREADS = 4  # tandas a la vez (numpy suelta el GIL): los 4 nucleos de rendimiento; cada tanda da lo mismo sola o en grupo
LAYERS = EDITED / "fondo"


def parse(raw) -> dict[str, float]:
    """Lo que manda el navegador, validado. Lo que falta vale 0; fuera de rango o no numerico, ValueError."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict) or set(raw) - set(KEYS):
        raise ValueError("fondo invalido")
    out = {}
    for k in KEYS:
        v = raw.get(k, 0)
        lo, hi = RANGE[k]
        if type(v) not in (int, float) or not math.isfinite(v) or not lo <= v <= hi:  # True no pasa
            raise ValueError("fondo invalido")
        out[k] = float(v)
    return out


def is_neutral(params: dict) -> bool:
    return all(not params.get(k) for k in KEYS)


# --- las capas: de la maestra sin ajustar, una vez por foto ---------------------------------------


def wall_light(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """La luz de la pared, RGB lineal a LO: promedio de la pared pura a escala ancha.

    Sin la gente ni un margen alrededor: con el pelo semitransparente adentro, la estimacion se
    oscurecia junto a la cabeza y quedaba un aura (estudio, QA v4). Donde la gente tapa todo el
    entorno se extrapola desde mas lejos.
    """
    h, w = alpha.shape
    size = (max(1, round(w * LO)), max(1, round(h * LO)))
    a_lo = cv2.resize(alpha, size, interpolation=cv2.INTER_AREA)
    short = min(size)
    r = max(1, round(WALL_MARGIN * short))  # el margen, en px de LO
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
    ws = 1.0 - cv2.dilate((a_lo > 0.02).astype(np.uint8), k).astype(np.float32)
    small = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA) * ws[..., None]
    sigma = WALL_SIGMA * short
    den = cv2.GaussianBlur(ws, (0, 0), sigma)
    near = cv2.GaussianBlur(small, (0, 0), sigma) / np.maximum(den, 1e-4)[..., None]
    wide = cv2.GaussianBlur(small, (0, 0), 4 * sigma) / np.maximum(cv2.GaussianBlur(ws, (0, 0), 4 * sigma), 1e-4)[..., None]
    cover = np.clip(den / 0.15, 0, 1)[..., None]
    return (cover * near + (1 - cover) * wide).astype(np.float32)


def wall_behind(rgb: np.ndarray, alpha: np.ndarray, light: np.ndarray) -> np.ndarray:
    """La pared detras de cada pixel: promedio de la pared pura de al lado (estudio, styles.py).

    Pared pura = alpha < 0.01 y a 4 px nativos o mas del borde. Promedio gaussiano de 12 px;
    donde no hay pared cerca (bajo el pelo, el cuello contra el hombro), uno de 120 px; y donde
    tampoco (un hueco chico entre el brazo y el cuerpo, lejos de la pared abierta), la luz de la
    pared (`light`, a LO). Sin esa ultima, en el hueco de la foto de grupo la pared de atras daba 0 y el blanco
    no lo tocaba (piloto de los parametros).
    """
    h, w = alpha.shape
    unit = min(h, w) / NATIVE
    r = max(1, int(round(4 * unit)))
    pure = cv2.erode((alpha < 0.01).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2))
    pure = pure.astype(np.float32)
    k = 512 / min(h, w)
    size = (round(w * k), round(h * k))
    small = cv2.resize(rgb * pure[..., None], size, interpolation=cv2.INTER_AREA)
    ws = cv2.resize(pure, size, interpolation=cv2.INTER_AREA)
    sw = 120 * 512 / NATIVE
    den_w = cv2.GaussianBlur(ws, (0, 0), sw)
    wide = cv2.GaussianBlur(small, (0, 0), sw) / np.maximum(den_w, 1e-4)[..., None]
    cover_w = np.clip(den_w / 0.15, 0, 1)[..., None]
    wide = cover_w * wide + (1 - cover_w) * cv2.resize(light, size, interpolation=cv2.INTER_LINEAR)
    wide = cv2.resize(wide, (w, h), interpolation=cv2.INTER_LINEAR)
    sig = max(0.8, 12 * unit)
    den = cv2.GaussianBlur(pure, (0, 0), sig)
    cover = np.clip(den / 0.15, 0, 1)
    out = np.empty(rgb.shape, np.float32)
    for c in range(3):
        num = cv2.GaussianBlur(np.ascontiguousarray(rgb[..., c]) * pure, (0, 0), sig)
        out[..., c] = cover * num / np.maximum(den, 1e-6) + (1 - cover) * wide[..., c]
    return out


@dataclass(frozen=True)
class Layers:
    """Lo que el fondo necesita de una foto. alpha16: 0 = pared pura, 65535 = persona; behind16: la pared de
    atras en sRGB de 16 bits; light: la luz de la pared, RGB lineal a LO; top: el L* que Evenness deja quieto."""

    alpha16: np.ndarray
    behind16: np.ndarray
    light: np.ndarray
    top: float


def edge_alpha16(alpha: np.ndarray) -> np.ndarray:
    """El alpha a 16 bits con el limite de la pared pura adentro: 0 lejos de la gente, y desde RING px de
    cualquier pixel con gente (alpha > EDGE), 257 o mas, que a 8 bits sigue siendo 1 o mas."""
    unit = min(alpha.shape) / NATIVE
    r = max(1, int(round(RING * unit)))
    some = cv2.dilate((alpha > EDGE).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)) > 0
    a16 = (np.clip(alpha, 0, 1) * 65535 + 0.5).astype(np.uint16)
    return np.where(some, np.maximum(a16, 257), 0).astype(np.uint16)


def top_lightness(light: np.ndarray) -> float:
    return float(np.percentile(100 * to_x(light @ LUMA), TOP))


def make_layers(name: str, native: np.ndarray, alpha: np.ndarray) -> Layers:
    """Las capas de una foto desde su maestra nativa (RGB lineal) y su alpha nativo; las escribe y las devuelve."""
    LAYERS.mkdir(parents=True, exist_ok=True)
    a16 = edge_alpha16(alpha)
    light = wall_light(native, alpha)
    behind16 = to_uint16(linear_to_srgb(wall_behind(native, alpha, light)))
    write_png16(LAYERS / f"{name}-capa.png", np.dstack([behind16, a16]))
    write_png16(LAYERS / f"{name}-luz.png", to_uint16(linear_to_srgb(light)))
    light16 = read_png16(LAYERS / f"{name}-luz.png")  # lo mismo que se va a leer despues, ya redondeado
    light = TO_LINEAR[light16]
    return Layers(a16, behind16, light, top_lightness(light))


def write_png16(path: Path, img: np.ndarray) -> None:
    """RGB o RGBA de 16 bits. A medias no queda con la fecha nueva: se escribe aparte y se cambia de una vez."""
    order = [2, 1, 0, 3][: img.shape[2]]
    tmp = path.with_name(f".{path.name}")
    if not cv2.imwrite(str(tmp), np.ascontiguousarray(img[..., order]), [cv2.IMWRITE_PNG_COMPRESSION, 6]):
        raise OSError(f"no se pudo escribir {tmp}")
    tmp.replace(path)


def read_png16(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None or img.dtype != np.uint16:
        raise OSError(f"{path} no es un PNG de 16 bits")
    order = [2, 1, 0, 3][: img.shape[2]]
    return np.ascontiguousarray(img[..., order])


def layer_paths(name: str) -> tuple[Path, Path]:
    return LAYERS / f"{name}-capa.png", LAYERS / f"{name}-luz.png"


def load_layers(name: str) -> Layers:
    capa, luz = layer_paths(name)
    rgba = read_png16(capa)
    light = TO_LINEAR[read_png16(luz)]
    return Layers(np.ascontiguousarray(rgba[..., 3]), np.ascontiguousarray(rgba[..., :3]), light, top_lightness(light))


def layers_at(layers: Layers, size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """La capa achicada a (ancho, alto), promediando en luz lineal: alpha16 y behind16. Un pixel que toca la zona
    de la gente sigue fuera de la pared pura (A >= 257)."""
    a = cv2.resize(layers.alpha16.astype(np.float32), size, interpolation=cv2.INTER_AREA)
    b = cv2.resize(TO_LINEAR[layers.behind16], size, interpolation=cv2.INTER_AREA)
    a16 = np.where(a > 0, np.maximum(a + 0.5, 257), 0).astype(np.uint16)
    return a16, to_uint16(linear_to_srgb(b))


# --- el render: la foto ajustada y el fondo encima --------------------------------------------------


def bilinear(n_src: int, n_dst: int, start: int, count: int) -> np.ndarray:
    """(count, n_src): los pesos con que la placa lee una textura de n_src px estirada a n_dst (centros en +0.5,
    el borde repetido), para los px start..start+count de la salida."""
    s = (np.arange(start, start + count, dtype=np.float64) + 0.5) * n_src / n_dst - 0.5
    s = np.clip(s, 0, n_src - 1)
    i0 = np.floor(s).astype(np.int64)
    i1 = np.minimum(i0 + 1, n_src - 1)
    f = (s - i0).astype(np.float32)
    m = np.zeros((count, n_src), np.float32)
    rows = np.arange(count)
    np.add.at(m, (rows, i0), 1 - f)
    np.add.at(m, (rows, i1), f)
    return m


def tone(x: np.ndarray, params: dict) -> np.ndarray:
    return x if tone_neutral(params) else adjust(x, params)


def target(light: np.ndarray, top: float, u: np.ndarray, p: dict) -> np.ndarray:
    """La ganancia de cada pixel de pared, RGB: de la luz de la pared (ya ajustada) a la buscada.

    top: el L* de la parte mas clara de la luz, ya ajustada. u: la posicion de cada columna, 0 a 1."""
    y = np.maximum(light @ LUMA, 1e-6)
    ev = 2 ** p["exposure"]
    L = 100 * to_x(y * ev)
    if p["evenness"]:
        top = 100 * to_x(from_x(top / 100) * ev)
        L = top + (1 - p["evenness"] / 100) * (L - top)
    if p["falloff"]:
        drop = FALL_MAX * np.clip((u - FALL_FROM) / (1 - FALL_FROM), 0, 1) ** FALL_POW
        L = L - p["falloff"] / 100 * drop
    L = np.clip(L, L_MIN, 100)
    g = (from_x(L / 100) / y)[..., None] * gains(p["temperature"] / 100, p["tint"] / 100)
    if p["saturation"]:  # la luz con su color escalado alrededor de su gris: en -100, gris
        k = 1 + p["saturation"] / 100
        g = g * (y[..., None] + k * (light - y[..., None])) / np.maximum(light, 1e-6)
    return g.astype(np.float32)


PAPER = (0.08, 0.2)  # log de la luz ancha sobre la de 12 px: las franjas del papel no pasan de 0,08 y las sombras de la
# gente llegan a 0,7 (bajo el banco de la foto de grupo). Hasta 0,08 se aplana entero; desde 0,2 no se toca: la sombra queda


def paper(d: np.ndarray) -> np.ndarray:
    """Cuanto de una diferencia d (log) es papel: 1 hasta PAPER[0], 0 desde PAPER[1], smoothstep entre medio."""
    t = np.clip((np.abs(d) - PAPER[0]) / (PAPER[1] - PAPER[0]), 0, 1)
    return 1 - t * t * (3 - 2 * t)


def compose(c: np.ndarray, a16: np.ndarray, behind: np.ndarray, light: np.ndarray, top: float, u: np.ndarray, p: dict) -> np.ndarray:
    """La foto ajustada c con el fondo encima. behind y light ya pasaron por los mismos ajustes que c."""
    g = target(light, top, u, p)
    if p["smoothing"]:  # las franjas del papel: la luz ancha sobre la de 12 px, solo lo que es papel
        d = np.log(np.maximum(light @ LUMA, 1e-6) / np.maximum(behind @ LUMA, 1e-6))
        g = g * np.exp(d * paper(d) * p["smoothing"] / 100)[..., None]
    a = (a16.astype(np.float32) / 65535)[..., None]
    wall = np.where((a16 == 0)[..., None], c, np.minimum((1 - a) * behind, c))
    return c + (g - 1) * wall


def toned_top(layers: Layers, params: dict) -> float:
    """El L* que Evenness deja quieto, despues de los ajustes de la foto: el de un gris de esa luz."""
    grey = np.full((1, 3), from_x(layers.top / 100), np.float32)
    return float(100 * to_x(tone(grey, params) @ LUMA)[0])


def render(img16: np.ndarray, x0: int, y0: int, size: tuple[int, int], layers: Layers, params: dict, bg: dict,
           a16: np.ndarray | None = None, behind16: np.ndarray | None = None) -> np.ndarray:
    """El recorte img16 (uint16 sRGB, ojeras incluidas) en (x0, y0) de una foto de size = (alto, ancho), con los
    ajustes del panel y el fondo. Devuelve uint16 sRGB.

    La gente (alpha 1) sale con los mismos codigos que sin fondo (adjust_uint16, o la maestra si no hay
    ajustes); lo demas, de compose() en luz lineal. a16 y behind16: la capa a otra escala (el piloto)."""
    H, W = size
    h, w = img16.shape[:2]
    a16 = layers.alpha16 if a16 is None else a16
    behind16 = layers.behind16 if behind16 is None else behind16
    out = adjust_uint16(img16, params)  # neutro: la misma imagen, sin copiar
    if is_neutral(bg):
        return out
    out = out.copy() if out is img16 else out
    lh, lw = layers.light.shape[:2]
    wx = bilinear(lw, W, x0, w).T.copy()
    u = ((np.arange(x0, x0 + w, dtype=np.float32) + 0.5) / W)[None, :]
    top = toned_top(layers, params)

    def strip(y: int) -> None:
        n = min(STRIP, h - y)
        a = a16[y0 + y : y0 + y + n, x0 : x0 + w]
        wall = a < 65535
        if not wall.any():
            return
        c = tone(TO_LINEAR[img16[y : y + n]], params)
        b = tone(TO_LINEAR[behind16[y0 + y : y0 + y + n, x0 : x0 + w]], params)
        wy = bilinear(lh, H, y0 + y, n)
        light = tone(np.stack([wy @ layers.light[..., k] @ wx for k in range(3)], -1), params)
        o = to_uint16(linear_to_srgb(compose(c, a, b, light, top, u, bg)))
        out[y : y + n][wall] = o[wall]  # cada tanda escribe solo sus filas

    with ThreadPoolExecutor(THREADS) as pool:
        list(pool.map(strip, range(0, h, STRIP)))
    return out
