"""Laminas de antes y despues de un arreglo: camara | antes | despues | que cambio.

Cada lamina es un lugar de la foto ampliado, una fila por estilo. "Antes" son las maestras
guardadas antes del arreglo (respaldos/v7-antes-arreglos/editadas), "despues" las de editadas/.
La camara se registra sobre la maestra en cada recorte (su JPEG esta corrido ~3 px), para que
los tres paneles muestren el mismo pixel. "Que cambio" es la maestra de despues apagada, con
rojo donde se movio el color (dE76 entre antes y despues; rojo pleno desde dE 8, nada debajo de 1,5).

Uso: .venv/bin/python tools/antes_despues.py [carpeta-de-antes] [prefijo-en-proceso]
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recipe"))
from crops import zones  # noqa: E402

FONT = "/System/Library/Fonts/Helvetica.ttc"
GAP = 8
FULL_DE = 8.0  # dE con el que el rojo de "que cambio" llega al maximo
MIN_DE = 1.5  # por debajo, el ruido de volver a comprimir el JPEG: no se marca
CAMERA_SHIFT = (-3.2, 0.65)  # el corrimiento tipico del JPEG de la camara sobre la maestra, en px
MAX_SHIFT = 8.0
LABELS = {"color": "Color", "ref-a": "Ref A", "ref-b": "Ref B", "ref-c": "Ref C"}  # la clave de cada estilo (styles.py) y su etiqueta


def sheets() -> list[dict]:
    """Las laminas, una por lugar a mirar: foto, centro (x, y) en pixeles de la maestra, radio, zoom, estilos y
    titulo. Se escriben a mano despues de cada arreglo, con lo que el QA marco. Abajo, dos de ejemplo: un lugar fijo
    y uno relativo a la cara (las zonas de crops.py)."""
    cara = zones("PHOTO_A")["cara"]
    return [
        {"file": "1-ceja", "photo": "PHOTO_A", "at": (1490, 840), "r": 70, "zoom": 3, "styles": ["ref-a", "color"],
         "title": "PHOTO_A · Ceja: la muesca blanca en la punta del mechón"},
        {"file": "2-rojos-labios", "photo": "PHOTO_A", "at": (cara[0] + 230, cara[1] + 200), "r": 110, "zoom": 2, "styles": ["color"],
         "title": "PHOTO_A · Rojos: la línea de los labios — diferencia con la cámara antes y después, en dE"},
    ]


def read(path: Path) -> np.ndarray:
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


def make(sheet: dict, before_dir: Path, after_dir: Path) -> Image.Image:
    name, (x, y), r, zoom = sheet["photo"], sheet["at"], sheet["r"], sheet["zoom"]
    crop = (slice(y - r, y + r), slice(x - r, x + r))
    cam_full = read(after_dir / name / f"{name}-original.jpg")
    rows = []
    for key in sheet["styles"]:
        after_full = read(after_dir / name / f"{name}-{key}.jpg")
        before = read(before_dir / name / f"{name}-{key}.jpg")[crop]
        cam = registered(cam_full, after_full, x, y, r)
        after = after_full[crop]
        del after_full
        rows.append((key, [cam, before, after, changed(before, after)]))
    del cam_full

    side = int(round(2 * r * zoom))
    head, label_h = 56, 34
    font = ImageFont.truetype(FONT, 22)
    title_font = ImageFont.truetype(FONT, 26)
    cols = ["Cámara", "Antes", "Después", "Qué cambió"]
    width = 4 * side + 3 * GAP
    height = head + len(rows) * (label_h + side) + (len(rows) - 1) * GAP
    canvas = Image.new("RGB", (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 14), sheet["title"], fill=(240, 240, 240), font=title_font)
    top = head
    for key, panels in rows:
        for i, (col, im) in enumerate(zip(cols, panels)):
            left = i * (side + GAP)
            label = col if i == 0 or i == 3 else f"{col} · {LABELS[key]}"
            draw.text((left + 4, top + 6), label, fill=(210, 210, 210), font=font)
            canvas.paste(Image.fromarray(cv2.resize(im, (side, side), interpolation=cv2.INTER_CUBIC)), (left, top + label_h))
        top += label_h + side + GAP
    return canvas


def main() -> None:
    before_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "respaldos" / "v7-antes-arreglos" / "editadas"
    prefix = sys.argv[2] if len(sys.argv) > 2 else "v7-revision"  # proceso/ no tiene carpetas: el grupo va de prefijo
    for sheet in sheets():
        path = ROOT / "proceso" / f"{prefix}-antes-despues-{sheet['file']}.png"
        make(sheet, before_dir, ROOT / "editadas").save(path)
        print(path.name, flush=True)


if __name__ == "__main__":
    main()
