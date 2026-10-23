"""Tres estilos de prensa, cada uno un juego de parametros: los de la foto (adjust.py) y los del fondo (backdrop.py).

El pedido (2026-10-15): estilos de profesionales "para una foto en una nota", con referencias de las
empresas que mas se destacan por su gusto y su oficio (references.py; lo medido, en
proceso/estilos-medida-<ref>.png y proceso-notas/estilos/).

Como se llego aca:
1. Ajustes globales del editor, con tinte sobre la gente: el beige de Stripe puesto sobre toda la foto
   volvia marrones las remeras negras y bronceaba la piel (el fotografo: "no son naturales esos colores").
2. Solo el fondo, la gente bit a bit como en la maestra. Lo que hace a cada referencia es su fondo: el
   buzo azul de Collison sigue azul (b* -9) delante del papel beige.
3. El fotografo: que se juegue tambien con el contraste y la luz "como si la editara una persona", y que el fondo
   no se pinte sino que salga de mover parametros. Asi que cada estilo es lo que haria un retocador en
   Lightroom: ajustes de la foto entera (Light, sin tocar la temperatura ni el tinte de la gente, que es
   lo que fallo en la 1) y un ajuste local sobre el fondo, con la mascara del matting (Background).

Los estilos, con lo medido en cada referencia:
- Warm beige (Stripe): el mismo papel en beige, con su luz y su caida. Background: Saturation -100 (la
  pared a gris, sin el tibio que le deja el piso abajo) y Temperature +55 y Tint +16, que a la luz de estas
  paredes (68 a 79 L*) dan a* +2,3/+2,5 y b* +4,8/+5,4. Lo medido en la de Stripe: a* +2,4 y b* +5,1 en
  promedio, entre +1,4/+3,4 y +3,8/+6,3.
- Bright white (Ramp): papel casi blanco, 94 L* donde mas luz le da (la exposicion que lo lleva ahi, por
  foto), con la caida achicada al 35 % (Evenness 65). Neutro (Saturation -100): un papel blanco bajo la
  misma luz que la gente sale neutro; el tinte de la foto de Ramp (a* +1,8) es de su luz o su grado.
- Dark falloff (Apple Newsroom, el retrato de John Ternus): la pared de siempre, neutra, cayendo hacia la
  derecha, lejos de la luz principal (las cuatro la tienen a la izquierda), como en la de Apple: 78, 49 y 25 L*.

Una sola tabla, STYLES. La exposicion del fondo blanco se calcula por foto y se redondea al paso del
control antes de usarla: la maestra de cada estilo es exactamente lo que el editor muestra con su version.
`--seed` escribe las tres versiones de cada foto en editadas/versiones.json desde la misma tabla.

Salidas, sin tocar nada de lo que ya existe: editadas/<foto>-<estilo>.tif (16 bits) y .png (8 bits con el
mismo dither que la maestra), y editadas/pantalla/<foto>-<estilo>.png para el editor. Las capas del fondo
(alpha, pared de atras y luz de la pared) en editadas/fondo/, una vez por foto.

Uso: MallocLargeCache=0 nice -n 19 ../.venv/bin/python styles.py <foto> [estilo ...]   (una foto por proceso)
     ... styles.py <foto> --preview      el piloto: a 2560 px, en work/estilos/piloto/
     ... styles.py <foto> --layers       solo las capas del fondo
     ... styles.py --seed                  las versiones del editor, para las cuatro
     ... styles.py --seed-looks            las de LOOKS (solo parametros del panel, sin maestras)
"""

import json
import math
import os
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image

import backdrop
from adjust import KEYS as LIGHT_KEYS
from adjust import TO_LINEAR, from_x, to_x
from common import EDITED, NOTES, ROOT, _srgb_icc, lab, linear_to_srgb, save_png, to_uint8, to_uint16
from develop import frac_box
from masks import background_mask
from matte import cached, fresh, keep_polygons, matte_path, upsample_alpha
from photos import PHOTOS, STUDIO
from viewer import SCREEN, SCREENS, screen

