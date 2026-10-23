"""Separar a la persona del fondo con calidad de pelo: alpha matting + color del primer plano.

Metodo clasico, sin IA generativa:
- Trimapa desde la mascara de fondo: adentro seguro, afuera seguro, y una banda
  dudosa alrededor del borde (pelo, orejas, anteojos).
- Alpha por closed-form matting (Levin, Lischinski y Weiss, 2008): resuelve la
  transparencia de cada pixel de la banda, pelo por pelo.
- Color del primer plano por estimacion multinivel (Germer et al., 2020): saca el gris
  del fondo que contamina los pixeles del borde. Eso es lo que evita el halo al poner
  un fondo negro: el borde ya no trae gris pegado.

Se calcula a 1024 px y se guarda en work/. Para la salida a 2048 se sube el alpha con
filtro guiado y el color del borde se corrige sobre la imagen en alta.
"""

from pathlib import Path

import cv2
import numpy as np
from pymatting import estimate_alpha_cf, estimate_foreground_ml
from scipy.special import ndtr, ndtri

from common import ROOT, linear_to_srgb, srgb_to_linear
from masks import guided_filter, guided_filter_color, luminance

SIZE = 1024
BAND = 0.03  # banda dudosa: 3 % del lado
SOLID = (0.02, 0.96)  # alpha por debajo es pared pura, por encima persona opaca


def norm_scale(img: np.ndarray) -> float:
    """Escala para pasar la imagen a 0..1 sin recortar nada.

    Antes se usaba el percentil 99.5 y lo que pasaba de 1 se recortaba: el reflejo de la
    frente se volvia blanco puro y el color del primer plano lo devolvia gris neutro plano.
    """
    return max(float(np.percentile(img.max(axis=2), 99.99)), 1e-6) / 0.98


def trimap(coarse_bg: np.ndarray, band_px: int, face=None, srgb: np.ndarray | None = None) -> np.ndarray:
    """1 = persona segura, 0 = fondo seguro, 0.5 = a resolver.

    `face` es la elipse de la cara (cx, cy, rx, ry). Cerca de la cara, todo lo que sea
    mas claro que la pared de al lado es persona: el
    reflejo de la frente es neutro como la pared, pero la pared nunca es mas clara que
    si misma. Sin esto el recorte le ponia gris encima al reflejo.
    """
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (band_px, band_px))
    fg = cv2.erode((coarse_bg < 0.05).astype(np.uint8), k)
    bg = cv2.erode((coarse_bg > 0.95).astype(np.uint8), k)
    if face:
        cx, cy, rx, ry = (int(round(v)) for v in face)
        # (Forzar toda la elipse como persona no sirve: con la cabeza de perfil la elipse
        # pisa la pared y quedaba pared vieja pegada a la cara.)
        if srgb is not None:
            L = srgb.mean(axis=2)
            near = np.zeros_like(fg)
            cv2.ellipse(near, (cx, cy), (int(rx * 1.25), int(ry * 1.2)), 0, 0, 360, 1, -1)
            ring = np.zeros_like(fg)
            cv2.ellipse(ring, (cx, cy), (int(rx * 1.9), int(ry * 1.7)), 0, 0, 360, 1, -1)
            wall = (ring > 0) & (near == 0) & (coarse_bg > 0.95)
            if wall.any():
                # Solo pixeles casi neutros (el reflejo, |a*| < 3) y sin dilatar: con la dilatacion
                # de 5x5 a 1024 px y la piel iluminada adentro, el borde de la mandibula quedaba
                # clavado 10-12 px afuera, sobre la pared (auditoria v7). La piel con color la
                # resuelve settle_skin_edges.
                a_star = cv2.cvtColor(np.clip(srgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)[..., 1]
                brighter = (near > 0) & (L > float(np.percentile(L[wall], 95)) + 0.03) & (np.abs(a_star) < 3)
                fg |= brighter.astype(fg.dtype)
                bg[brighter] = 0
    tri = np.full(coarse_bg.shape, 0.5, np.float64)
    tri[fg > 0] = 1.0
    tri[bg > 0] = 0.0
    if srgb is not None:
        tri = settle_skin_edges(tri, srgb)
    return tri


def settle_skin_edges(tri: np.ndarray, srgb: np.ndarray) -> np.ndarray:
    """En la banda dudosa, decide por color donde no hay pelo.

    Piel clara contra pared clara se parecen en brillo y el matting dejaba el borde de la
    mejilla granulado, con pared colada. Pero se distinguen por color: la piel es rojiza
    (a* alto) y la pared es gris neutra. Solo el pelo queda para el matting fino.
    """
    lab = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2LAB)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    unknown = (tri > 0.1) & (tri < 0.9)
    wall = tri < 0.1
    if not wall.any():
        return tri
    wall_L = float(np.median(L[wall]))
    hair = (L < wall_L - 25).astype(np.uint8)
    near_hair = cv2.dilate(hair, np.ones((9, 9), np.uint8)) > 0
    skin = (a > 6) & ~near_hair
    neutral = (np.abs(a) < 2.0) & (np.abs(b) < 4.0) & (L > wall_L - 12) & ~near_hair
    out = tri.copy()
    out[unknown & skin] = 1.0
    out[unknown & neutral] = 0.0
    return out


