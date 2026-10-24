// Las versiones son las mismas en todas las fotos (pedido del fotografo, 2026-10-19): guardar en una la suma a todas con sus valores,
// borrar en una la saca de todas, y cada foto conserva sus valores en las que ya tenia. "Copy to other photos" pasa los
// valores de la version que se ve a esa misma version de las otras. Prueba la foto ya abierta (DialKit la retiene en
// memoria) y la que nunca se abrio (sale de sessionStorage), que llega al servidor y que sobrevive a recargar. Tambien
// los tooltips. Light y Color viajan como lo movido desde el punto de partida de cada foto (recipe/equivalents.py): una
// version con Exposure 0.77 en la 0 llega a otra con 0.77 - el de la 0 + el suyo. Servidor propio (8796) con una copia de editadas/versiones.json (EDITOR_VERSIONS): las versiones del
// fotografo no se tocan.
// Uso: node tools/editor_test/apply_version.mjs
import { spawn } from "node:child_process";
import { copyFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";

const ROOT = new URL("../../", import.meta.url).pathname;
const PORT = 8796;
const WORK = `${ROOT}work/apply-version/`;
mkdirSync(WORK, { recursive: true });
copyFileSync(process.env.VERSIONS_FROM ?? `${ROOT}editadas/versiones.json`, `${WORK}versiones.json`);
const require = createRequire(`${process.env.PW_PATH ?? `${process.env.HOME}/.npm/_npx/705bc6b22212b352/node_modules`}/index.js`);
const { chromium } = require("playwright");

let failures = 0;
const check = (cond, msg, extra = "") => { console.log(cond ? "ok  " : "FAIL", msg, extra); if (!cond) failures++; };

const server = spawn("nice", ["-n", "19", ".venv/bin/python", "recipe/editor_server.py", String(PORT)],
  { cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: `${WORK}versiones.json`, EDITOR_IMPORTS: `${ROOT}work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"] });
server.stderr.on("data", () => {});
await new Promise((ok, fail) => { let b = ""; server.stdout.on("data", d => { b += d; if (b.includes("Editor en")) ok(); }); setTimeout(() => fail(new Error("server")), 15000); });

const browser = await chromium.launch({ channel: "chrome" });
try {
  const page = await (await browser.newContext({ viewport: { width: 1470, height: 956 } })).newPage();
  page.on("pageerror", e => check(false, "sin errores de pagina", e.message));
  const open = async () => {
    await page.goto(`http://127.0.0.1:${PORT}/editor.html`, { waitUntil: "networkidle" });
    await page.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
  };
  const at = i => page.evaluate(async i => {
    pickPhoto(i);
    await new Promise(r => setTimeout(r, 300));
    const d = DialKit.DialStore, list = d.getPresets(dial.id);
    return { key: P().key, active: activeVersion(), values: { ...d.snapshots.get(dial.id) }, list: list.map(v => ({ id: v.id, name: v.name, values: v.values })) };
  }, i);
  const ids = s => s.list.map(v => v.id).join();
  // las ojeras van por cara: una cara que la otra foto no tiene (de la de grupo a un retrato) no viaja
  const same = (a, b) => Object.keys(b).every(k => typeof b[k] === "object" || a[k] === b[k] || (k.startsWith("Under-eyes.") && !(k in a)));
  await open();
  const keys = await page.evaluate(() => PHOTOS.map(p => p.key));
  // el valor del panel de la 0 en la foto i, a mano y con moved() (que pasa todas las claves de Light y Color)
  const starts = await page.evaluate(() => PHOTOS.map(p => startOf(p).exposure));
  const expo = (x, i) => +(x - starts[0] + starts[i]).toFixed(2);
  const movedTo = (values, i) => page.evaluate(([v, i]) => moved(v, PHOTOS[0], PHOTOS[i]), [values, i]);

  // la 1 se abre y se deja (queda retenida en memoria); la 2 y la 3 nunca se abren antes de guardar
  await at(1);
  const before = await page.evaluate(() => Object.fromEntries(PHOTOS.map(p => [p.key, JSON.parse(sessionStorage.getItem(storeKey(p.key)))?.presets ?? []])));
  await at(0);
  const made = await page.evaluate(async () => {
    const d = DialKit.DialStore, had = new Set(d.getPresets(dial.id).map(v => v.id));
    d.updateValue(dial.id, "Light.Exposure", 0.77);
    saveVersion();
    await new Promise(r => setTimeout(r, 200));
    const v = d.getPresets(dial.id).find(x => !had.has(x.id));
    return { id: v.id, name: v.name, values: { ...v.values }, toast: await lastToast() };
  });
  check(made.values["Light.Exposure"] === 0.77 && /saved in all photos/.test(made.toast), "guardar: la version nueva guarda Exposure 0.77 y el aviso dice que va a todas", made.toast);
  const src = await at(0);
  for (const i of [1, 2, 3]) {
    const s = await at(i), v = s.list.find(x => x.id === made.id);
    check(ids(s) === ids(src), `guardar ${s.key}: misma lista, mismo orden`);
    check(v && v.name === made.name && same(v.values, await movedTo(made.values, i)) && v.values["Light.Exposure"] === expo(0.77, i), `guardar ${s.key}: la nueva llega con los valores de la que la guardo`);
    const kept = before[s.key].every(o => same(s.list.find(x => x.id === o.id)?.values ?? {}, o.values));
    check(kept, `guardar ${s.key}: sus valores en las que ya tenia quedan intactos`);
  }

  const rows = await page.evaluate(() => [...document.querySelectorAll(".version")].map(r => [...r.querySelectorAll("button.act")].map(b => `${b.className}:${b.dataset.tip}`).join()));
  check(rows.every(r => r === "act more:Rename or delete,act del:Delete from all photos"), "cada fila tiene ⋯ y Delete, y dice que borra en todas", rows[0]);

  // borrar desde otra foto (la 2): sale de todas, y la que la tenia puesta pasa a la primera que queda
  await at(0);
  await page.evaluate(id => pickVersion(id), made.id);  // en la 0 queda puesta la nueva
  await at(2);
  await page.evaluate(id => [...document.querySelectorAll(".version")].find(r => r.querySelector(".item").textContent === DialKit.DialStore.getPresets(dial.id).find(v => v.id === id).name).querySelector(".del").click(), made.id);
  for (const i of [0, 1, 2, 3]) {
    const s = await at(i);
    check(!s.list.some(x => x.id === made.id) && s.list.length === src.list.length - 1, `borrar ${s.key}: no esta mas`);
  }
  const zero = await at(0);
  check(zero.active === zero.list[0].name && same(zero.values, zero.list[0].values), `borrar: la que la tenia puesta (${zero.key}) pasa a la primera, con sus valores`, zero.active);

  // renombrar: clic derecho abre el menu, Rename vuelve el nombre un campo; Enter guarda en todas, Escape no cambia nada,
  // un nombre repetido no entra. Tambien desde el ⋯
  const target = zero.list[1];
  const rename = (how, text, key) => page.evaluate(async ([id, how, text, key]) => {
    const row = () => [...document.querySelectorAll(".version")].find(r => r.dataset.id === id);
    if (how === "right") {
      const r = row().getBoundingClientRect();
      row().querySelector(".item").dispatchEvent(new MouseEvent("contextmenu", { bubbles: true, cancelable: true, clientX: r.left + 30, clientY: r.top + 10 }));
    } else row().querySelector(".act.more").click();
    await new Promise(r => setTimeout(r, 50));
    const menu = $("versionMenu").matches(":popover-open"), focus = document.activeElement?.textContent;
    $("versionMenu").querySelector('[data-do="rename"]').click();
    const field = row().querySelector("input.rename");
    field.value = text;
    field.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true, cancelable: true }));
    await new Promise(r => setTimeout(r, 100));
    return { menu, focus, field: !!field, name: DialKit.DialStore.getPresets(dial.id).find(v => v.id === id).name, toast: await lastToast(),
             shown: row().querySelector(".item")?.textContent };
  }, [target.id, how, text, key]);
  const r1 = await rename("right", "  Studio   white ", "Enter");
  check(r1.menu && r1.focus === "Rename" && r1.field && r1.name === "Studio white" && r1.shown === "Studio white" && /Renamed to Studio white in all photos/.test(r1.toast),
        "renombrar: clic derecho abre el menu con el foco en Rename, y Enter guarda (sin espacios de mas)", JSON.stringify(r1));
  const r2 = await rename("more", "Nope", "Escape");
  check(r2.menu && r2.name === "Studio white" && r2.shown === "Studio white", "renombrar: desde el ⋯, y Escape deja el que estaba", JSON.stringify(r2));
  const r3 = await rename("more", zero.list[0].name, "Enter");
  check(r3.name === "Studio white" && /already exists/.test(r3.toast), "renombrar: un nombre repetido no entra", r3.toast);
  for (const i of [1, 2, 3]) {
    const s = await at(i), v = s.list.find(x => x.id === target.id);
    check(v?.name === "Studio white" && ids(s) === ids(zero), `renombrar ${s.key}: el nombre nuevo, misma lista`);
  }
  await at(0);

  // tooltips: el primero espera, el siguiente sale al instante, y frio vuelve a esperar
  const center = sel => page.evaluate(sel => { const b = typeof sel === "string" ? document.querySelector(sel)
    : [...document.querySelectorAll("aside .dialkit-button")].find(x => x.textContent.trim() === sel.text);
    b.scrollIntoView({ block: "nearest" }); const r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }, sel);
  const tipState = () => page.evaluate(() => ({ open: tip.classList.contains("open"), instant: tip.hasAttribute("data-instant"), text: tip.textContent, op: +getComputedStyle(tip).opacity }));
  const shared = zero.list.find(v => before[keys[1]].some(o => o.id === v.id)) ?? zero.list[0];
  await page.evaluate(id => pickVersion(id), shared.id);
  await page.mouse.move(...await center({ text: "Copy to other photos" }));
  await page.waitForTimeout(300);
  check(!(await tipState()).open, "tooltip: a los 300 ms todavia no");
  await page.waitForTimeout(500);
  const t1 = await tipState();
  // las otras fotos, como las nombra el tooltip: hasta tres por su pestana, y si son mas, cuantas
  const to = await page.evaluate(() => PHOTOS.filter(q => q.key !== P().key).map(q => q.label));
  const list = to.length > 3 ? `the other ${to.length} photos` : to.length > 1 ? `${to.slice(0, -1).join(", ")} and ${to.at(-1)}` : to[0];
  check(t1.open && !t1.instant && t1.text === `Copies these settings to ${shared.name} in ${list}, replacing theirs.`, "tooltip: a los 800 ms aparece, animado, y dice que pisa", t1.text);
  await page.mouse.move(...await center("#zoom"), { steps: 4 });
  await page.waitForTimeout(30);
  const t2 = await tipState();
  check(t2.open && t2.instant && t2.op === 1 && /Zoom/.test(t2.text), "tooltip: el siguiente sale al instante, sin animar", t2.text);
  await page.mouse.move(5, 300); await page.waitForTimeout(900);
  check(!(await tipState()).open && !(await page.evaluate(() => tip.matches(":popover-open"))), "tooltip: al salir se cierra");
  await page.mouse.move(...await center("#zoom"));
  await page.waitForTimeout(150);
  check(!(await tipState()).open, "tooltip: frio, vuelve a esperar");
  await page.mouse.down(); await page.mouse.up(); await page.mouse.move(5, 300);

  // Copy to other photos: los valores de la compartida, en esa misma version de las otras, puesta
  const copied = await page.evaluate(async id => {
    const d = DialKit.DialStore;
    pickVersion(id);
    d.updateValue(dial.id, "Light.Exposure", 0.66);
    await new Promise(r => setTimeout(r, 100));
    [...document.querySelectorAll("aside .dialkit-button")].find(b => b.textContent.trim() === COPY).click();
    return { toast: await lastToast(), values: { ...d.getPresets(dial.id).find(v => v.id === id).values } };
  }, shared.id);
  check(/copied to the other 3 photos/.test(copied.toast) && copied.values["Light.Exposure"] === 0.66, "copiar: el aviso dice a cuantas", copied.toast);
  for (const i of [1, 2, 3]) {
    const s = await at(i), v = s.list.find(x => x.id === shared.id);
    const want = await movedTo(copied.values, i);
    check(s.active === shared.name && same(s.values, want) && same(v.values, want) && v.values["Light.Exposure"] === expo(0.66, i), `copiar ${s.key}: queda puesta con los valores copiados`);
    check(s.list.length === zero.list.length, `copiar ${s.key}: no suma versiones`);
  }

  // llega al servidor: las cuatro con la misma lista
  await page.evaluate(() => flushSaves());
  await page.waitForTimeout(800);
  const saved = await page.evaluate(async () => (await fetch("api/versions")).json());
  const lists = keys.map(k => saved.photos?.[k]?.presets.map(v => v.id).join());
  check(lists.every(l => l === lists[0]) && !lists[0].includes(made.id), "servidor: las cuatro con la misma lista, sin la borrada");
  check(keys.every(k => saved.photos[k].presets.find(v => v.id === zero.list[1].id)?.name === "Studio white"), "servidor: el nombre nuevo en las cuatro");
  for (const k of keys) {
    const st = saved.photos[k], v = st.presets.find(x => x.id === st.activePresetId);
    check(v?.id === shared.id && v.values["Light.Exposure"] === expo(0.66, keys.indexOf(k)), `servidor: ${k} tiene puesta la copiada`, v?.name);
  }

  // y sobrevive a recargar (sessionStorage nuevo desde el servidor)
  await page.evaluate(() => sessionStorage.clear());
  await open();
  for (const i of [3, 2]) {
    const s = await at(i);
    check(s.active === shared.name && s.values["Light.Exposure"] === expo(0.66, i) && ids(s) === lists[0], `${s.key}: despues de recargar sigue igual`, s.active);
  }
} finally {
  await browser.close();
  server.kill("SIGTERM");
}
console.log(failures ? `${failures} FALLAS` : "todo ok");
process.exit(failures ? 1 : 0);