# light: lo mismo para las cuatro (es gente distinta: igualarles la piel seria cambiarles el tono). Sin temperatura ni
# tinte, y vibrancia de 15 como mucho: el color de la gente es el de la maestra. Medido con tools/style_pilot.py
# (proceso-notas/estilos/luz-<ref>.txt)
STYLES = {
    "beige": {"name": "Warm beige", "ref": "stripe",  # luminoso y suave: sombras abiertas, poco contraste
              "light": {"exposure": 0.15, "contrast": -5, "highlights": -10, "shadows": 30, "whites": 5, "blacks": -12, "vibrance": 5},
              "background": {"saturation": -100, "temperature": 55, "tint": 16}},
    "white": {"name": "Bright white", "ref": "ramp",  # claro y nitido: negros firmes, luces contenidas contra el blanco
              "light": {"exposure": 0.15, "contrast": 5, "highlights": -20, "shadows": 20, "whites": 8, "blacks": -15, "vibrance": 10},
              "background": {"saturation": -100, "exposure": "top", "evenness": 65}},  # "top": lleva lo mas claro a WHITE_TOP
    "falloff": {"name": "Dark falloff", "ref": "apple",  # denso: mas contraste y color, negros profundos con detalle
                "light": {"contrast": 20, "highlights": -12, "shadows": 8, "blacks": -10, "vibrance": 15},
                "background": {"saturation": -100, "falloff": 100}},
}
# Mas versiones, pedidas el 2026-10-15 ("armame versiones solo tocando estos parametros de la sidebar derecha"):
# solo valores del panel, sin maestras propias (styles.py <foto> no las renderiza; --seed-looks las suma al editor).
# Una primera tanda inventada (Soft gray, Cool gray, Warm sand, Charcoal, Matte) recoloreaba o aplanaba la pared y
# el fotografo la rechazo ("no random, son horribles"): estas son recetas publicadas con numeros, tal cual, y el fondo en 0
# porque ningun profesional lo toca con los ajustes globales. Los numeros son los de Lightroom puestos en nuestros
# controles, que siguen su sentido y su rango pero no su fuerza exacta. Los presets de retrato de Adobe no tienen
# sus valores publicados en ningun lado. Lo medido: proceso-notas/estilos/versiones-piloto.json.
LOOKS = {
    # Simon Ringsmuth, Digital Photography School, "How to do basic processing on a portrait in 5 minutes":
    # "I always start with these" (Clarity -5 no esta en el panel; el balance, con el gotero: ya esta en la entrega)
    # https://digital-photography-school.com/how-to-do-basic-processing-on-a-portrait-in-5-minutes-using-lightroom/
    "natural": {"name": "Natural headshot",
                "light": {"highlights": -25, "shadows": 20, "whites": 20, "blacks": -25, "saturation": 5},
                "background": {}},
    # SLR Lounge, retrato de alto contraste (Clarity -20, la viñeta y la curva "Vintage Punch" no estan en el panel)
    # https://www.slrlounge.com/?p=140798
    "contrast": {"name": "High contrast",
                 "light": {"contrast": 25, "highlights": -30, "shadows": -15, "whites": -30, "blacks": -30},
                 "background": {}},
    # la misma receta en blanco y negro, que es como la publica SLR Lounge
    "contrast_bw": {"name": "High contrast B&W",
                    "light": {"contrast": 25, "highlights": -30, "shadows": -15, "whites": -30, "blacks": -30, "saturation": -100},
                    "background": {}},
    # Fotos de equipo en color de empresas con gusto (2026-10-17, pedido: "linear, apple, robinhood, public, nothing"),
    # medidas con tools/ref_measure.py (proceso/estilos-medida-<ref>.png). Primera vuelta: los percentiles de piel de la
    # referencia copiados con un juego para las cuatro, y el fotografo: "adaptar los estilos bien a las fotos, no es
    # poner el filtro y ya" (exposure +0,6, blacks +-40, highlights -40: lavado o empastado). Ahora:
    # - de la referencia sale la pared (Background, con el blanco hasta 97 para que el papel conserve su grano) y la
    #   direccion (base), dentro del rango de los tres estilos aprobados: contraste hasta 20, luces y sombras hasta 20 o
    #   30, vibrance hasta 15, saturation hasta 5, sin temperatura ni tinte en la gente;
    # - por foto (photos), lo que sale de tools/look_fit.py: la exposicion que lleva la luz de la piel (p90) a la de la
    #   referencia, con tope de 0,3 pasos, y los negros que dejan la ropa negra entre 5 y 10 L* sin aplastarla;
    # - las luces de la piel recuperadas (2026-10-17, "que siga buenas practicas"): con la piel subida, el brillo de la
    #   frente y los pomulos quemaba el rojo en 2-10 % de la cara. Highlights -20 y whites -8 (el borde del rango
    #   aprobado) lo llevan a 0 con 1,5 L* menos de piel; en la crema ademas saturation 0 y vibrance 10, porque el
    #   rojo de la piel seguia quemando (proceso-notas/estilos/face_clip_try.py).
    # - smoothing 100 en todas: el papel tiene franjas verticales que el contraste y el blanco hacen ver ("noto una
    #   linea", 2026-10-17); los tres estilos de prensa de STYLES no lo llevan, ya estaban aprobados.
    # Apple Srouji (laboratorio desenfocado) quedo afuera: no tiene pared que copiar, y pintar la nuestra de azul era
    # el filtro. Apple ya esta en Dark falloff.
    "robinhood": {"name": "White wall, light skin", "ref": "robinhood",  # blanco puro y parejo, piel clara, limpio
                  "base": {"contrast": 5, "highlights": -20, "shadows": 20, "whites": -8, "blacks": -10, "vibrance": 10},
                  "photos": {"PHOTO_A": {"exposure": 0.29, "blacks": -12}},  # tools/look_fit.py (una entrada por foto de la sesion)
                  "background": {"smoothing": 100, "saturation": -100, "evenness": 90, "exposure": "top:97"}},
    "public": {"name": "Cream wall", "ref": "public",  # blanco hueso calido parejo, negros hondos, piel con color
               "base": {"contrast": 10, "highlights": -20, "shadows": 10, "whites": -8, "blacks": -12, "vibrance": 10},
               "photos": {"PHOTO_A": {"exposure": 0.28, "blacks": -12}},  # tools/look_fit.py (una entrada por foto de la sesion)
               "background": {"smoothing": 100, "saturation": -100, "temperature": 75, "tint": 22, "evenness": 85, "exposure": "top:86"}},
    # Carl Pei con flash: de la referencia solo la direccion (punch, negros hondos, color). Su fondo es una oficina: la
    # pared queda como esta, gris.
    "nothing": {"name": "Deep blacks, grey wall", "ref": "nothing",
                "base": {"contrast": 15, "highlights": -20, "shadows": 10, "whites": -8, "blacks": -15, "vibrance": 12},
                "photos": {"PHOTO_A": {"exposure": 0.29, "blacks": -15}},  # tools/look_fit.py (una entrada por foto de la sesion)
                "background": {"smoothing": 100, "saturation": -100}},
    # Linear (/careers, el del sillon): pared blanca neutra pareja, suave pero no lavado
    "linear": {"name": "Soft contrast, white wall", "ref": "linear-sofa",
               "base": {"contrast": -5, "highlights": -15, "shadows": 20, "blacks": -8},
               "photos": {"PHOTO_A": {"exposure": 0.01, "blacks": -8}},  # tools/look_fit.py (una entrada por foto de la sesion)
               "background": {"smoothing": 100, "saturation": -100, "evenness": 70, "exposure": "top:84"}},
}
WHITE_TOP = 94.0  # L* de la parte mas clara del papel blanco: el de Ramp mide 93,9
PREVIEW = ROOT / "work" / "estilos" / "piloto"
VERSIONS = EDITED / "versiones.json"
EYES = EDITED / "ojeras" / "ojeras.json"

