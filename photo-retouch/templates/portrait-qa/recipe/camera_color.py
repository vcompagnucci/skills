"""El color de la camara sobre mi revelado: matriz, curva y croma sacadas del JPEG de la camara.

Mi revelado del RAW (rawpy, neutro) deja la piel palida y algo magenta (un perfil: croma 11,
matiz 23 grados) al lado del JPEG que hizo la camara (croma 22, matiz 30). Antes eso se
compensaba girando el matiz y subiendo la croma de la piel por franja de brillo, y quedaban
parches lila y amarillos en el menton (el fotografo, QA v6). Despues, una matriz y una sola
saturacion: el promedio de la piel coincidia, pero la mejilla iluminada quedaba con 8 de
croma de mas y la sombra con 8 de menos (v7). El fotografo prefiere la piel de la camara, asi que
ahora todo sale de la camara, en tres pasos globales, iguales para todos los pixeles:

1. Matriz 3x3 de cromaticidades (camera_matrix): el balance de blancos y los matices.
2. Curva de tono (fit_tone): los cuantiles del brillo de la persona en mi revelado llevados
   a los del JPEG. Por cuantiles y no pixel a pixel: no hace falta registrar las dos fotos.
3. Croma y matiz por brillo (fit_chroma): Velvia satura mas la sombra que la luz; una
   ganancia de croma y un giro de matiz por franja de L*, suaves.

Nada se pinta por zonas ni se inventa: es lo que haria un perfil de camara.
"""

import cv2
import numpy as np

from common import linear_to_srgb, luminance, srgb_to_linear
from output import camera_original
from tone import lstar, pchip

FIT = 384  # tamano para la matriz: chico alcanza, y achicar esconde desalineaciones de 1-2 px
Y = np.array([0.2126, 0.7152, 0.0722], np.float32)
QUANTILES = np.array([0.5, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99.5], np.float32)
CHROMA_EDGES = np.arange(5.0, 100.0, 5.0, dtype=np.float32)  # franjas de L* para la croma
MIN_BIN = 300  # pixeles por franja para confiar en ella
GAIN_RANGE = (0.5, 3.0)  # la camara es el techo; esto solo frena una franja con ruido


def camera_matrix(name: str, img: np.ndarray, skin: np.ndarray) -> np.ndarray:
    """Matriz 3x3 (lineal) que lleva el color de `img` (el encuadre abierto) al del JPEG de la camara."""
    ours = cv2.resize(img, (FIT, FIT), interpolation=cv2.INTER_AREA).reshape(-1, 3)
    cam_srgb = camera_original(name, "abierto", FIT).reshape(-1, 3)
    cam = srgb_to_linear(cam_srgb)
    w = cv2.resize(skin, (FIT, FIT), interpolation=cv2.INTER_AREA).reshape(-1) * 4 + 1
    y_o, y_c = ours @ Y, cam @ Y
    ok = (cam_srgb.max(axis=1) < 0.95) & (cam_srgb.min(axis=1) > 0.04) & (y_o > 1e-4)
    x = ours[ok] / y_o[ok, None]  # cromaticidad: la exposicion y la curva de la camara se cancelan
    c = cam[ok] / y_c[ok, None]
    sw = np.sqrt(w[ok])[:, None]
    m, *_ = np.linalg.lstsq(x * sw, c * sw, rcond=None)
    return m.T.astype(np.float32)


def apply_matrix(f: np.ndarray, m: np.ndarray) -> np.ndarray:
    """El color nuevo con el mismo brillo de antes en cada pixel."""
    out = np.maximum(f @ m.T, 0)
    y_in, y_out = f @ Y, out @ Y
    out *= (y_in / np.maximum(y_out, 1e-8))[..., None]
    return out.astype(np.float32)


