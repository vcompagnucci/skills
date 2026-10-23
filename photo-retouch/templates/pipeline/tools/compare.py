"""Dos intermedios lado a lado (por defecto base y retocada), mismo recorte y exposicion, a PNG.

Uso: .venv/bin/python tools/compare.py <foto> x0 y0 x1 y1 salida.png [--a base] [--b retocada] [--zoom 2] [--ev 1.2] [--diff]
--diff agrega un tercer panel con la diferencia de luminancia x8 (gris = sin cambio).
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    for k in ("x0", "y0", "x1", "y1"):
        p.add_argument(k, type=int)
    p.add_argument("out")
    p.add_argument("--a", default="base")
    p.add_argument("--b", default="retocada")
    p.add_argument("--zoom", type=float, default=1.0)
    p.add_argument("--ev", type=float, default=1.2)
    p.add_argument("--diff", action="store_true")
    a = p.parse_args()
    sl = (slice(a.y0, a.y1), slice(a.x0, a.x1))
    A, B = load_linear(a.name, a.a)[sl], load_linear(a.name, a.b)[sl]
    panels = [linear_to_srgb(A * 2**a.ev), linear_to_srgb(B * 2**a.ev)]
    if a.diff:
        d = np.log2(np.maximum(luminance(B), 1e-6) / np.maximum(luminance(A), 1e-6))
        panels.append(np.dstack([np.clip(0.5 + 8 * d, 0, 1)] * 3).astype(np.float32))
    ims = []
    for im in panels:
        if a.zoom != 1:
            im = cv2.resize(im, None, fx=a.zoom, fy=a.zoom, interpolation=cv2.INTER_NEAREST if a.zoom > 1 else cv2.INTER_AREA)
        ims.append(to_uint8(im, dither=False))
    gap = np.full((ims[0].shape[0], 6, 3), 20, np.uint8)
    out = Image.fromarray(np.concatenate([x for im in ims for x in (im, gap)][:-1], 1))
    d = ImageDraw.Draw(out)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    w = ims[0].shape[1] + 6
    for i, label in enumerate([a.a, a.b, "diferencia x8"][: len(ims)]):
        d.text((i * w + 6, 6), label, fill=(255, 40, 160), font=font)
    path = Path(a.out)
    if not path.is_absolute() and path.parent == Path("."):
        path = PROCESS / "30-retoque" / path
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path, out.size)


if __name__ == "__main__":
    main()
