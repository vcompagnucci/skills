# Named operations

Read this when someone asks by name for an operation built and approved in the two projects ("do the under-eyes like we did", "sacá las pelusas"). Find it by its words. Paths are a project copied from `templates/pipeline/` (Profile styles: `templates/portrait-qa/`). The rules stay in the reference each entry points to. Sheet paths are where the template writes them; flatten them into `proceso/` (SKILL.md > Where things go).

**Approved values come in three kinds.** Keep them apart:

- **Approved constant:** the value in the code is the one the photographer approved. It changes only on a new complaint ([practices.md](practices.md) > Shared machine).
- **Per session:** the value in the code is project 2's session. Set it for this session ([templates/README.md](../templates/README.md) > How to start, step 3).
- **Per photo:** a hand decision in `recipe/photos.py`, with no default. The `PHOTO_A` values are made up; never cite them.

**Steps**, as SKILL.md > Which branch > A change to an existing project routes them:

- **Inventory:** the step 2 verdict in `recipe/photos.py`, step 3, then steps 6 to 8.
- **Strength:** steps 5 to 8. Where the entry says `recipe/retouch.py` reads the value, rerun `recipe/retouch.py <photo>` before step 6's `recipe/grade.py`, which reads the cached `work/<photo>-retocada.tif` and alone writes an unchanged master.
- **Editor only:** a saved version, no render. Back up `editadas/versiones.json` first ([practices.md](practices.md) > Every change).

New photos run every step from step 0; an operation there is the same code at its step.

## Retouch

### Spots and kept marks

- **Words:** spots, pimples, blemishes, red marks, scratches; keep a mole or freckle; granos, granitos, marcas rojas, raspones; dejale el lunar, la peca. "Grano" for added texture is Film grain.
- **Does:** heals each hand-marked spot ([skin.md](skin.md) > Heal, never blur). Freckles, moles and scars stay.
- **Code:** `heal()` in `recipe/heal.py`, run by `recipe/retouch.py`; candidate sheets from `recipe/spots.py <photo>`.
- **Approved:** pimples go, freckles stay (2026-10-10); the method, 2026-10-14.
- **Set:** per photo, `spots` (x, y, radius) to heal; marks to keep in `kept`, which every skin step leaves pixel-identical. "Dejale el lunar": move it from `spots` to `kept`.
- **See:** `proceso/10-candidatos/<photo>-<face>-tiras.png` and `-mapa.png`; after, `tools/compare.py <photo> x0 y0 x1 y1 <out> --diff`.
- **Steps:** Inventory. A `kept` change names the face in `esperado.txt` ([skin.md](skin.md) > Kept marks).

### Hot pixels

- **Words:** hot pixel, stuck pixel, a bright dot; píxel caliente, un puntito.
- **Does:** pixels far from the 5×5 median take it, only in a 25 px window around the marked point.
- **Code:** `fix_hot()` in `recipe/heal.py`, called with `half=12` by `recipe/retouch.py`.
- **Approved:** constant, 2026-10-14.
- **Set:** per photo, `hot` (x, y).
- **See:** `tools/compare.py` on a crop around it.
- **Steps:** Inventory. Rule: [skin.md](skin.md) > Hot pixels.

### Wall marks

- **Words:** wall marks, dust, scuffs, a wrinkle in the paper; manchas de la pared, marcas, polvo, arrugas del papel.
- **Does:** a mark up to radius 12 heals like a spot; a larger one, or one at the frame edge, is lifted with a soft gain toward a plane fitted around it, lighter only, at most 50 %. Paper seams and long folds stay.
- **Code:** `wall_mark()` (`SMALL_MARK = 12`) and `lift()` in `recipe/heal.py`; candidates from `recipe/wall.py <photo>`; real center and size from `tools/wall_measure.py <photo> x,y ...`.
- **Approved:** constants, 2026-10-14. The detector only proposes: a loose hair against the wall is also darker.
- **Set:** per photo, `wall_marks` (x, y, radius); a streak is several small points along it.
- **See:** `proceso/21-pared/<photo>-manchas.png` (candidates); `tools/wall_check.py <photo>` writes `proceso/21-pared/<photo>-curadas.png`.
- **Steps:** Inventory.

