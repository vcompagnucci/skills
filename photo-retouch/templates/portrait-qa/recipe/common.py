"""Piezas compartidas: leer la base lineal, codificar a sRGB, guardar y armar hojas."""

import os
from functools import cache
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent


def load_base(name: str) -> np.ndarray:
    """Base lineal en float32, 0..1, RGB."""
    return tifffile.imread(ROOT / "work" / f"{name}-base.tif").astype(np.float32) / 65535.0


def save_base(name: str, img: np.ndarray, suffix: str) -> Path:
    out = ROOT / "work" / f"{name}-{suffix}.tif"
    tifffile.imwrite(out, np.clip(img * 65535.0, 0, 65535).astype(np.uint16), compression="zlib")
    return out


def luminance(img: np.ndarray) -> np.ndarray:
    return img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def linear_to_srgb(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def srgb_to_linear(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, np.power((x + 0.055) / 1.055, 2.4))


def to_uint8(srgb: np.ndarray) -> np.ndarray:
    return (np.clip(srgb, 0, 1) * 255 + 0.5).astype(np.uint8)


def resize(img: np.ndarray, height: int) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (round(w * height / h), height), interpolation=cv2.INTER_AREA)


def write_atomically(path: Path, write) -> None:
    """Escribe al lado y renombra: quien lea el archivo (el servidor del editor) nunca lo ve a medio escribir."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    write(tmp)
    os.replace(tmp, path)


def save_jpeg(srgb: np.ndarray, path: Path, quality: int = 95) -> None:
    img = Image.fromarray(to_uint8(srgb))
    write_atomically(path, lambda tmp: img.save(tmp, "JPEG", quality=quality, subsampling=0, icc_profile=srgb_icc()))


def to_uint16(srgb: np.ndarray) -> np.ndarray:
    return (np.clip(srgb, 0, 1) * 65535 + 0.5).astype(np.uint16)


def save_tiff16(srgb: np.ndarray, path: Path) -> None:
    """La maestra sin perdida: 16 bits por canal, sRGB con su perfil. De aca salen las exportaciones."""
    data = to_uint16(srgb)
    write_atomically(path, lambda tmp: tifffile.imwrite(tmp, data, photometric="rgb", compression="zlib", predictor=True,
                                                         iccprofile=srgb_icc(), resolution=(72, 72), resolutionunit="INCH"))


def contact_sheet(tiles: list[tuple[str, np.ndarray]], path: Path, height: int = 900) -> None:
    """Tiles en sRGB 0..1, una fila, con la etiqueta abajo de cada uno."""
    gap, label_h = 12, 44
    small = [(label, to_uint8(resize(img, height))) for label, img in tiles]
    width = sum(t.shape[1] for _, t in small) + gap * (len(small) + 1)
    sheet = Image.new("RGB", (width, height + label_h + gap), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
    x = gap
    for label, tile in small:
        sheet.paste(Image.fromarray(tile), (x, gap))
        draw.text((x, height + gap + 8), label, fill="black", font=font)
        x += tile.shape[1] + gap
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=88)


@cache
def srgb_icc() -> bytes | None:
    try:
        from PIL import ImageCms

        return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    except Exception:
        return None
