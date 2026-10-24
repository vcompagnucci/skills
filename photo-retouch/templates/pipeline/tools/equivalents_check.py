"""Prueba recipe/equivalents.py: el ajuste encuentra los valores con que se hizo una imagen, y las versiones se mueven
una sola vez.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python tools/equivalents_check.py

- El ajuste: una "maestra" hecha con adjust.adjust() y valores conocidos sobre el RAW original de la primera foto (a
  1024 px, como lo ve equivalents.py; sin fotos, un degradado de colores) tiene que dar un residuo casi nulo, y la
  exposicion y el color cerca de los conocidos (los demas controles se pisan entre si: varias combinaciones dan la misma
  imagen, por eso se mide la imagen y no cada valor).
- shifted(): suma solo a Light y Color, solo lo que esta, al paso de cada control.
- main(), con el ajuste y la carga de imagenes reemplazados (rapido) y todo en work/equivalents-check/ (editadas/,
  recipe/equivalents.json y versiones.json no se tocan): la primera vez suma el punto de partida a las versiones, con
  respaldo; la segunda no hace nada; si la maestra cambia, el punto de partida se vuelve a calcular y las versiones
  quedan como estaban.
- load_starts() sin el archivo: ninguno.
"""

import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import adjust  # noqa: E402
import equivalents  # noqa: E402
from common import EDITED, ROOT  # noqa: E402
from photos import PHOTOS  # noqa: E402

WORK = ROOT / "work" / "equivalents-check"
KNOWN = {"exposure": 0.35, "brightness": 0.0, "contrast": 18.0, "highlights": -20.0, "shadows": 15.0, "whites": 0.0,
         "blacks": -10.0, "temperature": 12.0, "tint": -25.0, "vibrance": 0.0, "saturation": 10.0}

failed = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok ' if ok else 'MAL'} {name}{'' if ok else f'  ({detail})'}", flush=True)
    if not ok:
        failed.append(name)


def source() -> tuple[str, np.ndarray]:
    """El RAW original de la primera foto que lo tenga, a 1024 px y en luz lineal; sin fotos, un degradado de colores."""
    for name in PHOTOS:
        if (EDITED / f"{name}.tif").exists() and (EDITED / f"{name}-antes.png").exists():
            return "el RAW original de la primera foto", equivalents.load(name)[0]
    y, x = np.mgrid[0:512, 0:768] / np.array([511, 767])[:, None, None]
    img = np.stack([x, y, 1 - (x + y) / 2], axis=-1) ** 2.2
    return "un degradado de colores", img.astype(np.float32)


def check_fit() -> None:
    what, raw = source()
    master = adjust.adjust(raw, KNOWN)
    values, res, edges = equivalents.fit(raw, master)
    check(f"ajuste sobre {what}: la imagen con los valores encontrados es la maestra (|dL*| media < 0,3, dE76 media < 0,5)",
          res["mean_dL"] < 0.3 and res["mean_dE"] < 0.5, f"{res}")
    check("ajuste: la exposicion a 0,1 de la conocida y el color (temperatura, tinte) a 8",
          abs(values["exposure"] - KNOWN["exposure"]) <= 0.1 and all(abs(values[k] - KNOWN[k]) <= 8 for k in ("temperature", "tint")),
          f"{values}")
    check("ajuste: valores al paso de cada control y ninguno en el limite",
          values["exposure"] == round(values["exposure"], 2) and all(values[k] == round(values[k]) for k in adjust.KEYS if k != "exposure") and not edges,
          f"{values} {edges}")
    same = equivalents.fit(raw, adjust.adjust(raw, dict.fromkeys(adjust.KEYS, 0.0)))[0]
    check("ajuste: una maestra igual al RAW da todo 0 (o un paso)",
          all(abs(v) <= (0.01 if k == "exposure" else 1) for k, v in same.items()), f"{same}")


def check_shifted() -> None:
    flat = {"Light.Exposure": 0.1, "Light.Contrast": 5, "Color.Tint": -3, "Background.Exposure": 0.4, "Under-eyes.Beard": 70,
            "Light.Reset": {"type": "action"}}
    delta = {"exposure": 0.234, "contrast": 49.4, "tint": -60, "shadows": 20, "saturation": 0}
    out = equivalents.shifted(flat, delta)
    check("shifted: suma a Light y Color, al paso (0,01 y 1)", out["Light.Exposure"] == 0.33 and out["Light.Contrast"] == 54 and out["Color.Tint"] == -63, f"{out}")
    check("shifted: no agrega controles que no estan ni toca Background, ojeras ni botones",
          "Light.Shadows" not in out and out["Background.Exposure"] == 0.4 and out["Under-eyes.Beard"] == 70 and out["Light.Reset"] == {"type": "action"}, f"{out}")
    check("shifted: no cambia lo que recibe", flat["Light.Exposure"] == 0.1)


