// Prueba funcional del editor en Chrome, WebKit y Firefox: cada funcion una vez por celda (motor x pantalla), con una
// comprobacion de que paso de verdad. Uso, desde la carpeta del proyecto:
//   nice -n 19 node tools/editor_test/browsers.mjs [motor] [WxH]      (sin argumentos, la matriz entera)
// Levanta sus propios servidores en 8795 y 8796 con EDITOR_VERSIONS apuntando a una copia en work/: nunca escribe
// editadas/versiones.json. Las descargas van a work/editor-test-browsers/downloads y se borran al final. El cuarto formato
// (el de 8 bits con perdida) nunca se baja a disco: se arma con /api/prepare y se lee en memoria.
// Resultados en proceso-notas/editor-test/browsers.json; capturas en proceso/browsers-<motor>-<WxH>-<que>.png
import { spawn } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const WORK = join(ROOT, "work/editor-test-browsers"), DOWNLOADS = join(WORK, "downloads"), VERSIONS = join(WORK, "versiones.json");
const OUT = join(ROOT, "proceso-notas/editor-test/browsers.json"), SHOTS = join(ROOT, "proceso");
const PORTS = [8795, 8796], BASE = `http://127.0.0.1:${PORTS[0]}`;
// la version de Playwright que corresponde a los navegadores instalados (webkit-2336, firefox-1538)
const PW = process.env.PW_PATH ?? join(homedir(), ".npm/_npx/705bc6b22212b352/node_modules");
const pw = createRequire(join(PW, "index.js"))("playwright");
const PW_VERSION = JSON.parse(readFileSync(join(PW, "playwright/package.json"), "utf8")).version;

const ENGINES = [
  { name: "chrome", type: pw.chromium, launch: { channel: "chrome" } },
  { name: "webkit", type: pw.webkit, launch: {} },
  { name: "firefox", type: pw.firefox, launch: {} },
];
const VIEWPORTS = [
  { width: 1470, height: 956, dpr: 2 }, { width: 1280, height: 800, dpr: 2 },
  { width: 2560, height: 1440, dpr: 1 }, { width: 1024, height: 700, dpr: 2 },
  { width: 1470, height: 956, dpr: 2, reduced: true },
];
const [onlyEngine, onlyVp] = process.argv.slice(2);

