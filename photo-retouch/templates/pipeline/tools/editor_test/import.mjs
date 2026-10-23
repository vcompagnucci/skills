// Sumar fotos al editor, de punta a punta en Chrome: el + (un RAW de verdad, un TIFF de 16 bits y un HEIC), soltar un
// PNG sobre la ventana, y lo que se rechaza (un .txt y un JPG, que este proyecto no acepta). Por cada una: la pestana
// muestra el paso, al terminar se abre con un click, el panel tiene lo que corresponde (sin Under-eyes; Background solo
// con pared de estudio), los ajustes llegan al dibujo, el export sale con los pixeles nativos, y Save version y Copy to
// other photos andan con ella.
// Servidor propio (8794): versiones, registro y originales en work/import-e2e/ (EDITOR_VERSIONS, EDITOR_IMPORTS,
// EDITOR_ORIGINALS). Lo que se genera en editadas/ con las claves de prueba se borra al final.
// Uso: MallocLargeCache=0 nice -n 19 node tools/editor_test/import.mjs
import { spawn, execFileSync } from "node:child_process";
import { copyFileSync, mkdirSync, rmSync, readFileSync, existsSync, readdirSync, unlinkSync } from "node:fs";
import { createRequire } from "node:module";

const ROOT = new URL("../../", import.meta.url).pathname;
const PORT = 8794;
const WORK = `${ROOT}work/import-e2e/`;
rmSync(WORK, { recursive: true, force: true });
mkdirSync(`${WORK}originales`, { recursive: true }); mkdirSync(`${WORK}in`, { recursive: true });
copyFileSync(`${ROOT}editadas/versiones.json`, `${WORK}versiones.json`);
const require = createRequire(`${process.env.PW_PATH ?? `${process.env.HOME}/.npm/_npx/705bc6b22212b352/node_modules`}/index.js`);
const { chromium } = require("playwright");

let failures = 0;
const check = (cond, msg, extra = "") => { console.log(cond ? "ok  " : "FAIL", msg, extra); if (!cond) failures++; };

// los archivos de entrada: un RAW de la sesion con otro nombre, y dos imagenes sinteticas (sin pared). El RAW es
// EDITOR_TEST_RAW (un nombre de originales/) o el primero de originales/; tiene que tener pared de estudio. Si su nombre
// termina en numeros (como los de las camaras: XXXX1234), la copia se llama TEST1234 y su pestana corta diria lo mismo
// que la de la sesion: la prueba mira que entonces muestre la clave entera
const RAW = process.env.EDITOR_TEST_RAW ?? readdirSync(`${ROOT}originales`).find(f => /\.(raf|nef|cr2|cr3|arw|dng|orf|rw2)$/i.test(f));
const DIGITS = RAW.match(/(\d{3,5})\.[^.]+$/)?.[1];
const TEST = `TEST${DIGITS ?? "RAW"}`;
const TEST_FILE = `${TEST}${RAW.slice(RAW.lastIndexOf("."))}`;
execFileSync("cp", ["-c", `${ROOT}originales/${RAW}`, `${WORK}in/${TEST_FILE}`]);
execFileSync(`${ROOT}.venv/bin/python`, ["-c", `
import numpy as np, tifffile
from PIL import Image
h, w = 900, 1400
y, x = np.mgrid[0:h, 0:w]
a = np.stack([x / w, y / h, 0.5 + 0.4 * np.sin(x / 40)], -1)
tifffile.imwrite("${WORK}in/test-tiff16.tif", (a * 65535).astype(np.uint16), photometric="rgb")
Image.fromarray((a[::-1] * 255).astype(np.uint8)).save("${WORK}in/test-heic-src.png")
# 16 bits en Display P3 (se convierte a sRGB en 16) y 8 bits en sRGB (tienen que quedar sus mismos 8 bits)
p3 = open("/System/Library/ColorSync/Profiles/Display P3.icc", "rb").read()
tifffile.imwrite("${WORK}in/test-p3.tif", (a * 65535).astype(np.uint16), photometric="rgb", iccprofile=p3)
Image.fromarray((np.random.default_rng(3).random((500, 700, 3)) * 255).astype(np.uint8)).save("${WORK}in/test-srgb8.png")
`]);
execFileSync("sips", ["-s", "format", "heic", `${WORK}in/test-heic-src.png`, "--out", `${WORK}in/test-heic.heic`], { stdio: "ignore" });

