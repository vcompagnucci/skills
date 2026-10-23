// Prueba el editor de punta a punta en Chrome headless: el panel de DialKit (solo controles), el cambio de foto en un
// solo dibujo, la vista (RAW original y Before / after), Espacio y las flechas, los ajustes que llegan al render, las
// versiones (Save version, cambiar, recorrerlas con ↓ ↑, borrar, y que vuelvan al recargar y en otro puerto), el antes y
// despues entre versiones (su menu con el mouse y el teclado), el export igual a lo que se ve (y su resumen, sin zoom
// al pasar el puntero y con Download apagado sin servidor), el panel de export (Format, Size, Crop: los cuatro formatos,
// el JPG solo en memoria; el marco del recorte con el mouse y las flechas; el zoom de la vista previa, que nunca muestra
// mas detalle que el archivo), que los parches de ojeras no dejen bordes, el zoom
// (pellizco en cualquier parte sin agrandar la pagina, el boton y ⌘+ ⌘- ⌘0) y la barra del antes y despues (correrla
// nunca corre la foto, y en los bordes se sigue agarrando) y el fondo (la carpeta Background: solo la pared, y a 1:1
// igual al archivo del servidor).
// Uso: node tools/editor_test/test.mjs [pagina]   (editor.html si no se dice)
// Arranca dos servidores propios (8792 y 8793) y los apaga siempre al final. editadas/versiones.json no se toca: los
// servidores guardan en work/editor-test/versiones-test.json (EDITOR_VERSIONS), que arranca vacio. Asi se puede correr
// con el fotografo editando en el suyo. Deja capturas en proceso/editor-prueba-*.png.
// Necesita al menos dos fotos en la sesion (recipe/photos.py), la primera con pared y con caras inventariadas.
import { spawn } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { launch, sleep } from "./cdp.mjs";

const ROOT = new URL("../../", import.meta.url).pathname;
const PAGE = process.argv[2] ?? "editor.html";
const PORTS = [8792, 8793];
const OUT = `${ROOT}proceso/`;
const VERSIONS = `${ROOT}work/editor-test/versiones-test.json`;
mkdirSync(OUT, { recursive: true });
mkdirSync(`${ROOT}work/editor-test`, { recursive: true });

let failures = 0;
const check = (cond, msg, extra = "") => { console.log(cond ? "ok  " : "FAIL", msg, extra); if (!cond) failures++; };

function server(port) {
  const proc = spawn("nice", ["-n", "19", `${ROOT}.venv/bin/python`, `${ROOT}recipe/editor_server.py`, String(port)],
                     { cwd: ROOT, env: { ...process.env, MallocLargeCache: "0", EDITOR_VERSIONS: VERSIONS, EDITOR_IMPORTS: `${ROOT}work/sin-importadas.json` }, stdio: ["ignore", "pipe", "pipe"] });
  let log = "";
  proc.stderr.on("data", d => { log = (log + d).slice(-4000); });  // se lee siempre: lleno, frenaria al servidor
  const exited = new Promise(ok => proc.on("exit", ok));
  const ready = new Promise((ok, fail) => {
    let buf = "";
    proc.stdout.on("data", d => { buf += d; if (buf.includes("Editor en")) ok(); });
    exited.then(c => fail(new Error(`el servidor ${port} se cerro (${c}); ¿puerto ocupado?\n${log}`)));
    setTimeout(() => fail(new Error(`el servidor ${port} no arranco en 15 s`)), 15000);
  });
  return { ready, stop: () => { if (proc.exitCode === null) proc.kill("SIGTERM"); return exited; } };
}

