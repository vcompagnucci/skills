"""Retoque de piel sobre la base lineal, cara por cara, despues de curar los granos.

Cada paso es un dodge & burn automatico, nunca un desenfoque: se separa una banda de
frecuencias, se corrige solo esa banda, y la textura fina (poros, vello, vello facial) queda como
estaba. Ojos, cejas, boca y fosas nasales quedan protegidos, y nada llega a 12 px del borde
de la piel (faces.skin_mask con fence): el contorno de la cara queda igual que en el RAW.

1. Rojo: baja el exceso de rojo de las manchas y rojeces respecto de la piel de al lado.
2. Tono: empareja manchas de luz y sombra de 6 a 12 px (las de la piel, no la forma de la cara).
3. Ojeras (undereye.py): desde la linea de pestanas para abajo, mas luz y menos violeta, hacia
   la piel de alrededor, sin borrarlas. Sale a la intensidad de la final (undereye.INTENSITY).
4. Brillo: baja el brillo especular de frente, nariz y pomulos, sin aplanar la forma.
5. Dientes (solo si se ven): les saca parte del amarillo, sin blanquearlos.
"""

import cv2
import numpy as np

from common import blur, lab, luminance, norm_blur
from faces import ellipse_mask, skin_mask, window
from undereye import correct as correct_under_eyes

REDNESS_LOCAL = 0.50  # cuanto del rojo de una mancha se saca
REDNESS_BROAD = 0.15  # cuanto del rojo general de mejillas y nariz
EVENING = 0.35  # cuanto se emparejan las manchas de tono de escala media
SHINE = 0.35  # cuanto del brillo especular (lo que pasa un 10 % el entorno) se baja
TEETH = 0.35  # cuanto del croma (el amarillo) de los dientes se saca
EDGE_FENCE = 12
TONE_LIMIT = 0.08  # pasos (log2): mas fuerte que esto es forma, no mancha


def even_redness(crop: np.ndarray, w: np.ndarray, scale: float) -> np.ndarray:
    R, G = crop[..., 0], crop[..., 1]
    ratio = np.log(np.maximum(R, 1e-6) / np.maximum(G, 1e-6))
    fine = norm_blur(ratio, w, 3.0)
    local = norm_blur(ratio, w, scale)
    median = float(np.median(ratio[w > 0.5]))
    excess = REDNESS_LOCAL * np.maximum(fine - local, 0) + REDNESS_BROAD * np.maximum(local - median, 0)
    out = crop.copy()
    out[..., 0] = R * np.exp(-excess * w)
    # mismo brillo: solo cambia el color
    return out * (luminance(crop) / np.maximum(luminance(out), 1e-6))[..., None]


def even_tone(crop: np.ndarray, w: np.ndarray) -> np.ndarray:
    log_y = np.log2(np.maximum(luminance(crop), 1e-6))
    # la banda empieza en 6 px y no en 2: desde 2 px se lleva el poro y el vello facial
    band = norm_blur(log_y, w, 6.0) - norm_blur(log_y, w, 12.0)
    # solo manchas suaves: un borde de forma (la sombra de la nariz, el pliegue de la sonrisa)
    # da una banda mas fuerte y queda como esta. Si no, la cara se aplana (un retrato, nariz).
    band = band * np.exp(-((band / TONE_LIMIT) ** 2))
    return crop * np.exp2(-EVENING * band * w)[..., None]


def reduce_shine(crop: np.ndarray, w: np.ndarray, scale: float) -> np.ndarray:
    """Brillo especular: mas claro que su entorno Y con menos color que la piel (la luz que rebota
    en la grasa es blanca). Lo claro con color es forma (la nariz, el pomulo) y queda como esta.

    Se mide suavizado (2 px) y se baja con una ganancia: el poro adentro del brillo queda.
    """
    y = luminance(crop)
    smooth = norm_blur(y, w, 2.0)
    around = norm_blur(y, w, scale)
    excess = np.maximum(smooth - 1.10 * around, 0)
    rgb = norm_blur(crop, w, 2.0)
    sat = (rgb.max(2) - rgb.min(2)) / np.maximum(rgb.max(2), 1e-6)
    typical = float(np.median(sat[w > 0.5]))
    white = np.clip((typical - sat) / (0.25 * typical), 0, 1)
    gain = 1 - SHINE * white * excess / np.maximum(smooth, 1e-6)
    return crop * (1 - (1 - gain) * w)[..., None]


def teeth_mask(crop: np.ndarray, face: dict, origin: tuple[int, int]) -> np.ndarray:
    """Dientes: adentro de la boca, lo mas claro y menos rojo.

    Medido en un retrato sonriente: los labios dan tono ~25 grados y L* 40-70; los dientes, tono ~35 y L*
    70-80. Los separa sobre todo el brillo, y el tono deja afuera el brillo de los labios.
    """
    mouth = ellipse_mask(crop.shape[:2], [face["features"][5]], origin)
    inside = mouth > 0
    k = 0.18 / max(float(np.median(luminance(crop)[inside])), 1e-6)
    L, a, b = np.moveaxis(lab(np.clip(crop * k, 0, None)), -1, 0)
    hue = np.degrees(np.arctan2(b, a))
    light = np.clip((L - np.percentile(L[inside], 75)) / 6, 0, 1)
    less_red = np.clip((hue - 28) / 6, 0, 1)
    return blur(light * less_red * mouth, 1.0)


def clean_teeth(crop: np.ndarray, m: np.ndarray) -> np.ndarray:
    y = luminance(crop)[..., None]
    return y + (crop - y) * (1 - TEETH * m)[..., None]


def retouch_face(img: np.ndarray, face: dict, kept=()) -> tuple[dict, dict]:
    """Retoca una cara en el lugar. Devuelve cuanta piel toco (para el editor) y las capas de las
    ojeras al 100 y al 200 % con su origen en la foto (para las puntas del control del editor).
    kept: los lunares y pecas que quedan (photos.py), afuera de la mascara de piel. Las ojeras usan
    su propia mascara (undereye.skin_weight) y no los ven."""
    sy, sx = window(face, img.shape[:2])
    crop = img[sy, sx].copy()
    origin = (sy.start, sx.start)
    w = skin_mask(crop, face, origin, fence=EDGE_FENCE, kept=kept)
    rx = face["oval"][2]
    crop = even_redness(crop, w, rx / 12)
    crop = even_tone(crop, w)
    crop, eyes, layer, top = correct_under_eyes(crop, face, origin)
    crop = reduce_shine(crop, w, rx / 8)
    info = {"skin_px": int((w > 0.5).sum()), "under_eyes": eyes}
    if face.get("teeth"):
        t = teeth_mask(crop, face, origin)
        crop = clean_teeth(crop, t)
        info["teeth_px"] = int((t > 0.5).sum())
    img[sy, sx] = crop
    return info, {"origin": origin, "layer": layer, "top": top}
