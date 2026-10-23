"""Laminas de antes y despues de un arreglo: camara | antes | despues | que cambio.

Una lamina por maestra que esta en las dos carpetas: "antes" es la del respaldo de antes del arreglo (--before, la
carpeta editadas/ adentro de respaldos/<version>-antes-<que>/), "despues" la de --after (editadas/ si no se da). Sin
fotos, todas las maestras de --after; <foto> sola, todos sus estilos; <foto>:<estilo>, esa. Una maestra que no esta en
el respaldo (un estilo que se renderiza por primera vez) no tiene antes: lleva una linea "nuevo", sin lamina, y se
mira entera en editadas/.
Lee los dos formatos de editadas/:
- el de los avatares: <foto>/<foto>-<estilo>.jpg, con el original de la camara en <after>/<foto>/<foto>-original.jpg;
- el del pipeline (grade.py, styles.py): <foto>.tif (estilo "maestra") y <foto>-<estilo>.tif sueltos, de cada foto
  con su <foto>-antes.png al lado. La camara es ese -antes.png: el RAW con el balance de la camara, sin JPEG (sirve en
  un proyecto .sin-jpg) y alineado al pixel con la maestra (develop.py), asi que no se registra.

Cada lamina es el lugar de la foto donde mas cambio el color, ampliado: un recuadro de 2 x R px de la maestra centrado
en el pico del dE por encima de MIN_DE desenfocado con una gaussiana de R/2 px (buscado a 1/4: con una suma por
ventana, un cambio mas chico que la ventana empata en muchos centros y quedaba en una esquina). Si nada pasa de MIN_DE, la maestra no lleva lamina y se dice. La camara se
registra sobre la maestra en cada recorte (su JPEG esta corrido ~3 px), para que los tres paneles muestren el mismo
pixel. "Que cambio" es la maestra de despues apagada, con rojo donde se movio el color (dE76 entre antes y despues;
rojo pleno desde dE 8, nada debajo de 1,5). Salida: proceso/antes-despues-<foto>-<estilo>.png.

Uso: .venv/bin/python tools/antes_despues.py --before DIR [--after DIR] [<photo>[:<style>] ...]
"""

import argparse
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

FONT = "/System/Library/Fonts/Helvetica.ttc"
GAP = 8
FULL_DE = 8.0  # dE con el que el rojo de "que cambio" llega al maximo
MIN_DE = 1.5  # por debajo, el ruido de volver a comprimir el JPEG: no se marca
CAMERA_SHIFT = (-3.2, 0.65)  # el corrimiento tipico del JPEG de la camara sobre la maestra, en px
MAX_SHIFT = 8.0
R, ZOOM = 110, 2  # medio lado del recorte en px de la maestra, y su ampliacion en la lamina
SEARCH = 4  # el lugar que mas cambio se busca a 1/4
BASE = "maestra"  # el estilo de <foto>.tif del pipeline, la maestra sin estilo (como pantalla/<foto>-maestra.png)
LABELS = {BASE: "Maestra", "color": "Color", "ref-a": "Ref A", "ref-b": "Ref B", "ref-c": "Ref C"}  # la clave de cada estilo (styles.py) y su etiqueta; si falta, la clave


def masters(folder: Path) -> dict[tuple[str, str], Path]:
    """(foto, estilo) -> archivo de cada maestra de la carpeta, en los dos formatos (ver arriba), sin la camara."""
    out = {}
    for path in folder.glob("*/*.jpg"):
        name = path.parent.name
        if path.stem.startswith(f"{name}-") and path.stem != f"{name}-original":
            out[(name, path.stem[len(name) + 1 :])] = path
    names = sorted((p.name[: -len("-antes.png")] for p in folder.glob("*-antes.png")), key=len, reverse=True)
    for path in folder.glob("*.tif"):
        for name in names:  # la mas larga primero: "A-2.tif" es de la foto A-2 si existe, no un estilo de A
            if path.stem == name or path.stem.startswith(f"{name}-"):
                out[(name, path.stem[len(name) + 1 :] or BASE)] = path
                break
    return out


def camera(after_dir: Path, name: str) -> tuple[Path, bool]:
    """El original de la camara de la foto y si hay que registrarlo: el JPEG de los avatares esta corrido ~3 px; el
    -antes.png del pipeline sale del mismo revelado que la maestra y ya esta alineado."""
    jpg = after_dir / name / f"{name}-original.jpg"
    return (jpg, True) if jpg.exists() else (after_dir / f"{name}-antes.png", False)