# los controles del editor (CONFIG en viewer_template.html): carpeta y nombre de cada parametro, y su paso
LIGHT_UI = {"exposure": ("Light", "Exposure"), "brightness": ("Light", "Brightness"), "contrast": ("Light", "Contrast"),
            "highlights": ("Light", "Highlights"), "shadows": ("Light", "Shadows"), "whites": ("Light", "Whites"),
            "blacks": ("Light", "Blacks"), "temperature": ("Color", "Temperature"), "tint": ("Color", "Tint"),
            "vibrance": ("Color", "Vibrance"), "saturation": ("Color", "Saturation")}
BACKGROUND_UI = {k: ("Background", k.capitalize()) for k in backdrop.KEYS}
STEP = {"exposure": 0.01}  # el resto, enteros


def master(name: str) -> np.ndarray:
    """La maestra de 16 bits."""
    return tifffile.imread(EDITED / f"{name}.tif")


def faces(name: str, scale: float) -> list[tuple[float, float, float, float]]:
    return [tuple(v * scale for v in f["oval"][:4]) for f in PHOTOS[name]["faces"]]


def alpha_for(name: str, native: np.ndarray, out: np.ndarray) -> np.ndarray:
    """Alpha (1 = persona) al tamano de `out`. El matting sale de la maestra nativa y se guarda."""
    boxes = PHOTOS[name].get("backdrop_sure", ())
    coarse, hand = background_mask(native, faces(name, 1.0), PHOTOS[name].get("backdrop_holes", ()), boxes, with_hand=True)
    small, tri = cached(name, native, coarse, faces(name, 1.0), hand, boxes)
    if boxes and hand.shape != out.shape[:2]:
        hand = cv2.resize(hand, (out.shape[1], out.shape[0]), interpolation=cv2.INTER_NEAREST)
    scale = out.shape[0] / native.shape[0]
    alpha = upsample_alpha(out, small, faces(name, scale), tri, hand if boxes else None)
    return keep_polygons(out, alpha, PHOTOS[name].get("backdrop_keep", ()), scale)


