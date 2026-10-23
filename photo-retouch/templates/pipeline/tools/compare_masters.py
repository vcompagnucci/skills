"""Compara en pixeles decodificados los archivos de un respaldo contra los de hoy (editadas/, o la carpeta del
proyecto que se respaldo). Los hashes de archivo no sirven: el ICC del TIFF lleva fecha.

Uso: .venv/bin/python tools/compare_masters.py respaldos/<version>-antes-<que> [--mask FILE]
Recorre todo lo que hay en el respaldo (editadas/, work/, ...) y busca lo mismo en la raiz del proyecto. Por archivo:
identico, o el cambio maximo y medio, el % de pixeles distintos y el recuadro (x0, y0, x1, y1) donde cambiaron,
para ver que el cambio quedo donde se esperaba. Lo que hoy esta en esas mismas carpetas y no en el respaldo (un
estilo renderizado por primera vez) sale como NUEVO: no hay contra que compararlo. Copiado de un proyecto anterior de
retratos.

--mask FILE: un alpha (.npz con la clave alpha, o un PNG/TIFF gris; persona donde alpha > 0,5, con el gris
llevado a 0..1 por el maximo de su formato). Cada archivo distinto suma una linea con el cambio maximo, el medio y
el % de pixeles distintos adentro de la mascara (persona) y afuera (pared), por separado: despues de un cambio solo
de pared, la persona tiene que dar max 0. Si el archivo tiene otro tamano que la mascara pero la misma proporcion
(+-1 %), la mascara se lleva a su tamano (lineal, y despues el umbral); con otra proporcion, no se separa.
"""
import argparse
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
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


def load_mask(p: Path) -> np.ndarray:
    """El alpha en 0..1 (float32, alto x ancho)."""
    if p.suffix.lower() == ".npz":
        a = np.load(p)["alpha"].astype(np.float32)
    else:
        a = load(p)
        top = np.iinfo(a.dtype).max if np.issubdtype(a.dtype, np.integer) else 1.0
        a = a.astype(np.float32) / top
        if a.ndim == 3:  # un gris guardado en RGB: el promedio de los canales
            a = a[..., :3].mean(axis=-1)
    if a.ndim != 2:
        raise SystemExit(f"{p}: la mascara tiene que ser gris (alto x ancho), tiene forma {a.shape}")
    return a


def person_for(alpha: np.ndarray, shape: tuple[int, int]) -> tuple[np.ndarray | None, str]:
    """La persona (bool) al tamano del archivo, y una nota si hubo que llevarla o no se pudo."""
    if alpha.shape == shape:
        return alpha > 0.5, ""
    if abs(alpha.shape[1] / alpha.shape[0] - shape[1] / shape[0]) > 0.01 * shape[1] / shape[0]:
        return None, f"mascara de otra forma {alpha.shape[1]}x{alpha.shape[0]}: sin separar"
    import cv2
    shrink = shape[0] < alpha.shape[0]
    a = cv2.resize(alpha, (shape[1], shape[0]), interpolation=cv2.INTER_AREA if shrink else cv2.INTER_LINEAR)
    return a > 0.5, f"mascara llevada de {alpha.shape[1]}x{alpha.shape[0]} a {shape[1]}x{shape[0]}"


def change(d: np.ndarray, px: np.ndarray, where: np.ndarray, scale: int) -> str:
    """Cambio maximo, medio (sobre todos los canales, como la linea del archivo) y % de pixeles distintos."""
    if not where.any():
        return "sin pixeles"
    sel = d[where]
    return f"max {sel.max()}/{scale}  media {sel.mean():.4f}  px distintos {px[where].mean() * 100:.3f} %"


def main() -> None:
    ap = argparse.ArgumentParser(description="Compara un respaldo contra el proyecto, en pixeles decodificados.")
    ap.add_argument("respaldo", type=Path)
    ap.add_argument("--mask", type=Path, metavar="FILE", help="alpha: .npz (clave alpha) o PNG/TIFF gris; persona donde > 0.5")
    args = ap.parse_args()
    old_root = args.respaldo.resolve()
    if not old_root.is_dir():
        ap.error(f"{args.respaldo}: no existe esa carpeta de respaldo")
    alpha = load_mask(args.mask) if args.mask else None

    same, diff, missing = [], [], []
    for old in sorted(old_root.rglob("*")):
        if not old.is_file() or old.name.startswith(".") or old.suffix.lower() not in EXT:
            continue
        rel = old.relative_to(old_root)
        new = ROOT / rel
        if not new.exists():
            missing.append(str(rel))
            continue
        a, b = load(old), load(new)
        if a.shape != b.shape:
            diff.append((str(rel), f"forma {a.shape} -> {b.shape}", None))
            continue
        d = np.abs(a.astype(np.int32) - b.astype(np.int32))
        if d.max() == 0:
            same.append(str(rel))
            continue
        scale = 65535 if a.dtype == np.uint16 else 255
        px = d.max(axis=-1) > 0 if d.ndim == 3 else d > 0
        ys, xs = np.nonzero(px)
        split = None
        if alpha is not None:
            person, note = person_for(alpha, px.shape)
            split = note if person is None else (f"persona: {change(d, px, person, scale)}   |   pared: {change(d, px, ~person, scale)}"
                                                 + (f"   ({note})" if note else ""))
        diff.append((str(rel), f"max {d.max()}/{scale}  media {d.mean():.4f}  px distintos {px.mean() * 100:.3f} %"
                               f"  en x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}", split))
    new_files = []
    for top in sorted(d for d in old_root.iterdir() if d.is_dir() and not d.name.startswith(".")):
        for cur in sorted((ROOT / top.name).rglob("*")):
            if cur.is_file() and not cur.name.startswith(".") and cur.suffix.lower() in EXT:
                rel = cur.relative_to(ROOT)
                if not (old_root / rel).exists():
                    new_files.append(str(rel))
    print(f"identicos {len(same)}  distintos {len(diff)}  faltan {len(missing)}"
          + (f"  nuevos {len(new_files)}" if new_files else ""))
    for r, s, split in diff:
        print("DISTINTO", r, s)
        if split:
            print("    ", split)
    for r in missing:
        print("FALTA", r)
    for r in new_files:
        print("NUEVO", r)


if __name__ == "__main__":
    main()
