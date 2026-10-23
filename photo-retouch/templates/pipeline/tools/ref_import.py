"""Una referencia de estilo (un archivo, un miembro de un zip, o una URL de cualquiera de los dos), a
proceso/referencias-<id>.png en sRGB.

Los press kits vienen en JPEG y este proyecto no tiene JPEG en ningun paso (.sin-jpg): la imagen o el miembro del zip
se lee en memoria, se convierte desde su perfil ICC (Display P3 incluido) a sRGB y se guarda en PNG. Una URL http(s)
se baja a memoria, nunca a disco, y sigue igual que un archivo local. Nunca toca el disco como JPEG. Sin perfil, se
toma como sRGB. No la agranda ni la recorta.

Uso: .venv/bin/python tools/ref_import.py <id> <archivo|url>                    (PNG, TIFF, JPEG...)
     .venv/bin/python tools/ref_import.py <id> <zip|url> "<miembro del zip, o un pedazo unico de su nombre>"
     .venv/bin/python tools/ref_import.py --list <zip|url> [--max=900]        hoja de las imagenes del zip, a 900 px,
                                                                              en proceso/referencias-<zip>-hoja.png
"""

import io
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "recipe"))
from common import PROCESS  # noqa: E402

Image.MAX_IMAGE_PIXELS = 200_000_000
FONT = "/System/Library/Fonts/Helvetica.ttc"
SRGB = ImageCms.createProfile("sRGB")
IMAGES = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"  # algunos CDN de press kits rechazan el de urllib


def is_url(src: str) -> bool:
    return src.startswith(("http://", "https://"))


def name_of(src: str) -> str:
    """El nombre del archivo, tambien el de una URL (el ultimo pedazo de su ruta)."""
    return Path(urllib.parse.urlparse(src).path).name if is_url(src) else Path(src).name


def fetch(url: str) -> bytes:
    """La URL bajada entera a memoria: no pasa por el disco."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def zip_of(src: str) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(fetch(src)) if is_url(src) else Path(src))


def to_srgb(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data))
    icc = im.info.get("icc_profile")
    im = im.convert("RGB")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, SRGB, renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                       outputMode="RGB")
    return im


def read(src: str, member: str | None) -> bytes:
    if member is None and name_of(src).lower().endswith(".zip"):
        raise SystemExit(f"{name_of(src)} es un zip: falta el miembro (los nombres, con --list {src})")
    if member is None:
        return fetch(src) if is_url(src) else Path(src).read_bytes()
    with zip_of(src) as z:
        names = [n for n in z.namelist() if n.lower().endswith(IMAGES) and "__MACOSX" not in n]
        found = [n for n in names if member == n or member in n]  # un pedazo del nombre alcanza
        if len(found) != 1:
            raise SystemExit(f"{member!r}: {len(found)} imagenes con ese nombre en {name_of(src)}")
        return z.read(found[0])


def save(ref: str, src: str, member: str | None) -> Path:
    im = to_srgb(read(src, member))
    out = PROCESS / f"referencias-{ref}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    srgb_icc = ImageCms.ImageCmsProfile(SRGB).tobytes()
    im.save(out, icc_profile=srgb_icc, compress_level=6)
    print(out, im.size)
    return out


def sheet(src: str, size: int) -> Path:
    """Las imagenes del zip en chico, para elegir: proceso/referencias-<zip>-hoja.png."""
    with zip_of(src) as z:
        names = [n for n in z.namelist() if n.lower().endswith(IMAGES) and "__MACOSX" not in n]
        thumbs = []
        for n in names:
            im = to_srgb(z.read(n))
            print(n, im.size)
            im.thumbnail((size // 3, size // 3))
            thumbs.append((Path(n).name, im))
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    cell = size // 3
    out_im = Image.new("RGB", (cell * cols, (cell + 20) * rows), (20, 20, 20))
    draw, font = ImageDraw.Draw(out_im), ImageFont.truetype(FONT, 12)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * cell, (i // cols) * (cell + 20)
        out_im.paste(im, (x, y + 20))
        draw.text((x + 4, y + 4), name[:40], fill=(220, 220, 220), font=font)
    out = PROCESS / f"referencias-{Path(name_of(src)).stem or 'zip'}-hoja.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out_im.save(out)
    print(out)
    return out


if __name__ == "__main__":
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--list" in sys.argv:
        sheet(args[0], int(opts.get("max", 900)))
    else:
        save(args[0], args[1], args[2] if len(args) > 2 else None)
