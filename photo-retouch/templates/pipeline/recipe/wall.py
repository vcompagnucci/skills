"""La pared: sus manchas (para curarlas una por una) y el emparejado de su luz.

- Manchas: lo que en la pared lisa queda mas oscuro que su entorno (marcas, raspones,
  polvo). El detector propone en una hoja (proceso/21-pared); las que se curan quedan
  escritas en photos.py (`wall_marks`), igual que los granos. Un pelo suelto contra la pared
  tambien es "mas oscuro", por eso decide la hoja y no el detector.
- Emparejado: la pared tiene la caida de luz del flash (mas oscura abajo y hacia los
  costados). Se mide con una superficie suave (polinomio de grado 3 sobre el log de la
  luminancia, ajustado solo sobre la pared) y se la empareja a medias, con una ganancia
  igual de suave sobre toda la foto: como un filtro graduado, sin mascara y sin recortar a
  nadie, asi que no puede dejar halos. La luz sobre las caras no cambia.

Uso: .venv/bin/python recipe/wall.py <foto>   -> proceso/21-pared/<foto>-manchas.png
"""

import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import PROCESS, blur, lab, linear_to_srgb, load_linear, luminance, norm_blur, to_uint8
from develop import frac_box
from photos import PHOTOS

EVEN = 0.5  # cuanto de la caida de luz se corrige
EVEN_LIMIT = 0.35  # tope de la correccion, en pasos (EV), para arriba y para abajo
DOWN = 16  # la superficie se mide a 1/16: es suave por construccion
OUT = PROCESS / "21-pared"
TILE_GRAY = 0.45  # gris lineal al que va cada recuadro de la hoja (~0,7 en sRGB)


def wall_level(img: np.ndarray, name: str) -> float:
    return float(np.median([np.median(luminance(img[frac_box(b, img.shape[:2])])) for b in PHOTOS[name]["wall"]]))


def wall_mask(img: np.ndarray, level: float) -> np.ndarray:
    """Pared: clara, neutra y lisa. 0/1 en la resolucion de img."""
    y = luminance(img)
    bright = blur(y, 8.0) > 0.45 * level
    L, a, b = np.moveaxis(lab(blur(img, 4.0) * (0.5 / level)), -1, 0)
    neutral = np.hypot(a, b) < 5
    lg = np.log2(np.maximum(y, 1e-6))
    smooth = np.sqrt(np.maximum(blur(lg**2, 8.0) - blur(lg, 8.0) ** 2, 0)) < 0.08
    return (bright & neutral & smooth).astype(np.float32)


