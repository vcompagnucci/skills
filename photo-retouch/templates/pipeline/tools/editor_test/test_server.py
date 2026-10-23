"""Prueba del servidor del editor: exportar con luz y color y con el fondo, nombres de archivo y versiones guardadas.

Uso: .venv/bin/python tools/editor_test/test_server.py

Arranca recipe/editor_server.py en el puerto 8791 y lo apaga siempre al final. editadas/versiones.json
se respalda antes y se deja como estaba.
"""

import http.client
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "recipe"))
import adjust  # noqa: E402
import backdrop  # noqa: E402
import editor_server  # noqa: E402  (importarlo no arranca nada)
from photos import PHOTOS, STUDIO  # noqa: E402

PORT = 8791
HOST = f"127.0.0.1:{PORT}"
VERSIONS = ROOT / "editadas" / "versiones.json"
# la foto de la prueba: EDITOR_TEST_PHOTO, o la primera de la sesion (recipe/photos.py). Tiene que tener pared (para
# el fondo) y al menos una cara inventariada (para las ojeras)
PHOTO = os.environ.get("EDITOR_TEST_PHOTO") or STUDIO[0]
OTHER = next((k for k in STUDIO if k != PHOTO), None)  # una segunda foto, para las versiones de dos fotos
_cx, _cy = PHOTOS[PHOTO]["faces"][0]["oval"][:2]
_H, _W = tifffile.TiffFile(ROOT / "editadas" / f"{PHOTO}.tif").pages[0].shape[:2]  # la maestra
# toca el parche de ojeras de la primera cara, sin salirse de la foto
BOX = [min(max(int(_cx) - 512, 0), max(_W - 1024, 0)), min(max(int(_cy) - 512, 0), max(_H - 1024, 0)), 1024, 1024]
ALL_ON = {k: (0.6 if k == "exposure" else 35 - 7 * i) for i, k in enumerate(adjust.KEYS)}
BG_ON = {"exposure": 0.45, "evenness": 65, "falloff": 30, "temperature": 40, "tint": -12, "saturation": -100}

failed = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok ' if ok else 'MAL'} {name}{'' if ok else f'  ({detail})'}", flush=True)
    if not ok:
        failed.append(name)


def call(method: str, path: str, body=None, headers=None, raw: bytes | None = None) -> tuple[int, dict, bytes]:
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=30)
    h = {"Host": HOST}
    if body is not None or raw is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    try:
        conn.request(method, path, body=data, headers=h)
        r = conn.getresponse()
        return r.status, dict(r.getheaders()), r.read()
    finally:
        conn.close()


def prepare(**extra) -> tuple[int, dict]:
    req = {"photo": PHOTO, "image": "edit", "box": BOX, "size": "full", "format": "png"} | extra
    status, _, data = call("POST", "/api/prepare", req)
    return status, json.loads(data)


def download(fid: str) -> bytes:
    status, _, data = call("GET", f"/api/file/{fid}")
    assert status == 200, status
    return data


def decode(png: bytes) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def state(n: int = 1, active: str | None = "preset-a") -> dict:
    presets = [{"id": f"preset-{'a' if i == 0 else i}", "name": f"Version {i + 1}", "values": {"Light.exposure": 0.3 * i}}
               for i in range(n)]
    return {"version": 1, "values": {"Light.exposure": 0.5, "Color.tint": -12, "Panel.open": True, "mode": "edit"},
            "baseValues": {"Light.exposure": 0}, "presets": presets, "activePresetId": active}


def wait_ready(proc: subprocess.Popen) -> None:
    for _ in range(150):
        if proc.poll() is not None:
            raise RuntimeError("el servidor se cerro al arrancar")
        try:
            if call("GET", "/editor.html")[0] == 200:
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("el servidor no contesto")


