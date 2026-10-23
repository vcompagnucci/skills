"""Lo que miraria un retocador en Lightroom sobre la final de 16 bits: histograma, recortes,
pared, piel, ojos, ruido y aberracion cromatica. Solo mide; no cambia nada.

- Histograma: L* en percentiles (los negros de la ropa, los blancos de la pared) y cuanto se
  recorta en 0 o en 65535 (los triangulos de Lightroom).
- Pared: L* y color en cada recuadro de photos.py, y su caida hacia las esquinas (la vineta que
  queda despues del emparejado a medias).
- Piel: la iluminada de cada cara (mediana de L*, a*, b*, tono), para comparar entre fotos.
- Ojos: el blanco del ojo (lo mas claro y sin color adentro de cada ojo) contra la piel.
- Ruido: en la pared y en lo oscuro y liso (ropa negra), el de luz (L*) y el de color (a*, b*),
  medido como el desvio de lo que queda despues de un desenfoque de 1,5 px.
- Aberracion cromatica lateral: corrimiento sub-pixel de R y de B contra G en recuadros con bordes,
  del centro a las esquinas.

Uso: .venv/bin/python tools/lr_audit.py <foto> [...]
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import tifffile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from color_check import skin_pixels  # noqa: E402
from common import EDITED, blur, lab, lightness, luminance, srgb_to_linear  # noqa: E402
from develop import frac_box  # noqa: E402
from faces import ellipse_mask  # noqa: E402
from photos import PHOTOS  # noqa: E402

TILE = 256  # recuadro para la aberracion cromatica
GRID = 7  # recuadros por lado


def robust_std(x: np.ndarray) -> float:
    return float(1.4826 * np.median(np.abs(x - np.median(x)))) if x.size else float("nan")


def noise(lab_img: np.ndarray, m: np.ndarray) -> str:
    """Ruido de luz y de color donde m: lo que queda despues de un desenfoque de 1,5 px."""
    if m.sum() < 500:
        return "sin zona"
    out = []
    for k in range(3):
        ch = lab_img[..., k]
        out.append(robust_std((ch - blur(ch, 1.5))[m]))
    return f"L* {out[0]:.2f}  a* {out[1]:.2f}  b* {out[2]:.2f}  ({int(m.sum())} px)"


def ca_shift(srgb: np.ndarray, H: int, W: int) -> list[tuple[float, float, float]]:
    """(radio 0..1, corrimiento radial de R contra G, de B contra G) en px, por recuadro con bordes."""
    out = []
    for gy in range(GRID):
        for gx in range(GRID):
            y0 = int((H - TILE) * gy / (GRID - 1))
            x0 = int((W - TILE) * gx / (GRID - 1))
            t = srgb[y0 : y0 + TILE, x0 : x0 + TILE].astype(np.float64)
            hp = [c - cv2.GaussianBlur(c, (0, 0), 4) for c in np.moveaxis(t, -1, 0)]
            if np.std(hp[1]) < 0.01:  # sin bordes: la fase no dice nada
                continue
            win = cv2.createHanningWindow((TILE, TILE), cv2.CV_64F)
            cy, cx = y0 + TILE / 2 - H / 2, x0 + TILE / 2 - W / 2
            r = np.hypot(cx, cy)
            if r < 1:
                continue
            ux, uy = cx / r, cy / r
            shifts = []
            for k in (0, 2):
                (dx, dy), resp = cv2.phaseCorrelate(hp[1], hp[k], win)
                shifts.append(dx * ux + dy * uy if resp > 0.2 else np.nan)
            out.append((r / np.hypot(W / 2, H / 2), *shifts))
    return out


def audit(name: str) -> None:
    srgb = tifffile.imread(EDITED / f"{name}.tif")
    H, W = srgb.shape[:2]
    white = float((srgb == 65535).any(-1).mean() * 100)
    black = float((srgb == 0).any(-1).mean() * 100)
    srgb = srgb.astype(np.float32) / 65535
    lin = srgb_to_linear(srgb)
    L = lightness(luminance(lin))
    pct = np.percentile(L[::2, ::2], [0.1, 1, 5, 50, 95, 99, 99.9])
    print(f"{name}  {W}x{H}")
    print(f"  L* p0.1 {pct[0]:.1f}  p1 {pct[1]:.1f}  p5 {pct[2]:.1f}  p50 {pct[3]:.1f}  p95 {pct[4]:.1f}  p99 {pct[5]:.1f}  p99.9 {pct[6]:.1f}")
    print(f"  recorte: blancos {white:.4f} %  negros {black:.4f} %")
    del L

    p = PHOTOS[name]
    for box in p["wall"]:
        Lw, aw, bw = (np.median(v) for v in np.moveaxis(lab(lin[frac_box(box, (H, W))][::2, ::2]), -1, 0))
        print(f"  pared {box}: L* {Lw:.1f}  a* {aw:+.2f}  b* {bw:+.2f}")
    # caida de la pared: L* por bloques de 1/16 donde es pared lisa, centro contra bordes
    small = cv2.resize(lin, (W // 16, H // 16), interpolation=cv2.INTER_AREA)
    Ls, as_, bs = np.moveaxis(lab(small), -1, 0)
    wall_level = float(np.median([np.median(luminance(lin[frac_box(b, (H, W))][::4, ::4])) for b in p["wall"]]))
    flat = np.sqrt(np.maximum(blur(Ls**2, 2) - blur(Ls, 2) ** 2, 0)) < 1.0
    wall = flat & (np.hypot(as_, bs) < 4) & (luminance(small) > 0.5 * wall_level)
    h, w = Ls.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
    bands = [(0, 0.35), (0.35, 0.6), (0.6, 0.8), (0.8, 1.01)]
    vals = [np.median(Ls[wall & (rr >= a) & (rr < b)]) if (wall & (rr >= a) & (rr < b)).sum() > 20 else np.nan for a, b in bands]
    print("  pared por radio (centro -> esquina): " + "  ".join(f"{v:.1f}" for v in vals) + f"   ({int(wall.sum())} bloques)")
    print(f"  pared L* p5 {np.percentile(Ls[wall], 5):.1f}  p50 {np.median(Ls[wall]):.1f}  p95 {np.percentile(Ls[wall], 95):.1f}")

    for face in p["faces"]:
        cx, cy, rx, ry = face["oval"][:4]
        y0, x0 = max(cy - ry, 0), max(cx - rx, 0)
        crop = lin[y0 : cy + ry, x0 : cx + rx]
        cl = lab(crop)
        m = skin_pixels(crop, face, (y0, x0))
        Lf, af, bf = (np.median(cl[..., k][m]) for k in range(3))
        # blanco del ojo: adentro de cada ojo, sin color y lo mas claro
        eyes = ellipse_mask(crop.shape[:2], face["features"][:2], (y0, x0)) > 0.5
        c = np.hypot(cl[..., 1], cl[..., 2])
        cand = eyes & (c < 14)
        sclera = cand & (cl[..., 0] >= np.percentile(cl[..., 0][cand], 80)) if cand.sum() > 50 else cand
        Le, ae, be = (np.median(cl[..., k][sclera]) for k in range(3)) if sclera.sum() else (np.nan,) * 3
        print(f"  {face['id']:<11} piel L* {Lf:.1f}  a* {af:.1f}  b* {bf:.1f}  tono {np.degrees(np.arctan2(bf, af)):.1f}"
              f"   blanco del ojo L* {Le:.1f}  a* {ae:+.1f}  b* {be:+.1f}")

    # ruido: pared (recuadros) y oscuro liso, a resolucion completa en una franja del centro
    walls = []
    for box in p["wall"]:
        part = lab(lin[frac_box(box, (H, W))])
        walls.append(noise(part, np.ones(part.shape[:2], bool)))
    print("  ruido pared: " + " | ".join(walls))
    band = lin[H // 3 : H, W // 4 : 3 * W // 4]
    bl = lab(band)
    flat = np.sqrt(np.maximum(blur(bl[..., 0] ** 2, 6) - blur(bl[..., 0], 6) ** 2, 0)) < 1.5
    dark = flat & (bl[..., 0] < 25) & (np.hypot(bl[..., 1], bl[..., 2]) < 6)
    print(f"  ruido oscuro liso: {noise(bl, dark)}   L* ahi {np.median(bl[..., 0][dark]) if dark.any() else float('nan'):.1f}")
    del bl, band

    shifts = np.array(ca_shift(srgb, H, W))
    if len(shifts):
        for a, b in ((0, 0.5), (0.5, 0.8), (0.8, 1.01)):
            s = shifts[(shifts[:, 0] >= a) & (shifts[:, 0] < b)]
            print(f"  aberracion (radio {a:.1f}-{min(b, 1):.1f}, {len(s)} recuadros): R-G {np.nanmedian(s[:, 1]):+.2f} px  B-G {np.nanmedian(s[:, 2]):+.2f} px"
                  f"   (max |B-G| {np.nanmax(np.abs(s[:, 2])):.2f})" if len(s) else f"  aberracion (radio {a:.1f}-{b:.1f}): sin bordes")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        audit(n)