def _poly_terms(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.stack([u**i * v**j for i in range(4) for j in range(4 - i)], -1)


def light_field(img: np.ndarray, name: str) -> np.ndarray:
    """log2 de la luz sobre la pared, como superficie suave, a 1/16 de la resolucion."""
    small = cv2.resize(img, (img.shape[1] // DOWN, img.shape[0] // DOWN), interpolation=cv2.INTER_AREA)
    level = wall_level(img, name)
    m = cv2.erode(wall_mask(small, level), np.ones((5, 5), np.uint8)) > 0.5
    h, w = m.shape
    v, u = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = u / w * 2 - 1, v / h * 2 - 1
    A = _poly_terms(u[m], v[m])
    t = np.log2(np.maximum(luminance(small)[m], 1e-6))
    wts = np.ones_like(t)
    for _ in range(4):  # robusto: marcas, sombras y bordes pesan poco
        coef, *_ = np.linalg.lstsq(A * wts[:, None], t * wts, rcond=None)
        res = t - A @ coef
        s = 1.4826 * np.median(np.abs(res)) + 1e-6
        wts = 1 / np.sqrt(1 + (res / (2 * s)) ** 2)
    return (_poly_terms(u, v) @ coef).astype(np.float32)


def evening_log(field: np.ndarray, name: str) -> np.ndarray:
    """Correccion en pasos (log2), a 1/16: la pared va a medias hacia su nivel a la altura de las caras."""
    h, w = field.shape
    if not PHOTOS[name]["faces"]:  # sin caras no hay altura a la que igualar: la pared queda como esta
        return np.zeros_like(field, dtype=np.float32)
    at_faces = [field[min(int(f["oval"][1] / DOWN), h - 1), min(int(f["oval"][0] / DOWN), w - 1)] for f in PHOTOS[name]["faces"]]
    return np.clip(EVEN * (float(np.mean(at_faces)) - field), -EVEN_LIMIT, EVEN_LIMIT).astype(np.float32)


def evening_gain(img: np.ndarray, name: str) -> np.ndarray:
    """Ganancia lineal a resolucion completa (para multiplicar la foto entera)."""
    g = evening_log(light_field(img, name), name)
    return np.exp2(cv2.resize(g, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)).astype(np.float32)


STAIN_DOWN = 4  # el color de referencia de la pared se mide a 1/4: es suave por construccion
STAIN_SCALE = 48  # px: escala de ese color de referencia (las salpicaduras miden 20-35 px)
STAIN_FENCE = 36  # px de distancia a todo lo que no es pared (gente, pelo suelto, el banco)


def stain_region(small: np.ndarray, level: float) -> np.ndarray:
    """Pared para el color, a 1/STAIN_DOWN: clara y lisa, con algo de color permitido (la mancha
    lo tiene: wall_mask la dejaria afuera), y lejos de todo lo demas."""
    y = luminance(small)
    bright = blur(y, 2.0) > 0.45 * level
    L, a, b = np.moveaxis(lab(blur(small, 1.0) * (0.5 / level)), -1, 0)
    pale = np.hypot(a, b) < 12
    lg = np.log2(np.maximum(y, 1e-6))
    smooth = np.sqrt(np.maximum(blur(lg**2, 2.0) - blur(lg, 2.0) ** 2, 0)) < 0.08
    m = (bright & pale & smooth).astype(np.uint8)
    r = STAIN_FENCE // STAIN_DOWN
    return cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(np.float32)


def neutral_stains(img: np.ndarray, name: str, strip: int = 768) -> np.ndarray:
    """Manchas de color de la pared (salpicaduras amarillas en un retrato): mismo brillo que la pared y
    otro color, asi que find_marks, que busca lo oscuro, no las ve. El color de cada pixel de la
    pared se lleva al color promedio de la pared alrededor (STAIN_SCALE); el brillo y el grano
    quedan como estan. Lo que no tiene el brillo de la pared (un pelo suelto, mas oscuro) no se
    toca, y el borde de la zona es suave. En el lugar; devuelve cuanto cambio el color (0..1).
    """
    h, w = img.shape[:2]
    level = wall_level(img, name)
    small = cv2.resize(img, (w // STAIN_DOWN, h // STAIN_DOWN), interpolation=cv2.INTER_AREA)
    region = stain_region(small, level)
    g = np.maximum(small[..., 1], 1e-6)
    ref_r = norm_blur(np.log(np.maximum(small[..., 0], 1e-6) / g), region, STAIN_SCALE / STAIN_DOWN)
    ref_b = norm_blur(np.log(np.maximum(small[..., 2], 1e-6) / g), region, STAIN_SCALE / STAIN_DOWN)
    soft = blur(region, 2.0)  # borde de la zona: ~8 px a resolucion completa
    up = lambda x: cv2.resize(x, (w, h), interpolation=cv2.INTER_LINEAR)  # noqa: E731
    ref_r, ref_b, soft = up(ref_r), up(ref_b), up(soft)
    amount = np.zeros((h, w), np.float32)
    pad = 32
    for y0 in range(0, h, strip):
        a0, a1 = max(y0 - pad, 0), min(y0 + strip + pad, h)
        part = img[a0:a1]
        y = np.maximum(luminance(part), 1e-6)
        # el brillo de la pared alrededor: lo que se aparta mas de un 4 % empieza a no ser pared,
        # y a 12 % ya no lo es (un pelo suelto). Medido apenas suavizado: el grano no cuenta.
        near = np.abs(np.log2(np.maximum(blur(y, 1.5), 1e-6) / np.maximum(blur(y, 6.0), 1e-6)))
        k = slice(y0 - a0, y0 - a0 + min(strip, h - y0))
        wgt = soft[y0 : y0 + strip] * np.clip(1 - (near - 0.04) / 0.08, 0, 1)[k]
        p = part[k]
        g = np.maximum(p[..., 1], 1e-6)
        rr = np.log(np.maximum(p[..., 0], 1e-6) / g)
        bb = np.log(np.maximum(p[..., 2], 1e-6) / g)
        out = np.stack([g * np.exp(rr + (ref_r[y0 : y0 + strip] - rr) * wgt), g, g * np.exp(bb + (ref_b[y0 : y0 + strip] - bb) * wgt)], -1)
        out *= (y[k] / np.maximum(luminance(out), 1e-7))[..., None]
        img[y0 : y0 + strip] = out
        amount[y0 : y0 + strip] = wgt
    return amount


def find_marks(img: np.ndarray, name: str, max_n: int = 60) -> list[dict]:
    level = wall_level(img, name)
    m = wall_mask(img, level)
    # lejos de los bordes de la gente: un pelo o una sombra en el borde no es una mancha
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    m[:12], m[-12:], m[:, :12], m[:, -12:] = 0, 0, 0, 0  # el borde del cuadro da falsos positivos
    y = luminance(img)
    d = np.log2(np.maximum(norm_blur(y, m, 2.0), 1e-6)) - np.log2(np.maximum(norm_blur(y, m, 30.0), 1e-6))
    cand = ((d < -0.035) & (m > 0.5)).astype(np.uint8)
    n, labels, stats, cents = cv2.connectedComponentsWithStats(cand)
    out = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 6:
            continue
        x0, y0, w, h = (int(v) for v in stats[i, :4])
        depth = float(-d[y0 : y0 + h, x0 : x0 + w][labels[y0 : y0 + h, x0 : x0 + w] == i].min())
        out.append({"x": int(cents[i][0]), "y": int(cents[i][1]), "r": int(max(w, h) / 2 + 2), "depth": depth, "area": area})
    out.sort(key=lambda c: -c["depth"] * np.sqrt(c["area"]))
    return out[:max_n]


def sheet(name: str, img: np.ndarray, marks: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    level = wall_level(img, name)
    gain = 0.8 / level
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    half, z = 40, 3
    tile = 2 * half * z
    cols = 6
    rows = max(1, (len(marks) + cols - 1) // cols)
    grid = Image.new("RGB", (cols * (tile + 8) + 8, rows * (tile + 24) + 8), (16, 16, 16))
    d = ImageDraw.Draw(grid)
    for i, c in enumerate(marks):
        cy = min(max(c["y"], half), img.shape[0] - half)
        cx = min(max(c["x"], half), img.shape[1] - half)
        t = img[cy - half : cy + half, cx - half : cx + half]
        # cada recuadro a su propio gris: cerca del flash la pared es mas clara y con la ganancia
        # de toda la foto quedaba blanca. Despues, contraste x3: la mancha se ve aunque sea leve.
        t = linear_to_srgb(t * (TILE_GRAY / max(float(np.median(luminance(t))), 1e-6)))
        t = np.clip((t - t.mean()) * 3 + t.mean(), 0, 1)
        t = cv2.resize(to_uint8(t, dither=False), (tile, tile), interpolation=cv2.INTER_NEAREST)
        gx, gy = 8 + (i % cols) * (tile + 8), 8 + (i // cols) * (tile + 24)
        grid.paste(Image.fromarray(t), (gx, gy))
        d.text((gx, gy + tile + 4), f"{i + 1}  ({c['x']}, {c['y']}) r{c['r']}  -{c['depth'] * 100:.0f}%", fill=(220, 220, 220), font=font)
    grid.save(OUT / f"{name}-manchas.png")
    small = 0.15
    over = cv2.resize(img, None, fx=small, fy=small, interpolation=cv2.INTER_AREA)
    over = Image.fromarray(to_uint8(linear_to_srgb(over * gain), dither=False))
    dm = ImageDraw.Draw(over)
    for i, c in enumerate(marks):
        x, y = c["x"] * small, c["y"] * small
        dm.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 40, 160), width=2)
        dm.text((x + 7, y - 7), str(i + 1), fill=(255, 40, 160), font=font)
    over.save(OUT / f"{name}-mapa.png")


def field_sheet(name: str, img: np.ndarray) -> None:
    """La luz medida sobre la pared y la correccion, lado a lado, para revisar el emparejado."""
    OUT.mkdir(parents=True, exist_ok=True)
    field = light_field(img, name)
    g = evening_log(field, name)
    lo, hi = np.percentile(field, [1, 99])
    a = np.clip((field - lo) / max(hi - lo, 1e-6), 0, 1)
    b = np.clip(0.5 + g / (2 * EVEN_LIMIT), 0, 1)  # gris = sin cambio, claro = sube
    both = np.concatenate([a, np.ones((a.shape[0], 8), np.float32), b], 1)
    Image.fromarray(to_uint8(np.dstack([both] * 3), dither=False)).save(OUT / f"{name}-luz.png")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        base = load_linear(n, "base")
        marks = find_marks(base, n)
        sheet(n, base, marks)
        field_sheet(n, base)
        f = light_field(base, n)
        print(f"{n}: {len(marks)} manchas candidatas; luz de la pared de {f.min():+.2f} a {f.max():+.2f} EV (log2)")
