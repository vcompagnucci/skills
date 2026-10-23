"""Candidatos de granos, marcas y lunares en cada cara, para revisarlos ampliados.

El detector solo propone; la decision (curar o dejar) la tomo mirando cada recorte y queda
escrita en photos.py. Criterio, el de siempre: lo temporal se cura (granos, marcas rojas,
raspones); lo permanente se queda (lunares, pecas, cicatrices).

Lo que mide cada candidato contra la piel de alrededor (radio ~12 px):
- dL: cuanto mas oscuro (L*); da: cuanto mas rojo (a*); db: cuanto mas amarillo (b*).
- Un grano o una marca roja: da alto, dL chico. Un lunar o una peca: dL negativo con db
  positivo (marron). El vello facial: oscuro y azulado (db negativo), no entra.

Uso: .venv/bin/python recipe/spots.py <foto>      -> proceso/10-candidatos/<foto>-<cara>.png
"""

import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import PROCESS, blur, lab, linear_to_srgb, load_linear, luminance, norm_blur, to_uint8
from faces import skin_mask, window
from photos import PHOTOS

OUT = PROCESS / "10-candidatos"


def roundness(score: np.ndarray, sigma: float) -> np.ndarray:
    """Cociente de los autovalores del Hessiano: 1 en una mancha redonda, ~0 en una arruga."""
    s = blur(score, sigma)
    dxx = cv2.Sobel(s, cv2.CV_32F, 2, 0, ksize=3)
    dyy = cv2.Sobel(s, cv2.CV_32F, 0, 2, ksize=3)
    dxy = cv2.Sobel(s, cv2.CV_32F, 1, 1, ksize=3)
    tr = dxx + dyy
    disc = np.sqrt((dxx - dyy) ** 2 + 4 * dxy**2)
    l1, l2 = (tr - disc) / 2, (tr + disc) / 2  # en un pico los dos son negativos, l1 el mas fuerte
    return np.where(l1 < 0, np.clip(l2 / np.minimum(l1, -1e-6), 0, 1), 0)


def candidates(crop: np.ndarray, skin: np.ndarray, max_n: int = 48) -> list[dict]:
    y = luminance(crop)
    k = 0.30 / max(float(np.median(y[skin > 0.5])), 1e-6)
    L, a, b = np.moveaxis(lab(np.clip(crop * k, 0, None)), -1, 0)
    w = (skin > 0.5).astype(np.float32)
    fine = {c: norm_blur(v, w, 1.2) for c, v in (("L", L), ("a", a), ("b", b))}
    local = {c: norm_blur(v, w, 12.0) for c, v in (("L", L), ("a", a), ("b", b))}
    dL, da, db = (fine[c] - local[c] for c in "Lab")
    red = np.maximum(da, 0)
    brown = np.maximum(-dL, 0) * (db > 0.5)
    score = (1.6 * red + 0.6 * brown) * w
    score = blur(score, 1.0)
    # las arrugas y los pliegues dan lineas, no manchas: se descartan por forma
    round_ = np.maximum(roundness(score, 2.0), roundness(score, 4.0))
    peaks = (score == cv2.dilate(score, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))) & (score > 2.6) & (round_ > 0.3)
    ys, xs = np.nonzero(peaks)
    order = np.argsort(-score[ys, xs])[:max_n]
    out = []
    for i in order:
        cy, cx = int(ys[i]), int(xs[i])
        # radio: hasta donde la diferencia cae a la mitad
        s0 = score[cy, cx]
        r = 2
        while r < 16 and cy - r > 0 and cx - r > 0 and cy + r < score.shape[0] - 1 and cx + r < score.shape[1] - 1:
            ring = [score[cy - r, cx], score[cy + r, cx], score[cy, cx - r], score[cy, cx + r]]
            if np.mean(ring) < s0 * 0.4:
                break
            r += 1
        out.append({"x": cx, "y": cy, "r": r, "dL": float(dL[cy, cx]), "da": float(da[cy, cx]), "db": float(db[cy, cx]), "s": float(s0)})
    return out


def sheet(name: str, face: dict, crop: np.ndarray, origin: tuple[int, int], cands: list[dict], gain: float) -> None:
    oy, ox = origin
    srgb = linear_to_srgb(crop * gain)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    # vista general con los numeros
    over = Image.fromarray(to_uint8(srgb, dither=False))
    d = ImageDraw.Draw(over)
    for i, c in enumerate(cands, 1):
        d.ellipse((c["x"] - c["r"] - 4, c["y"] - c["r"] - 4, c["x"] + c["r"] + 4, c["y"] + c["r"] + 4), outline=(0, 220, 255), width=2)
        d.text((c["x"] + c["r"] + 5, c["y"] - 8), str(i), fill=(0, 220, 255), font=font)
    # tiras ampliadas x4, con contexto
    z, half = 4, 30
    tile = 2 * half * z
    cols = 8
    rows = (len(cands) + cols - 1) // cols
    grid = Image.new("RGB", (cols * (tile + 8) + 8, rows * (tile + 40) + 8), (16, 16, 16))
    gd = ImageDraw.Draw(grid)
    pad = np.pad(srgb, ((half, half), (half, half), (0, 0)), mode="edge")
    for i, c in enumerate(cands):
        y0, x0 = c["y"], c["x"]
        t = pad[y0 : y0 + 2 * half, x0 : x0 + 2 * half]
        t = cv2.resize(t, (tile, tile), interpolation=cv2.INTER_NEAREST)
        gx, gy = 8 + (i % cols) * (tile + 8), 8 + (i // cols) * (tile + 40)
        grid.paste(Image.fromarray(to_uint8(t, dither=False)), (gx, gy))
        # marcas afuera del radio, para saber cual es el punto sin taparlo
        cxp, cyp, rr = gx + tile // 2, gy + tile // 2, (c["r"] + 4) * z
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            gd.line([(cxp + dx * rr, cyp + dy * rr), (cxp + dx * (rr + 10), cyp + dy * (rr + 10))], fill=(0, 220, 255), width=2)
        gd.text((gx, gy + tile + 3), f"{i + 1}  ({c['x'] + ox}, {c['y'] + oy}) r{c['r']}", fill=(235, 235, 235), font=small)
        gd.text((gx, gy + tile + 19), f"dL {c['dL']:+.1f}  da {c['da']:+.1f}  db {c['db']:+.1f}", fill=(160, 160, 160), font=small)
    OUT.mkdir(parents=True, exist_ok=True)
    over.save(OUT / f"{name}-{face['id']}-mapa.png")
    grid.save(OUT / f"{name}-{face['id']}-tiras.png")


def main(name: str) -> None:
    img = load_linear(name, "base")
    gain = 0.85 / np.percentile(luminance(img[::8, ::8]), 99)
    for face in PHOTOS[name]["faces"]:
        sy, sx = window(face, img.shape[:2])
        crop = img[sy, sx]
        origin = (sy.start, sx.start)
        skin = skin_mask(crop, face, origin)
        cands = candidates(crop, skin)
        sheet(name, face, crop, origin, cands, gain)
        # la mascara de piel, para revisarla
        m = Image.fromarray(to_uint8(np.dstack([skin] * 3), dither=False))
        m.save(OUT / f"{name}-{face['id']}-piel.png")
        print(f"{name} {face['id']}: {len(cands)} candidatos")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