// --- servidores propios -------------------------------------------------------
const servers = [];
function stopServers() { for (const s of servers) if (s.exitCode === null) s.kill("SIGTERM"); }
process.on("exit", stopServers);
for (const sig of ["SIGINT", "SIGTERM"]) process.on(sig, () => { stopServers(); process.exit(1); });
async function startServers() {
  for (const port of PORTS) {
    const busy = await fetch(`http://127.0.0.1:${port}/api/versions`).then(() => true, () => false);
    if (busy) throw new Error(`port ${port} is taken`);
  }
  for (const port of PORTS) {
    const log = join(WORK, `server-${port}.log`);
    writeFileSync(log, "");
    const s = spawn("nice", ["-n", "19", ".venv/bin/python", "recipe/editor_server.py", String(port)], {
      cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: VERSIONS, EDITOR_IMPORTS: `${ROOT}/work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"],
    });
    const append = d => writeFileSync(log, d, { flag: "a" });
    s.stdout.on("data", append); s.stderr.on("data", append);
    servers.push(s);
  }
  for (const port of PORTS) {
    for (let i = 0; ; i++) {
      if (await fetch(`http://127.0.0.1:${port}/api/versions`).then(r => r.ok, () => false)) break;
      if (i > 100) throw new Error(`server ${port} did not start`);
      await new Promise(r => setTimeout(r, 100));
    }
  }
}

// --- una celda ------------------------------------------------------------------
const IDLE = `frame.classList.contains("ready") && fullPending.size === 0 && !$("loading").classList.contains("show") && animTarget === null && drag === null && splitDrag === null`;
const MAGIC = { png: [0x89, 0x50, 0x4e, 0x47], tif: null, webp: [0x52, 0x49, 0x46, 0x46] };
const SUMMARY = /^(\d+) × (\d+) · (\d+)-bit (\S+) · sRGB(?: · ([\d.]+ [KM]B))?/;

async function runCell(browser, engine, vp) {
  const tag = `${engine}-${vp.width}x${vp.height}${vp.reduced ? "-reduced" : ""}`;
  const cell = { engine, viewport: `${vp.width}x${vp.height}@${vp.dpr}`, reducedMotion: !!vp.reduced, checks: [], errors: [], wheel: {} };
  const t0 = Date.now();
  let phase = "load", shots = 0;
  copyFileSync(join(ROOT, "editadas/versiones.json"), VERSIONS);  // cada celda arranca de las versiones de verdad
  const context = await browser.newContext({
    viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: vp.dpr, acceptDownloads: true,
    reducedMotion: vp.reduced ? "reduce" : "no-preference",
  });
  // cada rueda que llega, leida como la lee el editor (deltaY antes que deltaMode: en Firefox leer deltaMode primero
  // cambia las unidades), y si alguien le hizo preventDefault
  await context.addInitScript(() => {
    window.__wheels = [];
    addEventListener("wheel", e => {
      const dy = e.deltaY, dx = e.deltaX;
      __wheels.push({ dy, dx, mode: e.deltaMode, ctrl: e.ctrlKey, meta: e.metaKey, prevented: e.defaultPrevented, trusted: e.isTrusted });
    }, { passive: true });
  });
  const page = await context.newPage();
  page.on("console", m => { if (m.type() === "error") cell.errors.push({ phase, kind: "console", text: m.text() }); });
  page.on("pageerror", e => cell.errors.push({ phase, kind: "pageerror", text: String(e.message) }));
  // nada que no sea PNG, TIFF o WebP llega a disco
  page.on("download", d => {
    if (!/\.(png|tif|webp)$/.test(d.suggestedFilename())) { d.cancel(); check("guard: unexpected download cancelled", false, d.suggestedFilename()); }
  });

  const ev = (expr, arg) => (typeof expr === "string" ? page.evaluate(expr) : page.evaluate(expr, arg));
  const until = (expr, timeout = 15000) => page.waitForFunction(expr, null, { timeout, polling: 50 }).then(() => true, () => false);
  const idle = (timeout = 30000) => until(IDLE, timeout);
  const blur = () => ev(`document.activeElement?.blur()`);
  const wait = ms => page.waitForTimeout(ms);
  function check(name, ok, detail = "", level = "native") {
    cell.checks.push({ name, ok: !!ok, detail: typeof detail === "string" ? detail : JSON.stringify(detail), ...(level !== "native" ? { level } : {}) });
  }
  async function shot(what) {
    if (shots >= 4) return;
    shots++;
    await page.screenshot({ path: join(SHOTS, `browsers-${tag}-${what}.png`) }).catch(() => {});
  }
  async function step(name, fn) {
    phase = name;
    try { await fn(); } catch (e) {
      check(`${name}: threw`, false, String(e.message).split("\n")[0]);
      await shot(`fail-${name.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}`);
      await page.keyboard.up("Control").catch(() => {}); await page.mouse.up().catch(() => {});
    }
  }
  const pageOk = async () => {
    const s = await ev(`[scrollX, scrollY, document.scrollingElement.scrollTop, visualViewport.scale, innerWidth, devicePixelRatio].join()`);
    return { ok: s === `0,0,0,1,${vp.width},${vp.dpr}`, s };
  };
  const zoomText = () => page.textContent("#zoom").then(t => t.trim());
  // el punto de la foto bajo un punto de la pantalla, y cuantos pixeles de la foto hay por pixel de pantalla
  const photoAt = (x, y) => ev(([x, y]) => {
    const r = frame.getBoundingClientRect(), v = view(), k = v.size / r.width;
    return [v.cx + (x - r.left - r.width / 2) * k, v.cy + (y - r.top - r.height / 2) * k, k];
  }, [x, y]);
  const frameBox = () => page.locator("#frame").boundingBox();
  const lastWheel = () => ev(`__wheels.at(-1) ?? null`);
  async function settled(timeout = 6000) {  // la vista quieta (tambien la inercia, que no marca animTarget) y adentro
    const t = Date.now();
    let a = await ev(`JSON.stringify(view())`);
    while (Date.now() - t < timeout) {
      await wait(150);
      const b = await ev(`JSON.stringify(view())`);
      if (a === b && await ev(IDLE)) return true;
      a = b;
    }
    return false;
  }

  try {
    // 1. carga: WebGL dibuja, sin errores
    await step("load", async () => {
      await page.goto(`${BASE}/editor.html`);
      const ready = await until(`document.querySelector("#frame")?.classList.contains("ready")`, 60000);
      await idle();
      const gl = await ev(`[!!renderer, renderer && renderer.gl.getError(), size.w, frame.style.width, canvas.width, Math.round(size.w * dpr())].join()`);
      const [has, err, w, fw, cw, want] = gl.split(",");
      check("load: #frame.ready", ready);
      check("load: WebGL2 renderer, gl.getError() 0", has === "true" && err === "0", gl);
      check("load: frame and canvas sized to fit", fw === `${w}px` && cw === want && Number(w) > 0, gl);
      check("load: no console errors or page errors", !cell.errors.length, cell.errors.map(e => e.text).join(" | "));
      // cada dibujo del lienzo principal, para ver que lo que se mueve llega al render
      await ev(`window.__draws = 0; window.__last = null; { const d = renderer.draw; renderer.draw = (s, t, c) => { if (!t) { __draws++; __last = { show: s.show, on: s.adjust.on, gain: s.adjust.gain, clip: c }; } return d(s, t, c); }; }`);
      if (vp.reduced) check("reduced motion: matchMedia matches", await ev(`matchMedia("(prefers-reduced-motion: reduce)").matches`));
    });

    // 2. cambiar de foto: boton y ← →
    await step("photo switch", async () => {
      await page.click("#photos button:nth-child(2)");
      await idle();
      const a = await ev(`[state.photo, $("photos").children[1].getAttribute("aria-pressed"), frame.classList.contains("ready")].join()`);
      check("photo: button switches", a === "1,true,true", a);
      await blur();
      await page.keyboard.press("ArrowRight"); await idle();
      const r = await ev(`state.photo`);
      await page.keyboard.press("ArrowLeft"); await idle();
      const l = await ev(`state.photo`);
      check("photo: → and ← switch", r === 2 && l === 1, `${r},${l}`);
      await page.click("#photos button:nth-child(1)"); await idle();
      check("photo: back to the first", await ev(`state.photo`) === 0);
    });

    // 3. RAW
    await step("raw view", async () => {
      await page.click("#rawView");
      const on = await ev(`[mode(), $("rawView").getAttribute("aria-pressed"), $("controls").inert, __last?.show].join()`);
      await page.click("#rawView");
      const off = await ev(`[mode(), $("rawView").getAttribute("aria-pressed"), $("controls").inert, __last?.show].join()`);
      check("RAW: toggles on (panel inert, RAW drawn) and off", on === "raw,true,true,1" && off === "edit,false,false,0", `${on} / ${off}`);
    });

    // 4. Espacio: solo sobre la version
    const peekCheck = async label => {
      await blur();
      await page.keyboard.down("Space");
      const held = await ev(`[state.peek, __last?.show, getComputedStyle($("peekKey")).display].join()`);
      await page.keyboard.up("Space");
      const after = await ev(`[state.peek, __last?.show].join()`);
      return { held, after, label };
    };
    await step("space", async () => {
      const e = await peekCheck("edit");
      check("Space in edit: RAW while held, released after", e.held.startsWith("true,1,") && e.after === "false,0" && !e.held.endsWith("none"), e);
      await page.click("#rawView");
      const r = await peekCheck("raw");
      check("Space in RAW: nothing, #peekKey display none", r.held === "false,1,none" && r.after === "false,1", r);
      await page.click("#rawView");
    });

    // 5. antes y despues
    await step("before/after", async () => {
      await page.click("#compareView");
      check("Before/after: on", await ev(`mode() === "compare" && frame.classList.contains("compare")`));
      const s = await peekCheck("compare");
      check("Space in Before/after: nothing, #peekKey display none", s.held.startsWith("false,") && s.held.endsWith(",none") && s.after.startsWith("false"), s);
      // la barra, arrastrada desde la manija
      const k = await page.locator("#knob").boundingBox(), f = await frameBox();
      await page.mouse.move(k.x + k.width / 2, k.y + k.height / 2); await page.mouse.down();
      for (let i = 1; i <= 6; i++) await page.mouse.move(k.x + k.width / 2 + ((f.x + f.width * 0.25) - (k.x + k.width / 2)) * i / 6, k.y + k.height / 2);
      await page.mouse.up();
      const dragged = await ev(`[state.split.toFixed(3), $("knob").getAttribute("aria-valuenow"), __last?.clip?.join("-")].join()`);
      check("Before/after: split drag", Math.abs(Number(dragged.split(",")[0]) - 0.25) < 0.02, dragged);
      // un clic lejos con la foto entera: la barra viene (con movimiento reducido, de una)
      await page.mouse.click(f.x + f.width * 0.8, f.y + f.height * 0.5);
      const now = await ev(`state.split`);
      await wait(250);
      const later = await ev(`state.split`);
      check("Before/after: click far moves the split there", Math.abs(later - 0.8) < 0.02, `${now.toFixed(3)} → ${later.toFixed(3)}`);
      if (vp.reduced) check("reduced motion: split jumps without glide", Math.abs(now - 0.8) < 0.02, now.toFixed(3));
      await page.focus("#knob");
      const k0 = await ev(`state.split`);
      await page.keyboard.press("ArrowLeft");
      const k1 = await ev(`state.split`);
      await page.keyboard.press("Shift+ArrowLeft");
      const k2 = await ev(`[state.split, state.photo].join()`);
      check("Before/after: knob ← and Shift+← (photo unchanged)", Math.abs(k0 - k1 - 0.02) < 1e-6 && Math.abs(k1 - Number(k2.split(",")[0]) - 0.1) < 1e-6 && k2.endsWith(",0"), `${k0} ${k1} ${k2}`);
      await ev(`state.split = 0.5; paintSplit(); draw()`);
      await shot("compare");
      // el menu del antes con el mouse
      await page.click("#beforePick");
      await until(`$("beforeMenu").matches(":popover-open") && $("beforeMenu").contains(document.activeElement)`, 3000);
      const open = await ev(`[$("beforeMenu").matches(":popover-open"), $("beforePick").getAttribute("aria-expanded"), $("beforeMenu").contains(document.activeElement)].join()`);
      check("before menu: opens on click, focus inside", open === "true,true,true", open);
      const want = await ev(`$("beforeMenu").children[1].dataset.value`);
      await page.click("#beforeMenu [role=menuitemradio]:nth-child(2)");
      const chose = await ev(`[$("beforeMenu").matches(":popover-open"), state.before[P().key], $("beforeName").textContent].join("|")`);
      check("before menu: mouse choice applies and closes", chose.startsWith(`false|${want}|`), chose);
      // con el teclado: Enter abre, ↓ baja, Enter elige; Escape cierra
      await page.focus("#beforePick"); await page.keyboard.press("Enter");
      await until(`$("beforeMenu").matches(":popover-open") && $("beforeMenu").contains(document.activeElement)`, 3000);
      const kOpen = await ev(`$("beforeMenu").matches(":popover-open")`);
      await page.keyboard.press("ArrowDown"); await page.keyboard.press("Enter");
      await until(`!$("beforeMenu").matches(":popover-open")`, 3000);
      const kChose = await ev(`[$("beforeMenu").matches(":popover-open"), state.before[P().key] ?? "raw"].join("|")`);
      await page.focus("#beforePick"); await page.keyboard.press("Enter");
      await until(`$("beforeMenu").matches(":popover-open") && $("beforeMenu").contains(document.activeElement)`, 3000);
      const reOpen = await ev(`$("beforeMenu").matches(":popover-open")`);
      await page.keyboard.press("Escape");
      await until(`!$("beforeMenu").matches(":popover-open")`, 3000);
      const esc = await ev(`[$("beforeMenu").matches(":popover-open"), document.activeElement?.id].join()`);
      check("before menu: keyboard Enter/↓/Enter chooses, Escape closes", kOpen && reOpen && kChose.startsWith("false|") && kChose.split("|")[1] !== want && esc.startsWith("false"),
            `${kOpen} ${kChose} ${reOpen} ${esc}`);
      // ↓ ↑ recorren las versiones
      await blur();
      const v0 = await ev(`store.getActivePresetId(dial.id)`);
      // con la ultima puesta, ↓ no tiene adonde ir: primero ↑ y despues ↓
      const last = await ev(`store.getPresets(dial.id).at(-1)?.id === store.getActivePresetId(dial.id)`);
      await page.keyboard.press(last ? "ArrowUp" : "ArrowDown");
      const v1 = await ev(`store.getActivePresetId(dial.id)`);
      await page.keyboard.press(last ? "ArrowDown" : "ArrowUp");
      const v2 = await ev(`store.getActivePresetId(dial.id)`);
      check("↓/↑ walk the versions", v1 !== v0 && v2 === v0 && v1, `${v0} → ${v1} → ${v2}`);
      await page.click("#compareView");
      check("Before/after: off", await ev(`mode()`) === "edit");
    });

    // 6. zoom de la foto
    await step("main zoom", async () => {
      await idle();
      const f = await frameBox(), x = f.x + f.width * 0.4, y = f.y + f.height * 0.45;
      const before = await photoAt(x, y), s0 = await ev(`view().size`);
      await page.mouse.move(x, y);
      await page.keyboard.down("Control"); await page.mouse.wheel(0, -100); await page.keyboard.up("Control");
      let w = await lastWheel(), level = "native";
      if (!w?.ctrl) {  // el motor no mando ctrlKey con la rueda: el evento a mano
        level = "handler-level";
        await ev(([x, y]) => $("canvas").dispatchEvent(new WheelEvent("wheel", { deltaY: -100, ctrlKey: true, clientX: x, clientY: y, bubbles: true, cancelable: true })), [x, y]);
        w = await lastWheel();
      }
      const s1 = await ev(`view().size`), mid = await photoAt(x, y);
      await settled();
      const after = await photoAt(x, y);
      cell.wheel.ctrlZoom = { received: w, sizeRatio: +(s0 / s1).toFixed(3), level };
      check("ctrl+wheel zooms in at the pointer", s1 < s0 * 0.9 && Math.hypot(mid[0] - before[0], mid[1] - before[1]) < mid[2] * 1.5 && (await zoomText()) !== "Fit",
            { before: before.map(Math.round), mid: mid.map(Math.round), after: after.map(Math.round), ratio: (s0 / s1).toFixed(2), z: await zoomText() }, level);
      check("ctrl+wheel: preventDefault (page does not zoom)", w?.prevented && (await pageOk()).ok, { w, page: (await pageOk()).s }, level);
      // la rueda sola desplaza
      const c0 = await ev(`view()`);
      await page.mouse.wheel(0, 100);
      const pw0 = await lastWheel(), c1 = await ev(`view()`);
      cell.wheel.plainPan = { received: pw0, panCssPx: +((c1.cy - c0.cy) / mid[2]).toFixed(1), panPhotoPx: +(c1.cy - c0.cy).toFixed(1) };
      check("plain wheel pans (preventDefault, page still)", c1.cy > c0.cy && pw0?.prevented && (await pageOk()).ok, cell.wheel.plainPan);
      // con lo que manda una rueda en modo lineas (deltaMode 1, 3 lineas por muesca): lo que hace el editor con eso
      const l0 = await ev(`view()`);
      await ev(([x, y]) => $("canvas").dispatchEvent(new WheelEvent("wheel", { deltaY: 3, deltaMode: 1, clientX: x, clientY: y, bubbles: true, cancelable: true })), [x, y]);
      const l1 = await ev(`view()`);
      await ev(([x, y]) => $("canvas").dispatchEvent(new WheelEvent("wheel", { deltaY: -3, deltaMode: 1, ctrlKey: true, clientX: x, clientY: y, bubbles: true, cancelable: true })), [x, y]);
      const l2 = await ev(`view()`);
      cell.wheel.lineMode = { level: "handler-level", panCssPxPerNotch: +((l1.cy - l0.cy) / mid[2]).toFixed(2), zoomRatioPerNotch: +(l1.size / l2.size).toFixed(4) };
      await settled();
      await page.keyboard.press("Meta+Digit0"); await settled();
      check("⌘0 back to Fit", (await zoomText()) === "Fit");
      // el boton y el doble clic: al 100 % y de vuelta
      await page.click("#zoom"); await settled();
      const b1 = await zoomText();
      await page.click("#zoom"); await settled();
      const b2 = await zoomText();
      check("#zoom button: Fit → 100% → Fit", b1 === "100%" && b2 === "Fit", `${b1} ${b2}`);
      await page.mouse.dblclick(f.x + f.width / 2, f.y + f.height / 2); await settled();
      const d1 = await zoomText();
      await page.mouse.dblclick(f.x + f.width / 2, f.y + f.height / 2); await settled();
      const d2 = await zoomText();
      check("dblclick: Fit → 100% → Fit", d1 === "100%" && d2 === "Fit", `${d1} ${d2}`);
      // ⌘+ ⌘− ⌘0
      await blur();
      await page.keyboard.press("Meta+Equal"); await settled();
      const p1 = await zoomText();
      await page.keyboard.press("Meta+Equal"); await settled();
      const p2 = await zoomText();
      await page.keyboard.press("Meta+Minus"); await settled();
      const m1 = await zoomText();
      await page.keyboard.press("Meta+Digit0"); await settled();
      const z0 = await zoomText();
      check("⌘+ ⌘+ ⌘− ⌘0 step through the zoom stops", p1 !== "Fit" && parseInt(p2) > parseInt(p1) && m1 === p1 && z0 === "Fit" && (await pageOk()).ok, `${p1} ${p2} ${m1} ${z0}`);
      // arrastrar con inercia, y que quede adentro
      await page.mouse.dblclick(f.x + f.width / 2, f.y + f.height / 2); await settled();
      await page.keyboard.press("Meta+Equal"); await settled();  // 200 %
      const g0 = await ev(`view()`), cx = f.x + f.width / 2, cy = f.y + f.height / 2;
      await page.mouse.move(cx, cy); await page.mouse.down();
      for (let i = 1; i <= 8; i++) await page.mouse.move(cx - 25 * i, cy - 12 * i);
      await page.mouse.up();
      const g1 = await ev(`view()`);
      await wait(120);
      const g2 = await ev(`view()`);
      const ok = await settled(8000);
      const g3 = await ev(`[JSON.stringify(view()) === JSON.stringify(clampView(view())), drag === null].join()`);
      check("drag pans, keeps moving after release (inertia), settles inside bounds", g1.cx > g0.cx && g2.cx > g1.cx && ok && g3 === "true,true",
            { dragPhotoPx: Math.round(g1.cx - g0.cx), inertiaPhotoPx: Math.round(g2.cx - g1.cx), settled: ok, inside: g3 });
      await page.keyboard.press("Meta+Digit0"); await settled();
      // pellizco de Safari: gesture* a mano (no se puede generar de verdad)
      if (engine === "webkit") {
        const q0 = await ev(`view().size`);
        await ev(([x, y]) => {
          const mk = (type, scale) => { const e = new Event(type, { bubbles: true, cancelable: true }); Object.assign(e, { scale, clientX: x, clientY: y }); return e; };
          $("canvas").dispatchEvent(mk("gesturestart", 1)); $("canvas").dispatchEvent(mk("gesturechange", 2)); $("canvas").dispatchEvent(mk("gestureend", 2));
        }, [f.x + f.width / 2, f.y + f.height / 2]);
        const q1 = await ev(`view().size`);
        await settled();
        check("WebKit gesturechange scale 2 halves the view", Math.abs(q0 / q1 - 2) < 0.05 && (await pageOk()).ok, `${q0} → ${q1}`, "handler-level");
        await page.keyboard.press("Meta+Digit0"); await settled();
      }
      check("page never scrolled or zoomed (main view)", (await pageOk()).ok, (await pageOk()).s);
    });

    // 7. DialKit
    const slider = label => page.locator(`#controls .dialkit-slider[aria-label="${label}"]`).first();
    const tapButton = text => page.locator("#controls .dialkit-button", { hasText: text }).first().click();
    await step("dialkit", async () => {
      await tapButton("Reset");
      check("Reset zeroes the panel", await ev(`Object.values(settings.adjust).every(v => v === 0) && !uniforms.on`));
      const head = page.locator("#controls .dialkit-folder-header-top", { hasText: "Light" }).first();
      const content = `(() => { const t = [...document.querySelectorAll("#controls .dialkit-folder-header-top")].find(f => f.textContent.trim() === "Light"); return [t.getAttribute("aria-expanded"), t.closest(".dialkit-folder").querySelector(".dialkit-folder-content").inert].join(); })()`;
      await head.click(); await wait(500);
      const shut = await ev(content);
      await head.click(); await wait(600);
      const back = await ev(content);
      check("folder collapses and expands", shut === "false,true" && back === "true,false", `${shut} / ${back}`);
      // arrastrar Exposure
      const s = slider("Exposure"); await s.scrollIntoViewIfNeeded();
      const b = await s.boundingBox();
      const e0 = await ev(`settings.adjust.exposure`), d0 = await ev(`__draws`);
      await page.mouse.move(b.x + b.width * 0.5, b.y + b.height / 2); await page.mouse.down();
      for (let i = 1; i <= 6; i++) await page.mouse.move(b.x + b.width * (0.5 + 0.04 * i), b.y + b.height / 2);
      await page.mouse.up(); await wait(300);
      const e1 = await ev(`[settings.adjust.exposure, uniforms.on, __last?.on, __draws > ${d0}].join()`);
      check("slider drag moves Exposure and reaches the render", Number(e1.split(",")[0]) > e0 && e1.endsWith("true,true,true"), e1);
      // las flechas sobre Contrast
      await slider("Contrast").focus();
      await page.keyboard.press("ArrowRight"); await page.keyboard.press("ArrowRight");
      // el control dice el valor del panel; lo que se aplica es la diferencia con el punto de partida (recipe/equivalents.py)
      const c = await ev(`[settings.adjust.contrast, document.querySelector('#controls .dialkit-slider[aria-label="Contrast"]').getAttribute("aria-valuenow") - startOf(P()).contrast, state.photo].join()`);
      check("arrow keys move Contrast (not the photo)", Number(c.split(",")[0]) > 0 && c.split(",")[0] === c.split(",")[1] && c.endsWith(",0"), c);
      // clic en el numero para escribirlo (DialKit lo habilita despues de 800 ms con el puntero encima)
      const value = s.locator(".dialkit-slider-value");
      await value.hover(); await wait(950); await value.click();
      const typing = await ev(`document.activeElement?.classList.contains("dialkit-slider-input")`);
      await page.keyboard.press("Meta+a"); await page.keyboard.type("0.5"); await page.keyboard.press("Enter");
      await wait(300);
      // 0.5 es el valor del panel: se aplica 0.5 menos el punto de partida
      const typed = await ev(`[settings.adjust.exposure, __last?.gain.map(g => g.toFixed(3)).join("/")].join(" ")`);
      const delta = await ev(`+(0.5 - startOf(P()).exposure).toFixed(2)`);
      const want = (await ev(`adjustUniforms({ ...settings.adjust, exposure: ${delta} }).gain.map(g => g.toFixed(3)).join("/")`));
      check("click-to-type sets Exposure 0.5 and the shader gets its gain", typing && typed === `${delta} ${want}`, `${typing} ${typed} want ${delta} ${want}`);
      await tapButton("Reset"); await wait(500);
    });

    // 8. versiones
    await step("versions", async () => {
      const names = () => ev(`store.getPresets(dial.id).map(v => v.name)`);
      const n0 = await names(), active0 = await ev(`activeVersion()`);
      await tapButton("Save version");
      const n1 = await names(), made = n1.find(n => !n0.includes(n));
      const t = await ev(`lastToast()`);
      check("Save version adds one and stays on the current one", n1.length === n0.length + 1 && made && t === `${made} saved in all photos` && await ev(`activeVersion()`) === active0, `${made} · ${t}`);
      await page.locator("#versions .item", { hasText: made }).first().click();
      check("clicking a version shows it", await ev(`activeVersion()`) === made);
      await wait(900);
      const key = await ev(`P().key`), onDisk = () => JSON.parse(readFileSync(VERSIONS, "utf8")).photos[key].presets.map(v => v.name);
      check("saved to the server copy (EDITOR_VERSIONS)", onDisk().includes(made));
      await page.reload(); await until(`document.querySelector("#frame")?.classList.contains("ready")`, 60000); await idle();
      check("reload keeps the version", (await names()).includes(made));
      const other = await context.newPage();
      await other.goto(`http://127.0.0.1:${PORTS[1]}/editor.html`);
      await other.waitForFunction(() => document.querySelector("#frame")?.classList.contains("ready"), null, { timeout: 60000 });
      const there = await other.evaluate(`store.getPresets(dial.id).map(v => v.name)`);
      await other.close();
      check("the second port sees it", there.includes(made));
      // borrar la que se ve pasa a la primera que queda
      await page.locator("#versions .item", { hasText: made }).first().click();
      const row = page.locator("#versions .version", { has: page.locator(".item", { hasText: made }) }).first();
      await row.hover(); await row.locator(".del").click();
      await wait(900);
      const n2 = await names(), act = await ev(`activeVersion()`);
      check("delete removes it and shows the first remaining", !n2.includes(made) && n2.length === n0.length && act === n2[0] && !onDisk().includes(made), `${act} · ${n2.length}`);
      await ev(`window.__draws = 0; window.__last = null; { const d = renderer.draw; renderer.draw = (s, t, c) => { if (!t) { __draws++; __last = { show: s.show, on: s.adjust.on, gain: s.adjust.gain, clip: c }; } return d(s, t, c); }; }`);
      await tapButton("Reset"); await wait(500);  // el export sin fondo: cada pedido sale rapido
    });

    // 9. export
    const dlg = `[dialog.open, getComputedStyle(dialog).opacity, getComputedStyle(dialog).display, $("previewCanvas").width > 0, $("export").getAttribute("aria-expanded")].join()`;
    const openDialog = async () => {
      await page.click("#export");
      await until(`dialog.open && $("previewCanvas").width > 0 && getComputedStyle(dialog).opacity === "1"`, 30000);
    };
    const closed = () => until(`!dialog.open && getComputedStyle(dialog).display === "none"`, 3000);
    const summary = async (withBytes = true) => {
      if (withBytes) await until(`/sRGB · [\\d.]+ [KM]B/.test($("info").textContent) || $("foot").dataset.state === "warn"`, 60000);
      const [text, dims, req] = await ev(`[$("info").textContent, outDims(), request()]`);
      return { text, dims, req, m: text.match(SUMMARY) };
    };
    const cropScreen = () => ev(() => {
      const pc = $("previewCanvas"), r = pc.getBoundingClientRect(), G = pvGeom(), k = dpr() / G.z, [X, Y, W, H] = box();
      return { x: r.left + (X - G.x0) / k, y: r.top + (Y - G.y0) / k, w: W / k, h: H / k, box: box() };
    });
    const dragBy = async (x, y, dx, dy) => {
      await page.mouse.move(x, y); await page.mouse.down();
      for (let i = 1; i <= 5; i++) await page.mouse.move(x + dx * i / 5, y + dy * i / 5);
      await page.mouse.up(); await wait(100);
    };
    // la guia de la foto de perfil (2026-10-23) y Flip (2026-10-20), con clics y teclas de verdad
    await step("guide and flip", async () => {
      const guide = () => ev(`(() => { const m = document.querySelector(".mask"), a = getComputedStyle(m, "::after"), f = frame.getBoundingClientRect(), side = Math.min(f.width, f.height);
        return [getComputedStyle(m).opacity, a.borderTopLeftRadius, Math.abs(parseFloat(a.width) - side) < 1 && Math.abs(parseFloat(a.height) - side) < 1].join(); })()`);
      await page.click("#guide button:nth-child(2)"); await wait(300);
      const circle = await guide();
      await page.click("#guide button:nth-child(3)"); await wait(300);
      const square = await guide();
      await page.click("#guide button:nth-child(1)"); await wait(300);
      const off = await guide();
      check("guide: Circle and Square, the largest centered fit; Off hides it", circle === "1,50%,true" && square === "1,0px,true" && off.startsWith("0,"), `${circle} / ${square} / ${off}`);
      await page.click("#flip");
      const on = await ev(`[$("flip").getAttribute("aria-pressed"), flipped(), scene(P(), view(), 64).mirror].join()`);
      await blur();
      await page.keyboard.press("f");
      const back = await ev(`[$("flip").getAttribute("aria-pressed"), flipped(), scene(P(), view(), 64).mirror].join()`);
      check("Flip: the button mirrors the photo, F turns it back", on === "true,true,true" && back === "false,false,false", `${on} / ${back}`);
    });
    await step("export dialog", async () => {
      phase = "export";
      await openDialog();
      const o = await ev(dlg);
      check("export opens (open, opacity 1, preview drawn)", o.startsWith("true,1,") && o.endsWith(",true,true"), o);
      if (vp.reduced) check("reduced motion: dialog transition is 0s", await ev(`getComputedStyle(dialog).transitionDuration.split(",").every(d => parseFloat(d) === 0)`), await ev(`getComputedStyle(dialog).transitionDuration`));
      await page.click("#close");
      check("closes by X", await closed(), await ev(dlg));
      await openDialog(); await page.keyboard.press("Escape");
      check("closes by Escape", await closed(), await ev(dlg));
      await openDialog(); await page.mouse.click(5, 5);
      check("closes by backdrop click", await closed(), await ev(dlg));
      await openDialog();
    });
    await step("export options", async () => {
      // Size primero (1024): los formatos se arman rapido
      await page.click("#size button:nth-child(1)");
      for (let i = 0; i < 4; i++) {
        await page.click(`#format button:nth-child(${i + 1})`);
        const f = await ev(`FORMATS[${i}]`), s = await summary();
        const ok = s.m && Number(s.m[1]) === s.dims[0] && Number(s.m[2]) === s.dims[1] && Number(s.m[3]) === f.bits && s.m[4] === f.label && s.m[5] && s.req.format === f.id;
        check(`Format ${f.label}: summary and request`, ok && await ev(`$("format").children[${i}].getAttribute("aria-pressed")`) === "true", s.text);
      }
      await page.click("#format button:nth-child(1)");
      const sizes = await ev(`SIZES`);
      for (let i = 0; i < sizes.length; i++) {
        if (await ev(`$("size").children[${i}].disabled`)) { check(`Size ${sizes[i]}: disabled (bigger than the crop)`, true); continue; }
        // Full no se arma de verdad (un PNG de 16 bits entero tarda): se retiene el pedido y se mira el resumen previo
        let held = null;
        if (sizes[i] === "full") await page.route("**/api/prepare", r => { held = r; });
        await page.click(`#size button:nth-child(${i + 1})`);
        const s = await summary(sizes[i] !== "full"), long = await ev(`Math.max(box()[2], box()[3])`);
        const wantLong = sizes[i] === "full" ? long : Math.min(sizes[i], long);
        check(`Size ${sizes[i]}: summary and request`, s.m && Math.max(Number(s.m[1]), Number(s.m[2])) === wantLong && Number(s.m[1]) === s.dims[0] && s.req.size === sizes[i], s.text);
        if (sizes[i] === "full") {
          await page.click("#size button:nth-child(1)"); await wait(300);
          await page.unroute("**/api/prepare"); await held?.abort().catch(() => {});
        }
      }
      await page.click("#size button:nth-child(1)");
      const crops = await ev(`CROPS`);
      for (let i = 0; i < crops.length; i++) {
        await page.click(`#area button:nth-child(${i + 1})`);
        const s = await summary(), [x, y, w, h] = s.req.box;
        const shape = crops[i].r ? Math.abs(w / h - crops[i].r) < 0.01 : true;
        check(`Crop ${crops[i].label}: frame, summary and request`, shape && s.m && Number(s.m[1]) === s.dims[0] && Number(s.m[2]) === s.dims[1] &&
              JSON.stringify(s.req.box) === JSON.stringify(await ev(`box()`)) && await ev(`crop().id`) === crops[i].id, `${s.text} box ${[x, y, w, h]}`);
      }
      // el marco con el mouse: desde 1:1 pasado a Free
      await page.click("#area button:nth-child(2)"); await page.click("#area button:nth-child(1)");
      let c = await cropScreen();
      await dragBy(c.x + c.w - 1, c.y + c.h - 1, -30, -30);
      const corner = await cropScreen();
      check("crop: corner resize (bottom-right)", corner.box[0] === c.box[0] && corner.box[1] === c.box[1] && corner.box[2] < c.box[2] && corner.box[3] < c.box[3], { from: c.box, to: corner.box });
      c = corner;
      await dragBy(c.x + 1, c.y + c.h / 2, 25, 0);
      const edge = await cropScreen();
      check("crop: left edge resize", edge.box[0] > c.box[0] && edge.box[2] < c.box[2] && edge.box[3] === c.box[3], { from: c.box, to: edge.box });
      c = edge;
      await dragBy(c.x + c.w / 2, c.y + c.h / 2, 20, 20);
      const moved = await cropScreen();
      check("crop: drag inside moves it", moved.box[0] !== c.box[0] && moved.box[1] !== c.box[1] && moved.box[2] === c.box[2] && moved.box[3] === c.box[3], { from: c.box, to: moved.box });
      await page.focus("#previewCanvas");
      await page.keyboard.press("ArrowLeft"); await page.keyboard.press("ArrowUp");
      const keyed = await ev(`[box(), dialog.open]`);
      check("crop: arrow keys move it (dialog stays open)", keyed[0][0] < moved.box[0] && keyed[0][1] < moved.box[1] && keyed[1], { from: moved.box, to: keyed[0] });
      const saved = await ev(`JSON.parse(localStorage.getItem("studio-export-v1")).crops[P().key].rect`);
      check("crop: saved in localStorage", saved && saved.length === 4);
      await shot("export");
    });
    await step("preview zoom", async () => {
      const pc = await page.locator("#previewCanvas").boundingBox(), x = pc.x + pc.width * 0.45, y = pc.y + pc.height * 0.4;
      const toPhoto = () => ev(([x, y]) => { const r = $("previewCanvas").getBoundingClientRect(), G = pvGeom(), k = dpr() / G.z; return [G.x0 + (x - r.left) * k, G.y0 + (y - r.top) * k, k]; }, [x, y]);
      const pvText = () => page.textContent("#pvZoom").then(t => t.trim());
      const a0 = await toPhoto();
      await page.mouse.move(x, y);
      await page.keyboard.down("Control"); await page.mouse.wheel(0, -100); await page.keyboard.up("Control");
      let level = "native";
      if (!(await lastWheel())?.ctrl) {
        level = "handler-level";
        await ev(([x, y]) => $("previewCanvas").dispatchEvent(new WheelEvent("wheel", { deltaY: -100, ctrlKey: true, clientX: x, clientY: y, bubbles: true, cancelable: true })), [x, y]);
      }
      await wait(100);
      const a1 = await toPhoto();
      check("preview: ctrl+wheel zooms at the pointer", await ev(`pview !== null`) && Math.hypot(a1[0] - a0[0], a1[1] - a0[1]) < a1[2] * 1.5 && /%$/.test(await pvText()),
            { before: a0.map(Math.round), after: a1.map(Math.round), z: await pvText() }, level);
      const g0 = await ev(`pvGeom().cy`);
      await page.mouse.wheel(0, 100); await wait(100);
      const g1 = await ev(`pvGeom().cy`), pw1 = await lastWheel();
      cell.wheel.previewPan = { received: pw1, photoPx: +(g1 - g0).toFixed(1) };
      check("preview: plain wheel pans", g1 > g0 && pw1?.prevented, cell.wheel.previewPan);
      await page.mouse.dblclick(x, y); await wait(150);
      const dd1 = await pvText();
      await page.mouse.dblclick(x, y); await wait(150);
      const dd2 = await pvText();
      check("preview: dblclick toggles Fit / 100%", dd1 === "Fit" && dd2 === "100%", `${dd1} ${dd2}`);
      await page.click("#pvZoom"); await wait(100);
      const z1 = await pvText();
      await page.click("#pvZoom"); await wait(100);
      const z2 = await pvText();
      check("preview: #pvZoom pill toggles", z1 === "Fit" && z2 === "100%", `${z1} ${z2}`);
      const k0 = await ev(`pvGeom().z`);
      await page.keyboard.press("Meta+Equal"); await wait(100);
      const k1 = await ev(`pvGeom().z`);
      await page.keyboard.press("Meta+Minus"); await wait(100);
      const k2 = await ev(`pvGeom().z`);
      await page.keyboard.press("Meta+Digit0"); await wait(100);
      const k3 = await ev(`[pview, document.getElementById("pvZoom").textContent, dialog.open, view().size === P().w].join()`);
      check("preview: ⌘+ ⌘− ⌘0 (main view untouched)", k1 > k0 && k2 < k1 && k3 === ",Fit,true,true" && (await pageOk()).ok, `${k0} ${k1} ${k2} ${k3}`);
      if (engine === "webkit") {
        const q0 = await ev(`pvGeom().z`);
        await ev(([x, y]) => {
          const mk = (type, scale) => { const e = new Event(type, { bubbles: true, cancelable: true }); Object.assign(e, { scale, clientX: x, clientY: y }); return e; };
          const c = $("previewCanvas");
          c.dispatchEvent(mk("gesturestart", 1)); c.dispatchEvent(mk("gesturechange", 3)); c.dispatchEvent(mk("gestureend", 3));
        }, [x, y]);
        await wait(100);
        const q1 = await ev(`[pvGeom().z, pvGeom().cx, pvGeom().cy].join()`);
        check("preview: WebKit gesturechange scale 3 zooms", Number(q1.split(",")[0]) > q0 * 2.5 && !q1.includes("NaN"), `${q0} → ${q1}`, "handler-level");
      }
      if ((await pvText()) === "Fit") await page.click("#pvZoom");
      await until(`$("pvZoom").textContent !== "Fit"`, 3000);
      const zoomedText = await pvText();
      await page.click("#close"); await closed(); await openDialog();
      // lo que dice la pastilla apenas abre, y despues del primer dibujo de la vista previa
      const first = await ev(`[pview, $("pvZoom").textContent].join()`);
      await until(`$("pvZoom").textContent === "Fit"`, 3000);
      const reopened = await ev(`[pview, $("pvZoom").textContent].join()`);
      check("preview: back to Fit on reopen", zoomedText !== "Fit" && reopened === ",Fit", `${zoomedText} → ${reopened}`);
      cell.pillOnReopen = first;
    });
    // Shape: Circle pone 1:1 y pide el circulo; JPG lo apaga. Vuelve a Square y al recorte de antes
    await step("export shape", async () => {
      if (!(await ev(`dialog.open`))) await openDialog();
      const before = await ev(`JSON.stringify(cropOf(P()))`);
      await page.click("#shape button:nth-child(2)");
      const s = await summary();
      const c = await ev(`(() => { const [, , w, h] = box(); return [cropOf(P()).mode, w === h, request().shape, $("shape").children[1].getAttribute("aria-pressed")].join(); })()`);
      check("Shape Circle: 1:1 crop, request asks for the circle", c === "1:1,true,circle,true" && s.req.shape === "circle", `${c} · ${s.text}`);
      await page.click("#format button:nth-child(4)");
      const jpg = await ev(`[$("shape").children[1].disabled, request().shape].join()`);
      check("Shape: Circle disabled in the 8-bit lossy format, the file goes square", jpg === "true,square", jpg);
      await page.click("#format button:nth-child(1)");
      await page.click("#shape button:nth-child(1)");
      await ev(`opts.crops[P().key] = JSON.parse(${JSON.stringify(before)}); setOpt("crops", opts.crops)`);
      await summary();
    });
    await step("download", async () => {
      phase = "download";
      for (const [i, ext] of [[0, "png"], [1, "tif"], [2, "webp"]]) {
        if (!(await ev(`dialog.open`))) await openDialog();
        await page.click(`#format button:nth-child(${i + 1})`);
        const s = await summary();
        const [download] = await Promise.all([page.waitForEvent("download", { timeout: 60000 }), page.click("#download")]);
        const name = download.suggestedFilename(), path = join(DOWNLOADS, `${tag}-${name}`);
        await download.saveAs(path);
        const head = [...readFileSync(path).subarray(0, 12)];
        const magic = ext === "tif" ? (head[0] === 0x49 && head[1] === 0x49 && head[2] === 42) || (head[0] === 0x4d && head[2] === 0) : MAGIC[ext].every((b, j) => head[j] === b);
        const dims = `-${s.dims[0]}x${s.dims[1]}.${ext}`;
        check(`Download ${ext}: name, extension and bytes`, name.startsWith(await ev(`P().key`)) && name.endsWith(dims) && name.includes("-crop") && magic,
              `${name} · ${head.slice(0, 4).map(b => b.toString(16)).join(" ")}`);
        check(`Download ${ext}: dialog closes, toast`, await closed() && (await ev(`lastToast()`)) === `Saved ${name}`);
      }
      // el cuarto formato: solo en memoria, nunca a disco
      await openDialog();
      await page.click("#format button:nth-child(4)");
      const r = await ev(async () => {
        const p = await prepare(true), b = new Uint8Array(await (await fetch(`api/file/${p.id}`)).arrayBuffer());
        return { name: p.name, bits: p.bits, head: [b[0], b[1]], n: b.length, label: FORMATS[3].label };
      });
      check(`${r.label} via /api/prepare in memory: FF D8, 8-bit`, r.head[0] === 0xff && r.head[1] === 0xd8 && r.bits === 8 && /\.\w+$/.test(r.name), `${r.name} · ${r.n} bytes`);
      await page.click("#format button:nth-child(1)");
      await summary();
      // sin servidor: el aviso y Download apagado
      phase = "offline";
      await page.route("**/api/prepare", route => route.abort());
      await page.click("#size button:nth-child(2)");
      const warned = await until(`$("foot").dataset.state === "warn"`, 10000);
      const st = await ev(`[$("info").textContent === OFFLINE, $("download").getAttribute("aria-disabled")].join()`);
      let downloaded = false;
      const onD = () => { downloaded = true; };
      page.on("download", onD);
      // con aria-disabled Playwright no hace clic: un clic de mouse de verdad sobre el boton
      const db = await page.locator("#download").boundingBox();
      await page.mouse.click(db.x + db.width / 2, db.y + db.height / 2); await wait(1000);
      page.off("download", onD);
      check("offline: message shown, Download does nothing", warned && st === "true,true" && !downloaded && await ev(`dialog.open`), `${st} downloaded=${downloaded}`);
      await page.unroute("**/api/prepare");
      await page.click("#size button:nth-child(1)");
      const back = await until(`$("foot").dataset.state === "" && /sRGB · [\\d.]+ [KM]B/.test($("info").textContent)`, 30000);
      check("offline: recovers when the server answers", back, await ev(`$("info").textContent`));
      phase = "export";
      await page.keyboard.press("Escape"); await closed();
    });

    // 10. la ventana cambia de tamano: la foto se vuelve a encajar
    await step("resize", async () => {
      const a = await ev(`[size.w, size.h]`);
      await page.setViewportSize({ width: vp.width - 200, height: vp.height - 100 });
      await wait(300); await idle();
      const b = await ev(`[size.w, size.h, frame.style.width, canvas.width, Math.round(size.w * dpr()), isFitted(view()), $("stage").getBoundingClientRect().width].join()`);
      const [w, , fw, cw, want, fitted] = b.split(",");
      check("window resize refits the photo", Number(w) < a[0] && fw === `${w}px` && cw === want && fitted === "true", `${a} → ${b}`);
      await page.setViewportSize({ width: vp.width, height: vp.height });
    });
    check("no uncaught page errors", !cell.errors.some(e => e.kind === "pageerror"), cell.errors.filter(e => e.kind === "pageerror").map(e => e.text).join(" | "));
  } finally {
    cell.ms = Date.now() - t0;
    cell.pass = cell.checks.filter(c => c.ok).length;
    cell.fail = cell.checks.filter(c => !c.ok).length;
    await context.close().catch(() => {});
  }
  return cell;
}

// --- la matriz ------------------------------------------------------------------
mkdirSync(DOWNLOADS, { recursive: true }); mkdirSync(dirname(OUT), { recursive: true });
const result = { started: new Date().toISOString(), playwright: PW_VERSION, browsers: {}, cells: [] };
const save = () => writeFileSync(OUT, JSON.stringify(result, null, 2));
let failed = false;
try {
  await startServers();
  for (const e of ENGINES) {
    if (onlyEngine && e.name !== onlyEngine) continue;
    const browser = await e.type.launch({ ...e.launch, headless: true, downloadsPath: DOWNLOADS });
    result.browsers[e.name] = browser.version();
    try {
      for (const vp of VIEWPORTS) {
        if (onlyVp === "reduced" ? !vp.reduced : onlyVp && (`${vp.width}x${vp.height}` !== onlyVp || vp.reduced)) continue;
        const cell = await runCell(browser, e.name, vp);
        result.cells.push(cell); save();
        console.log(`${cell.engine} ${cell.viewport}${cell.reducedMotion ? " reduced" : ""}: ${cell.pass} pass, ${cell.fail} fail, ${(cell.ms / 1000).toFixed(0)} s`);
        for (const c of cell.checks.filter(c => !c.ok)) console.log(`  FAIL ${c.name} — ${c.detail}`);
      }
    } finally { await browser.close(); }
  }
} catch (err) {
  failed = true; result.error = String(err.stack ?? err); console.error(err);
} finally {
  result.finished = new Date().toISOString(); save();
  stopServers();
  if (existsSync(DOWNLOADS)) rmSync(DOWNLOADS, { recursive: true, force: true });
}
process.exitCode = failed || result.cells.some(c => c.fail) ? 1 : 0;
