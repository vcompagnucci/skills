// Los tres estilos de recipe/styles.py en el editor: que esten en la lista de cada foto que los tiene, en orden, y que al
// elegirlos con el mouse el panel y el render tomen sus ajustes de luz y color y su fondo (los de cada foto: la
// exposicion del fondo de Bright white cambia de una a otra). Sin "Version 1" en la lista (con versiones guardadas la
// base se esconde) y abriendo en la version puesta. Sin errores en la pagina.
// Uso: node tools/editor_test/styles_check.mjs   (despues de .venv/bin/python recipe/styles.py --seed)
// Arranca su propio servidor (8794) y lo apaga al final. editadas/versiones.json no se toca: se copia a
// work/editor-test/versiones-estilos.json y el servidor guarda ahi (EDITOR_VERSIONS), asi elegir una version no cambia
// la que el fotografo tiene puesta. Deja una captura por estilo en proceso/estilos-editor-*.png.
import { spawn } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { launch } from "./cdp.mjs";

const ROOT = new URL("../../", import.meta.url).pathname;
const PORT = 8794;
const VERSIONS = `${ROOT}work/editor-test/versiones-estilos.json`;
// las de styles.py que siguen en el editor: el fotografo puede borrar alguna (en la sesion original borro Warm beige y
// Dark falloff el 2026-10-19), y borrar una version la saca de todas las fotos
const NAMES = ["Warm beige", "Bright white", "Dark falloff"].filter(n => Object.values(JSON.parse(readFileSync(`${ROOT}editadas/versiones.json`)).photos)
  .some(s => s.presets.some(v => v.name === n)));
const SHOT_ENV = process.env.EDITOR_TEST_PHOTO;  // la foto de las capturas; sin ella, la primera que tiene los estilos

let failures = 0;
const check = (cond, msg, extra = "") => { console.log(cond ? "ok  " : "FAIL", msg, extra); if (!cond) failures++; };

