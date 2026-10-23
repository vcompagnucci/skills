"""Adapta una version de LOOKS (recipe/styles.py) a cada foto: la exposicion y los negros, por foto, con topes.

El fotografo (2026-10-17): "fijate de adaptar los estilos bien a las fotos, no es poner el filtro y ya". Copiar los
percentiles de piel de la referencia forzaba el panel a donde ningun retocador lo lleva (exposure +0,6, blacks +-40,
highlights -40), porque esos percentiles los pone la luz del fotografo, que el panel no cambia. Asi que de la
referencia se toma la pared (Background) y la direccion (los demas ajustes, dentro del rango de los tres estilos
aprobados), y por foto se resuelven solo dos cosas, con el mismo codigo que mide las referencias (ref_measure):

- exposicion: la luz de la piel (p90) a la de la referencia, como mucho EXP_MAX pasos para cada lado;
- quemado: el % de la cara (las elipses) con algun canal quemado se informa, no se corrige: el fotografo aprobo la luz de
  Robinhood y Nothing con el brillo de la frente quemado (2026-10-17), asi que es su decision;
- negros: la ropa negra (p50 de los recuadros `blacks`) entre BLACK_LO y BLACK_HI, y su p1 sin aplastar. La ropa de
  la referencia (un saco de terciopelo, una remera lavada) no cuenta: es una restriccion, no un objetivo.

Uso: .venv/bin/python tools/look_fit.py <clave de LOOKS> [...]   -> imprime lo de cada foto, para copiar a LOOKS
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from adjust import adjust, parse  # noqa: E402
from common import NOTES, PHOTO_NAMES  # noqa: E402
from ref_measure import ellipses, measure, ref_regions  # noqa: E402
from references import load_reference  # noqa: E402
from style_pilot import mine, regions  # noqa: E402
from styles import LOOKS  # noqa: E402

EXP_MAX = 0.3  # pasos: los tres estilos aprobados no pasan de 0,15
BLACK_LO, BLACK_HI = 5.0, 10.0  # L* de la ropa negra: mas abajo se empasta, mas arriba se lava
BLACKS_RANGE = (-20, 5)  # el control de negros, buscado dentro de esto
P1_MIN = 0.5  # L* del percentil 1 de la foto: por debajo, negro sin detalle


def face_clip(lin: np.ndarray, reg) -> float:
    m = ellipses(lin.shape[:2], reg.faces, 1.0)
    return float((lin.max(axis=-1)[m] >= 0.99).mean() * 100)


def measured(lin, reg, params):
    """Lo medido y el % de cara quemada, con un solo adjust."""
    out = adjust(lin, parse(params))
    m = measure(out, reg)
    m["face_clip"] = face_clip(out, reg)
    return m


def fit(name: str, light: dict, target_p90: float) -> tuple[dict, dict]:
    lin = mine(name)
    reg = regions(name, lin)
    p = dict(light)
    lo, hi = -EXP_MAX, EXP_MAX
    for _ in range(12):  # biseccion sobre la exposicion: p90 de la piel crece con ella
        p["exposure"] = round((lo + hi) / 2, 2)
        m = measured(lin, reg, p)
        if m["skin"]["p90"] < target_p90:
            lo = p["exposure"]
        else:
            hi = p["exposure"]
    m = measured(lin, reg, p)
    black = m["black"]["p50"]
    if not (BLACK_LO <= black <= BLACK_HI) or m["tone"][0] < P1_MIN:
        want = min(max(black, BLACK_LO), BLACK_HI)
        best = None
        for v in range(BLACKS_RANGE[0], BLACKS_RANGE[1] + 1):
            q = p | {"blacks": v}
            mq = measured(lin, reg, q)
            if mq["tone"][0] < P1_MIN:
                continue
            err = abs(mq["black"]["p50"] - want)
            if best is None or err < best[0]:
                best = (err, v, mq)
        if best:
            p["blacks"], m = best[1], best[2]
    return {k: v for k, v in p.items() if v}, m


def main(keys: list[str]) -> None:
    for key in keys:
        look = LOOKS[key]
        ref = look["ref"]
        r = measure(load_reference(ref), ref_regions(ref))
        target = r["skin"]["p90"]
        print(f"== {key} ({ref}): piel p90 {target:.1f}, ropa {BLACK_LO:g}-{BLACK_HI:g}")
        out = {}
        for name in PHOTO_NAMES:
            p, m = fit(name, look["base"], target)
            out[name] = {"exposure": p.get("exposure", 0.0), "blacks": p.get("blacks", 0)}
            s, b = m["skin"], m["black"]
            print(f"  {name} exp {out[name]['exposure']:+.2f} blacks {out[name]['blacks']:+d} | piel {s['p50']:.0f}/{s['p90']:.0f}"
                  f" C {s['C']:.1f} | ropa {b['p50']:.1f} p1 {m['tone'][0]:.1f} | cara quemada {m['face_clip']:.2f} %")
        (NOTES / "estilos" / f"ajuste-{key}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:] or [k for k, v in LOOKS.items() if "base" in v])
