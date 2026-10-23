"""Las entradas de las pruebas del borde y del color: cuatro renders de la maestra y el alpha de la foto.

Por caso, en work/gate/ (o en la carpeta de --out, que las pruebas no leen: leen solo work/gate/):
- <foto>-<estilo>-pared-no-crudo.png: la persona con su luz, su curva y su color, y la pared como salio del RAW;
- <foto>-<estilo>-pared-si-crudo.png: el mismo render con la pared llevada a la del estilo (edit_wall);
- <foto>-<estilo>-pared-no-final.png: el primero con el enfoque de salida (finish, sin grano ni LUT);
- <foto>-<estilo>-pared-si-final.png: el segundo con el enfoque de salida, sin grano, y la LUT de la camara en los
  estilos con camera_look: la maestra antes del grano;
- <foto>-alpha.npz: alpha y skin de la escena (float16). En blanco y negro el gate no reconoce la piel por el color.

Son los mismos pixeles que las pruebas del piloto del metodo del proyecto original: la misma escena, los mismos
parametros y el mismo orden de llamadas. Las asimetrias son a proposito: "pared-no" mide la curva sola contra el
aclarado, asi que no lleva LUT; ningun render lleva grano, que taparia el borde. Los leen tools/edge_gate.py,
tools/edge_montage.py y tools/color_zones.py.

Una maestra a 4170 px pasa los 2 GB: correr una foto por vez, con MallocLargeCache=0 nice -n 19.

Uso: .venv/bin/python tools/gate_renders.py <photo>:<style> [...] [--out DIR]
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "recipe"))
from camera_lut import camera_lut  # noqa: E402
from common import ROOT  # noqa: E402
from photos import PHOTOS  # noqa: E402
from styles import MASTER, STYLES, build_scene, edit_wall, finish, fit_params, render_person, targets_of, to_srgb  # noqa: E402

GATE = ROOT / "work" / "gate"


def write_png(path: Path, srgb: np.ndarray) -> None:
    cv2.imwrite(str(path), cv2.cvtColor((srgb * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])


def render_case(name: str, key: str, out: Path) -> None:
    style = {s.key: s for s in STYLES}[key]
    want = targets_of(style)
    p = fit_params(name, style, want)
    scene = build_scene(name, "abierto", MASTER)
    person, toe = render_person(scene, style, p)
    base = to_srgb(edit_wall(scene, person, toe, want=want))  # edit_wall con la persona lineal, antes de to_srgb
    del toe
    person = to_srgb(person)
    for label, img in (("pared-no-crudo", person), ("pared-si-crudo", base), ("pared-no-final", finish(person))):
        write_png(out / f"{name}-{key}-{label}.png", img)
    del person
    master = camera_lut(name, finish(base)) if style.camera_look else finish(base)
    del base
    write_png(out / f"{name}-{key}-pared-si-final.png", master)
    del master
    np.savez_compressed(out / f"{name}-alpha.npz", alpha=scene.alpha.astype(np.float16), skin=scene.skin.astype(np.float16))
    del scene
    build_scene.cache_clear()  # una foto entera por vez en memoria
    print(f"{name} {key} -> {out}", flush=True)


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description="Renders de entrada de edge_gate.py, edge_montage.py y color_zones.py.")
    ap.add_argument("cases", nargs="+", metavar="<photo>:<style>")
    ap.add_argument("--out", type=Path, default=GATE, metavar="DIR", help="en lugar de work/gate")
    args = ap.parse_args(argv)
    keys = [s.key for s in STYLES]
    cases = []
    for case in args.cases:
        name, sep, key = case.rpartition(":")
        if not sep or name not in PHOTOS or key not in keys:
            ap.error(f"{case!r}: tiene que ser <foto>:<estilo>, con la foto en photos.py y el estilo uno de {', '.join(keys)}")
        cases.append((name, key))
    args.out.mkdir(parents=True, exist_ok=True)
    for name, key in cases:
        render_case(name, key, args.out)


if __name__ == "__main__":
    main(sys.argv[1:])
