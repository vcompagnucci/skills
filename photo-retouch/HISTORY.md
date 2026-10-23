# History

How the rules in this skill were reached. This file is for people. Agents read SKILL.md.

Two projects in October 2026, told in the order things happened. They overlap from the 14th on, so each heading says which project it belongs to.

- **Project 1:** the photographer's own studio portraits. Four Fujifilm X-T4 RAWs on a grey seamless wall, edited into profile pictures. Three light-background black-and-white styles, each taken from a phone screenshot of someone else's avatar, plus one color style.
- **Project 2:** studio photos of a three-person team, edited for a client. Two group photos (persons A, B and C) and two portraits of person C. Natural color, from the RAW, with no JPEG at any step.

Both ended with a local photo editor: a page served by a small server on the same machine, with the photo in the middle, versions on the left and controls on the right.

## 2026-10-10. First looks and the base rules (project 1)

- First pass: styles matched by eye with global adjustments. Previews of the four photos at 1536 px took about 6 minutes.
- Generative retouching was offered. The photographer refused ("no quiero que uses IA generativa"). From then on every pixel comes from the photo: inpainting, frequency separation, curves, gains, alpha matting.
- Corrections that day, each of which became a rule:
  - Restyle the whole light, beyond the tone ("tenés que adaptar y tocar toda la iluminación").
  - Compare by measuring, "una arriba de la otra". The same code measures the reference and the edit, on the same crop at the same face width.
  - Pimples go, freckles stay ("si son pecas no, si son granos sí").
  - The bar for edges: "como si edito yo la foto a mano".
- Automatic blemish detection failed on the photographer's own face. Spots were inventoried by hand on 100-200 % sheets with coordinate grids, one verdict per candidate, written into a hand-edited file.
- Problems in v4 that shaped the method:
  - Semi-transparent hair left a light aura of +1.5 to +3 L* around the head. Estimating the wall light without the person and a margin around them brought it to ±0.6.
  - Lit skin reached 91-94 L*, merged with the wall and lost a freckle and a mole. A tone curve with three anchors, applied to face light with the fine texture added back on top (never under 80 %), fixed it.
  - A skin mask built from a* > 3 also took hair and the sweatshirt, so the shadow fill greyed the hair. Two learned color models per photo replaced it: skin against hair and clothing.
  - Measured on an ellipse, the face shadow on the photo with glasses read 28 L*. On skin only it read 47.
- The develop clipped forehead and nose highlights to white, up to 23,000 pixels per photo, although the sensor had not clipped. The linear 16-bit develop now clips under 0.005 %, which is hot pixels only.

## 2026-10-12. v7 approved: edges and camera color (project 1)

- The photographer approved v7. Edges were rebuilt so contours match the camera original. For the color style they chose the camera's own look ("prefiero original"): the tone and color of the camera JPEG, with only the wall and the spots changed.
- Wall brightening became additive by the wall's share of each pixel: I' = I + (1-α)(g-1)B. Multiplying the whole pixel had left a light rim on skin and a dark one on hair and clothing.
- The color master of the photo with glasses got a grey cap on the crown. The wall share inside an edge pixel had to be measured after the camera curve, which multiplies dark hair by about 0.14 and the wall by about 1.2. Hair went from 14.5 to 12.6 L* (camera: 8.0).
- A luminance clamp on the wall share let blue and green through and greyed brown hair. It became a per-channel clamp.
- Edge fixes, one per failure:
  - Hair tip over an eyebrow: mixing three colors (skin, hair, wall) instead of two removed a white notch.
  - Glasses rim over the face: a second person color removed a white wedge seen through the lens.
  - Shadowed jaw against a wall of similar color: the color projection read skin texture as transparency and the edge came out jagged. There the edge now comes from the shape.
  - Hair strands 2-3 px thin behind an ear: a luminance key from the contour, as a hand selection would do, kept them from being brightened away.
- A per-photo 3D LUT fitted against the camera JPEG fixed reds the 3x3 matrix missed: a lip line from 3.6 to 0.7 dE, ears from 2.9 to 1.3-1.5. It is used only where it passes three checks. One photo got none because its ear did not improve.
- A review of all 16 masters at 100 % found 30 problems. The fixed ones went into before/after sheets; the rest went to the README's pending list.
- The scene build read 3.98 GB of peak memory. With `MallocLargeCache=0` the same code and output read 2.20 GB.

