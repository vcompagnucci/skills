"""Centro y tamano real de una mancha de la pared, para anotarla en photos.py.

La candidata de la hoja (proceso/21-pared) da el centro de lo que paso el umbral, que a veces
junta la mancha con el grano de alrededor. Aca se busca lo mas oscuro a menos de 25 px y se mide
la mancha que lo rodea (lo que queda por debajo del 40 % de su hondura).

Uso: .venv/bin/python tools/wall_measure.py <foto> 2928,1354 3695,126 ...
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import load_linear, luminance, norm_blur  # noqa: E402

SEARCH = 25
HALF = 70


def main() -> None:
    name = sys.argv[1]
    y = luminance(load_linear(name, "base"))
    for arg in sys.argv[2:]:
        x, yy = (int(v) for v in arg.split(","))
        y0, x0 = max(yy - HALF, 0), max(x - HALF, 0)
        win = y[y0 : yy + HALF, x0 : x + HALF]
        ones = np.ones_like(win)
        d = np.log2(np.maximum(norm_blur(win, ones, 1.2), 1e-6)) - np.log2(np.maximum(norm_blur(win, ones, 25.0), 1e-6))
        sy0, sx0 = max(yy - y0 - SEARCH, 0), max(x - x0 - SEARCH, 0)
        near = d[sy0 : yy - y0 + SEARCH, sx0 : x - x0 + SEARCH]
        iy, ix = np.unravel_index(np.argmin(near), near.shape)
        py, px = iy + sy0, ix + sx0
        comp = (d < 0.4 * d[py, px]).astype(np.uint8)
        _, labels, stats, cents = cv2.connectedComponentsWithStats(comp)
        k = labels[py, px]
        w, h = int(stats[k, 2]), int(stats[k, 3])
        cx, cy = int(round(cents[k][0])) + x0, int(round(cents[k][1])) + y0
        print(f"{arg:>12}: {d[py, px] * 100:4.0f}% en ({px + x0}, {py + y0}); mancha {w}x{h} -> ({cx}, {cy}, {max(w, h) // 2 + 2})")


if __name__ == "__main__":
    main()