def check_main() -> None:
    shutil.rmtree(WORK, ignore_errors=True)
    edited, notes, process = WORK / "editadas", WORK / "proceso-notas", WORK / "proceso"
    edited.mkdir(parents=True)
    names = list(PHOTOS)[:2]
    for n in names:
        (edited / f"{n}.tif").write_bytes(b"maestra")
        (edited / f"{n}-antes.png").write_bytes(b"raw")
    version = {"Light.Exposure": 0.5, "Light.Contrast": 10, "Background.Exposure": 0.45}
    state = {"version": 1, "values": dict(version), "baseValues": {"Light.Exposure": 0}, "activePresetId": "a",
             "presets": [{"id": "a", "name": "Version 2", "values": dict(version)}]}
    versions = edited / "versiones.json"
    versions.write_text(json.dumps({"photos": {names[0]: state}}))
    starts = {names[0]: dict(KNOWN, exposure=0.2, contrast=40.0), names[1]: dict(KNOWN, exposure=-0.3)}
    small = np.full((24, 36, 3), 0.18, np.float32)
    saved = {k: getattr(equivalents, k) for k in ("EDITED", "NOTES", "PROCESS", "STARTS", "VERSIONS", "BACKUPS", "fit", "load")}
    fits = []
    equivalents.EDITED, equivalents.NOTES, equivalents.PROCESS = edited, notes, process
    equivalents.STARTS, equivalents.VERSIONS, equivalents.BACKUPS = WORK / "equivalents.json", versions, WORK / "respaldos"
    equivalents.load = lambda photo: (small, small)
    try:
        def run(*args, values_by_photo):
            """main() con el ajuste reemplazado: devuelve, foto por foto en orden, los valores de values_by_photo."""
            order = [n for n in names if n in values_by_photo]
            fits.clear()

            def fake_fit(raw, master):
                fits.append(1)
                return dict(values_by_photo[order[len(fits) - 1]]), {"mean_dL": 0.5, "p95_dL": 1.0, "mean_dE": 0.6, "p95_dE": 1.2}, []

            equivalents.fit = fake_fit
            out = io.StringIO()
            with redirect_stdout(out):
                equivalents.main(list(args))
            return out.getvalue()

        run(values_by_photo=starts)
        st = json.loads(versions.read_text())["photos"][names[0]]
        p = st["presets"][0]["values"]
        check("main, la primera vez: a las versiones se les suma el punto de partida (Light y Color; el fondo igual)",
              p["Light.Exposure"] == 0.7 and p["Light.Contrast"] == 50 and p["Background.Exposure"] == 0.45 and st["values"] == p and st["baseValues"]["Light.Exposure"] == 0.2,
              f"{st}")
        backups = list((WORK / "respaldos").glob("versiones-antes-equivalentes-*.json"))
        check("main, la primera vez: respaldo de versiones.json antes de moverlas",
              len(backups) == 1 and json.loads(backups[0].read_text())["photos"][names[0]]["presets"][0]["values"]["Light.Exposure"] == 0.5)
        written = equivalents.load_starts()
        check("main: recipe/equivalents.json con los dos puntos de partida", written == starts, f"{written}")
        check("main: la hoja en proceso/ y la tabla en proceso-notas/",
              (process / "equivalentes-hoja.png").exists() and (notes / "equivalentes" / "equivalentes.txt").exists())

        before = versions.read_text()
        log = run(values_by_photo={})
        check("main, la segunda vez: nada que ajustar y las versiones igual", not fits and versions.read_text() == before and "versiones con el punto" not in log, log)

        os.utime(edited / f"{names[0]}.tif", ns=(1, 1))  # la maestra cambio (su firma)
        log = run(names[0], values_by_photo={names[0]: dict(KNOWN, exposure=0.4, contrast=40.0)})
        check("main, maestra nueva: se vuelve a ajustar esa sola, y avisa que el punto de partida cambio",
              len(fits) == 1 and equivalents.load_starts()[names[0]]["exposure"] == 0.4 and "el punto de partida cambio" in log, log)
        check("main, maestra nueva: las versiones no se tocan (son valores del panel) ni hay otro respaldo",
              versions.read_text() == before and len(list((WORK / "respaldos").glob("*.json"))) == 1)
    finally:
        for k, v in saved.items():
            setattr(equivalents, k, v)

    equivalents.STARTS = WORK / "no-existe.json"
    try:
        check("load_starts sin el archivo: ninguno (el panel arranca en 0)", equivalents.load_starts() == {})
    finally:
        equivalents.STARTS = saved["STARTS"]
    shutil.rmtree(WORK, ignore_errors=True)


def main() -> int:
    check_shifted()
    check_main()
    check_fit()
    if failed:
        print(f"fallaron {len(failed)}: {', '.join(failed)}")
        return 1
    print("todo bien")
    return 0


if __name__ == "__main__":
    sys.exit(main())