def compute(img_lin: np.ndarray, coarse_bg: np.ndarray, face=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Alpha (1 = persona), color del primer plano (sRGB) y trimapa, a SIZE px."""
    small = cv2.resize(img_lin, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    srgb = np.clip(linear_to_srgb(small / norm_scale(small)), 0, 1).astype(np.float64)
    s = SIZE / img_lin.shape[0]
    face_small = tuple(v * s for v in face) if face else None
    tri = trimap(cv2.resize(coarse_bg, (SIZE, SIZE), interpolation=cv2.INTER_AREA), int(SIZE * BAND) | 1, face_small, srgb)
    alpha = estimate_alpha_cf(srgb, tri)
    fg = estimate_foreground_ml(srgb, alpha)
    return alpha.astype(np.float32), fg.astype(np.float32), tri.astype(np.float32)


def cached(key: str, img_lin: np.ndarray, coarse_bg: np.ndarray, face=None) -> tuple[np.ndarray, np.ndarray, float]:
    """Alpha y primer plano guardados en work/ (se calculan una vez por foto y encuadre).

    Devuelve tambien la escala con la que se normalizo la imagen para el matting, para
    poder volver el color del primer plano a la luz lineal original.
    """
    path = ROOT / "work" / f"{key}-matte.npz"
    small = cv2.resize(img_lin, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    scale = norm_scale(small)
    if path.exists():
        data = np.load(path)
        return data["alpha"].astype(np.float32), data["fg"].astype(np.float32), scale
    alpha, fg, tri = compute(img_lin, coarse_bg, face)
    alpha, fg, tri = (x.astype(np.float16) for x in (alpha, fg, tri))
    np.savez_compressed(path, alpha=alpha, fg=fg, tri=tri)
    # lo mismo que se va a leer en las corridas siguientes: devolverlo en float32 sin redondear
    # hacia que la primera corrida despues de borrar el matte no coincidiera con las demas
    return alpha.astype(np.float32), fg.astype(np.float32), scale


def upsample_alpha(img_lin: np.ndarray, alpha: np.ndarray, face=None) -> np.ndarray:
    """Solo el alpha al tamano de `img_lin`: filtro guiado y borde de piel por color.

    Es lo unico que hace falta cuando el fondo se edita en vez de reemplazarse: el alpha
    dice cuanto aclarar cada pixel, el color de la persona es el de la foto.
    """
    n = img_lin.shape[0]
    a_up = cv2.resize(alpha, (n, n), interpolation=cv2.INTER_CUBIC)
    lum = luminance(img_lin)
    guide = np.sqrt(np.clip(lum / max(float(np.percentile(lum, 99)), 1e-6), 0, 1)).astype(np.float32)
    a_up = np.clip(guided_filter(guide, a_up, max(2, n // 512), 1e-4), 0, 1).astype(np.float32)
    return key_thin_hair(img_lin, refine_edges(img_lin, a_up, face))


def upsample(img_lin: np.ndarray, alpha: np.ndarray, scale: float) -> tuple[np.ndarray, np.ndarray]:
    """Alpha y primer plano (lineal) al tamano de `img_lin`.

    El alpha se sube con filtro guiado. El color del primer plano se vuelve a estimar a
    la resolucion final: subir una correccion calculada a 1024 dejaba el borde escalonado.
    """
    n = img_lin.shape[0]
    a_up = cv2.resize(alpha, (n, n), interpolation=cv2.INTER_CUBIC)
    lum = luminance(img_lin)
    guide = np.sqrt(np.clip(lum / max(float(np.percentile(lum, 99)), 1e-6), 0, 1)).astype(np.float32)
    a_up = np.clip(guided_filter(guide, a_up, max(2, n // 512), 1e-4), 0, 1).astype(np.float32)
    a_up = refine_edges(img_lin, a_up)
    fg = foreground_tiled(img_lin, a_up, scale)
    return a_up, fg


def refine_edges(img: np.ndarray, alpha: np.ndarray, face=None, guide_scale: float | None = None) -> np.ndarray:
    """El alpha del contorno a la resolucion final, por la recta de color entre persona y pared.

    El alpha viene de 1024 px y del filtro guiado. Cada pixel cerca del contorno (alpha 0.5)
    se proyecta sobre la recta que une la persona de al lado (F) con la pared de al lado (B):
    alpha = (I - B)·(F - B) / |F - B|² (Chuang 2001). F y B salen de 6 a 20 px a cada lado,
    sin tocar la rampa.

    - Piel: contra la pared clara casi no se distingue en brillo, y los brillos de la nariz y
      la sombra de la comisura caen del lado de la pared. Ahi se proyecta solo en +-5 px (lo
      que mide la rampa del sensor) y afuera de la banda el alpha es 1 o 0, como una seleccion
      hecha a mano; afuera, un pelo o una pestana (fuera de la recta) toma su alpha del brillo.
      Proyectar todo lo que tenia alpha entre 0.01 y 0.99 dejaba mordidas blancas en el
      perfil (un retrato de perfil, QA v7).
    - Buzo y pelo (F oscuro): la separacion es enorme y la proyeccion es fiel pixel a pixel,
      asi que se usa hasta 50 px a cada lado. El buzo negro vuelve a ser opaco (el matting lo
      dejaba en 0.90-0.97 y el aclarado de la pared le ponia un velo: 14 -> 24 L*), y cada
      pelo suelto queda con su transparencia real. Donde el pixel no esta sobre la recta (piel
      del cuello pegada al pelo) adentro es persona y afuera queda el matting.
    """
    n = alpha.shape[0]
    # semiancho de la banda en piel: el borde del sensor mide 5,2 px de 10 a 90 % en un retrato de perfil
    # (sigma ~2 px), asi que la rampa entera llega a +-5 px. Con +-3 se cortaban las colas y
    # el contorno quedaba 1 px mas nitido que el original (gate v7).
    m = max(2, round(5 * n / 4170))
    far = 4 * m  # F y B se miden hasta aca
    reach = 10 * m  # hasta aca se proyecta en los bordes oscuros
    solid = (alpha > 0.5).astype(np.uint8)
    d_full = cv2.distanceTransform(solid, cv2.DIST_L2, 5)
    d_out = cv2.distanceTransform(1 - solid, cv2.DIST_L2, 5)
    d_in = d_full
    near = (d_in <= reach) & (d_out <= reach)
    if not near.any():
        return alpha
    pad = 2 * far
    ys, xs = np.where(near)
    y0, y1 = max(0, ys.min() - pad), min(n, ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(n, xs.max() + pad + 1)
    del ys, xs, near
    I = img[y0:y1, x0:x1].astype(np.float32)
    a = alpha[y0:y1, x0:x1]
    di, do = d_in[y0:y1, x0:x1], d_out[y0:y1, x0:x1]
    del d_out
    r = 2 * far
    sigma = 0.75 * far

    def local_mean(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Media gaussiana normalizada. Con un filtro de caja F y B saltaban en lineas rectas
        cuando un grupo de pixeles entraba o salia de la ventana: escalones en la sien y una
        raya vertical en el pelo (gate v7)."""
        mask = mask.astype(np.float32)
        w = cv2.GaussianBlur(mask, (0, 0), sigma)
        s = cv2.GaussianBlur(I * mask[..., None], (0, 0), sigma)
        return s / np.maximum(w, 1e-6)[..., None], w

    F, wf = local_mean((di > m) & (di <= far))
    B, wb = local_mean((do > m) & (do <= far))
    # cuanto alpha le dejo el matting a esa pared (para skin_hair_alpha)
    ring = ((do > m) & (do <= far)).astype(np.float32)
    a_wall = cv2.GaussianBlur(a * ring, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(ring, (0, 0), sigma), 1e-6)
    del ring
    d = F - B
    dd = np.maximum((d * d).sum(axis=2), 1e-12)
    I -= B
    a_raw = (I * d).sum(axis=2) / dd
    I -= a_raw[..., None] * d
    off = np.sqrt((I * I).sum(axis=2) / dd)  # distancia a la recta, en unidades de |F - B|
    del I
    a_c = np.clip(a_raw, 0, 1)  # mas alla de F (un brillo de la piel sobre la recta) es persona
    del a_raw
    on_line = np.clip((0.3 - off) / 0.15, 0, 1)
    lum = lambda x: x @ np.array([0.2126, 0.7152, 0.0722], np.float32)  # noqa: E731
    # confianza: hay persona y pared de los dos lados, y F se separa de B bastante mas que el ruido
    sep = np.clip((np.sqrt(dd) / np.maximum(lum(B), 1e-6) - 0.06) / 0.08, 0, 1)
    both = np.clip(wf / 0.03, 0, 1) * np.clip(wb / 0.03, 0, 1)
    w = cv2.GaussianBlur(sep * both, (0, 0), r / 2)
    # piel: F calida y clara (el pelo y el buzo son oscuros)
    warm = np.clip((F[..., 0] / np.maximum(F[..., 2], 1e-6) - 1.08) / 0.12, 0, 1)
    bright = np.clip((lum(F) / np.maximum(lum(B), 1e-6) - 0.35) / 0.2, 0, 1)
    skin = cv2.GaussianBlur(warm * bright, (0, 0), r / 2)
    # un pelo o una pestana sobre la pared, junto a la piel, no esta sobre la recta piel-pared:
    # su alpha sale del brillo, como una mascara de luminancia (el pelo es ~10 veces mas oscuro
    # que la pared). Con 0 a secas se borraban las pestanas y los pelos de la sien (gate v7).
    y_b = np.maximum(lum(B), 1e-6)
    a_dark = np.clip((y_b - lum(img[y0:y1, x0:x1].astype(np.float32))) / (0.9 * y_b), 0, 1)
    # cuanto mas oscura que la pared es la piel de al lado (0 si es mas clara): lo que la mezcla
    # piel-pared ya oscurece un pixel del borde, sin pelo
    skin_dark = np.clip(1 - lum(F) / y_b, 0, 1) / 0.9
    # cuanto se separa la piel de la pared, en unidades de la pared: la mandibula del retrato con anteojos en sombra
    # da 0.29-0.41; la piel clara de perfil y la cara bajo el lente del retrato con anteojos, 0.5-1.7
    rel = np.sqrt(dd) / y_b
    # el filo de piel con un mechon encima (sin pared): ver skin_hair_alpha. Solo donde la pared de
    # al lado es pared: junto al aro de los anteojos el matting le deja 0.17-0.3 y B no lo es
    a_rim = skin_hair_alpha(img[y0:y1, x0:x1], F, B, a_c, skin, max(1, round(RIM_HAIR_PX * n / 4170)), RIM_H_SIGMA * m)
    a_rim *= both * np.clip((RIM_WALL[0] - a_wall) / RIM_WALL[1], 0, 1)
    del a_wall
    # un pliegue de la persona de otro color, tan oscuro como la pared (la punta roja de la mejilla
    # vista a traves de un lente): ver second_colour
    s_fix = second_colour(img[y0:y1, x0:x1], F, B, off, di, do, skin, a_dark, m)
    del F, B, d, dd, wf, wb, sep, both, warm, bright, y_b
    # sobre la recta: la proyeccion. Fuera de ella, la silueta con el borde de color de la foto
    # (filtro guiado en color, radio 3 px), como el "perfeccionar borde" de una seleccion a
    # mano: adentro es persona (piel del cuello junto al pelo) y afuera un pelo o una pestana,
    # con su alpha por brillo. Con 1 a secas adentro, donde la piel se aparta de la recta (el
    # labio y la nariz de otro perfil contra una pared casi igual de clara) el alpha saltaba de 0.09 a
    # 0.98 en un pixel y el perfil quedaba escalonado; un calado gaussiano parejo, en cambio,
    # ensanchaba los bordes nitidos (gate v7, A/B en otro perfil).
    # en el lugar: con cada paso en una copia nueva, la guia (3 canales a 4170 px) llevaba el pico a 4 GB
    guide = img[y0:y1, x0:x1].astype(np.float32)
    if guide_scale is None:
        guide_scale = float(np.percentile(img[::4, ::4], 99.5))
    np.divide(guide, max(guide_scale, 1e-6), out=guide)
    np.sqrt(np.clip(guide, 0, 1, out=guide), out=guide)
    calado = np.clip(guided_filter_color(guide, solid[y0:y1, x0:x1].astype(np.float32), max(1, round(3 * n / 4170)), 1e-4), 0, 1)
    del guide
    target = on_line * a_c + (1 - on_line) * np.where(di > 0, calado, np.maximum(a_dark, calado))
    del calado
    if s_fix is not None:
        sy, sx, s_alpha, s_w = s_fix
        target[sy, sx] += s_w * (s_alpha - target[sy, sx])
    del s_fix
    if skin.max() > 0:
        # Piel: el contorno como una seleccion a mano, con el desenfoque del sensor. Con piel en
        # sombra contra la pared (la mandibula del retrato con anteojos: |F - B| ~0.07 y la textura de la piel ~0.02
        # por canal) la proyeccion pixel a pixel lee la textura como transparencia: el perfil sube y
        # baja (dientes de hasta 3 px, mordidas blancas adentro y puntitos en la pared hasta 28 px
        # afuera). Ahi el borde sale de la geometria y no del pixel: el contorno 0.5 de este mismo
        # resultado, suavizado a lo largo del borde, y una rampa del ancho del sensor alrededor.
        # Monotona por construccion; el contorno queda donde estaba (d50 +-0.05 px en el retrato con anteojos) y el
        # ancho es el que la foto tiene en ese tramo del borde.
        a_sk = skin_ramp(a + w * (target - a), m, a_c, on_line)
        # afuera, un pelo o una pestana (fuera de la recta y oscuro) conserva su alpha por brillo
        a_sk += (di == 0) * (1 - on_line) * np.maximum(a_dark - a_sk, 0)
        # Lo que la proyeccion pone por encima de la rampa de forma pareja es un objeto y no textura:
        # el aro de los anteojos cruzando el borde de la cara (un lente, hasta 0.57 de promedio
        # en m). La textura de la piel en sombra leida como alpha promedia como mucho 0.057 en la
        # mandibula del retrato con anteojos: por encima de 0.06 se conserva, entero desde 0.12.
        extra = np.maximum(target - a_sk, 0)
        coh = cv2.GaussianBlur(extra, (0, 0), SKIN_SMOOTH * m)
        coh -= 0.06
        coh *= 1 / 0.06
        np.clip(coh, 0, 1, out=coh)
        extra *= coh
        a_sk += extra
        del extra, coh
        # Un pixel bastante mas oscuro de lo que lo haria la mezcla piel-pared (un pelo suelto, la
        # ceja, una pestana; 0.04 es el ruido del sensor) conserva el alpha de antes: `skin` viene
        # desenfocado 20 px y alcanza al pelo de al lado de la frente.
        skin_dark *= a_sk
        np.subtract(a_dark, skin_dark, out=skin_dark)
        wsk = np.clip((skin_dark - 0.04) / 0.08, 0, 1)  # cuanto es pelo
        del skin_dark
        wsk -= 1
        wsk *= -skin  # el peso de la rampa: piel y no pelo
        # y solo donde la proyeccion no es confiable: con la piel bien separada de la pared lee el
        # borde pixel a pixel sin dientes, y la rampa (sigma de al menos 1.25 px) lo ensanchaba
        # (perfil, estilo ref-a: +0.9 px de 10 a 90 %) y borraba los mechones finos de al lado (piloto r2)
        rel -= SKIN_REL[0]
        rel *= -1 / SKIN_REL[1]
        rel += 1
        np.clip(rel, 0, 1, out=rel)
        # Donde la proyeccion es confiable la rampa solo rellena mordidas (la cuna clara del lente
        # del retrato con anteojos): sube el alpha, nunca lo baja, y solo donde a lo ancho del borde falta alpha en
        # neto. Una rampa mas ancha que el borde real falta afuera y sobra adentro en partes
        # iguales (neto ~0, perfil: p50 -0.003); una mordida falta de los dos lados (0.04-0.08).
        a_sk -= target
        fill = cv2.GaussianBlur(a_sk * np.clip(wsk, 0, 1), (0, 0), SKIN_FILL[0] * m)
        fill -= SKIN_FILL[1]
        fill *= 1 / SKIN_FILL[2]
        np.clip(fill, 0, 1, out=fill)
        fill *= a_sk > 0
        fill *= 1 - rel
        rel += fill
        del fill
        a_sk *= wsk
        a_sk *= rel
        target += a_sk
        del a_sk, wsk, rel
    else:
        del skin_dark, rel
    # piso dentro de la silueta: un pixel mucho mas oscuro que la pared no es pared. El iris y
    # las pestanas del perfil quedaban con el 0.7-0.9 del matting (la confianza no llega a 1) y
    # la pared aclarada les sumaba 10-20 L* (gate v7)
    floor = a_dark * (di > 0)
    # el filo de piel con un mechon encima: afuera solo en la rampa del sensor (m), adentro hasta far
    np.maximum(floor, a_rim * (di <= far) * np.clip((m + 2 - do) / 2, 0, 1), out=floor)
    del a_rim
    # en piel, pasando la banda, adentro es persona: ahi caian los brillos de la nariz y la
    # sombra de la comisura
    deep_skin = skin * ((di > m) & (do == 0))
    target += deep_skin * (1 - target)
    del deep_skin
    # adentro de la piel solo hasta `far`; afuera y en lo oscuro hasta `reach`, apagandose en
    # el ultimo cuarto
    dist = np.maximum(di, do)
    limit = np.where(di > 0, skin * far + (1 - skin) * reach, reach)
    w *= np.clip((limit - dist) / (0.25 * limit), 0, 1)
    out = alpha.copy()
    out[y0:y1, x0:x1] = np.maximum(a + w * (target - a), floor)
    del floor, a_dark
    if face is not None:
        # Detras de la ceja, las pestanas y el ojo hay piel, no pared. El matting a 1024 los dejaba
        # en 0.6-0.9 y el aclarado de la pared les ponia un velo gris (perfil, gate v7). Dentro de
        # la elipse de la cara, lo que esta a mas de 2 bandas del contorno es persona.
        ell = np.zeros((n, n), np.uint8)
        cx, cy, rx, ry = (int(round(v)) for v in face)
        cv2.ellipse(ell, (cx, cy), (rx, ry), 0, 0, 360, 1, -1)
        deep = ((d_full > 2 * m) & (ell > 0)).astype(np.float32)
        np.maximum(out, cv2.GaussianBlur(deep, (0, 0), m / 2), out=out)
        del ell, deep
    # Niveles, como una seleccion solida: el ruido de la proyeccion recortado en 1 deja el
    # adentro del buzo en 0.99, y en un negro ese 1 % de pared aclarada ya son +2-3 L* (gate v7).
    out -= SOLID[0]
    out *= 1.0 / (SOLID[1] - SOLID[0])
    return np.clip(out, 0, 1, out=out)


SKIN_SIGMA = 0.4  # desenfoque del sensor, en m, donde no se puede medir: 2 px a 4170 (un perfil mide 5,2 px de 10 a 90 %)
SKIN_SMOOTH = 1.0  # suavizado del contorno a lo largo del borde, en m
SKIN_TANG = 3.0  # ventana a lo largo del borde para medirlo, en m
SKIN_REL = (0.45, 0.2)  # la rampa entera hasta |F - B| / pared 0.45, nada desde 0.65
SKIN_FILL = (1.0, 0.02, 0.03)  # la mordida: el faltante neto en una gaussiana de 1 m, desde 0.02 y entero desde 0.05


def skin_ramp(f: np.ndarray, m: int, proj: np.ndarray, wgt: np.ndarray) -> np.ndarray:
    """Rampa alrededor del contorno 0.5 de `f`, con el contorno suavizado.

    La distancia con signo al contorno sale de un desenfoque gaussiano del umbral: para un
    borde recto, Phi^-1 del umbral desenfocado por sigma_s es la distancia / sigma_s, con
    precision sub-pixel; el unico sesgo es la curvatura (sigma_s^2 k / 2, ~0.05 px en una
    mandibula). El desenfoque promedia la posicion del contorno a lo largo del borde (los
    dientes) sin ensanchar la rampa, que la pone Phi(d / sigma).

    sigma es el de la foto en ese tramo (`skin_width`), o el del sensor donde no se puede medir.
    """
    b = cv2.GaussianBlur((f > 0.5).astype(np.float32), (0, 0), SKIN_SMOOTH * m)
    np.clip(b, 1e-7, 1 - 1e-7, out=b)
    d = ndtri(b).astype(np.float32)
    del b
    d *= SKIN_SMOOTH * m  # distancia al contorno, px (+ adentro)
    sig = skin_width(d, proj, wgt, m)
    d /= sig
    return ndtr(d).astype(np.float32)


def skin_width(d: np.ndarray, proj: np.ndarray, wgt: np.ndarray, m: int) -> np.ndarray:
    """El desenfoque del borde en cada tramo, medido en la propia foto.

    La camara no deja el borde igual en toda la cara: en la mandibula del retrato con anteojos (mas lejos del
    foco) el 25-75 % mide ~4 px y arriba ~2; en la cara bajo el lente ~1.7. Un pixel solo no
    dice nada (la textura pesa como el salto), pero el promedio de la proyeccion a la misma
    distancia del contorno, a lo largo de 3 m de borde, es el perfil del borde de ese tramo (el
    "ESF" alineado). Del 25-75 % de ese perfil sale sigma; se calcula a 1/4 (la ventana es
    ancha) y se acota a 0.25-0.8 m. Donde el perfil no sube de la pared a la piel, sigma del sensor.
    """
    h, wd = d.shape
    q = 4
    small = (max(1, wd // q), max(1, h // q))
    st = SKIN_TANG * m / q

    def mean_at(lo: float, hi: float) -> np.ndarray:
        k = ((d >= lo) & (d < hi)).astype(np.float32) * wgt
        num = cv2.GaussianBlur(cv2.resize(k * proj, small, interpolation=cv2.INTER_AREA), (0, 0), st)
        den = cv2.GaussianBlur(cv2.resize(k, small, interpolation=cv2.INTER_AREA), (0, 0), st)
        return num / np.maximum(den, 1e-4), den

    u = 0.2 * m  # 1 px a 4170
    lo, _ = mean_at(-9 * u, -6 * u)
    hi, _ = mean_at(5 * u, 8 * u)
    span = hi - lo
    edges = np.arange(-5, 5.01, 1.0)  # el perfil en bins de 1 px, -5..+5
    prev = None
    x25 = np.full(lo.shape, np.nan, np.float32)
    x75 = np.full(lo.shape, np.nan, np.float32)
    for t in edges:
        e, den = mean_at((t - 0.5) * u, (t + 0.5) * u)
        e = (e - lo) / np.maximum(span, 1e-3)
        e[den < 1e-3] = np.nan
        if prev is not None:
            pe, pt = prev
            for L, x in ((0.25, x25), (0.75, x75)):
                hit = np.isnan(x) & (pe < L) & (e >= L)
                x[hit] = (pt + (L - pe) / np.maximum(e - pe, 1e-6) * u)[hit]
        prev = (e, t * u)
    sig = (x75 - x25) / 1.349
    ok = np.isfinite(sig) & (span > 0.5)
    conf = np.where(ok, np.clip((span - 0.5) / 0.2, 0, 1), 0).astype(np.float32)
    sig = np.where(ok, np.clip(sig, 0.25 * m, 0.8 * m), SKIN_SIGMA * m).astype(np.float32)
    sig = conf * sig + (1 - conf) * np.float32(SKIN_SIGMA * m)
    return cv2.resize(sig, (wd, h), interpolation=cv2.INTER_LINEAR)


RIM_HAIR = 0.3  # un pelo: le falta al menos esto de pared en algun canal
RIM_HAIR_PX = 2  # el piso vale a esta distancia de un pelo o menos (px a 4170)
RIM_MIN = 0.10  # ruido de 1 - min_c(I_c/B_c) en la pared pura (p99.9: 0.085 en el retrato con anteojos)
RIM_WALL = (0.15, 0.07)  # alpha medio del anillo de pared: limpia 0.03-0.07, junto al aro de unos anteojos 0.17-0.18
RIM_H_SIGMA = 2.0  # radio del color local del pelo, en unidades de m (10 px a 4170)
RIM_H_PASSES = 3  # cada pasada se queda con la mitad mas oscura del pelo de al lado (3: ~p12)
RIM_MARGIN = 0.1  # rampa: el piso cuenta donde la mezcla le gana a la proyeccion por esto
RIM_SKIN = (0.05, 0.1)  # hay piel en la mezcla: wF desde 0.05, entero desde 0.15
RIM_SOLID = (0.75, 0.1)  # o casi sin pared: alpha de la mezcla desde 0.75, entero desde 0.85


def skin_hair_alpha(I: np.ndarray, F: np.ndarray, B: np.ndarray, a_c: np.ndarray, skin: np.ndarray, hair_px: int = 2,
                    h_sigma: float = 10.0) -> np.ndarray:
    """Piso del alpha donde un mechon oscuro corre pegado al filo de la piel: piel + pelo, sin pared.

    En un perfil, entre la ceja y el parpado (QA v7, la mordida blanca de 4 a 10 px) el
    mechon y el filo de piel se tocan. La proyeccion sobre la recta piel-pared supone que cada pixel
    es piel y pared, y ahi falla dos veces:
    - el del medio (321/211/229 contra pared 241/243/254 y piel ~700/500/500) es piel y pelo: mas
      claro que la pared solo en el rojo, sobre la recta da alpha 0.05-0.09;
    - el mechon (166/150/102) cae del lado de la pared sobre la misma recta y la proyeccion lo deja
      en 0; adentro de la silueta el brillo (a_dark) le da 0.3-0.45.
    El aclarado de la pared volvia todo eso una mordida blanca entre el pelo y la piel.

    Aca cada pixel es una mezcla de tres colores, todos divididos por la pared de al lado (que queda
    en 1, 1, 1): la piel F, el pelo H y la pared, con pesos >= 0 que suman 1 (unmix3). El alpha es
    lo que no es pared. Una mezcla piel-pared da lo mismo que la proyeccion; una piel-pelo da 1 y
    una pelo-pared da la transparencia del pelo.
    - H es el pelo de al lado: la media gaussiana (h_sigma) de los pelos (a_min > RIM_HAIR),
      quedandose RIM_H_PASSES veces con la mitad mas oscura. Un H mas claro que el pelo de verdad
      le da al pelo sobre la pared mas alpha del que tiene (con la media a secas, +0.09 en promedio
      y hasta +0.3 en un perfil); uno mas oscuro solo se queda corto.
    - a_min = 1 - min_c(I_c / B_c) - RIM_MIN marca los pelos: con F >= 0 la pared que tiene el
      pixel no puede ser mas que el canal que mas le falta, y al pelo castano le falta el azul.
      En una mezcla piel-pared es 0 (la piel es mas clara en los tres canales).
    Solo a hair_px o menos de un pelo y con piel de al lado (F calida y clara): sin pelo, la cola
    roja de la rampa de la piel (el rojo del sensor se abre mas que el verde, con un pozo chico en
    verde y azul) es la misma mezcla de colores y el piso movia el borde de la piel limpia, y la
    piel vista a traves del vidrio de unos anteojos tambien.
    El piso solo cuenta donde la mezcla da mas persona que la proyeccion a_c (rampa RIM_MARGIN):
    donde coinciden (piel-pared) siguen mandando la proyeccion y la mezcla con el matting de la
    banda, y el borde de piel limpio queda igual bit a bit (sin la rampa, el retrato con anteojos cambiaba 0.02 junto
    al lente y un pelo de la ceja de un perfil pasaba la referencia por 0.25).
    Memoria: el recuadro entero solo ve mapas de un canal; el color del pelo se mide canal por
    canal en el recuadro chico que rodea a la zona, y la mezcla solo en los pixeles de la zona.
    """
    lum = np.array([0.2126, 0.7152, 0.0722], np.float32)
    ratio_c = lambda c, sl=np.s_[:, :]: I[sl][..., c] / np.maximum(B[sl][..., c], 1e-6)  # noqa: E731
    r_min = ratio_c(0)
    for c in (1, 2):
        np.minimum(r_min, ratio_c(c), out=r_min)
    hair = r_min < 1 - RIM_MIN - RIM_HAIR  # a_min > RIM_HAIR
    del r_min
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * hair_px + 1,) * 2)
    zone = cv2.dilate(hair.astype(np.uint8), k).astype(np.float32)
    e_f = F[..., 0] / np.maximum(B[..., 0], 1e-6) - F[..., 1] / np.maximum(B[..., 1], 1e-6)
    zone *= np.clip((e_f - 0.3) / 0.15, 0, 1)
    del e_f
    zone *= np.clip((skin - 0.5) / 0.3, 0, 1)
    out = np.zeros(zone.shape, np.float32)
    ys, xs = np.nonzero(zone)
    if not len(ys):
        return out
    # recuadro chico: la zona mas el alcance del desenfoque (4 sigma en OpenCV), asi H sale igual
    pad = int(4 * h_sigma) + 2
    py0, px0 = max(0, ys.min() - pad), max(0, xs.min() - pad)
    sl = np.s_[py0 : ys.max() + pad + 1, px0 : xs.max() + pad + 1]
    idx = (ys - py0, xs - px0)
    core = hair[sl].astype(np.float32)
    yr = lum[0] * ratio_c(0, sl)
    for c in (1, 2):
        yr += lum[c] * ratio_c(c, sl)

    def blur_mean(x: np.ndarray, w: np.ndarray) -> np.ndarray:
        x *= w
        mean = cv2.GaussianBlur(x, (0, 0), h_sigma)
        mean /= np.maximum(cv2.GaussianBlur(w, (0, 0), h_sigma), 1e-6)
        return mean

    for _ in range(RIM_H_PASSES):
        core *= yr <= blur_mean(yr.copy(), core)
    del yr
    H = np.stack([blur_mean(ratio_c(c, sl), core)[idx] for c in range(3)], axis=-1)
    del core
    x = I[sl][idx] / np.maximum(B[sl][idx], 1e-6)
    f = F[sl][idx] / np.maximum(B[sl][idx], 1e-6)
    w_b, w_f = unmix3(x, f, H)
    a_u = 1 - w_b
    a_u *= np.clip((a_u - a_c[ys, xs]) / RIM_MARGIN, 0, 1)
    # Solo donde el pelo toca la piel: con piel en la mezcla (wF) o casi sin pared (el mechon
    # entero). Un pelo fino sobre la pared, sin piel, queda con su alpha por brillo
    # (key_thin_hair): con el de la mezcla le quedaba una mancha gris de 5 px al lado del mechon
    # de un perfil (piloto r2).
    del w_b, w_f
    out[ys, xs] = zone[ys, xs] * a_u
    return out


def unmix3(x: np.ndarray, f: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Parte de pared de cada pixel, por mezcla de tres colores normalizados por la pared.

    x, f, h: (N, 3), el pixel, la piel y el pelo divididos por la pared (que queda en 1, 1, 1).
    x = wF f + wH h + wB 1 con wF + wH + wB = 1 y pesos >= 0: cuadrados minimos con la suma
    eliminada (x - 1 = wF (f - 1) + wH (h - 1)), en forma cerrada. Si la solucion libre sale del
    triangulo, el optimo esta en un lado: se prueban los tres (cada uno recortado a [0, 1]) y
    gana el de menor residuo. Devuelve wB y wF.
    """
    u, v, r = f - 1, h - 1, x - 1
    uu, vv, uv = (u * u).sum(1), (v * v).sum(1), (u * v).sum(1)
    ur, vr = (u * r).sum(1), (v * r).sum(1)
    det = uu * vv - uv * uv
    ok = det > 1e-6 * uu * vv  # piel y pelo en la misma recta que la pared: solo los lados
    det = np.where(ok, det, 1.0)
    wf = np.where(ok, (vv * ur - uv * vr) / det, -1.0)
    wh = np.where(ok, (uu * vr - uv * ur) / det, -1.0)
    inside = (wf >= 0) & (wh >= 0) & (wf + wh <= 1)
    # los lados: piel-pared (wH = 0), pelo-pared (wF = 0), piel-pelo (wB = 0)
    t_f = np.clip(ur / np.maximum(uu, 1e-12), 0, 1)
    t_h = np.clip(vr / np.maximum(vv, 1e-12), 0, 1)
    fh = f - h
    t_fh = np.clip(((x - h) * fh).sum(1) / np.maximum((fh * fh).sum(1), 1e-12), 0, 1)
    err = np.stack([((r - t_f[:, None] * u) ** 2).sum(1), ((r - t_h[:, None] * v) ** 2).sum(1),
                    ((x - h - t_fh[:, None] * fh) ** 2).sum(1)])
    side = np.argmin(err, axis=0)
    edge = np.choose(side, [1 - t_f, 1 - t_h, np.zeros_like(t_fh)])
    edge_f = np.choose(side, [t_f, np.zeros_like(t_h), t_fh])
    return np.where(inside, 1 - wf - wh, edge).astype(np.float32), np.where(inside, wf, edge_f).astype(np.float32)


S_SRC_OFF = 0.45  # fuera de la recta piel-pared: el pliegue, no la rampa (la rampa del lente da 0.2-0.4)
S_LUM = (0.25, 0.1)  # tan claro como la pared, +-25 %: lo que el piso por brillo (a_dark) no ve
S_PERP = (0.25, 0.1)  # S se aparta de la recta piel-pared al menos esto (en |F - B|), si no la cuenta no se sostiene
S_RED = 0.1  # R/G al menos 10 % sobre el de la piel
S_WEIGHT = (0.026, 0.012)  # cuanto pliegue tiene que haber cerca para medir S (rampa: sin escalon donde se acaba)


def second_colour(I: np.ndarray, F: np.ndarray, B: np.ndarray, off: np.ndarray, di: np.ndarray, do: np.ndarray,
                  skin: np.ndarray, a_dark: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
    """Alpha con dos colores de persona: piel F y un pliegue S de otro color, contra la pared B.

    A traves de un lente de anteojos la mejilla termina en una punta rojo oscuro (S), tan oscura como la
    pared. Fuera de la recta piel-pared, refine_edges le daba la silueta (1) a toda la punta, aunque
    se va mezclando con la pared; y sobre la recta, la union de la punta con la piel (piel + rojo,
    persona entera) caia a 0.6-0.7, porque el rojo oscuro cuenta como pared. Una punta opaca y una
    union a medias: la muesca blanca junto al aro.

    Cada pixel de la banda de piel (0 < di <= m) se descompone en I - B = a_s (S - B) + a_f (F - B),
    los dos >= 0, y su alpha es a_s + a_f (la pared es 1 - a_s - a_f). S es la media local de lo
    que esta bien fuera de la recta, tan claro como la pared y mas rojo que la piel, 2-10 px adentro.
    Devuelve (filas, columnas, alpha, peso) de esos pixeles, o None si no hay pliegue. Pesa solo
    cerca del pliegue y donde el plano B-F-S explica el pixel; lo demas conserva el alpha de antes.
    Lo oscuro (pestanas, pelo) ya lo resuelve el piso por brillo: queda fuera de S y de la banda
    (pesa por 1 - 3 a_dark). El aro dorado queda fuera de S por no ser rojo.
    """
    lw = np.array([0.2126, 0.7152, 0.0722], np.float32)
    cy, cx = np.nonzero((off > S_SRC_OFF) & (di > 2) & (di <= 2 * m))
    i, b, f = I[cy, cx].astype(np.float32), B[cy, cx], F[cy, cx]
    ok = np.abs((i @ lw) / np.maximum(b @ lw, 1e-6) - 1) < S_LUM[0]
    # y mas rojo que la piel: un pliegue o la sombra de la piel, no el aro dorado de los anteojos
    ok &= i[:, 0] * f[:, 1] > (1 + S_RED) * i[:, 1] * f[:, 0]
    if not ok.any():
        return None
    srcf = np.zeros(di.shape, np.float32)
    srcf[cy[ok], cx[ok]] = 1
    del cy, cx, i, b, f, ok
    # cuanto pliegue hay cerca: la densidad de S, y su maximo a m px (la punta del pliegue, que ya
    # casi no tiene pixeles de S, se mide con el pliegue de al lado; mas alla se apaga)
    ws = cv2.GaussianBlur(srcf, (0, 0), 2 * m)
    cv2.dilate(ws, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * m + 1,) * 2), dst=ws)
    ys, xs = np.nonzero(ws > S_WEIGHT[0])
    k = skin[ys, xs] * (1 - np.clip(3 * a_dark[ys, xs], 0, 1))
    keep = (di[ys, xs] > 0) & (di[ys, xs] <= m) & (do[ys, xs] == 0) & (k > 0)
    ys, xs, k = ys[keep], xs[keep], k[keep]
    del keep
    if not len(ys):
        return None
    # S solo en la caja de la banda que lo usa (a la maestra entera seria otra imagen de 3 canales)
    py0, py1 = max(0, ys.min() - 6 * m), ys.max() + 6 * m + 1
    px0, px1 = max(0, xs.min() - 6 * m), xs.max() + 6 * m + 1
    sub = srcf[py0:py1, px0:px1]
    S = cv2.GaussianBlur(I[py0:py1, px0:px1] * sub[..., None], (0, 0), 2 * m)
    S /= np.maximum(cv2.GaussianBlur(sub, (0, 0), 2 * m), 1e-6)[..., None]
    del sub, srcf
    s = S[ys - py0, xs - px0]
    del S
    b, f, i = B[ys, xs], F[ys, xs], I[ys, xs].astype(np.float32)
    u, v, r = s - b, f - b, i - b
    uu, uv, vv = (u * u).sum(1), (u * v).sum(1), np.maximum((v * v).sum(1), 1e-12)
    ur, vr = (u * r).sum(1), (v * r).sum(1)
    det = np.maximum(uu * vv - uv * uv, 1e-12)
    a_s, a_f = (vv * ur - uv * vr) / det, (uu * vr - uv * ur) / det
    # con un coeficiente negativo, el mejor de los dos con uno solo (NNLS de dos variables)
    s1, f1 = np.maximum(ur / np.maximum(uu, 1e-12), 0), np.maximum(vr / vv, 0)
    use_s = ((r - s1[:, None] * u) ** 2).sum(1) < ((r - f1[:, None] * v) ** 2).sum(1)
    neg = (a_s < 0) | (a_f < 0)
    a_s = np.where(neg, np.where(use_s, s1, 0), a_s)
    a_f = np.where(neg, np.where(use_s, 0, f1), a_f)
    res = np.sqrt(((r - a_s[:, None] * u - a_f[:, None] * v) ** 2).sum(1) / vv)
    perp = np.sqrt(np.maximum(uu - uv * uv / vv, 0) / vv)
    lum_r = (s @ lw) / np.maximum(b @ lw, 1e-6)
    k *= np.clip((ws[ys, xs] - S_WEIGHT[0]) / S_WEIGHT[1], 0, 1)
    k *= np.clip((perp - S_PERP[0]) / S_PERP[1], 0, 1)
    k *= np.clip((S_LUM[0] - np.abs(lum_r - 1)) / S_LUM[1], 0, 1)
    k *= np.clip((0.3 - res) / 0.15, 0, 1)  # el plano explica el pixel, como on_line con la recta
    return ys, xs, np.clip(a_s + a_f, 0, 1).astype(np.float32), k.astype(np.float32)


def key_thin_hair(img: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """El pelo sobre la pared por su brillo: mascara de luminancia, desde el contorno.

    El matting a 1024 px no ve un mechon de 2-3 px: los de detras de la oreja del retrato con anteojos quedaron con
    alpha ~0, y el aclarado de la pared los borraba (gate v7). Es la seleccion de pelo a mano:
    el brillo de la pared de al lado contra el del pixel; el pelo es ~10 veces mas oscuro.

    La pared de al lado es la mayor de dos medidas. Un cierre morfologico del brillo (radio
    12 px) rellena lo oscuro mas angosto que eso (mechones sueltos) y sigue las sombras suaves de
    la pared. Pero pegado a algo oscuro y grande no llega a la pared: detras de la oreja del retrato con anteojos
    (oreja oscura, mechones opacos pegados) el cierre se hundia, esos mechones quedaban en 0.1-0.3 y
    el dodge de la cara no los tocaba: una raya oscura en el borde de la oreja (el fotografo, v7). Por
    eso tambien el promedio de la pared pura de al lado, como en `styles.wall_behind`.

    Desde la banda del borde (5 px afuera) hasta el 4 % del lado. Adentro de la banda, que en un
    borde limpio es la rampa del sensor, solo donde refine_edges se equivoca: donde la pared que
    mide (a 5-20 px del contorno) es pelo, bastante mas oscura que la pared de al lado. Contra la
    pared limpia (el buzo, la campera) su proyeccion es fiel y la mascara la corria 0,3 px hacia
    afuera (gate v7). Solo sube el alpha, y en la piel no hace nada: con F clara, el brillo da
    menos que el alpha verdadero (alpha (1 - F/B) / 0.9).
    """
    n = alpha.shape[0]
    k = n / 4170
    m = max(2, round(5 * k))  # los mismos anchos que refine_edges
    band = 0.04 * n
    d_out = cv2.distanceTransform((alpha <= 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    ys, xs = np.where((d_out < band) & (alpha < 0.99))
    if not len(ys):
        return alpha
    r = max(2, round(12 * k))
    sig = max(0.8, 12 * k)
    pad = max(2 * r, int(3 * sig) + 1)
    y0, y1 = max(0, ys.min() - pad), min(n, ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(n, xs.max() + pad + 1)
    del ys, xs
    a, do = alpha[y0:y1, x0:x1], d_out[y0:y1, x0:x1]
    del d_out
    y = cv2.GaussianBlur(luminance(img[y0:y1, x0:x1]).astype(np.float32), (0, 0), max(0.5, 0.7 * k))
    env = cv2.morphologyEx(y, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2))
    wall = wall_level(y, a, k, sig)
    np.maximum(env, wall, out=env)
    # la pared que mide refine_edges (anillo de m a 4m afuera, media gaussiana) contra la de al lado
    ring = ((do > m) & (do <= 4 * m)).astype(np.float32)
    ring_b = cv2.GaussianBlur(y * ring, (0, 0), 3 * m) / np.maximum(cv2.GaussianBlur(ring, (0, 0), 3 * m), 1e-6)
    del ring
    wrong = np.clip((0.85 - ring_b / np.maximum(wall, 1e-6)) / 0.2, 0, 1)
    del ring_b, wall
    zone = np.maximum(wrong, np.clip((do - m) / m, 0, 1)) * (a < 0.99) * np.clip((band - do) / (0.25 * band), 0, 1)
    del wrong, do
    # 0.04 es el ruido del sensor
    key = np.clip(((env - y) / (0.9 * np.maximum(env, 1e-6)) - 0.04) / 0.96, 0, 1)
    del y, env
    out = alpha.copy()
    out[y0:y1, x0:x1] = np.maximum(a, key * zone)
    return out


def wall_level(y: np.ndarray, alpha: np.ndarray, k: float, sig: float) -> np.ndarray:
    """El brillo de la pared de al lado: promedio de la pared pura (radio `sig`), y donde no hay
    pared cerca, un promedio ancho calculado a 1/8."""
    pure = cv2.erode((alpha < 0.01).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * max(1, round(4 * k)) + 1,) * 2))
    pure = pure.astype(np.float32)
    den = cv2.GaussianBlur(pure, (0, 0), sig)
    near = cv2.GaussianBlur(y * pure, (0, 0), sig) / np.maximum(den, 1e-6)
    h, w = y.shape
    small = (max(1, w // 8), max(1, h // 8))
    s_num = cv2.GaussianBlur(cv2.resize(y * pure, small, interpolation=cv2.INTER_AREA), (0, 0), 6 * sig / 8)
    s_den = cv2.GaussianBlur(cv2.resize(pure, small, interpolation=cv2.INTER_AREA), (0, 0), 6 * sig / 8)
    wide = cv2.resize(s_num / np.maximum(s_den, 1e-6), (w, h), interpolation=cv2.INTER_LINEAR)
    del pure, s_num, s_den
    cover = np.clip(den / 0.15, 0, 1)
    del den
    near *= cover
    near += (1 - cover) * wide
    return near


def foreground_tiled(img_lin: np.ndarray, alpha: np.ndarray, scale: float, tiles: int = 2, overlap: int = 160) -> np.ndarray:
    """Color del primer plano por partes con superposicion: misma calidad, la mitad de memoria.

    A 4170 px la estimacion entera pasaba los 4 GB (regla de la Mac). Es local, asi que
    por cuadrantes con 160 px de solape y mezcla lineal en el solape da lo mismo.
    """
    n = img_lin.shape[0]
    out = np.zeros_like(img_lin, dtype=np.float32)
    weight = np.zeros((n, n, 1), np.float32)
    edges = np.linspace(0, n, tiles + 1).astype(int)
    for i in range(tiles):
        for j in range(tiles):
            y0, y1 = max(0, edges[i] - overlap), min(n, edges[i + 1] + overlap)
            x0, x1 = max(0, edges[j] - overlap), min(n, edges[j + 1] + overlap)
            srgb = np.clip(linear_to_srgb(img_lin[y0:y1, x0:x1] / scale), 0, 1).astype(np.float64)
            fg = estimate_foreground_ml(srgb, alpha[y0:y1, x0:x1].astype(np.float64))
            fg = srgb_to_linear(np.clip(fg, 0, 1)).astype(np.float32) * scale
            wy = ramp(y1 - y0, y0 > 0, y1 < n, overlap)
            wx = ramp(x1 - x0, x0 > 0, x1 < n, overlap)
            w = (wy[:, None] * wx[None, :])[..., None]
            out[y0:y1, x0:x1] += fg * w
            weight[y0:y1, x0:x1] += w
            del srgb, fg
    return out / np.maximum(weight, 1e-6)


def ramp(length: int, start: bool, end: bool, overlap: int) -> np.ndarray:
    w = np.ones(length, np.float32)
    k = 2 * overlap
    if start:
        w[:k] = np.linspace(0, 1, k, dtype=np.float32)
    if end:
        w[-k:] = np.minimum(w[-k:], np.linspace(1, 0, k, dtype=np.float32))
    return np.maximum(w, 1e-3)
