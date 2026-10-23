"""Ojeras: se suavizan, no se borran. Version 3 (2026-10-14): ojo por ojo, con intensidad.

La version 2 (proceso-notas/31-ojeras/undereye-v2-suave.py.txt) gusto como primera version, pero media
la ojera contra una sola cifra (la mediana de una franja de mejilla) y su zona se apagaba justo
donde esta el arco de abajo: en una de las caras el arco y el violeta quedaban casi enteros. Despues
el fotografo pidio notar mas la diferencia, siempre natural, y poder mover la intensidad. Ahora, como en
un retoque a mano:

1. Pestanas y parpado: igual que en la v2, que fue lo que la hizo aceptable. La linea de pestanas
   de abajo esta medida a mano (`lids`); la franja de debajo (LID_GAP) no se toca y la correccion
   entra de a poco en la siguiente (LID_RAMP, larga: sin una linea donde empieza). Las pestanas
   (LASH) no se miden: no son piel. El ojo en si queda siempre afuera.
2. Zona: una medialuna debajo de cada ojo, con la hondura, el ancho y el corrimiento hacia el
   lagrimal de cada cara (`under_eye` en photos.py, y `eyes` para un ojo solo). El borde entra
   desde adentro: afuera de la zona no cambia ni un pixel.
3. Piel esperada: la que habria si la ojera fuera mejilla. Es una superficie suave (una membrana
   tensa) que pasa por la piel de alrededor: la mejilla de abajo y el rabillo, no el costado de la
   nariz, que es otro plano. Y la sostiene tambien la piel clara de la mitad de abajo de la zona
   (el pomulo), asi la ojera se compara con la piel que tiene justo debajo y no con la mejilla de
   mas abajo, que ya cae en sombra. Respeta como cae la luz: el ojo del lado de la sombra queda en
   sombra.
4. Color: lo violeta o marron se lleva hacia el color esperado (`color`).
5. Luz: se devuelve `light` de la luz que falta, con un tope suave (MAX_LIFT), medida con un
   filtro suave: poros, arrugas y la forma de la bolsa quedan. Es una ganancia, asi que la textura
   y el grano quedan los del RAW.

Intensidad: los valores de arriba son el 100 %, el maximo que sigue siendo natural. La final sale
a INTENSITY. Como todo es ganancia, la intensidad la escala exacta (apply), y grade.py arma con la
capa las puntas del control del editor: 0 y 100 %.

Tope del editor, 200 % (2026-10-15, el fotografo pidio una punta que las limpie aun mas, siempre natural):
otra capa (layers(top=True)), no la de arriba al doble. La primera version (el doble de luz y de
color sobre la misma zona) casi no se distinguia del 100 %: la zona entra recien a LID_GAP +
LID_RAMP de las pestanas, y la parte mas oscura de la ojera esta justo ahi. Ahora:

1. Falta: se mide con un filtro a la mitad (TOP_FINE) y con la piel desde mas cerca de las pestanas
   (TOP_LASH), asi sigue el arco de la bolsa.
2. Luz: la ojera llega a la piel esperada, menos una sombra de parpado (LID_SHADOW) que se apaga
   hacia abajo (LID_SHADOW_FADE). Una ojera suave no llega a esa sombra y no se toca; una honda se
   levanta casi hasta las pestanas (desde TOP_GAP). El tope suave (TOP_LIFT) es alto: lo que manda
   es lo que falta. `light` y `color` no cuentan aca: el ojo del lado de la sombra sigue en sombra
   porque la piel esperada ya la trae.
3. Color: el que falta, entero, entrando en TOP_COLOR_RAMP.
4. Arrugas: con la luz de vuelta, el surco de cada arruga queda a la vista. Se acerca a la piel de
   alrededor (CREASE), como en una separacion de frecuencias: el poro y el grano quedan.
5. `reach_lashes` (una de las caras): la ojera es una medialuna pegada a las pestanas, y con el borde de
   siempre quedaba entera. Debajo del ojo el borde no entra desde la linea de pestanas y la luz sube
   desde ahi con una pendiente maxima (REACH_SLOPE). Pasadas las esquinas vuelve el borde de siempre
   (REACH_CORNER): ahi la linea de pestanas sigue de largo y no es un borde de verdad. En un retrato sonriente el
   borde del parpado es una sombra ancha (sonrie, y la foto es mas blanda): abrirlo dibujaba una
   linea, y queda con el borde de siempre.
"""

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from common import blur, lab, luminance, norm_blur
from faces import ellipse_mask

