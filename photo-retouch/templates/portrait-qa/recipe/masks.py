"""Mascaras para ajustes locales de luz: fondo, cara y brillos de la piel.

El fondo es un gris liso sin color; la persona es piel (con color) o ropa y pelo
(mas oscuros que el fondo). Se calcula a un cuarto de resolucion y se suaviza al
escalar, que para mover luz alcanza y evita bordes duros.
"""

import cv2
import numpy as np

from common import linear_to_srgb, luminance

def background_mask(img: np.ndarray) -> np.ndarray:
    """1 = fondo, 0 = persona, con bordes suaves. Float32 al tamano de `img`.

    El fondo queda entre un piso y un techo alrededor de su nivel local: el techo
    deja afuera el brillo de la frente, que es casi gris pero mucho mas claro.
    """
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    srgb = (linear_to_srgb(small) * 255).astype(np.uint8)
    lab = cv2.cvtColor(srgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, a, b = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    chroma = np.hypot(a, b)

    # El fondo tiene un degrade de luz: se compara contra su propio nivel local.
    # Nivel del fondo medido en la esquina superior izquierda, que es fondo en las cuatro.
    corner = L[int(0.04 * L.shape[0]) : int(0.16 * L.shape[0]), int(0.04 * L.shape[1]) : int(0.22 * L.shape[1])]
    floor = 0.7 * float(np.median(corner))  # la ropa negra y el pelo son neutros pero mas oscuros
    # La luz principal tine apenas de azul el lado claro del fondo (b* ~ -5): se acepta
    # croma baja siempre que no tire a rojo, que es lo que tiene la piel (a* ~ 13).
    seed = ((chroma < 8) & (a < 3) & (L > floor)).astype(np.uint8)
    seed = cv2.erode(seed, np.ones((9, 9), np.uint8))
    level = cv2.GaussianBlur(L * seed, (0, 0), 30) / (cv2.GaussianBlur(seed.astype(np.float32), (0, 0), 30) + 1e-3)

    # Cerca de la persona el fondo cae en sombra: por eso el margen hacia abajo es amplio.
    # El pelo y la ropa negra quedan afuera por el piso, y la piel por el rojo (a*).
    bg = ((chroma < 9) & (a < 4) & (L > level - 35) & (L < level + 30) & (L > floor)).astype(np.uint8)
    bg = cv2.morphologyEx(bg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    bg = cv2.morphologyEx(bg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(bg)
    keep = np.zeros_like(bg)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 0.01 * bg.size:
            keep[labels == i] = 1
    # Islas chicas de "persona" en medio del fondo (marcas del papel) son fondo.
    person = 1 - keep
    n, labels, stats, _ = cv2.connectedComponentsWithStats(person)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 0.002 * bg.size:
            keep[labels == i] = 1
    soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.5)
    return cv2.resize(soft, (w, h), interpolation=cv2.INTER_LINEAR)


def radial_mask(shape: tuple[int, int], cx: float, cy: float, radius: float, softness: float = 1.0) -> np.ndarray:
    """1 en el centro, cae suave a 0 hacia `radius * (1 + softness)`."""
    h, w = shape
    y, x = np.ogrid[:h, :w]
    d = np.sqrt((x.astype(np.float32) - cx) ** 2 + (y.astype(np.float32) - cy) ** 2) / radius
    t = np.clip((d - 1) / softness, 0, 1)
    return (1 - t * t * (3 - 2 * t)).astype(np.float32)


def vignette(shape: tuple[int, int], strength: float) -> np.ndarray:
    """Multiplicador: 1 en el centro, 1 - strength en las esquinas."""
    h, w = shape
    y, x = np.ogrid[:h, :w]
    x, y = x.astype(np.float32), y.astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    return (1 - strength * d**2.2).astype(np.float32)


def skin_highlights(img: np.ndarray, face: np.ndarray, threshold: float) -> np.ndarray:
    """Brillos de la piel (frente, nariz) dentro de la zona de la cara."""
    lum = cv2.GaussianBlur(luminance(img), (0, 0), 6)
    m = np.clip((lum - threshold) / threshold, 0, 1)
    return (m * face).astype(np.float32)


def guided_filter(guide: np.ndarray, src: np.ndarray, radius: int, eps: float) -> np.ndarray:
    """Filtro guiado (He et al. 2010): suaviza `src` pero pega sus bordes a los de `guide`.

    Sirve para que la mascara del fondo siga el contorno real del pelo y la cara en
    vez de un borde borroso parejo, que deja un halo claro al oscurecer el fondo.
    """
    k = (2 * radius + 1, 2 * radius + 1)
    mean_i = cv2.boxFilter(guide, -1, k)
    mean_p = cv2.boxFilter(src, -1, k)
    corr_ip = cv2.boxFilter(guide * src, -1, k)
    var_i = cv2.boxFilter(guide * guide, -1, k) - mean_i * mean_i
    a = (corr_ip - mean_i * mean_p) / (var_i + eps)
    b = mean_p - a * mean_i
    return cv2.boxFilter(a, -1, k) * guide + cv2.boxFilter(b, -1, k)


def guided_filter_color(guide: np.ndarray, src: np.ndarray, radius: int, eps: float, strip: int = 512) -> np.ndarray:
    """Filtro guiado con guia en color (He et al. 2010, sec. 3.5): el borde de `src` toma la
    forma del borde de color de `guide`, aunque los dos lados tengan el mismo brillo.

    Por franjas de `strip` filas: la covarianza 3x3 por pixel a 4170 px pasaba 1 GB.
    """
    n = src.shape[0]
    out = np.empty_like(src)
    k = (2 * radius + 1, 2 * radius + 1)
    eye = eps * np.eye(3, dtype=np.float32)
    for s0 in range(0, n, strip):
        a0, a1 = max(0, s0 - 2 * radius), min(n, s0 + strip + 2 * radius)
        g, p = guide[a0:a1], src[a0:a1]
        mean_i = [cv2.boxFilter(g[..., c], -1, k) for c in range(3)]
        mean_p = cv2.boxFilter(p, -1, k)
        cov_ip = np.stack([cv2.boxFilter(g[..., c] * p, -1, k) - mean_i[c] * mean_p for c in range(3)], -1)
        var = np.empty(p.shape + (3, 3), np.float32)
        for i in range(3):
            for j in range(i, 3):
                var[..., i, j] = var[..., j, i] = cv2.boxFilter(g[..., i] * g[..., j], -1, k) - mean_i[i] * mean_i[j]
        a = np.linalg.solve(var + eye, cov_ip[..., None])[..., 0]
        b = mean_p - sum(a[..., c] * mean_i[c] for c in range(3))
        q = sum(cv2.boxFilter(np.ascontiguousarray(a[..., c]), -1, k) * g[..., c] for c in range(3)) + cv2.boxFilter(b, -1, k)
        rows = min(strip, n - s0)
        out[s0 : s0 + rows] = q[s0 - a0 : s0 - a0 + rows]
    return out


def background_full(name: str) -> np.ndarray:
    """Mascara de fondo de la foto completa, calculada una vez y guardada en work/.

    Se calcula siempre sobre la imagen entera porque los tamanos de los filtros
    estan pensados para esa escala; los recortes la recortan junto con la foto.
    """
    from common import ROOT, load_base

    path = ROOT / "work" / f"{name}-fondo.png"
    if not path.exists():
        img = load_base(name)
        cv2.imwrite(str(path), (background_mask(img) * 255).astype(np.uint8))
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0


def refine(img: np.ndarray, coarse: np.ndarray) -> np.ndarray:
    """Pega el borde de una mascara gruesa al contorno real de la imagen. 1 = fondo."""
    lum = luminance(img)
    guide = np.sqrt(np.clip(lum / max(float(np.percentile(lum, 99)), 1e-6), 0, 1)).astype(np.float32)
    radius = max(2, img.shape[0] // 300)
    return np.clip(guided_filter(guide, coarse.astype(np.float32), radius, 1e-3), 0, 1).astype(np.float32)




def _gauss(feat: np.ndarray, sample: np.ndarray) -> np.ndarray:
    """Log-verosimilitud de cada pixel bajo una gaussiana ajustada a `sample`."""
    mean = sample.mean(axis=0)
    cov = np.cov(sample.T) + np.eye(sample.shape[1]) * 1e-6
    inv = np.linalg.inv(cov)
    d = feat - mean
    return (-0.5 * np.einsum("...i,ij,...j->...", d, inv, d) - 0.5 * np.log(np.linalg.det(cov))).astype(np.float32)


def skin_chroma_mask(img: np.ndarray, alpha: np.ndarray, geo: tuple[float, float, float]) -> np.ndarray:
    """Peso de piel por color: 1 = piel (iluminada o en sombra), 0 = pelo, vello facial, ropa, pared.

    La mascara vieja (a* > 3) era moteada y entraban el pelo castano y el buzo: el relleno
    de sombra levantaba el pelo junto con la cara. Ahora se aprenden dos modelos en cada
    foto, piel (el centro de la cara, lado iluminado y en sombra) y pelo (arriba de la
    cabeza), sobre la cromaticidad rg y el brillo, y cada pixel va al que mejor lo explica.
    Un solo modelo de la mejilla no alcanza: la luz principal y la de la sombra tienen
    distinto color, y el lado iluminado quedaba afuera (retrato con anteojos).
    """
    n = img.shape[0]
    cx, cy, r = geo
    soft = cv2.GaussianBlur(img, (0, 0), max(1.5, n / 400))
    total = np.maximum(soft.sum(axis=2), 1e-6)
    lum = luminance(soft)
    feat = np.stack([soft[..., 0] / total, soft[..., 1] / total, np.log2(np.maximum(lum, 1e-6)) / 8], axis=2).astype(np.float32)
    yy, xx = np.ogrid[:n, :n]
    solid = alpha > 0.95
    inner = ((((xx - cx) / (0.55 * r)) ** 2 + ((yy - (cy + 0.1 * r)) / (0.6 * r)) ** 2) < 1) & solid
    lo, hi = np.percentile(lum[inner], [15, 98])
    skin = feat[inner & (lum > lo) & (lum < hi)]
    top = (yy < cy - 0.95 * r) & (np.abs(xx - cx) < 1.1 * r) & solid
    hair = feat[top & (lum < np.percentile(lum[top], 95))] if top.sum() > 50 else None
    below = (yy > cy + 2.2 * r) & (np.abs(xx - cx) < 1.5 * r) & solid
    cloth = feat[below] if below.sum() > 50 else None
    ls = _gauss(feat, skin)
    others = [_gauss(feat, s_) for s_ in (hair, cloth) if s_ is not None and len(s_) > 50]
    lo_ = np.maximum.reduce(others) if others else np.full_like(ls, -1e9)
    w = 1 / (1 + np.exp(np.clip(lo_ - ls, -30, 30)))
    region = (((xx - cx) / (1.6 * r)) ** 2 + ((yy - (cy + 0.6 * r)) / (2.2 * r)) ** 2) < 1
    w = w * region * np.clip((alpha - 0.5) / 0.4, 0, 1)
    return cv2.GaussianBlur(w.astype(np.float32), (0, 0), max(1.0, n / 1536)).astype(np.float32)


def key_wall(img: np.ndarray, alpha: np.ndarray, keys: list[tuple[float, float, float, float, float]]) -> np.ndarray:
    """Corrige el alpha donde el matte toma pared por persona: distancia al color de la pared.

    Cada clave es (x, y, medio lado, x e y de una muestra de pared), en pixeles de `img`.
    Adentro de la zona, un pixel del color de la muestra es pared (alpha 0) y uno lejos de
    ese color queda como estaba. Es el viejo croma-key, local: el hueco entre el brazo y la
    mano de un retrato quedaba como persona y no recibia el fondo (QA v4). Solo baja el alpha:
    la version que lo subia (un perfil, v6) marcaba como persona la pared en la sombra del
    menton y dejaba una banda oscura (auditoria v7).
    """
    out = alpha.copy()
    srgb = linear_to_srgb(np.clip(img / max(float(np.percentile(img, 99)), 1e-6), 0, 1))
    n = img.shape[0]
    for x, y, half, sx, sy in keys:
        x0, x1 = int(max(0, x - half)), int(min(n, x + half + 1))
        y0, y1 = int(max(0, y - half)), int(min(n, y + half + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        sx, sy = int(np.clip(sx, 1, n - 2)), int(np.clip(sy, 1, n - 2))
        wall = np.median(srgb[sy - 1 : sy + 2, sx - 1 : sx + 2].reshape(-1, 3), axis=0)
        dist = np.linalg.norm(srgb[y0:y1, x0:x1] - wall, axis=2)
        # umbral suave y corto: la mano (rosada, clara) esta a ~0,2 del color de la pared y un
        # key lineal la aclaraba como si fuera pared en parte
        keyed = np.clip((dist - 0.05) / 0.10, 0, 1).astype(np.float32)
        # sin borde: la correccion se apaga hacia el contorno de la zona, salvo donde la zona
        # toca el borde de la foto (ahi no hay nada con que empalmar)
        far = 10 * n
        def edge(lo, hi, size):
            d = np.arange(hi - lo, dtype=np.float32)
            return np.minimum(d if lo > 0 else far, d[::-1] if hi < size else far)
        ramp = np.minimum.outer(edge(y0, y1, n), edge(x0, x1, n))
        fade = np.clip(ramp / max(2.0, 0.25 * half), 0, 1)
        region = out[y0:y1, x0:x1]
        out[y0:y1, x0:x1] = region * (1 - fade) + np.minimum(region, keyed) * fade
    return out
