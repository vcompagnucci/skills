---
name: photo-retouch
description: Retouching RAW photos with classical tools, measured against the camera original or a reference look, and optionally a local editor to review and export them. Use when RAF/RAW files arrive, when asked to retouch skin, fix light, color or the wall, match a reference style, re-render or export a photo project, build or change its editor, or answer what was touched or whether everything is saved.
effort: high
---

# Photo retouch

The method a photographer and an agent arrived at over two studio projects (portraits and a team shoot), correction by correction. Validated on studio portraits on a grey seamless wall: Fujifilm X-Trans RAF, flash. For outdoor shots or colored backgrounds, say the method is untested there before starting.

Projects live in one root folder, `$PHOTO_ROOT` (default `~/PHOTOS`), one folder per project: `<date>-<name>/`. The working code to start from is in [templates/](templates/README.md); how the result was reached, for humans, is [HISTORY.md](HISTORY.md).

## The bar

Every rule below came from one of the photographer's corrections, and keeps its reason beside it. Where none applies, the bar is that the result looks **hand-edited** in front of the camera original.

- **Classical tools only.** Inpainting, frequency separation, curves, gains and alpha matting: every pixel comes from the photo itself. A model that invents pixels (Gemini, Flux, gpt-image, GFPGAN, CodeFormer) is never used. Face or skin detection may locate things, nothing more. The photographer forbade generative AI on 2026-10-10.
- **From the RAW.** Every edit starts from the RAW develop. The camera JPEG is a target or a QA reference only. When the brief says "no JPG", the project root carries the marker file `.sin-jpg` and no JPEG exists at any step, previews included. [scripts/photo_guard.py](scripts/photo_guard.py) enforces it (setup in [references/practices.md](references/practices.md) > Guard hook).
- **Native resolution, maximum quality.** Never upsample. Exports have no quality option.
- **Contours identical to the camera original.** No bite, rim, halo, veil or disc where the wall meets skin, hair, lashes or clothing.
- **Pimples go, freckles and moles stay.** Eyes, brows, mouth and nostrils are protected zones.
- **Private.** Photos and edits stay on the machine: never a notes vault, git or a third-party service.

## What the photographer reads

The photographer reads the images, not the process (said on 2026-10-15). Every word of method in a reply is time and usage they pay for and skip. Before reading any image or launching a subagent, read [references/speed.md](references/speed.md) > Agent time.

- **A reply is the result in 1–3 lines** plus the file to look at in `editadas/`. No method, measurements, step list or "what I tried" unless asked why or what was touched.
- **Make every process image in `proceso/`.** They are browsed alone in Finder's gallery: don't open them for the photographer and don't describe them one by one.
- **Ask only when the decision is theirs**: taste, which version wins, touching an approved master. Everything else, decide and do.

## Where things go

The folder names are Spanish because the templates use them: `editadas/` deliverables, `proceso/` process images, `proceso-notas/` notes and numbers, `respaldos/` regression baselines, `originales/` read-only RAWs, `work/` regenerable scratch.

- Every **image that shows what I did** goes straight into `proceso/`, named `<group>-<name>` (`process_file` in `templates/portrait-qa/recipe/output.py`): side-by-side comparisons, masks, alpha and trimaps, dE maps, histograms, numbered candidates, grids, measurement sheets, whole versions. `proceso/` holds images only and **no subfolders**, since Finder's gallery doesn't open them (asked on 2026-10-15, with everything except plain zooms). A single crop with nothing drawn and nothing beside it goes to `work/`. Numbers, notes and data arrays go to `proceso-notas/`, grouped in subfolders by the same group names. 659 images were once stranded in `work/` and `/tmp`, where macOS deleted some.
- A script that is run again (a measurement, a regression check) lives in `tools/`, a pipeline step in `recipe/`, a one-off in `proceso-notas/`. Never in `work/`, which is regenerable: a script left there is rebuilt by the next agent who can't find it.
- Decisions made by eye (spots, kept marks, protected zones, wall marks) are written by hand into `recipe/photos.py`. A decision inferred at run time drifts between runs and reopens approved spots.
- The README is the **handoff**, kept complete for the next agent, in the photographer's language. In an existing project, read it before anything else.

## Which branch

