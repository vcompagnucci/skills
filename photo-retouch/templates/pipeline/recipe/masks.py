"""Mascaras para separar a la gente de la pared: la mascara gruesa del fondo y el filtro guiado.

Copiadas de un proyecto anterior de retratos (portrait-qa/recipe/masks.py en estas plantillas), donde se validaron con el matting
(matte.py). La mascara gruesa solo arma el trimapa: el contorno fino lo resuelve el matting.
"""

import cv2
import numpy as np

from common import linear_to_srgb, luminance  # noqa: F401  (matte.py toma luminance de aca)


FLOOR = 0.35  # el piso de brillo del fondo, en fraccion de la esquina de arriba a la izquierda
# El color que se acepta como pared (a*, b* de OpenCV, ~ unidades Lab): de neutro a amarillo. Abajo,
# lejos del flash, la pared y el piso de estas fotos tiran a calido (b* +7 a +9 a ~45 L*), y con la
# croma < 9 del proyecto anterior quedaban como persona a manchas. Lo que queda afuera: la piel por el rojo
# (a* ~13) y el jean por el azul (b* < -6).
WALL_A = (-4, 4)
WALL_B = (-6, 12)
# Huecos: la pared que se ve entre un brazo y el cuerpo, entre las patas de la banqueta o entre la mano y
# la pierna. Encerrados por la gente no llegan al 1 % de la foto, quedaban como persona y el fondo nuevo
# no les llegaba: pared gris vieja en el blanco (piloto, 11 huecos en las cuatro).
# Brillo en unidades del L de OpenCV (L* x 2,55), como el resto de la mascara.
HOLE_MIN = 2e-5  # area minima, en fraccion de la foto (~30 px a 1/4: unos 20 px nativos de lado)
HOLE_SHADE = 90  # cuanto mas oscuro que la pared puede estar un hueco (35 L*): el triangulo entre las piernas de la foto de grupo
HOLE_STD = 2.5  # textura maxima: mediana del desvio de L en 5x5, contando solo el hueco (el papel es liso)
# El borde del hueco (la gente) mas oscuro que el hueco: al menos HOLE_RING[0] si es liso, y HOLE_RING[1] si
# no se puede medir la textura (un hueco angosto es todo borde). Medido en el piloto: los huecos de verdad,
# 89-176; la zapatilla blanca en sombra, 33-58.
HOLE_RING = (10, 70)
HOLE_HEAD = (2.2, 2.6)  # alrededor de cada cara (en radios de su elipse) no hay huecos: ahi esta el pelo
# En un recuadro marcado a mano, lo que esta lejos de la pared marcada y es mas oscuro que HAND_DARK (18 L*) es
# persona segura: la remera negra y el pelo (8-15 L*). La pared mas oscura de esos huecos esta en 27 L*, y un pelo
# suelto sobre la pared, a 1/4, promedia mas claro. HAND_RING (px a 1/4) alrededor de la pared queda para el matting.
HAND_DARK = 18 * 2.55
HAND_RING = 2


