"""Retoque sobre la base lineal, en este orden:

1. Granos (photos.py `spots`): pincel corrector, uno por uno. Lunares y pecas no se tocan.
2. Pixeles calientes (`hot`).
3. Manchas de la pared (`wall_marks`): las chicas se curan como un grano, las grandes se aclaran.
   Despues, las manchas de color (salpicaduras amarillas): la pared toma su color promedio.
4. Piel, cara por cara (skin.py): rojo, tono, ojeras, brillo y dientes.
5. Pelusas de la ropa negra (lint.py), con su hoja de revision en proceso/20-pelusas.

Salida: work/<foto>-retocada.tif (lineal, float16), work/<foto>-retoque.json, la lista de lo
que se hizo y donde, que el editor muestra como marcas sobre la foto, y work/<foto>-ojeras.npz, la
capa de las ojeras al 100 % de cada cara y la del 200 % (grade.py arma con ellas el control de intensidad).

Uso: .venv/bin/python recipe/retouch.py <foto> [...]
"""

import json
import sys

import numpy as np

from common import WORK, load_linear, save_linear
from heal import fix_hot, heal, wall_mark
from lint import find as find_lint
from lint import remove as remove_lint
from lint import sheet as lint_sheet
from photos import PHOTOS
from skin import retouch_face
from wall import neutral_stains


def save_under_eyes(name: str, layers: dict) -> None:
    """Las capas de cada cara (100 % y, con -200, el tope del editor), recortadas a donde no son
    cero, con su origen en la foto."""
    out = {}
    for fid, part in layers.items():
        ys, xs = np.nonzero(np.any((part["layer"] != 0) | (part["top"] != 0), axis=-1))
        if not len(ys):
            continue
        cut = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        out[fid], out[f"{fid}-200"] = part["layer"][cut], part["top"][cut]
        out[f"{fid}-origen"] = np.array([part["origin"][0] + ys.min(), part["origin"][1] + xs.min()])
    np.savez_compressed(WORK / f"{name}-ojeras.npz", **out)


def retouch(name: str) -> dict:
    img = load_linear(name, "base")
    p = PHOTOS[name]
    for x, y, r in p.get("spots", []):
        heal(img, x, y, r)
    for x, y in p.get("hot", []):
        fix_hot(img, x, y, half=12)
    for x, y, r in p.get("wall_marks", []):
        wall_mark(img, x, y, r)
    neutral_stains(img, name)
    faces, layers = {}, {}
    for f in p["faces"]:
        faces[f["id"]], layers[f["id"]] = retouch_face(img, f)
    save_under_eyes(name, layers)
    del layers
    before = img.copy()
    specks = find_lint(img, name)
    remove_lint(img, specks)
    lint_sheet(name, before, img, specks)
    del before
    save_linear(img, name, "retocada")
    info = {
        "spots": [list(s) for s in p.get("spots", [])],
        "kept": [list(s) for s in p.get("kept", [])],
        "hot": [list(h) for h in p.get("hot", [])],
        "wall_marks": [list(m) for m in p.get("wall_marks", [])],
        "lint": [[s["x"], s["y"]] for s in specks],
        "faces": faces,
    }
    (WORK / f"{name}-retoque.json").write_text(json.dumps(info))
    return info


if __name__ == "__main__":
    for n in sys.argv[1:]:
        info = retouch(n)
        print(
            f"{n}: {len(info['spots'])} granos, {len(info['hot'])} pixeles calientes, "
            f"{len(info['wall_marks'])} manchas de pared, {len(info['lint'])} pelusas, caras {info['faces']}"
        )
