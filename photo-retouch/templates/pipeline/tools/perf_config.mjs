// Escenarios de emil-performance para el editor. Uso, con el editor abierto en 8775:
//   node <skills>/emil-performance/measure.mjs tools/perf_config.mjs proceso-notas/perf/before.json
//   node <skills>/emil-performance/measure.mjs --table proceso-notas/perf/before.json
export const BASE = "http://127.0.0.1:8775";
const PATH = "/editor.html";
// la medicion nunca escribe: las versiones no llegan a editadas/versiones.json y el servidor no arma exports
// Para comparar un cambio con --vs sin un segundo servidor: poner los dos caminos detras de window.__legacy, prenderlo
// aca con context.addInitScript solo cuando origin === BASE, y pasar el mismo servidor como http://localhost:8775. El
// flag se borra despues de medir
export async function prepareContext(context) {
  await context.route("**/api/versions", route => (route.request().method() === "POST"
    ? route.fulfill({ status: 200, contentType: "application/json", body: '{"ok":true}' }) : route.continue()));
  await context.route("**/api/prepare", route => route.abort());
}
const ready = page => page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
const center = async (page, sel) => { const b = await page.locator(sel).boundingBox(); return [b.x + b.width / 2, b.y + b.height / 2]; };
// lo que hay en la vista previa, en pocos pixeles; en la vista principal (WebGL, sin preserveDrawingBuffer: leerla da
// vacio), su vista y lo que falta cargar. Los globales del editor se leen por nombre: es un script clasico
const sig = (page, id) => page.evaluate(id => {
  if (id === "canvas") return JSON.stringify(view()) + fullPending.size + document.getElementById("loading").classList.contains("show");
  const c = document.getElementById(id), t = document.createElement("canvas");
  t.width = 16; t.height = 16; t.getContext("2d").drawImage(c, 0, 0, 16, 16);
  return c.width + "x" + c.height + ":" + t.getContext("2d").getImageData(0, 0, 16, 16).data.join(",");
}, id);
// espera a que el lienzo deje de cambiar (la foto entera llego y se dibujo): dos lecturas iguales con 1 s de distancia
async function stable(page, id) {
  let a = await sig(page, id);
  for (let i = 0; i < 30; i++) { await page.waitForTimeout(1000); const b = await sig(page, id); if (a === b) return; a = b; }
  throw new Error(`${id} never settled`);
}
async function openExport(page) {
  await ready(page);
  await page.evaluate(() => document.getElementById("export").click());
  await page.waitForFunction(() => document.querySelector("dialog")?.open && document.getElementById("previewCanvas").width > 0, null, { timeout: 60000 });
  await stable(page, "previewCanvas");
}
async function exportAt100(page) {
  await openExport(page);
  await page.evaluate(() => document.getElementById("pvZoom").click());
  await stable(page, "previewCanvas");
  if ((await page.textContent("#pvZoom")).trim() === "Fit") throw new Error("preview did not zoom");
}
// arrastra el borde izquierdo del marco del recorte, ida y vuelta
async function cropDrag(page, n = 240) {
  const b = await page.locator("#previewCanvas").boundingBox(), x = b.x + 1, y = b.y + b.height / 2;
  const before = await page.evaluate(() => localStorage.getItem("studio-export-v1"));
  await page.mouse.move(x, y); await page.mouse.down();
  for (let i = 0; i < n; i++) await page.mouse.move(x + 1 + 60 * Math.sin((i / n) * Math.PI) ** 2, y);
  await page.mouse.move(x + 40, y); await page.mouse.up();
  await page.waitForTimeout(300);
  if ((await page.evaluate(() => localStorage.getItem("studio-export-v1"))) === before) throw new Error("crop drag did nothing");
  return n + 1;
}
export const SCENARIOS = [
  { name: "editor", kind: "idle", path: PATH, prepare: async page => { await ready(page); await stable(page, "canvas"); } },
  { name: "export open", kind: "idle", path: PATH, prepare: openExport },
  { name: "export at 100%", kind: "idle", path: PATH, prepare: exportAt100 },
  {
    name: "main pan", kind: "event", row: "Main view pan at 200%, photo redraw per pointer move", path: PATH,
    prepare: async page => {
      await ready(page); await page.keyboard.press("Meta+="); await page.keyboard.press("Meta+="); await page.keyboard.press("Meta+=");
      await page.waitForTimeout(600); await stable(page, "canvas");
      if ((await page.textContent("#zoom")).trim() === "Fit") throw new Error("main view did not zoom");
    },
    act: async page => {
      const [x, y] = await center(page, "#frame"), n = 240, s0 = await sig(page, "canvas");
      await page.mouse.move(x, y); await page.mouse.down();
      for (let i = 0; i < n; i++) await page.mouse.move(x + 150 * Math.sin((i / n) * Math.PI), y + 60 * Math.sin((i / n) * Math.PI));
      await page.mouse.up(); await page.waitForTimeout(1000);
      if ((await sig(page, "canvas")) === s0) throw new Error("main view did not pan");
      return n;
    },
  },
  {
    name: "main zoom", kind: "frame", gpu: "main view zoom animation", row: "Main view zoom to 100% and back, photo redraw per frame", path: PATH,
    prepare: async page => {  // la entera se carga antes: la fila mide la animacion, no la subida a la placa
      await ready(page);
      await page.evaluate(() => document.getElementById("zoom").click()); await page.waitForTimeout(600); await stable(page, "canvas");
      await page.evaluate(() => document.getElementById("zoom").click()); await page.waitForTimeout(600); await stable(page, "canvas");
    },
    act: async page => {
      await page.evaluate(() => document.getElementById("zoom").click()); await page.waitForTimeout(500);
      if ((await page.textContent("#zoom")).trim() === "Fit") throw new Error("did not zoom in");
      await page.evaluate(() => document.getElementById("zoom").click()); await page.waitForTimeout(500);
      if ((await page.textContent("#zoom")).trim() !== "Fit") throw new Error("did not return to Fit");
    },
  },
  {
    name: "slider", kind: "event", row: "DialKit slider (Exposure, keyboard), photo redraw per key", path: PATH,
    prepare: async page => { await ready(page); await stable(page, "canvas"); await page.locator('[role="slider"][aria-label="Exposure"]').first().focus(); },
    act: async page => {
      const s = page.locator('[role="slider"][aria-label="Exposure"]').first(), v0 = await s.getAttribute("aria-valuenow"), n = 120;
      for (let i = 0; i < n; i++) await page.keyboard.press(i < n / 2 ? "ArrowRight" : "ArrowLeft");
      await page.waitForTimeout(300);
      for (let i = 0; i < 20; i++) await page.keyboard.press("ArrowRight");
      await page.waitForTimeout(500);
      if ((await s.getAttribute("aria-valuenow")) === v0) throw new Error("slider did not move");
      return n + 20;
    },
  },
  { name: "crop drag", kind: "event", row: "Export crop drag, preview redraw per pointer move", path: PATH, prepare: openExport, act: page => cropDrag(page) },
  {
    name: "preview pan", kind: "event", row: "Export preview pan at 100%, preview redraw per wheel event", path: PATH, prepare: exportAt100,
    act: async page => {
      const [x, y] = await center(page, "#previewCanvas"), n = 120, s0 = await sig(page, "previewCanvas");
      await page.mouse.move(x, y);
      for (let i = 0; i < n; i++) await page.mouse.wheel(0, 10);
      await page.waitForTimeout(800);
      if ((await sig(page, "previewCanvas")) === s0) throw new Error("preview did not pan");
      return n;
    },
  },
];
