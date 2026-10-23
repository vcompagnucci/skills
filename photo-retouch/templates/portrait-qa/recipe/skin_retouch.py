"""Retoque de piel y ropa sobre la base lineal, despues de curar los granos.

Cada paso es un dodge & burn automatico, nunca un desenfoque de la piel: se separa una
banda de frecuencias, se corrige solo esa banda y la textura fina (poros, vello) queda
como estaba. Ojos, boca, fosas nasales, pecas y lunares quedan protegidos.

1. Rojo: baja el exceso de rojo de las manchas y rojeces respecto de la piel de al lado.
2. Tono: empareja manchas de luz y sombra de 6 a 12 px (las de la piel, no la forma de
   la cara ni la textura).
3. Ojeras: aclara el bajo-ojo hasta acercarlo a la mejilla, sin borrarlo.
4. Pelusas: saca fibras y puntos claros chicos de la ropa negra.
"""

import cv2
import numpy as np

from common import linear_to_srgb, luminance
from photos import PHOTOS

REDNESS_LOCAL = 0.50  # cuanto del rojo de una mancha se saca
REDNESS_BROAD = 0.15  # cuanto del rojo general de mejillas y nariz
EVENING = 0.35  # cuanto se emparejan las manchas de tono de escala media
UNDER_EYE = 0.40  # cuanto de la diferencia ojera-mejilla se aclara


# Lo minimo que el retoque se aleja del contorno de la persona, en pixeles del RAW. La
# piel cerca del borde se retocaba con la mascara gruesa de persona (rampa de ~20 px), asi
# que el retoque oscurecia la pared pegada al menton hasta 3 L* y aclaraba la piel del
# borde: un contorno con mas contraste que el original (auditoria v7).
EDGE_FENCE = 12


def interior(person: np.ndarray) -> np.ndarray:
    """1 adentro de la persona, lejos del contorno; 0 en el borde y afuera. Borde suave de 3 px."""
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * EDGE_FENCE + 1,) * 2)
    inner = cv2.erode((person > 0.98).astype(np.uint8), disc).astype(np.float32)
    return cv2.GaussianBlur(inner, (0, 0), 3.0)


def norm_blur(x: np.ndarray, w: np.ndarray, sigma: float) -> np.ndarray:
    """Desenfoque que solo promedia piel: los ojos o el pelo no se meten en el promedio."""
    return cv2.GaussianBlur(x * w, (0, 0), sigma) / (cv2.GaussianBlur(w, (0, 0), sigma) + 1e-6)


def face_window(name: str, shape: tuple[int, int]) -> tuple[slice, slice]:
    cx, cy, r = PHOTOS[name]["face"]
    y0, y1 = max(0, int(cy - 1.7 * r)), min(shape[0], int(cy + 2.3 * r))
    x0, x1 = max(0, int(cx - 1.7 * r)), min(shape[1], int(cx + 1.7 * r))
    return slice(y0, y1), slice(x0, x1)


def protected(name: str, shape: tuple[int, int], origin: tuple[int, int]) -> np.ndarray:
    """1 donde no se toca: ojos, boca, fosas nasales, pecas y lunares (con margen)."""
    oy, ox = origin
    m = np.zeros(shape, np.uint8)
    for cx, cy, rx, ry in PHOTOS[name]["features"]:
        cv2.ellipse(m, (cx - ox, cy - oy), (int(rx * 1.3), int(ry * 1.4)), 0, 0, 360, 1, -1)
    for x, y, r in PHOTOS[name]["freckles"]:
        cv2.circle(m, (x - ox, y - oy), r + 5, 1, -1)
    return m.astype(np.float32)


