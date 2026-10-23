"""Estilos de foto de perfil: tres referencias de fondo claro y el color de la camara.

Cada estilo copia a su referencia por medicion (measure.py), pero comparando lo que se
puede comparar entre dos fotos con luces distintas. Las fotos de la sesion tienen luz lateral
dura; las referencias, luz frontal suave. Igualar los niveles de toda la cara aplanaba su
luz (la sombra subia, lo iluminado bajaba) y quedaba palido y sin volumen. Ahora:

1. La foto entera se queda: persona y pared son los pixeles reales. El alpha (matte.py)
   solo dice cuanto aclarar cada pixel de pared. Antes la pared se reemplazaba por un
   fondo sintetico y de ahi salian el halo, el borde blando y el aspecto de recorte.
2. Curva de tonos con dos anclas: el negro con el negro y la piel iluminada con la piel
   iluminada (la luz suave de la cara, percentil 90, en la referencia y en la mia).
3. La sombra de la cara se levanta o se hunde hacia la de la referencia, pero con tope:
   como mucho FILL_EV de relleno. Mas que eso es cambiar la luz, y eso no se hace en post.
4. Contraste local por escala (Shih et al. 2014, Bae et al. 2006): la energia de cada
   banda de una pila laplaciana sobre la cara, igualada a la de la referencia con una
   ganancia por banda. Reemplaza a la "claridad" de una sola escala.
5. La pared se lleva al plano medido en la referencia (nivel e inclinaciones) con una
   mascara de ganancia sobre los pixeles reales: multiplicar, no componer.
6. Grano de tres escalas en mezcla fija, igualado a la energia fina del fondo de la referencia.
7. En color, la persona como la saco la camara: su curva y su croma por brillo, medidas
   contra el JPEG de la camara (camera_color.py). Cambian solo la pared y los granos.

Todo sin IA generativa: nada se inventa, se mueve la luz que ya esta en la foto.

Salida: una imagen maestra por foto y estilo (el encuadre abierto a 4170 px, la resolucion
nativa, para el editor), los tres encuadres de siempre a 1024 px recortados de ella y
work/ajustes.json con lo medido y lo que se le hizo a cada foto.

Cada foto corre en su propio proceso (una maestra nativa pasa los 2 GB, y entre foto y
foto la memoria vuelve a cero); despues las comparaciones se arman leyendo lo exportado.

Uso: MallocLargeCache=0 taskpolicy -b nice -n 19 .venv/bin/python recipe/styles.py [estilo ...]
     ... recipe/styles.py <foto> [estilo ...]   # una foto sola, sin las comparaciones

Con estilos elegidos, el original de la camara y el raw se exportan solo si cambio algo de lo que
entra en ellos (la huella en work/<foto>-originales.sha256): no dependen del estilo. Las fotos
corren de a dos (de a una si la Mac ya tiene presion de memoria).
"""

import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache

import cv2
import numpy as np

from camera_color import (apply_chroma, apply_matrix, apply_tone, camera_lstar, camera_matrix, fit_chroma, fit_mask, fit_tone,
                          lab_of)
from camera_lut import camera_lut
from common import ROOT, linear_to_srgb, luminance, save_jpeg, save_tiff16, srgb_to_linear, to_uint8
from geometry import FRAMINGS, crop_box, load_crop
from masks import background_full, guided_filter, key_wall, skin_chroma_mask
from matte import cached as matte_cached
from matte import upsample_alpha
from measure import (BAND_CENTERS, BAND_SIGMAS, FACE_RX, MIN_BAND_PX, SIZE, band_energy, ellipse_mask, flat_face, light_shape, lit_skin, measure, upper_face,
                     measure_reference, plane_fit, reference_profile, skin_bands)
from output import PROCESS, camera_original, comparison_card, raw_original, reference_image, reference_path, sheet
from photos import PHOTOS
from tone import fit_curve, lstar, pchip, y_from


@dataclass(frozen=True)
class Style:
    key: str
    label: str
    reference: str | None = None  # los objetivos salen de medir la referencia
    targets: dict | None = None  # o se dan a mano (estilo investigado)
    mono: bool = True
    skin_hue: float | None = None  # matiz de la piel buscado, en grados (color sin referencia)
    chroma_cap: float = 1.25  # la croma de la piel nunca pasa de esto por la natural
    keep_light: bool = False  # no tocar la sombra de la cara
    grain_r: float = 0.0  # radio del grano de pelicula en pixeles de la maestra (0 = sin grano agregado)
    camera_look: bool = False  # la persona con el tono y el color del JPEG de la camara (camera_color.py)


# Techo fotografico de la piel iluminada (v6). Las referencias son avatares con luz frontal
# suave y su piel iluminada mide 84-88 L*; copiada sobre la luz lateral dura de estas fotos,
# la mejilla y la nariz se quemaban (el fotografo, QA v5: "foto quemada, pasa con todas"). Para luz
# dura la piel iluminada va a ~75-84 (proceso-notas/investigacion-metodo-v6.md); la prueba con
# el retrato con anteojos a 78 recupero tono y textura. Si la referencia pide mas, se baja todo junto (piel
# iluminada, techo y sombra) la misma cantidad: queda el contraste de la referencia, sin quemar.
LIT_MAX = 80.0
# Grano de pelicula por el modelo booleano de Newson et al. 2017 (IPOL), solo en ref-b: es
# el unico estilo con grano. Antes el grano se igualaba a la "energia fina" de la referencia,
# pero un avatar agrandado no tiene grano medible sino ruido de compresion, y salian nubes
# (QA v4 y v5). Ahora el grano son granos: se pone una sola vez en la maestra, a su tamano
# real, y cada exportacion lo achica como una copia mas chica de la misma pelicula.
GRAIN_R = 0.05

# Fondos claros (pedido del fotografo, 2026-10-10): ref-a y ref-c blancos, ref-b gris claro con
# grano. Cada estilo apunta a su referencia (las tablas de measure.py, la imagen en
# proceso/referencias-ref-<id>.png).
STYLES = [
    Style("ref-a", "Ref A high-key suave", "ref-a"),
    Style("ref-b", "Ref B gris claro con grano", "ref-b", grain_r=GRAIN_R),
    Style("ref-c", "Ref C editorial fondo blanco", "ref-c"),
    # La persona como la saco la camara (el fotografo: "prefiero original"): su tono, su color y su
    # luz, sin dodge ni brillos bajados; cambian solo la pared (clara, como eligio) y los granos.
    # Antes era "color investigado" (piel iluminada 72 y una saturacion pareja), y la mejilla
    # quedaba 8 de croma por encima de la camara y la sombra 8 por debajo (v7).
    Style("color", "Color de la camara", mono=False, keep_light=True, camera_look=True,
          targets=dict(bg_top=90.0, bg_bottom=86.0, bg_a=0.0, bg_b=0.0)),
]

# Tres anclas: el negro, la piel iluminada (p90) y el techo de la piel (p98). Con dos, la
# curva empujaba lo iluminado de tres retratos a 91-94 L*: se pegaba a la pared y se
# perdian pecas y lunares de la frente (QA v4).
ANCHOR_WEIGHTS = {"p1": 1.0, "lit": 3.0, "top": 2.0}
# Lo maximo que se levanta la sombra de la cara, en pasos. Era 0,7 porque la mascara vieja
# tenia pelo y el relleno lo agrisaba; con la mascara por color (masks.skin_chroma_mask)
# se puede rellenar mas sin tocar el pelo.
FILL_EV = 1.2
SHAPE_MIN = 0.3  # y nunca menos del 30 % del modelado: con FILL_EV solo, una cara de sombra poco profunda quedaba plana
SHAPE_MAX = 1.5  # lo maximo que se hunde la sombra: con 2,2 las ojeras pasaban de -31 a -47 y el vello facial se volvia una mancha
# Se iguala solo la banda de 4 a 8 px (en unidades de cara, a SIZE). Las de 0 a 4 px no: la
# referencia es una captura de un avatar y no tiene esa resolucion (Bae et al. §6), asi que
# igualarlas borraba el detalle del RAW. La de 8-16 es el modelado: lo da la luz.
MATCH_BANDS = (3,)  # la referencia es un avatar de ~400 px mostrado a SIZE: la banda 2 (2-4 px) cae en su limite de resolucion
BAND_GAIN = (0.8, 1.3)  # con 2 la ganancia global (sin mapa por zona) oscurecia ojeras y marcaba manchas (Bae et al. §6, QA v4)
# Las bandas se separan con filtro guiado (He et al. 2010), no con gaussianas: un borde fuerte
# (piel contra buzo negro, el logo, el perfil contra la pared) queda en la base y no en el
# detalle, asi que subir el detalle no deja halos. EDGE_EPS es la varianza (en L*/100 al
# cuadrado) a partir de la cual algo es borde y no textura: la piel varia 1-3 L*, un borde 30-60.
EDGE_EPS = 0.04**2
DETAIL_FLOOR = 0.8  # la textura fina conserva al menos el 80 % aunque la curva se aplane ahi
MONO_MIX = np.array([0.45, 0.45, 0.10], np.float32)  # mas rojo que la luminancia: piel pareja en ByN
GRAIN_SKIN = 0.5  # sobre la piel, la mitad: el grano fuerte en la cara parece piel mala
# El matiz de una franja casi sin color (los brillos) es ruido: girarlo 75 grados ponia la
# frente amarilla verdosa. Debajo de esta croma la franja toma el giro de la vecina, y
# ninguna se aparta mas de BAND_HUE_MAX grados del giro general.
MIN_HUE_CHROMA = 6.0
BAND_HUE_MAX = 25.0
# Croma buscada por franja de brillo, relativa a skin_c: la sombra y los brillos tienen
# menos color que los medios (sin esto la sombra quedaba gris oliva, C 11 contra 27).
CHROMA_SHAPE = np.array([0.9, 1.0, 1.0, 1.0, 0.85, 0.6], np.float32)