## 2026-10-14. 16-bit masters and the first export (project 1)

- Masters moved to 16-bit TIFF with ICC at native resolution (4170 px).
- On that re-render the grain style changed grain (±1.4 %), because the grain used a random-device seed. The other 20 masters came out pixel-identical. The fixed-seed rule started here.
- The viewer page (drag and zoom over each style, launched by a `.command` file) got English labels and an export modal.
- The export preview moved to a Worker with an OffscreenCanvas, drawn at the file's resolution. Drawing from the displayed image, or scaling the 4170 px image on the main thread, cost 20-90 ms. Measured paired: open from 31 to 21 ms, size click from 37 to 13, format click from 87 to 13.
- "RAW export" was asked for twice. A sensor RAW cannot hold an edit, so the answer is a linear DNG. LibRaw read it back at most 2 of 65535 off, and the macOS RAW engine 0.5 % darker. The README says plainly it holds the same data as the TIFF.
- A "RAW original" button shows the plain develop, flat on purpose. The camera JPEG stays as the QA reference.

## 2026-10-14. The team brief: develop, retouch and color (project 2)

- Brief: a simple, clean, natural studio edit in color. Heal blemishes, keep moles and freckles, take lint off black clothes, fix light and color, everything from the RAW, no JPEG anywhere. The project root got a `.sin-jpg` marker, later enforced by a hook.
- Develop: white balance measured on hand-picked wall patches and applied before demosaic, since X-Trans interpolates better on balanced data. One exposure for all four (+0.85 EV): same session, flash and camera.
- Retouch, in order:
  - Spots healed one by one (6, 3, 4 and 3 per photo). Tone from Telea inpainting, texture from the evenest neighbouring patch.
  - One hot pixel took a median over 25 px. A global median would have erased the catchlights in eyes, a watch and rivets.
  - Wall marks read by hand on sheets (14, 19, 12 and 1). The detector only proposes, because a loose hair against the wall is also darker. Small marks heal; large ones get a soft gain of at most 50 %. Paper seams and long folds stay, since half-cutting them would show.
  - Yellow wall stains have the wall's brightness, so the dark-spot detector missed them. Each wall pixel takes the mean wall color around it; brightness and grain stay.
  - Skin by frequency bands: 50 % of each spot's excess red, 15 % of the overall red, 35 % evening of 6-12 px tone patches. Starting at 2 px took pores and beard. Anything over 0.08 EV is form and stays.
  - Lint found automatically: 21, 17, 16 and 3 specks. Clusters, colored things, hair, faces and hand-marked zones are skipped.
- Color: chroma ×1.18 and skin hue turned 8° toward yellow. On the vectorscope lit skin went from about 115° (pink) to 120-126°, on the skin line. With +12° person B turned yellow.
- Editor v1 of this project: a page with a hand-made copy of a control panel, a magnet at 70 % and retouch marks toggled with M.

## 2026-10-14. Under-eyes, three rounds (project 2)

- v1 returned 55 % of the missing light, up to 1.2 EV, starting 2 px under the lashes. "Muy notorio": it covered person B's eyes.
- v2 returned 20 %, capped at 0.3 EV. Natural, but barely visible. It measured each under-eye against one cheek number, and its zone faded right at the lower arc, so on person C the arc and the violet stayed.
- The photographer asked to see more difference, with a control, "siempre bien hecha y natural".
- v3 works like a hand retouch:
  - The lower lash line is marked by hand, three points per eye. The strip under it (6 % of eye width) is untouched, and the correction ramps in over the next 20 %.
  - The zone is a crescent per eye. Outside it no pixel changes.
  - Expected skin is a smooth membrane through the skin around the eye: lower cheek, outer corner, cheekbone. The side of the nose is another plane and is left out. So the eye on the shadow side stays in shadow.
  - At 100 % it returns 80 % of the missing light and moves the color 80 % toward the expected skin. It is a pure gain, so texture and grain are the RAW's.
  - A smile builds a bag that is form, so that portrait gets less light (45 %) and less color (60 %).
  - Delivered at 70 %. Since it is a gain, the slider scales it exactly.