### Wall stains

- **Words:** yellow stains, splashes, color stains on the wall; manchas amarillas, salpicaduras, manchas de color en la pared.
- **Does:** each wall pixel takes the mean wall color around it (48 px); brightness and grain stay, and anything off the wall's brightness (a loose hair) is left alone.
- **Code:** `neutral_stains()` in `recipe/wall.py` (`STAIN_SCALE = 48`, `STAIN_FENCE = 36`), run by `recipe/retouch.py` on every photo.
- **Approved:** constants, 2026-10-14.
- **Set:** nothing per photo; with no seamless wall, skip the call ([templates/README.md](../templates/README.md) > Other photos).
- **See:** `tools/stain_check.py <photo>` writes `proceso/21-pared/<photo>-color.png`.
- **Steps:** it runs in step 3 (`recipe/retouch.py <photo>`, then `recipe/grade.py <photo>`); a change to it reruns step 3, then steps 6 to 8.

### Skin

- **Words:** even the skin, redness, blotches, shine, teeth; emparejar la piel, rojeces, manchas, brillo, dientes amarillos.
- **Does:** per face, frequency-band dodge and burn: 50 % of each spot's excess red, 15 % of the overall red, 35 % evening of 6–12 px tone patches; over 0.08 EV is form and stays. Then 35 % of the specular shine and, with `teeth`, 35 % of the teeth's yellow.
- **Code:** `retouch_face()` in `recipe/skin.py` (`REDNESS_LOCAL`, `REDNESS_BROAD`, `EVENING`, `TONE_LIMIT`, `SHINE`, `TEETH`).
- **Approved:** red and tone, constants, 2026-10-14 (starting at 2 px took pores and beard). Shine and teeth are template values with no dated approval.
- **Set:** per face, `oval`, `features` (the protected zones) and `teeth: True`.
- **See:** `tools/check_faces.py <photo>` writes `proceso/01-caras/<photo>-<face>.png`; fine texture at least 80 % of the base's (SKILL.md step 3).
- **Steps:** Inventory. Rules: [skin.md](skin.md).

### Under-eyes

- **Words:** under-eyes, dark circles, bags, "like we did with the team"; ojeras, bolsas, "las ojeras como las hicimos".
- **Does:** per eye, a gain inside a crescent under the hand-marked lash line (project 2, the team). Rule: [skin.md](skin.md) > Under-eyes.
- **Code:** `correct()` in `recipe/undereye.py`, called from `retouch_face()` by `recipe/retouch.py`, applies `INTENSITY` there; `recipe/grade.py` then writes the 0, 100 and 200 % patches to `editadas/ojeras/`.
- **Approved:** v3, 2026-10-14: at 100 % `light` 0.8 and `color` 0.8 (`DEFAULTS`), delivered at 70 % (`INTENSITY = 0.7`). A smiling portrait got less light (`light` 0.45) and less color (`color` 0.6) in its `under_eye`, since the smile's bag is form. Rejected: v1, 55 % up to 1.2 EV ("muy notorio"); v2, 20 % capped at 0.3 EV.
- **Set:** per face, `lids` (three points per eye, read on `tools/eyes_grid.py --lids <photo>`) and `under_eye` (`light`, `color`, `depth`, `span`, `shift`, `pin`; `eyes` for one eye). The strength for every face is `INTENSITY`.
- **See:** `tools/eyes_bench.py cache <photo>`, then `hoja <photo>`: `proceso/31-ojeras/v3/<photo>-<face>.png`, with `parpado` 0 and `contorno` at most 0.09 EV/px; `tools/eyes_preview.py <photo>`.
- **Steps:** a `lids` or zone change, Inventory; a strength, Strength (`recipe/retouch.py` reads it).

### Under-eyes, the 200 % end