# Los valores son los del 100 % de la intensidad, el maximo que sigue siendo natural. La final
# usa INTENSITY, y el editor deja moverla entre 0 y 200 % (grade.py arma las puntas).
INTENSITY = 0.7
DEFAULTS = {
    "light": 0.8,  # cuanto de la luz que le falta a la ojera se le devuelve
    "color": 0.8,  # cuanto de su color se lleva hacia el esperado
    "depth": 0.70,  # hondura de la medialuna debajo de las pestanas, en anchos de ojo
    "span": 0.62,  # medio ancho de la medialuna, en anchos de ojo
    "shift": 0.06,  # corrimiento de la medialuna hacia la nariz, en anchos de ojo
    "pin": 0.5,  # desde aca para abajo (en hondura de la zona) la piel clara tambien es referencia
    "reach_lashes": False,  # al 200 %, la luz llega hasta las pestanas: para una medialuna pegada a ellas
}
MAX_LIFT = 0.8  # tope, en pasos (suave: tanh)
LID_GAP = 0.06  # franja debajo de las pestanas que no se toca, en anchos de ojo
LID_RAMP = 0.2  # franja siguiente, donde la correccion entra de a poco: larga, sin linea
EDGE = 0.18  # el borde de la zona entra en esto, en anchos de ojo
LASH = 0.10  # pestanas y borde del parpado: no son piel, ahi no se mide
RING = 0.15  # anillo de piel alrededor de la zona que define la piel esperada
SCALE = 0.08  # filtro suave, en anchos de ojo: mas ancho que el anillo de la bolsa

# El 200 % del editor (anchos de ojo, salvo que diga otra cosa)
TOP_LIFT = 2.0  # tope suave del aclarado, en pasos: alto, lo que manda es la luz que falta
TOP_FINE = 0.5  # la falta se mide con SCALE por esto: sigue el arco de la bolsa
TOP_LASH = 0.07  # la piel se mide desde aca debajo de las pestanas (LASH: 0,10)
TOP_GAP = 0.03  # la luz entra desde aca debajo de las pestanas
LID_SHADOW = 0.35  # sombra de parpado que queda debajo de las pestanas, en pasos...
LID_SHADOW_FADE = 0.10  # ...y se apaga hacia abajo en esto
TOP_COLOR_RAMP = 0.08  # el color entra en esto, desde TOP_GAP
CREASE = 0.8  # cuanto se acerca el surco de una arruga a la piel de alrededor
CREASE_WIDTHS = (1.5, 2.5, 3.5)  # anchos de arruga que se buscan, en px
CREASE_AROUND = 0.05  # la piel de alrededor de una arruga
# con reach_lashes
REACH_GAP = 0.01  # la luz entra desde aca debajo de las pestanas...
REACH_SLOPE = 8.0  # ...con esta pendiente maxima, en pasos por ancho de ojo: sin escalon donde empieza
REACH_COLOR_GAP = 0.04  # el color entra desde aca (mas tarde que la luz: si no, una franja rosa)...
REACH_COLOR_RAMP = 0.12  # ...en esto
REACH_CORNER = 0.10  # pasadas las esquinas del ojo vuelve el borde de siempre, en esto