mkdirSync(`${ROOT}work/editor-test`, { recursive: true });
copyFileSync(`${ROOT}editadas/versiones.json`, VERSIONS);  // solo se lee: la prueba trabaja sobre la copia
const expected = JSON.parse(readFileSync(VERSIONS)).photos;
const proc = spawn("nice", ["-n", "19", `${ROOT}.venv/bin/python`, `${ROOT}recipe/editor_server.py`, String(PORT)],
                   { cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: VERSIONS, EDITOR_IMPORTS: `${ROOT}work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"] });
proc.stderr.on("data", () => {});
const exited = new Promise(ok => proc.on("exit", ok));
let page = null;
try {
  await new Promise((ok, fail) => {
    let buf = "";
    proc.stdout.on("data", d => { buf += d; if (buf.includes("Editor en")) ok(); });
    exited.then(c => fail(new Error(`el servidor se cerro (${c}); ¿puerto ocupado?`)));
    setTimeout(() => fail(new Error("el servidor no arranco en 15 s")), 15000);
  });
  page = await launch({ out: `${ROOT}proceso/` });
  const ev = expr => page.eval(expr);
  await page.goto(`http://127.0.0.1:${PORT}/editor.html`);
  await page.waitFor(`frame.classList.contains("ready") && PHOTOS.every(p => [screenUrl(p, "edit"), ...bgUrls(p)].every(renderer.ready))`, 30000);
  const tap = async text => {
    const r = await ev(`(() => { const b = [...$("versions").querySelectorAll(".item")].find(b => b.textContent === ${JSON.stringify(text)});
      b.scrollIntoView({ block: "nearest" }); const r = b.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    await page.click(r.x, r.y);
    await page.waitFor(`$("versions").querySelector('[aria-current="true"]')?.textContent === ${JSON.stringify(text)}`, 5000).catch(() => {});
  };
  // de cada ajuste del panel, su valor plano en versiones.json ("Light.Exposure")
  const LIGHT = { exposure: "Light.Exposure", brightness: "Light.Brightness", contrast: "Light.Contrast", highlights: "Light.Highlights",
                  shadows: "Light.Shadows", whites: "Light.Whites", blacks: "Light.Blacks", temperature: "Color.Temperature",
                  tint: "Color.Tint", vibrance: "Color.Vibrance", saturation: "Color.Saturation" };
  const BACKGROUND = { exposure: "Background.Exposure", evenness: "Background.Evenness", smoothing: "Background.Smoothing", falloff: "Background.Falloff",
                       temperature: "Background.Temperature", tint: "Background.Tint", saturation: "Background.Saturation" };
  // Light y Color se guardan como valor del panel (el punto de partida de la foto, recipe/equivalents.py, mas lo del
  // estilo) y se aplica lo movido: lo aplicado tiene que ser el del estilo, el mismo con que styles.py hizo su maestra
  const same = (got, map, want, start = {}) => Object.entries(map).every(([k, flat]) => Math.abs(got[k] - ((want[flat] ?? start[k] ?? 0) - (start[k] ?? 0))) < 1e-9);

  // solo las fotos que tienen los tres: en una de la sesion original el fotografo dejo seis versiones suyas, sin estos estilos
  const photos = await ev(`PHOTOS.map(p => p.key)`);
  const styled = photos.filter(key => NAMES.every(name => expected[key]?.presets.some(v => v.name === name)));
  const SHOT = SHOT_ENV ?? styled[0];
  check(NAMES.length && styled.includes(SHOT), `fotos con los estilos que quedan (${NAMES.join(", ")}): ${styled.join(", ")}`, `(sin ellos: ${photos.filter(k => !styled.includes(k)).join(", ") || "ninguna"})`);
  for (const [i, key] of photos.entries()) {
    if (!styled.includes(key)) continue;
    await ev(`pickPhoto(${i})`);
    await page.waitFor(`P().key === ${JSON.stringify(key)}`);
    // algunos nombres llevan coma ("Deep blacks, grey wall"): la lista se lee como arreglo
    const rows = await ev(`[...$("versions").querySelectorAll(".item")].map(b => [b.textContent, b.getAttribute("aria-current") === "true"])`);
    const names = rows.map(([n]) => n), shown = rows.map(([n, on]) => n + (on ? "*" : "")).join(" | ");
    const saved = expected[key], puesta = saved.presets.find(v => v.id === saved.activePresetId)?.name ?? saved.presets[0].name;
    const order = NAMES.map(n => names.indexOf(n));
    check(names.join("|") === saved.presets.map(v => v.name).join("|") && !names.includes("Version 1") && order.every((n, j) => n >= 0 && (j === 0 || n > order[j - 1])) &&
          rows.filter(([, on]) => on).map(([n]) => n).join("|") === puesta,
          `${key}: sus versiones en orden (con las tres), sin la base, y abre en la puesta (${puesta})`, shown);
    for (const name of NAMES) {
      await tap(name);
      const want = saved.presets.find(v => v.name === name).values;
      const got = JSON.parse(await ev(`JSON.stringify({ adjust: settings.adjust, background: settings.background, levels: Object.fromEntries(eyeControls(P()).map(([k, face]) => [k, settings.levels[face]])), on: bgU.on })`));
      const ok = same(got.adjust, LIGHT, want, await ev(`startOf(P())`)) && same(got.background, BACKGROUND, want) && Object.entries(got.levels).every(([k, l]) => l === (want[`Under-eyes.${k}`] ?? want["Under-eyes.Intensity"])) && got.on;
      check(ok, `${key}: ${name} pone su luz, su color y su fondo`, ok ? "" : JSON.stringify(got));
      if (key === SHOT) {
        await page.waitFor(`sceneReady(scene(P(), view(), canvas.width))`, 10000);
        // el mouse se queda sobre la version recien elegida y la captura salia con el hover de la lista
        await page.mouse("mouseMoved", (await ev("innerWidth")) / 2, 4);
        await page.shot(`estilos-editor-${name.toLowerCase().replace(/ /g, "-")}`);
      }
    }
    await tap(puesta);  // la copia queda como estaba
  }
  check(page.errors.length === 0, "sin errores en la pagina", page.errors.join(" | "));
} catch (err) {
  failures++;
  console.log("FAIL", err.message);
} finally {
  await page?.close?.();
  if (proc.exitCode === null) proc.kill("SIGTERM");
  await exited;
}
console.log(failures ? `${failures} fallas` : "todo bien");
process.exit(failures ? 1 : 0);