def read(path: Path) -> np.ndarray:
    """RGB de 8 bits. La maestra de 16 bits se lleva a 8 redondeando, como su PNG."""
    if path.suffix.lower() in (".tif", ".tiff"):
        img = tifffile.imread(path)[..., :3]
        return (img.astype(np.float32) / 257 + 0.5).astype(np.uint8) if img.dtype == np.uint16 else img
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(path)
    return img[..., ::-1]


def registered(cam: np.ndarray, ref: np.ndarray, x: int, y: int, r: int) -> np.ndarray:
    """El recorte de la camara llevado sobre el de la maestra: correlacion de fase sobre el
    detalle del gris en una ventana del doble del recorte, y el corrimiento subpixel aplicado."""
    w = 2 * r
    win = (slice(y - w, y + w), slice(x - w, x + w))

    def hp(im: np.ndarray) -> np.ndarray:
        g = cv2.cvtColor(np.ascontiguousarray(im[win]), cv2.COLOR_RGB2GRAY).astype(np.float32)
        return g - cv2.GaussianBlur(g, (0, 0), 6)

    (dx, dy), _ = cv2.phaseCorrelate(hp(ref), hp(cam), cv2.createHanningWindow((2 * w, 2 * w), cv2.CV_32F))
    if np.hypot(dx, dy) > MAX_SHIFT:  # la pared distinta puede enganar a la correlacion
        dx, dy = CAMERA_SHIFT
    m = np.float32([[1, 0, x - r + dx], [0, 1, y - r + dy]])
    return cv2.warpAffine(cam, m, (2 * r, 2 * r), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)


def changed(before: np.ndarray, after: np.ndarray) -> np.ndarray:
    """La maestra de despues apagada a gris, con rojo donde el color se movio."""
    lab = [cv2.cvtColor(im.astype(np.float32) / 255, cv2.COLOR_RGB2LAB) for im in (before, after)]
    de = np.sqrt(((lab[1] - lab[0]) ** 2).sum(-1))
    k = np.clip((de - MIN_DE) / (FULL_DE - MIN_DE), 0, 1)[..., None]
    gray = cv2.cvtColor(after, cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None] * 0.35 + 40
    red = np.array([235, 40, 40], np.float32)
    return (gray * (1 - k) + red * k).clip(0, 255).astype(np.uint8)


