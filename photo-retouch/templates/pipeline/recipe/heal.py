"""Pincel corrector clasico: granos, manchas, pelusas y pixeles calientes, uno por uno.

Sin IA generativa: el tono se rellena desde lo que rodea al punto (inpaint de Telea) y la
textura se copia de un parche limpio de al lado, para que no quede un manchon liso.
"""

import cv2
import numpy as np

from common import luminance

OFFSETS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]


def _inpaint(win: np.ndarray, hole: np.ndarray, radius: int) -> np.ndarray:
    # inpaint en float32 devuelve basura en OpenCV; en 16 bits anda bien (y sobra precision)
    win16 = np.clip(win * 65535.0, 0, 65535).astype(np.uint16)
    return np.dstack(
        [cv2.inpaint(np.ascontiguousarray(win16[..., k]), hole, radius, cv2.INPAINT_TELEA) for k in range(3)]
    ).astype(np.float32) / 65535.0


def heal(img: np.ndarray, x: int, y: int, r: int) -> None:
    """Cura un punto redondo de radio r (en el lugar). Cerca del borde del cuadro la ventana se
    corta ahi: hay arrugas de la pared a 50 px del borde."""
    pad = 6 * r
    y0, x0 = max(y - pad, 0), max(x - pad, 0)
    win = img[y0 : y + pad, x0 : x + pad]
    cy, cx = y - y0, x - x0
    if not (r + 2 <= cy and r + 2 <= cx and cy + r + 3 <= win.shape[0] and cx + r + 3 <= win.shape[1]):
        raise ValueError(f"punto ({x}, {y}) r{r} pegado al borde")
    hole = np.zeros(win.shape[:2], np.uint8)
    cv2.circle(hole, (cx, cy), r + 1, 1, -1)
    filled = _inpaint(win, hole, r)

    # textura: la del parche vecino mas parecido en brillo y mas parejo (no otra mancha)
    sigma = max(r / 2, 1.5)
    best, best_cost = None, np.inf
    ring = cv2.dilate(hole, np.ones((5, 5), np.uint8)) - hole
    ring_mean = luminance(win)[ring > 0].mean()
    for dist in (2.5, 3.5):
        for ox, oy in OFFSETS:
            sx, sy = int(cx + ox * dist * r), int(cy + oy * dist * r)
            if sy - r - 2 < 0 or sx - r - 2 < 0:  # un indice negativo tomaria el otro lado
                continue
            src = win[sy - r - 2 : sy + r + 3, sx - r - 2 : sx + r + 3]
            if src.shape[:2] != (2 * r + 5, 2 * r + 5):
                continue
            lum = luminance(src)
            cost = abs(lum.mean() - ring_mean) / ring_mean + 3 * lum.std() / max(lum.mean(), 1e-6)
            if cost < best_cost:
                best, best_cost = src, cost
    texture = best - cv2.GaussianBlur(best, (0, 0), sigma)
    patch = filled[cy - r - 2 : cy + r + 3, cx - r - 2 : cx + r + 3] + texture

    alpha = np.zeros((2 * r + 5, 2 * r + 5), np.float32)
    cv2.circle(alpha, (r + 2, r + 2), r + 1, 1.0, -1)
    alpha = cv2.GaussianBlur(alpha, (0, 0), max(r / 3, 1.0))[..., None]
    region = img[y - r - 2 : y + r + 3, x - r - 2 : x + r + 3]
    region[:] = region * (1 - alpha) + patch * alpha


def fill(img: np.ndarray, y0: int, x0: int, hole: np.ndarray) -> None:
    """Rellena una forma cualquiera (una pelusa alargada) desde su contorno, con borde suave.

    hole: mascara uint8 de la ventana que empieza en (y0, x0). Para cosas finas sobre tela,
    donde copiar textura de al lado se notaria mas que el relleno.
    """
    h, w = hole.shape
    win = img[y0 : y0 + h, x0 : x0 + w]
    filled = _inpaint(win, hole, 3)
    alpha = cv2.GaussianBlur(cv2.dilate(hole, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)[..., None]
    win[:] = win * (1 - alpha) + filled * alpha


def lift(img: np.ndarray, x: int, y: int, r: int) -> None:
    """Mancha oscura sobre una superficie lisa (la pared): se la lleva al nivel de alrededor con
    una ganancia suave, canal por canal. No se rellena nada, asi que el grano queda el original.

    El nivel esperado es un plano ajustado sobre un anillo de 1,4r a 2,2r: respeta el degrade de
    la luz sobre la pared. Solo aclara (nunca oscurece) y como mucho un 50 %.
    """
    pad = int(2.4 * r) + 8
    # la ventana se corta en el borde del cuadro: hay manchas a 20 px del borde de arriba
    y0, y1 = max(y - pad, 0), min(y + pad, img.shape[0])
    x0, x1 = max(x - pad, 0), min(x + pad, img.shape[1])
    win = img[y0:y1, x0:x1]
    yy, xx = np.mgrid[y0 - y : y1 - y, x0 - x : x1 - x].astype(np.float32)
    dist = np.hypot(xx, yy)
    # el desenfoque sigue el borde de la mancha (con r/4 quedaba un rastro en el borde de una mancha grande)
    low = cv2.GaussianBlur(win, (0, 0), max(r / 10, 2.0))
    ring = (dist > 1.4 * r) & (dist < 2.2 * r)
    A = np.stack([np.ones(ring.sum(), np.float32), xx[ring], yy[ring]], 1)
    gain = np.ones_like(win)
    for k in range(3):
        coef, *_ = np.linalg.lstsq(A, low[..., k][ring], rcond=None)
        expected = coef[0] + coef[1] * xx + coef[2] * yy
        gain[..., k] = np.clip(expected / np.maximum(low[..., k], 1e-6), 1.0, 1.5)
    m = cv2.GaussianBlur((dist <= 1.15 * r).astype(np.float32), (0, 0), max(r / 4, 1.5))[..., None]
    win[:] = win * (1 + (gain - 1) * m)


SMALL_MARK = 12  # px de radio: hasta aca una mancha de la pared se cura como un grano


def wall_mark(img: np.ndarray, x: int, y: int, r: int) -> None:
    """Mancha de la pared. Una chica se cura como un grano: desaparece entera. Aclarada, de un
    punto chico y hondo quedaba el centro (lo que el filtro suave no ve). Una grande, o pegada al
    borde del cuadro, se aclara: ahi una textura copiada se notaria, y aclarar no deja rastro.
    Una raya se anota como varios puntos chicos a lo largo.
    """
    fits = r + 2 <= y <= img.shape[0] - r - 3 and r + 2 <= x <= img.shape[1] - r - 3
    if r <= SMALL_MARK and fits:
        heal(img, x, y, r)
    else:
        lift(img, x, y, r)


def fix_hot(img: np.ndarray, x: int, y: int, half: int = 7) -> None:
    """Pixel caliente: los pixeles que se apartan mucho de la mediana 5x5 toman la mediana.

    Solo en una ventana chica alrededor del punto anotado: un filtro de mediana sobre toda la
    foto borraria los brillos de los ojos, del reloj y de los remaches.
    """
    win = img[y - half : y + half + 1, x - half : x + half + 1]
    med = np.dstack([cv2.medianBlur(np.ascontiguousarray(win[..., k]), 5) for k in range(3)])
    dev = np.abs(win - med)
    mad = np.median(dev, axis=(0, 1)) + 1e-5
    bad = (dev > 6 * mad).any(axis=2).astype(np.uint8)
    bad = cv2.dilate(bad, np.ones((3, 3), np.uint8)) > 0
    win[bad] = med[bad]