- Measured at the deepest point, person C went from 0.30 EV of lift (v2) to 0.52 (delivered). At 100 %, in all 16 eyes, the lid strip does not change and the border moves at most 0.09 EV between neighbouring pixels.

## 2026-10-15. The 200 % end and editor v2 (project 2)

- They asked for an end that cleans them more. The 100 % layer doubled was barely distinguishable, because the darkest part sits right under the lashes, where the 100 % layer does not reach. So 200 % became its own layer: a finer filter, measured closer to the lashes, keeping a 0.35 EV lid shadow, with wrinkle grooves brought toward the skin around them. Stronger tries drew lines and color seams on one portrait. The chosen one was approved ("S4 está bien").
- They asked for a real editor: a right panel with no text, only the real DialKit; versions they can save, listed on the left; the M marks gone; Space as the only shortcut; and a clean, instant photo switch.
- Editor v2:
  - WebGL2. One shader draws the base, the under-eye patches and the adjustments, with under half a level of dither at the end.
  - Display images of every photo at 2560 px, downscaled in linear light and preloaded. A photo switch takes one frame (about 5 ms), with no black flash. Full resolution loads when the view stays on a photo or zooms.
  - The adjustments live in one Python function the server uses; the shader is a line-by-line copy. On the same input they differ by at most 1 level of 255.
  - Under-eye patches are added as a difference against a base crop decoded the same way. Before, at fit, the patch box showed as a rectangle of up to 22 levels of noise.
  - DialKit 2.0.2, vendored untouched. The server saves versions to a JSON file, because browser storage depends on the port.
- More requests the same day:
  - Versions are saved only with *Save version*, a snapshot that keeps editing the open one. Saving from the list went, and DialKit's own version menu is hidden.
  - Pinching outside the photo zoomed the whole page. Now pinch and ⌘+wheel anywhere zoom the photo only. 100 % is one image pixel per device pixel. Fit and 100 % toggle; ⌘+ ⌘- ⌘0 step through Fit, 50, 100, 200 and 400.
  - "Edited se va o dónde queda?": the Edited view went, since it was the open version under another name. RAW original and Before/after became exclusive toggles. Before/after compares any pair, drawn as two scissored passes so each side keeps its own adjustments. ↓ ↑ walk the versions.
  - Round 2. The native select rendered as a light macOS popup in a dark editor, so the menu became the editor's own ("que sea nuestro"). Grabbing near the 2 px divider moved the photo ("es una sensación horrible"); the divider got a 44 px grab band, and at Fit a drag anywhere moves it. The export lost its hover loupe ("odio eso que pasás el cursor y se hace zoom") and gained a summary above Download. The right panel lost DialKit's card ("una sidebar adentro de otra").

## 2026-10-15. Press styles (project 2)

- Request: three styles "para una foto en una nota", referenced on companies known for photo craft: warm beige (Stripe), bright white (Ramp), dark falloff (Apple Newsroom).
- First try: global tints. Stripe's beige over the whole photo turned black shirts brown and tanned the skin ("no son naturales esos colores").
- Second try: the background only.
- Third, after they asked for light edited "como si la editara una persona" and a background made from parameters: global light settings with no temperature or tint on people, plus a Background folder (exposure, evenness, falloff, temperature, tint, saturation) applied only to the wall through a closed-form alpha matte.
- "Está cortando la zapatilla": the matte called a white sneaker wall, and two styles painted it (10,321 pixels over dE 2). Hand-drawn keep polygons fed into the matting solve made the nearby wall go to 0.4-0.8 alpha and flipped a lace tip. Applied after the matting, they gave 0 pixels with alpha under 1 inside (from 88,674), and the people stayed pixel-identical.
- Chrome reads a 16-bit PNG by dropping the low byte without rounding, so the editor got rounded 8-bit copies.
- "Armame versiones solo tocando estos parámetros": a first batch of invented looks recolored or flattened the wall and was rejected ("no random, son horribles"). Published Lightroom recipes, with their numbers and sources, replaced them.

## 2026-10-15. Speed, folders and agent time (project 1)