def keep_mark(name: str) -> Path:
    """Con que poligonos backdrop_keep se hicieron las capas guardadas: no entran al matting, asi que su firma no
    lo cubre, y sin esto cambiar un poligono dejaba las capas viejas."""
    return matte_path(name).with_name(f"{name}-keep.json")


def keep_wanted(name: str) -> list:
    return [[[int(round(v)) for v in pt] for pt in poly] for poly in PHOTOS[name].get("backdrop_keep", ())]


def keep_done(name: str) -> list:
    return json.loads(keep_mark(name).read_text()) if keep_mark(name).exists() else []


def layers_for(name: str, m16: np.ndarray, rebuild: bool = False) -> backdrop.Layers:
    """Las capas del fondo de una foto: las guardadas si estan al dia con la maestra y el matting; si no, se rehacen."""
    capa, luz = backdrop.layer_paths(name)
    deps = [EDITED / f"{name}.tif", matte_path(name)]
    newest = max((p.stat().st_mtime for p in deps if p.exists()), default=0)
    current = fresh(name, PHOTOS[name].get("backdrop_sure", ())) and keep_done(name) == keep_wanted(name)
    if not rebuild and current and capa.exists() and luz.exists() and min(capa.stat().st_mtime, luz.stat().st_mtime) >= newest:
        return backdrop.load_layers(name)
    native = TO_LINEAR[m16]
    alpha = alpha_for(name, native, native)
    layers = backdrop.make_layers(name, native, alpha)
    if keep_wanted(name):
        keep_mark(name).write_text(json.dumps(keep_wanted(name)))
    else:
        keep_mark(name).unlink(missing_ok=True)
    print(f"{name}: capas del fondo escritas", flush=True)
    return layers


