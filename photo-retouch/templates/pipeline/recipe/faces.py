"""Mascaras de cada cara, dibujadas desde coordenadas (sin deteccion automatica).

- El ovalo de la cara (`oval`) limita todo el retoque de piel.
- Los rasgos (`features`: ojos, cejas, boca, fosas nasales) quedan protegidos: el retoque
  no los toca.
- La piel adentro del ovalo se elige por color, con borde suave: el pelo, el vello facial cerrado
  y la ropa no son piel.
"""

import cv2
import numpy as np

from common import blur, lab, luminance


def ellipse_mask(shape: tuple[int, int], ellipses: list, origin: tuple[int, int], grow: float = 1.0) -> np.ndarray:
    """1 adentro de cualquiera de las elipses (cx, cy, rx, ry[, angulo]), en una ventana que empieza en origin."""
    oy, ox = origin
    m = np.zeros(shape, np.uint8)
    for e in ellipses:
        cx, cy, rx, ry = e[:4]
        ang = e[4] if len(e) > 4 else 0
        cv2.ellipse(m, (int(cx - ox), int(cy - oy)), (int(rx * grow), int(ry * grow)), ang, 0, 360, 1, -1)
    return m.astype(np.float32)


def window(face: dict, shape: tuple[int, int], pad: float = 0.15) -> tuple[slice, slice]:
    cx, cy, rx, ry = face["oval"][:4]
    r = max(rx, ry) * (1 + pad)
    y0, y1 = max(0, int(cy - r)), min(shape[0], int(cy + r))
    x0, x1 = max(0, int(cx - r)), min(shape[1], int(cx + r))
    return slice(y0, y1), slice(x0, x1)


def skin_mask(crop: np.ndarray, face: dict, origin: tuple[int, int], fence: int = 0) -> np.ndarray:
    """Piel: adentro del ovalo, sin rasgos, y con color de piel (calida, no oscura). Suave, 0..1.

    fence: cuantos pixeles se aleja la mascara del borde de la piel (pelo, vello facial, pared). El
    retoque usa 12: asi nunca toca el contorno de la cara, que queda igual que en el RAW.
    """
    oval = ellipse_mask(crop.shape[:2], [face["oval"]], origin)
    # la piel de esta cara define su propio rango de brillo y color
    y = luminance(crop)
    ref = oval > 0
    k = 0.18 / max(float(np.median(y[ref])), 1e-6)  # la cara a un gris medio, solo para medir
    L, a, b = np.moveaxis(lab(np.clip(crop * k, 0, None)), -1, 0)
    hue = np.degrees(np.arctan2(b, a))
    chroma = np.hypot(a, b)
    warm = np.clip((chroma - 4) / 4, 0, 1) * np.clip(1 - np.abs(hue - 55) / 45, 0, 1)
    bright = np.clip((L - 22) / 12, 0, 1)
    m = warm * bright * oval
    # los reflejos (frente, nariz) casi no tienen croma: se cierran los huecos de la mascara
    rx = face["oval"][2]
    kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(rx / 6) | 1,) * 2)
    closed = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, kk).astype(np.float32) * oval
    m = np.maximum(m, closed)
    if fence:
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * fence + 1,) * 2)
        m = np.minimum(m, cv2.erode((m > 0.5).astype(np.uint8), disc).astype(np.float32))
    keep = 1 - ellipse_mask(crop.shape[:2], face.get("features", []), origin, grow=1.15)
    return blur(m * keep, 3.0 if fence else 1.5).astype(np.float32)