- The photographer said no request should take an hour per run, with no loss of quality.
  - The grain stage took 341 of 474 s: its OpenMP pragmas had been compiled without OpenMP. It was rebuilt with 4 threads.
  - The scene is built once per photo. Two photos run at a time when memory pressure is normal.
  - Originals are re-exported only when the fingerprint of their inputs changes. An existence check had left exports stale after a framing edit.
  - `taskpolicy -b` pinned the work to the efficiency cores and made each photo 3.8x slower. They chose the fastest option.
  - Grain got a fixed seed per channel, so any re-render can be proven identical.
  - Result: one photo in four styles from about 14 min to 1 min 52 s; all 16 masters from 61 min to 8 min 14 s. 116 of 136 files were pixel-identical; only the grain style changed, by its new seed.
- Agent time, measured over the day: the model thinking and writing was 69-85 % of the work, renders 8-18 %. Audits were 34 % of 29 hours. Hence effort high, mechanical steps on a low-effort subagent, one auditor per deliverable, and crops instead of whole sheets.
- They said they do not read the process, only the images. Replies became 1-3 lines plus the file to open.
- Finder's gallery does not open subfolders, so `proceso/` was flattened with group prefixes. 867 plain zooms went to the Trash. 659 images that lived only in `work/`, the project root, `/tmp` or the agent's own folders were gathered in. Crops left in `/tmp` between the 10th and the 12th were already gone, emptied by macOS.
- The "exact" version: they asked that every number in the color report match each reference.
  - The old report compared different anatomy: a reference ellipse took cheek, chin and a jacket collar. Now skin is compared with skin.
  - Rebuilding parameters from their saved dictionary dropped one field, and skin came out 16 L* darker than the approved master. Everything built before the fix was redone.
  - Matching the skin histogram with no limit came out exact, with large dark islands. A slope cap of 2.5 kept it natural. They chose per style which light to keep.
  - A highlight shoulder stopped forehead and cheek from burning. One cheek edge still showed a white line ("mal") until the shoulder compressed the edge pixel too.
- The first version of this skill was written that day from 63 candidate rules, with a hook that blocks `/tmp` and JPEG writes in no-JPEG projects.

## 2026-10-15 to 10-17. One editor design for both projects (project 1)

- On the 15th project 1's viewer took project 2's layout: photos on top, list on the left, photo in the middle, reference and controls on the right.
- On the 16th the rest was ported from a frozen, dated copy of project 2's editor: zoom, the before/after bar, keyboard, export area and sizes, the Background folder. Project 1 kept what was its own: the reference panel, the circle or square guide, the styles, and JPEG and DNG export.
- On the 17th, "saca las exactas": the exact versions left the list. They stayed on disk and can still be exported.
- Also on the 17th, the panel opens at each style's equivalent settings instead of zero. The styles were made with measured curves, local light, grain and matte, so a least-squares fit finds, per photo and style, the panel values that bring the RAW closest to the master. All 16 hit a control limit and the mean error is 1.7-4.2 L*, so they are only a starting point. The photo shown stays the master; moving a control applies the difference.
- The editor asks the server for the masters again when the window regains focus, so a re-rendered master reloads without a rebuild.

## 2026-10-17. Company versions and details (project 2)

- Team-photo references from Linear, Apple, Robinhood, Public and Nothing, imported from press kits to sRGB PNG and measured with the same code as the photos.
- The first batch copied each reference's light: exposure up to +0.6, blacks ±40, highlights -40. One clipped 12-16 % of the frame, and the set looked washed out or muddy ("no es poner el filtro y ya"). Now only the wall and the direction come from the reference. A fitting tool sets exposure per photo (skin toward the reference, at most ±0.3) and blacks (black clothing between 5 and 10 L*).
- "Seguí corrigiendo detalles, que siga buenas prácticas":
  - With the skin raised, forehead and cheekbones clipped red on 2-10 % of the face. The light versions got Highlights -20 and Whites -8: 0 % clipped, for 1.5 L* less skin. The fitting tool now reports the clipped share of the face.
  - A line in the wall was the paper's own vertical stripes, made visible by the contrast. A new Smoothing control flattens paper differences up to 8 % and keeps anything from 20 % up, which is a shadow of the people.
  - Re-seeding replaces only the versions a photo still has, so deleted versions stay deleted.