rmSync(VERSIONS, { force: true });  // la copia de la prueba, nunca la de editadas/
const servers = PORTS.map(server);
let page = null;
try {
  await Promise.all(servers.map(s => s.ready));
  page = await launch({ out: OUT });
  const ev = expr => page.eval(expr);
  const until = (expr, ms = 10000) => page.waitFor(expr, ms).then(() => true, () => false);
  // abierto = dibujado y con las imagenes de pantalla de las cuatro fotos (sus ojeras y su fondo) en la placa
  const open = async port => {
    await page.goto(`http://127.0.0.1:${port}/${PAGE}`);
    await page.waitFor(`frame.classList.contains("ready") && PHOTOS.every(p => [screenUrl(p, "edit"), screenUrl(p, "raw"), ...eyeUrls(p), ...bgUrls(p)].every(renderer.ready))`, 30000);
  };
  const versions = () => ev(`[...$("versions").querySelectorAll(".item")].map(b => b.textContent + (b.getAttribute("aria-current") === "true" ? "*" : "")).join(", ")`);
  const tap = async sel => { const r = await page.rect(sel); await page.click(r.x + r.w / 2, r.y + r.h / 2); };
  const slider = label => `#controls .dialkit-slider[aria-label="${label}"]`;
  // las acciones de DialKit (Reset, Save version) son botones sin nada propio mas que el texto
  const tapButton = async text => {
    const r = await ev(`(() => { const b = [...document.querySelectorAll("#controls .dialkit-button")].find(b => b.textContent.trim() === ${JSON.stringify(text)});
      b.scrollIntoView({ block: "nearest" }); const r = b.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    await page.click(r.x, r.y);
  };
  // las ojeras van por cara: look() da la intensidad si todas son iguales; allEyes(n), todas las caras de la foto a n
  const look = () => ev(`[settings.adjust.exposure, [...new Set(Object.values(settings.levels))].join("/")].join()`);
  const allEyes = n => `Object.fromEntries(eyeControls(P()).map(([k]) => [k, ${n}]))`;
  const saved = cond => until(`fetch("api/versions", { cache: "no-store" }).then(r => r.json()).then(d => { const s = d.photos?.[P().key]; return !!s && (${cond}); })`);

  await open(PORTS[0]);

  // 1. el panel derecho: solo DialKit, con sus cuatro carpetas, los diecinueve controles y Reset
  const panel = await ev(`(() => {
    const aside = $("controls"), kids = [...aside.children], dial = aside.querySelector('.dialkit-slider[aria-label="' + eyeControls(P())[0][0] + '"]');
    return { only: kids.length === 1 && kids[0].classList.contains("dialkit-root"),
             folders: [...aside.querySelectorAll(".dialkit-folder-header-top")].filter(f => f.checkVisibility()).map(f => f.textContent.trim()).join(),
             labels: [...aside.querySelectorAll(".dialkit-slider")].map(s => s.getAttribute("aria-label")).join(),
             reset: [...aside.querySelectorAll("button")].some(b => b.textContent.trim() === "Reset"),
             eyes: [dial.getAttribute("aria-valuemin"), dial.getAttribute("aria-valuemax"), dial.getAttribute("aria-valuenow")].join() };
  })()`);
  check(panel.only, "el panel derecho tiene solo DialKit");
  check(panel.folders === "Under-eyes,Light,Color,Background", "el panel con las carpetas Under-eyes, Light, Color y Background, sin el titulo Edit (las dos barras abren con un titulo de seccion)", panel.folders);
  // las ojeras: un control por cara de la primera foto, con el nombre que les da el editor (FACE_NAMES o el id)
  const faceLabels = await ev(`eyeControls(P()).map(([name]) => name).join()`);
  check(panel.labels === faceLabels + ",Exposure,Brightness,Contrast,Highlights,Shadows,Whites,Blacks,Temperature,Tint,Vibrance,Saturation," +
                         "Exposure,Evenness,Smoothing,Falloff,Temperature,Tint,Saturation" && panel.reset,
        "los controles en orden (las ojeras, una por cara, de izquierda a derecha) y Reset", panel.labels);
  check(panel.eyes === `0,${await ev("EYE_MAX")},${await ev("EYE_DEFAULT")}`, "ojeras de 0 al tope, arranca en la entrega", panel.eyes);
  // sin versiones guardadas, la lista muestra la base de DialKit; con alguna, la base se esconde (en el 7)
  check(await versions() === "Version 1*", "versiones: sin ninguna guardada, arranca con la base (Version 1)", await versions());
  const chrome = await ev(`(() => {
    const buttons = [...document.querySelectorAll("#controls .dialkit-button")];
    return { menu: getComputedStyle(document.querySelector("#controls .dialkit-panel-toolbar")).display,
             buttons: buttons.map(b => b.textContent.trim()).join(),
             weight: buttons.map(b => getComputedStyle(b).color).join(" / "),
             nav: [...document.querySelectorAll(".side-nav h2")].map(h => h.textContent).join(),
             views: [...$("views").querySelectorAll(".item")].map(b => b.textContent + ":" + b.getAttribute("aria-pressed")).join(),
             left: [...document.querySelectorAll(".side-nav button")].filter(b => /new|save/i.test(b.textContent)).length };
  })()`);
  check(chrome.menu === "none" && chrome.buttons === "Reset,Copy to other photos,Save version" && chrome.left === 0,
        "versiones: Copy to other photos y Save version, abajo del panel; sin el menu de DialKit ni New version a la izquierda", chrome.buttons);
  check(chrome.weight.split(" / ")[0] !== chrome.weight.split(" / ").at(-1) && chrome.weight.split(" / ")[0] === chrome.weight.split(" / ")[1], "Save version pesa mas que Reset y Copy to other photos", chrome.weight);
  check(chrome.nav === "View,Versions" && chrome.views === "RAW original:false,Before / after:false",
        "titulos en oracion, como las carpetas de DialKit; la vista: RAW original y Before / after, apagados", `${chrome.nav} · ${chrome.views}`);
  // la barra derecha es el panel mismo, como la izquierda: sin una tarjeta adentro (borde, esquinas, vidrio) y con el
  // fondo de la pagina, tambien detras de su titulo fijo
  const card = await ev(`(() => {
    const s = getComputedStyle(document.querySelector("#controls .dialkit-panel-inner"));
    return { border: s.borderTopWidth, radius: s.borderTopLeftRadius, glass: s.backdropFilter, bg: s.backgroundColor,
             head: getComputedStyle(document.querySelector("#controls .dialkit-panel-header")).backgroundColor,
             page: getComputedStyle(document.body).backgroundColor };
  })()`);
  check(card.border === "0px" && card.radius === "0px" && card.glass === "none" && card.bg === card.page && card.head === card.page,
        "la barra derecha sin tarjeta adentro: sin borde, esquinas ni vidrio, con el fondo de la pagina", JSON.stringify(card));

  // 2. cambiar de foto: un solo dibujo, ya con la editada de la foto nueva, el lienzo a su medida y su panel. Sin RAW
  // ni negro en el medio, y en menos de dos cuadros
  const switches = await ev(`(() => {
    const calls = [], orig = renderer.draw, out = [];
    renderer.draw = (s, t, clip) => { if (!t) calls.push({ edit: s.edit, show: s.show, w: canvas.width, h: canvas.height }); return orig(s, t, clip); };
    try {
      for (const i of [...PHOTOS.keys()].slice(1).concat(0)) {
        calls.length = 0;
        const t0 = performance.now(); pickPhoto(i); const ms = performance.now() - t0;
        const p = P(), c = calls[0];
        out.push({ key: p.key, ms, n: calls.length, edit: !!c && c.edit === screenUrl(p, "edit"), show: c?.show,
                   aspect: !!c && Math.abs(c.w / c.h - p.w / p.h) < 0.01, panel: dial.id === panelId(p.key) });
      }
    } finally { renderer.draw = orig; }
    return out;
  })()`);
  for (const s of switches)
    check(s.n === 1 && s.edit && s.show === 0 && s.aspect && s.panel && s.ms < 34, `${s.key}: un dibujo con su editada, en ${s.ms.toFixed(1)} ms`,
          s.n === 1 && s.edit ? "" : JSON.stringify(s));

  // si la foto nueva todavia no llego (recien abierto) y tiene otra orientacion, queda la anterior entera, a su tamano,
  // y cambia de una cuando llega: achicar el lienzo antes lo borraba y se veia negro
  const early = await ev(`(async () => {
    const p = PHOTOS[1], before = [canvas.width, canvas.height, frame.style.width].join();
    renderer.release(screenUrl(p, "edit"));
    pickPhoto(1);
    const held = [canvas.width, canvas.height, frame.style.width].join() === before;
    await renderer.load(screenUrl(p, "edit")); draw();
    const swapped = Math.abs(canvas.width / canvas.height - p.w / p.h) < 0.01 && frame.style.width === size.w + "px";
    pickPhoto(0);
    return { held, swapped };
  })()`);
  check(early.held && early.swapped, "foto nueva sin cargar: queda la anterior a su tamano y cambia de una al llegar", JSON.stringify(early));

  // 3. teclado: ← y → cambian de foto (↓ y ↑ recorren las versiones: en el 7); la M ya no hace nada
  await ev(`document.activeElement?.blur()`);
  await page.key("ArrowRight", { keyCode: 39 });
  const right = await ev("state.photo");
  await page.key("ArrowLeft", { keyCode: 37 });
  check(right === 1 && await ev("state.photo") === 0, "→ y ← cambian de foto");
  const before = await ev(`JSON.stringify([state, settings, $("versions").innerHTML])`);
  await page.key("m", { keyCode: 77 });
  check(await ev(`JSON.stringify([state, settings, $("versions").innerHTML])`) === before, "la M no hace nada");

  // 4. Espacio mantenido muestra el RAW sobre la version, con el foco donde sea salvo donde se escribe; un control con
  // foco no se aprieta
  await ev(`window.__shows = []; window.__draw = renderer.draw;
            renderer.draw = (s, t, clip) => { if (!t) __shows.push([s.show, clip ? clip.join("-") : "all"]); return __draw(s, t, clip); }`);
  const hold = async focus => {
    await ev(`(${focus}); __shows.length = 0`);
    await page.keyDown(" ", { keyCode: 32, code: "Space" });
    await page.keyDown(" ", { keyCode: 32, code: "Space", repeat: true });
    const on = await ev(`[state.peek, ...(__shows.at(-1) ?? [])].join()`);
    await page.keyUp(" ", { keyCode: 32, code: "Space" });
    return [on, await ev(`[state.peek, ...(__shows.at(-1) ?? [])].join()`)].join(" / ");
  };
  const folder = `[...document.querySelectorAll(".dialkit-folder-header-top")].find(f => f.textContent.trim() === "Light")`;
  check(await hold(`document.activeElement?.blur()`) === "true,1,all / false,0,all", "Espacio: RAW mientras se mantiene, la editada al soltar");
  const folderPeek = await hold(`${folder}.focus()`);
  check(folderPeek === "true,1,all / false,0,all" && await ev(`${folder}.getAttribute("aria-expanded")`) === "true",
        "con el foco en una carpeta: muestra el RAW y la carpeta no se cierra", folderPeek);
  const sliderPeek = await hold(`document.querySelector('${slider("Exposure")}').focus()`);
  check(sliderPeek === "true,1,all / false,0,all" && await look() === "0,70", "con el foco en un control: muestra el RAW y el valor no cambia", sliderPeek);
  await ev(`document.querySelector('${slider("Exposure")}').focus()`);
  await page.key("Enter", { keyCode: 13 });  // Enter abre el numero del control para escribirlo
  const typing = await ev(`document.activeElement.classList.contains("dialkit-slider-input")`), typed = await hold(`void 0`);
  check(typing && typed.startsWith("false"), "escribiendo el numero de un control, Espacio no hace nada", typed);
  await page.key("Escape", { keyCode: 27 });
  // la vista: un clic prende y apaga; RAW original y Before / after se excluyen, y en el RAW el panel queda apagado
  const views = () => ev(`[mode(), $("rawView").getAttribute("aria-pressed"), $("compareView").getAttribute("aria-pressed"), $("controls").inert,
                           $("controls").classList.contains("off")].join()`);
  await tap("#rawView");
  const rawOn = await views();
  await tap("#compareView");
  const compareOn = await views();
  await tap("#compareView");
  const bothOff = await views();
  check(rawOn === "raw,true,false,true,true" && compareOn === "compare,false,true,false,false" && bothOff === "edit,false,false,false,false",
        "la vista: un clic prende y apaga, RAW y Before / after se excluyen, y en el RAW el panel se apaga", `${rawOn} · ${compareOn} · ${bothOff}`);
  // Espacio es solo para la version: en el RAW y en el antes y despues no hace nada (no dibuja) y su ayuda se va
  const peekHint = () => ev(`getComputedStyle($("peekKey")).display`);
  const editHint = await peekHint();
  await ev(`state.raw = true; render()`);
  const rawPeek = await hold(`document.activeElement?.blur()`), rawHint = await peekHint();
  await ev(`state.raw = false; state.compare = true; render()`);
  const comparePeek = await hold(`document.activeElement?.blur()`), compareHint = await peekHint();
  await ev(`state.compare = false; render()`);
  check(rawPeek === "false / false" && comparePeek === "false / false", "en el RAW y en el antes y despues, Espacio no hace nada", `${rawPeek} · ${comparePeek}`);
  check(editHint !== "none" && rawHint === "none" && compareHint === "none" && await peekHint() !== "none",
        "la ayuda de Espacio se ve solo sobre la version", `${editHint} · ${rawHint} · ${compareHint}`);
  // cambiar de vista con Espacio apretado lo suelta: al volver, se ve la version
  await ev(`document.activeElement?.blur()`);
  await page.keyDown(" ", { keyCode: 32, code: "Space" });
  const held = await ev("state.peek");
  await tap("#rawView");
  const released = await ev("state.peek");
  await page.keyUp(" ", { keyCode: 32, code: "Space" });
  await tap("#rawView");
  check(held && !released && await ev(`[state.peek, mode()].join()`) === "false,edit", "cambiar de vista con Espacio apretado lo suelta", `${held} → ${released}`);
  await ev(`renderer.draw = __draw`);

  // 5. las flechas sobre un control son del control: mueven el valor, no la foto
  await ev(`document.querySelector('${slider("Contrast")}').focus()`);
  await page.key("ArrowRight", { keyCode: 39 });
  const arrow = await ev(`[state.photo, settings.adjust.contrast].join()`);
  check(arrow.startsWith("0,") && Number(arrow.split(",")[1]) > 0, "→ sobre Contrast lo sube y no cambia la foto", arrow);

  // 6. arrastrar Exposure con el mouse llega al render; Reset vuelve a la entrega
  await ev(`document.activeElement?.blur(); dial.setValues(defaultsFor(P()))`);
  const mean = `(() => { const p = P(), w = 96, h = Math.round(w * p.h / p.w), px = renderer.read(scene(p, view(), w, { dither: false }), w, h);
    let s = 0; for (let i = 0; i < px.length; i += 4) s += px[i] + px[i + 1] + px[i + 2]; return s / (px.length * 0.75); })()`;
  const m0 = await ev(mean), ex = await page.rect(slider("Exposure"));
  await page.drag([ex.x + ex.w / 2, ex.y + ex.h / 2], [ex.x + ex.w * 0.8, ex.y + ex.h / 2]);
  await sleep(500);
  const exposure = await ev("settings.adjust.exposure"), m1 = await ev(mean);
  check(exposure > 0.5 && m1 > m0 + 5, `arrastrar Exposure a ${exposure} aclara la foto`, `(${m0.toFixed(1)} → ${m1.toFixed(1)})`);
  await tapButton("Reset");
  check(await ev(`Object.values(settings.levels).every(l => l === EYE_DEFAULT) && KEYS.every(k => settings.adjust[k] === 0)`), "Reset: ojeras en la entrega y sin ajustes");

  // 7. versiones: Save version guarda lo que se ve como una nueva, fija, y se sigue en la que estaba; cambiar, borrar;
  // se guardan en el servidor y vuelven al recargar y en otro puerto. La base de DialKit ("Version 1") solo esta en la
  // lista, en el menu del antes y en ↓ ↑ mientras no haya ninguna guardada (pedido del fotografo, 2026-10-18)
  const rowOf = name => `[...$("versions").querySelectorAll(".item")].find(b => b.textContent === ${JSON.stringify(name)})`;
  const tapAt = async expr => {
    const r = await ev(`(() => { const r = (${expr}).getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    await page.click(r.x, r.y);
  };
  const tapVersion = name => tapAt(rowOf(name));
  const deleteVersion = name => tapAt(`${rowOf(name)}.closest(".version").querySelector(".del")`);
  const toastSaid = () => ev(`lastToast()`);
  await ev(`dial.setValues({ Light: { Exposure: 0.5 } })`);
  await tapButton("Save version");
  const said = await toastSaid();
  const onBase = { list: await versions(), current: await ev(`$("versions").querySelectorAll('[aria-current="true"]').length`), after: await ev(`$("afterLabel").textContent`) };
  check(onBase.list.replace("*", "") === "Version 2" && said === "Version 2 saved in all photos", "Save version sobre la base guarda la 2, y la base sale de la lista", `${onBase.list} · ${said}`);
  // con alguna version guardada, lo que se ve tiene que ser una de la lista
  check(onBase.current === 1 && onBase.after === "Version 2", "despues de guardar la primera, la que se ve esta marcada en la lista y en el rotulo del despues",
        JSON.stringify(onBase));
  await tapVersion("Version 2");
  check(await versions() === "Version 2*" && await look() === "0.5,70", "elegir la 2 la pone", `${await versions()} ${await look()}`);
  await tapButton("Save version");
  const said3 = await toastSaid();
  check(await versions() === "Version 2*, Version 3" && said3 === "Version 3 saved in all photos", "Save version guarda la 3 y se sigue en la 2", `${await versions()} · ${said3}`);
  await ev(`dial.setValues({ Light: { Exposure: -0.4 }, "Under-eyes": ${allEyes(150)} })`);
  await tapVersion("Version 3");
  const v3 = await look();
  await tapVersion("Version 2");
  const v2 = await look();
  check(v2 === "-0.4,150" && v3 === "0.5,70", "la 3 quedo fija; lo que se movio despues fue a la 2", `(2: ${v2}; 3: ${v3})`);
  await tap("#rawView");
  await page.key("ArrowDown", { keyCode: 40 });
  const walked = [await versions(), await look(), await ev("mode()")].join(" ");
  await page.key("ArrowDown", { keyCode: 40 });
  const end = await versions();
  await page.key("ArrowUp", { keyCode: 38 });
  await page.key("ArrowUp", { keyCode: 38 });
  check(walked === "Version 2, Version 3* 0.5,70 edit" && end === "Version 2, Version 3*" && await versions() === "Version 2*, Version 3" && await look() === "-0.4,150",
        "↓ y ↑ recorren las versiones, se frenan en la primera y la ultima (sin la base) y salen del RAW", `${walked} · ${end} · ${await versions()}`);

  // el antes y despues por version: a la derecha la puesta; a la izquierda lo que se elija en el menu de su rotulo, menos
  // ella. El menu es nuestro (el de macOS salia claro sobre el editor oscuro) y se usa como uno: clic o teclado
  await tap("#compareView");
  // las opciones, la marcada (si el rotulo dice otra cosa, las dos) y el rotulo de la derecha
  const pickOf = () => ev(`(() => {
    const items = [...$("beforeMenu").children], on = items.find(b => b.getAttribute("aria-checked") === "true")?.textContent, name = $("beforeName").textContent;
    return [items.map(b => b.textContent).join("|"), on === name ? on : on + "≠" + name, $("afterLabel").textContent].join();
  })()`);
  const menuOpen = () => ev(`[$("beforeMenu").matches(":popover-open"), $("beforePick").getAttribute("aria-expanded")].join()`);
  const menuShut = () => until(`$("beforePick").getAttribute("aria-expanded") === "false"`, 2000);
  const choose = async name => {
    await tap("#beforePick");
    await until(`$("beforeMenu").contains(document.activeElement)`, 2000);
    const r = await ev(`(() => { const r = [...$("beforeMenu").children].find(b => b.textContent === ${JSON.stringify(name)}).getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
    await page.click(r.x, r.y);
    await menuShut();
  };
  const menu = await pickOf();
  await tap("#beforePick");
  await until(`$("beforeMenu").contains(document.activeElement)`, 2000);
  const opened = [await menuOpen(), await ev(`document.activeElement.textContent`)].join();
  await page.key("Escape", { keyCode: 27 });
  await menuShut();
  const escaped = [await menuOpen(), await ev(`document.activeElement === $("beforePick")`)].join();
  check(opened === "true,true,RAW original" && escaped === "false,false,true",
        "el menu del antes se abre con la elegida en foco; Escape lo cierra y el foco vuelve al rotulo", `${opened} · ${escaped}`);
  await choose("Version 3");
  const chosen = await pickOf(), picked = [await menuOpen(), await ev(`$("beforePick").matches(":focus-visible")`)].join();
  check(menu === "RAW original|Version 3,RAW original,Version 2" && chosen === "RAW original|Version 3,Version 3,Version 2",
        "el antes arranca en el RAW y ofrece las otras versiones, sin la base; el despues es la puesta", `${menu} · ${chosen}`);
  check(picked === "false,false,false", "elegir con el mouse cierra el menu, sin dejar el anillo del teclado en el rotulo", picked);
  // lo que se ve: la izquierda de la barra es la 3 y la derecha la 2, pixel a pixel contra cada una dibujada sola
  const halvesOf = () => ev(`(() => {
    draw();
    const gl = renderer.gl, W = canvas.width, H = canvas.height, x = Math.round(state.split * W), row = W * 4;
    const live = new Uint8Array(W * H * 4);
    gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, live);  // de abajo hacia arriba
    const p = P(), v = view(), b = renderer.read(scene(p, v, size.cw, { look: beforeLook() }), W, H).slice(),
          a = renderer.read(scene(p, v, size.cw, { look: liveLook() }), W, H).slice();
    let left = 0, right = 0, apart = 0;
    for (let y = 0; y < H; y++) for (let i = 0; i < W; i++) for (let k = 0; k < 3; k++) {
      const s = (H - 1 - y) * row + i * 4 + k, t = y * row + i * 4 + k;
      if (i < x - 1) left = Math.max(left, Math.abs(live[s] - b[t]));
      if (i > x) right = Math.max(right, Math.abs(live[s] - a[t]));
      apart += Math.abs(a[t] - b[t]);
    }
    return { left, right, apart: apart / (W * H * 3) };
  })()`);
  const halves = await halvesOf();
  check(halves.left === 0 && halves.right === 0 && halves.apart > 2, "la izquierda es la 3 y la derecha la 2, al pixel", JSON.stringify(halves));
  await page.key("ArrowDown", { keyCode: 40 });
  const same = await pickOf();
  await page.key("ArrowUp", { keyCode: 38 });
  check(same === "RAW original|Version 2,RAW original,Version 3" && await pickOf() === chosen,
        "con la 3 a la derecha, la izquierda es el RAW; al volver a la 2, el antes vuelve a ser la 3", `${same} · ${await pickOf()}`);
  await ev(`$("knob").focus()`);
  await page.key("ArrowRight", { keyCode: 39 });
  const knob = await ev(`[state.photo, state.split.toFixed(2)].join()`);
  check(knob === "0,0.52", "con la perilla seleccionada, → corre la barra y no cambia de foto", knob);
  await ev(`state.split = 0.5; paintSplit(); document.activeElement.blur()`);
  // y al reves, con el teclado: con la 3 puesta, la 2 a la izquierda. Enter abre el menu en la elegida (el RAW), ↓ baja
  // a la 2 y Enter la elige
  await page.key("ArrowDown", { keyCode: 40 });
  await ev(`$("beforePick").focus()`);
  await page.key("Enter", { keyCode: 13, text: "\r" });
  await until(`$("beforeMenu").contains(document.activeElement)`, 2000);
  await page.key("ArrowDown", { keyCode: 40 });
  await page.key("Enter", { keyCode: 13, text: "\r" });
  await menuShut();
  const flipped = await pickOf(), reverse = await halvesOf();
  check(flipped === "RAW original|Version 2,Version 2,Version 3" && reverse.left === 0 && reverse.right === 0 && reverse.apart > 2,
        "con la 3 puesta, la 2 a la izquierda tambien (elegida con Enter, ↓ y Enter), al pixel", `${flipped} · ${JSON.stringify(reverse)}`);
  await page.key("ArrowUp", { keyCode: 38 });
  await tap("#compareView");
  check(await saved(`s.presets.length === 2 && s.activePresetId === s.presets[0].id && Object.values(s.presets[1].values).includes(0.5) &&
                     Object.values(s.presets[0].values).includes(-0.4)`),
        "se guardan en el archivo de versiones (la copia de la prueba)");
  await open(PORTS[0]);
  check(await versions() === "Version 2*, Version 3" && await look() === "-0.4,150", "al recargar vuelven, con la 2 puesta", await versions());
  await open(PORTS[1]);
  check(await versions() === "Version 2*, Version 3" && await look() === "-0.4,150", "en otro puerto tambien", await versions());
  await ev(`pickPhoto(1)`);
  const other = [await versions(), await look()].join(" ");
  await ev(`pickPhoto(0)`);
  // la 2 se movio despues de guardarla: eso queda en esta foto, la otra la tiene con los valores de cuando se guardo
  check(other === "Version 2*, Version 3 0.5,70" && await versions() === "Version 2*, Version 3", "las otras fotos tienen las mismas versiones, con los valores de cuando se guardaron", other);
  // una foto con versiones y ninguna puesta abre en la primera: se le copian las de esta a la ultima, sin la puesta
  const lastKey = await ev(`PHOTOS.at(-1).key`);
  const posted = await ev(`fetch("api/versions", { cache: "no-store" }).then(r => r.json()).then(d => fetch("api/versions", { method: "POST",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify({ photo: ${JSON.stringify(lastKey)}, state: { ...d.photos[P().key], activePresetId: null } }) }).then(r => r.ok))`);
  await open(PORTS[1]);
  await ev(`pickPhoto(PHOTOS.length - 1)`);
  const opensFirst = [await versions(), await look()].join(" ");
  await ev(`dial.setValues(defaultsFor(P())); pickPhoto(0)`);  // la ultima vuelve a verse como la entrega, para el 9
  check(posted && opensFirst === "Version 2*, Version 3 -0.4,150", "una foto sin version puesta abre en la primera", opensFirst);
  await ev(`state.compare = true; state.before[P().key] = store.getPresets(dial.id)[1].id; render()`);
  await tapVersion("Version 3");
  await deleteVersion("Version 3");
  check(await versions() === "Version 2*" && await look() === "-0.4,150", "borrar la que se ve pasa a la primera que queda, con sus valores", `${await versions()} ${await look()}`);
  const gone = await ev(`[state.before[P().key], [...$("beforeMenu").children].map(b => b.textContent).join("|"), $("beforeName").textContent, $("beforePick").disabled].join()`);
  check(gone === ",RAW original,RAW original,true", "borrar la version del antes lo vuelve al RAW; sin otra version, el rotulo no abre menu", gone);
  await ev(`state.compare = false; render()`);
  check(await saved(`s.presets.length === 1 && s.activePresetId === s.presets[0].id`), "el borrado se guarda");
  await open(PORTS[0]);
  check(await versions() === "Version 2*" && await look() === "-0.4,150", "y no vuelve en el primer puerto", await versions());
  // borrar la ultima vuelve a la base, con sus valores (los que tenia al guardar la 2)
  await deleteVersion("Version 2");
  check(await versions() === "Version 1*" && await look() === "0.5,70", "borrar todas vuelve la base (Version 1), con sus valores", `${await versions()} ${await look()}`);
  check(await saved(`s.presets.length === 0 && !s.activePresetId`), "y se guarda");
  // en la base, el nombre del archivo dice lo que cambio
  await ev(`dial.setValues({ "Under-eyes": ${allEyes(40)} })`);
  const plain = await ev(`post(keyOf(request()), new AbortController().signal).then(r => r.name)`);
  check(/^[\w-]+-adjusted-under-eyes-40-\d+x\d+\.png$/.test(plain), "en la base, el nombre dice lo que cambio", plain);

  // 8. exportar: el nombre lleva la version o lo que cambio; y el archivo es lo que se ve, en un recorte 1:1 con un
  // parche de ojeras entero adentro y ajustes en todo. La pantalla parte de la editada de 8 bits, con dither de hasta
  // 1,5 niveles contra la maestra de 16 que exporta el servidor, y los ajustes lo estiran: hasta 3 niveles, sin sesgo.
  // La matematica es la misma: con la misma entrada de 8 bits, el shader y recipe/adjust.py difieren en 1 nivel. El
  // archivo se compara en WebP (8 bits redondeados): un PNG de 16 bits, Chrome lo lee cortando bits (v >> 8)
  await tapButton("Save version");
  await tapVersion("Version 2");
  await ev(`dial.setValues({ "Under-eyes": ${allEyes(150)}, Light: { Exposure: 0.3, Brightness: 10, Contrast: 20, Highlights: -30, Shadows: 25, Whites: 10, Blacks: -10 },
                             Color: { Temperature: 15, Tint: -10, Vibrance: 20, Saturation: -10 } })`);
  await ev(`setOpt("size", 1024)`);
  await tap("#export");
  const ready = await until(`prepared?.key === keyOf(request())`, 30000);
  const exp = await ev(`({ name: prepared?.name, what: $("what").textContent, info: $("info").textContent })`);
  check(ready && /^[\w-]+-version-2-\d+x\d+\.png$/.test(exp.name) && exp.what === "Version 2" && /^\d+ × \d+ · 16-bit PNG · sRGB · [\d.]+ (KB|MB)$/.test(exp.info),
        "con la 2 puesta, el archivo y el resumen la nombran; abajo, la medida, el formato, sRGB y el peso", JSON.stringify(exp));
  // la vista previa no se agranda al pasar el puntero: para mirar de cerca esta el editor
  const pv0 = await page.rect("#previewCanvas");
  await page.mouse("mouseMoved", pv0.x + pv0.w * 0.3, pv0.y + pv0.h * 0.3);
  await sleep(300);
  const pv1 = await page.rect("#previewCanvas"), pvStyle = await ev(`$("preview").className + " " + getComputedStyle($("previewCanvas")).transform`);
  check(JSON.stringify(pv1) === JSON.stringify(pv0) && pvStyle === "preview none", "la vista previa no hace zoom al pasar el puntero", `${JSON.stringify(pv1)} ${pvStyle}`);
  // sin servidor: el aviso en el lugar del resumen y Download apagado (un clic no hace nada); vuelve al contestar
  await ev(`window.__fetch = fetch; window.fetch = (u, o) => String(u).startsWith("api/prepare") ? Promise.reject(new TypeError("Failed to fetch")) : __fetch(u, o)`);
  await ev(`setOpt("size", 2048)`);
  const warned = await until(`$("foot").dataset.state === "warn"`, 5000);
  const offline = await ev(`[$("info").textContent === OFFLINE, $("download").getAttribute("aria-disabled")].join()`);
  // otro cambio con el aviso puesto: el aviso se queda (se borraba hasta que el pedido volvia a fallar, y parpadeaba)
  const steady = await ev(`(setOpt("size", 4096), [$("foot").dataset.state, $("info").textContent === OFFLINE, $("download").getAttribute("aria-disabled")].join())`);
  await tap("#download");
  await sleep(200);
  const stayed = await ev(`dialog.open && $("download").textContent === "Download"`);
  await ev(`window.fetch = __fetch; setOpt("size", 1024)`);
  const recovered = await until(`$("foot").dataset.state === "" && $("download").getAttribute("aria-disabled") === "false" && /MB|KB/.test($("info").textContent)`, 30000);
  check(warned && offline === "true,true" && steady === "warn,true,true" && stayed && recovered,
        "sin servidor, el aviso y Download apagado, sin parpadear al cambiar algo; al volver, el resumen y Download", `${warned} ${offline} ${steady} ${stayed} ${recovered}`);
  await page.key("Escape", { keyCode: 27 });
  const parity = await ev(`(async () => {
    const p = P(), e = p.eyes[0], pad = 48;
    const x = Math.max(e.x - pad, 0), y = Math.max(e.y - pad, 0), w = Math.min(e.x + e.w + pad, p.w) - x, h = Math.min(e.y + e.h + pad, p.h) - y;
    loadFull(p);
    while (!renderer.ready(fullUrl(p, "edit")) || !renderer.ready(fullUrl(p, "raw"))) await new Promise(r => setTimeout(r, 100));
    const s = scene(p, { cx: x + w / 2, cy: y + h / 2, size: w }, w, { scale: 1, dither: false, look: liveLook() });
    if (!s.full || !sceneReady(s)) return { error: "sin la entera" };
    const mine = renderer.read(s, w, h).slice();
    const r = await post(JSON.stringify({ ...request(), box: [x, y, w, h], size: "full", format: "webp" }), new AbortController().signal);
    const bmp = await createImageBitmap(await (await fetch("api/file/" + r.id)).blob(), { colorSpaceConversion: "none", premultiplyAlpha: "none" });
    const c = new OffscreenCanvas(w, h).getContext("2d");
    c.drawImage(bmp, 0, 0);
    const theirs = c.getImageData(0, 0, w, h).data;
    let max = 0, sum = 0, bias = 0;
    for (let i = 0; i < mine.length; i += 4) for (let k = 0; k < 3; k++) {
      const d = mine[i + k] - theirs[i + k]; max = Math.max(max, Math.abs(d)); sum += Math.abs(d); bias += d;
    }
    const n = w * h * 3;
    return { key: p.key, size: [bmp.width, bmp.height].join("x"), max, mean: sum / n, bias: bias / n };
  })()`);
  check(!parity.error && parity.max <= 3 && parity.mean < 0.5 && Math.abs(parity.bias) < 0.1, "el archivo es lo que se ve (1:1, ojeras al 150 % y todos los ajustes)",
        `(${parity.error ?? `${parity.key} ${parity.size}: max ${parity.max}, media ${parity.mean.toFixed(3)}, sesgo ${parity.bias.toFixed(3)}`})`);

  // 8b. el panel de export: Format, Size y Crop, sin presets, sin renglones de ayuda y sin Reset (pedido del fotografo, 2026-10-19)
  const seg = (id, text) => `[...$(${JSON.stringify(id)}).querySelectorAll("button")].find(b => b.textContent === ${JSON.stringify(text)})`;
  const preparedNow = () => until(`prepared?.key === keyOf(request()) && $("foot").dataset.state === ""`, 30000);
  await tap("#export");
  await preparedNow();
  const fields = await ev(`(() => {
    const side = document.querySelector("#dialog .side"), names = id => [...$(id).querySelectorAll("button")].map(b => b.textContent).join();
    return { labels: [...side.querySelectorAll(".field > span")].map(s => s.textContent).join(), format: names("format"), size: names("size"), crop: names("area"),
             lines: [...side.querySelectorAll("p, small, .hint")].map(p => p.id).join(), gone: /Reset|Visible area|Long edge|preset/i.test(side.textContent),
             buttons: [...side.querySelectorAll("button")].filter(b => !b.closest(".seg")).map(b => b.id).join() };
  })()`);
  check(fields.labels === "Format,Size,Crop" && fields.format === "PNG,TIFF,WebP,JPG" && fields.size === "1024,2048,4096,Full" &&
        fields.crop === "Free,1:1,4:5,3:2,16:9" && fields.lines === "what,info" && !fields.gone && fields.buttons === "close,download",
        "export: Format, Size y Crop con sus opciones; sin presets, ayudas ni Reset", JSON.stringify(fields));
  // cada formato: el resumen (medida del archivo, bits, formato, sRGB y peso), la extension, y el pedido lleva box, size y format.
  // El JPG se mira en memoria (empieza con FF D8): nunca se escribe en el proyecto
  for (const [id, label, ext, bits] of [["png", "PNG", "png", 16], ["tiff", "TIFF", "tif", 16], ["webp", "WebP", "webp", 8], ["jpeg", "JPG", "jpg", 8]]) {
    await tapAt(seg("format", label));
    const done = await preparedNow();
    const got = await ev(`(async () => {
      const req = JSON.parse(prepared.key), [w, h] = outDims();
      const head = ${id === "jpeg"} ? [...new Uint8Array(await (await fetch("api/file/" + prepared.id)).arrayBuffer()).slice(0, 2)].join() : "";
      return { info: $("info").textContent, want: w + " × " + h, name: prepared.name, bits: prepared.bits, head, pressed: ${seg("format", label)}.getAttribute("aria-pressed"),
               req: JSON.stringify(req.box) === JSON.stringify(box()) && req.size === opts.size && req.format === ${JSON.stringify(id)} };
    })()`);
    const line = new RegExp(`^${got.want} · ${bits}-bit ${label} · sRGB · [\\d.]+ (KB|MB)$`);
    check(done && line.test(got.info) && got.name.endsWith(`.${ext}`) && got.bits === bits && got.req && got.pressed === "true" && (id !== "jpeg" || got.head === "255,216"),
          `export en ${label}: el resumen, la extension y el pedido con box, size y format`, JSON.stringify(got));
  }
  // el aviso de un WebP o un JPG pesado para una pagina (mas de 15 MB), en ambar; un PNG igual de pesado no lo lleva
  const heavy = await ev(`(() => {
    const out = [];
    for (const f of ["webp", "jpeg", "png"]) {
      opts.format = f; info({ w: 6000, h: 4000, bits: 8, bytes: 2e7 });
      out.push([f, $("info").textContent.endsWith(" · heavy for a web page"), $("info").classList.contains("heavy"), getComputedStyle($("info")).color].join(":"));
    }
    return out.join(" ");
  })()`);
  await tapAt(seg("format", "PNG"));
  check(heavy === "webp:true:true:rgb(255, 179, 64) jpeg:true:true:rgb(255, 179, 64) png:false:false:rgb(142, 142, 147)",
        "WebP y JPG de mas de 15 MB avisan en ambar; PNG no", heavy);

  // el recorte: cada proporcion es el marco mas grande que entra, centrado en las caras (adentro de la foto)
  const frameOf = () => ev(`(() => { const p = P(), [x, y, w, h] = box(); return { x, y, w, h, pw: p.w, ph: p.h, mode: cropOf(p).mode,
    saved: JSON.parse(localStorage.getItem("studio-export-v1")).crops?.[p.key] ?? null }; })()`);
  check(JSON.stringify(await frameOf()).startsWith(`{"x":0,"y":0,"w":${await ev("P().w")},"h":${await ev("P().h")},`), "sin tocar, el recorte es la foto entera");
  for (const [label, r] of [["1:1", 1], ["4:5", 4 / 5], ["3:2", 3 / 2], ["16:9", 16 / 9]]) {
    await tapAt(seg("area", label));
    const f = await frameOf(), [fx, fy] = await ev(`faceCenter(P())`);
    const clamp = (v, a, b) => Math.min(Math.max(v, a), b);
    const cx = clamp(fx * f.pw, f.w / 2, f.pw - f.w / 2), cy = clamp(fy * f.ph, f.h / 2, f.ph - f.h / 2);
    const ok = Math.abs(f.w - f.h * r) <= 1 && (Math.abs(f.w - f.pw) <= 1 || Math.abs(f.h - f.ph) <= 1) &&
               Math.abs(f.x + f.w / 2 - cx) <= 1 && Math.abs(f.y + f.h / 2 - cy) <= 1 && f.mode === label && f.saved?.mode === label;
    check(ok, `crop ${label}: el marco mas grande, centrado en las caras, guardado por foto`, JSON.stringify(f));
  }
  // donde esta el marco en la pantalla (sus bordes, en px de CSS) y cuantos px de la foto es un px de la pantalla
  const onScreen = () => ev(`(() => { const r = $("previewCanvas").getBoundingClientRect(), G = pvGeom(), k = dpr() / G.z, [X, Y, W, H] = box();
    return { l: r.left + (X - G.x0) / k, t: r.top + (Y - G.y0) / k, r: r.left + (X + W - G.x0) / k, b: r.top + (Y + H - G.y0) / k, k }; })()`);
  // adentro, arrastrar lo mueve sin cambiar su tamano (hacia donde haya lugar)
  let s0 = await onScreen(), f0 = await frameOf();
  const down = f0.ph - f0.h - f0.y > f0.y ? 1 : -1;
  await page.drag([(s0.l + s0.r) / 2, (s0.t + s0.b) / 2], [(s0.l + s0.r) / 2, (s0.t + s0.b) / 2 + 40 * down]);
  let f1 = await frameOf();
  const wantY = Math.min(Math.max(f0.y + 40 * down * s0.k, 0), f0.ph - f0.h);
  check(f1.w === f0.w && f1.h === f0.h && f1.x === f0.x && Math.abs(f1.y - wantY) <= s0.k && f1.y !== f0.y && f1.saved.mode === "16:9",
        "arrastrar adentro del marco lo mueve", `${f0.y} → ${f1.y} (esperado ${wantY.toFixed(0)})`);
  // una esquina con proporcion: achica, la proporcion se queda y la esquina de enfrente no se mueve
  s0 = await onScreen(); f0 = f1;
  await page.drag([s0.l + 1, s0.t + 1], [s0.l + 61, s0.t + 41]);
  f1 = await frameOf();
  check(f1.w < f0.w - 100 && Math.abs(f1.w - f1.h * 16 / 9) <= 1 && Math.abs(f1.x + f1.w - (f0.x + f0.w)) <= 1 && Math.abs(f1.y + f1.h - (f0.y + f0.h)) <= 1,
        "la esquina achica el marco con su proporcion y la de enfrente queda", `${JSON.stringify(f0)} → ${JSON.stringify(f1)}`);
  // Free suelta la proporcion y deja el marco; un borde estira solo su lado
  await tapAt(seg("area", "Free"));
  f0 = await frameOf(); s0 = await onScreen();
  check(f0.mode === "free" && f0.x === f1.x && f0.w === f1.w, "Free deja el marco como estaba", JSON.stringify(f0));
  // 3 px adentro: el borde puede caer justo en el borde del lienzo, y ahi el puntero ya esta afuera
  await page.drag([s0.r - 3, (s0.t + s0.b) / 2], [s0.r - 33, (s0.t + s0.b) / 2]);
  f1 = await frameOf();
  check(Math.abs(f1.w - (f0.w - 30 * s0.k)) <= s0.k && f1.x === f0.x && f1.y === f0.y && f1.h === f0.h, "en Free, el borde derecho estira solo el ancho",
        `${f0.w} → ${f1.w} (esperado ${(f0.w - 30 * s0.k).toFixed(0)})`);
  // las flechas, con el foco en la vista previa, corren el marco un 2 % del lado largo; con Shift, un 10 % (hacia
  // donde haya lugar para los dos pasos)
  await ev(`$("previewCanvas").focus()`);
  const arrows = [], versionBefore = await versions();
  f0 = await frameOf();
  const dir = f0.ph - f0.h - f0.y > f0.y ? 1 : -1;
  for (const shift of [false, true]) {
    f0 = await frameOf();
    await page.key(dir > 0 ? "ArrowDown" : "ArrowUp", { keyCode: dir > 0 ? 40 : 38, shift });
    f1 = await frameOf();
    const d = Math.max(f0.pw, f0.ph) * (shift ? 0.1 : 0.02) * dir, want = Math.min(Math.max(f0.y + d, 0), f0.ph - f0.h);
    arrows.push(Math.abs(f1.y - want) <= 1 && f1.y !== f0.y && f1.x === f0.x && f1.w === f0.w ? "ok" : `${f0.y}→${f1.y}≠${want.toFixed(0)}`);
  }
  check(arrows.join() === "ok,ok" && await ev("dialog.open && state.photo") === 0 && await versions() === versionBefore,
        "las flechas y Shift corren el marco (2 y 10 %) sin cambiar de foto ni de version", arrows.join());
  // por foto, y vuelve al recargar
  const kept = JSON.stringify(await frameOf());
  await page.key("Escape", { keyCode: 27 });
  await ev(`pickPhoto(1)`);
  const otherCrop = await ev(`box().join() === [0, 0, P().w, P().h].join()`);
  await ev(`pickPhoto(0)`);
  const cropBack = JSON.stringify(await frameOf());
  await open(PORTS[0]);
  check(otherCrop && cropBack === kept && JSON.stringify(await frameOf()) === kept, "el recorte es de cada foto y vuelve al recargar", `${otherCrop} ${kept === cropBack}`);

  // la vista previa: ⌘ + rueda acerca donde esta el puntero, la rueda sola recorre (solo acercado), doble clic y la
  // pastilla van al 100 % y vuelven a Fit, ⌘+ ⌘- ⌘0 son suyos con el panel abierto, y al reabrir vuelve a Fit
  await tap("#export");
  await preparedNow();
  const pvState = () => ev(`(() => { const G = pvGeom(); return { label: $("pvZoom").textContent, on: pview !== null, z: G.z, cx: G.cx, cy: G.cy }; })()`);
  const under = (x, y) => ev(`(() => { const r = $("previewCanvas").getBoundingClientRect(), G = pvGeom(), k = dpr() / G.z;
    return [G.x0 + (${x} - r.left) * k, G.y0 + (${y} - r.top) * k]; })()`);
  const pc = await page.rect("#previewCanvas"), at = [pc.x + pc.w * 0.3, pc.y + pc.h * 0.4];
  const mainView = await ev(`JSON.stringify(view())`);
  let z0 = await pvState();
  await page.wheel(...at, 60);
  const fitWheel = await pvState();
  const p0 = await under(...at);
  for (let i = 0; i < 6; i++) await page.wheel(...at, -20, { modifiers: 4 });
  await sleep(100);
  const p1 = await under(...at), zin = await pvState();
  check(z0.label === "Fit" && !fitWheel.on && zin.on && zin.z > z0.z * 1.2 && /^\d+%$/.test(zin.label) && Math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 2,
        "vista previa: ⌘ + rueda acerca con el punto del puntero quieto; la rueda sola en Fit no hace nada", `${z0.label} → ${zin.label} (${p0.map(Math.round)} → ${p1.map(Math.round)})`);
  await page.wheel(...at, 80);
  await sleep(100);
  const panned = await pvState();
  check(panned.z === zin.z && panned.cy !== zin.cy, "acercada, la rueda sola recorre", `${zin.cy.toFixed(0)} → ${panned.cy.toFixed(0)}`);
  // desde Fit: acercada (a cualquier zoom), el doble clic vuelve a Fit
  await ev(`pview = null; drawPreview()`);
  await page.click(...at, 2);
  await sleep(150);
  const dbl1 = (await pvState()).label;
  await page.click(...at, 2);
  await sleep(150);
  const dbl0 = (await pvState()).label;
  await tap("#pvZoom"); await sleep(150);
  const pill1 = (await pvState()).label;
  await tap("#pvZoom"); await sleep(150);
  const pill0 = (await pvState()).label;
  check(dbl1 === "100%" && dbl0 === "Fit" && pill1 === "100%" && pill0 === "Fit", "doble clic y la pastilla van al 100 % y vuelven a Fit", `${dbl1} ${dbl0} · ${pill1} ${pill0}`);
  const pvSteps = [];
  for (const [key, code, keyCode] of [["=", "Equal", 187], ["=", "Equal", 187], ["-", "Minus", 189], ["0", "Digit0", 48]]) {
    await page.key(key, { code, keyCode, meta: true }); await sleep(150); pvSteps.push((await pvState()).label);
  }
  check(pvSteps.join() === "50%,100%,50%,Fit" && await ev(`JSON.stringify(view())`) === mainView && await ev(`$("zoom").textContent`) === "Fit",
        "con el panel abierto, ⌘+ ⌘- ⌘0 son de la vista previa y la foto de atras no se mueve", pvSteps.join());
  // nunca mas detalle que el archivo: al 100 %, la imagen leida tiene los pixeles que va a tener el archivo en ese pedazo
  await tap("#pvZoom");
  const detail = {};
  for (const sz of [1024, "full"]) {
    await ev(`setOpt("size", ${JSON.stringify(sz)})`);
    const want = `(() => { const G = pvGeom(), [ow] = outDims(), [, , bw] = box(); return Math.max(1, Math.round(G.CW * Math.min(G.z, ow / bw) / G.z)); })()`;
    const okSize = await until(`pvImage?.width === ${want}`, 30000);
    detail[sz] = [okSize, await ev("pvImage?.width"), await ev(want), await ev("pvGeom().CW")].join(":");
  }
  const [w1024, wFull, cw] = [Number(detail[1024].split(":")[1]), Number(detail.full.split(":")[1]), Number(detail.full.split(":")[3])];
  check(detail[1024].startsWith("true") && detail.full.startsWith("true") && w1024 < wFull && wFull < cw,
        "la vista previa nunca muestra mas detalle que el archivo con ese Size", JSON.stringify(detail));
  const pvBefore = (await pvState()).label;
  await page.key("Escape", { keyCode: 27 });
  await tap("#export");
  await sleep(200);
  const reopened = await pvState();
  check(pvBefore === "100%" && reopened.label === "Fit" && !reopened.on, "al reabrir el panel, la vista previa vuelve a Fit", `${pvBefore} → ${reopened.label}`);
  await page.key("Escape", { keyCode: 27 });
  await ev(`setOpt("crops", {}); setOpt("size", 1024)`);

  // 9. a pantalla completa, los parches de ojeras no dejan borde: al 0 y al tope, contra la entrega, el borde del
  // parche (3 px hacia adentro) queda igual; el parche entra como diferencia contra su base. Antes de eso daba hasta 22
  // niveles. A 3 px de pantalla (13 de la foto) ya asoma la correccion al tope, filtrada: a lo sumo un nivel suelto
  await ev(`dial.setValues(defaultsFor(P()))`);
  const seams = await ev(`(() => {
    const out = [], keep = settings;
    for (let i = 0; i < PHOTOS.length; i++) {
      pickPhoto(i);
      const p = P(), v = view(), W = canvas.width, H = canvas.height, k = W / v.size, x0 = v.cx - v.size / 2, y0 = v.cy - (v.size * p.h) / p.w / 2;
      const at = level => { settings = { ...keep, levels: Object.fromEntries(p.eyes.map(e => [e.face, level])) }; return renderer.read(scene(p, v, W, { dither: false }), W, H).slice(); };
      const base = at(EYE_DEFAULT);
      for (const level of [0, EYE_MAX]) {
        const px = at(level);
        let max = 0, sum = 0, n = 0;
        for (const e of p.eyes) {
          const L = (e.x - x0) * k, T = (e.y - y0) * k, R = L + e.w * k, B = T + e.h * k;
          for (let y = Math.max(Math.floor(T), 0); y < Math.min(Math.ceil(B), H); y++)
            for (let x = Math.max(Math.floor(L), 0); x < Math.min(Math.ceil(R), W); x++) {
              if (Math.min(x + 0.5 - L, R - x - 0.5, y + 0.5 - T, B - y - 0.5) > 3) continue;
              for (let c = 0; c < 3; c++) { const d = Math.abs(px[(y * W + x) * 4 + c] - base[(y * W + x) * 4 + c]); max = Math.max(max, d); sum += d; n++; }
            }
        }
        out.push({ key: p.key, level, max, mean: sum / Math.max(n, 1) });
      }
    }
    settings = keep;
    pickPhoto(0);
    return out;
  })()`);
  for (const s of seams) check(s.max <= 1 && s.mean < 0.01, `${s.key} al ${s.level} %: sin borde en el parche`, `(max ${s.max}, media ${s.mean.toFixed(4)})`);

  // 10. la entera se pide sola al quedarse en una foto y se suelta la de las otras; doble clic al 100 % la usa
  await ev(`pickPhoto(PHOTOS.length - 1)`);
  const full = await until(`renderer.ready(fullUrl(P(), "edit")) && renderer.ready(fullUrl(P(), "raw"))`, 30000);
  check(full && !await ev(`PHOTOS.some(p => p !== P() && (renderer.ready(fullUrl(p, "edit")) || renderer.ready(fullUrl(p, "raw"))))`),
        "la entera de esta foto llega sola y la de las otras se suelta");
  const fr = await page.rect("#frame");
  await page.click(fr.x + fr.w * 0.5, fr.y + fr.h * 0.3, 2);
  await sleep(700);
  check(await ev(`view().size < P().w / 2 && scene(P(), view(), canvas.width).full && !$("loading").classList.contains("show")`), "doble clic: al 100 %, con la entera");
  await page.shot("editor-prueba-zoom-100");
  for (let i = 0; i < await ev("PHOTOS.length"); i++) { await ev(`pickPhoto(${i})`); await sleep(150); await page.shot(`editor-prueba-${await ev("P().key")}`); }

  // 11. el zoom dice Fit o el porcentaje. El pellizco y ⌘ + rueda, en cualquier parte, agrandan la foto y nunca la
  // pagina; el boton va al 100 % y vuelve como el doble clic, y ⌘+ ⌘- ⌘0 van por los escalones
  const zoomState = () => ev(`({ label: $("zoom").textContent, zoomed: view().size < P().w - 0.5, page: visualViewport.scale, dpr: devicePixelRatio })`);
  const pageOk = z => z.page === 1 && z.dpr === 2;
  const toFit = () => ev(`(stopAnim(), setView(fitView(P())))`);
  await ev(`pickPhoto(0)`); await toFit();
  let z = await zoomState();
  check(z.label === "Fit" && !z.zoomed, "con la foto entera, el zoom dice Fit", z.label);
  const stage = await page.rect("#stage"), pill = await page.rect("#zoom"), side = await page.rect("#controls"), photo = await page.rect("#frame");
  check(photo.y + photo.h + 8 <= pill.y && pill.y + pill.h <= stage.y + stage.h - 8, "el boton del zoom no toca la foto ni el borde", JSON.stringify(pill));
  await page.pinch(stage.x + 12, stage.y + 12, 2); await sleep(400);
  z = await zoomState();
  check(z.zoomed && pageOk(z) && /^\d+%$/.test(z.label), "pellizcar en el margen agranda la foto, no la pagina", JSON.stringify(z));
  await toFit();
  for (let i = 0; i < 8; i++) await page.wheel(pill.x + pill.w / 2, pill.y + pill.h / 2, -10, { modifiers: 2 });
  await sleep(200); z = await zoomState();
  check(z.zoomed && pageOk(z), "ctrl + rueda sobre el boton del zoom tambien", JSON.stringify(z));
  await toFit();
  for (let i = 0; i < 8; i++) await page.wheel(side.x + side.w / 2, side.y + 200, -10, { modifiers: 4 });
  await sleep(200); z = await zoomState();
  check(z.zoomed && pageOk(z), "y ⌘ + rueda sobre el panel, hacia el centro", JSON.stringify(z));
  await toFit(); await sleep(50);
  await tap("#zoom"); await sleep(500);
  const there = (await zoomState()).label;
  await tap("#zoom"); await sleep(500);
  const back = (await zoomState()).label;
  check(there === "100%" && back === "Fit", "el boton va al 100 % y vuelve a Fit", `${there} → ${back}`);
  const steps = [];
  for (const [key, code, keyCode] of [["=", "Equal", 187], ["=", "Equal", 187], ["-", "Minus", 189], ["0", "Digit0", 48]]) {
    await page.key(key, { code, keyCode, meta: true }); await sleep(450); steps.push((await zoomState()).label);
  }
  z = await zoomState();
  check(steps.join() === "50%,100%,50%,Fit" && pageOk(z), "⌘+ ⌘- ⌘0 van por Fit, 50 y 100 % sin agrandar la pagina", steps.join());
  await ev(`(() => { const r = frame.getBoundingClientRect(), at = { clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 };
    const g = (type, scale) => frame.dispatchEvent(Object.assign(new Event(type, { bubbles: true, cancelable: true }), { scale, ...at }));
    g("gesturestart", 1); g("gesturechange", 2); g("gestureend", 2); })()`);
  await sleep(400); z = await zoomState();
  check(z.zoomed, "el pellizco de Safari (gesture*) tambien agranda la foto", z.label);
  await toFit();

  // 12. la barra del antes y despues: queriendo correr la barra nunca se corre la foto. Con la foto entera no hay foto
  // que mover: se agarra desde cualquier parte y viene al puntero. Con zoom se agarra en su zona de 44 px, sin saltar, y
  // fuera de ella se mueve la foto. En los bordes la perilla queda entera y se agarra, y el rotulo que taparia se va
  {
    await tap("#compareView");
    await ev(`state.split = 0.5; paintSplit(); draw()`);
    const at = () => ev(`({ split: state.split, view: JSON.stringify(view()) })`);
    let fr = await page.rect("#frame");
    const still = (await at()).view;
    await page.drag([fr.x + fr.w * 0.15, fr.y + fr.h * 0.7], [fr.x + fr.w * 0.3, fr.y + fr.h * 0.75]);
    await sleep(250);
    const fitted = await at();
    check(Math.abs(fitted.split - 0.3) < 0.005 && fitted.view === still, "con la foto entera, arrastrar lejos de la barra la trae al puntero y la foto no se mueve",
          `${fitted.split.toFixed(3)}${fitted.view === still ? "" : " " + fitted.view}`);

    await ev(`state.split = 0.5; paintSplit(); stopAnim(); setView(clampView({ cx: P().w / 2, cy: P().h / 2, size: oneToOne() }))`);
    await sleep(100);
    fr = await page.rect("#frame");
    const zoomed = (await at()).view, line = fr.x + fr.w * 0.5;
    await page.drag([line + 12, fr.y + fr.h * 0.3], [line + 72, fr.y + fr.h * 0.3]);
    await sleep(100);
    const band = await at();
    check(Math.abs(band.split - (0.5 + 60 / fr.w)) < 0.003 && band.view === zoomed, "con zoom, agarrar la barra 12 px al costado la corre sin saltar y la foto no se mueve",
          `${band.split.toFixed(3)} (esperado ${(0.5 + 60 / fr.w).toFixed(3)})`);
    await page.drag([fr.x + fr.w * 0.2, fr.y + fr.h * 0.5], [fr.x + fr.w * 0.2 + 80, fr.y + fr.h * 0.5 + 40]);
    await sleep(700);
    const panned = await at();
    check(panned.split === band.split && panned.view !== zoomed, "con zoom, fuera de la barra se mueve la foto y la barra queda", `${band.split.toFixed(3)} → ${panned.split.toFixed(3)}`);

    await toFit();
    await ev(`state.split = 0; paintSplit(); draw()`);
    fr = await page.rect("#frame");
    const knob0 = await page.rect("#knob"), stage0 = await page.rect("#stage");
    const grip = await ev(`document.elementFromPoint(${knob0.x + 3}, ${knob0.y + knob0.h / 2})?.closest(".knob") === $("knob")`);
    await page.drag([knob0.x + 3, knob0.y + knob0.h / 2], [knob0.x + 93, knob0.y + knob0.h / 2]);
    await sleep(100);
    const edge = await at();
    check(knob0.x < fr.x && knob0.x >= stage0.x && grip && Math.abs(edge.split - 90 / fr.w) < 0.003,
          "en el borde, la perilla queda entera afuera de la foto y se agarra de su mitad de afuera", `${knob0.x.toFixed(1)} < ${fr.x.toFixed(1)} · ${grip} · ${edge.split.toFixed(3)}`);
    const covers = async s => { await ev(`state.split = ${s}; paintSplit(); draw()`); return ev(`[$("beforePick"), $("afterLabel")].map(l => l.classList.contains("covered")).join()`); };
    const ends = [await covers(0), await covers(0.5), await covers(1)].join(" · ");
    check(ends === "true,false · false,false · false,true", "en los bordes se va el rotulo que la barra taparia; en el medio estan los dos", ends);
    await ev(`state.split = 0.5; paintSplit(); draw()`);
    const knob5 = await page.rect("#knob");
    await page.click(knob5.x + knob5.w / 2, knob5.y + knob5.h / 2, 2);
    await sleep(500);
    const onKnob = (await zoomState()).label;
    await page.click(knob5.x + knob5.w / 2, fr.y + fr.h * 0.3, 2);
    await sleep(500);
    const onLine = (await zoomState()).label;
    check(onKnob === "Fit" && onLine === "100%", "doble clic en la perilla no hace zoom; en la linea, como en el resto de la foto, si", `${onKnob} · ${onLine}`);
    await toFit();
    await tap("#compareView");
  }

  // 13. el fondo. La carpeta Background mueve solo la pared: la gente queda como sin fondo, al bit; arrastrar su
  // Exposure con el mouse llega al render; el RAW no lo lleva. A 1:1, el lienzo es el archivo del servidor en el borde del
  // pelo, en el hueco entre el brazo y el cuerpo y en la pared pura de la derecha (con la caida), con los ajustes de la
  // foto tambien puestos: hasta 3 niveles y sin sesgo, como el resto del export. La media llega a 0,63 porque la ganancia
  // de la pared (~1,5 aca) estira el dither de la editada de 8 bits: recipe/backdrop.py con las mismas entradas de 8 bits
  // da 0,40, 0,52 y 0,63 contra la maestra (2026-10-15), lo mismo que el shader
  {
    await ev(`pickPhoto(0); state.raw = false; state.compare = false; render(); dial.setValues(defaultsFor(P())); document.activeElement?.blur()`);
    await toFit();
    const bgFolder = `[...document.querySelectorAll("#controls .dialkit-folder")].find(f => f.querySelector(".dialkit-folder-header-top")?.textContent.trim() === "Background")`;
    const bgPanel = await ev(`[...${bgFolder}.querySelectorAll(".dialkit-slider")].map(s => ["aria-label", "aria-valuemin", "aria-valuemax", "aria-valuenow"].map(a => s.getAttribute(a)).join(":")).join()`);
    check(bgPanel === "Exposure:-2:2:0,Evenness:0:100:0,Smoothing:0:100:0,Falloff:0:100:0,Temperature:-100:100:0,Tint:-100:100:0,Saturation:-100:100:0",
          "la carpeta Background: siete controles, en 0", bgPanel);
    // a la medida del lienzo, sin dither: la cara (adentro del ovalo) y un cuadro de pared pura arriba a la derecha
    const fitPx = `(() => { const p = P(), v = view(), W = canvas.width, H = canvas.height; return { W, H, k: W / v.size, x0: v.cx - v.size / 2, y0: v.cy - (v.size * p.h) / p.w / 2,
      px: renderer.read(scene(p, v, W, { dither: false }), W, H).slice() }; })()`;
    const zone = (f, [x, y, w, h]) => {
      const out = [];
      for (let j = Math.ceil((y - f.y0) * f.k); j < Math.floor((y + h - f.y0) * f.k); j++)
        for (let i = Math.ceil((x - f.x0) * f.k); i < Math.floor((x + w - f.x0) * f.k); i++) out.push((j * f.W + i) * 4);
      return out;
    };
    const FACE = [1360 - 125, 1280 - 165, 250, 330], WALL = [2585, 100, 256, 256];
    const off = await ev(`(() => { const f = ${fitPx}; return { ...f, px: [...f.px] }; })()`);
    const ex = await ev(`(() => { const s = ${bgFolder}.querySelector('.dialkit-slider[aria-label="Exposure"]'); s.scrollIntoView({ block: "nearest" });
      const r = s.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`);
    await page.drag([ex.x + ex.w / 2, ex.y + ex.h / 2], [ex.x + ex.w * 0.8, ex.y + ex.h / 2]);
    await sleep(500);
    const on = await ev(`(() => { const f = ${fitPx}; return { ...f, px: [...f.px], bg: settings.background.exposure, light: settings.adjust.exposure, u: bgU.on }; })()`);
    const diff = (z, f) => z.map(i => (Math.abs(on.px[i] - off.px[i]) + Math.abs(on.px[i + 1] - off.px[i + 1]) + Math.abs(on.px[i + 2] - off.px[i + 2])) / 3).reduce(f, 0);
    const face = zone(on, FACE), wall = zone(on, WALL);
    const faceMax = diff(face, (a, d) => Math.max(a, d)), wallLift = diff(wall, (a, d) => a + d) / wall.length;
    check(on.bg > 0.5 && on.light === 0 && on.u && faceMax === 0 && wallLift > 10,
          `arrastrar Exposure de Background a ${on.bg} aclara la pared y no la cara`, `(cara: max ${faceMax}; pared: +${wallLift.toFixed(1)} niveles)`);
    const rawBg = await ev(`(() => { state.raw = true; render(); const s = scene(P(), view(), 96); state.raw = false; render(); return [s.show, s.bg.on].join(); })()`);
    check(rawBg === "1,false", "el RAW no lleva el fondo", rawBg);

    await ev(`dial.setValues({ Light: { Exposure: 0.3, Brightness: 10, Contrast: 20, Highlights: -30, Shadows: 25, Whites: 10, Blacks: -10 },
                               Color: { Temperature: 15, Tint: -10, Vibrance: 20, Saturation: -10 },
                               Background: { Exposure: 0.45, Evenness: 65, Falloff: 30, Temperature: 40, Tint: -12, Saturation: -100 } })`);
    const BOXES = [["pelo", 848, 438, 1024, 1024], ["hueco", 3365, 3765, 120, 160], ["pared", ...WALL]];
    const bgParity = await ev(`(async () => {
      const p = P(), out = [];
      loadFull(p, true);
      while (![fullUrl(p, "edit"), fullUrl(p, "raw"), layerUrl(p, true), lightUrl(p)].every(renderer.ready)) await new Promise(r => setTimeout(r, 100));
      const capa = await createImageBitmap(await (await fetch(layerUrl(p, true))).blob(), { colorSpaceConversion: "none", premultiplyAlpha: "none" });
      for (const [name, x, y, w, h] of ${JSON.stringify(BOXES)}) {
        const at = look => { const s = scene(p, { cx: x + w / 2, cy: y + h / 2, size: w }, w, { scale: 1, dither: false, look });
                             return s.full && (!s.bg.on || s.layer === layerUrl(p, true)) && sceneReady(s) ? renderer.read(s, w, h).slice() : null; };
        const mine = at(liveLook()), plain = at({ ...liveLook(), bg: BG_OFF });
        if (!mine || !plain) return [{ name, error: "sin la entera" }];
        const r = await post(JSON.stringify({ ...request(), box: [x, y, w, h], size: "full", format: "webp" }), new AbortController().signal);
        const bmp = await createImageBitmap(await (await fetch("api/file/" + r.id)).blob(), { colorSpaceConversion: "none", premultiplyAlpha: "none" });
        const c = new OffscreenCanvas(w, h).getContext("2d");
        c.drawImage(bmp, 0, 0);
        const theirs = c.getImageData(0, 0, w, h).data;
        c.clearRect(0, 0, w, h);
        c.drawImage(capa, x, y, w, h, 0, 0, w, h);
        const alpha = c.getImageData(0, 0, w, h).data;
        let max = 0, sum = 0, bias = 0, people = 0, peopleMax = 0, wall = 0, lift = 0;
        for (let i = 0; i < mine.length; i += 4) {
          for (let k = 0; k < 3; k++) { const d = mine[i + k] - theirs[i + k]; max = Math.max(max, Math.abs(d)); sum += Math.abs(d); bias += d; }
          if (alpha[i + 3] === 255) { people++; for (let k = 0; k < 3; k++) peopleMax = Math.max(peopleMax, Math.abs(mine[i + k] - plain[i + k])); }
          if (alpha[i + 3] === 0) { wall++; lift += (mine[i] + mine[i + 1] + mine[i + 2] - plain[i] - plain[i + 1] - plain[i + 2]) / 3; }
        }
        const n = w * h * 3;
        out.push({ name, backdrop: r.backdrop, max, mean: +(sum / n).toFixed(3), bias: +(bias / n).toFixed(3), people, peopleMax, wall, lift: +(wall ? lift / wall : 0).toFixed(1) });
      }
      capa.close();
      return out;
    })()`);
    for (const b of bgParity)
      check(!b.error && b.backdrop === true && b.max <= 3 && b.mean < 0.7 && Math.abs(b.bias) < 0.1 && b.peopleMax === 0 &&
            ({ pelo: b.wall > 0 && b.people > 0, pared: b.wall === 256 * 256 }[b.name] ?? true),
            `fondo a 1:1, ${b.name}: el lienzo es el archivo, la gente queda como sin fondo`, JSON.stringify(b));
    await page.shot("editor-prueba-fondo");
    // una version guarda su fondo, y el antes y despues lo dibuja
    await tapButton("Save version");
    const kept = await ev(`(() => { const v = store.getPresets(dial.id).at(-1); return [v.values["Background.Falloff"], versionLook(v.id).bg.on].join(); })()`);
    check(kept === "30,true", "Save version guarda el fondo", kept);
    await tapButton("Reset");
    check(await ev(`BG_KEYS.every(k => settings.background[k] === 0) && bgU === BG_OFF`), "Reset apaga el fondo");
    await ev(`pickPhoto(1)`);
    check(!await ev(`renderer.ready(layerUrl(PHOTOS[0], true))`), "al cambiar de foto, la capa entera de la otra se suelta");
    await ev(`pickPhoto(0)`);
  }

  check(!await ev("saveWarned"), "ningun guardado fallo");
  console.log("errores de consola:", page.errors.length ? page.errors : "ninguno");
  if (page.errors.length) failures++;
} catch (err) {
  console.log("FAIL", err.stack);
  failures++;
} finally {
  await page?.close();
  await Promise.all(servers.map(s => s.stop()));
}
console.log(failures ? `${failures} fallas` : "todo bien");
process.exit(failures ? 1 : 0);
