"""Genera editor.html: las cuatro fotos con el RAW, el antes y despues, las ojeras y el fondo.

Uso: .venv/bin/python recipe/viewer.py

Antes escribe en editadas/pantalla/ las imagenes que muestra el editor, a 2560 px de lado largo: la
editada sale de la maestra de 16 bits y el antes del PNG del RAW, achicadas en luz lineal; la capa del
fondo (<foto>-capa.png), de la de editadas/fondo/, como la achica backdrop.layers_at, en RGBA de 8 bits.

Las capas del fondo enteras y la luz de la pared, el editor las lee en copias de 8 bits redondeadas
(editadas/fondo/<foto>-capa-editor.png y -luz-editor.png): Chrome lee un PNG de 16 bits cortando los 8 bits
de abajo (v >> 8), y en la pared clara eso corria la luz y oscurecia el fondo medio nivel contra el
export (medido el 2026-10-15: proceso-notas/editor/decode16.mjs).
"""

import json

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageOps

import backdrop
import imports
from adjust import TO_LINEAR
from common import EDITED, ROOT, linear_to_srgb, save_png
from photos import PHOTOS, STUDIO

THUMB = 96  # la pestana la muestra a 28 px: alcanza para una pantalla 3x
SCREEN = 2560  # lado largo de las imagenes del editor
EYES = EDITED / "ojeras"  # las puntas del control de ojeras (grade.py)
SCREENS = EDITED / "pantalla"
TO_LINEAR_8 = TO_LINEAR[np.arange(256) * 257]  # el RAW es de 8 bits: los mismos valores que exporta el servidor


def eye_manifest() -> dict:
    """Donde va cada parche de ojeras, a que intensidad salio la final y hasta donde llega el control."""
    path = EYES / "ojeras.json"
    return {"max": 100} | json.loads(path.read_text()) if path.exists() else {"intensity": 100, "max": 100, "photos": {}}


def screen(src, out) -> None:
    """Una imagen del editor: a luz lineal por tabla, achicada promediando ahi y de vuelta a sRGB de 8 bits."""
    if src.suffix == ".tif":
        lin = TO_LINEAR[tifffile.imread(src)]
    else:
        with Image.open(src) as im:
            lin = TO_LINEAR_8[np.asarray(im.convert("RGB"))]
    h, w = lin.shape[:2]
    long = max(h, w)
    size = (round(w * SCREEN / long), round(h * SCREEN / long))
    small = cv2.resize(lin, size, interpolation=cv2.INTER_AREA)
    del lin
    tmp = out.with_name(f".{out.name}")  # a medias no queda con fecha nueva: la proxima pasada la rehace
    save_png(linear_to_srgb(small), tmp)
    tmp.replace(out)