def most_changed(before: np.ndarray, after: np.ndarray, r: int, native: bool = True) -> tuple[int, int] | None:
    """Centro (x, y), en pixeles de la maestra, del pico del dE sobre MIN_DE desenfocado a r/2; None si nada cambio.
    El centro queda a 2r del borde: la registracion de la camara mira una ventana del doble del recorte. Con
    `native` (maestras sin perdida, TIFF o PNG), si cambio se decide a tamano nativo, sobre los pixeles que se
    movieron: achicar a 1/4 promedia un cambio de pocos pixeles (una pestana, un grano) por debajo de MIN_DE, y si a
    1/4 no queda nada el centro es el pixel de dE mas alto. Entre JPEG se decide a 1/4, donde el ruido de volver a
    comprimir se promedia."""
    h, w = after.shape[:2]
    m = 2 * r
    ys, xs = np.nonzero((before != after).any(axis=-1))
    if not ys.size:
        return None
    if native:
        moved = [cv2.cvtColor(im[ys, xs].reshape(-1, 1, 3).astype(np.float32) / 255, cv2.COLOR_RGB2LAB) for im in (before, after)]
        de_px = np.sqrt(((moved[1] - moved[0]) ** 2).sum(-1)).ravel()
        if de_px.max() <= MIN_DE:
            return None
    size = (w // SEARCH, h // SEARCH)
    lab = [cv2.cvtColor(cv2.resize(im, size, interpolation=cv2.INTER_AREA).astype(np.float32) / 255, cv2.COLOR_RGB2LAB) for im in (before, after)]
    de = np.sqrt(((lab[1] - lab[0]) ** 2).sum(-1))
    k = np.clip((de - MIN_DE) / (FULL_DE - MIN_DE), 0, 1)
    if k.any():
        score = cv2.GaussianBlur(k, (0, 0), max(1.0, r / 2 / SEARCH))
        sy, sx = np.unravel_index(int(np.argmax(score)), score.shape)
        x, y = sx * SEARCH + SEARCH // 2, sy * SEARCH + SEARCH // 2
    elif not native:
        return None
    else:
        i = int(np.argmax(de_px))
        x, y = xs[i], ys[i]
    return int(np.clip(x, m, w - m)), int(np.clip(y, m, h - m))


def make(name: str, key: str, before_path: Path, after_path: Path, after_dir: Path, r: int = R, zoom: int = ZOOM) -> Image.Image | None:
    after_full = read(after_path)
    before_full = read(before_path)
    spot = most_changed(before_full, after_full, r, native=after_path.suffix.lower() != ".jpg")
    if spot is None:
        return None
    x, y = spot
    crop = (slice(y - r, y + r), slice(x - r, x + r))
    cam_path, register = camera(after_dir, name)
    cam = registered(read(cam_path), after_full, x, y, r) if register else read(cam_path)[crop]
    before, after = before_full[crop], after_full[crop]
    del before_full, after_full
    rows = [(key, [cam, before, after, changed(before, after)])]
    title = f"{name} · {LABELS.get(key, key)} · donde más cambió ({x}, {y})"

    side = int(round(2 * r * zoom))
    head, label_h = 56, 34
    font = ImageFont.truetype(FONT, 22)
    title_font = ImageFont.truetype(FONT, 26)
    cols = ["Cámara", "Antes", "Después", "Qué cambió"]
    width = 4 * side + 3 * GAP
    height = head + len(rows) * (label_h + side) + (len(rows) - 1) * GAP
    canvas = Image.new("RGB", (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 14), title, fill=(240, 240, 240), font=title_font)
    top = head
    for key, panels in rows:
        for i, (col, im) in enumerate(zip(cols, panels)):
            left = i * (side + GAP)
            label = col if i == 0 or i == 3 else f"{col} · {LABELS.get(key, key)}"
            draw.text((left + 4, top + 6), label, fill=(210, 210, 210), font=font)
            canvas.paste(Image.fromarray(cv2.resize(im, (side, side), interpolation=cv2.INTER_CUBIC)), (left, top + label_h))
        top += label_h + side + GAP
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser(description="Laminas de antes y despues: camara | antes | despues | que cambio.")
    ap.add_argument("--before", type=Path, required=True, metavar="DIR", help="editadas/ del respaldo de antes del arreglo")
    ap.add_argument("--after", type=Path, default=ROOT / "editadas", metavar="DIR", help="por defecto editadas/")
    ap.add_argument("photos", nargs="*", metavar="<photo>[:<style>]")
    args = ap.parse_args()
    before, after = masters(args.before), masters(args.after)
    if not before:  # un respaldo sin maestras es una ruta equivocada: si no, todo saldria "nuevo"
        ap.error(f"{args.before}: no hay maestras en el respaldo")
    if not args.photos:
        todo = sorted(after)
    else:
        todo = []
        for item in args.photos:
            name, _, key = item.partition(":")
            found = sorted(m for m in after if m[0] == name and (not key or m[1] == key))
            if not found:
                ap.error(f"{item}: no hay maestras de {name}{':' + key if key else ''} en {args.after}")
            todo += [m for m in found if m not in todo]
    if not todo:
        ap.error("no hay maestras (<foto>/<foto>-<estilo>.jpg, o <foto>[-<estilo>].tif con <foto>-antes.png)")
    out_dir = ROOT / "proceso"  # sin carpetas: el fotografo la mira en la galeria del Finder
    out_dir.mkdir(exist_ok=True)
    for name, key in todo:
        if (name, key) not in before:
            print(f"{name} {key}: nuevo (no esta en el respaldo, no hay antes), sin lamina", flush=True)
            continue
        sheet = make(name, key, before[name, key], after[name, key], args.after)
        if sheet is None:
            print(f"{name} {key}: sin cambios (dE < {MIN_DE} en toda la maestra), sin lamina", flush=True)
            continue
        path = out_dir / f"antes-despues-{name}-{key}.png"
        sheet.save(path)
        print(path.name, flush=True)


if __name__ == "__main__":
    main()
