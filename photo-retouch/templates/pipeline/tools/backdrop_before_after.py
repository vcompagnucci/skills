"""Antes y despues de rehacer las capas del fondo, en nativo: una zona de una foto con cada estilo.

Una fila por estilo: la maestra con la luz y el color del estilo y sin fondo | antes | despues | que cambio
(dE entre antes y despues, blanco = 4 o mas). Abajo, el alpha antes y despues (blanco = persona). "Antes" son
las capas guardadas en --before (por defecto work/estilos/antes-recuadros/, copiadas con cp -c antes de rehacer).

Uso: .venv/bin/python tools/backdrop_before_after.py <foto> 2300,2300,2700,3100 --name=franja
     opciones: --keys=white,beige  --zoom=2  --before=work/estilos/antes-recuadros
Deja proceso/estilos-antes-despues-<foto>[-<nombre>].png y los numeros en
proceso-notas/estilos/antes-despues-<foto>[-<nombre>].json: el dE entre antes y despues y, para cada uno, cuanto
se aclararon los negros de la gente (L* < 14 sin fondo: la remera y el pelo, que el fondo no tiene que tocar).
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import backdrop  # noqa: E402
from adjust import TO_LINEAR, adjust_uint16  # noqa: E402
from common import NOTES, PROCESS, ROOT, lab  # noqa: E402
from styles import STYLES, master, preset  # noqa: E402

FONT = "/System/Library/Fonts/Helvetica.ttc"
DE_WHITE = 4.0  # dE que se pinta blanco en el mapa
BLACK = 14.0  # L* sin fondo por debajo del cual un pixel es ropa negra o pelo
GAP, HEAD = 8, 22


def old_layers(name: str, folder: Path) -> backdrop.Layers:
    rgba = backdrop.read_png16(folder / f"{name}-capa.png")
    light = TO_LINEAR[backdrop.read_png16(folder / f"{name}-luz.png")]
    return backdrop.Layers(np.ascontiguousarray(rgba[..., 3]), np.ascontiguousarray(rgba[..., :3]), light, backdrop.top_lightness(light))


def to8(img16: np.ndarray) -> np.ndarray:
    return (img16.astype(np.float32) / 257 + 0.5).astype(np.uint8)


def tile(img8: np.ndarray, zoom: int) -> Image.Image:
    im = Image.fromarray(img8)
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def main(name: str, box: tuple[int, int, int, int], keys: list[str], zoom: int, before: Path, tag: str) -> Path:
    m16 = master(name)
    H, W = m16.shape[:2]
    x0, y0, x1, y1 = box
    crop = m16[y0:y1, x0:x1]
    new, old = backdrop.load_layers(name), old_layers(name, before)
    rows, report = [], {"photo": name, "box": list(box), "styles": {}}
    for key in keys:
        outs = []
        for layers in (old, new):
            light, bg = preset(name, key, layers)
            outs.append(backdrop.render(crop, x0, y0, (H, W), layers, light, bg))
        people = adjust_uint16(crop, preset(name, key, new)[0])
        de = np.linalg.norm(lab(TO_LINEAR[outs[1]]) - lab(TO_LINEAR[outs[0]]), axis=-1)
        L0 = lab(TO_LINEAR[people])[..., 0]
        black = L0 < BLACK
        lift = [lab(TO_LINEAR[o])[..., 0][black] - L0[black] for o in outs]
        report["styles"][key] = {"dE_mean": round(float(de.mean()), 3), "dE_p99": round(float(np.percentile(de, 99)), 2),
                                 "px_dE_over_2": int((de > 2).sum()), "black_px": int(black.sum()),
                                 **{f"black_lift_{t}": {"p99": round(float(np.percentile(v, 99)), 2) if v.size else 0.0,
                                                        "max": round(float(v.max()), 2) if v.size else 0.0,
                                                        "px_over_1": int((v > 1).sum())} for t, v in zip(("antes", "despues"), lift)}}
        demap = np.repeat((np.clip(de / DE_WHITE, 0, 1) * 255).astype(np.uint8)[..., None], 3, -1)
        rows.append((STYLES[key]["name"], [to8(people), to8(outs[0]), to8(outs[1]), demap]))
    alphas = [np.repeat(to8(layers.alpha16[y0:y1, x0:x1])[..., None], 3, -1) for layers in (old, new)]
    rows.append(("Alpha", alphas))
    labels = ["Sin fondo", "Antes", "Despues", f"Que cambio (blanco = dE {DE_WHITE:g})"]
    tw, th = (x1 - x0) * zoom, (y1 - y0) * zoom
    sheet = Image.new("RGB", (4 * tw + 5 * GAP, len(rows) * (th + HEAD + GAP) + GAP), (20, 20, 20))
    draw, font = ImageDraw.Draw(sheet), ImageFont.truetype(FONT, 14)
    for r, (title, imgs) in enumerate(rows):
        top = GAP + r * (th + HEAD + GAP)
        for c, img in enumerate(imgs):
            left = GAP + c * (tw + GAP)
            sheet.paste(tile(img, zoom), (left, top + HEAD))
            draw.text((left + 2, top + 3), f"{title} - {labels[c] if r < len(keys) else ('Antes', 'Despues')[c]}", fill=(220, 220, 220), font=font)
    suffix = f"-{tag}" if tag else ""
    out = PROCESS / f"estilos-antes-despues-{name}{suffix}.png"
    sheet.save(out)
    notes = NOTES / "estilos"
    notes.mkdir(parents=True, exist_ok=True)
    (notes / f"antes-despues-{name}{suffix}.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report["styles"]))
    print(out)
    return out


if __name__ == "__main__":
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], tuple(int(v) for v in args[1].split(",")), opts.get("keys", ",".join(STYLES)).split(","),
         int(opts.get("zoom", 2)), ROOT / opts.get("before", "work/estilos/antes-recuadros"), opts.get("name", ""))
