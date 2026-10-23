"""Salida: exportar, el original de camara, y las hojas para mirar y comparar."""

import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import ROOT, linear_to_srgb, load_base, to_uint8
from geometry import crop_box

PROCESS = ROOT / "proceso"  # solo imagenes
NOTES = ROOT / "proceso-notas"  # lo demas del proceso: numeros, notas y datos
BACKUPS = ROOT / "respaldos"  # maestras de versiones anteriores, base de la regresion (no se miran)


def process_file(group: str, name: str) -> Path:
    """proceso/ no tiene carpetas (el fotografo la mira en la galeria del Finder, que no las abre): el grupo va de prefijo."""
    return PROCESS / f"{group}-{name}"


def reference_path(ref: str) -> Path:
    return process_file("referencias", f"ref-{ref}.png")


def raw_original(name: str, framing: str, size: int) -> np.ndarray:
    """El RAW como sale de develop.py, sin retoque ni estilo: el punto de partida de todas las ediciones.

    Para el boton "Original de la camara" del editor. Las pruebas siguen comparando contra el
    JPEG de la camara (camera_original), que es la vara del color y de los contornos.
    """
    x0, y0, side = crop_box(name, framing)
    crop = load_base(name)[y0 : y0 + side, x0 : x0 + side]
    if side != size:
        crop = cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA)
    return linear_to_srgb(crop)


def camera_original(name: str, framing: str, size: int = 2048) -> np.ndarray:
    """El JPEG que hizo la camara (simulacion Velvia), con el mismo encuadre."""
    path = ROOT / "work" / f"{name}-camara.jpg"
    if not path.exists():
        raw = subprocess.run(
            ["exiftool", "-b", "-PreviewImage", str(ROOT / "originales" / f"{name}.RAF")], capture_output=True, check=True
        ).stdout
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)  # ya aplica la rotacion EXIF
        cv2.imwrite(str(path), img, [cv2.IMWRITE_JPEG_QUALITY, 97])
    cam = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    s = max(cam.shape[:2]) / 6240  # la vista previa cubre los 6240 px del lado largo del sensor (ECC: 0,7079)
    x0, y0, side = crop_box(name, framing)
    crop = cam[int(y0 * s) : int((y0 + side) * s), int(x0 * s) : int((x0 + side) * s)]
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_CUBIC if crop.shape[0] < size else cv2.INTER_AREA)


def circle(img: np.ndarray, d: int) -> Image.Image:
    tile = Image.fromarray(to_uint8(cv2.resize(img, (d, d), interpolation=cv2.INTER_AREA)))
    mask = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    out = Image.new("RGB", (d, d), (0, 0, 0))
    out.paste(tile, (0, 0), mask.resize((d, d), Image.LANCZOS))
    return out


def sheet(rows: list[tuple[str, list[tuple[str, np.ndarray]]]], path: Path, d: int = 320) -> None:
    gap, label = 18, 34
    cols = max(len(items) for _, items in rows)
    title = 40
    w = cols * (d + gap) + gap
    h = len(rows) * (d + label + title + gap) + gap
    canvas = Image.new("RGB", (w, h), (12, 12, 12))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    y = gap
    for heading, items in rows:
        draw.text((gap, y), heading, fill=(235, 235, 235), font=big)
        y += title
        for i, (lab, img) in enumerate(items):
            x = gap + i * (d + gap)
            canvas.paste(circle(img, d), (x, y))
            draw.text((x, y + d + 6), lab, fill=(170, 170, 170), font=font)
        y += d + label + gap
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=88)


def histogram(rgb: np.ndarray) -> np.ndarray:
    n = rgb.shape[0]
    L = cv2.cvtColor(to_uint8(rgb), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32) * 100 / 255
    yy, xx = np.ogrid[:n, :n]
    circle = ((xx - n / 2) ** 2 + (yy - n / 2) ** 2) < (0.95 * n / 2) ** 2
    h, _ = np.histogram(L[circle], bins=50, range=(0, 100))
    return h / h.max()


def comparison_card(title: str, ref_img: np.ndarray | None, items: list[tuple[str, np.ndarray, list[str]]], path: Path) -> None:
    """Por cada foto: la referencia arriba, mi version abajo, histogramas encimados y los numeros."""
    d, gap, hist_h = 300, 20, 110
    lines = max(len(rows) for _, _, rows in items)
    cols = len(items)
    w = gap + cols * (d + gap)
    h = 60 + (d + gap) * 2 + hist_h + 16 + lines * 24 + 40
    canvas = Image.new("RGB", (w, h), (12, 12, 12))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    draw.text((gap, 16), f"{title}: referencia arriba, mi version abajo", fill=(235, 235, 235), font=big)
    ref_hist = histogram(cv2.resize(ref_img, (420, 420))) if ref_img is not None else None
    for i, (name, img, rows) in enumerate(items):
        x = gap + i * (d + gap)
        y = 60
        if ref_img is not None:
            canvas.paste(circle(ref_img, d), (x, y))
        canvas.paste(circle(img, d), (x, y + d + gap))
        hy = y + 2 * (d + gap)
        draw.rectangle((x, hy, x + d, hy + hist_h), fill=(24, 24, 24))
        for hist, color in ((ref_hist, (120, 120, 120)), (histogram(img), (255, 196, 0))):
            if hist is None:
                continue
            pts = [(x + d * (k + 0.5) / len(hist), hy + hist_h - hist[k] * (hist_h - 6)) for k in range(len(hist))]
            draw.line(pts, fill=color, width=2)
        for j, row in enumerate(rows):
            draw.text((x, hy + hist_h + 8 + j * 24), row, fill=(255, 196, 0) if j == 0 else (200, 200, 200), font=font)
    draw.text((gap, h - 28), "Histograma de L*: gris = referencia, amarillo = mi version. Numeros: referencia / mia, en L* (0 negro, 100 blanco).",
              fill=(140, 140, 140), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=88)


def reference_image(ref: str) -> np.ndarray:
    bgr = cv2.imread(str(reference_path(ref)))
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
