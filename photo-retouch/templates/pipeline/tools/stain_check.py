"""Manchas de color de la pared antes y despues de wall.neutral_stains, con contraste x3.

Busca las 12 manchas mas fuertes (menos azul que la pared alrededor, o sea amarillas) y muestra
cada una antes | despues; abajo, a 1/8, donde actua la correccion (blanco = entera).

Uso: .venv/bin/python tools/stain_check.py <foto> -> proceso/21-pared/<foto>-color.png
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, norm_blur, to_uint8  # noqa: E402
from wall import TILE_GRAY, neutral_stains, wall_level, wall_mask  # noqa: E402

TILE = 240
HALF = 60


def strongest(img: np.ndarray, name: str, n: int = 12) -> list[tuple[int, int]]:
    small = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
    m = wall_mask(small, wall_level(small, name))
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    yb = np.log2(np.maximum(small[..., 2], 1e-6)) - np.log2(np.maximum(luminance(small), 1e-6))
    d = norm_blur(yb, m, 2.0) - norm_blur(yb, m, 25.0)
    d[m < 0.5] = 0
    picks = []
    for _ in range(n):
        iy, ix = np.unravel_index(np.argmin(d), d.shape)
        if d[iy, ix] > -0.03:
            break
        picks.append((int(ix) * 2, int(iy) * 2))
        d[max(iy - HALF, 0) : iy + HALF, max(ix - HALF, 0) : ix + HALF] = 0
    return picks


def tile(img: np.ndarray, x: int, y: int, gain: float, mean: np.ndarray) -> np.ndarray:
    cy = min(max(y, HALF), img.shape[0] - HALF)
    cx = min(max(x, HALF), img.shape[1] - HALF)
    t = linear_to_srgb(img[cy - HALF : cy + HALF, cx - HALF : cx + HALF] * gain)
    t = np.clip((t - mean) * 3 + mean, 0, 1)
    return cv2.resize(to_uint8(t, dither=False), (TILE, TILE), interpolation=cv2.INTER_NEAREST)


def main(name: str) -> None:
    base = load_linear(name, "base")
    picks = strongest(base, name)
    fixed = base.copy()
    amount = neutral_stains(fixed, name)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    cols = 3
    rows = max(1, (len(picks) + cols - 1) // cols)
    small = cv2.resize(amount, (amount.shape[1] // 8, amount.shape[0] // 8), interpolation=cv2.INTER_AREA)
    over = Image.fromarray(to_uint8(np.dstack([small] * 3), dither=False))
    width = cols * (2 * TILE + 16) + 8
    sheet = Image.new("RGB", (max(width, over.width + 16), rows * (TILE + 24) + 16 + over.height), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for i, (x, y) in enumerate(picks):
        cy, cx = min(max(y, HALF), base.shape[0] - HALF), min(max(x, HALF), base.shape[1] - HALF)
        before = base[cy - HALF : cy + HALF, cx - HALF : cx + HALF]
        gain = TILE_GRAY / max(float(np.median(luminance(before))), 1e-6)
        # el mismo gris en los dos paneles, canal por canal: el color que cambia se ve x3
        mean = linear_to_srgb(before * gain).mean((0, 1))
        gx, gy = 8 + (i % cols) * (2 * TILE + 16), 8 + (i // cols) * (TILE + 24)
        sheet.paste(Image.fromarray(tile(base, x, y, gain, mean)), (gx, gy))
        sheet.paste(Image.fromarray(tile(fixed, x, y, gain, mean)), (gx + TILE + 2, gy))
        d.text((gx, gy + TILE + 4), f"({x}, {y})   antes | despues", fill=(220, 220, 220), font=font)
    sheet.paste(over, (8, rows * (TILE + 24) + 8))
    out = PROCESS / "21-pared" / f"{name}-color.png"
    sheet.save(out)
    print(out.name, sheet.size, f"{len(picks)} manchas; zona corregida {float((amount > 0.5).mean()) * 100:.0f} % de la foto")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