const server = spawn("nice", ["-n", "19", ".venv/bin/python", "recipe/editor_server.py", String(PORT)], {
  cwd: ROOT, stdio: ["ignore", "pipe", "pipe"],
  env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: `${WORK}versiones.json`, EDITOR_IMPORTS: `${WORK}importadas.json`, EDITOR_ORIGINALS: `${WORK}originales` },
});
server.stderr.on("data", () => {});
await new Promise((ok, fail) => { let b = ""; server.stdout.on("data", d => { b += d; if (b.includes("Editor en")) ok(); }); setTimeout(() => fail(new Error("server")), 15000); });

const keys = [];
const browser = await chromium.launch({ channel: "chrome" });
try {
  const page = await (await browser.newContext({ viewport: { width: 1470, height: 956 } })).newPage();
  page.on("pageerror", e => check(false, "sin errores de pagina", e.message));
  const open = async () => {
    await page.goto(`http://127.0.0.1:${PORT}/editor.html`, { waitUntil: "networkidle" });
    await page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
  };
  await open();
  const N0 = await page.evaluate(() => PHOTOS.length);  // las de la sesion
  check(N0 > 0, `arranca con las de la sesion (${N0})`);
  check(await page.evaluate(() => { const o = PHOTOS.filter(p => p.key !== P().key).map(p => p.label); return o.length > 3 || o.every(l => copyTip().includes(l)); }),
        "hasta cuatro, Copy to other photos nombra a las otras");
  check(await page.evaluate(() => $("actions").firstElementChild.getAttribute("aria-label") === "Add photos" && $("actions").lastElementChild === $("export") && !$("photos").querySelector(".add")),
        "el + esta aparte, al lado de Export");

  // lo que no se acepta: el servidor lo dice y el editor lo muestra
  for (const [name, want] of [["notes.txt", /isn't an image/], ["photo.jpg", /JPG is off/]]) {
    const r = await page.evaluate(async name => {
      const res = await fetch(`api/import?name=${encodeURIComponent(name)}`, { method: "POST", headers: { "Content-Type": "application/octet-stream" }, body: new Blob(["x"]) });
      return { status: res.status, error: (await res.json()).error };
    }, name);
    check(r.status === 400 && want.test(r.error), `${name}: se rechaza con un motivo`, r.error);
  }
  check(!existsSync(`${WORK}importadas.json`) || !/notes|photo/.test(readFileSync(`${WORK}importadas.json`, "utf8")), "lo rechazado no queda en el registro");

  // el +: tres archivos
  await page.setInputFiles("#addFiles", [`${WORK}in/${TEST_FILE}`, `${WORK}in/test-tiff16.tif`, `${WORK}in/test-heic.heic`, `${WORK}in/test-p3.tif`, `${WORK}in/test-srgb8.png`]);
  await page.waitForFunction(() => document.querySelectorAll(".photos .pending").length === 5, null, { timeout: 30000 });
  const steps = new Set();
  // soltar un PNG hecho en la pagina sobre la ventana
  await page.evaluate(async () => {
    const c = new OffscreenCanvas(800, 600), g = c.getContext("2d");
    const grad = g.createLinearGradient(0, 0, 800, 600); grad.addColorStop(0, "#c33"); grad.addColorStop(1, "#33c");
    g.fillStyle = grad; g.fillRect(0, 0, 800, 600);
    const file = new File([await c.convertToBlob({ type: "image/png" })], "dropped.png", { type: "image/png" });
    const dt = new DataTransfer(); dt.items.add(file);
    dispatchEvent(new DragEvent("dragenter", { dataTransfer: dt }));
    const shown = $("drop").classList.contains("show");
    dispatchEvent(new DragEvent("drop", { dataTransfer: dt, cancelable: true }));
    window.__dropShown = shown;
  });
  check(await page.evaluate(() => window.__dropShown), "al arrastrar archivos aparece Drop to add photos");
  await page.waitForFunction(() => document.querySelectorAll(".photos .pending").length === 6, null, { timeout: 30000 });
  // esperar a las cuatro, anotando los pasos que se ven
  const t0 = Date.now();
  while (Date.now() - t0 < 600000) {
    const st = await page.evaluate(() => [...document.querySelectorAll(".photos .pending")].map(b => [b.dataset.state, b.textContent]));
    st.forEach(([, t]) => steps.add(t.split(" · ")[1]));
    if (st.every(([s]) => s === "done" || s === "failed")) break;
    await page.waitForTimeout(500);
  }
  const final = await page.evaluate(() => [...document.querySelectorAll(".photos .pending")].map(b => ({ state: b.dataset.state, text: b.textContent, tip: b.dataset.tip })));
  console.log("     pasos vistos:", [...steps].join(", "), `(${Math.round((Date.now() - t0) / 1000)} s)`);
  check(final.length === 6 && final.every(f => f.state === "done"), "las seis terminan", JSON.stringify(final.filter(f => f.state !== "done")));
  check(steps.has("Developing") && steps.has("Separating the wall"), "la pestana muestra en que paso esta");
  const reg = JSON.parse(readFileSync(`${WORK}importadas.json`, "utf8")).photos;
  keys.push(...Object.keys(reg));
  check(reg[TEST]?.wall === true && reg[TEST]?.white_balance === "wall", "el RAW de estudio: balance en la pared y fondo", JSON.stringify(reg[TEST]));
  check(reg["test-tiff16"]?.bits === 16 && reg["test-tiff16"]?.wall === false, "el TIFF de 16 bits entra en 16 y sin fondo");
  check(reg["test-heic"]?.ready && reg.dropped?.ready, "el HEIC y el PNG soltado tambien");
  check(reg["test-p3"]?.bits === 16, "el TIFF en Display P3 pasa a sRGB en 16 bits", JSON.stringify(reg["test-p3"]));
  const exact = execFileSync(`${ROOT}.venv/bin/python`, ["-c", `
import numpy as np
from PIL import Image
a = np.asarray(Image.open("${WORK}in/test-srgb8.png")); b = np.asarray(Image.open("${ROOT}editadas/test-srgb8.png").convert("RGB"))
import tifffile; t = tifffile.imread("${ROOT}editadas/test-srgb8.tif")
print(int((a != b).sum()), int((t != a.astype(np.uint16) * 257).sum()))`]).toString().trim();
  check(exact === "0 0" && reg["test-srgb8"]?.bits === 8, "el PNG de 8 bits en sRGB queda con sus mismos pixeles (PNG y TIFF)", exact);

  // abrir una: click en su pestana -> recarga con ella puesta
  await Promise.all([page.waitForEvent("load"), page.evaluate(() => [...document.querySelectorAll(".photos .pending")].find(b => b.textContent.startsWith(TEST)).click())]);
  await page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
  const opened = await page.evaluate(() => ({ n: PHOTOS.length, key: P().key, pend: document.querySelectorAll(".photos .pending").length,
    folders: Object.keys(configFor(P())), top: P().top, tabs: [...$("photos").querySelectorAll("button:not(.add)")].map(b => b.textContent) }));
  check(opened.n === N0 + 6 && opened.key === TEST && (!DIGITS || opened.tabs.filter(t => t === DIGITS).length === 1) && opened.tabs.includes(TEST) && opened.pend === 0,
        `al abrirla: ${N0 + 6} fotos, la nueva puesta (${TEST}${DIGITS ? `, no otra ${DIGITS}` : ""}) y sin pestanas pendientes`, JSON.stringify(opened.tabs));
  check(!opened.folders.includes("Under-eyes") && opened.folders.includes("Background") && opened.top != null, "el RAW: sin Under-eyes, con Background", opened.folders.join());

  for (const key of [TEST, "test-tiff16", "test-heic", "test-p3", "test-srgb8", "dropped"]) {
    const r = await page.evaluate(async key => {
      const wait = ms => new Promise(r => setTimeout(r, ms));
      pickPhoto(PHOTOS.findIndex(p => p.key === key));
      while (!frame.classList.contains("ready") || holding) await wait(100);
      const p = P(), d = DialKit.DialStore;
      const read = () => { const s = scene(p, fitView(p), 400, { look: liveLook(), dither: false }); return sceneReady(s) ? renderer.read(s, 400, Math.round(400 * p.h / p.w)).slice() : null; };
      await wait(300);
      const a = read();
      // un paso entero desde donde este: la foto abre en una version heredada, que ya puede tener Exposure en 0.5
      const e0 = d.snapshots.get(dial.id)["Light.Exposure"] ?? 0;
      d.updateValue(dial.id, "Light.Exposure", e0 > 0 ? e0 - 1 : e0 + 1);
      await wait(300);
      const b = read();
      let moved = 0;
      if (a && b) for (let i = 0; i < a.length; i += 4) moved += Math.abs(a[i] - b[i]);
      const body = { ...request(), box: [0, 0, p.w, p.h], size: "full", format: "png" };
      const meta = await (await fetch("api/prepare", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json();
      d.updateValue(dial.id, "Light.Exposure", e0);
      return { w: p.w, h: p.h, folders: Object.keys(configFor(p)), moved: a && b ? moved / (a.length / 4) : -1, meta };
    }, key);
    check(r.moved > 5, `${key}: Exposure mueve el dibujo`, r.moved.toFixed?.(1));
    check(r.meta.w === r.w && r.meta.h === r.h, `${key}: el export sale a ${r.w}x${r.h}`, JSON.stringify(r.meta).slice(0, 160));
    if (key !== TEST) check(!r.folders.includes("Background") && !r.folders.includes("Under-eyes"), `${key}: sin Background ni Under-eyes`, r.folders.join());
  }
  // el TIFF de 16 bits rotado no; el HEIC se dio vuelta arriba-abajo en el origen: la miniatura dice si quedo derecho
  const heicTop = await page.evaluate(async () => {
    const img = new Image(); img.src = `editadas/pantalla/test-heic.png?v=${DATA.version}`; await img.decode();
    const c = new OffscreenCanvas(img.width, img.height).getContext("2d"); c.drawImage(img, 0, 0);
    return [c.getImageData(5, 5, 1, 1).data[1], c.getImageData(5, img.height - 5, 1, 1).data[1]];
  });
  check(heicTop[0] > heicTop[1], "el HEIC conserva su orientacion (verde arriba)", heicTop.join(" vs "));

  // versiones con una importada: llega con la lista de las demas, y guardar y copiar llegan a todas
  const lists = await page.evaluate(() => PHOTOS.map(p => JSON.stringify((JSON.parse(sessionStorage.getItem(storeKey(p.key)))?.presets ?? []).map(v => v.id))));
  check(lists[0] !== "[]" && lists.every(l => l === lists[0]), "las importadas abren con las mismas versiones que las demas", `${new Set(lists).size} listas`);
  const v = await page.evaluate(async () => {
    pickPhoto(PHOTOS.findIndex(p => p.key === "test-tiff16"));
    await new Promise(r => setTimeout(r, 300));
    DialKit.DialStore.updateValue(dial.id, "Light.Contrast", 33);
    saveVersion();
    const d = DialKit.DialStore, made = d.getPresets(dial.id).at(-1);
    pickVersion(made.id);
    [...document.querySelectorAll("aside .dialkit-button")].find(b => b.textContent.trim() === COPY).click();
    const t = await lastToast();
    pickPhoto(0);  // la primera de la sesion
    await new Promise(r => setTimeout(r, 300));
    return { t, active: activeVersion(), contrast: d.snapshots.get(dial.id)["Light.Contrast"], has: d.getPresets(dial.id).some(x => x.id === made.id) };
  });
  check(v.t.includes(`copied to the other ${N0 + 5} photos`) && v.contrast === 33 && v.has, "Save version y Copy to other photos desde una importada", `${v.t} · ${v.active}`);

  // un reinicio del servidor no las pierde
  check(await page.evaluate(async () => (await (await fetch("editor.html")).text()).includes('"key": "dropped"')), "la pagina las trae sin volver a armar editor.html");
} finally {
  await browser.close();
  server.kill("SIGTERM");
  // lo que dejaron las claves de prueba en editadas/ y work/
  const dirs = [`${ROOT}editadas/`, `${ROOT}editadas/pantalla/`, `${ROOT}editadas/miniaturas/`, `${ROOT}editadas/fondo/`, `${ROOT}work/`, `${ROOT}work/imports/`, `${ROOT}work/estilos/`];
  let removed = 0;
  for (const d of dirs) if (existsSync(d)) for (const f of readdirSync(d)) if (keys.some(k => f === k || f.startsWith(`${k}-`) || f.startsWith(`${k}.`))) { unlinkSync(d + f); removed++; }
  console.log(`     limpieza: ${removed} archivos de prueba`);
}
console.log(failures ? `${failures} FALLAS` : "todo ok");
process.exit(failures ? 1 : 0);
