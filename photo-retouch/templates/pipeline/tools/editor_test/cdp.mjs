// Chrome headless por el protocolo de DevTools, sin dependencias (Node 22+ trae WebSocket).
// Lanza un Chrome con un perfil temporal, abre una pestana y da lo justo para probar el editor.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
export const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function launch({ out, width = 1512, height = 860, dpr = 2 }) {
  const profile = mkdtempSync(join(tmpdir(), "editor-test-"));
  const proc = spawn(CHROME, [
    "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "--no-first-run",
    "--no-default-browser-check", "--hide-scrollbars", "--force-color-profile=srgb", "about:blank",
  ], { stdio: ["ignore", "ignore", "pipe"] });
  const exited = new Promise(ok => proc.on("exit", ok));
  const wsUrl = await new Promise((ok, fail) => {
    let buf = "";
    proc.stderr.on("data", d => { buf += d; const m = buf.match(/DevTools listening on (ws:\S+)/); if (m) ok(m[1]); });
    exited.then(c => fail(new Error(`Chrome se cerro (${c})`)));
    setTimeout(() => fail(new Error("Chrome no arranco en 20 s")), 20000);
  });
  const ws = new WebSocket(wsUrl);
  await new Promise(ok => ws.addEventListener("open", ok, { once: true }));

  let id = 0;
  const pending = new Map(), listeners = [];
  ws.addEventListener("message", ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { ok, fail } = pending.get(m.id); pending.delete(m.id);
      m.error ? fail(new Error(JSON.stringify(m.error))) : ok(m.result);
    } else for (const l of listeners) l(m);
  });
  const send = (method, params = {}, sessionId) => new Promise((ok, fail) => {
    const i = ++id; pending.set(i, { ok, fail });
    ws.send(JSON.stringify({ id: i, method, params, sessionId }));
  });
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const S = (m, p) => send(m, p, sessionId);

  // errores de la pagina: excepciones, console.error/warn y recursos que no cargan
  const errors = [];
  listeners.push(m => {
    if (m.sessionId !== sessionId) return;
    if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text);
    if (m.method === "Runtime.consoleAPICalled" && ["error", "warning", "assert"].includes(m.params.type))
      errors.push(m.params.args.map(a => a.value ?? a.description).join(" "));
    if (m.method === "Log.entryAdded" && m.params.entry.level === "error") errors.push(`${m.params.entry.text} ${m.params.entry.url ?? ""}`);
  });
  await S("Page.enable"); await S("Runtime.enable"); await S("Log.enable");

  const page = {
    errors,
    size: (w, h) => S("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile: false }),
    async eval(expr) {
      const r = await S("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
      return r.result.value;
    },
    async waitFor(expr, ms = 30000) {
      const t0 = Date.now();
      while (Date.now() - t0 < ms) { if (await page.eval(expr)) return; await sleep(100); }
      throw new Error(`no paso en ${ms / 1000} s: ${expr}`);
    },
    async goto(url) {
      const loaded = new Promise(ok => listeners.push(m => { if (m.sessionId === sessionId && m.method === "Page.loadEventFired") ok(); }));
      await S("Page.navigate", { url }); await loaded;
    },
    async shot(name, clip) {
      const r = await S("Page.captureScreenshot", { format: "png", ...(clip ? { clip: { ...clip, scale: 1 } } : {}) });
      writeFileSync(join(out, `${name}.png`), Buffer.from(r.data, "base64"));
    },
    rect: sel => page.eval(`(() => { const r = document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect();
      return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`),
    mouse: (type, x, y, { held = false, clickCount = 1 } = {}) => S("Input.dispatchMouseEvent", {
      type, x, y, clickCount, button: type === "mouseMoved" && !held ? "none" : "left", buttons: type === "mousePressed" || held ? 1 : 0,
    }),
    async click(x, y, clickCount = 1) {
      await page.mouse("mouseMoved", x, y);
      await page.mouse("mousePressed", x, y, { clickCount }); await page.mouse("mouseReleased", x, y, { clickCount });
    },
    async drag(from, to, steps = 8) {
      await page.mouse("mouseMoved", from[0], from[1]);
      await page.mouse("mousePressed", from[0], from[1]);
      for (let i = 1; i <= steps; i++)
        await page.mouse("mouseMoved", from[0] + ((to[0] - from[0]) * i) / steps, from[1] + ((to[1] - from[1]) * i) / steps, { held: true });
      await page.mouse("mouseReleased", to[0], to[1]);
    },
    // text: lo que la tecla escribe; Enter con text "\r" aprieta el boton que tiene el foco, como en el teclado
    async key(key, { keyCode = 0, code = key, shift = false, meta = false, text } = {}) {
      const base = { key, code, windowsVirtualKeyCode: keyCode, modifiers: (shift ? 8 : 0) | (meta ? 4 : 0) };
      await S("Input.dispatchKeyEvent", { type: "keyDown", ...base, ...(text ? { text } : {}) });
      await S("Input.dispatchKeyEvent", { type: "keyUp", ...base });
    },
    // una tecla mantenida (Espacio): bajar, repetir y soltar por separado
    keyDown: (key, { keyCode = 0, code = key, repeat = false } = {}) =>
      S("Input.dispatchKeyEvent", { type: "keyDown", key, code, windowsVirtualKeyCode: keyCode, autoRepeat: repeat }),
    keyUp: (key, { keyCode = 0, code = key } = {}) => S("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode }),
    type: text => S("Input.insertText", { text }),
    // rueda (modifiers: 2 ctrl, 4 cmd); el pellizco del trackpad le llega a la pagina como rueda con ctrl
    wheel: (x, y, deltaY, { deltaX = 0, modifiers = 0 } = {}) =>
      S("Input.dispatchMouseEvent", { type: "mouseWheel", x, y, deltaX, deltaY, modifiers }),
    // el pellizco entero, como lo hace el trackpad: si la pagina no lo frena, el navegador agranda la pagina
    pinch: (x, y, scaleFactor) => S("Input.synthesizePinchGesture", { x, y, scaleFactor, gestureSourceType: "mouse" }),
    // las letras con las que Chrome dibujo el texto de un elemento (la que encontro, no la que pide el CSS)
    async fonts(sel) {
      await S("DOM.enable"); await S("CSS.enable");
      const { root } = await S("DOM.getDocument", { depth: 0 });
      const { nodeId } = await S("DOM.querySelector", { nodeId: root.nodeId, selector: sel });
      return (await S("CSS.getPlatformFontsForNode", { nodeId })).fonts;
    },
    async close() {
      try { ws.close(); } catch {}
      proc.kill("SIGTERM");
      await exited;
      // Chrome deja procesos hijos escribiendo un momento despues de cerrarse
      rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 100 });
    },
  };
  await page.size(width, height);
  return page;
}
