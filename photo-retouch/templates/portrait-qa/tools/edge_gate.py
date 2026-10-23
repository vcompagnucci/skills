"""Prueba del borde: ¿el contorno de la edicion es el de la foto original?

Sobre todo el contorno de la persona (alpha 0.5), una normal cada 8 px con un perfil de
+-14 px en RGB lineal, en el render con la pared aclarada y en el mismo render sin aclararla
(misma curva y color: la curva sola ya mueve el 50 % y el ancho de una rampa lineal). En
cada perfil de la base, el alpha por la recta de color entre la pared (t < -8) y la persona
(t > 8); en la edicion, el alpha que uso el aclarado (lift_alpha), que no se confunde cuando
el contraste se da vuelta.
Cada normal se clasifica por la persona de su lado: piel (el mapa de piel de la escena,
o calida y clara si no esta), oscuro (buzo,
pelo denso) o intermedio. Pasa si, por clase (mediana de las diferencias con - sin):
  |d50| <= 0.3 px (p90 <= 0.6) · d(10-90) en [-0.3, +0.5] px · pozo/loma nuevo <= 1 L*
  (pelo e intermedio: <= 1.8, el pelo con huecos deja ver la pared aclarada) · a*, b*
  minimos en la rampa >= los de la base - 1.

Uso: .venv/bin/python tools/edge_gate.py <foto> color [crudo|final]
Lee work/gate/<foto>-<estilo>-pared-{si,no}-<etapa>.png y work/gate/<foto>-alpha.npz;
guarda los peores puntos de cada clase en work/gate/<foto>-<estilo>-peores.json.
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recipe"))
from common import ROOT, srgb_to_linear  # noqa: E402

GATE = ROOT / "work" / "gate"
LIMITS = {"piel": 1.0, "oscuro": 1.0, "intermedio": 1.8}  # pozo/loma nuevo, L*
STEP = 8


def read_linear(path: Path) -> np.ndarray:
    return srgb_to_linear(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255)


def lab(lin: np.ndarray) -> np.ndarray:
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(np.clip(lin, 0, None), 1 / 2.4) - 0.055)
    return cv2.cvtColor(np.clip(s, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)


def profile_stats(p: np.ndarray, t: np.ndarray) -> tuple:
    B, F = np.median(p[t < -8], axis=0), np.median(p[t > 8], axis=0)
    d = F - B
    a = (p - B) @ d / max(float(d @ d), 1e-12)

    def cross(level: float) -> float:
        idx = np.where((a[:-1] - level) * (a[1:] - level) <= 0)[0]
        if not len(idx):
            return np.nan
        i = idx[np.argmin(np.abs(t[idx]))]
        return float(t[i] + (level - a[i]) / (a[i + 1] - a[i] + 1e-9) * (t[1] - t[0]))

    Lp = lab(p[None])[0]
    LB, LF = lab(B[None, None])[0, 0], lab(F[None, None])[0, 0]
    lo, hi = min(LB[0], LF[0]), max(LB[0], LF[0])
    ramp = (a > 0.05) & (a < 0.95)
    mina = Lp[ramp, 1].min() - min(LB[1], LF[1]) if ramp.any() else np.nan
    minb = Lp[ramp, 2].min() - min(LB[2], LF[2]) if ramp.any() else np.nan
    return (cross(0.5), abs(cross(0.9) - cross(0.1)), max(lo - Lp[:, 0].min(), 0), max(Lp[:, 0].max() - hi, 0), mina, minb, *LF)


def lift_alpha(base: np.ndarray, edit: np.ndarray, t: np.ndarray) -> tuple:
    """El alpha que uso la edicion, leido del perfil: 1 - aclarado / aclarado de la pared pura.

    I' = I + (1 - alpha)(g - 1)B, asi que (I' - I) sobre su valor en la pared (t < -8) es
    1 - alpha. No depende del signo del contraste: cuando la piel es mas clara que la pared
    en la base y mas oscura despues de aclararla (un perfil en blanco y negro), la
    rampa de la edicion se da vuelta y su 10-90 % deja de medir el borde (gate v7).
    Devuelve (50 %, 10-90 %) del alpha, o nan si la pared casi no se aclaro.
    """
    lift = edit - base
    wall = np.median(lift[t < -8], axis=0)
    if float(wall @ wall) < 1e-4:
        return np.nan, np.nan
    a = 1 - lift @ wall / float(wall @ wall)

    def cross(level: float) -> float:
        idx = np.where((a[:-1] - level) * (a[1:] - level) <= 0)[0]
        if not len(idx):
            return np.nan
        i = idx[np.argmin(np.abs(t[idx]))]
        return float(t[i] + (level - a[i]) / (a[i + 1] - a[i] + 1e-9) * (t[1] - t[0]))

    return cross(0.5), abs(cross(0.9) - cross(0.1))


def normals(alpha: np.ndarray) -> list[tuple[int, int, float, float]]:
    a = cv2.GaussianBlur(alpha, (0, 0), 2.0)
    cs, _ = cv2.findContours((a > 0.5).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    gx, gy = cv2.Sobel(a, cv2.CV_32F, 1, 0), cv2.Sobel(a, cv2.CV_32F, 0, 1)
    n = alpha.shape[0]
    out = []
    for c in cs:
        if len(c) < 40:  # motas sueltas del pelo: no son el contorno
            continue
        for x, y in c[::STEP, 0, :]:
            if min(x, y) < 20 or max(x, y) > n - 21:
                continue
            g = np.hypot(gx[y, x], gy[y, x])
            if g > 1e-4:
                out.append((int(x), int(y), float(gx[y, x] / g), float(gy[y, x] / g)))
    return out


def main(name: str, key: str, stage: str = "crudo") -> bool:
    edit = read_linear(GATE / f"{name}-{key}-pared-si-{stage}.png")
    base = read_linear(GATE / f"{name}-{key}-pared-no-{stage}.png")
    data = np.load(GATE / f"{name}-alpha.npz")
    alpha = data["alpha"].astype(np.float32)
    skin = data["skin"].astype(np.float32) if "skin" in data else None
    t = np.arange(-14, 14.01, 0.25, dtype=np.float32)
    rows, pts = [], []
    norms = normals(alpha)
    for x, y, nx, ny in norms:
        mx = (x + t * nx).astype(np.float32)[None, :]
        my = (y + t * ny).astype(np.float32)[None, :]
        pb, pe = cv2.remap(base, mx, my, cv2.INTER_LINEAR)[0], cv2.remap(edit, mx, my, cv2.INTER_LINEAR)[0]
        sb, se = profile_stats(pb, t), profile_stats(pe, t)
        rows.append(sb + se + lift_alpha(pb, pe, t))
        pts.append((x, y))
    r, pts = np.array(rows, np.float64), np.array(pts)
    LF = r[:, 6:9]  # la persona en la base: L*, a*, b*
    if skin is None:
        is_skin = (LF[:, 1] > 6) & (LF[:, 0] > 40)
    else:  # el mapa de piel de la escena, 8 px adentro: vale tambien en blanco y negro
        nrm = np.array([(nx, ny) for _, _, nx, ny in norms])
        sx = np.clip(np.round(pts[:, 0] + 8 * nrm[:, 0]).astype(int), 0, alpha.shape[1] - 1)
        sy = np.clip(np.round(pts[:, 1] + 8 * nrm[:, 1]).astype(int), 0, alpha.shape[0] - 1)
        is_skin = skin[sy, sx] > 0.5
    cls = np.where(is_skin, "piel", np.where(LF[:, 0] < 30, "oscuro", "intermedio"))
    # posicion y ancho: el alpha usado contra el borde de la base; si la pared no se aclaro, la
    # rampa de la edicion contra la de la base
    lifted = ~np.isnan(r[:, 18])
    d50 = np.where(lifted, r[:, 18], r[:, 9]) - r[:, 0]
    dw = np.where(lifted, r[:, 19], r[:, 10]) - r[:, 1]
    dext = np.maximum(r[:, 11] - r[:, 2], r[:, 12] - r[:, 3])
    mina = r[:, 13] - np.minimum(r[:, 4], 0)
    minb = r[:, 14] - np.minimum(r[:, 5], 0)
    ok_all, worst = True, {}
    print(f"{name} {key} ({stage}): {len(r)} normales")
    for c in ("piel", "oscuro", "intermedio"):
        k = cls == c
        if k.sum() < 5:
            continue
        med = lambda v: float(np.nanmedian(v[k]))  # noqa: E731
        p90 = lambda v: float(np.nanpercentile(v[k], 90))  # noqa: E731
        checks = {
            "posicion 50 %": (abs(med(d50)) <= 0.3 and p90(np.abs(d50)) <= 0.6, f"{med(d50):+.2f} px (p90 |d| {p90(np.abs(d50)):.2f})"),
            "ancho 10-90 %": (-0.3 <= med(dw) <= 0.5, f"{med(dw):+.2f} px"),
            "pozo/loma nuevo": (med(dext) <= LIMITS[c], f"{med(dext):.2f} L* (p90 {p90(dext):.2f})"),
            "a*, b* en la rampa": (min(med(mina), med(minb)) >= -1, f"{med(mina):+.2f}, {med(minb):+.2f}"),
        }
        print(f"  {c}: {int(k.sum())} normales")
        for name_, (ok, txt) in checks.items():
            print(f"     {'PASA ' if ok else 'FALLA'} {name_}: {txt}")
            ok_all &= ok
        idx = np.flatnonzero(k)
        by_ext = idx[np.argsort(-np.nan_to_num(dext[idx]))[:3]]
        by_pos = idx[np.argsort(-np.nan_to_num(np.abs(d50[idx])))[:2]]
        worst[c] = [[int(v) for v in pts[i]] + [round(float(dext[i]), 1), round(float(d50[i]), 1)] for i in [*by_ext, *by_pos]]
    (GATE / f"{name}-{key}-peores.json").write_text(json.dumps(worst))
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:]) else 1)