def rounded(key: str, v: float) -> float:
    step = STEP.get(key, 1)
    return round(round(v / step) * step, 2) if step < 1 else float(round(v))


def preset(name: str, key: str, layers: backdrop.Layers) -> tuple[dict, dict]:
    """Los parametros de un estilo para una foto, redondeados al paso de cada control: (luz y color, fondo)."""
    s = (STYLES | LOOKS)[key]
    raw = s["light"] if "light" in s else s["base"] | s["photos"].get(name, {})  # LOOKS de empresas: base + lo de cada foto
    light = {k: rounded(k, float(raw.get(k, 0))) for k in LIGHT_KEYS}
    bg = {k: 0.0 for k in backdrop.KEYS}
    for k, v in s["background"].items():
        if isinstance(v, str) and v.startswith("top"):  # la exposicion que lleva lo mas claro de la pared, ya ajustada,
            target = float(v[4:]) if v.startswith("top:") else WHITE_TOP  # a ese L* (WHITE_TOP si no dice)
            v = math.log2(float(from_x(target / 100)) / float(from_x(backdrop.toned_top(layers, light) / 100)))
        bg[k] = rounded(k, v)
    return light, backdrop.parse(bg)


def wall_numbers(rgb: np.ndarray, name: str) -> list:
    """L*, a* y b* de cada parche de pared de photos.py."""
    out = []
    for box in PHOTOS[name]["wall"]:
        L, a, b = np.median(lab(rgb[frac_box(box, rgb.shape[:2])]).reshape(-1, 3), axis=0)
        out.append([round(float(L), 1), round(float(a), 2), round(float(b), 2)])
    return out


def render(name: str, keys: list[str], preview: bool) -> dict:
    m16 = master(name)
    layers = layers_for(name, m16)
    H, W = m16.shape[:2]
    if preview:
        k = SCREEN / max(H, W)
        size = (round(W * k), round(H * k))
        img16 = to_uint16(linear_to_srgb(cv2.resize(TO_LINEAR[m16], size, interpolation=cv2.INTER_AREA)))
        a16, b16 = backdrop.layers_at(layers, size)
        del m16
    else:
        img16, a16, b16 = m16, layers.alpha16, layers.behind16
    person = a16 == 65535
    report = {"photo": name, "size": list(img16.shape[:2]), "person": round(float(person.mean()), 4),
              "wall_before": wall_numbers(TO_LINEAR[img16], name), "styles": {}}
    if preview:
        PREVIEW.mkdir(parents=True, exist_ok=True)
        np.save(PREVIEW / f"{name}-alpha.npy", (a16 / 65535).astype(np.float16))
        save_png(srgb_float(img16), PREVIEW / f"{name}-maestra.png")
    for key in keys:
        light, bg = preset(name, key, layers)
        o16 = backdrop.render(img16, 0, 0, img16.shape[:2], layers, light, bg, a16, b16)
        report["styles"][key] = {"light": {k: v for k, v in light.items() if v}, "background": {k: v for k, v in bg.items() if v},
                                 "wall_after": wall_numbers(TO_LINEAR[o16], name)}
        if preview:
            save_png(srgb_float(o16), PREVIEW / f"{name}-{key}.png")
            continue
        tif = EDITED / f"{name}-{key}.tif"
        tifffile.imwrite(tif, o16, compression="zlib", photometric="rgb", iccprofile=_srgb_icc())
        # 8 bits con el dither de la maestra (mismo campo para la misma forma)
        o8 = to_uint8(srgb_float(o16))
        del o16
        Image.fromarray(o8).save(EDITED / f"{name}-{key}.png", icc_profile=_srgb_icc(), compress_level=6)
        del o8
        screen(tif, SCREENS / f"{name}-{key}.png")
        print(f"{name}-{key}: escrita", flush=True)
    print(json.dumps(report, ensure_ascii=False))
    return report


