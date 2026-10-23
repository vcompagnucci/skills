"""Mide piel y pared en la base lineal: la referencia para fijar exposicion y color.

Uso: .venv/bin/python tools/measure.py [suffix] [fotos...]   (suffix: base, retocada...)
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PHOTO_NAMES, lab, lightness, load_linear, luminance  # noqa: E402
from develop import frac_box  # noqa: E402
from faces import skin_mask, window  # noqa: E402
from photos import PHOTOS  # noqa: E402


def load(name: str, suffix: str) -> np.ndarray:
    """"final" = la salida de 16 bits de editadas/, vuelta a lineal."""
    if suffix == "final":
        import tifffile

        from common import EDITED, srgb_to_linear

        return srgb_to_linear(tifffile.imread(EDITED / f"{name}.tif").astype(np.float32) / 65535)
    return load_linear(name, suffix)


def main(suffix: str, names: list[str]) -> None:
    for name in names:
        img = load(name, suffix)
        walls = [np.median(luminance(img[frac_box(b, img.shape[:2])])) for b in PHOTOS[name]["wall"]]
        print(f"{name} pared Y {' '.join(f'{w:.3f}' for w in walls)}  (L* {' '.join(f'{lightness(w):.1f}' for w in walls)})")
        for face in PHOTOS[name]["faces"]:
            sy, sx = window(face, img.shape[:2])
            crop = img[sy, sx]
            w = skin_mask(crop, face, (sy.start, sx.start)) > 0.5
            y = luminance(crop)[w]
            lit = y >= np.percentile(y, 50)
            L, a, b = np.moveaxis(lab(crop[w][lit]), -1, 0)
            print(
                f"  {face['id']:<11} piel Y p50 {np.median(y):.3f} p90 {np.percentile(y, 90):.3f}  "
                f"lado iluminado L* {np.median(L):.1f} a* {np.median(a):.1f} b* {np.median(b):.1f} "
                f"tono {np.degrees(np.arctan2(np.median(b), np.median(a))):.0f} croma {np.hypot(np.median(a), np.median(b)):.1f}"
            )


if __name__ == "__main__":
    args = sys.argv[1:]
    suffix = args.pop(0) if args and args[0] not in PHOTOS else "base"  # o "final"
    main(suffix, args or PHOTO_NAMES)
