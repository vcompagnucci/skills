// ¿El archivo que se descarga es lo que se ve en el editor? Por foto, con su version puesta (la de editadas/versiones.json),
// la foto entera a 2048 de lado largo (el editor la dibuja como a Fit: texturas de pantalla) contra el export de 2048.
// Cuatro dibujos del editor, para separar las causas:
//   seen        como lo dibuja el editor: texturas de pantalla y dither
//   seenNoDith  igual, sin dither
//   full        con las texturas enteras (foto y capa del fondo), sin dither: el shader contra Python a esa escala
// y el archivo: WebP sin perdida (8 bits exactos del de 16) a 2048, y el Full achicado a 2048 por el navegador.
// Zonas por el alpha de la capa del fondo: pared pura (A = 0), gente (A = 255) y borde (lo demas).
// Nada en JPG; el servidor es propio (8797) y guarda versiones en una copia (EDITOR_VERSIONS).
// Uso: MallocLargeCache=0 nice -n 19 node tools/download_parity.mjs
// Salida: proceso/download-parity-<foto>.png (|editor - archivo| x 10, pared en azul tenue), numeros en
// proceso-notas/download-parity/parity.json.
import { spawn } from "node:child_process";
import { copyFileSync, mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const ROOT = new URL("../", import.meta.url).pathname;
const PORT = 8797;
const WORK = `${ROOT}work/download-parity/`;
const NOTES = `${ROOT}proceso-notas/download-parity/`;
mkdirSync(WORK, { recursive: true }); mkdirSync(NOTES, { recursive: true });
copyFileSync(`${ROOT}editadas/versiones.json`, `${WORK}versiones.json`);
const require = createRequire(`${process.env.PW_PATH ?? `${process.env.HOME}/.npm/_npx/705bc6b22212b352/node_modules`}/index.js`);
const { chromium } = require("playwright");

const server = spawn("nice", ["-n", "19", ".venv/bin/python", "recipe/editor_server.py", String(PORT)],
  { cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: `${WORK}versiones.json`, EDITOR_IMPORTS: `${ROOT}work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"] });
server.stderr.on("data", () => {});
await new Promise((ok, fail) => { let b = ""; server.stdout.on("data", d => { b += d; if (b.includes("Editor en")) ok(); }); setTimeout(() => fail(new Error("server")), 15000); });

const browser = await chromium.launch({ channel: "chrome" });
const results = {};
try {
  const page = await (await browser.newContext({ viewport: { width: 1470, height: 956 }, deviceScaleFactor: 2 })).newPage();
  page.on("pageerror", e => console.log("pageerror", e.message));
  await page.goto(`http://127.0.0.1:${PORT}/editor.html`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
  for (let i = 0; i < 4; i++) {
    const r = await page.evaluate(async i => {
      const wait = ms => new Promise(r => setTimeout(r, ms));
      pickPhoto(i);
      while (!frame.classList.contains("ready") || holding) await wait(100);
      await wait(800);
      const p = P(), L = 2048, W = Math.round(p.w * L / Math.max(p.w, p.h)), H = Math.round(p.h * L / Math.max(p.w, p.h)), v = fitView(p), look = liveLook();
      const ver = activeVersion();
      // texturas: las de pantalla ya estan; las enteras se piden
      loadFull(p, true);
      const need = () => [fullUrl(p, "edit"), fullUrl(p, "raw"), layerUrl(p, true), lightUrl(p), layerUrl(p, false)];
      while (!need().every(u => renderer.ready(u))) await wait(150);
      const drawn = opts => { const s = scene(p, v, W, { look, ...opts }); if (!sceneReady(s)) throw new Error("no listo"); return s; };
      const sScreen = drawn({ dither: true });
      if (sScreen.full) throw new Error("a Fit no deberia usar la entera");
      const seen = renderer.read(sScreen, W, H).slice();
      const seenNoDith = renderer.read(drawn({ dither: false }), W, H).slice();
      const sFull = { ...drawn({ dither: false }), full: true, edit: fullUrl(p, "edit"), raw: fullUrl(p, "raw"),
                      layer: sScreen.bg.on ? layerUrl(p, true) : null };
      const full = renderer.read(sFull, W, H).slice();
      // el archivo: lo mismo que pide Download, con la foto entera
      const base = { ...request(), box: [0, 0, p.w, p.h] };
      const get = async body => {
        const meta = await (await fetch("api/prepare", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json();
        if (!meta.id) throw new Error("prepare: " + JSON.stringify(meta) + " " + JSON.stringify(body));
        const blob = await (await fetch("api/file/" + meta.id)).blob();
        if (!blob.type.startsWith("image/")) throw new Error("file: " + blob.type + " " + blob.size);
        const bmp = await createImageBitmap(blob, { colorSpaceConversion: "none", premultiplyAlpha: "none" });
        return { meta, bmp };
      };
      const asPixels = (bmp, w, h, smooth) => {
        const c = new OffscreenCanvas(w, h).getContext("2d", { colorSpace: "srgb" });
        c.imageSmoothingEnabled = smooth; c.imageSmoothingQuality = "high";
        c.drawImage(bmp, 0, 0, w, h);
        return c.getImageData(0, 0, w, h).data;
      };
      const webp = await get({ ...base, size: L, format: "webp" });
      const file = asPixels(webp.bmp, W, H, false);
      // el archivo Full, achicado por el navegador en gamma, como lo haria un visor (WebP: Chrome no decodifica un PNG de
      // 16 bits de este tamano)
      const png = await get({ ...base, size: "full", format: "webp" });
      const pngDown = asPixels(png.bmp, W, H, true);
      // zonas, del alpha de la capa de pantalla a este tamano
      const layerBlob = await (await fetch(layerUrl(p, false))).blob();
      const layerBmp = await createImageBitmap(layerBlob, { colorSpaceConversion: "none", premultiplyAlpha: "none" }).catch(e => { throw new Error("layer " + layerBlob.size + " " + e.message); });
      const alpha = asPixels(layerBmp, W, H, true);
      const zoneOf = j => (alpha[j + 3] === 0 ? "wall" : alpha[j + 3] === 255 ? "people" : "edge");
      const stats = (a, b) => {
        const z = { wall: [0, 0, 0, 0, []], people: [0, 0, 0, 0, []], edge: [0, 0, 0, 0, []], all: [0, 0, 0, 0, []] };
        for (let j = 0; j < a.length; j += 4) {
          const d = (a[j] - b[j] + a[j + 1] - b[j + 1] + a[j + 2] - b[j + 2]) / 3, ad = Math.abs(d);
          for (const k of [zoneOf(j), "all"]) { const s = z[k]; s[0]++; s[1] += ad; s[2] += d; s[3] = Math.max(s[3], ad); if ((j >> 2) % 7 === 0) s[4].push(ad); }
        }
        const out = {};
        for (const [k, [n, sum, bias, max, sample]] of Object.entries(z)) {
          sample.sort((x, y) => x - y);
          out[k] = n ? { px: n, mean: +(sum / n).toFixed(3), bias: +(bias / n).toFixed(3), p99: +sample[Math.floor(sample.length * 0.99)].toFixed(2), max: +max.toFixed(1) } : null;
        }
        return out;
      };
      // escalones del papel: niveles distintos de luma en la pared pura, y el salto mas grande entre vecinos de una fila
      const banding = a => {
        const levels = new Set(); let step = 0;
        for (let y = 0; y < H; y++) for (let x = 1; x < W; x++) {
          const j = (y * W + x) * 4, k = j - 4;
          if (alpha[j + 3] !== 0 || alpha[k + 3] !== 0) continue;
          const l = Math.round((a[j] * 54 + a[j + 1] * 183 + a[j + 2] * 19) / 256); levels.add(l);
          step = Math.max(step, Math.abs(l - Math.round((a[k] * 54 + a[k + 1] * 183 + a[k + 2] * 19) / 256)));
        }
        return { levels: levels.size, maxStep: step };
      };
      // mapa: |seen - file| x 10 en gris, la pared pura apenas azul para ubicarse
      const map = new OffscreenCanvas(W, H), mc = map.getContext("2d"), img = mc.createImageData(W, H);
      for (let j = 0; j < seen.length; j += 4) {
        const d = Math.min(255, 10 * (Math.abs(seen[j] - file[j]) + Math.abs(seen[j + 1] - file[j + 1]) + Math.abs(seen[j + 2] - file[j + 2])) / 3);
        const wall = alpha[j + 3] === 0;
        img.data[j] = d; img.data[j + 1] = d; img.data[j + 2] = wall ? Math.max(d, 40) : d; img.data[j + 3] = 255;
      }
      mc.putImageData(img, 0, 0);
      const mapUrl = await new Promise(async ok => { const r = new FileReader(); r.onload = () => ok(r.result); r.readAsDataURL(await map.convertToBlob({ type: "image/png" })); });
      return {
        photo: p.key, version: ver, size: [W, H], bg: sScreen.bg.on, file: webp.meta.name, fullFile: png.meta.name,
        seenVsFile: stats(seen, file), noDitherVsFile: stats(seenNoDith, file), fullVsFile: stats(full, file),
        seenVsScreenNoDither: stats(seen, seenNoDith), seenVsPngShrunkByBrowser: stats(seen, pngDown),
        bandingWall: { seen: banding(seen), file: banding(file) }, mapUrl,
      };
    }, i);
    writeFileSync(`${ROOT}proceso/download-parity-${r.photo}.png`, Buffer.from(r.mapUrl.split(",")[1], "base64"));
    delete r.mapUrl;
    results[r.photo] = r;
    const f = (o, z) => `${o[z].mean}/${o[z].bias}/${o[z].p99}/${o[z].max}`;
    console.log(r.photo, r.version, r.size.join("x"), "seen vs file wall", f(r.seenVsFile, "wall"), "people", f(r.seenVsFile, "people"), "edge", f(r.seenVsFile, "edge"),
                "| full vs file wall", f(r.fullVsFile, "wall"), "edge", f(r.fullVsFile, "edge"), "| banding", JSON.stringify(r.bandingWall));
  }
} finally {
  await browser.close();
  server.kill("SIGTERM");
}
writeFileSync(`${NOTES}parity.json`, JSON.stringify(results, null, 1));
