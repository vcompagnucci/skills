"""Suma una foto al editor desde el archivo que se subio (originales/<clave>.<ext>), con lo mismo que tienen las cuatro:
maestra de 16 bits, el "antes", las imagenes de pantalla y, si hay pared de estudio, las capas del fondo.

- RAW (todo lo que lee LibRaw): el revelado de develop.py (lineal, primarios sRGB) con el balance de blancos de la
  camara, porque no hay parches de pared medidos a mano. La exposicion se elige sola para que lo mas claro de la foto
  (el percentil 99,5 de la luminancia) quede donde quedo en las cuatro de la sesion (0,56 lineal: con eso la de grupo y un retrato
  salen a x1,89 y x1,73, contra el 1,80 elegido a mano). Despues, la misma curva, color y nitidez que grade.py. Sin
  igualar la caida del flash: eso se mide sobre la pared de cada foto.
- Imagen ya revelada (TIFF, PNG, HEIC, AVIF, WebP, PSD...): macOS la lee (ImageIO) y ColorSync la pasa a sRGB a 16
  bits; la maestra son esos pixeles tal cual (de 8 bits en sRGB, sus mismos 8 bits). No se le aplica nada: ya fue
  editada por quien la hizo.
- El "antes" es el RAW con el balance de la camara y sin curva, como en las cuatro; de una imagen, la imagen misma.
- Caras: las ubica el detector de macOS (Vision, recipe/faces_vision.swift). Solo ubica.
- Fondo: solo si la foto tiene pared de estudio (gris neutra, lisa, arriba y en la esquina donde masks.py la mide).
  Las capas salen del mismo matting que las cuatro (styles.layers_for), sin los recuadros puestos a mano. Si el alpha
  no da una persona razonable, se descartan y la foto queda sin la carpeta Background.
- Sin retoque de piel ni ojeras: dependen de un inventario a ojo (README > Volver a correr).

Imprime "STEP <paso>" al empezar cada uno: el servidor lo muestra en la pestana.
Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python recipe/import_photo.py <clave>   (lo corre el servidor)
"""

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import rawpy
import tifffile
from PIL import Image

import backdrop
import imports
import viewer
from common import EDITED, ROOT, WORK, _srgb_icc, linear_to_srgb, luminance, save_png, save_tiff16
from develop import demosaic, rgb_cam, wall_white_balance
from grade import EXPOSURE, finish
from masks import WALL_A, WALL_B
from photos import PHOTOS

TARGET = 0.56  # luminancia lineal del percentil 99,5 despues de la exposicion: donde quedaron las cuatro
TOP_PCT = 99.5
VISION = ROOT / "recipe" / "faces_vision.swift"
VISION_BIN = WORK / "bin" / "faces_vision"
TMP = WORK / "imports"


def step(name: str) -> None:
    print(f"STEP {name}", flush=True)


def update(key: str, **fields) -> None:
    with imports.editing() as data:
        data["photos"].setdefault(key, {}).update(fields)


# --- leer ------------------------------------------------------------------------------------------
# donde se busca pared para el balance: las dos esquinas de arriba (y0, y1, x0, x1 en fracciones, como `wall` en photos.py).
# La de la izquierda es la que masks.py usa para el nivel de la pared
WALL_BOXES = [(0.04, 0.16, 0.04, 0.22), (0.04, 0.16, 0.78, 0.96)]


