"""El registro de las fotos importadas desde el editor (editadas/importadas.json, o EDITOR_IMPORTS en las pruebas):
que archivo vino, como se llama en el editor y en que quedo. Lo escriben el servidor (al recibir el archivo) y
import_photo.py (al terminar cada paso), asi que cada escritura toma un lock de archivo y cambia el JSON de una vez.

Que se acepta: todo RAW que lea LibRaw y toda imagen que lea macOS (sips: TIFF, PNG, HEIC, AVIF, WebP, GIF, BMP, PSD).
JPEG no, mientras el proyecto tenga .sin-jpg: el brief fue sin JPG en ningun paso (README > Pendiente).
"""

import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

from common import ROOT
from photos import IMPORTS, STUDIO

# las pruebas traen sus archivos de work/ (EDITOR_ORIGINALS): nunca escriben en originales/
ORIGINALS = Path(os.environ.get("EDITOR_ORIGINALS") or ROOT / "originales")
RAW = {".raf", ".dng", ".cr2", ".cr3", ".crw", ".nef", ".nrw", ".arw", ".srf", ".sr2", ".orf", ".rw2", ".raw", ".pef",
       ".srw", ".x3f", ".3fr", ".fff", ".iiq", ".erf", ".mef", ".mos", ".mrw", ".kdc", ".dcr", ".rwl", ".gpr"}
RASTER = {".tif", ".tiff", ".png", ".heic", ".heif", ".hif", ".avif", ".webp", ".gif", ".bmp", ".psd"}
LOSSY = {".jpg", ".jpeg", ".jpe", ".jfif"}
MAX_BYTES = 600 * 1024 * 1024  # un RAW de medio formato entra; un archivo de 2 GB no es una foto
NO_LOSSY = (ROOT / ".sin-jpg").exists()


def kind(filename: str) -> str | None:
    """raw, raster o None (no se acepta)."""
    ext = Path(filename).suffix.lower()
    if ext in RAW:
        return "raw"
    if ext in RASTER or (ext in LOSSY and not NO_LOSSY):
        return "raster"
    return None


def read() -> dict:
    try:
        return json.loads(IMPORTS.read_text()) if IMPORTS.exists() else {"photos": {}}
    except (OSError, ValueError):
        return {"photos": {}}


@contextmanager
def editing():
    """El registro, para cambiarlo: con lock, y se escribe entero al salir."""
    IMPORTS.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPORTS.with_name(f".{IMPORTS.name}.lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = read()
        yield data
        fd, tmp = tempfile.mkstemp(dir=IMPORTS.parent, prefix=".importadas-", suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, IMPORTS)


def new_key(filename: str, taken) -> str:
    """La clave de la foto: el nombre del archivo en letras, numeros, _ y -; si ya esta, con -2, -3..."""
    stem = re.sub(r"[^A-Za-z0-9_-]+", "-", Path(filename).stem).strip("-")[:40] or "foto"
    key, n = stem, 2
    while key in taken or key in STUDIO or any(ORIGINALS.glob(f"{key}.*")):
        key, n = f"{stem}-{n}", n + 1
    return key


def label(key: str, taken=()) -> str:
    """Lo que dice la pestana: el numero de un nombre de camara (XXXX1234 -> 1234), y si no, el nombre corto. Si otra
    foto ya dice eso (un XXXX1234 de otra sesion), la clave entera: dos pestanas iguales no se distinguen."""
    m = re.fullmatch(r"[A-Za-z_]{3,5}(\d{3,5})(-\d+)?", key)
    short = f"{m.group(1)}{m.group(2) or ''}" if m else key[:12]
    return short if short not in taken else key[:24]