def fit_mask(alpha: np.ndarray, cam_srgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Persona y pared seguras, lejos del borde (3 % de la cara no alcanza: 1 % del lado) y sin
    canales recortados en el JPEG."""
    n = alpha.shape[0]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * max(2, n // 256) + 1,) * 2)
    person = cv2.erode((alpha > 0.99).astype(np.uint8), k) > 0
    wall = cv2.erode((alpha < 0.01).astype(np.uint8), k) > 0
    ok = (cam_srgb.max(axis=2) < 0.98) & (cam_srgb.min(axis=2) > 0.005)
    return person & ok, wall & ok


def fit_tone(l_ours: np.ndarray, l_cam: np.ndarray, person: np.ndarray, wall: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La curva L* -> L* que lleva mi brillo al de la camara, por cuantiles.

    La persona da la curva de 0 a la piel iluminada; la pared, el tramo de arriba (los pelos
    sobre la pared son una mezcla de los dos). Si la camara no tiene tono local, los dos
    tramos son la misma curva; donde chocan, la regresion isotonica los promedia.
    """
    xs, ys = [], []
    for m in (person, wall):
        if m.sum() < 1000:
            continue
        xs += list(np.percentile(l_ours[m], QUANTILES))
        ys += list(np.percentile(l_cam[m], QUANTILES))
    order = np.argsort(xs)
    x, y = np.array(xs, np.float32)[order], np.array(ys, np.float32)[order]
    y = isotonic_increasing(y)
    # puntos casi iguales en x se juntan: la pchip no admite x repetidas
    keep = np.concatenate([[True], np.diff(x) > 0.5])
    x, y = x[keep], y[keep]
    x = np.concatenate([[0.0], x, [100.0]]).astype(np.float32)
    top = y[-1] + (100 - x[-2]) * max(min((y[-1] - y[-2]) / max(x[-2] - x[-3], 1e-3), 1.5), 0.3)
    y = np.concatenate([[0.0], y, [min(100.0, top)]]).astype(np.float32)
    return x, np.maximum.accumulate(y)


def isotonic_increasing(y: np.ndarray) -> np.ndarray:
    """Regresion isotonica (pool adjacent violators), pesos iguales."""
    blocks = [[float(v), 1] for v in y]
    out: list[list[float]] = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][0] > out[-1][0]:
            v2, w2 = out.pop()
            v1, w1 = out.pop()
            out.append([(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2])
    return np.concatenate([[v] * int(w) for v, w in out]).astype(np.float32)


def tone_table(curve_in: np.ndarray, curve_out: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    xs = np.linspace(0, 100, 2001, dtype=np.float32)
    return xs, np.clip(pchip(curve_in, curve_out, xs), 0, 100).astype(np.float32)


def apply_tone(f: np.ndarray, y: np.ndarray, curve_in: np.ndarray, curve_out: np.ndarray) -> np.ndarray:
    """La curva sobre el brillo de cada pixel, el color (la cromaticidad) igual: como la camara."""
    xs, ys = tone_table(curve_in, curve_out)
    l_out = np.interp(lstar(y), xs, ys).astype(np.float32)
    y_out = np.where(l_out > 8, ((l_out + 16) / 116) ** 3, l_out / 903.3).astype(np.float32)
    return f * (y_out / np.maximum(y, 1e-6))[..., None]


def lab_of(rgb_lin: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.clip(linear_to_srgb(np.clip(rgb_lin, 0, 1)), 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)


def band_stats(lab: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Por franja de L*: pixeles, croma mediana y matiz medio (pesado por croma), en radianes."""
    L, a, b = lab[..., 0][mask], lab[..., 1][mask], lab[..., 2][mask]
    c = np.hypot(a, b)
    idx = np.digitize(L, CHROMA_EDGES) - 1
    k = len(CHROMA_EDGES) - 1
    count, chroma, hue = np.zeros(k), np.zeros(k), np.zeros(k)
    for i in range(k):
        s = idx == i
        count[i] = s.sum()
        if count[i]:
            chroma[i] = np.median(c[s])
            hue[i] = np.angle(np.sum(a[s] + 1j * b[s]))
    return count, chroma, hue


def fit_chroma(lab_ours: np.ndarray, lab_cam: np.ndarray, person: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ganancia de croma y giro de matiz por franja de L*, para que la persona tenga la croma y
    el matiz de la camara en cada brillo. Franjas con pocos pixeles o casi sin color toman el
    valor de la vecina; despues se suaviza con la vecina para que no haya escalones."""
    n_o, c_o, h_o = band_stats(lab_ours, person)
    n_c, c_c, h_c = band_stats(lab_cam, person)
    ok = (n_o >= MIN_BIN) & (n_c >= MIN_BIN) & (c_o > 2) & (c_c > 2)
    centers = (CHROMA_EDGES[:-1] + CHROMA_EDGES[1:]) / 2
    if not ok.any():
        return centers, np.ones_like(centers), np.zeros_like(centers)
    gain = np.clip(c_c / np.maximum(c_o, 1e-3), *GAIN_RANGE)
    turn = np.angle(np.exp(1j * (h_c - h_o)))
    gain = np.interp(centers, centers[ok], gain[ok])
    turn = np.interp(centers, centers[ok], np.unwrap(turn[ok]))
    smooth = np.array([0.25, 0.5, 0.25])
    gain = np.convolve(np.pad(gain, 1, mode="edge"), smooth, "valid")
    turn = np.convolve(np.pad(turn, 1, mode="edge"), smooth, "valid")
    return centers.astype(np.float32), gain.astype(np.float32), turn.astype(np.float32)


def apply_chroma(rgb: np.ndarray, centers: np.ndarray, gain: np.ndarray, turn: np.ndarray) -> np.ndarray:
    """Croma y matiz por el L* de cada pixel: un gris sigue gris (su croma es 0)."""
    if not len(centers):
        return rgb
    lab = lab_of(rgb)
    L, a, b = lab[..., 0], lab[..., 1].copy(), lab[..., 2].copy()
    g = np.interp(L, centers, gain).astype(np.float32)
    t = np.interp(L, centers, turn).astype(np.float32)
    c, s = np.cos(t) * g, np.sin(t) * g
    lab[..., 1] = a * c - b * s
    lab[..., 2] = a * s + b * c
    del a, b, g, t, c, s
    return srgb_to_linear(np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB), 0, 1))


def camera_lstar(cam_srgb: np.ndarray) -> np.ndarray:
    return lstar(luminance(srgb_to_linear(cam_srgb)))