def targets_of(style: Style) -> dict:
    if style.targets:
        return dict(style.targets)
    path = reference_path(style.reference)
    st = measure_reference(path, style.reference)
    t = dict(p1=st.p1, p99=st.p99)
    t.update(reference_profile(path, style.reference))
    over = t["lit"] - LIT_MAX
    if over > 0:
        for k in ("lit", "top", "shade10", "shade50", "shade90"):
            if k in t:
                t[k] -= over
    t.pop("grain_bands", None)  # el grano lo da el estilo (grain_r), no la referencia
    return t


# --- escena: todo lo que no depende del estilo -------------------------------

@dataclass
class Scene:
    n: int
    img: np.ndarray  # la foto retocada, lineal
    alpha: np.ndarray  # 1 = persona
    geo: tuple[float, float, float]  # cara (cx, cy, r) en el recorte
    face: np.ndarray  # elipse de la cara entera (bool)
    skin: np.ndarray  # peso de piel, suave
    dodge: np.ndarray  # pincel suave sobre la piel, sin huecos (ojos, cejas, boca)
    tint: np.ndarray  # pincel del color de la piel: el de arriba, solo en pixeles con matiz de piel
    skin_ev: float  # dodge de la foto (photos.py): solo si la cara quedo en sombra
    mid_box: tuple[int, int, int]  # el cuadrado del encuadre medio en esta escena (el de la referencia)
    color: np.ndarray  # matriz 3x3 al color del JPEG de la camara (camera_color.py), para el estilo en color
    wall: np.ndarray  # color de la pared detras de cada pixel (lineal, float16): la parte de pared de los pixeles del borde


def face_ellipse(geo) -> tuple[float, float, float, float]:
    cx, cy, r = geo
    return cx, cy + 0.05 * r, 0.78 * r, 1.08 * r