def background_mask(img: np.ndarray, faces=(), hand=(), sure=(), with_hand: bool = False):
    """1 = fondo, 0 = persona, con bordes suaves. Float32 al tamano de `img`. Con with_hand, ademas lo que dicen
    los recuadros `sure` (photos.py, backdrop_sure), al tamano de `img`: 0 = pared segura, 1 = persona segura,
    0.5 = adentro de un recuadro sin decidir, -1 = afuera (sin opinion). El matting lo toma como seguro.

    El fondo queda entre un piso y un techo alrededor de su nivel local: el techo
    deja afuera el brillo de la frente, que es casi gris pero mucho mas claro.
    `faces` (cx, cy, rx, ry a la escala de `img`) marca las cabezas, donde no se buscan huecos.
    `hand` son los huecos marcados a mano (photos.py, `backdrop_holes`: x0, y0, x1, y1 a la escala
    de `img`): adentro, todo lo que tiene color de pared es pared, sin techo ni pruebas de borde.
    `sure` (backdrop_sure), lo mismo, y ademas la opinion de arriba.
    """
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    srgb = (linear_to_srgb(small) * 255).astype(np.uint8)
    lab = cv2.cvtColor(srgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, a, b = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128

    # El fondo tiene un degrade de luz: se compara contra su propio nivel local.
    # Nivel del fondo medido en la esquina superior izquierda, que es fondo en las cuatro.
    corner = L[int(0.04 * L.shape[0]) : int(0.16 * L.shape[0]), int(0.04 * L.shape[1]) : int(0.22 * L.shape[1])]
    # La ropa negra y el pelo son neutros pero mas oscuros. En el proyecto anterior el piso era 0,7 de la
    # esquina; aca la pared cae hasta ~45 L* abajo a la derecha y el piso en sombra de la foto de grupo a ~34 (la
    # caida del flash), y quedaban como persona. La ropa negra, el banco y el pelo: L* < 15. Cerca de
    # la gente manda el nivel local (L > level - 35), no el piso.
    floor = FLOOR * float(np.median(corner))
    wall_color = (a > WALL_A[0]) & (a < WALL_A[1]) & (b > WALL_B[0]) & (b < WALL_B[1])
    seed = (wall_color & (np.abs(a) < 3) & (b < 10) & (L > floor)).astype(np.uint8)
    seed = cv2.erode(seed, np.ones((9, 9), np.uint8))
    level = cv2.GaussianBlur(L * seed, (0, 0), 30) / (cv2.GaussianBlur(seed.astype(np.float32), (0, 0), 30) + 1e-3)

    # Cerca de la persona el fondo cae en sombra: por eso el margen hacia abajo es amplio.
    # El pelo y la ropa negra quedan afuera por el piso, y la piel por el rojo (a*).
    bg = (wall_color & (L > level - 35) & (L < level + 30) & (L > floor)).astype(np.uint8)
    bg = cv2.morphologyEx(bg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    bg = cv2.morphologyEx(bg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(bg)
    keep = np.zeros_like(bg)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 0.01 * bg.size:
            keep[labels == i] = 1
    heads = np.zeros_like(bg)
    for cx, cy, rx, ry in faces:
        cv2.ellipse(heads, (round(cx / 4), round(cy / 4)), (round(HOLE_HEAD[0] * rx / 4), round(HOLE_HEAD[1] * ry / 4)), 0, 0, 360, 1, -1)
    # El nivel de arriba se apaga lejos de la pared (adentro de la gente da ~0): un hueco encerrado entre
    # dos piernas no tenia contra que compararse (el triangulo de la foto de grupo). Para los huecos, el promedio de
    # la pared de al lado y, donde no llega, uno ancho.
    sf = seed.astype(np.float32)
    w_near = cv2.GaussianBlur(sf, (0, 0), 30)
    near = cv2.GaussianBlur(L * sf, (0, 0), 30) / np.maximum(w_near, 1e-6)
    wide = cv2.GaussianBlur(L * sf, (0, 0), 120) / np.maximum(cv2.GaussianBlur(sf, (0, 0), 120), 1e-6)
    cover = np.clip(w_near / 0.05, 0, 1)
    hole_level = cover * near + (1 - cover) * wide
    keep |= holes(L, a, b, hole_level, floor, keep | heads) & (1 - heads)
    marked = np.zeros_like(keep)
    boxes = np.zeros_like(keep)
    for i, (x0, y0, x1, y1) in enumerate([*hand, *sure]):
        sl = np.s_[y0 // 4 : -(-y1 // 4), x0 // 4 : -(-x1 // 4)]
        wall_px = (np.abs(a[sl]) < 3) & (b[sl] > WALL_B[0]) & (b[sl] < WALL_B[1]) & (L[sl] > np.maximum(floor, hole_level[sl] - HOLE_SHADE))
        keep[sl] |= wall_px.astype(keep.dtype)
        if i >= len(hand):
            marked[sl] |= wall_px.astype(keep.dtype)
            boxes[sl] = 1
    # sin esto, la banda dudosa del matting se metia ~40 px en la remera negra y en el pelo de al lado de la
    # franja de la otra foto de grupo, con alpha 0,9-0,98, y el blanco los aclaraba hasta 7 L*: puntitos grises (2026-10-15)
    ring = cv2.dilate(marked, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * HAND_RING + 1,) * 2))
    solid = (boxes > 0) & (L < HAND_DARK) & (ring == 0)
    # Islas chicas de "persona" en medio del fondo (marcas del papel) son fondo.
    person = 1 - keep
    n, labels, stats, _ = cv2.connectedComponentsWithStats(person)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 0.002 * bg.size:
            keep[labels == i] = 1
    soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.5)
    soft = cv2.resize(soft, (w, h), interpolation=cv2.INTER_LINEAR)
    if not with_hand:
        return soft
    opinion = np.where(boxes > 0, 0.5, -1.0).astype(np.float32)
    opinion[solid] = 1.0
    opinion[marked > 0] = 0.0
    return soft, cv2.resize(opinion, (w, h), interpolation=cv2.INTER_NEAREST)


def holes(L: np.ndarray, a: np.ndarray, b: np.ndarray, level: np.ndarray, floor: float, skip: np.ndarray) -> np.ndarray:
    """Los huecos de pared encerrados por la gente (1 = hueco), fuera de `skip` (la pared grande y las cabezas).

    Pared en color, en brillo hasta HOLE_SHADE abajo de la pared (la ropa negra y la banqueta
    quedan abajo del piso de la mascara) y rodeada de algo mas oscuro (HOLE_RING): la ropa negra, la banqueta, el brazo en la sombra; si el contraste es
    poco, ademas lisa por dentro (HOLE_STD). El cuero de una zapatilla blanca en sombra tiene el gris de la pared, pero lo rodea
    cuero iluminado. Con el techo mas bajo (nivel + 8) se perdian los de un retrato: abajo el nivel lo
    baja el piso y la pared del hueco queda por encima. La textura se mide solo adentro: con la
    ventana cruzando el borde (ropa negra contra pared clara) todo hueco angosto daba textura.
    """
    cand = ((np.abs(a) < 3) & (b > WALL_B[0]) & (b < WALL_B[1]) & (L > level - HOLE_SHADE) & (L < level + 30)
            & (L > floor)).astype(np.uint8)
    cand = cv2.morphologyEx(cand, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cand[skip > 0] = 0
    m = cand.astype(np.float32)
    w = np.maximum(cv2.blur(m, (5, 5)), 1e-6)
    mean = cv2.blur(L * m, (5, 5)) / w
    std = np.sqrt(np.maximum(cv2.blur(L * L * m, (5, 5)) / w - mean * mean, 0))
    out = np.zeros_like(cand)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(cand)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < HOLE_MIN * L.size:
            continue
        x, y, w, h = stats[i, :4]
        sl = np.s_[max(0, y - 4) : y + h + 4, max(0, x - 4) : x + w + 4]
        comp = labels[sl] == i
        ring = (cv2.dilate(comp.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & ~comp
        contrast = float(np.median(L[sl][comp])) - float(np.median(L[sl][ring]))
        smooth = float(np.median(std[sl][comp])) <= HOLE_STD
        if contrast < HOLE_RING[1] and not (smooth and contrast >= HOLE_RING[0]):
            continue
        out[sl][comp] = 1
    return out


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