- Versions are named by what they are, without the company (the photographer's request). One reference with no wall to compare was dropped.

## 2026-10-18 to 10-19. The editor, request by request (project 2)

Before each change below, the files it touched were copied as `<file>.antes-<change>.<ext>`. Each change closed with its own test.

- 10-18: no "Version 1". The library's base version no longer shows while saved versions exist.
- Export became Format, Size and Crop, with no presets, explanation lines or Reset (the photographer removed them). JPEG was added at their request, built in memory for the download only, so the project stays JPEG-free. Crop works like the one in Apple Photos. A check script tests 4 formats × 3 sizes × 3 crops against the server: 36 of 36.
- "Tal cual como se ve en el preview así se exporte": the export preview got zoom, drawn at the smaller of the zoom and the file size, so it never shows more detail than the file will have.
- Performance audit: 0 frames per second at rest; each gesture costs 1-2 ms of main thread. Dragging the crop frame went from 2.3 to 1.7 ms, with old and new measured interleaved. Panning went from 1.8 to 1.2 ms, inside the noise, and was reported that way.
- Holding Space shows the RAW only over a version. In the RAW and before/after views it does nothing.
- Browser matrix with Playwright: Chrome, WebKit and Firefox, five viewports plus reduced motion. 1204 of 1204. It found two real bugs: *Save version* from the base kept editing the hidden base, and the zoom pill flashed its old value on reopen. Safari's pinch and trackpad inertia were tested only at handler level and flagged for real hardware.
- Faster downloads: a whole photo with background took 19-23 s. The server now keeps the full adjusted render and starts the export when the panel opens. The first download takes about 11 s; each later change of format, size or crop takes 0.05-0.6 s. Pixels identical on 7 cases. The cost, written down: lighter compression, PNG 1 % larger and lossless WebP 18-25 % larger.
- "Si se elimina de una se elimina de todas": one version list across photos. Values stay per photo, since each wall is tuned per photo. A one-off script synchronized the four photos, after a backup of the versions file.
- Animations, following the emil-animations skill: menus grow from their trigger in 150 ms and leave in 100; under reduced motion everything is instant. Measured: at 60 ms a menu is at 0.72 opacity. The rename field and keyboard navigation are not animated.
- Notices moved to Sonner, bundled offline: neutral dark grey, no green or red, 2.6 s, at most three stacked. The container is a popover, so notices show over the export modal. They moved beside the panel because they covered *Save version*.
- Under-eyes per face, keyed by person, so copying from a portrait to a group photo changes the same face. Test: with one face at 150, the other two stay pixel-identical on screen and in the file.
- Rename a version from a right-click or ⋯ menu, in place, across all photos.
- Both sidebars paired: same margins, title heights and row heights, taken from DialKit's own tokens.
- *Copy to other photos* overwrites that version in the other photos. Its tooltip names the version and the photos before the click.
- "Is the download what I see?" was answered with a measurement that changed nothing: the wall under 1 level apart, people 0.5-0.8. The only real gap is at the silhouette edge, fine hair and shoes (1.3-3.4 mean), because at Fit the screen draws from display-size layers.
- Import photos from the editor: any RAW LibRaw reads and any image macOS opens, with JPEG refused. Images go to 16-bit sRGB through ColorSync, since `sips` dropped them to 8 bits. Faces are located by the macOS detector, only to place them. Retouch and under-eyes stay off until the hand inventory is done. A RAF takes about 1 min and 2.8 GB.

## 2026-10-20. Flip and a count (project 1)

- Flip mirrors one photo so the face looks toward the text beside an avatar. Everything of that photo mirrors, on screen and in the export; the shape guide and labels stay. The server mirrors the master before cropping, so the visible area exports the same. With Flip off every file is byte-identical to before.
- The README said 129 lint specks on one photo, from an older run. A script that counts the specks changed in the delivered retouch measured 143. The README now quotes the measured number.

## What held throughout

- Every change started from a backup: APFS clones of the masters before a render, dated copies of editor files before an edit, a copy of the versions file before migrating it.
- Every feature got a test that fails when that feature breaks. The result went into the README with the date and the request.
- The README stayed the handoff. Each new session resumed from it.