def skin_weight(crop: np.ndarray, name: str, origin: tuple[int, int]) -> np.ndarray:
    """Piel por color (rojo calido, no oscura), sin las zonas protegidas, con borde suave."""
    g = 0.30 / max(float(np.percentile(luminance(crop), 70)), 1e-6)
    lab = cv2.cvtColor((linear_to_srgb(np.clip(crop * g, 0, 1)) * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    L, a = lab[..., 0], lab[..., 1] - 128
    warm = np.clip((a - 3) / 4, 0, 1) * np.clip((L - 60) / 30, 0, 1)
    # El reflejo de la frente o la nariz no tiene rojo y quedaba como un agujero en la piel:
    # el retoque lo rodeaba sin tocarlo y se le marcaba el borde. Se cierran los agujeros.
    r = PHOTOS[name]["face"][2]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r / 5) | 1, int(r / 5) | 1))
    closed = cv2.morphologyEx((warm > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, k).astype(np.float32)
    warm = np.maximum(warm, closed)
    keep = 1 - protected(name, warm.shape, origin)
    return cv2.GaussianBlur(warm * keep, (0, 0), 2.0).astype(np.float32)


def even_redness(crop: np.ndarray, w: np.ndarray, r: float) -> np.ndarray:
    R, G = crop[..., 0], crop[..., 1]
    ratio = np.log(np.maximum(R, 1e-6) / np.maximum(G, 1e-6))
    fine = norm_blur(ratio, w, 3.0)
    local = norm_blur(ratio, w, r / 12)
    median = float(np.median(ratio[w > 0.5]))
    excess = REDNESS_LOCAL * np.maximum(fine - local, 0) + REDNESS_BROAD * np.maximum(local - median, 0)
    out = crop.copy()
    out[..., 0] = R * np.exp(-excess * w)
    return out * (luminance(crop) / np.maximum(luminance(out), 1e-6))[..., None]


def even_tone(crop: np.ndarray, w: np.ndarray) -> np.ndarray:
    log_y = np.log2(np.maximum(luminance(crop), 1e-6))
    # la banda empieza en 6 px y no en 2: desde 2 px se llevaba el 18 % del poro y el vello facial
    # (la piel se veia mas blanda que en el JPEG de la camara, medicion v7)
    band = norm_blur(log_y, w, 6.0) - norm_blur(log_y, w, 12.0)
    return crop * np.exp2(-EVENING * band * w)[..., None]


def lift_under_eyes(crop: np.ndarray, w: np.ndarray, name: str, origin: tuple[int, int]) -> np.ndarray:
    oy, ox = origin
    log_y = np.log2(np.maximum(luminance(crop), 1e-6))
    gain = np.zeros(log_y.shape, np.float32)
    for ex, ey, rx, ry in PHOTOS[name]["features"][:2]:
        ex, ey = ex - ox, ey - oy
        under = np.zeros(log_y.shape, np.float32)
        cheek = np.zeros(log_y.shape, np.uint8)
        cv2.ellipse(under, (ex, int(ey + 1.9 * ry)), (int(1.1 * rx), int(0.9 * ry)), 0, 0, 360, 1.0, -1)
        cv2.ellipse(cheek, (ex, int(ey + 4.2 * ry)), (int(1.1 * rx), int(0.9 * ry)), 0, 0, 360, 1, -1)
        ref = cheek.astype(bool) & (w > 0.5)
        if not ref.any():
            continue
        low = norm_blur(log_y, w, ry * 0.6)
        deficit = np.maximum(float(np.median(low[ref])) - low, 0)
        gain += UNDER_EYE * deficit * cv2.GaussianBlur(under, (0, 0), ry * 0.5) * w
    return crop * np.exp2(gain)[..., None]


def lint_candidates(img: np.ndarray, name: str, person: np.ndarray) -> tuple[int, list[tuple[int, int, int]]]:
    """Pelusas: puntos claros, aislados y neutros sobre tela oscura, debajo de la cara.

    Lo que NO es pelusa y se descarta: grupos de puntos (letras del logo, dientes del
    cierre, costuras), puntos con color (el cierre es dorado) y bordes de la piel (manos).
    Devuelve (y0, [(x, y, componente)]) en coordenadas de la region que empieza en y0.
    """
    cx, cy, r = PHOTOS[name]["face"]
    y0 = int(cy + 1.1 * r)
    region = img[y0:]
    y = luminance(region)
    who = person[y0:] > 0.5
    log_y = np.log2(np.maximum(y, 1e-6))
    surround = cv2.GaussianBlur(y, (0, 0), 15.0)
    dark_fabric = (surround < np.percentile(y[who], 40)) & who
    spike = (log_y - cv2.GaussianBlur(log_y, (0, 0), 4.0) > 0.9) & (log_y - cv2.GaussianBlur(log_y, (0, 0), 15.0) > 0.9)
    cand = (spike & dark_fabric).astype(np.uint8)
    n, labels, stats, cents = cv2.connectedComponentsWithStats(cand)
    # piel cercana (manos, cuello) y color: R/B alto = calido (piel, cierre dorado)
    # (suavizado: en la tela negra el ruido de cada pixel da cualquier color)
    smooth = cv2.GaussianBlur(region, (0, 0), 3.0)
    warmth = np.log(np.maximum(smooth[..., 0], 1e-6) / np.maximum(smooth[..., 2], 1e-6))
    bright = luminance(smooth) > np.percentile(y[who], 70)
    warm_zone = cv2.dilate(((warmth > 0.35) & bright & who).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    # el cierre: dientes chicos, muy claros y dorados (el suavizado los apaga, por eso aparte)
    raw_warm = np.log(np.maximum(region[..., 0], 1e-6) / np.maximum(region[..., 2], 1e-6))
    metal = (raw_warm > 0.25) & (y > np.percentile(y[who], 85)) & who
    metal = cv2.morphologyEx(metal.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    warm_zone |= cv2.dilate(metal, np.ones((31, 31), np.uint8)) > 0
    specks = []
    for i in range(1, n):
        if not 2 <= stats[i, cv2.CC_STAT_AREA] <= 60:
            continue
        x, yy = int(cents[i][0]), int(cents[i][1])
        if warm_zone[yy, x] or warmth[yy, x] > 0.25:
            continue
        specks.append((x, yy, i))
    # aislamiento: si hay 3 o mas puntos a menos de 25 px entre si, es un dibujo, no pelusa
    clusters = np.zeros(y.shape, np.uint8)
    for x, yy, _ in specks:
        cv2.circle(clusters, (x, yy), 25, 1, -1)
    nc, clabels = cv2.connectedComponents(clusters)
    counts = np.bincount(np.array([clabels[yy, x] for x, yy, _ in specks], int), minlength=nc) if specks else []
    isolated = [(x, yy, i) for x, yy, i in specks if counts[clabels[yy, x]] <= 2]
    return y0, isolated, labels


def remove_lint(img: np.ndarray, name: str, person: np.ndarray) -> tuple[np.ndarray, int]:
    y0, specks, labels = lint_candidates(img, name, person)
    out = img.copy()
    region = out[y0:]
    pad = 12
    for x, yy, i in specks:
        sy = slice(max(0, yy - pad), min(region.shape[0], yy + pad))
        sx = slice(max(0, x - pad), min(region.shape[1], x + pad))
        win = np.clip(region[sy, sx] * 65535, 0, 65535).astype(np.uint16)
        msk = cv2.dilate((labels[sy, sx] == i).astype(np.uint8), np.ones((5, 5), np.uint8))
        fixed = np.dstack([cv2.inpaint(np.ascontiguousarray(win[..., k]), msk, 4, cv2.INPAINT_TELEA) for k in range(3)])
        region[sy, sx] = fixed.astype(np.float32) / 65535.0
    return out, len(specks)


def retouch_skin(img: np.ndarray, name: str, person: np.ndarray) -> tuple[np.ndarray, dict]:
    sy, sx = face_window(name, img.shape[:2])
    crop = img[sy, sx]
    origin = (sy.start, sx.start)
    w = skin_weight(crop, name, origin) * interior(person[sy, sx])
    r = PHOTOS[name]["face"][2]
    crop = even_redness(crop, w, r)
    crop = even_tone(crop, w)
    crop = lift_under_eyes(crop, w, name, origin)
    out = img.copy()
    out[sy, sx] = crop
    out, lint = remove_lint(out, name, person)
    return out, {"pelusas": lint, "piel_px": int((w > 0.5).sum())}