def skin_weight(crop: np.ndarray, face: dict, origin) -> np.ndarray:
    """Piel para las ojeras: como faces.skin_mask, pero aceptando piel en sombra y violeta. La
    mascara del resto del retoque pide brillo y un tono calido, y del lado en sombra de la cara
    (dos retratos) dejaba afuera justo la parte mas oscura de la ojera.

    Un cerco de 4 px la separa del pelo y de la pared, y cierra los huecos de un poro oscuro.
    """
    oval = ellipse_mask(crop.shape[:2], [face["oval"]], origin)
    k = 0.18 / max(float(np.median(luminance(crop)[oval > 0])), 1e-6)
    L, a, b = np.moveaxis(lab(np.clip(crop * k, 0, None)), -1, 0)
    hue = np.degrees(np.arctan2(b, a))
    chroma = np.hypot(a, b)
    # el tono va del violeta al amarillo: una ojera puede ser violeta, y eso es justo lo que se
    # corrige. La pared queda afuera por no tener color; el pelo, por oscuro.
    warm = np.clip((chroma - 2) / 2, 0, 1) * np.clip(1 - np.abs(hue - 40) / 75, 0, 1)
    m = warm * np.clip((L - 6) / 6, 0, 1) * oval
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    solid = cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, disc)
    return blur(cv2.erode(solid, disc).astype(np.float32), 2.0)


def lid_curve(points, origin) -> np.ndarray:
    """Parabola y(x) por los tres puntos de la linea de pestanas, en coordenadas de la ventana."""
    oy, ox = origin
    xs = np.array([p[0] - ox for p in points], float)
    ys = np.array([p[1] - oy for p in points], float)
    return np.polyfit(xs, ys, 2)


def smooth(t):
    """De 0 a 1 en S entre t = 0 y t = 1: sin un escalon donde empieza ni donde termina."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def lineness(log_y: np.ndarray) -> np.ndarray:
    """0..1: cuanto es cada pixel el fondo de una linea oscura (una arruga) de alguno de los anchos de
    CREASE_WIDTHS. Sale de la curvatura de la luz: fuerte de traves y casi nula a lo largo, asi una
    mancha redonda no cuenta. Una arruga marcada (curvatura 0,02) cuenta entera."""
    best = np.zeros_like(log_y)
    for s in CREASE_WIDTHS:
        hxx = gaussian_filter(log_y, s, order=(0, 2)) * s * s
        hyy = gaussian_filter(log_y, s, order=(2, 0)) * s * s
        hxy = gaussian_filter(log_y, s, order=(1, 1)) * s * s
        tr, det = hxx + hyy, hxx * hyy - hxy * hxy
        disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
        across, along = tr / 2 + disc, tr / 2 - disc
        line = np.clip(across, 0, None) * np.exp(-((np.abs(along) / np.maximum(across, 1e-6)) ** 2) / (2 * 0.5**2))
        best = np.maximum(best, line)
    return np.clip(best / 0.02, 0, 1)


def membrane(values: np.ndarray, known: np.ndarray, unknown: np.ndarray) -> np.ndarray:
    """La superficie mas lisa (armonica) adentro de `unknown` que en su borde vale lo que `values`
    en `known`. Donde el vecino no es ni una cosa ni la otra (el ojo, el parpado, el pelo) el borde
    queda libre. Devuelve una copia de `values` con `unknown` rellenado."""
    h, w = values.shape
    ys, xs = np.nonzero(unknown)
    index = np.full((h, w), -1, np.int64)
    index[ys, xs] = np.arange(len(ys))
    diag = np.zeros(len(ys))
    rhs = np.zeros(len(ys))
    rows, cols = [], []
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = ys + dy, xs + dx
        inside = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        ny, nx, me = ny[inside], nx[inside], np.nonzero(inside)[0]
        other = index[ny, nx]
        free = other >= 0
        rows.append(me[free])
        cols.append(other[free])
        diag[me[free]] += 1
        fixed = ~free & known[ny, nx]
        diag[me[fixed]] += 1
        np.add.at(rhs, me[fixed], values[ny[fixed], nx[fixed]])
    lonely = diag == 0  # sin vecinos: queda como estaba
    diag[lonely] = 1
    rhs[lonely] = values[ys[lonely], xs[lonely]]
    r, c = np.concatenate(rows), np.concatenate(cols)
    a = csr_matrix((np.concatenate([diag, -np.ones(len(r))]), (np.concatenate([np.arange(len(ys)), r]), np.concatenate([np.arange(len(ys)), c]))), shape=(len(ys), len(ys)))
    out = values.copy()
    out[ys, xs] = spsolve(a, rhs)
    return out


def envelope(low: np.ndarray, known: np.ndarray, region: np.ndarray, pinnable: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La piel esperada: la membrana desde el anillo, pero la piel de adentro que queda por encima
    (el pomulo, en la parte de abajo de la zona) tambien la sostiene. Asi la ojera se compara con la
    piel que tiene justo debajo y no con la mejilla de mas abajo, que ya cae en sombra."""
    pins = np.zeros_like(region)
    expected = membrane(low, known, region)
    for _ in range(4):
        new = pinnable & ~pins & (low > expected + 0.01)
        if not new.any():
            break
        pins |= new
        expected = membrane(low, known | pins, region & ~pins)
    return expected, pins