def to8(v16: np.ndarray) -> np.ndarray:
    return ((v16.astype(np.uint32) + 128) // 257).astype(np.uint8)


def write_png8(img: np.ndarray, out) -> None:
    """RGB o RGBA de 8 bits; a medias no queda con fecha nueva."""
    tmp = out.with_name(f".{out.name}")
    order = [2, 1, 0, 3][: img.shape[2]]
    if not cv2.imwrite(str(tmp), np.ascontiguousarray(img[..., order]), [cv2.IMWRITE_PNG_COMPRESSION, 4]):
        raise OSError(f"no se pudo escribir {tmp}")
    tmp.replace(out)


def layer8(a16: np.ndarray, b16: np.ndarray) -> np.ndarray:
    """La capa a 8 bits: un pixel que toca la gente sigue fuera de la pared pura (A >= 1)."""
    a8 = np.where(a16 > 0, np.maximum(to8(a16), 1), 0).astype(np.uint8)
    return np.dstack([to8(b16), a8])


def editor_layers(n: str) -> None:
    """Lo que el editor lee del fondo de una foto, a 8 bits: la capa a la escala de pantalla (promediada como en el
    piloto, backdrop.layers_at) y entera, y la luz de la pared. Lo que esta al dia no se rehace."""
    capa, luz = backdrop.layer_paths(n)
    outs = {"pantalla": SCREENS / f"{n}-capa.png", "entera": backdrop.LAYERS / f"{n}-capa-editor.png",
            "luz": backdrop.LAYERS / f"{n}-luz-editor.png"}
    stale = [k for k, out in outs.items() if not out.exists() or out.stat().st_mtime < (luz if k == "luz" else capa).stat().st_mtime]
    if not stale:
        print(f"{n}: fondo del editor al dia")
        return
    layers = backdrop.load_layers(n)
    h, w = layers.alpha16.shape
    long = max(h, w)
    if "pantalla" in stale:
        write_png8(layer8(*backdrop.layers_at(layers, (round(w * SCREEN / long), round(h * SCREEN / long)))), outs["pantalla"])
    if "entera" in stale:
        write_png8(layer8(layers.alpha16, layers.behind16), outs["entera"])
    if "luz" in stale:
        write_png8(to8(backdrop.read_png16(luz)), outs["luz"])
    print(f"{n}: fondo del editor escrito ({', '.join(stale)})", flush=True)


def screens() -> None:
    """Las imagenes de editadas/pantalla/, de a una foto; las que estan al dia no se rehacen."""
    cv2.setNumThreads(2)
    for n in visible():
        for src, out in ((EDITED / f"{n}.tif", SCREENS / f"{n}.png"), (EDITED / f"{n}-antes.png", SCREENS / f"{n}-antes.png")):
            if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
                print(f"{out.name}: al dia")
                continue
            screen(src, out)
            print(f"{out.name}: escrita", flush=True)
        if all(f.exists() for f in backdrop.layer_paths(n)):
            editor_layers(n)
        else:
            print(f"{n}: sin capas del fondo (recipe/styles.py {n} --layers)")


def bases(eyes: dict) -> None:
    """La base de cada parche de ojeras: el recorte de la editada de 8 bits, pixel a pixel (grade.py hace los parches
    con el mismo dither). El editor suma cada parche como diferencia contra su base, leidos con el mismo filtro: donde
    el parche no corrige la diferencia es 0 exacto, y a ningun zoom queda el borde del recorte."""
    manifest = (EYES / "ojeras.json").stat().st_mtime
    for n in visible():
        src = EDITED / f"{n}.png"
        newest = max(src.stat().st_mtime, manifest)
        todo = [e for e in eyes["photos"].get(n, []) if not (base(n, e).exists() and base(n, e).stat().st_mtime >= newest)]
        if not todo:
            continue
        with Image.open(src) as im:
            for e in todo:
                im.crop((e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"])).save(base(n, e), icc_profile=im.info.get("icc_profile"))
                print(f"{base(n, e).name}: escrita", flush=True)


def base(n: str, e: dict):
    return EYES / f"{n}-{e['face']}-base.png"


def photo(n: str, eyes: dict) -> dict:
    """Medidas, ojeras, fondo y miniatura de una foto. La miniatura es el cuadrado del centro de la editada:
    asi la pestana no le hace decodificar 26 MP al navegador para un icono de 28 px. Al dia, no se rehace.
    top: el L* de la parte mas clara de la luz de la pared (backdrop.top_lightness), el que Evenness deja quieto;
    None si la foto no tiene capas del fondo (el editor no le aplica la carpeta Background)."""
    src, thumb = EDITED / f"{n}.png", EDITED / "miniaturas" / f"{n}.png"
    with Image.open(src) as im:
        w, h = im.size
        if not thumb.exists() or thumb.stat().st_mtime < src.stat().st_mtime:
            ImageOps.fit(im, (THUMB, THUMB), Image.LANCZOS).save(thumb, icc_profile=im.info.get("icc_profile"))
    capa, luz = backdrop.layer_paths(n)
    made = [SCREENS / f"{n}-capa.png", backdrop.LAYERS / f"{n}-capa-editor.png", backdrop.LAYERS / f"{n}-luz-editor.png"]
    top = backdrop.top_lightness(TO_LINEAR[backdrop.read_png16(luz)]) if all(f.exists() for f in [capa, luz, *made]) else None
    return {"key": n, "label": PHOTOS[n].get("label") or imports.label(n), "w": w, "h": h, "eyes": eyes["photos"].get(n, []),
            "top": None if top is None else round(float(top), 4)}


def visible() -> list[str]:
    """Las fotos del editor: las cuatro y las importadas ya terminadas (recipe/import_photo.py)."""
    return [n for n in PHOTOS if n in STUDIO or (PHOTOS[n].get("ready") and (EDITED / f"{n}.tif").exists())]


def page_html(names: list[str]) -> str:
    """editor.html con los datos de esas fotos. El servidor la arma en cada pedido: una foto importada aparece sin
    volver a correr este script."""
    eyes = eye_manifest()
    data = {
        # cambia con cada pasada: sin esto el navegador puede seguir mostrando las editadas viejas
        "version": int(max(f.stat().st_mtime for f in [*EDITED.glob("*.png"), *EYES.glob("*.png"), *SCREENS.glob("*.png"),
                                                        *backdrop.LAYERS.glob("*.png")])),
        "screen": SCREEN,
        "eyes": {"default": eyes["intensity"], "max": eyes["max"]},
        "photos": [photo(n, eyes) for n in names],
    }
    return (ROOT / "recipe" / "viewer_template.html").read_text().replace("/*DATA*/", json.dumps(data, ensure_ascii=False))


def main() -> None:
    screens()
    (EDITED / "miniaturas").mkdir(exist_ok=True)
    eyes = eye_manifest()
    if eyes["photos"]:
        bases(eyes)
    (ROOT / "editor.html").write_text(page_html(visible()))
    print("editor.html listo")


if __name__ == "__main__":
    main()
