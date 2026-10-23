"""Una referencia de estilo bajada (un archivo o un miembro de un zip), a proceso/referencias-<id>.png en sRGB.

Los press kits vienen en JPEG y este proyecto no tiene JPEG en ningun paso (.sin-jpg): el miembro del zip se lee en
memoria, se convierte desde su perfil ICC (Display P3 incluido) a sRGB y se guarda en PNG. Nunca toca el disco como
JPEG. Sin perfil, se toma como sRGB. No la agranda ni la recorta.

Uso: .venv/bin/python tools/ref_import.py <id> <archivo>                    (PNG, TIFF...)
     .venv/bin/python tools/ref_import.py <id> <zip> "<miembro del zip, o un pedazo unico de su nombre>"
     .venv/bin/python tools/ref_import.py --list <zip> [--max=900]        hoja de las imagenes del zip, a 900 px
"""

import io
import sys
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


def to_srgb(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data))
    icc = im.info.get("icc_profile")
    im = im.convert("RGB")
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        im = ImageCms.profileToProfile(im, src, SRGB, renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
                                       outputMode="RGB")
    return im


def read(src: Path, member: str | None) -> bytes:
    if member is None:
        return src.read_bytes()
    with zipfile.ZipFile(src) as z:
        names = [n for n in z.namelist() if n.lower().endswith(IMAGES) and "__MACOSX" not in n]
        found = [n for n in names if member == n or member in n]  # un pedazo del nombre alcanza
        if len(found) != 1:
            raise SystemExit(f"{member!r}: {len(found)} imagenes con ese nombre en {src.name}")
        return z.read(found[0])


def save(ref: str, src: Path, member: str | None) -> Path:
    im = to_srgb(read(src, member))
    out = PROCESS / f"referencias-{ref}.png"
    srgb_icc = ImageCms.ImageCmsProfile(SRGB).tobytes()
    im.save(out, icc_profile=srgb_icc, compress_level=6)
    print(out, im.size)
    return out


def sheet(src: Path, size: int) -> Path:
    """Las imagenes del zip en chico, para elegir: work/referencias-nuevas/<zip>-hoja.png."""
    with zipfile.ZipFile(src) as z:
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
    out = ROOT / "work" / "referencias-nuevas" / f"{src.stem}-hoja.png"
    out_im.save(out)
    print(out)
    return out


if __name__ == "__main__":
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--list" in sys.argv:
        sheet(Path(args[0]), int(opts.get("max", 900)))
    else:
        save(args[0], Path(args[1]), args[2] if len(args) > 2 else None)