def params(face: dict, i: int) -> dict:
    """Los de la cara (`under_eye` en photos.py), con lo de cada ojo (`eyes`) encima."""
    p = DEFAULTS | {k: v for k, v in face.get("under_eye", {}).items() if k != "eyes"}
    eyes = face.get("under_eye", {}).get("eyes", [{}, {}])
    return p | eyes[i]


def geometry(shape, face: dict, i: int, origin, p: dict) -> dict:
    """Zona (0..1, con el parpado y el borde ya suaves), region dura y anillo de un ojo."""
    oy, ox = origin
    points, other = face["lids"][i], face["lids"][1 - i]
    lid = lid_curve(points, origin)
    left, right = min(q[0] for q in points) - ox, max(q[0] for q in points) - ox
    width = right - left
    mid = (left + right) / 2
    inner = 1 if np.mean([q[0] for q in other]) - ox > mid else -1
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]].astype(np.float32)
    # px debajo de la linea de pestanas; pasadas las esquinas, la linea sigue derecha
    below = yy - np.polyval(lid, np.clip(xx, left, right)).astype(np.float32)
    cx = mid + inner * p["shift"] * width
    cy = float(np.polyval(lid, cx))
    a, b = p["span"] * width, p["depth"] * width
    ellipse = ((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2 <= 1
    region = ellipse & (below > 0)
    ra, rb = a + RING * width, b + RING * width
    outer = ((xx - cx) / ra) ** 2 + ((yy - cy) / rb) ** 2 <= 1
    ring = outer & ~region & (below > -0.1 * width)
    # el costado de la nariz es otro plano (claro del lado de la luz, oscuro del de la sombra): no
    # dice como seria la piel de la ojera. Manda la mejilla de abajo y el rabillo.
    corner = right if inner > 0 else left
    nose = (inner * (xx - corner) > 0) & (below < 0.5 * b)
    ring &= ~nose
    # el borde entra desde adentro de la region: afuera no cambia nada
    dist = cv2.distanceTransform(region.astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(dist / (EDGE * width), 0, 1)
    edge = t * t * (3 - 2 * t)
    top = np.clip((below - LID_GAP * width) / (LID_RAMP * width), 0, 1)
    zone = edge * top * top * (3 - 2 * top)  # entra en S: sin un escalon donde empieza
    lash = outer & (below > -0.1 * width) & (below < LASH * width)
    return {"zone": zone.astype(np.float32), "region": region, "ring": ring, "lash": lash, "below": below, "width": width,
            "edge": edge, "ellipse": ellipse, "left": left, "right": right}


def top_light(log_y: np.ndarray, expected: np.ndarray, g: dict, p: dict, skin: np.ndarray, eyes: np.ndarray, hole: np.ndarray, s: float):
    """El 200 % de un ojo: el aclarado (sin las arrugas) y las zonas donde entran la luz y el color."""
    w = g["width"]
    b = g["below"] / w
    # la falta con un filtro mas fino, y la piel medida desde mas cerca de las pestanas
    skin_top = ((skin > 0.5) & (hole < 0.05) & ~(g["lash"] & (g["below"] < TOP_LASH * w))).astype(np.float32)
    deficit = np.where(g["region"], np.clip(expected - norm_blur(log_y, skin_top, max(TOP_FINE * s, 2.0)), 0, None), 0)
    edge, hole_top, gap, color_gap, color_ramp = g["edge"], hole, TOP_GAP, TOP_GAP, TOP_COLOR_RAMP
    if p["reach_lashes"]:
        # debajo del ojo el borde entra desde el resto de la elipse, no desde la linea de pestanas, y
        # el ojo se corta en esa linea (la elipse de features baja de ella). Pasadas las esquinas, el
        # borde de siempre.
        xs = np.arange(log_y.shape[1], dtype=np.float32)[None, :]
        under = 1 - smooth(np.maximum(g["left"] - xs, xs - g["right"]) / (REACH_CORNER * w))
        dist = cv2.distanceTransform(g["ellipse"].astype(np.uint8), cv2.DIST_L2, 5)
        edge = smooth(dist / (EDGE * w)) * under + g["edge"] * (1 - under)
        lid_cut = blur(((eyes > 0.5) & (g["below"] <= 0)).astype(np.float32), max(0.04 * w, 2.0))
        hole_top = lid_cut * under + hole * (1 - under)
        gap, color_gap, color_ramp = REACH_GAP, REACH_COLOR_GAP, REACH_COLOR_RAMP
    full = edge * skin * (1 - hole_top) * g["region"]
    light_zone = full * smooth(b / gap)
    color_zone = full * smooth((b - color_gap) / color_ramp)
    shadow = LID_SHADOW * (1 - smooth((b - gap) / LID_SHADOW_FADE))
    lift = TOP_LIFT * np.tanh(np.clip(deficit - shadow, 0, None) / TOP_LIFT) * light_zone
    if p["reach_lashes"]:
        lift = np.minimum(lift, REACH_SLOPE * np.clip(b, 0, None))
    return lift, light_zone, color_zone


def creases(log_y: np.ndarray, lift: np.ndarray, lines: np.ndarray, is_skin: np.ndarray, g: dict, light_zone: np.ndarray) -> np.ndarray:
    """Al 200 %, con la luz de vuelta, el surco de cada arruga se acerca a la piel de alrededor. Como
    en una separacion de frecuencias: el sombreado de la arruga (oscuro, con sus hombros claros) se
    suaviza, y el poro y el grano quedan. Solo donde hay una linea (`lines`), y recien pasadas las
    pestanas, que tambien son lineas."""
    w = g["width"]
    lit = log_y + lift
    around = norm_blur(lit, is_skin, max(CREASE_AROUND * w, 4.0))
    past_lashes = smooth((g["below"] - LASH * w) / (0.05 * w))
    return CREASE * (around - blur(lit, 1.0)) * lines * light_zone * past_lashes


def eye_maps(crop: np.ndarray, face: dict, origin, skin=None, eyes=None) -> list[dict]:
    """Todo lo de cada ojo: zona, piel esperada, falta de luz, aclarado y corrimiento de color, al
    100 % y al 200 % del editor."""
    skin = skin_weight(crop, face, origin) if skin is None else skin
    eyes = ellipse_mask(crop.shape[:2], face["features"][:2], origin) if eyes is None else eyes
    y = luminance(crop)
    log_y = np.log2(np.maximum(y, 1e-6))
    chans = [np.log(np.maximum(crop[..., k], 1e-6) / np.maximum(crop[..., 1], 1e-6)) for k in (0, 2)]
    lines = blur(lineness(log_y), 1.5)  # las arrugas, para el 200 %
    out = []
    for i in range(2):
        p = params(face, i)
        g = geometry(y.shape, face, i, origin, p)
        # el ojo queda afuera con un borde a escala del ojo, no de 2 px: si no, cerca del rabillo el
        # aclarado cambiaria de golpe
        hole = blur(eyes.astype(np.float32), max(0.04 * g["width"], 2.0))
        zone = g["zone"] * skin * (1 - hole)
        s = max(SCALE * g["width"], 4.0)
        is_skin = ((skin > 0.5) & (hole < 0.05) & ~g["lash"]).astype(np.float32)
        known = g["ring"] & (is_skin > 0)
        low = norm_blur(log_y, is_skin, s)
        pinnable = g["region"] & (g["below"] > p["pin"] * p["depth"] * g["width"]) & (is_skin > 0)
        expected, pins = envelope(low, known, g["region"], pinnable)
        deficit = np.where(g["region"], np.clip(expected - low, 0, None), 0).astype(np.float32)
        # tope suave: cerca del tope sube cada vez menos, sin una meseta plana
        lift = MAX_LIFT * np.tanh(p["light"] * deficit / MAX_LIFT) * zone
        light_top, light_zone, color_zone = top_light(log_y, expected, g, p, skin, eyes, hole, s)
        lift_top = light_top + creases(log_y, light_top, lines, is_skin, g, light_zone)
        tints, tints_top = [], []
        for chan in chans:
            low_c = norm_blur(chan, is_skin, s)
            missing = membrane(low_c, known | pins, g["region"] & ~pins) - low_c  # el color que falta, entero
            tints.append((p["color"] * missing * zone).astype(np.float32))
            tints_top.append((missing * color_zone).astype(np.float32))
        out.append(g | {"params": p, "zone": zone, "deficit": deficit, "lift": lift.astype(np.float32), "tint": tints,
                        "lift_top": lift_top.astype(np.float32), "tint_top": tints_top, "pins": pins, "low": low, "expected": expected})
    return out


def layers(maps: list[dict], top: bool = False) -> np.ndarray:
    """Aclarado (pasos) y corrimiento de color (log R, log B) de los dos ojos, en una sola capa: la del
    100 %, o con top la del 200 % del editor."""
    lift, tint = ("lift_top", "tint_top") if top else ("lift", "tint")
    return np.stack([sum(m[lift] for m in maps), sum(m[tint][0] for m in maps), sum(m[tint][1] for m in maps)], -1)


def apply(crop: np.ndarray, layer: np.ndarray, t: float = 1.0) -> np.ndarray:
    """La correccion a la intensidad t (0..1): todo es ganancia, asi que t la escala exacta."""
    y = luminance(crop)
    out = crop.copy()
    out[..., 0] *= np.exp(t * layer[..., 1])
    out[..., 2] *= np.exp(t * layer[..., 2])
    target = y * np.exp2(t * layer[..., 0])
    return out * (target / np.maximum(luminance(out), 1e-7))[..., None]


def correct(crop: np.ndarray, face: dict, origin) -> tuple[np.ndarray, list, np.ndarray, np.ndarray]:
    """Suaviza las dos ojeras de una cara a la intensidad de la final. Devuelve el recorte, la info
    por ojo (para el editor) y las capas del 100 % y del 200 %, con las que grade.py arma las puntas
    del control."""
    maps = eye_maps(crop, face, origin)
    layer = layers(maps)
    info = []
    for m in maps:
        core = m["zone"] > 0.5
        before = float(np.percentile(m["deficit"][core], 90)) if core.any() else 0.0
        info.append({"deficit": round(before, 2), "lifted": round(INTENSITY * float(m["lift"].max()), 2)})
    return apply(crop, layer, INTENSITY), info, layer, layers(maps, top=True)
