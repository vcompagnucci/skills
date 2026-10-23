"""Mide tono, fondo, grano y color de un avatar circular.

La misma funcion mide las referencias y los resultados: asi la comparacion es
pareja y un numero fuera de lugar dice que perilla tocar sin tener que mirar.
Todo en L* (0 negro, 100 blanco) sobre el circulo a SIZE px, el tamano al que
estan las capturas de referencia.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

SIZE = 1090

# Recuadros de cara (lado iluminado) y de fondo en cada referencia, en una grilla de 400 px, marcados a mano sobre
# proceso/referencias-ref-<id>.png. Las claves son las `reference` de STYLES (styles.py); los valores de abajo son
# de ejemplo: hay que medirlos en las referencias propias.
REF_FACE = {
    "ref-a": (120, 170, 200, 250),
    "ref-b": (160, 180, 250, 250),
    "ref-c": (140, 190, 280, 230),
}
REF_BG = {
    "ref-a": (20, 200, 60, 280),
    "ref-b": (60, 80, 140, 160),
    "ref-c": (320, 120, 380, 240),
}


@dataclass
class Stats:
    p1: float
    p5: float
    p50: float
    p95: float
    p99: float
    face50: float
    face75: float
    face90: float
    bg: float
    grain: float
    skin_chroma: float

    def row(self) -> str:
        return (
            f"{self.p1:4.0f} {self.p5:4.0f} {self.p50:4.0f} {self.p95:4.0f} {self.p99:4.0f} | "
            f"{self.face50:4.0f} {self.face75:4.0f} {self.face90:4.0f} | {self.bg:4.0f} | "
            f"{self.grain:5.2f} | {self.skin_chroma:4.1f}"
        )


HEADER = "  p1   p5  p50  p95  p99 | cara50 75 90 | fondo | grano | croma piel"


def measure(rgb8: np.ndarray, face: np.ndarray, bg: np.ndarray) -> Stats:
    """rgb8: cuadrado RGB uint8 a SIZE. face y bg: mascaras booleanas al mismo tamano."""
    h, w = rgb8.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    circle = ((xx - w / 2) ** 2 + (yy - h / 2) ** 2) < (0.95 * w / 2) ** 2
    lab = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0] * 100 / 255
    a, b = lab[..., 1] - 128, lab[..., 2] - 128
    p = np.percentile(L[circle], [1, 5, 50, 95, 99])
    f = L[face]
    grain_src = np.where(bg, L, np.nan)
    hp = L - cv2.GaussianBlur(L, (0, 0), 3)
    bg_core = cv2.erode(bg.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    return Stats(
        *[float(v) for v in p],
        float(np.percentile(f, 50)),
        float(np.percentile(f, 75)),
        float(np.percentile(f, 90)),
        float(np.nanmedian(grain_src)),
        float(hp[bg_core].std()) if bg_core.any() else float("nan"),
        float(np.hypot(a[face], b[face]).mean()),
    )


# Franjas de brillo de la piel, en L*. Una piel no tiene un solo color: en la sombra es mas
# roja y en la luz mas amarilla, y un brillo que se vuelve rosa se nota aunque el promedio
# de la cara de bien.
SKIN_BANDS = [(20, 40), (40, 55), (55, 65), (65, 75), (75, 85), (85, 101)]
BAND_CENTERS = np.array([30, 47.5, 60, 70, 80, 92], np.float32)
MIN_BAND_PX = 150


def skin_bands(lab: np.ndarray, mask: np.ndarray) -> list[tuple[int, float, float]]:
    """(pixeles, a*, b*) medio de la piel en cada franja. lab en float (L* 0..100)."""
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    out = []
    for lo, hi in SKIN_BANDS:
        m = mask & (L >= lo) & (L < hi)
        k = int(m.sum())
        out.append((k, float(a[m].mean()) if k else 0.0, float(b[m].mean()) if k else 0.0))
    return out


def box_mask(shape: tuple[int, int], box: tuple[int, int, int, int]) -> np.ndarray:
    s = shape[0] / 400
    x0, y0, x1, y1 = (int(v * s) for v in box)
    m = np.zeros(shape, bool)
    m[y0:y1, x0:x1] = True
    return m


def measure_reference(path: Path, ref: str) -> Stats:
    bgr = cv2.imread(str(path))
    rgb8 = cv2.cvtColor(cv2.resize(bgr, (SIZE, SIZE), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    return measure(rgb8, box_mask((SIZE, SIZE), REF_FACE[ref]), box_mask((SIZE, SIZE), REF_BG[ref]))


# Cara entera (lado iluminado y lado en sombra) en cada referencia: elipse (cx, cy, rx, ry)
# en la grilla de 400 px. Mide la forma de la luz: cuanto mas oscuro el lado en sombra.
REF_FACE_FULL = {
    "ref-a": (150, 205, 50, 80),
    "ref-b": (205, 225, 45, 60),
    "ref-c": (205, 245, 70, 95),
}
# Fondo arriba y abajo (para el degradado), en la grilla de 400 px.
REF_BG_TOP = {
    "ref-a": (20, 120, 50, 170),
    "ref-b": (90, 40, 150, 80),
    "ref-c": (320, 60, 370, 110),
}
REF_BG_BOTTOM = {
    "ref-a": (20, 280, 50, 320),
    "ref-b": (20, 260, 60, 300),
    "ref-c": (10, 200, 40, 240),
}


# Hasta donde baja el fondo en cada referencia (fraccion del alto): mas abajo empieza el
# torso, y un buzo crema puede ser tan liso y claro como la pared.
REF_BG_YMAX = {"ref-a": 0.72, "ref-b": 0.72, "ref-c": 0.70}


def plane_fit(L: np.ndarray, mask: np.ndarray) -> tuple[float, float, float]:
    """El fondo como plano: L* = c0 + cx * x + cy * y, con x e y de 0 a 1 en el cuadro.

    Ajuste robusto (descarta lo que se aleja mas de 2,5 desvios y repite), para que un
    mechon o un borde que se cuele en la mascara no tuerza el plano.
    """
    n = L.shape[0]
    ys, xs = np.nonzero(mask)
    if len(xs) > 40000:
        pick = np.random.default_rng(0).choice(len(xs), 40000, replace=False)
        ys, xs = ys[pick], xs[pick]
    A = np.c_[np.ones(len(xs)), xs / n, ys / n]
    v = L[ys, xs].astype(np.float64)
    keep = np.ones(len(v), bool)
    for _ in range(4):
        coef, *_ = np.linalg.lstsq(A[keep], v[keep], rcond=None)
        r = v - A @ coef
        mad = max(float(np.median(np.abs(r[keep]))) * 1.4826, 0.3)
        keep = np.abs(r) < 2.5 * mad
    return tuple(float(c) for c in coef)


def reference_background(ref: str, L: np.ndarray, face: np.ndarray) -> np.ndarray:
    """Mascara del fondo de una referencia: dentro del circulo, claro, liso y lejos de la cara."""
    n = L.shape[0]
    yy, xx = np.ogrid[:n, :n]
    circle = ((xx - n / 2) ** 2 + (yy - n / 2) ** 2) < (0.93 * n / 2) ** 2
    mean = cv2.blur(L, (9, 9))
    std = np.sqrt(np.maximum(cv2.blur(L * L, (9, 9)) - mean * mean, 0))
    far = cv2.dilate(face.astype(np.uint8), np.ones((n // 12, n // 12), np.uint8)) == 0
    m = circle & (L > 78) & (std < 1.5) & far & (yy < REF_BG_YMAX[ref] * n)
    # Solo lo que toca el borde del circulo: en high-key la frente es tan clara y lisa como
    # la pared, pero queda encerrada por el pelo.
    ring = circle & (((xx - n / 2) ** 2 + (yy - n / 2) ** 2) > (0.8 * n / 2) ** 2)
    k, labels = cv2.connectedComponents(m.astype(np.uint8), connectivity=4)
    touching = np.unique(labels[ring & m])
    return np.isin(labels, touching[touching > 0])


# Contraste local por escala (Shih et al. 2014, Bae et al. 2006): la energia de cada banda
# de una pila laplaciana sobre la cara. Sigmas en pixeles de la grilla de SIZE: la banda k
# va de SIGMAS[k] a SIGMAS[k+1] (la primera, desde el pixel). La ultima (8-16 px, con la
# cara de ~140 px de radio) es el modelado de la cara; las primeras son poros, vello, grano.
BAND_SIGMAS = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0]


def bands(L: np.ndarray, unit: float = 1.0) -> list[np.ndarray]:
    """Pila laplaciana de L*: L = suma de bandas + base. `unit` = pixeles por pixel de SIZE."""
    blurred = [L if s == 0 else cv2.GaussianBlur(L, (0, 0), s * unit) for s in BAND_SIGMAS]
    return [blurred[k] - blurred[k + 1] for k in range(len(BAND_SIGMAS) - 1)]


# Ancho de cara de referencia para medir el contraste por escala: los sigmas de las bandas
# de la cara van en unidades de cara (Shih et al. calibran por distancia entre ojos), asi
# una referencia con la cara mas grande no parece tener mas textura fina que la mia.
FACE_RX = 150.0


def band_energy(L: np.ndarray, mask: np.ndarray, unit: float = 1.0) -> list[float]:
    """Desvio de cada banda dentro de la mascara (cara o fondo), a SIZE px."""
    core = cv2.erode(mask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    return [float(b[core].std()) if core.any() else 0.0 for b in bands(L, unit)]


def light_shape(L: np.ndarray, ellipse_mask: np.ndarray, sigma: float) -> tuple[float, float, float]:
    """p10, p50 y p90 del L* suavizado dentro de la cara: el lado en sombra, el medio y el iluminado."""
    m = ellipse_mask.astype(np.float32)
    low = cv2.GaussianBlur(L * m, (0, 0), sigma) / (cv2.GaussianBlur(m, (0, 0), sigma) + 1e-4)
    core = cv2.erode(ellipse_mask.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    return tuple(float(v) for v in np.percentile(low[core], [10, 50, 90]))


FLAT_LIMIT = 0.6  # L* por unidad de cara: arriba de esto la luz de baja frecuencia cambia rapido (el terminador)


def flat_face(L: np.ndarray, mask: np.ndarray, unit: float) -> np.ndarray:
    """La mascara sin el terminador: donde la luz suave de la cara cambia despacio.

    La energia por escala sobre la cara entera media tambien el paso de la luz a la sombra,
    que en mis fotos (luz lateral dura) es mucho mas fuerte que en las referencias (luz
    frontal suave). Asi la textura no se podia comparar: se comparaba la luz, y las
    ganancias se iban al tope en las dos direcciones (QA v5). Se mide solo donde la
    pendiente de la luz suave es chica, en las dos fotos con el mismo umbral.
    """
    g = cv2.GaussianBlur(L, (0, 0), 8 * unit)
    grad = np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)) / 8 * unit
    flat = mask & (grad < FLAT_LIMIT)
    return flat if flat.sum() > 0.25 * mask.sum() else mask


def upper_face(shape: tuple[int, int], cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    """Frente, ojos y pomulos: la cara por encima de la boca, donde se mide la textura.

    La elipse entera de una referencia incluye el vello facial, y su energia por escala salia inflada por un
    pelo que yo no tengo: igualarla ponia mi piel granulosa.
    """
    m = ellipse_mask(shape, cx, cy, rx * 0.85, ry)
    m[int(cy + 0.2 * ry) :] = False
    return m


def lit_skin(L: np.ndarray, face: np.ndarray, rx: float, q: float = 90) -> float:
    """La piel iluminada: p90 del L* apenas suavizado (sin poros) dentro de la cara.

    Con q=98 da el techo de la piel (el brillo de la frente o el pomulo): la tercera ancla
    de la curva, para que lo iluminado no se aplaste contra el blanco.

    Con un desenfoque grande, en una cara con luz lateral dura la zona iluminada (angosta)
    se mezcla con el lado en sombra y el numero queda bajo; la curva la empujaba hasta
    quemarla. Con un desenfoque chico los ojos, cejas y sombras caen en la cola de abajo y
    el p90 lee la piel.
    """
    # rx/40 es la escala del poro. Con rx/12, en una franja iluminada angosta (retrato con anteojos) el
    # desenfoque mezclaba la sombra; despues de una curva concava ese promedio bajaba 8 L*
    # y el ajuste empujaba la curva contra el blanco (QA v5).
    smooth = cv2.GaussianBlur(L, (0, 0), max(1.0, rx / 40))
    core = cv2.erode(face.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    return float(np.percentile(smooth[core], q))


def ellipse_mask(shape: tuple[int, int], cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    yy, xx = np.ogrid[: shape[0], : shape[1]]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 < 1


def band_contrast(L: np.ndarray, region: np.ndarray, scale: float) -> float:
    """Contraste local (claridad) a la escala de un avatar de 400 px: desvio del pasa-banda."""
    small = cv2.resize(L, (400, 400), interpolation=cv2.INTER_AREA)
    reg = cv2.resize(region.astype(np.uint8), (400, 400), interpolation=cv2.INTER_NEAREST) > 0
    band = cv2.GaussianBlur(small, (0, 0), 1.0) - cv2.GaussianBlur(small, (0, 0), 4.0)
    return float(band[reg].std())


def reference_profile(path: Path, ref: str) -> dict:
    """Todo lo que se copia de una referencia, medido sobre la captura a SIZE px."""
    bgr = cv2.imread(str(path))
    rgb8 = cv2.cvtColor(cv2.resize(bgr, (SIZE, SIZE), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    L = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255
    s = SIZE / 400
    cx, cy, rx, ry = (v * s for v in REF_FACE_FULL[ref])
    face = ellipse_mask(L.shape, cx, cy, rx, ry)
    shape = light_shape(L, face, rx / 4)
    top = float(np.median(L[box_mask(L.shape, REF_BG_TOP[ref])]))
    bottom = float(np.median(L[box_mask(L.shape, REF_BG_BOTTOM[ref])]))
    core = cv2.erode(face.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    levels = np.percentile(L[core], [50, 75, 90])
    lab = cv2.cvtColor(rgb8.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    inner = ellipse_mask(L.shape, cx, cy, rx * 0.8, ry * 0.8)
    bg = box_mask(L.shape, REF_BG_TOP[ref]) | box_mask(L.shape, REF_BG[ref])
    bg_mask = reference_background(ref, L, face) if ref in REF_BG_YMAX else None
    plane = plane_fit(L, bg_mask) if bg_mask is not None else None
    return dict(face_bands=band_energy(L, flat_face(L, upper_face(L.shape, cx, cy, rx, ry), rx / FACE_RX), rx / FACE_RX), face_rx=float(rx), lit=lit_skin(L, face, rx), top=lit_skin(L, face, rx, 98), grain_bands=band_energy(L, bg_mask)[:3] if bg_mask is not None else None,
                skin_a=float(lab[..., 1][inner].mean()), skin_b=float(lab[..., 2][inner].mean()),
                skin_bands=skin_bands(lab, inner), bg_plane=plane,
                bg_a=float(lab[..., 1][bg].mean()), bg_b=float(lab[..., 2][bg].mean()),
                shade10=shape[0], shade50=shape[1], shade90=shape[2], bg_top=top, bg_bottom=bottom,
                clarity=band_contrast(L, face, s),
                face50=float(levels[0]), face75=float(levels[1]), face90=float(levels[2]))
