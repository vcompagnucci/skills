"""Compara en pixeles decodificados los archivos de un respaldo contra los de hoy (editadas/, o la carpeta del
proyecto que se respaldo). Los hashes de archivo no sirven: el ICC del TIFF lleva fecha.

Uso: .venv/bin/python tools/compare_masters.py respaldos/<version>-antes-<que>
Recorre todo lo que hay en el respaldo (editadas/, work/, ...) y busca lo mismo en la raiz del proyecto. Por archivo:
identico, o el cambio maximo y medio, el % de pixeles distintos y el recuadro (x0, y0, x1, y1) donde cambiaron,
para ver que el cambio quedo donde se esperaba. Copiado de un proyecto anterior de retratos.
"""
import sys
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OLD = Path(sys.argv[1]).resolve()
EXT = (".tif", ".tiff", ".png", ".webp", ".npy")


def load(p: Path) -> np.ndarray:
    if p.suffix.lower() in (".tif", ".tiff"):
        return tifffile.imread(p)
    if p.suffix.lower() == ".npy":
        return np.load(p)
    if p.suffix.lower() == ".png":  # 16 bits con alpha: PIL no los abre bien
        import cv2
        return cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    return np.asarray(Image.open(p))


same, diff, missing = [], [], []
for old in sorted(OLD.rglob("*")):
    if not old.is_file() or old.name.startswith(".") or old.suffix.lower() not in EXT:
        continue
    rel = old.relative_to(OLD)
    new = ROOT / rel
    if not new.exists():
        missing.append(str(rel))
        continue
    a, b = load(old), load(new)
    if a.shape != b.shape:
        diff.append((str(rel), f"forma {a.shape} -> {b.shape}"))
        continue
    d = np.abs(a.astype(np.int32) - b.astype(np.int32))
    if d.max() == 0:
        same.append(str(rel))
        continue
    scale = 65535 if a.dtype == np.uint16 else 255
    px = d.max(axis=-1) > 0 if d.ndim == 3 else d > 0
    ys, xs = np.nonzero(px)
    diff.append((str(rel), f"max {d.max()}/{scale}  media {d.mean():.4f}  px distintos {px.mean() * 100:.3f} %"
                           f"  en x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}"))
print(f"identicos {len(same)}  distintos {len(diff)}  faltan {len(missing)}")
for r, s in diff:
    print("DISTINTO", r, s)
for r in missing:
    print("FALTA", r)
