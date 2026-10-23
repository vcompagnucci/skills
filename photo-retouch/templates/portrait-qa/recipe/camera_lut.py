"""La LUT 3D de color por foto: el ultimo paso del estilo color, sobre la maestra terminada.

La curva y la matriz de la camara (camera_color.py) dejan el color medio de la piel en su lugar,
pero no los rojos que la camara separa de una piel del mismo brillo: la linea de los labios, las
orejas, las pecas. La LUT (17^3, sRGB) se ajusto por foto sobre la maestra contra el JPEG de la
camara (work/fix3/out/lut-retry/retry.py: 1536 px, fit_mask, prior 0.1, el brillo de cada nivel
neutralizado, oscuros y grises anclados). Se aplica a la imagen entera; en la pared mueve 0.00-0.01 dE.

Entra solo donde paso los tres criterios: estable entre 1536 y 2085 (p99 < 0.5 dE), ninguna zona de
piel que pasaba deja de pasar, y la mancha mejora tambien con su caja fuera del ajuste. Una foto de
la sesion original quedo sin LUT: su oreja retenida empeoraba (1.55 -> 1.67 dE). La de un perfil deja ademas en la identidad
los rojos muy oscuros (L* < 12, work/fix3/out/lut-retry/retry2.py deep12): su boca abierta es una
linea de L* 10 que la LUT comun aclaraba y enrojecia (1.5 -> 2.8 dE). En otras dos esa misma
regla se comia el arreglo de los labios, que son mas claros, asi que solo va en ese perfil.
"""

import numpy as np

from common import ROOT

LUTS = ROOT / "recipe" / "luts"
CHUNK = 1 << 20  # pixeles por tanda: ~100 MB extra a 4170 px


def lut_for(name: str) -> np.ndarray | None:
    path = LUTS / f"{name}-color.npy"
    return np.load(path).astype(np.float32) if path.exists() else None


def corners(x: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Indices planos y pesos de las 8 esquinas trilineales de cada color (x: N x 3 en 0..1)."""
    p = np.clip(x, 0, 1) * (n - 1)
    i0 = np.minimum(p.astype(np.int32), n - 2)
    f = (p - i0).astype(np.float32)
    idx = np.empty((len(x), 8), np.int32)
    wt = np.empty((len(x), 8), np.float32)
    k = 0
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                idx[:, k] = ((i0[:, 0] + dr) * n + (i0[:, 1] + dg)) * n + (i0[:, 2] + db)
                wt[:, k] = (f[:, 0] if dr else 1 - f[:, 0]) * (f[:, 1] if dg else 1 - f[:, 1]) * (f[:, 2] if db else 1 - f[:, 2])
                k += 1
    return idx, wt


def apply_lut(srgb: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """La LUT (n x n x n x 3) sobre una imagen sRGB float 0..1, trilineal y por tandas."""
    flat = srgb.reshape(-1, 3)
    n = lut.shape[0]
    table = lut.reshape(-1, 3)
    out = np.empty(flat.shape, np.float32)
    for s in range(0, len(flat), CHUNK):
        idx, wt = corners(flat[s : s + CHUNK], n)
        out[s : s + CHUNK] = np.einsum("nk,nkc->nc", wt, table[idx])
    return np.clip(out.reshape(srgb.shape), 0, 1)


def camera_lut(name: str, srgb: np.ndarray) -> np.ndarray:
    """La maestra de color con la LUT de su foto, o tal cual si la foto no tiene."""
    lut = lut_for(name)
    return srgb if lut is None else apply_lut(srgb, lut)