@lru_cache(maxsize=2)  # la escena para resolver (SOLVE) y la de la maestra de la foto en curso
def build_scene(name: str, framing: str, n: int) -> Scene:
    img, geo = load_crop(name, framing, n)
    x0, y0, side = crop_box(name, framing)
    coarse = cv2.resize(background_full(name)[y0 : y0 + side, x0 : x0 + side], (n, n), interpolation=cv2.INTER_AREA)
    a_small, _, _ = matte_cached(f"{name}-{framing}", img, coarse, face_ellipse(geo))
    alpha = upsample_alpha(img, a_small, face_ellipse(geo))
    if PHOTOS[name].get("wall_keys"):
        k = n / side
        alpha = key_wall(img, alpha, [((x - x0) * k, (y - y0) * k, h * k, (sx - x0) * k, (sy - y0) * k)
                                      for x, y, h, sx, sy in PHOTOS[name]["wall_keys"]])
    cx, cy, rx, ry = face_ellipse(geo)
    face = ellipse_mask((n, n), cx, cy, rx, ry)
    norm = np.clip(img / max(float(np.percentile(img, 99)), 1e-6), 0, 1)
    lab = cv2.cvtColor(to_uint8(linear_to_srgb(norm)), cv2.COLOR_RGB2LAB)
    region = ellipse_mask((n, n), cx, cy + 0.3 * ry, rx * 1.25, ry * 1.5).astype(np.float32)
    region = cv2.GaussianBlur(region, (0, 0), rx / 6)
    # piel por color (piel contra pelo y ropa, aprendidos en cada foto): la vieja (a* > 3)
    # era moteada y metia el pelo castano y el buzo (proceso/200 y 201)
    skin = skin_chroma_mask(img, alpha, geo)
    # La piel completa, para bajar brillos y mover luz: el reflejo de la frente es casi
    # blanco, sin el rojo de la piel, y quedaba como un hueco. Se cierran los huecos y se
    # suma lo muy claro dentro de la cara.
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(geo[2] / 4) | 1, int(geo[2] / 4) | 1))
    closed = cv2.morphologyEx((skin > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, k) > 0
    lum = luminance(norm)
    bright = (lum > np.percentile(lum[skin > 0.5], 90)) & ellipse_mask((n, n), cx, cy, rx * 1.2, ry * 1.15) if (skin > 0.5).any() else closed
    full = np.maximum(skin, ((closed | bright) & (alpha > 0.5)).astype(np.float32) * region)
    # Desenfoque normalizado por el alpha (convolucion normalizada): el promedio se toma solo
    # sobre la persona. Con el desenfoque solo, la pared entraba como cero y el pincel caia
    # de 0,57 a 0,16 en los ~100 px antes del borde: una franja de otro tono y otro color a
    # lo largo de la mandibula (perfil en color, QA v5).
    dodge = cv2.GaussianBlur(full * alpha, (0, 0), geo[2] / 6) / np.maximum(cv2.GaussianBlur(alpha, (0, 0), geo[2] / 6), 0.05)
    dodge = np.clip(dodge / max(float(np.percentile(dodge[face], 90)), 1e-3), 0, 1) * alpha
    # El color de la piel se mueve solo donde el color de la foto ya es de piel: el pincel
    # sin huecos tocaba tambien el buzo negro junto al cuello y al subir la croma se ponia
    # violeta. Matiz natural entre ~10 y ~90 grados y no oscuro (pelo, ropa).
    a_, b_ = lab[..., 1].astype(np.float32) - 128, lab[..., 2].astype(np.float32) - 128
    off = np.abs(np.degrees(np.angle(np.exp(1j * (np.arctan2(b_, a_) - np.radians(50)))))).astype(np.float32)
    gate = np.clip(1 - (off - 40) / 25, 0, 1) * np.clip((lab[..., 0].astype(np.float32) * 100 / 255 - 8) / 12, 0, 1)
    tint = cv2.GaussianBlur(gate, (0, 0), max(1.0, n / 1024)) * dodge
    del norm, lab, a_, b_, off, gate, full, lum, region
    mid_box = preset_box(name, "medio", n) if framing == "abierto" else (0, 0, n)
    return Scene(n, img, alpha, geo, face, skin, dodge.astype(np.float32), tint.astype(np.float32),
                 PHOTOS[name].get("skin_ev", 0.0), mid_box, camera_matrix(name, img, skin), wall_behind(img, alpha))


def wall_behind(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """El color de la pared detras de cada pixel: promedio de la pared pura de al lado.

    Pared pura = alpha < 0.01 y a 4 px o mas del borde (en pixeles de la maestra). Promedio
    gaussiano normalizado de 12 px; donde no hay pared cerca (bajo el pelo, el cuello contra
    el hombro) se usa uno de 120 px. Es lo que permite tocar solo la parte de pared de un
    pixel del borde (o solo la de persona): I = alpha F + (1 - alpha) B.
    """
    n = alpha.shape[0]
    unit = n / MASTER
    r = max(1, int(round(4 * unit)))
    pure = cv2.erode((alpha < 0.01).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2))
    pure = pure.astype(np.float32)
    out = np.empty(rgb.shape, np.float16)
    lo = 512
    small, ws = cv2.resize(rgb * pure[..., None], (lo, lo), interpolation=cv2.INTER_AREA), cv2.resize(pure, (lo, lo), interpolation=cv2.INTER_AREA)
    wide = cv2.GaussianBlur(small, (0, 0), 120 * lo / MASTER) / np.maximum(cv2.GaussianBlur(ws, (0, 0), 120 * lo / MASTER), 1e-4)[..., None]
    wide = cv2.resize(wide, (n, n), interpolation=cv2.INTER_LINEAR)
    sig = max(0.8, 12 * unit)
    den = cv2.GaussianBlur(pure, (0, 0), sig)
    for c in range(3):
        num = cv2.GaussianBlur(rgb[..., c] * pure, (0, 0), sig)
        cover = np.clip(den / 0.15, 0, 1)
        out[..., c] = cover * num / np.maximum(den, 1e-6) + (1 - cover) * wide[..., c]
    return out


def person_gain(scene: Scene, f: np.ndarray, gain: np.ndarray, wall: np.ndarray) -> np.ndarray:
    """Una ganancia de la persona (dodge, relleno, brillo) aplicada solo a su parte de cada pixel.

    En un pixel del borde, I = alpha F + (1 - alpha) B. Multiplicar el pixel entero aclaraba
    tambien la pared que tiene adentro: con 1,5 EV en la cara del retrato con anteojos, un halo claro todo
    alrededor. Ahora: I' = I + (gain - 1) max(I - (1 - alpha) B, 0), con B la pared de al lado
    (`wall`, en el mismo color que `f`). El max: si el alpha se queda corto (pelo fino que el
    matting dio por pared), la parte de persona sale negativa y el pixel se iba a negro; los
    mechones detras de la oreja del retrato con anteojos quedaban como manchas negras (gate v7). Asi el pixel
    queda como estaba.
    """
    person = f - (1.0 - scene.alpha)[..., None] * wall
    np.maximum(person, 0, out=person)
    person *= (gain - 1.0)[..., None]
    person += f
    return person


def interior_weight(scene: Scene, w: np.ndarray) -> np.ndarray:
    """Un pincel de la persona sin el factor alpha (que ahora pone person_gain)."""
    return np.clip(w / np.maximum(scene.alpha, 0.02), 0, 1) * (scene.alpha > 0.02)


def crop_scene(scene: Scene, box: tuple[int, int, int]) -> Scene:
    """La escena recortada a un encuadre, para medir con las mismas mascaras."""
    x0, y0, side = box
    sl = (slice(y0, y0 + side), slice(x0, x0 + side))
    cx, cy, r = scene.geo
    return Scene(side, scene.img[sl], scene.alpha[sl], (cx - x0, cy - y0, r), scene.face[sl], scene.skin[sl],
                 scene.dodge[sl], scene.tint[sl], scene.skin_ev,
                 (scene.mid_box[0] - x0, scene.mid_box[1] - y0, scene.mid_box[2]), scene.color, scene.wall[sl])


def face_unit(scene: Scene) -> float:
    """Pixeles de esta escena por pixel de una cara de ancho FACE_RX: para el contraste por escala."""
    return face_ellipse(scene.geo)[2] / FACE_RX


# --- render ------------------------------------------------------------------

@dataclass
class Params:
    curve_in: np.ndarray
    curve_out: np.ndarray
    shape: float = 1.0  # <1 levanta la sombra de la cara, >1 la hunde; lo iluminado queda
    shade_center: float = 0.0  # la luz de la piel iluminada, en log2: el punto fijo de `shape`
    skin_ev: float = 0.0  # dodge sobre la piel (cara, cuello, manos), en EV
    band_gains: np.ndarray = field(default_factory=lambda: np.ones(len(BAND_SIGMAS) - 1, np.float32))
    hue: float = 0.0  # giro del matiz de la piel, en radianes (Lab)
    chroma: float = 1.0  # escala de la croma de la piel
    # matiz y croma por franja de brillo (measure.SKIN_BANDS), encima de los de arriba
    hue_bands: np.ndarray = field(default_factory=lambda: np.zeros(len(BAND_CENTERS), np.float32))
    chroma_bands: np.ndarray = field(default_factory=lambda: np.ones(len(BAND_CENTERS), np.float32))
    shine: float = 0.35  # cuanto se bajan los brillos de la piel (reduce_shine); 0 en el color de la camara
    # color de la camara (camera_color.fit_chroma): ganancia de croma y giro de matiz por L*
    chroma_L: np.ndarray = field(default_factory=lambda: np.zeros(0, np.float32))
    chroma_gain: np.ndarray = field(default_factory=lambda: np.zeros(0, np.float32))
    chroma_turn: np.ndarray = field(default_factory=lambda: np.zeros(0, np.float32))
    detail: float = 0.0  # realce del detalle fino de la persona (add_detail): el enfoque de la camara


def shaped(scene: Scene, style: Style, p: Params) -> tuple[np.ndarray, np.ndarray]:
    """La foto con la luz de la piel retocada. Devuelve (color lineal, luminancia).

    Dodge & burn sobre la luz de baja frecuencia de la piel: la luz suave (un desenfoque
    grande del log de la luminancia, solo con piel) se estira o se comprime alrededor de
    la piel iluminada, que queda fija. La textura no se toca.
    """
    def look(x: np.ndarray) -> np.ndarray:
        """El color de la camara: puntual, igual para todos los pixeles."""
        return x if style.mono else apply_matrix(x, scene.color)

    f = look(scene.img)
    wall = look(scene.wall.astype(np.float32))
    mix = (lambda x: x @ MONO_MIX) if style.mono else luminance
    if p.skin_ev:
        # separa la cara de la ropa cuando la cara quedo en sombra (retrato con anteojos)
        f = person_gain(scene, f, np.exp2(p.skin_ev * interior_weight(scene, scene.dodge)).astype(np.float32), wall)
    y = mix(f)
    if p.shine:
        f, y = reduce_shine(scene, f, y, mix, wall, p.shine)
    if p.shape != 1.0:
        sigma = scene.geo[2] / 5
        w = scene.skin
        log_y = np.log2(np.maximum(y, 1e-5))
        low = cv2.GaussianBlur(log_y * w, (0, 0), sigma) / (cv2.GaussianBlur(w, (0, 0), sigma) + 1e-4)
        # el pincel sin huecos (ojos, cejas, el brillo de la frente), solo sobre la persona: con
        # el desenfoque de la mascara sola el relleno se iba a la pared (velo gris en ref-c)
        weight = interior_weight(scene, scene.dodge)
        # solo lo que esta por debajo de la piel iluminada se mueve
        gain = np.exp2(np.minimum(low - p.shade_center, 0) * (p.shape - 1) * weight).astype(np.float32)
        f = person_gain(scene, f, gain, wall)
        y = mix(f)
    del wall
    return headroom(scene, f, y)


def headroom(scene: Scene, f: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Que nada de la persona pase del blanco antes de la curva (la curva va de 0 a 100 L*)."""
    top = float(np.percentile(y[scene.alpha > 0.5], 99.8))
    k = max(1.0, top / 0.9)
    return f / k, y / k


def reduce_shine(scene: Scene, f: np.ndarray, y: np.ndarray, mix, wall: np.ndarray, amount: float = 0.35) -> tuple[np.ndarray, np.ndarray]:
    """Baja un poco el brillo de la piel (frente, pomulos, nariz): es temporal, como un grano.

    Suave a proposito: bajarlo mucho dejaba un parche plano y grisaceo en la frente. Se
    comprime solo lo que pasa del 85 % mas brillante de la luz suave de la piel.
    """
    w = scene.dodge
    if not (w > 0.5).any():
        return f, y
    sigma = max(2.0, scene.geo[2] / 25)
    low = cv2.GaussianBlur(np.log2(np.maximum(y, 1e-5)), (0, 0), sigma)
    lo, hi = np.percentile(low[w > 0.5], [85, 99.7])
    t = np.clip((low - lo) / max(hi - lo, 1e-3), 0, 1)
    gain = np.exp2(-amount * (low - lo) * t * interior_weight(scene, w)).astype(np.float32)
    f = person_gain(scene, f, gain, wall)
    return f, mix(f)


def tone_map(L: np.ndarray, p: Params, unit: float) -> np.ndarray:
    """La curva sobre la luz (base) y la textura encima, que nunca se aplasta (Durand y Dorsey 2002).

    Con la curva sobre cada pixel, donde se aplana (lo iluminado de una cara con luz dura,
    11 L* de entrada en 2 de salida) las pecas y lunares de la frente desaparecian, y como
    una curva concava baja el promedio, el ajuste la empujaba mas arriba todavia. Ahora la
    base (filtro guiado, los bordes fuertes quedan en ella) pasa por la curva y el detalle
    fino se suma por la pendiente de la curva en ese punto, nunca menos de DETAIL_FLOOR.
    """
    guide = (L / 100).astype(np.float32)
    base = guided_filter(guide, guide, max(1, int(round(2 * BAND_SIGMAS[3] * unit))), EDGE_EPS) * 100
    del guide
    xs = np.linspace(0, 100, 2001, dtype=np.float32)  # la curva como tabla: a 4170 px, pchip por pixel come memoria
    ys = pchip(p.curve_in, p.curve_out, xs)
    out = np.interp(base, xs, ys).astype(np.float32)
    slope = np.interp(base, xs, np.maximum(np.gradient(ys, xs), DETAIL_FLOOR)).astype(np.float32)
    base -= L
    base *= slope  # -(detalle) * pendiente
    out -= base
    return out


def soft_white(lstar_: np.ndarray, knee: float = 92.0, top: float = 98.0) -> np.ndarray:
    """Hombro en las altas luces: arriba de `knee` comprime hacia `top` sin recortar nunca."""
    over = np.maximum(lstar_ - knee, 0)
    return np.where(lstar_ < knee, lstar_, knee + (top - knee) * np.tanh(over / (top - knee)))


def local_contrast(L: np.ndarray, gains: np.ndarray, weight: np.ndarray, unit: float) -> np.ndarray:
    """Cada banda de detalle multiplicada por su ganancia, solo sobre la persona.

    Las bandas salen de filtros guiados del mismo L* a radios crecientes (bordes fuertes
    en la base): sin halos en el cuello contra el buzo ni en el perfil contra la pared.
    """
    if np.allclose(gains, 1.0):
        return L
    guide = (L / 100).astype(np.float32)
    acc = np.zeros_like(L)
    prev = L
    for k in range(int(np.flatnonzero(np.abs(gains - 1.0) > 1e-6)[-1]) + 1):
        radius = max(1, int(round(2 * BAND_SIGMAS[k + 1] * unit)))  # caja de radio 2 sigma ~ gaussiana de sigma
        nxt = guided_filter(guide, guide, radius, EDGE_EPS) * 100
        if gains[k] != 1.0:
            acc += (gains[k] - 1.0) * (prev - nxt)
        prev = nxt
    del prev, guide
    acc *= weight
    acc += L
    return acc


def wall_target(scene: Scene, want: dict, size: int) -> np.ndarray:
    """El fondo de la referencia, RGB lineal a `size` px: su plano medido o un degradado vertical.

    El plano se pone sobre el encuadre medio (el de la referencia). Fuera de ese cuadrado no
    sigue para siempre: queda dentro de lo que la referencia muestra, mas o menos 2 L*.
    """
    t = (np.arange(size, dtype=np.float32) + 0.5) / size * scene.n
    if want.get("bg_plane"):
        c0, cx, cy = want["bg_plane"]
        bx, by, bs = scene.mid_box
        x, y = (t - bx) / bs, (t - by) / bs
        L = c0 + cx * x[None, :] + cy * y[:, None]
        corners = [c0 + cx * u + cy * v for u in (0, 1) for v in (0, 1)]
        L = np.clip(L, min(corners) - 2, min(max(corners) + 2, 99.0))
    else:
        L = np.repeat((want["bg_top"] + (want["bg_bottom"] - want["bg_top"]) * t / scene.n)[:, None], size, axis=1)
    lab = np.stack([L, np.full_like(L, want.get("bg_a", 0.0)), np.full_like(L, want.get("bg_b", 0.0))], axis=2)
    return srgb_to_linear(np.clip(cv2.cvtColor(lab.astype(np.float32), cv2.COLOR_LAB2RGB), 0, 1)).astype(np.float32)


def edit_wall(scene: Scene, rgb: np.ndarray, toe: np.ndarray | None = None, *, want: dict) -> np.ndarray:
    """Lleva la pared real al fondo de la referencia multiplicando, sin reemplazar nada.

    ganancia = fondo buscado / luz suave de la pared real (con la persona tapada). Se aplica
    en proporcion a cuanto de pared tiene cada pixel (1 - alpha): un pelo sobre la pared
    recibe parte, la piel nada. Un error del alpha se vuelve un poco de brillo de mas o de
    menos, no un borde pegado. La textura y el grano de la pared quedan.

    Lejos de la persona la ganancia se calcula contra la pared apenas suavizada (sin grano):
    asi tambien se van las marcas y manchas de la pared, como con un pincel corrector, y queda
    el fondo liso de la referencia con el grano propio. Cerca de la persona no, para no
    tocar pelos sueltos.
    """
    n, lo = scene.n, 512
    # La luz de la pared se estima sin la persona ni un margen alrededor (1 % del lado): con
    # pesos (1 - alpha)^2 el pelo semitransparente oscurecia la estimacion junto a la cabeza,
    # la ganancia subia y quedaba un aura clara de +1,5 a +3 L* pegada al pelo (QA v4).
    a_lo = cv2.resize(scene.alpha, (lo, lo), interpolation=cv2.INTER_AREA)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(0.01 * lo) + 1,) * 2)
    ws = 1.0 - cv2.dilate((a_lo > 0.02).astype(np.uint8), k).astype(np.float32)
    small = cv2.resize(rgb, (lo, lo), interpolation=cv2.INTER_AREA) * ws[..., None]
    sigma = lo / 80  # ~50 px a 4170: sigue la sombra de la persona sobre la pared
    wall = cv2.GaussianBlur(small, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(ws, (0, 0), sigma), 1e-4)[..., None]
    # donde la persona tapa todo el entorno, la pared se extrapola desde mas lejos
    wide = cv2.GaussianBlur(small, (0, 0), 4 * sigma) / np.maximum(cv2.GaussianBlur(ws, (0, 0), 4 * sigma), 1e-4)[..., None]
    cover = np.clip(cv2.GaussianBlur(ws, (0, 0), sigma) / 0.15, 0, 1)[..., None]
    wall = cover * wall + (1 - cover) * wide
    target = wall_target(scene, want, lo)
    gain = cv2.resize(np.clip(target / np.maximum(wall, 1e-5), 0.2, 8.0), (n, n), interpolation=cv2.INTER_LINEAR)
    # lejos de la persona: de 1,5 % a 4 % del lado del encuadre abierto
    free = (a_lo < 0.02).astype(np.uint8)
    dist = cv2.distanceTransform(free, cv2.DIST_L2, 5)
    far = cv2.resize(np.clip((dist - 0.015 * lo) / (0.025 * lo), 0, 1).astype(np.float32), (n, n), interpolation=cv2.INTER_LINEAR)
    if toe is not None:
        # cuanto multiplico la curva a la pared de al lado de cada pixel, con el mismo pincel
        k_lo = cv2.resize(toe, (lo, lo), interpolation=cv2.INTER_AREA) * ws
        k_wall = cv2.GaussianBlur(k_lo, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(ws, (0, 0), sigma), 1e-4)
        k_wide = cv2.GaussianBlur(k_lo, (0, 0), 4 * sigma) / np.maximum(cv2.GaussianBlur(ws, (0, 0), 4 * sigma), 1e-4)
        k_wall = cover[..., 0] * k_wall + (1 - cover[..., 0]) * k_wide
        toe = np.minimum(1.0, toe / np.maximum(cv2.resize(k_wall, (n, n), interpolation=cv2.INTER_LINEAR), 1e-6))
        del k_lo, k_wall, k_wide
    del small, ws, wall, wide, cover, free, dist, a_lo
    # en el lugar: a 4170 px cada copia RGB son 210 MB
    fine = cv2.GaussianBlur(rgb, (0, 0), 2.0 * n / 1536)
    np.maximum(fine, 1e-5, out=fine)
    np.divide(cv2.resize(target, (n, n), interpolation=cv2.INTER_LINEAR), fine, out=fine)
    np.clip(fine, 0.2, 8.0, out=fine)
    fine -= gain
    fine *= far[..., None]
    gain += fine
    del fine, far
    # Solo la parte de pared de cada pixel: I' = I + (1 - alpha)(g - 1) B (Smith y Blinn 1996).
    # Antes se multiplicaba el pixel entero por 1 + (1 - alpha)(g - 1), y eso aclaraba tambien
    # la parte de persona del pixel del borde: el error es alpha (1 - alpha)(g - 1)(F - B),
    # un filete claro en la piel y uno oscuro en el pelo y el buzo (+3 y -8 L*, auditoria v7).
    # En la pared pura B es el pixel mismo (su textura y su grano se escalan, como antes); donde
    # hay algo de persona, B es la pared de al lado de este mismo render.
    gain -= 1.0
    unit = n / MASTER
    r = max(1, int(round(2 * unit)))
    some = cv2.dilate((scene.alpha > 0.02).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2))
    behind = wall_behind(rgb, scene.alpha).astype(np.float32)
    behind -= rgb
    behind *= some[..., None]
    behind += rgb  # B: la pared de al lado donde hay persona, el pixel mismo en la pared pura
    # La parte de pared de un pixel no puede ser mas clara que el pixel entero: (1 - alpha) B <= I.
    # Donde el alpha se queda corto, o la curva oscurecio el pixel y B no (la de la camara lleva el
    # pelo oscuro del retrato con anteojos de 17 a 3 L*), se le sumaba mas pared de la que tiene: el pelo de arriba
    # del retrato con anteojos en color quedaba como un casquete gris, con el 48 % del borde en una parte de pared
    # imposible (QA v7). El tope va por canal: por luminancia la pared, mas neutra que el pelo
    # castano, le sumaba azul y verde de mas y el casquete quedaba gris (croma 15 -> 10, recheck v7).
    # En color la causa es la curva de la camara: multiplica cada pixel por un factor segun su
    # brillo (el pelo de la coronilla del retrato con anteojos por ~0,14, la pared por ~1,2), asi que la pared que
    # queda dentro de un pixel oscuro del borde es (1 - alpha) B por k_pixel / k_pared, no (1 - alpha) B.
    # Sin eso el tope saltaba en el 78 % del borde de la coronilla.
    share = 1.0 - scene.alpha
    if toe is not None:
        share = share * toe
        del toe
    behind *= share[..., None]
    del share
    np.minimum(behind, rgb, out=behind)
    np.maximum(behind, 0.0, out=behind)
    gain *= behind
    del behind, some
    gain += rgb
    return gain


def render(scene: Scene, style: Style, p: Params, want: dict) -> np.ndarray:
    """sRGB 0..1, sin grano ni enfoque de salida."""
    return to_srgb(edit_wall(scene, *render_person(scene, style, p), want=want))


def to_srgb(rgb: np.ndarray) -> np.ndarray:
    return np.clip(linear_to_srgb(np.clip(rgb, 0, 1)), 0, 1).astype(np.float32)


def render_person(scene: Scene, style: Style, p: Params) -> tuple[np.ndarray, np.ndarray | None]:
    """Lineal, con la luz, la curva y el color de la persona, y la pared todavia como salio.

    Devuelve tambien, en color, cuanto multiplico la curva de la camara cada pixel (None en
    blanco y negro): edit_wall lo necesita para saber cuanta pared queda en un pixel del borde.
    """
    f, y = shaped(scene, style, p)
    if style.camera_look:
        # la curva de la camara sobre cada pixel, sin separar base y detalle ni hombro: la
        # camara no los tiene, y la textura queda como en su JPEG
        rgb = apply_tone(f, y, p.curve_in, p.curve_out)
        toe = luminance(rgb) / np.maximum(luminance(f), 1e-6)
        del f, y
        rgb = apply_chroma(clean_color(scene, rgb), p.chroma_L, p.chroma_gain, p.chroma_turn)
        return (add_detail(scene, rgb, p.detail) if p.detail else rgb), toe
    # el contraste local antes del hombro: despues, empujaba la piel clara contra el techo y
    # dejaba un filete quemado en el cuello y la oreja (QA v4)
    L = local_contrast(tone_map(lstar(y), p, face_unit(scene)), p.band_gains, scene.alpha, face_unit(scene))
    L = soft_white(L)
    y_out = y_from(L)
    del L
    if style.mono:
        rgb = np.repeat(y_out[..., None], 3, axis=2)
    else:
        rgb = f * (y_out / np.maximum(y, 1e-6))[..., None]
        rgb = skin_color(scene, p, clean_color(scene, rgb))
    del f, y, y_out
    return rgb, None


def clean_color(scene: Scene, rgb: np.ndarray) -> np.ndarray:
    """El ruido de color que el revelado no saco, sin cruzar nunca el contorno.

    a* y b* suavizados (el brillo no), mas fuerte en lo oscuro, como la reduccion de ruido
    de color de Lightroom: sin esto el pelo tenia confeti rosa y verde. El promedio se toma
    adentro de la persona y adentro de la pared por separado, y los pixeles del borde no se
    tocan: con un desenfoque comun el color de la piel se corria 2-4 px sobre la pared.

    Ya no se neutraliza el borde ni lo oscuro: el gris del borde, despues de enfriar la pared,
    era el filo celeste de la mandibula (auditoria v7).

    En el borde (pelo fino sobre la pared) el color se limpia con un filtro guiado por el
    brillo: en una ventana chica, a* y b* siguen a L* en linea recta, que es lo que hace la
    mezcla de un pelo con la pared, y el ruido (que no sigue a L*) se va. Sin esto los pelos
    sueltos tenian confeti celeste y magenta, 4-7 veces el de la camara (v7).
    """
    lab = cv2.cvtColor(linear_to_srgb(np.clip(rgb, 0, 1)).astype(np.float32), cv2.COLOR_RGB2LAB)
    L = lab[..., 0]
    k = scene.n / MASTER
    dark = np.clip((35 - L) / 20, 0, 1)
    inside = (scene.alpha > 0.99).astype(np.float32)
    outside = (scene.alpha < 0.01).astype(np.float32)

    def nblur(x: np.ndarray, w: np.ndarray, sigma: float) -> np.ndarray:
        return cv2.GaussianBlur(x * w, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigma), 1e-4)

    edge = 1 - inside - outside
    guide = L / 100
    for c in (1, 2):
        ch = lab[..., c]
        out = guided_filter(guide, ch, max(1, round(2 * k)), 1e-3) * edge
        for w in (inside, outside):
            fine = nblur(ch, w, max(0.6, 2 * k))
            coarse = nblur(ch, w, max(1.5, 6 * k))
            out += (fine + dark * (coarse - fine)) * w
            del fine, coarse
        lab[..., c] = out
        del out
    del L, dark, inside, outside, edge, guide
    return srgb_to_linear(np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB), 0, 1))


def skin_color(scene: Scene, p: Params, rgb: np.ndarray) -> np.ndarray:
    """Matiz y croma de la piel como en el HSL de Lightroom, por franja de brillo.

    Se gira el matiz y se escala la croma de cada pixel, asi un brillo casi sin color sigue
    sin color. El giro y la escala cambian con el brillo, como el color grading por sombras,
    medios y luces, y se leen sobre el brillo suavizado: el poro no cambia de color.
    """
    if not (p.hue or p.chroma != 1.0 or p.hue_bands.any() or (p.chroma_bands != 1).any()):
        return rgb
    lab = cv2.cvtColor(linear_to_srgb(np.clip(rgb, 0, 1)).astype(np.float32), cv2.COLOR_RGB2LAB)
    a, b = lab[..., 1].copy(), lab[..., 2].copy()
    L_low = cv2.GaussianBlur(lab[..., 0], (0, 0), scene.n / 400)
    hue = np.interp(L_low, BAND_CENTERS, p.hue + p.hue_bands).astype(np.float32)
    chroma = np.interp(L_low, BAND_CENTERS, p.chroma * p.chroma_bands).astype(np.float32)
    c, s_ = np.cos(hue), np.sin(hue)
    del L_low, hue
    w = scene.tint
    lab[..., 1] = a + w * (chroma * (a * c - b * s_) - a)
    lab[..., 2] = b + w * (chroma * (a * s_ + b * c) - b)
    del a, b, c, s_, chroma
    return srgb_to_linear(np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB), 0, 1))


GRAIN_BIN = ROOT / "tools" / "film_grain" / "bin" / "film_grain_rendering_main"
# El programa reparte los pixeles en hilos (OpenMP): cada pixel sale de su propia semilla, asi
# que con 1 o con 4 hilos el grano es el mismo. 4 con una foto sola; main() baja a 2 cuando
# corren dos fotos a la vez, para dejar libre un cuarto de la CPU (regla de la Mac).
GRAIN_THREADS = 4


def film_grain(srgb: np.ndarray, r: float) -> np.ndarray:
    """La capa de grano (sRGB, centrada en 0) del modelo booleano de Newson et al. 2017.

    La pelicula es un proceso de Poisson de granos de radio `r` (en pixeles): cada pixel
    vale la fraccion cubierta, filtrada como un ampliador. Por eso el grano es mas fuerte
    en los medios tonos y se apaga en el blanco y el negro, como en una copia real, y no
    tiene escalas gruesas: no puede hacer nubes. El programa es el de IPOL (tools/film_grain).
    """
    grey = to_uint8(srgb.mean(axis=2))
    with tempfile.TemporaryDirectory() as d:
        src, dst = f"{d}/in.png", f"{d}/out.png"
        cv2.imwrite(src, grey)
        subprocess.run([str(GRAIN_BIN), src, dst, "-r", str(r), "-sigmaR", "0", "-sigmaFilter", "0.8",
                        "-NmonteCarlo", "100", "-zoom", "1", "-algorithmID", "0", "-color", "0"],
                       check=True, capture_output=True, env={"OMP_NUM_THREADS": str(GRAIN_THREADS), **os.environ})
        out = cv2.imread(dst, cv2.IMREAD_GRAYSCALE)
    # El programa devuelve la pelicula ya filtrada por el ampliador (gaussiana de 0,8 px): se resta
    # la imagen con ese mismo filtro y la capa queda solo grano. Restando la imagen sin filtrar,
    # la capa llevaba tambien el desenfoque y ref-b salia mas blanda que los otros estilos: pelos
    # sueltos perdidos y pestanas borrosas (QA v7).
    return (out.astype(np.float32) - cv2.GaussianBlur(grey.astype(np.float32), (0, 0), 0.8)) / 255


def finish(srgb: np.ndarray, grain_r: float = 0.0, skin: np.ndarray | None = None) -> np.ndarray:
    """Enfoque de salida para pantalla y grano, al tamano final."""
    out = cv2.GaussianBlur(srgb, (0, 0), 0.8)
    np.subtract(srgb, out, out=out)
    out *= 0.35
    out += srgb
    if grain_r:
        layer = film_grain(out, grain_r)
        if skin is not None:
            layer *= 1 - (1 - GRAIN_SKIN) * skin
        out += layer[..., None]
    return np.clip(out, 0, 1)


def lstar_of(srgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(to_uint8(srgb), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255


def nnls(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Minimos cuadrados con x >= 0 para un sistema chico (saca la columna mas negativa y repite)."""
    active = list(range(A.shape[1]))
    while active:
        x, *_ = np.linalg.lstsq(A[:, active], b, rcond=None)
        if (x >= 0).all():
            out = np.zeros(A.shape[1])
            out[active] = x
            return out
        active.pop(int(np.argmin(x)))
    return np.zeros(A.shape[1])


# --- medir y resolver --------------------------------------------------------

def profile_of(srgb: np.ndarray, scene: Scene) -> dict:
    """Los mismos numeros que se miden en la referencia, sobre mi version, a SIZE px."""
    n = srgb.shape[0]
    rgb8 = to_uint8(cv2.resize(srgb, (SIZE, SIZE), interpolation=cv2.INTER_AREA) if n != SIZE else srgb)
    alpha = cv2.resize(scene.alpha, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    face = (cv2.resize(scene.face.astype(np.uint8), (SIZE, SIZE), interpolation=cv2.INTER_NEAREST) > 0) & (alpha > 0.9)
    geo = tuple(v * SIZE / n for v in scene.geo)
    cx, cy, r = geo
    yy, xx = np.ogrid[:SIZE, :SIZE]
    cheek = (((xx - cx) ** 2 + (yy - cy) ** 2) < (0.6 * r) ** 2) & (alpha > 0.9)
    back = (alpha < 0.05) & (yy < 0.72 * SIZE)
    st = measure(rgb8, cheek, back)
    lab = cv2.cvtColor(rgb8.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    L = lab[..., 0]
    core = cv2.erode(face.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    levels = np.percentile(L[core], [50, 75, 90])
    # la sombra se mide solo en la piel: en la elipse entraban los anteojos y el pelo, y el
    # relleno perseguia pixeles que no son piel (retrato con anteojos: 28 en la elipse, 47 en la piel)
    skin = (cv2.resize(scene.skin, (SIZE, SIZE), interpolation=cv2.INTER_AREA) > 0.5) & face
    shade = light_shape(L, skin if skin.sum() > 500 else face, face_ellipse(geo)[2] / 4)
    ex = face_ellipse(geo)
    inner = ellipse_mask((SIZE, SIZE), ex[0], ex[1], ex[2] * 0.8, ex[3] * 0.8) & (alpha > 0.9)
    return dict(p1=st.p1, p99=st.p99, face50=float(levels[0]), face75=float(levels[1]), face90=float(levels[2]),
                bg=st.bg, shade10=shade[0], shade50=shade[1], shade90=shade[2], lit=lit_skin(L, face, ex[2]), top=lit_skin(L, face, ex[2], 98),
                face_bands=band_energy(L, flat_face(L, upper_face((SIZE, SIZE), *ex) & (alpha > 0.9), ex[2] / FACE_RX), ex[2] / FACE_RX), grain_bands=band_energy(L, back)[:3],
                skin_a=float(lab[..., 1][inner].mean()), skin_b=float(lab[..., 2][inner].mean()),
                skin_bands=skin_bands(lab, inner),
                bg_a=float(lab[..., 1][back].mean()) if back.any() else 0.0,
                bg_b=float(lab[..., 2][back].mean()) if back.any() else 0.0,
                bg_plane=plane_fit(L, back) if back.sum() > 500 else None)


def input_points(scene: Scene, y: np.ndarray) -> dict:
    """Donde estan, antes de la curva, el negro de la persona y su piel iluminada."""
    L = lstar(y)
    person = scene.alpha > 0.5
    face = scene.face & (scene.alpha > 0.9)
    rx = face_ellipse(scene.geo)[2]
    return dict(p1=float(np.percentile(L[person], 1)), lit=lit_skin(L, face, rx), top=lit_skin(L, face, rx, 98))


def solve(scene: Scene, style: Style, want: dict, box: tuple[int, int, int], iters: int = 7) -> Params:
    """Mide, corrige y vuelve a medir: curva, sombra de la cara, contraste por escala y color.

    `scene` es el encuadre abierto (el mismo de la maestra, mas chico) y se mide solo el
    cuadrado `box` del encuadre medio, como en la referencia.
    """
    mid = crop_scene(scene, box)
    aim = {k: want[k] for k in ANCHOR_WEIGHTS}
    p = Params(np.array([0, 100], np.float32), np.array([0, 100], np.float32), skin_ev=scene.skin_ev)
    # punto fijo de la sombra: la piel iluminada; tope del relleno: FILL_EV sobre la piel mas oscura
    y0 = (scene.img @ MONO_MIX) if style.mono else luminance(scene.img)
    w = scene.skin
    sigma = scene.geo[2] / 5
    low = cv2.GaussianBlur(np.log2(np.maximum(y0, 1e-5)) * w, (0, 0), sigma) / (cv2.GaussianBlur(w, (0, 0), sigma) + 1e-4)
    depth = 1.0
    if (w > 0.5).any():
        p.shade_center = float(np.percentile(low[w > 0.5], 90))
        depth = max(p.shade_center - float(np.percentile(low[w > 0.5], 5)), 0.5)
    shape_min = max(1.0 - FILL_EV / depth, SHAPE_MIN)
    for _ in range(iters):
        _, y = shaped(scene, style, p)
        p.curve_in, p.curve_out = fit_curve(input_points(mid, cut(y, box)), aim, ANCHOR_WEIGHTS, "lit")
        got = profile_of(cut(render(scene, style, p, want), box), mid)
        for k in ANCHOR_WEIGHTS:
            aim[k] = float(np.clip(aim[k] + 0.8 * (want[k] - got[k]), 0, 98))
        if not style.keep_light and "shade10" in want:
            spread_want = want["lit"] - want["shade10"]
            spread_got = max(got["lit"] - got["shade10"], 1.0)
            p.shape = float(np.clip(p.shape * (spread_want / spread_got) ** 0.8, shape_min, SHAPE_MAX))
        if want.get("face_bands"):
            for k in MATCH_BANDS:
                ratio = want["face_bands"][k] / max(got["face_bands"][k], 1e-3)
                p.band_gains[k] = float(np.clip(p.band_gains[k] * ratio**0.8, *BAND_GAIN))
        if not style.mono and style.skin_hue is not None:
            solve_color(p, style, want, got)
    return p


def add_detail(scene: Scene, rgb: np.ndarray, amount: float) -> np.ndarray:
    """El detalle de 1 a 4 px de la persona realzado, como el enfoque de la camara.

    La camara enfoca su JPEG; mi revelado no. En la piel de un perfil, la textura de 1-2 px quedaba
    en 0,82 de la de la camara y la de 2-4 px en 0,87 (poros mas blandos). Una banda de
    diferencia de gaussianas sobre L*, con los dos desenfoques tomados solo sobre la persona
    (convolucion normalizada por el alpha): asi la banda nunca ve la pared y el contorno no
    gana un halo. Lo de menos de 1 px (el ruido) no se toca: ya estaba en 1,15.
    """
    k = scene.n / MASTER
    y = luminance(rgb)
    L = lstar(y)
    a = scene.alpha
    band = np.zeros_like(L)
    for sign, sigma in ((1.0, max(0.5, 1.0 * k)), (-1.0, max(1.0, 4.0 * k))):
        num = cv2.GaussianBlur(L * a, (0, 0), sigma)
        num /= np.maximum(cv2.GaussianBlur(a, (0, 0), sigma), 1e-4)
        band += sign * num
        del num
    band *= amount * a
    band += L
    del L
    gain = y_from(band) / np.maximum(y, 1e-6)
    del band, y
    return rgb * gain[..., None]


def solve_camera(name: str, scene: Scene, style: Style) -> Params:
    """El tono y el color de la persona sacados del JPEG de la camara, una sola pasada.

    Sin dodge, sin brillos bajados, sin relleno de sombra: la luz es la que hubo. La curva sale
    de los cuantiles del brillo (fit_tone) y la croma y el matiz por brillo, de la persona ya
    con esa curva (fit_chroma).
    """
    p = Params(np.array([0, 100], np.float32), np.array([0, 100], np.float32), skin_ev=0.0, shine=0.0)
    cam = camera_original(name, "abierto", scene.n)
    person, wall = fit_mask(scene.alpha, cam)
    f, y = shaped(scene, style, p)
    p.curve_in, p.curve_out = fit_tone(lstar(y), camera_lstar(cam), person, wall)
    lab = lab_of(clean_color(scene, apply_tone(f, y, p.curve_in, p.curve_out)))
    del f, y
    p.chroma_L, p.chroma_gain, p.chroma_turn = fit_chroma(lab, cv2.cvtColor(cam.astype(np.float32), cv2.COLOR_RGB2LAB), person)
    # el enfoque se mide a la resolucion de la maestra, no a SOLVE: 0,2 lleva la textura de
    # 1-4 px de un perfil a la de la camara (add_detail)
    p.detail = CAMERA_DETAIL
    return p


def fit_params(name: str, style: Style, want: dict) -> Params:
    """Los parametros del estilo para esta foto, resueltos sobre el encuadre abierto a SOLVE px."""
    scene = build_scene(name, "abierto", SOLVE)
    if style.camera_look:
        return solve_camera(name, scene, style)
    return solve(scene, style, want, preset_box(name, "medio", SOLVE))


def solve_color(p: Params, style: Style, want: dict, got: dict) -> None:
    got_c = float(np.hypot(got["skin_a"], got["skin_b"]))
    got_h = float(np.arctan2(got["skin_b"], got["skin_a"]))
    if "skin_a" in want:
        want_c, want_h = float(np.hypot(want["skin_a"], want["skin_b"])), float(np.arctan2(want["skin_b"], want["skin_a"]))
    else:
        want_c, want_h = want.get("skin_c", got_c / p.chroma), float(np.radians(style.skin_hue))
    hue_tot = p.hue + p.hue_bands
    chroma_tot = p.chroma * p.chroma_bands
    p.hue += 0.9 * float(np.angle(np.exp(1j * (want_h - got_h))))
    # cuidado con la saturacion: la croma nunca pasa de chroma_cap veces la natural
    p.chroma = float(np.clip(p.chroma * (want_c / max(got_c, 1e-3)) ** 0.9, 0.7, style.chroma_cap))
    # Por franja de brillo, cada una contra su propio objetivo, absoluto: con referencia se
    # copia su color en cada franja; sin referencia, el matiz buscado en todas y la croma
    # natural. El tope de croma vale tambien por franja.
    ref_bands = want.get("skin_bands")
    for i, (k, ga, gb) in enumerate(got["skin_bands"]):
        g_h, g_c = float(np.arctan2(gb, ga)), float(np.hypot(ga, gb))
        if k < MIN_BAND_PX or g_c < MIN_HUE_CHROMA:
            continue
        if ref_bands is not None:
            rk, ra, rb = ref_bands[i]
            if rk < MIN_BAND_PX:
                continue
            w_h, w_c = float(np.arctan2(rb, ra)), float(np.hypot(ra, rb))
            t = np.clip(chroma_tot[i] * (w_c / max(g_c, 1e-3)) ** 0.8, 0.7, style.chroma_cap)
            p.chroma_bands[i] = t / p.chroma
        else:
            # sin referencia: la croma buscada en cada franja (CHROMA_SHAPE), con el mismo tope
            w_h = float(np.radians(style.skin_hue))
            w_c = want.get("skin_c", g_c) * float(CHROMA_SHAPE[i])
            t = np.clip(chroma_tot[i] * (w_c / max(g_c, 1e-3)) ** 0.8, 0.7, style.chroma_cap)
            p.chroma_bands[i] = t / p.chroma
        h = hue_tot[i] + 0.8 * float(np.angle(np.exp(1j * (w_h - g_h))))
        p.hue_bands[i] = np.clip(h - p.hue, -np.radians(BAND_HUE_MAX), np.radians(BAND_HUE_MAX))
    fill_empty(p, got["skin_bands"], ref_bands)


def fill_empty(p: Params, got_bands: list, ref_bands: list | None) -> None:
    """Una franja sin pixeles (o sin color) toma el valor de la vecina: la interpolacion no salta."""
    ok = [k >= MIN_BAND_PX and np.hypot(a, b) >= MIN_HUE_CHROMA and (ref_bands is None or ref_bands[i][0] >= MIN_BAND_PX)
          for i, (k, a, b) in enumerate(got_bands)]
    if not any(ok):
        return
    idx = np.flatnonzero(ok)
    for arr in (p.hue_bands, p.chroma_bands):
        arr[:] = np.interp(np.arange(len(arr)), idx, arr[idx])


# --- salida -----------------------------------------------------------------

MASTER = 4170  # la imagen maestra a la resolucion nativa del RAW: el encuadre abierto entero
CAMERA_DETAIL = 0.2  # realce del detalle en el color de la camara (add_detail)
SOLVE = 1536  # el encuadre abierto a este tamano para resolver: el medio queda a ~920-1250 px


def preset_box(name: str, framing: str, n: int = MASTER) -> tuple[int, int, int]:
    """El cuadrado de un encuadre, en pixeles del encuadre abierto a `n` px."""
    ax, ay, aside = crop_box(name, "abierto")
    x0, y0, side = crop_box(name, framing)
    s = n / aside
    return round((x0 - ax) * s), round((y0 - ay) * s), round(side * s)


def cut(img: np.ndarray, box: tuple[int, int, int]) -> np.ndarray:
    x0, y0, side = box
    return img[y0 : y0 + side, x0 : x0 + side]


def run_one(name: str, style: Style, want: dict, n: int = MASTER) -> tuple[np.ndarray, dict, Params, float]:
    """Resuelve el estilo midiendo el encuadre medio y lo aplica al encuadre abierto a `n` px.

    Devuelve la imagen, el perfil medido en el medio, los parametros (como se adapto el
    estilo a esta foto) y la amplitud del grano.
    """
    p = fit_params(name, style, want)
    scene = build_scene(name, "abierto", n)
    base = render(scene, style, p, want)
    mid = preset_box(name, "medio", n)
    mid_scene = crop_scene(scene, mid)
    out = finish(base, style.grain_r * n / MASTER, scene.dodge)
    del base
    if style.camera_look:
        out = camera_lut(name, out)
    return out, profile_of(cut(out, mid), mid_scene), p, style.grain_r


def export_all(master: np.ndarray, name: str, key: str, lossless: bool = True) -> dict[str, np.ndarray]:
    """La maestra para el editor y los tres encuadres de siempre a 1024 px.

    El JPEG es lo que muestra el editor. Las exportaciones salen del TIFF de 16 bits que va al
    lado (editor_server.py): sin el, un PNG exportado era un recorte sin perdida de un JPEG.
    """
    save_jpeg(master, ROOT / "editadas" / name / f"{name}-{key}.jpg", quality=92)
    if lossless:
        save_tiff16(master, ROOT / "editadas" / name / f"{name}-{key}.tif")
    presets = {}
    for framing in FRAMINGS:
        sq = cut(master, preset_box(name, framing))
        sq = cv2.resize(sq, (1024, 1024), interpolation=cv2.INTER_AREA)
        save_jpeg(sq, ROOT / "editadas" / name / framing / f"{name}-{key}.jpg", 92)
        presets[framing] = sq
    return presets


def params_dict(p: Params, grain: float) -> dict:
    return dict(curve_in=[float(v) for v in p.curve_in], curve_out=[float(v) for v in p.curve_out],
                shape=p.shape, skin_ev=p.skin_ev, band_gains=[float(v) for v in p.band_gains],
                grain=float(grain), hue_deg=float(np.degrees(p.hue)), chroma=p.chroma,
                hue_bands_deg=[float(np.degrees(v)) for v in p.hue_bands], chroma_bands=[float(v) for v in p.chroma_bands],
                shine=p.shine, chroma_L=[float(v) for v in p.chroma_L], chroma_gain=[float(v) for v in p.chroma_gain],
                chroma_turn_deg=[float(np.degrees(v)) for v in p.chroma_turn], detail=p.detail)


def adaptation(p: Params, style: Style, grain: float = 0.0) -> str:
    """Lo que el estilo tuvo que hacerle a esta foto para parecerse a la referencia."""
    pts = " ".join(f"{i:.0f}>{o:.0f}" for i, o in zip(p.curve_in, p.curve_out))
    if style.camera_look:
        return f"curva de la camara {pts} | croma por L* " + " ".join(
            f"{c:.0f}:x{g:.2f}/{np.degrees(t):+.0f}" for c, g, t in zip(p.chroma_L, p.chroma_gain, p.chroma_turn)) + f" | detalle +{p.detail:.2f}"
    ev = (p.shape - 1) * 100
    row = f"curva {pts} | sombra {'relleno' if ev < 0 else 'hundida'} {abs(ev):.0f} % | escalas " + " ".join(f"x{g:.2f}" for g in p.band_gains)
    if grain:
        row += f" | grano r {grain:.3f} px"
    if not style.mono:
        cap = " (tope)" if p.chroma >= style.chroma_cap - 1e-3 else ""
        row += f" | matiz {np.degrees(p.hue):+.1f} grados | croma x{p.chroma:.2f}{cap}"
        row += " | por brillo " + " ".join(f"{np.degrees(p.hue + h):+.0f}/x{p.chroma * c:.2f}" for h, c in zip(p.hue_bands, p.chroma_bands))
    return row


def card_rows(name: str, want: dict, got: dict) -> list[str]:
    rows = [f"{name}"]
    if "lit" in want:
        rows.append(f"piel iluminada {want['lit']:3.0f} / {got['lit']:3.0f}   negro {want['p1']:3.0f} / {got['p1']:3.0f}")
    else:
        rows.append(f"piel iluminada {got['lit']:3.0f}   negro {got['p1']:3.0f} (los de la camara)")
    if "shade10" in want:
        rows.append(f"sombra de la cara {want['shade10']:3.0f} / {got['shade10']:3.0f}")
    if want.get("face_bands"):
        rows.append("escalas " + " ".join(f"{want['face_bands'][k]:.1f}/{got['face_bands'][k]:.1f}" for k in MATCH_BANDS))
    if want.get("grain_bands"):
        rows.append("grano " + " ".join(f"{w:.2f}/{g:.2f}" for w, g in zip(want["grain_bands"], got["grain_bands"])))
    if want.get("bg_plane") and got.get("bg_plane"):
        rows.append("fondo " + " ".join(f"{w:.0f}/{g:.0f}" for w, g in zip(want["bg_plane"], got["bg_plane"])))
    if abs(got.get("skin_a", 0)) + abs(got.get("skin_b", 0)) > 2:
        rows.append(f"piel a*,b* {got['skin_a']:3.0f},{got['skin_b']:3.0f}")
    return rows


AJUSTES = ROOT / "work" / "ajustes"  # lo medido y lo que se le hizo, una foto por archivo


def originals_print(name: str) -> str:
    """La huella de todo lo que entra al original de la camara y al raw exportados.

    Si cambia la base, el JPEG de la camara, el encuadre o la forma de exportar, cambia la huella
    y se vuelven a exportar aunque se haya pedido un solo estilo.
    """
    h = hashlib.sha256(str(MASTER).encode())
    files = [ROOT / "work" / f"{name}-base.tif", ROOT / "work" / f"{name}-camara.jpg", ROOT / "originales" / f"{name}.RAF"]
    files += [ROOT / "recipe" / f for f in ("photos.py", "geometry.py", "output.py", "common.py")]
    for path in files:
        h.update(path.read_bytes() if path.exists() else b"-")
    for fn in (export_all, preset_box, cut):
        h.update(inspect.getsource(fn).encode())
    return h.hexdigest()


def export_originals(name: str, always: bool) -> None:
    """El original de la camara y el raw. No dependen del estilo: con estilos elegidos se saltean si nada cambio."""
    stamp = ROOT / "work" / f"{name}-originales.sha256"
    done = all((ROOT / "editadas" / name / f).exists() for f in (f"{name}-original.jpg", f"{name}-raw.tif"))
    if not always and done and stamp.exists() and stamp.read_text() == originals_print(name):
        return
    export_all(camera_original(name, "abierto", MASTER), name, "original", lossless=False)  # ya es un JPEG de 8 bits
    export_all(raw_original(name, "abierto", MASTER), name, "raw")
    stamp.write_text(originals_print(name))  # despues: camera_original crea el JPEG de la camara si faltaba


def render_photo(name: str, chosen: list[Style], originals: bool = True) -> None:
    """Las maestras y los encuadres de una foto en cada estilo elegido, y sus numeros."""
    export_originals(name, always=originals)
    path = AJUSTES / f"{name}.json"
    records = {r["style"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    for style in chosen:
        want = targets_of(style)
        master, got, p, grain = run_one(name, style, want)
        export_all(master, name, style.key)
        del master
        print(f"{style.key:6s} " + " | ".join(card_rows(name, want, got)))
        print(f"{style.key:6s} {name} ajuste | " + adaptation(p, style, grain), flush=True)
        records[style.key] = dict(photo=name, style=style.key, want=want, got=got, params=params_dict(p, grain))
    # La escena no depende del estilo: se arma una vez por foto y la usan los cuatro (antes se
    # rehacia en cada estilo: tres de cada cuatro eran de mas). Probado el 2026-10-15: las cuatro maestras salen
    # identicas pixel a pixel.
    build_scene.cache_clear()
    AJUSTES.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([records[s.key] for s in STYLES if s.key in records], indent=1, default=float))


def exported(name: str, framing: str, key: str) -> np.ndarray:
    """Un encuadre a 1024 px ya exportado, achicado para las hojas (sRGB 0..1)."""
    img = cv2.imread(str(ROOT / "editadas" / name / framing / f"{name}-{key}.jpg"))
    return cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (420, 420), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def summarize(chosen: list[Style], every: bool) -> None:
    """Las comparaciones con cada referencia y las hojas de estilos, desde lo exportado."""
    records = [r for n in PHOTOS for r in json.loads((AJUSTES / f"{n}.json").read_text())]
    by = {(r["photo"], r["style"]): r for r in records}
    for k, style in enumerate(STYLES):
        if style not in chosen:
            continue
        items = [(n, exported(n, "medio", style.key), card_rows(n, by[(n, style.key)]["want"], by[(n, style.key)]["got"])) for n in PHOTOS]
        ref = reference_image(style.reference) if style.reference else None
        comparison_card(style.label, ref, items, PROCESS / f"{190 + k}-comparacion-{style.key}-v7.jpg")
    (ROOT / "work" / "ajustes.json").write_text(json.dumps(records, indent=1, default=float))
    if not every:
        return
    for j, framing in enumerate(FRAMINGS):
        rows = [("Original de la camara", [(n, exported(n, framing, "original")) for n in PHOTOS])]
        rows += [(s.label, [(n, exported(n, framing, s.key)) for n in PHOTOS]) for s in STYLES]
        sheet(rows, PROCESS / f"{195 + j}-estilos-{framing}-v7.jpg", d=200)


def workers() -> int:
    """Cuantas fotos a la vez, con la regla de la Mac: dos (cada proceso pesa ~2,5 GB) con la memoria
    normal, una con la presion en aviso y al menos 30 % libre, y ninguna si ya esta saturada."""
    level = subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"], capture_output=True, text=True).stdout.strip()
    out = subprocess.run(["memory_pressure"], capture_output=True, text=True).stdout
    free = int(out.rsplit("free percentage:", 1)[1].split("%")[0]) if "free percentage:" in out else 0
    load = os.getloadavg()[0]
    if load < 20 and level == "1":
        return 2
    if load < 20 and level == "2" and free >= 30:
        return 1
    sys.exit(f"La Mac ya esta saturada (presion {level}, {free} % libre, carga {load:.0f}): no lanzo las maestras.")


def main(args: list[str]) -> None:
    photos = [a for a in args if a in PHOTOS]
    keys = [a for a in args if a not in PHOTOS]
    chosen = [s for s in STYLES if not keys or s.key in keys]
    if photos:
        for name in photos:
            render_photo(name, chosen, originals=not keys)
        return
    n = workers()
    env = {"OMP_NUM_THREADS": str(GRAIN_THREADS // n), **os.environ}
    with ThreadPoolExecutor(n) as pool:
        jobs = [pool.submit(subprocess.run, [sys.executable, __file__, name, *keys], check=True, env=env) for name in PHOTOS]
        for job in jobs:
            job.result()
    summarize(chosen, every=not keys)


if __name__ == "__main__":
    main(sys.argv[1:])
