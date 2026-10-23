"""Mirar un intermedio lineal: recorte, escala y exposicion, a PNG.

Uso: .venv/bin/python tools/peek.py <foto> base salida.png [x0 y0 x1 y1] [--width 1400] [--ev 0] [--auto]
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import linear_to_srgb, load_linear, luminance, resize, save_png  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("suffix")
    p.add_argument("out")
    p.add_argument("box", nargs="*", type=int)
    p.add_argument("--width", type=int, default=0)
    p.add_argument("--ev", type=float, default=0.0)
    p.add_argument("--auto", action="store_true", help="la pared (p99 de luminancia) a 0,85")
    a = p.parse_args()
    img = load_linear(a.name, a.suffix)
    if a.box:
        x0, y0, x1, y1 = a.box
        img = img[y0:y1, x0:x1]
    gain = 2**a.ev
    if a.auto:
        gain *= 0.85 / np.percentile(luminance(img[::4, ::4]), 99)
    out = linear_to_srgb(img * gain)
    if a.width and a.width != out.shape[1]:
        out = resize(out, a.width)
    save_png(out, Path(a.out), dither=False)
    print(a.out, out.shape)


if __name__ == "__main__":
    main()