def srgb_float(img16: np.ndarray) -> np.ndarray:
    """uint16 sRGB -> sRGB en float (0..1), sin pasar por luz lineal."""
    return img16.astype(np.float32) / 65535


def ui_values(light: dict, bg: dict, level: int) -> dict:
    """Los valores de una version del editor, planos como los guarda DialKit ("Light.Exposure")."""
    out = {"Under-eyes.Intensity": level}
    for k, v in light.items():
        folder, control = LIGHT_UI[k]
        out[f"{folder}.{control}"] = v
    for k, v in bg.items():
        folder, control = BACKGROUND_UI[k]
        out[f"{folder}.{control}"] = v
    return out


# versiones que se sacaron de LOOKS: el seed tambien las borra del editor. Apple lab (2026-10-17): la referencia de
# Srouji no tiene pared comparable (es un laboratorio desenfocado) y Apple ya esta en Dark falloff.
RETIRED = {"preset-apple_lab"}


def seed(table: dict = STYLES, update_only: bool = False) -> None:
    """Las versiones de una tabla (STYLES o LOOKS) en cada foto de editadas/versiones.json. Una version del mismo
    nombre se reemplaza; las demas, y lo que este abierto, quedan como estaban. update_only: solo se reemplazan las
    que la foto ya tiene, asi una version que el fotografo borro en una foto no vuelve."""
    level = json.loads(EYES.read_text())["intensity"] if EYES.exists() else 100
    zero = ui_values({k: 0.0 for k in LIGHT_KEYS}, {k: 0.0 for k in backdrop.KEYS}, level)
    names = {s["name"] for s in table.values()}
    # primero lo lento (las capas de cada foto) y recien despues leer y escribir el archivo: el editor puede estar
    # guardando, y asi la ventana en la que se pisaria un cambio suyo es de milisegundos
    made = {}
    for name in STUDIO:
        layers = backdrop.load_layers(name)
        made[name] = [{"id": f"preset-{key}", "name": s["name"], "values": ui_values(*preset(name, key, layers), level)}
                      for key, s in table.items()]
    data = json.loads(VERSIONS.read_text()) if VERSIONS.exists() else {"photos": {}}
    for name in STUDIO:
        state = data["photos"].get(name) or {"version": 1, "values": dict(zero), "baseValues": dict(zero),
                                             "presets": [], "activePresetId": None}
        if update_only:
            new = {p["id"]: p for p in made[name]}
            state["presets"] = [new.get(p["id"], p) for p in state["presets"] if p["id"] not in RETIRED]
        else:
            keep = [p for p in state["presets"] if p["name"] not in names and p["id"] not in RETIRED]
            state["presets"] = keep + made[name] if table is LOOKS else made[name] + keep  # las de LOOKS, abajo de lo que ya habia
        if state["activePresetId"] not in {p["id"] for p in state["presets"]}:
            state["activePresetId"] = None
        data["photos"][name] = state
    fd, tmp = tempfile.mkstemp(dir=EDITED, prefix=".versiones-", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, VERSIONS)
    print(f"{VERSIONS}: {len(table)} versiones en cada foto")


if __name__ == "__main__":
    cv2.setNumThreads(4)  # la Mac la comparten varios agentes: un cuarto de la CPU queda libre
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--seed" in sys.argv or "--seed-looks" in sys.argv:
        seed(LOOKS if "--seed-looks" in sys.argv else STYLES, "--update" in sys.argv)
        sys.exit()
    photo, keys = args[0], args[1:] or list(STYLES)
    if "--layers" in sys.argv:
        layers_for(photo, master(photo), rebuild=True)
        sys.exit()
    rep = render(photo, keys, "--preview" in sys.argv)
    notes = NOTES / "estilos"
    notes.mkdir(parents=True, exist_ok=True)
    (notes / f"fondo-{photo}{'-piloto' if '--preview' in sys.argv else ''}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