- **Words:** clean them more, the strongest end, S4; más limpias, la punta del 200.
- **Does:** its own layer, not the 100 % doubled: a finer filter measured closer to the lashes, a 0.35 EV lid shadow kept, wrinkle grooves brought 80 % toward the skin around them.
- **Code:** `layers(maps, top=True)`, `top_light()` and `creases()` in `recipe/undereye.py` (`TOP_LIFT`, `TOP_FINE`, `LID_SHADOW = 0.35`, `CREASE = 0.8`); `TOP = 200` in `recipe/grade.py`.
- **Approved:** 2026-10-15 ("S4 está bien"). Stronger tries drew lines and color seams on one portrait.
- **Set:** reached only from the editor's Under-eyes slider. `under_eye.reach_lashes: True` for a crescent glued to the lashes; `light` and `color` don't apply here.
- **See:** the 200 % column of the `eyes_bench.py` sheet; `tools/eyes_blend_check.py <photo>` for the patches.
- **Steps:** Strength (`recipe/retouch.py` reads it).

### Under-eyes per face

- **Words:** one person's under-eyes, per face, less on one person in the group photo; las ojeras de una sola cara, de la segunda persona, un poco menos, por persona, en la de grupo.
- **Does:** one strength per person: moving one face leaves the others pixel-identical, and copying a version from a portrait to a group photo changes the same person.
- **Code:** in the editor, the `Under-eyes.<face label>` controls (`eyeControls`, `FACE_NAMES` in `recipe/viewer_template.html`) and `under_eyes` as `{face: level}` in `recipe/editor_server.py`; in the master, that face's `under_eye.light` and `color` in `recipe/photos.py`.
- **Approved:** 2026-10-19.
- **Set:** per face, `faces[].id`, the same id for a person in every photo, labelled in `FACE_NAMES`. "The second person" counts left to right, the order the editor lists the controls (`eyeControls` sorts by x); when two readings fit, ask. The old single `Under-eyes.Intensity` still means every face ([editor.md](editor.md) > Versions).
- **See:** `tools/editor_test/eyes_per_face.mjs` (one face at 150, the others identical).
- **Steps:** with an editor, Editor only (that face's control moved). When the master is the deliverable, Strength on that face's `under_eye` (`recipe/retouch.py` reads it).

### Lint

- **Words:** lint, fluff, specks on the black clothes; pelusas, pelusitas, la pelusa del buzo, polvo en la ropa negra.
- **Does:** finds isolated light specks over black fabric (3–400 px; 3 or more within 25 px are weave and stay) and fills each from its edge.
- **Code:** `find()`, `remove()` and `sheet()` in `recipe/lint.py` (`VISIBLE = 5.0`), run by `recipe/retouch.py`, which prints the count.
- **Approved:** constants, 2026-10-14. Quote the count `retouch.py` prints: on 2026-10-20 a README said 129 from an older run, against 143 measured.
- **Set:** per photo, `lint_keep` (x, y, width, height) for what isn't lint (a scrape, a watch, a logo). A speck the detector misses has no field: say so instead of healing it as a spot. No black clothing: skip the three calls ([templates/README.md](../templates/README.md) > Other photos).
- **See:** `proceso/20-pelusas/<photo>-pelusas.png` (each speck ×4, before and after) and `<photo>-mapa.png`.
- **Steps:** Inventory. Rule: [skin.md](skin.md) > Lint.

## Light and color

### Wall evening

- **Words:** even the wall, the flash falloff, darker corners; emparejar la pared, la caída de luz.
- **Does:** halves the flash falloff on the wall with one smooth gain over the whole photo, no mask, capped at ±0.35 EV; the light on the faces doesn't change.
- **Code:** `evening_gain()` in `recipe/wall.py` (`EVEN = 0.5`, `EVEN_LIMIT = 0.35`), step 1 of `finish()` in `recipe/grade.py`.
- **Approved:** constants in project 2's delivered masters (2026-10-14).
- **Set:** nothing per photo; with no seamless wall or no faces, replace it with ones ([templates/README.md](../templates/README.md) > Other photos).
- **See:** `tools/lr_audit.py <photo>` (the wall's falloff toward the corners).
- **Steps:** Strength.

### Base color and exposure

- **Words:** skin too pink, more color, brighter; la piel rosada, más color, más luz.
- **Does:** chroma ×1.18 and skin hue 8° toward yellow, with neutrals and other colors unchanged; one exposure and one curve for the session.
- **Code:** `color()`, `tone()` and `finish()` in `recipe/grade.py` (`CHROMA`, `SKIN_HUE`, `EXPOSURE`, `CURVE`).
- **Approved:** per session. Project 2 (2026-10-14): `CHROMA` 1.18, `SKIN_HUE` 8 (+12° turned a face yellow), `EXPOSURE` 1.80 (+0.85 EV, the same for all four).
- **Set:** the top of `recipe/grade.py`.
- **See:** `tools/color_check.py <photo> ...` (vectorscope angle, ΔE between photos).
- **Steps:** Strength; `recipe/retouch.py` reads `EXPOSURE` too (lint is judged at it). Tolerances: [measurement.md](measurement.md) > Tolerances.

## Backdrop styles

### Press styles

- **Words:** press styles, the three styles, Warm beige, Bright white, Dark falloff; estilos de prensa, "para una foto en una nota".
- **Does:** three styles, each light settings plus a wall-only Background through the matte. Rule: [measurement.md](measurement.md) > Building a style.
- **Code:** `STYLES` in `recipe/styles.py` (`beige` from Stripe, `white` from Ramp with `WHITE_TOP = 94.0`, `falloff` from Apple Newsroom), composed by `recipe/backdrop.py`; references `stripe`, `ramp` and `apple` in `REFS` of `recipe/references.py`.
- **Approved:** the `STYLES` values, 2026-10-15. Rejected first: global tints ("no son naturales esos colores").
- **Set:** one table for every photo; `white`'s background exposure is solved per photo (`"top"`). The matte's per-photo fixes: Matte fixes below.
- **See:** `styles.py <photo> --preview` (pilot at 2560 px in `work/estilos/piloto/`), `tools/backdrop_sheet.py <photo>`, `tools/backdrop_zone.py <photo> x0,y0,x1,y1 --name=<zone>`, and the wall-only check in [qa.md](qa.md).
- **Steps:** in a new project, step 4 first: asking for these styles makes `stripe`, `ramp` and `apple` this project's references. Keep or re-add their template `REFS` entries (marks are in the reference's pixels), import each with `tools/ref_import.py <id> <source URL>`, adding the zip member the `source` names in parentheses (none named: pick it from `--list <zip>`), and measure it against these photos. Then steps 5 to 8, rendering with `styles.py <photo>` and seeding editor versions with `--seed`. Edges: [compositing.md](compositing.md).

### Matte fixes

- **Words:** it's cutting the sneaker, the background took a shoe, wall left between the arm and the body; "está cortando la zapatilla", quedó pared en el hueco.
- **Does:** hand regions that correct the matte: keep polygons are person, holes are wall, sure boxes decide both sides.
- **Code:** `keep_polygons()` in `recipe/matte.py`, called by `alpha_for()` in `recipe/styles.py`; holes and sure boxes in `background_mask()` of `recipe/masks.py`.
- **Approved:** 2026-10-15: inside the polygons, pixels under alpha 1 went from 88,674 to 0, and the people stayed pixel-identical.
- **Set:** per photo, `backdrop_keep` (polygons, 2 px inside the edge), `backdrop_holes` and `backdrop_sure` (boxes).
- **See:** `tools/backdrop_alpha_red.py <photo>` (matte wall painted red), `tools/backdrop_holes.py <photo> --preview`, `tools/backdrop_before_after.py <photo> x0,y0,x1,y1 --name=<zone>`.
- **Steps:** the step 2 verdict in `recipe/photos.py`, then `styles.py <photo> --layers` and steps 6 to 8. Step 3 doesn't read these fields, so skip it. Rule: [compositing.md](compositing.md).

### Lightroom looks

- **Words:** versions touching only the panel, published recipes, natural, high contrast, black and white; "armame versiones solo tocando estos parámetros", blanco y negro.
- **Does:** panel values from published recipes, background at 0; editor versions with no master of their own.
- **Code:** `LOOKS` `natural`, `contrast` and `contrast_bw` in `recipe/styles.py`; `styles.py --seed-looks`.
- **Approved:** 2026-10-15, after an invented batch was rejected ("no random, son horribles").
- **Set:** the table; every number cites its recipe ([measurement.md](measurement.md)).
- **See:** in the editor; `tools/style_pilot.py <ref> '<json>'`.
- **Steps:** Editor only: `--seed-looks`, with `--update` to replace only versions a photo still has ([editor.md](editor.md) > Versions).

### Company looks

- **Words:** like Linear, Robinhood, Public or Nothing, team-photo looks; como las de Linear, versiones por empresa.
- **Does:** the wall and the direction from each reference; exposure and blacks fitted per photo. Rules: [measurement.md](measurement.md) > Building a style and > Tolerances.
- **Code:** `LOOKS` `robinhood`, `public`, `nothing` and `linear` in `recipe/styles.py`; `tools/look_fit.py <key>`.
- **Approved:** 2026-10-17: Highlights -20 and Whites -8 on the light versions (their cost: Tolerances > Face clipping), `smoothing` 100, versions named by what they are, without the company. Rejected first: copying the reference's light ("no es poner el filtro y ya").
- **Set:** `base` and `background` shared; `photos` per photo and per session, from `look_fit.py`.
- **See:** `look_fit.py`'s output (face clipping %), `tools/ref_measure.py`.
- **Steps:** step 4 for the references, `look_fit.py`, then `--seed-looks`.

### Background controls

- **Words:** background exposure, evenness, falloff, a warmer wall, paper stripes; la pared más clara, más pareja, las líneas del papel, "noto una línea".
- **Does:** wall-only controls: Exposure, Evenness, Smoothing, Falloff, Temperature, Tint, Saturation. Smoothing flattens paper differences up to 8 % and keeps anything from 20 % up, which is a shadow of the people.
- **Code:** `KEYS` and `compose()` in `recipe/backdrop.py` (`PAPER = (0.08, 0.2)`); the shader copy is `backdrop()` in `recipe/viewer_template.html`.
- **Approved:** the folder, 2026-10-15; Smoothing, 2026-10-17. The three press styles stay without Smoothing: they were already approved.
- **Set:** per version in the editor, or a style's `background` in `recipe/styles.py`.
- **See:** in the editor; after a change to either copy, `tools/download_parity.mjs` ([editor.md](editor.md) > Screen equals export).
- **Steps:** a version, Editor only; a style's table, Strength.

## Editor actions

Rules for all of them: [editor.md](editor.md).

- **Copy to other photos** (copiá a las otras): overwrites that version's values in the other photos; values otherwise stay per photo. Rename and Delete from all photos also act on every photo. `copyToOthers()` in `recipe/viewer_template.html`, 2026-10-19. Editor only.
- **Import a photo** (sumá una foto, importá): any RAW LibRaw reads or image macOS opens, to 16-bit sRGB through ColorSync; JPEG refused in a `.sin-jpg` project; faces placed by the macOS detector only. Retouch and under-eyes stay off until the hand inventory. `/api/import` in `recipe/editor_server.py`, `recipe/import_photo.py`, 2026-10-19. Then SKILL.md step 2 for that photo.
- **Export** (exportá, bajala): Format, Size and Crop (2026-10-18). The export branch and [delivery.md](delivery.md) > Exports.
- **Flip** (espejala, espejar, dar vuelta, mirror; 2026-10-20): the Flip button (F) mirrors one photo so the face looks toward the text beside it: every view of it and its export, never the labels or the guide. Stored per photo in the browser; the server takes `"flip": true`. `toggleFlip()` in `recipe/viewer_template.html`, `recipe/editor_server.py`. Editor only.
- **Circle or square** (en círculo, foto de perfil, cuadrada): the Crop guide (Off, Circle, Square) frames the crop on screen; Export > Shape Circle writes the inscribed circle as transparency in PNG, TIFF and WebP, needs a square crop, and names the file `-circle`. JPEG and DNG come out square. `"shape"` in `recipe/editor_server.py`, 2026-10-23. Editor only.
- **DNG** ("RAW export", el RAW): Export > Format DNG, a linear 16-bit DNG with the TIFF's data. Say it holds no more quality ([delivery.md](delivery.md) > Exports).

## Panel and exact versions

- **Panel at each photo's equivalent settings** (que el panel arranque donde está la foto; 2026-10-17): `recipe/equivalents.py [photo ...]` fits the eleven Light and Color controls closest to each master by least squares and writes `recipe/equivalents.json`; the editor starts the panel there and applies only the difference from it. Without the file the panel starts at 0. Run it after a master changes, then reload the editor. It rewrites saved versions once, with a backup in `respaldos/`. Check: `tools/equivalents_check.py`; rule: [editor.md](editor.md) > Screen equals export.
- **Exact versions** (las exactas, igual a la referencia; 2026-10-15): `recipe/exacta.py <photo> [style ...] [--n 1536]` matches each style's skin L* percentiles to its reference, slope capped at 2.5, moving only L* inside a skin-and-neck brush that leaves black clothes and hair alone. It writes `editadas/<photo>-<style>-exacta.tif` and `.png` beside the style's master, which stays untouched, and its numbers to `proceso-notas/exacta/`. Needs the reference imported (step 4). Check: `tools/exacta_check.py`. It can't darken skin toward a darker reference (the JSON shows the gap left), and it looks flatter and paler than the master, so show both and let the photographer choose. ~35 s and 2.6 GB per master.

## Profile styles (portrait-qa)

Port first ([templates/README.md](../templates/README.md) > Porting). Their edge and color gates are in [qa.md](qa.md) (`tools/gate_renders.py`, `edge_gate.py`, `edge_montage.py`, `color_zones.py`; the last two don't run under `.sin-jpg`). Steps: step 4, then steps 5 to 8.

- **Light-background profile styles** (estilos de perfil, fondo claro, blanco y negro): `ref-a` high-key, `ref-b` light grey with grain, `ref-c` editorial white. Each copies its reference by measurement: a tone curve with three anchors, a face shadow fill capped at `FILL_EV = 1.2`, local contrast per band, the wall brightened additively through the matte. `STYLES`, `fit_params()` and `edit_wall()` in `portrait-qa/recipe/styles.py`. Approved in v7, 2026-10-12.
- **Camera color** ("prefiero original", el color de la cámara): the person as the camera JPEG rendered them (matrix, tone curve, chroma per brightness), with only the wall and the spots changed. `Style("color", ..., camera_look=True)` and `portrait-qa/recipe/camera_color.py`, 2026-10-12. The per-photo 3D LUT for reds (`camera_lut()` in `camera_lut.py`) reads `recipe/luts/<photo>-color.npy`; no LUT and no fit script ship, so it applies none. A LUT goes in only where it passes three checks; one photo got none.
- **Film grain** (ponele grano, grano de película, "como en los perfiles"): Newson's boolean grain on the master at its real size, half on skin. `film_grain()` and `finish()` in `portrait-qa/recipe/styles.py` (`GRAIN_R = 0.05`, `GRAIN_SKIN = 0.5`, `GRAIN_BIN`), only in `ref-b`; build `portrait-qa/tools/film_grain/` with `make` (OpenMP flags: its `makefile`). Seed fixed per channel since 2026-10-15 ([speed.md](speed.md)). A pipeline project has no grain hook or editor control: wiring it in is new code (on the sRGB render, after sharpening); say so before building it.
