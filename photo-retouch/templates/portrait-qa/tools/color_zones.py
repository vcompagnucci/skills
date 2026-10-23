"""El color de la persona contra el JPEG de la camara: por zonas de la cara y por franjas de brillo.

Zonas fijas (frente, mejillas, debajo de los ojos, labio de arriba, menton, cuello), puestas
con la cara y los rasgos de photos.py y recortadas a la piel, mas la piel por franjas de L*
de la camara. En cada una: L*, C*, h de la camara y de la edicion, y la diferencia. Pasa si
cada zona queda en +-1,5 L*, +-1,5 C* y +-3 grados.

Uso: .venv/bin/python tools/color_zones.py <foto> color
Lee work/gate/<foto>-<estilo>-pared-si-final.png y work/gate/<foto>-alpha.npz (con la piel).
"""

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
TOL = (1.5, 1.5, 3.0)  # L*, C*, grados


def lab(srgb8: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(srgb8.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def stats(lab_: np.ndarray, m: np.ndarray) -> tuple[float, float, float]:
    L, a, b = (lab_[..., i][m] for i in range(3))
    return float(np.median(L)), float(np.median(np.hypot(a, b))), float(np.degrees(np.angle(np.sum(a + 1j * b))))


def zones(name: str, n: int) -> dict[str, tuple[float, float, float]]:
    """Centro y radio de cada zona en pixeles del encuadre abierto a `n` px."""
    x0, y0, side = crop_box(name, "abierto")
    s = n / side
    fx, fy, r = PHOTOS[name]["face"]
    eyes = sorted(PHOTOS[name]["features"][:2])
    mouth = PHOTOS[name]["features"][2]
    ex = [(e[0], e[1]) for e in eyes]
    mid_eye = ((ex[0][0] + ex[1][0]) / 2, (ex[0][1] + ex[1][1]) / 2)
    z = {
        "frente": (mid_eye[0], mid_eye[1] - 0.45 * r, 0.09 * r),
        "ojera izq": (ex[0][0], ex[0][1] + 0.17 * r, 0.05 * r),
        "ojera der": (ex[1][0], ex[1][1] + 0.17 * r, 0.05 * r),
        "mejilla izq": (ex[0][0] - 0.05 * r, ex[0][1] + 0.42 * r, 0.08 * r),
        "mejilla der": (ex[1][0] + 0.05 * r, ex[1][1] + 0.42 * r, 0.08 * r),
        "labio sup": (mouth[0], mouth[1] - mouth[3] - 0.07 * r, 0.04 * r),
        "menton": (mouth[0], mouth[1] + mouth[3] + 0.2 * r, 0.07 * r),
        "cuello": (fx, fy + 1.35 * r, 0.12 * r),
    }
    return {k: ((x - x0) * s, (y - y0) * s, rr * s) for k, (x, y, rr) in z.items()}


def main(name: str, key: str) -> bool:
    ours = cv2.cvtColor(cv2.imread(str(GATE / f"{name}-{key}-pared-si-final.png")), cv2.COLOR_BGR2RGB)
    n = ours.shape[0]
    data = np.load(GATE / f"{name}-alpha.npz")
    alpha, skin = data["alpha"].astype(np.float32), data["skin"].astype(np.float32)
    cam = (camera_original(name, "abierto", n) * 255 + 0.5).astype(np.uint8)
    lo, lc = lab(ours), lab(cam)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    inside = cv2.erode((alpha > 0.99).astype(np.uint8), k) > 0
    is_skin = inside & (skin > 0.5)
    yy, xx = np.mgrid[0:n, 0:n]
    ok_all = True
    print(f"{name} {key}: zona          camara L/C/h        edicion L/C/h       dL    dC    dh")
    rows = []
    for label, (cx, cy, rr) in zones(name, n).items():
        m = is_skin & ((xx - cx) ** 2 + (yy - cy) ** 2 <= rr**2)
        if m.sum() < 200:
            print(f"  {label:12s} (sin piel suficiente: {int(m.sum())} px)")
            continue
        rows.append((label, stats(lc, m), stats(lo, m)))
    edges = np.percentile(lc[..., 0][is_skin], [5, 25, 50, 75, 95])
    for i in range(4):
        m = is_skin & (lc[..., 0] >= edges[i]) & (lc[..., 0] < edges[i + 1])
        rows.append((f"piel L {edges[i]:.0f}-{edges[i + 1]:.0f}", stats(lc, m), stats(lo, m)))
    for label, c, o in rows:
        d = (o[0] - c[0], o[1] - c[1], (o[2] - c[2] + 180) % 360 - 180)
        ok = all(abs(v) <= t for v, t in zip(d, TOL))
        ok_all &= ok
        print(f"  {'PASA ' if ok else 'FALLA'} {label:16s} {c[0]:5.1f} {c[1]:5.1f} {c[2]:5.1f}   {o[0]:5.1f} {o[1]:5.1f} {o[2]:5.1f}   {d[0]:+5.1f} {d[1]:+5.1f} {d[2]:+5.1f}")
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:]) else 1)
