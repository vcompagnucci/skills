"""Puntos del contorno con la camara al lado: camara | mismo render sin aclarar la pared | con.

Los puntos son los de referencia de cada foto (los bordes de la cara, el pelo de arriba y
de costado, la ropa) mas los peores de cada clase segun tools/edge_gate.py. Cada fila lleva
la clase y lo que midio el gate (loma o pozo nuevo en L*, corrimiento del 50 % en px).

Uso: .venv/bin/python tools/edge_montage.py <foto> color salida.png
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recipe"))
from common import ROOT  # noqa: E402
from geometry import crop_box  # noqa: E402
from output import camera_original  # noqa: E402
from photos import PHOTOS  # noqa: E402

GATE = ROOT / "work" / "gate"
H, T = 64, 240  # medio lado del recorte en px de la maestra, lado de cada cuadro


def landmarks(name: str, alpha: np.ndarray) -> list[tuple[str, int, int]]:
    """Bordes de la cara a la altura de los ojos y de la boca, pelo arriba y al costado, ropa."""
    n = alpha.shape[0]
    x0, y0, side = crop_box(name, "abierto")
    fx, fy, r = PHOTOS[name]["face"]
    s = n / side
    cx, cy, r = (fx - x0) * s, (fy - y0) * s, r * s
    person = alpha > 0.5

    def edges(y: float) -> tuple[int, int]:
        row = np.flatnonzero(person[int(np.clip(y, 0, n - 1))])
        return (int(row[0]), int(row[-1])) if row.size else (int(cx - r), int(cx + r))

    col = np.flatnonzero(person[:, int(cx)])
    top = int(col[0]) if col.size else int(cy - 1.5 * r)
    pts = []
    for label, y in (("ojos", cy - 0.1 * r), ("boca", cy + 0.45 * r), ("pelo-costado", cy - 0.6 * r), ("ropa", cy + 2.4 * r)):
        left, right = edges(y)
        pts += [(f"{label}-izq", left, int(y)), (f"{label}-der", right, int(y))]
    pts.append(("pelo-arriba", int(cx), top))
    return [(lb, int(np.clip(x, H, n - H - 1)), int(np.clip(y, H, n - H - 1))) for lb, x, y in pts]


def main(name: str, key: str, out: str) -> None:
    camera_original(name, "abierto", 64)  # deja work/<foto>-camara.jpg
    cam = cv2.imread(str(ROOT / "work" / f"{name}-camara.jpg"))
    no = cv2.imread(str(GATE / f"{name}-{key}-pared-no-final.png"))
    si = cv2.imread(str(GATE / f"{name}-{key}-pared-si-final.png"))
    alpha = np.load(GATE / f"{name}-alpha.npz")["alpha"].astype(np.float32)
    n = si.shape[0]
    x0, y0, side = crop_box(name, "abierto")
    k = max(cam.shape[:2]) / 6240  # la vista previa cubre los 6240 px del lado largo del sensor
    m = side / n
    pts = landmarks(name, alpha)
    worst = json.loads((GATE / f"{name}-{key}-peores.json").read_text()) if (GATE / f"{name}-{key}-peores.json").exists() else {}
    for c, items in worst.items():
        pts += [(f"{c} {e:+.1f}L* {d:+.1f}px", int(np.clip(x, H, n - H - 1)), int(np.clip(y, H, n - H - 1))) for x, y, e, d in items]
    rows = []
    for label, x, y in pts:
        cx, cy, ch = (x0 + x * m) * k, (y0 + y * m) * k, H * m * k
        sc = T / (2 * ch)
        c = cv2.warpAffine(cam, np.float32([[sc, 0, -(cx - ch) * sc], [0, sc, -(cy - ch) * sc]]), (T, T), flags=cv2.INTER_CUBIC)
        tiles = [c] + [cv2.resize(im[y - H : y + H, x - H : x + H], (T, T), interpolation=cv2.INTER_CUBIC) for im in (no, si)]
        row = np.concatenate([tiles[0], np.full((T, 3, 3), 255, np.uint8), tiles[1], np.full((T, 3, 3), 255, np.uint8), tiles[2]], 1)
        cv2.rectangle(row, (0, 0), (len(label) * 8 + 8, 18), (255, 255, 255), -1)
        cv2.putText(row, label, (4, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1, cv2.LINE_AA)
        rows.append(row)
    if len(rows) % 2:
        rows.append(np.full_like(rows[0], 255))
    half = len(rows) // 2
    gap = np.full((T * half, 14, 3), 255, np.uint8)
    cv2.imwrite(out, np.concatenate([np.concatenate(rows[:half], 0), gap, np.concatenate(rows[half:], 0)], 1))
    print(out, len(pts), "puntos")


if __name__ == "__main__":
    main(*sys.argv[1:4])