def test_prepare() -> None:
    x, y, w, h = BOX
    full = tifffile.imread(ROOT / "editadas" / f"{PHOTO}.tif")
    crop = full[y : y + h, x : x + w].copy()
    del full
    manifest = editor_server.eye_manifest()[0]
    default = manifest["intensity"]
    suffix = f"-crop-{w}x{h}.png"

    s1, r1 = prepare()
    a = download(r1["id"])
    s2, r2 = prepare(adjust={k: 0 for k in adjust.KEYS})
    b = download(r2["id"])
    check("neutro: identico con y sin adjust en 0", s1 == s2 == 200 and a == b)
    check("neutro: los pixeles de la maestra", np.array_equal(decode(a), crop))
    check("nombre neutro", r1["name"] == f"{PHOTO}{suffix}" and r1["adjusted"] is False and r1["version"] is None, r1["name"])

    s, r = prepare(adjust=ALL_ON)
    got = decode(download(r["id"])).astype(np.int32)
    want = adjust.adjust_uint16(editor_server.blend_eyes(crop, PHOTO, x, y, default, manifest), adjust.parse(ALL_ON))
    diff = int(np.abs(got - want).max())
    check("ajustado: igual a adjust_uint16 sobre la maestra", s == 200 and diff <= 1, f"{s}, {diff} niveles")
    check("nombre ajustado", r["name"] == f"{PHOTO}-adjusted{suffix}" and r["adjusted"] is True, r["name"])

    assert 120 != default and 120 <= manifest["max"], "120 tiene que ser distinto de la final"
    s, r = prepare(adjust=ALL_ON, under_eyes=120)
    got = decode(download(r["id"])).astype(np.int32)
    want = adjust.adjust_uint16(editor_server.blend_eyes(crop, PHOTO, x, y, 120, manifest), adjust.parse(ALL_ON))
    diff = int(np.abs(got - want).max())
    check("ajustado con ojeras al 120: los pixeles", s == 200 and diff <= 1, f"{s}, {diff} niveles")
    check("nombre ajustado con ojeras", r["name"] == f"{PHOTO}-adjusted-under-eyes-120{suffix}", r["name"])

    s, r = prepare(adjust=ALL_ON, under_eyes=120, version="Version 2")
    check("nombre con version", s == 200 and r["name"] == f"{PHOTO}-version-2{suffix}" and r["version"] == "version-2",
          r.get("name"))

    s, r = prepare(image="raw", adjust=ALL_ON, version="Version 2")
    check("el RAW ignora ajustes y version", s == 200 and r["name"] == f"{PHOTO}-raw{suffix}" and not r["adjusted"], r.get("name"))

    bad = {"clave desconocida": {"adjust": {"glow": 10}}, "101": {"adjust": {"contrast": 101}},
           "exposicion 3": {"adjust": {"exposure": 3}}, "NaN en texto": {"adjust": {"contrast": "NaN"}},
           "True": {"adjust": {"contrast": True}}, "version de 41": {"version": "v" * 41}, "version numero": {"version": 2},
           "fondo con clave desconocida": {"background": {"glow": 10}}, "fondo parejo 150": {"background": {"evenness": 150}},
           "fondo parejo negativo": {"background": {"evenness": -1}}, "fondo como lista": {"background": [1, 2]}}
    for name, extra in bad.items():
        s, r = prepare(**extra)
        check(f"prepare rechaza {name}", s == 400, f"{s} {r}")


def test_backdrop() -> None:
    """El fondo: lo mismo que backdrop.render sobre la maestra, en un recorte con pared, pelo y cara."""
    cx, cy, rx, ry = PHOTOS[PHOTO]["faces"][0]["oval"][:4]
    w = h = 1024
    x, y = int(cx - w / 2), int(max(cy - ry - h / 2, 0))
    full = tifffile.imread(ROOT / "editadas" / f"{PHOTO}.tif")
    H, W = full.shape[:2]
    crop = full[y : y + h, x : x + w].copy()
    del full
    manifest = editor_server.eye_manifest()[0]
    layers = backdrop.load_layers(PHOTO)
    a = layers.alpha16[y : y + h, x : x + w]
    check("fondo: el recorte tiene pared, borde y persona", (a == 0).any() and ((a > 0) & (a < 65535)).any() and (a == 65535).any())
    box, suffix = [x, y, w, h], f"-crop-{w}x{h}.png"

    s0, r0 = prepare(box=box)
    s1, r1 = prepare(box=box, background={k: 0 for k in backdrop.KEYS})
    check("fondo en 0: identico a sin fondo", s0 == s1 == 200 and download(r0["id"]) == download(r1["id"]) and r1["backdrop"] is False)

    for name, extra in {"solo el fondo": {}, "fondo y ajustes": {"adjust": ALL_ON}}.items():
        s, r = prepare(box=box, background=BG_ON, **extra)
        got = decode(download(r["id"])).astype(np.int32)
        eyes = editor_server.blend_eyes(crop, PHOTO, x, y, manifest["intensity"], manifest)
        want = backdrop.render(eyes, x, y, (H, W), layers, adjust.parse(extra.get("adjust")), backdrop.parse(BG_ON)).astype(np.int32)
        diff = np.abs(got - want)
        check(f"{name}: igual a backdrop.render", s == 200 and int(diff.max()) <= 1, f"{s}, {int(diff.max())} niveles")
        check(f"{name}: la gente como sin fondo", s == 200 and np.array_equal(
            got[a == 65535], adjust.adjust_uint16(eyes, adjust.parse(extra.get("adjust")))[a == 65535].astype(np.int32)))
        check(f"{name}: avisa el fondo y el nombre dice ajustado", r.get("backdrop") is True and r["name"] == f"{PHOTO}-adjusted{suffix}", r.get("name"))

    s, r = prepare(box=box, image="raw", background=BG_ON)
    check("el RAW ignora el fondo", s == 200 and r["backdrop"] is False and r["name"] == f"{PHOTO}-raw{suffix}", r.get("name"))


