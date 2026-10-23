"""Pelusas: puntos y fibras claras, chicas y aisladas, sobre la ropa negra.

Lo que NO es pelusa y queda:
- grupos de puntos (tejido, costuras, pelo con brillo): 3 o mas a menos de 25 px es un dibujo;
- lo que tiene color (piel, remaches dorados);
- lo que esta sobre pelo: el pelo es castano (entorno calido, log R/B > 0,15; la ropa negra
  da entre -0,2 y +0,07) y con textura de mechones (desvio local ~0,3; la tela, ~0,1);
- lo que esta cerca de una cara, y las zonas `lint_keep` de photos.py (pelo, reloj, logos).

Se juzga como se va a ver: la pelusa tiene que destacar al menos 5 L* sobre la tela con la
exposicion final (grade.EXPOSURE), si no, no se nota y no se toca. Cada una queda en una hoja de revision
(proceso/20-pelusas), antes y despues, para auditar que no se llevo nada que no era.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import PROCESS, blur, lightness, linear_to_srgb, luminance, to_uint8
from develop import frac_box
from faces import ellipse_mask
from grade import EXPOSURE
from heal import fill
from photos import PHOTOS

VISIBLE = 5.0  # L* sobre la tela, con la exposicion final
OUT = PROCESS / "20-pelusas"


def wall_level(img: np.ndarray, name: str) -> float:
    return float(np.median([np.median(luminance(img[frac_box(b, img.shape[:2])])) for b in PHOTOS[name]["wall"]]))


def keep_zones(name: str, shape: tuple[int, int]) -> np.ndarray:
    zones = [(f["oval"][0], f["oval"][1], f["oval"][2] * 1.3, f["oval"][3] * 1.3) for f in PHOTOS[name]["faces"]]
    return ellipse_mask(shape, zones + PHOTOS[name].get("lint_keep", []), (0, 0)) > 0


def find(img: np.ndarray, name: str) -> list[dict]:
    y = luminance(img)
    wl = wall_level(img, name)
    ys = blur(y, 0.7)
    surround = blur(y, 15.0)
    lg = np.log2(np.maximum(ys, 1e-5))
    # contra 15 px tiene que casi duplicar la tela; contra 4 px alcanza menos, porque una fibra
    # alargada se promedia consigo misma (una de un retrato da 0,58)
    spike = (lg - np.log2(np.maximum(blur(y, 4.0), 1e-5)) > 0.45) & (lg - np.log2(np.maximum(surround, 1e-5)) > 0.9)
    visible = lightness(ys * EXPOSURE) - lightness(surround * EXPOSURE) > VISIBLE
    dark = surround < 0.12 * wl
    cand = (spike & visible & dark & ~keep_zones(name, y.shape)).astype(np.uint8)
    del lg, ys
    n, labels, stats, cents = cv2.connectedComponentsWithStats(cand)
    smooth = blur(img, 3.0)
    around = blur(img, 40.0)
    lg = np.log2(np.maximum(blur(y, 0.7), 1e-5))
    texture = blur(np.sqrt(np.maximum(blur(lg**2, 6.0) - blur(lg, 6.0) ** 2, 0)), 25.0)
    del lg
    specks = []
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if not 3 <= area <= 400:
            continue
        x, yy = int(cents[i][0]), int(cents[i][1])
        warmth = np.log(max(smooth[yy, x, 0], 1e-6) / max(smooth[yy, x, 2], 1e-6))
        if warmth > 0.25:
            continue
        hair = np.log(max(around[yy, x, 0], 1e-6) / max(around[yy, x, 2], 1e-6)) > 0.15 or texture[yy, x] > 0.22
        if hair:
            continue
        x0, y0, w, h = (int(v) for v in stats[i, :4])
        specks.append({"x": x, "y": yy, "box": (x0, y0, w, h), "label": i, "area": int(area)})
    # aislamiento: 3 o mas a menos de 25 px es un dibujo (tejido, costura), no pelusa
    pts = np.array([[s["x"], s["y"]] for s in specks], np.float32).reshape(-1, 2)
    keep = []
    for s in specks:
        d = np.hypot(pts[:, 0] - s["x"], pts[:, 1] - s["y"])
        if (d < 25).sum() <= 2:  # se cuenta a si misma
            pad = 6
            x0, y0, w, h = s["box"]
            ya, xa = max(0, y0 - pad), max(0, x0 - pad)
            sl = (slice(ya, min(y.shape[0], y0 + h + pad)), slice(xa, min(y.shape[1], x0 + w + pad)))
            s["hole"] = cv2.dilate((labels[sl] == s["label"]).astype(np.uint8), np.ones((5, 5), np.uint8))
            s["origin"] = (ya, xa)
            keep.append(s)
    return keep


def remove(img: np.ndarray, specks: list[dict]) -> None:
    for s in specks:
        fill(img, *s["origin"], s["hole"])


def sheet(name: str, before: np.ndarray, after: np.ndarray, specks: list[dict]) -> None:
    """Cada pelusa ampliada x4, antes y despues, con la exposicion de la ropa (+3 EV)."""
    OUT.mkdir(parents=True, exist_ok=True)
    if not specks:
        return
    half, z = 20, 4
    tile = 2 * half * z
    cols = 6
    rows = (len(specks) + cols - 1) // cols
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    grid = Image.new("RGB", (cols * (2 * tile + 16) + 8, rows * (tile + 24) + 8), (16, 16, 16))
    d = ImageDraw.Draw(grid)
    for i, s in enumerate(specks):
        gx, gy = 8 + (i % cols) * (2 * tile + 16), 8 + (i // cols) * (tile + 24)
        cy = min(max(s["y"], half), before.shape[0] - half)
        cx = min(max(s["x"], half), before.shape[1] - half)
        for j, src in enumerate((before, after)):
            t = src[cy - half : cy + half, cx - half : cx + half] * EXPOSURE * 8
            t = cv2.resize(to_uint8(linear_to_srgb(t), dither=False), (tile, tile), interpolation=cv2.INTER_NEAREST)
            grid.paste(Image.fromarray(t), (gx + j * (tile + 4), gy))
        d.text((gx, gy + tile + 4), f"{i + 1}  ({s['x']}, {s['y']})  {s['area']} px", fill=(220, 220, 220), font=font)
    grid.save(OUT / f"{name}-pelusas.png")
    # mapa: donde esta cada una
    small = 0.25
    over = cv2.resize(after, None, fx=small, fy=small, interpolation=cv2.INTER_AREA)
    over = Image.fromarray(to_uint8(linear_to_srgb(over * EXPOSURE * 2.5), dither=False))
    dm = ImageDraw.Draw(over)
    for i, s in enumerate(specks):
        cx, cy = s["x"] * small, s["y"] * small
        dm.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=(0, 220, 255), width=2)
        dm.text((cx + 8, cy - 7), str(i + 1), fill=(0, 220, 255), font=font)
    over.save(OUT / f"{name}-mapa.png")
