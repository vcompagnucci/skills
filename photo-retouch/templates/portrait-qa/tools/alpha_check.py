"""Alpha nuevo de una foto en zonas del contorno, con un aclarado de pared simulado.

Por zona: la base (RAW retocado), la pared aclarada a mano (I + (1 - alpha)·1.4·B) y el
alpha, a 2x. Sirve para ver mordidas y filetes sin el render completo.
Uso: .venv/bin/python tools/alpha_check.py <foto> x,y x,y ...
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recipe"))
from common import ROOT  # noqa: E402
from geometry import load_crop  # noqa: E402
from matte import upsample_alpha  # noqa: E402
from styles import face_ellipse, wall_behind  # noqa: E402

name, pts = sys.argv[1], [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]]
img, geo = load_crop(name, "abierto", 4170)
small = np.load(ROOT / "work" / f"{name}-abierto-matte.npz")["alpha"].astype(np.float32)
alpha = upsample_alpha(img, small, face_ellipse(geo))
np.save(ROOT / "work" / f"{name}-alpha-check.npy", alpha.astype(np.float16))
scale = float(np.percentile(img @ [0.2126, 0.7152, 0.0722], 99.5))
B = wall_behind(img, alpha).astype(np.float32)
srgb = lambda x: np.clip(np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055), 0, 1)  # noqa: E731
rows = []
for x, y in pts:
    sl = (slice(y - 90, y + 90), slice(x - 90, x + 90))
    I, a = img[sl] / scale, alpha[sl]
    lit = I + ((1 - a) * 1.4)[..., None] * B[sl] / scale
    tiles = [srgb(I), srgb(lit), np.repeat(a[..., None], 3, 2)]
    row = np.concatenate([cv2.resize((t * 255).astype(np.uint8), (360, 360), interpolation=cv2.INTER_NEAREST) for t in tiles], 1)
    rows.append(cv2.cvtColor(row, cv2.COLOR_RGB2BGR))
cv2.imwrite(str(ROOT / "proceso" / f"alpha-check-{name}.png"), np.concatenate(rows, 0))  # proceso/ no tiene carpetas
