"""Manchas de la pared antes y despues de curarlas, con el contraste x3 de la hoja de candidatas.

Uso: .venv/bin/python tools/wall_check.py <foto> [x,y,r ...]
Sin marcas en la linea de comandos usa las de photos.py (`wall_marks`).
Salida: proceso/21-pared/<foto>-curadas.png
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402
from heal import wall_mark  # noqa: E402
from photos import PHOTOS  # noqa: E402
from wall import TILE_GRAY  # noqa: E402

TILE = 240


def tile(img: np.ndarray, x: int, y: int, half: int, gain: float, mean: float) -> np.ndarray:
    cy = min(max(y, half), img.shape[0] - half)
    cx = min(max(x, half), img.shape[1] - half)
    t = linear_to_srgb(img[cy - half : cy + half, cx - half : cx + half] * gain)
    t = np.clip((t - mean) * 3 + mean, 0, 1)
    return cv2.resize(to_uint8(t, dither=False), (TILE, TILE), interpolation=cv2.INTER_NEAREST)


def main() -> None:
    name = sys.argv[1]
    marks = [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]] or PHOTOS[name].get("wall_marks", [])
    base = load_linear(name, "base")
    fixed = base.copy()
    for x, y, r in marks:
        wall_mark(fixed, x, y, r)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    cols = 3  # pares antes | despues
    rows = (len(marks) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * TILE + 16) + 8, rows * (TILE + 24) + 8), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    for i, (x, y, r) in enumerate(marks):
        half = max(40, int(2.6 * r))
        # cada par a su propio gris (como la hoja de candidatas), el mismo en los dos paneles
        cy, cx = min(max(y, half), base.shape[0] - half), min(max(x, half), base.shape[1] - half)
        before = base[cy - half : cy + half, cx - half : cx + half]
        gain = TILE_GRAY / max(float(np.median(luminance(before))), 1e-6)
        mean = float(linear_to_srgb(before * gain).mean())
        gx, gy = 8 + (i % cols) * (2 * TILE + 16), 8 + (i // cols) * (TILE + 24)
        sheet.paste(Image.fromarray(tile(base, x, y, half, gain, mean)), (gx, gy))
        sheet.paste(Image.fromarray(tile(fixed, x, y, half, gain, mean)), (gx + TILE + 2, gy))
        d.text((gx, gy + TILE + 4), f"({x}, {y}) r{r}   antes | despues", fill=(220, 220, 220), font=font)
    out = PROCESS / "21-pared" / f"{name}-curadas.png"
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
