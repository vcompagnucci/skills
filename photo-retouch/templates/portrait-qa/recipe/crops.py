"""Recortes al 100 % de las maestras, para revisar bordes, pared, piel y ropa.

Para cada foto, siete zonas fijas (la cara, el borde del pelo arriba y a los costados, el
borde de la ropa, la pared lejos de la persona y la ropa negra), cada una en el original de
la camara y en cada estilo, a la resolucion nativa: work/qa-v7/<foto>/<zona>-<estilo>.jpg (un zoom
solo no va a proceso/: el fotografo pidio ahi solo lo que muestra lo que se hizo). La tira por zona, con
todos los estilos uno al lado del otro, va a proceso/qa-v7-<foto>-<zona>-tira.jpg.

Uso: .venv/bin/python recipe/crops.py [foto ...]
     .venv/bin/python recipe/crops.py <foto> --at 0.31 0.12 700   # una zona extra: x, y (0..1) y lado
"""

import sys

import cv2
import numpy as np

from common import ROOT
from geometry import crop_box
from output import process_file
from photos import PHOTOS
from styles import MASTER, STYLES

ZOOMS = ROOT / "work" / "qa-v7"  # cada recorte solo
SIDE = 700


def master(name: str, key: str) -> np.ndarray:
    return cv2.imread(str(ROOT / "editadas" / name / f"{name}-{key}.jpg"))


def face_in_master(name: str) -> tuple[float, float, float]:
    ax, ay, aside = crop_box(name, "abierto")
    fx, fy, r = PHOTOS[name]["face"]
    s = MASTER / aside
    return (fx - ax) * s, (fy - ay) * s, r * s


def zones(name: str) -> dict[str, tuple[int, int]]:
    """Centros de cada zona en pixeles de la maestra, a partir de la cara y del alpha."""
    alpha = np.load(ROOT / "work" / f"{name}-abierto-matte.npz")["alpha"].astype(np.float32)
    k = MASTER / alpha.shape[0]
    person = alpha > 0.5
    cx, cy, r = face_in_master(name)

    def row_edges(y: float) -> tuple[float, float]:
        row = np.flatnonzero(person[min(int(y / k), person.shape[0] - 1)])
        return (row[0] * k, row[-1] * k) if row.size else (cx - r, cx + r)

    col = np.flatnonzero(person[:, int(cx / k)])
    top = col[0] * k if col.size else cy - 1.5 * r
    left, right = row_edges(cy)
    hl, hr = row_edges(cy - 0.6 * r)
    sl, sr = row_edges(min(cy + 2.6 * r, MASTER - 1))
    # la pared mas lejos de la persona: la esquina de arriba con mas pared libre
    corner = (int(0.12 * MASTER), int(0.12 * MASTER)) if cx > MASTER / 2 else (int(0.88 * MASTER), int(0.12 * MASTER))
    return {
        "cara": (int(cx), int(cy)),
        "pelo-arriba": (int(cx), int(top)),
        "borde-izquierdo-cara": (int(left), int(cy)),
        "borde-derecho-cara": (int(right), int(cy)),
        "pelo-costado": (int(hl if cx > MASTER / 2 else hr), int(cy - 0.6 * r)),
        "borde-ropa": (int(sl if cx > MASTER / 2 else sr), int(min(cy + 2.6 * r, MASTER - SIDE / 2))),
        "pared-lejos": corner,
        "ropa": (int(cx), int(min(cy + 2.4 * r, MASTER - SIDE / 2))),
    }


def crop(img: np.ndarray, x: int, y: int, side: int = SIDE) -> np.ndarray:
    h = side // 2
    x0, y0 = int(np.clip(x - h, 0, img.shape[1] - side)), int(np.clip(y - h, 0, img.shape[0] - side))
    return img[y0 : y0 + side, x0 : x0 + side]


def label(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (len(text) * 11 + 12, 26), (0, 0, 0), -1)
    cv2.putText(out, text, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def run(name: str, extra: tuple[float, float, int] | None = None) -> None:
    keys = ["original"] + [s.key for s in STYLES]
    imgs = {key: master(name, key) for key in keys}
    zooms = ZOOMS / name
    zooms.mkdir(parents=True, exist_ok=True)
    zs = zones(name)
    side = SIDE
    if extra:
        x, y, side = extra
        zs = {f"extra-{x:.2f}-{y:.2f}": (int(x * MASTER), int(y * MASTER))}
    for zone, (x, y) in zs.items():
        tiles = []
        for key, img in imgs.items():
            c = crop(img, x, y, side)
            cv2.imwrite(str(zooms / f"{zone}-{key}.jpg"), c, [cv2.IMWRITE_JPEG_QUALITY, 95])
            tiles.append(label(cv2.resize(c, (400, 400), interpolation=cv2.INTER_AREA), key))
        cv2.imwrite(str(process_file("qa-v7", f"{name}-{zone}-tira.jpg")), np.concatenate(tiles, axis=1), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(name, ", ".join(f"{z} ({x},{y})" for z, (x, y) in zs.items()))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--at" in args:
        i = args.index("--at")
        run(args[0], (float(args[i + 1]), float(args[i + 2]), int(args[i + 3])))
    else:
        for name in args or list(PHOTOS):
            run(name)