def wall_boxes(base: np.ndarray) -> list:
    """Las esquinas que son pared lisa y casi gris en el revelado con el balance de la camara (que la tine apenas)."""
    small = cv2.resize(base, (640, round(base.shape[0] * 640 / base.shape[1])), interpolation=cv2.INTER_AREA)
    small = small * (0.5 / max(float(np.percentile(luminance(small), 99)), 1e-6))
    lab = cv2.cvtColor((linear_to_srgb(small) * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    L, a, b = lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128
    texture = np.abs(L - cv2.GaussianBlur(L, (0, 0), 6))
    found = []
    for box in WALL_BOXES:
        ys, xs = slice(int(box[0] * L.shape[0]), int(box[1] * L.shape[0])), slice(int(box[2] * L.shape[1]), int(box[3] * L.shape[1]))
        if np.median(texture[ys, xs]) < 1.5 and np.percentile(np.hypot(a[ys, xs], b[ys, xs]), 90) < 15 and np.median(L[ys, xs]) > 30:
            found.append(box)
    return found


def develop_raw(path: Path, key: str) -> tuple[np.ndarray, np.ndarray, str]:
    """RAW -> (base lineal para la maestra, antes lineal, de donde salio el balance). Con pared de estudio en las
    esquinas, el balance se mide en ella, como en las cuatro (develop.wall_white_balance); si no, el de la camara."""
    with rawpy.imread(str(path)) as raw:
        wb = np.array(raw.camera_whitebalance[:3], np.float64)
        if not (wb > 0).all():
            wb = np.array(raw.daylight_whitebalance[:3], np.float64)
        shot = list(wb / wb[1]) + [1.0]
        matrix_ok = np.abs(np.asarray(raw.rgb_xyz_matrix[:3])).sum() > 0
        if matrix_ok:
            base = demosaic(raw, shot) @ rgb_cam(raw).T
        else:  # sin matriz de la camara: que LibRaw lleve a sRGB lineal
            base = raw.postprocess(user_wb=shot, output_color=rawpy.ColorSpace.sRGB, gamma=(1, 1), no_auto_bright=True,
                                   output_bps=16, highlight_mode=rawpy.HighlightMode.Clip).astype(np.float32) / 65535
    before = base * (0.95 / max(float(np.percentile(base.max(axis=2), 99.995)), 1e-6))
    boxes = wall_boxes(base) if matrix_ok else []
    wb_from = "camera"
    if boxes:
        PHOTOS[key] = {"wall": boxes}
        with rawpy.imread(str(path)) as raw:
            base = demosaic(raw, wall_white_balance(raw, key)) @ rgb_cam(raw).T
        wb_from = "wall"
    return base.astype(np.float32), before.astype(np.float32), wb_from


ORIENT = {  # EXIF orientation -> como llevar los pixeles a derecho
    2: lambda a: a[:, ::-1], 3: lambda a: a[::-1, ::-1], 4: lambda a: a[::-1],
    5: lambda a: np.swapaxes(a, 0, 1), 6: lambda a: np.rot90(a, -1), 7: lambda a: np.rot90(a, 1)[::-1],
    8: lambda a: np.rot90(a, 1),
}


def orientation(path: Path) -> int:
    """La orientacion EXIF. PIL la lee de PNG, TIFF, WebP y AVIF (sips no la ve en un PNG); HEIC, sips."""
    try:
        with Image.open(path) as im:
            return int(im.getexif().get(0x0112, 1))
    except Exception:
        pass
    out = subprocess.run(["sips", "-g", "orientation", str(path)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.strip().startswith("orientation:"):
            v = line.split(":")[1].strip()
            return int(v) if v.isdigit() else 1
    return 1


DECODER = ROOT / "recipe" / "decode_image.swift"
DECODER_BIN = WORK / "bin" / "decode_image"


def built(source: Path, binary: Path) -> Path:
    """Los ayudantes de Swift se compilan la primera vez (y si cambia el codigo) en work/bin/."""
    if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
        binary.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["swiftc", "-O", str(source), "-o", str(binary)], check=True, capture_output=True)
    return binary


def source_bits(path: Path) -> int:
    out = subprocess.run(["sips", "-g", "bitsPerSample", str(path)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.strip().startswith("bitsPerSample:"):
            v = line.split(":")[1].strip()
            return int(v) if v.isdigit() else 16
    return 16


def decode_raster(path: Path, key: str) -> tuple[np.ndarray, int]:
    """Imagen -> (uint16 RGB en sRGB, bits utiles). ImageIO la lee y ColorSync la pasa a sRGB a 16 bits por canal
    (recipe/decode_image.swift): de sRGB sale identica, de Display P3 a menos de 25/65535 de la cuenta exacta. Si era
    de 8 bits y en sRGB, son sus mismos 8 bits (x257)."""
    TMP.mkdir(parents=True, exist_ok=True)
    tmp = TMP / f"{key}-leida.bin"
    r = subprocess.run([str(built(DECODER, DECODER_BIN)), str(path), str(tmp)], capture_output=True, text=True)
    if r.returncode or not tmp.exists():
        raise SystemExit(r.stderr.strip() or "macOS can't read this file")
    try:
        raw = tmp.read_bytes()
    finally:
        tmp.unlink(missing_ok=True)
    w, h = (int(v) for v in np.frombuffer(raw[:8], np.uint32))
    a16 = np.frombuffer(raw[8:], "<u2").reshape(h, w, 4)[..., :3]
    bits = 8 if source_bits(path) <= 8 and not (a16 % 257).any() else 16
    o = orientation(path)
    if o in ORIENT:
        a16 = ORIENT[o](a16)
    return np.ascontiguousarray(a16), bits


# --- caras y pared -----------------------------------------------------------------------------------
def faces_on(screen: Path, scale: float) -> list[dict]:
    """Las caras, como ovalos de photos.py (cx, cy, rx, ry nativos): el recuadro de Vision va de las cejas al menton,
    el ovalo de las cuatro sube a la frente. Factores promediados contra los ovalos a mano de la de grupo y un retrato."""
    out = subprocess.run([str(built(VISION, VISION_BIN)), str(screen)], capture_output=True, text=True, check=True).stdout
    faces = []
    for i, f in enumerate(json.loads(out or "[]")):
        x, y, w, h = (f[k] * scale for k in ("x", "y", "w", "h"))
        faces.append({"id": f"cara-{i + 1}", "oval": [round(x + w / 2), round(y + h * 0.42), round(w * 0.45), round(h * 0.57)]})
    return faces


def studio_wall(screen: Path) -> bool:
    """Pared de estudio: gris neutra y lisa en la esquina de arriba a la izquierda (donde masks.py mide el nivel de la
    pared) y en la mayor parte de la franja de arriba. El matting supone eso: sin pared asi, no hay carpeta Background."""
    with Image.open(screen) as im:
        rgb = np.asarray(im.convert("RGB"))
    h, w = rgb.shape[:2]
    small = cv2.resize(rgb, (640, round(h * 640 / w)), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, a, b = lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128
    wall = (a > WALL_A[0]) & (a < WALL_A[1]) & (b > WALL_B[0]) & (b < WALL_B[1]) & (L > 30) & (L < 97)
    texture = np.abs(L - cv2.GaussianBlur(L, (0, 0), 6))
    sh, sw = L.shape
    corner = (slice(int(0.04 * sh), int(0.16 * sh)), slice(int(0.04 * sw), int(0.22 * sw)))
    top = (slice(int(0.02 * sh), int(0.12 * sh)), slice(None))
    return bool(wall[corner].mean() > 0.9 and np.median(texture[corner]) < 1.5 and wall[top].mean() > 0.6)


def drop_layers(key: str) -> None:
    for f in [*backdrop.layer_paths(key), backdrop.LAYERS / f"{key}-capa-editor.png", backdrop.LAYERS / f"{key}-luz-editor.png",
              viewer.SCREENS / f"{key}-capa.png"]:
        f.unlink(missing_ok=True)


# --- todo ----------------------------------------------------------------------------------------------
def main(key: str) -> None:
    entry = imports.read()["photos"][key]
    src = imports.ORIGINALS / entry["file"]
    step("develop")
    if entry["kind"] == "raw":
        base, before, wb_from = develop_raw(src, key)
        k = TARGET / max(float(np.percentile(luminance(base[::4, ::4]), TOP_PCT)), 1e-6)
        k = float(np.clip(k, 0.25, 16))
        base *= k / EXPOSURE  # finish() multiplica por EXPOSURE
        srgb = finish(base, np.ones(base.shape[:2], np.float32))
        del base
        step("master")
        save_tiff16(srgb, EDITED / f"{key}.tif")
        save_png(srgb, EDITED / f"{key}.png")
        del srgb
        save_png(linear_to_srgb(before), EDITED / f"{key}-antes.png")
        del before
        update(key, exposure=round(k, 3), white_balance=wb_from)
    else:
        m16, bits = decode_raster(src, key)
        step("master")
        tifffile.imwrite(EDITED / f"{key}.tif", m16, compression="zlib", photometric="rgb", iccprofile=_srgb_icc())
        # de 8 bits, el PNG del editor son los mismos 8 bits (sin dither: no hay nada que redondear)
        if bits == 8:
            px = Image.fromarray((m16 // 257).astype(np.uint8))
            px.save(EDITED / f"{key}.png", icc_profile=_srgb_icc(), compress_level=6)
            px.save(EDITED / f"{key}-antes.png", icc_profile=_srgb_icc(), compress_level=6)
        else:
            srgb = m16.astype(np.float32) / 65535
            save_png(srgb, EDITED / f"{key}.png")
            save_png(srgb, EDITED / f"{key}-antes.png")
            del srgb
        del m16
        update(key, bits=bits)

    step("screens")
    viewer.SCREENS.mkdir(parents=True, exist_ok=True)
    for name in (f"{key}.tif", f"{key}-antes.png"):
        viewer.screen(EDITED / name, viewer.SCREENS / (name.replace(".tif", ".png")))
    with Image.open(EDITED / f"{key}.png") as im:
        w, h = im.size
    screen = viewer.SCREENS / f"{key}.png"
    with Image.open(screen) as im:
        scale = w / im.size[0]

    step("faces")
    faces = faces_on(screen, scale)
    wall = studio_wall(screen)
    update(key, w=w, h=h, faces=faces, wall=wall)

    if wall:
        step("background")
        import styles  # el matting: pesado, solo si hace falta

        PHOTOS[key] = imports.read()["photos"][key]
        m16 = tifffile.imread(EDITED / f"{key}.tif")
        layers = styles.layers_for(key, m16, rebuild=True)
        person = float((layers.alpha16 > 32768).mean())
        del m16, layers
        if 0.03 < person < 0.9:
            viewer.editor_layers(key)
        else:
            print(f"{key}: el fondo no separo bien a la gente ({person:.0%} de persona): sin Background", flush=True)
            drop_layers(key)
            wall = False
            update(key, wall=False, background_dropped=round(person, 3))
    step("done")
    update(key, ready=True)


if __name__ == "__main__":
    main(sys.argv[1])