- **New photos** → copy `templates/pipeline/` into the project instead of rebuilding tools (the second project rebuilt 16 tools where 7 existed). The QA tools the steps name are in `templates/portrait-qa/`, written for square avatars: port each one, with the `recipe/` modules it imports, when its step comes up (module names collide with `pipeline/recipe/`, so merge, never overwrite). The template carries `.sin-jpg`: keep it only if the brief says no JPG. Then steps 1 to 8 in order; with existing styles, step 4 measures their references against the new photos before the pilot.
- **A change to an existing project** → steps 5 to 8, scoped to the photo × style the change touches.
- **A reference style to match** → step 4 first, then the change path.
- **An export or a delivery** of existing masters → no render and no audit. Take the files from `editadas/` as [references/delivery.md](references/delivery.md) says, respect `.sin-jpg`, and write anything that leaves the project to the delivery folder the photographer names, never `~/Downloads`. Done when the files are written and the README line is in place; if another agent is working in the project, put that line in your reply instead of editing the README.
- **A plain question** ("what did you touch", "is everything saved", "show me") → answer from the files directly, with no multi-agent audit. Audits are for a deliverable whose quality is at stake.
- **"What did you touch"** → the README table "Qué se tocó en cada estilo", one Sí/No line per row for the style asked, never merged. If the table is missing, build it first with these rows: exposure, blacks, whites, shadows, highlights, contrast, clarity, WB, saturation, hue, sharpening, NR, grain, vignette, local D&B, blemishes, wall, crop.
- **Build or change the editor** (optional; only when asked for one) → [references/editor.md](references/editor.md), then [references/practices.md](references/practices.md) for every change.

Every branch that edits a file follows [references/practices.md](references/practices.md): backup first, a test that proves the change, the README updated, nothing left running.

## Steps

1. **Develop** linear 16-bit, white balance from the neutral wall.
   Done when clipped pixels, counted on the linear develop, are under 0.005 % (hot pixels only) and the count is in `proceso-notas/`.
2. **Inventory** at 100–200 % with coordinate grids, one candidate sheet per face, each candidate called pimple or mole one by one. Automatic detection failed on the first face it met.
   Done when every candidate has a verdict in `recipe/photos.py` and the sheet is in `proceso/`.
3. **Retouch**: details in [references/skin.md](references/skin.md). For wall and light, prefer smooth global gains without a mask. When a mask is unavoidable, follow [references/compositing.md](references/compositing.md).
   Done when fine skin texture (the finest band of `band_energy` in `templates/portrait-qa/recipe/measure.py`, on the upper face, healed spots excluded) is at least 80 % of the base's for each photo, and the number is in `proceso-notas/`.
4. **Reference** (skip when no style or reference is asked for): build the measurement sheet before editing: [references/measurement.md](references/measurement.md).
   Done when every number the style targets is on the sheet for both images.
5. **Pilot** the change on one case per affected photo, on crops or at preview size, in seconds. A fix that helps one site can hurt another.
   Done when every pilot case passes the gates in [references/qa.md](references/qa.md).
6. **Render** only the photo × style that changed, and scope the QA sheets the same way; run the full set once, at the end. Before the render, name what is expected to change and keep the previous masters as APFS clones (`cp -c`) in `respaldos/<version>-antes-*/` at the project root, with the `editadas/` tree intact; they are the regression baseline, not something the photographer looks at. When a fix in shared code would move approved masters nobody asked about, render the one asked about first, show it, and ask before the rest. Hand the render to a low-effort subagent once the command is decided. Command and speed: [references/speed.md](references/speed.md) > Speed; master format: [references/delivery.md](references/delivery.md) > Masters.
   Done when the clones predate the render, the masters are written and every skipped output had an unchanged input fingerprint.
7. **Regression and QA.** Compare decoded pixels against those clones with `tools/compare_masters.py` (file hashes differ anyway: the ICC header carries a timestamp). Then check at 100 % (200 % on contours) at fixed zones: face, hair edge top and sides, clothing edge, far wall, black clothing.
   Done when every master is either pixel-identical or changed exactly where named, and each remaining defect is listed in README > Pendiente.
8. **Show** before/after sheets from `antes_despues.py` (`templates/portrait-qa/tools/`): camera | before | after | what changed, as a dE76 map, registered on the same pixel, written to `proceso/` without opening them. Reply as "What the photographer reads" says, with an honest percent done: the share of gates passed, with what is left in README > Pendiente. Update the README.
   Done when the README matches what was delivered and `pgrep -fl` shows nothing of mine still running.
