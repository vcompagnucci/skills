"""Control de las puntas de ojeras que arma grade.py, foto por foto:

1. Costura: afuera de la ojera, cada parche tiene que ser pixel por pixel la final (PNG y TIFF).
2. Mezcla: el editor y la exportacion mezclan la final con una punta en sRGB (pasado el 100 %, la
   punta del 100 % con la del 200 %). Se compara contra el render exacto a 35, 85 y 150 % (el medio de
   cada tramo, donde la mezcla mas se aleja). Entre 100 y 200 el exacto es la capa del medio: la del
   100 % y la del 200 % mezcladas en ganancia.

Uso: .venv/bin/python tools/eyes_blend_check.py <foto> [...]
"""

import json
import sys
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import EDITED, WORK, load_linear  # noqa: E402
from grade import EYES, MARGIN, PAD, finish  # noqa: E402
from undereye import INTENSITY, apply  # noqa: E402
from wall import evening_gain  # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def check(name: str) -> None:
    entries = json.loads((EYES / "ojeras.json").read_text())["photos"][name]
    final16 = tifffile.imread(EDITED / f"{name}.tif")
    final8 = np.asarray(Image.open(EDITED / f"{name}.png").convert("RGB"))
    z = np.load(WORK / f"{name}-ojeras.npz")
    img = load_linear(name, "retocada")
    gain = evening_gain(img, name)
    d = INTENSITY
    for e in entries:
        x, y, w, h = e["x"], e["y"], e["w"], e["h"]
        layer, top = z[e["face"]], z[f"{e['face']}-200"]
        oy, ox = (int(v) for v in z[f"{e['face']}-origen"])
        support = np.zeros((h, w), bool)
        support[oy - y : oy - y + layer.shape[0], ox - x : ox - x + layer.shape[1]] = np.any((layer != 0) | (top != 0), axis=-1)
        # la nitidez mueve hasta ~15 px alrededor de la capa: la costura se mira mas alla
        from scipy.ndimage import binary_dilation

        near = binary_dilation(support, iterations=MARGIN)
        ends = {}
        for tag in ("0", "100", "200"):
            p16 = tifffile.imread(EYES / f"{name}-{e['face']}-{tag}.tif")
            p8 = np.asarray(Image.open(EYES / f"{name}-{e['face']}-{tag}.png").convert("RGB"))
            out16 = np.abs(p16.astype(int) - final16[y : y + h, x : x + w])[~near].max()
            out8 = np.abs(p8.astype(int) - final8[y : y + h, x : x + w])[~near].max()
            inside = np.abs(p16.astype(int) - final16[y : y + h, x : x + w]).max()
            print(f"{name} {e['face']} {tag:>3} %: afuera de la ojera difiere {out16} (16 bits) y {out8} (8 bits); adentro, hasta {inside / 65535:.1%}")
            ends[tag] = p16.astype(np.float64) / 65535
        base = final16[y : y + h, x : x + w].astype(np.float64) / 65535
        # el render exacto a t, en el mismo parche
        Y0, X0 = max(y - PAD, 0), max(x - PAD, 0)
        Y1, X1 = min(y + h + PAD, img.shape[0]), min(x + w + PAD, img.shape[1])
        padded, padded_top = (np.zeros((Y1 - Y0, X1 - X0, 3), np.float32) for _ in range(2))
        padded[oy - Y0 : oy - Y0 + layer.shape[0], ox - X0 : ox - X0 + layer.shape[1]] = layer
        padded_top[oy - Y0 : oy - Y0 + layer.shape[0], ox - X0 : ox - X0 + layer.shape[1]] = top
        inner = (slice(y - Y0, y - Y0 + h), slice(x - X0, x - X0 + w))
        for t in (0.35, 0.85, 1.5):
            if t <= 1:
                exact_layer = (t - d) * padded  # la final ya tiene d
                start, tag, f = (base, "0", 1 - t / d) if t < d else (base, "100", (t - d) / (1 - d))
            else:
                f = t - 1
                exact_layer = (1 - f - d) * padded + f * padded_top
                start, tag = ends["100"], "200"
            exact = finish(apply(img[Y0:Y1, X0:X1], exact_layer), gain[Y0:Y1, X0:X1])[inner].astype(np.float64)
            mixed = start + f * (ends[tag] - start)
            err = np.abs(mixed - np.clip(exact, 0, 1))[support]
            moved = np.abs(ends[tag] - start)[support]
            print(
                f"{name} {e['face']} a {t:.0%}: la mezcla se aleja del render exacto {err.max() * 255:.2f} niveles de 255 como mucho"
                f" (p99 {np.percentile(err, 99) * 255:.2f}); la correccion mueve hasta {moved.max() * 255:.1f}"
            )


if __name__ == "__main__":
    for n in sys.argv[1:]:
        check(n)
