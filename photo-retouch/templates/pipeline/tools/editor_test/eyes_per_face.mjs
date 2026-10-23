// Ojeras por cara (2026-10-19): mover una cara no toca las otras. En la primera foto de grupo (dos caras o mas), la cara
// de mas a la izquierda al 150 y las demas en la entrega: en pantalla (WebGL leido, sin dither) los recuadros de las
// otras caras quedan identicos a todo en la entrega y el de esa cara cambia; en el archivo del servidor (PNG de 16 bits
// del recuadro de cada cara), lo mismo, y el de esa cara es el mismo archivo que con todas al 150. Un numero solo (una
// pagina vieja) sigue valiendo para todas. Si hay un retrato (una cara) de alguien que esta en la de grupo, copiar del
// retrato a la de grupo cambia solo esa cara.
// Uso: node tools/editor_test/eyes_per_face.mjs   (servidor propio en 8798, con una copia de las versiones)
import { spawn } from "node:child_process";
import { copyFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
const ROOT = new URL("../../", import.meta.url).pathname, PORT = 8798, BASE = `http://127.0.0.1:${PORT}`;
mkdirSync(`${ROOT}work/editor-test`, { recursive: true });
copyFileSync(process.env.VERSIONS_FROM ?? `${ROOT}editadas/versiones.json`, `${ROOT}work/editor-test/versiones-caras.json`);
const require = createRequire(`${process.env.PW_PATH ?? `${process.env.HOME}/.npm/_npx/705bc6b22212b352/node_modules`}/index.js`);
const { chromium } = require("playwright");
const server = spawn("nice", ["-n", "19", ".venv/bin/python", "recipe/editor_server.py", String(PORT)],
  { cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: `${ROOT}work/editor-test/versiones-caras.json`, EDITOR_IMPORTS: `${ROOT}work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"] });
await new Promise(ok => { let b = ""; server.stdout.on("data", d => { b += d; if (b.includes("Editor en")) ok(); }); });
let fails = 0;
const check = (ok, what, detail = "") => { if (!ok) fails++; console.log(`${ok ? "ok  " : "FAIL"} ${what} ${detail}`); };
const browser = await chromium.launch({ channel: "chrome" });
const errors = [];
try {
  const page = await (await browser.newContext({ viewport: { width: 1470, height: 956 }, deviceScaleFactor: 2 })).newPage();
  page.on("pageerror", e => errors.push(e.message));
  await page.goto(`${BASE}/editor.html`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready") && PHOTOS.every(p => eyeUrls(p).every(renderer.ready)), null, { timeout: 60000 });
  // la de grupo y, si hay, un retrato de alguien que esta en ella (las caras se llaman igual en las dos)
  const pick = await page.evaluate(() => {
    const faces = p => [...new Set((p.eyes ?? []).map(e => e.face))];
    const group = PHOTOS.findIndex(p => faces(p).length > 1), gf = group < 0 ? [] : faces(PHOTOS[group]);
    const solo = PHOTOS.findIndex(p => faces(p).length === 1 && gf.includes(faces(p)[0]));
    return { group, solo, key: PHOTOS[group]?.key, soloFace: solo < 0 ? null : faces(PHOTOS[solo])[0] };
  });
  if (pick.group < 0) throw new Error("hace falta una foto con dos caras o mas, con sus ojeras inventariadas");
  const controls = await page.evaluate(group => { pickPhoto(group); return [...new Map(eyeControls(P()).map(([name, face]) => [face, name]))]; }, pick.group);
  const MOVED = controls[0][0], MOVED_NAME = controls[0][1];  // la cara de mas a la izquierda
  const labels = await page.evaluate(n => [...document.querySelectorAll("#controls .dialkit-slider")].slice(0, n).map(s => s.getAttribute("aria-label")).join(), controls.length);
  check(labels === controls.map(([, name]) => name).join(), `${pick.key}: un control por cara, de izquierda a derecha`, labels);
  // en pantalla: la foto entera leida, con todas en la entrega y con una cara al 150
  const screen = await page.evaluate(moved => {
    const p = P(), v = view(), W = canvas.width, H = canvas.height, k = W / v.size, x0 = v.cx - v.size / 2, y0 = v.cy - (v.size * p.h) / p.w / 2;
    const keep = settings, all = n => Object.fromEntries(p.eyes.map(e => [e.face, n]));
    const at = levels => { settings = { ...keep, levels }; return renderer.read(scene(p, v, W, { dither: false }), W, H).slice(); };
    const base = at(all(EYE_DEFAULT)), changed = at({ ...all(EYE_DEFAULT), [moved]: 150 });
    settings = keep;
    return p.eyes.map(e => {
      const L = Math.floor((e.x - x0) * k), T = Math.floor((e.y - y0) * k), R = Math.ceil((e.x + e.w - x0) * k), B = Math.ceil((e.y + e.h - y0) * k);
      let max = 0;
      for (let y = T; y < B; y++) for (let x = L; x < R; x++) for (let c = 0; c < 3; c++) max = Math.max(max, Math.abs(changed[(y * W + x) * 4 + c] - base[(y * W + x) * 4 + c]));
      return [e.face, max];
    });
  }, MOVED);
  for (const [face, max] of screen)
    check(face === MOVED ? max > 0 : max === 0, `pantalla, ${face}: ${face === MOVED ? "cambia" : "identica"} con ${MOVED_NAME} al 150`, `(max ${max})`);
  // copiar de un retrato (una cara) a la de grupo: esa cara toma el valor y las otras quedan con lo suyo
  if (pick.solo >= 0) {
    const set = Object.fromEntries(controls.map(([face], i) => [face, 33 + 11 * i]));
    const copied = await page.evaluate(async ([group, solo, values, soloName]) => {
      pickPhoto(group);
      const id = store.getActivePresetId(dial.id);
      dial.setValues({ "Under-eyes": values });
      await new Promise(r => setTimeout(r, 100));
      pickPhoto(solo);
      store.loadPreset(dial.id, id);
      dial.setValues({ "Under-eyes": { [soloName]: 150 } });
      await new Promise(r => setTimeout(r, 100));
      copyToOthers();
      pickPhoto(group);
      return settings.levels;
    }, [pick.group, pick.solo, Object.fromEntries(controls.map(([face, name]) => [name, set[face]])), controls.find(([f]) => f === pick.soloFace)[1]]);
    const want = { ...set, [pick.soloFace]: 150 };
    check(Object.keys(want).every(f => copied[f] === want[f]), `copiar del retrato a la de grupo: ${pick.soloFace} toma el valor, las otras quedan`, JSON.stringify(copied));
  } else console.log("     (sin un retrato de alguien de la de grupo: no se prueba copiar)");
  // el archivo: el recuadro de cada cara, PNG de 16 bits del servidor
  const file = (box, under_eyes) => page.evaluate(async ([box, under_eyes, KEY]) => {
    const r = await fetch("api/prepare", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ photo: KEY, image: "edit", box, size: "full", format: "png", under_eyes, adjust: null, background: null, version: null }) });
    if (!r.ok) return `HTTP ${r.status}`;
    const j = await r.json(), buf = new Uint8Array(await (await fetch(`api/file/${j.id}`)).arrayBuffer());
    let h = 0; for (const b of buf) h = (h * 31 + b) >>> 0;
    return `${buf.length}:${h}`;
  }, [box, under_eyes, pick.key]);
  const eyes = await page.evaluate(() => P().eyes.map(e => [e.face, [e.x, e.y, e.w, e.h]]));
  const all = n => Object.fromEntries(eyes.map(([f]) => [f, n]));
  for (const [face, box] of eyes) {
    const base = await file(box, all(70)), moved = await file(box, { ...all(70), [MOVED]: 150 }), max = await file(box, all(150)), old = await file(box, 70);
    if (face === MOVED) check(moved !== base && moved === max, `archivo, ${face}: cambia, y es el mismo que con todas al 150`);
    else check(moved === base, `archivo, ${face}: el mismo que con todas en la entrega`);
    check(old === base, `archivo, ${face}: un numero solo (pagina vieja) vale para todas`);
  }
  const bad = await file(eyes[0][1], { [MOVED]: 150 });
  check(bad === "HTTP 400", "faltan caras: 400", bad);
} finally { await browser.close(); server.kill("SIGTERM"); }
check(!errors.length, "sin errores en la pagina", errors.join(" | "));
console.log(fails ? `${fails} fallas` : "todo bien");
process.exit(fails ? 1 : 0);
