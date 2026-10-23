"""Recorte con una grilla rotulada en coordenadas de la imagen completa, para leer posiciones.

Uso: .venv/bin/python tools/grid.py <foto> x0 y0 x1 y1 salida.png [--step 50] [--zoom 1.0] [--ev 1.4]
     .venv/bin/python tools/grid.py <referencia> x0 y0 x1 y1 salida.png --ref   (una de recipe/references.py, sin --ev)
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import linear_to_srgb, load_linear, to_uint8  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("x0", type=int)
    p.add_argument("y0", type=int)
    p.add_argument("x1", type=int)
    p.add_argument("y1", type=int)
    p.add_argument("out")
    p.add_argument("--step", type=int, default=50)
    p.add_argument("--zoom", type=float, default=1.0)
    p.add_argument("--ev", type=float, default=1.4)
    p.add_argument("--suffix", default="base")
    p.add_argument("--ref", action="store_true", help="name es una referencia de estilo; se ve tal cual")
    a = p.parse_args()
    if a.ref:
        from references import load_reference

        img, ev = load_reference(a.name), 0.0
    else:
        img, ev = load_linear(a.name, a.suffix), a.ev
    img = img[a.y0 : a.y1, a.x0 : a.x1]
    srgb = linear_to_srgb(img * 2**ev)
    if a.zoom != 1:
        srgb = cv2.resize(srgb, None, fx=a.zoom, fy=a.zoom, interpolation=cv2.INTER_CUBIC if a.zoom > 1 else cv2.INTER_AREA)
    im = Image.fromarray(to_uint8(srgb, dither=False))
    d = ImageDraw.Draw(im, "RGBA")
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    first_x = (a.x0 // a.step + 1) * a.step
    for x in range(first_x, a.x1, a.step):
        px = (x - a.x0) * a.zoom
        major = x % (a.step * 2) == 0
        d.line([(px, 0), (px, im.height)], fill=(0, 255, 255, 110 if major else 55), width=1)
        if major:
            d.text((px + 2, 2), str(x), fill=(0, 255, 255, 255), font=font)
    first_y = (a.y0 // a.step + 1) * a.step
    for y in range(first_y, a.y1, a.step):
        py = (y - a.y0) * a.zoom
        major = y % (a.step * 2) == 0
        d.line([(0, py), (im.width, py)], fill=(255, 0, 255, 110 if major else 55), width=1)
        if major:
            d.text((2, py + 2), str(y), fill=(255, 0, 255, 255), font=font)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    im.save(a.out)
    print(a.out, im.size)


if __name__ == "__main__":
    main()