def test_versions() -> None:
    VERSIONS.unlink(missing_ok=True)
    s, hd, data = call("GET", "/api/versions")
    check("versiones: sin archivo, vacio", s == 200 and json.loads(data) == {"photos": {}}, f"{s} {data!r}")
    check("versiones: no-store", hd.get("Cache-Control") == "no-store", str(hd.get("Cache-Control")))

    one, two = state(3), state(1, None)
    s, _, data = call("POST", "/api/versions", {"photo": PHOTO, "state": one})
    check("versiones: guardar", s == 200 and json.loads(data) == {"ok": True}, f"{s} {data!r}")
    s, _, data = call("GET", "/api/versions")
    check("versiones: ida y vuelta", s == 200 and json.loads(data) == {"photos": {PHOTO: one}})
    saved = {PHOTO: one}
    if OTHER:
        s, _, _ = call("POST", "/api/versions", {"photo": OTHER, "state": two})
        s2, _, data = call("GET", "/api/versions")
        saved[OTHER] = two
        check("versiones: guardar otra foto deja la primera", s == s2 == 200 and json.loads(data) == {"photos": saved})

    good = {"photo": PHOTO, "state": one}
    cases = {
        "Host ajeno": (403, dict(headers={"Host": f"evil.example:{PORT}"}, body=good)),
        "Origin ajeno": (403, dict(headers={"Origin": "http://evil.example"}, body=good)),
        "Content-Type": (415, dict(headers={"Content-Type": "text/plain"}, body=good)),
        "mas de 65536 bytes": (413, dict(headers={"Content-Length": "65537"}, raw=b"")),
        "foto desconocida": (400, dict(body={"photo": "NO-SUCH-PHOTO", "state": one})),
        "clave de mas en el estado": (400, dict(body={"photo": PHOTO, "state": one | {"extra": 1}})),
        "clave de mas en el pedido": (400, dict(body=good | {"extra": 1})),
        "activePresetId ajeno": (400, dict(body={"photo": PHOTO, "state": one | {"activePresetId": "preset-zz"}})),
        "41 versiones": (400, dict(body={"photo": PHOTO, "state": state(41)})),
        "valor infinito": (400, dict(raw=json.dumps({"photo": PHOTO, "state": one | {"values": {"a": float("inf")}}}).encode())),
        "JSON roto": (400, dict(raw=b"{nope")),
    }
    for name, (want, kw) in cases.items():
        s, _, data = call("POST", "/api/versions", **kw)
        check(f"versiones rechaza {name}", s == want, f"{s} {data[:80]!r}")
    s, _, data = call("GET", "/api/versions")
    check("versiones: lo rechazado no se guardo", json.loads(data) == {"photos": saved})

    VERSIONS.write_text(f'{{"photos": {{"{PHOTO}": ')  # a medio escribir
    s, _, data = call("GET", "/api/versions")
    check("versiones corruptas: GET da 500 en JSON", s == 500 and "error" in json.loads(data), f"{s}")
    s, _, data = call("POST", "/api/versions", good)
    check("versiones corruptas: POST da 500 y no pisa el archivo",
          s == 500 and VERSIONS.read_text() == f'{{"photos": {{"{PHOTO}": ', f"{s}")
    check("versiones: no quedan temporales", not list(VERSIONS.parent.glob(".versiones-*")))


def main() -> int:
    backup = VERSIONS.read_bytes() if VERSIONS.exists() else None
    env = os.environ | {"MallocLargeCache": "0"}
    log = tempfile.TemporaryFile("w+")  # el log del servidor: solo se muestra si algo fallo
    server = subprocess.Popen(["nice", "-n", "19", sys.executable, str(ROOT / "recipe" / "editor_server.py"), str(PORT)],
                              cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=log)
    try:
        wait_ready(server)
        test_prepare()
        test_backdrop()
        test_versions()
    finally:
        server.terminate()
        try:
            server.wait(10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        if backup is None:
            VERSIONS.unlink(missing_ok=True)
        else:
            VERSIONS.write_bytes(backup)
    if failed:
        log.seek(0)
        print(log.read(), end="")
        print(f"fallaron {len(failed)}: {', '.join(failed)}")
        return 1
    print("todo bien")
    return 0


if __name__ == "__main__":
    sys.exit(main())
