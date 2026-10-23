# Photo-retouch templates

Starter code for a portrait-retouching project: RAW in, 16-bit masters and a local browser editor out. It was taken from two real retouching projects and scrubbed. Every per-photo table now holds one made-up example entry (`PHOTO_A`), so none of it describes a real photo.

Code comments are in Spanish. They explain why each number is what it is, and that reasoning is the most valuable part.

## What is here

| Folder | What it is |
|---|---|
| `pipeline/` | The full RAW-to-editor pipeline: develop, retouch (spots, hot pixels, wall marks, lint, under-eyes, skin), grade, wall matting and backdrop styles, plus the local editor (`recipe/editor_server.py` + `recipe/viewer_template.html`) and its tests (`tools/editor_test/`). |
| `portrait-qa/` | The QA tools from an earlier square-avatar project: edge gate and montage, alpha check, color zones, before/after sheets, frequency-band skin retouch (`recipe/skin_retouch.py`, `recipe/measure.py` `band_energy`), the matte it was validated on, and a film-grain renderer. It has its own `recipe/`, which is not the same as `pipeline/recipe/`. |

Both folders use the same layout. `recipe/` holds the steps and shared modules. `tools/` holds the measurements and contact sheets you rerun, read before changing a number.

## How to start

1. Copy `pipeline/` into a new project folder. Put the RAWs in `originales/` (`develop.py` expects `<photo>.RAF`, so change the extension there for other cameras; it reads through rawpy, which opens any RAW LibRaw reads, DNG included). Keep `.sin-jpg` only if the brief says no JPG. While it exists, JPEG leaves the editor only as an in-memory download.
2. Create a venv: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Fill in `recipe/photos.py` by hand. Replace `PHOTO_A` with one entry per photo, keyed by the file name without its extension. The docstring explains every field. Empty `REFS` in `recipe/references.py` the same way: its entries are the earlier projects' references, examples of the format, and this project's go there at SKILL.md step 4. The styles in `STYLES` and `LOOKS` of `recipe/styles.py` name those entries in `ref`: point a style the project keeps at one of its own references before `tools/look_fit.py` reads it. `wall` comes first: a photo without it develops on the camera's own white balance, so develop once, read the neutral patches on that base with `tools/grid.py`, fill `wall` and develop again. Measure the fields on the developed image, using the sheets that `tools/grid.py`, `tools/check_faces.py`, `recipe/spots.py` and `recipe/wall.py` write to `proceso/`. `EXPOSURE`, `CURVE`, `CHROMA` and `SKIN_HUE` at the top of `recipe/grade.py` are the earlier session's values (one flash, one camera, its skin): set them for this session: `tools/color_check.py` tries `CHROMA` and `SKIN_HUE` variants and reports lit-skin L* (its docstring), and `EXPOSURE` and `CURVE` are read on that L* and on the clip % of step 5.
4. Run the steps in order, one photo per process: `recipe/develop.py`, then `recipe/retouch.py`, then `recipe/grade.py`, which writes the master `editadas/<photo>.tif` and the camera original `<photo>-antes.png` that SKILL.md step 4 measures. Stop there: `recipe/styles.py <photo>` (optional backdrop styles; `--seed` writes them as editor versions) renders at SKILL.md step 6, once the references, the `respaldos/` clones and `esperado.txt` exist. For an editor ([editor.md](../references/editor.md)), after that render (it reads the backdrop layers of `styles.py <photo> --layers`), run `recipe/viewer.py` and open `Abrir editor.command`; for group photos, first give each face id a label in `FACE_NAMES` in `recipe/viewer_template.html` (`{ "face-id": "Label" }`): saved versions key the per-face controls by those labels.

`portrait-qa/` is a second reference, not a second pipeline. Copy the tools you need with the `recipe/` modules they import. `common.py`, `masks.py`, `matte.py`, `photos.py` and `styles.py` exist in both `recipe/` folders: merge them, never overwrite.

### Tests

- `tools/editor_test/test_server.py` runs against the Python server alone. The JS tests (`test.mjs`, `import.mjs`, `apply_version.mjs`, `styles_check.mjs`, `eyes_per_face.mjs`, `browsers.mjs`) need Playwright and Chrome. Set `PW_PATH` to the `node_modules` folder that contains `playwright` (`npm install playwright` in a folder outside the project, then `npx playwright install webkit firefox`; Chrome is the installed Google Chrome, `channel: "chrome"` in `browsers.mjs`).
- By default the tests use the first photo in `recipe/photos.py`. Override it with `EDITOR_TEST_PHOTO=<key>`. For `import.mjs`, `EDITOR_TEST_RAW=<file in originales/>` picks the RAW, which needs a studio wall.
- Every test starts its own server on a fixed port and works on a copy of the versions (`EDITOR_VERSIONS`, `EDITOR_IMPORTS`).
- `test.mjs` needs at least two photos. `eyes_per_face.mjs` needs one group photo (two or more faces).

### Platform

The pipeline is built for macOS:

- The two `.swift` files (Vision face detection and image decoding) are compiled with `swiftc` the first time they are needed.
- `sips`, `memory_pressure` and `sysctl` are called from the code, and `Abrir editor.command` uses `open` and `lsof`.
- `portrait-qa/recipe/output.py` reads the camera's embedded JPEG with `exiftool`.

### Requirements

Python 3.12, with `numpy`, `opencv-python-headless`, `pillow`, `tifffile`, `rawpy`, `scipy` and `pymatting` (which brings `numba` and `llvmlite`), pinned in `pipeline/requirements.txt`, which `portrait-qa/` shares.

## Vendored code and licenses

| Code | Version | License | Where |
|---|---|---|---|
| DialKit | 2.0.2 | MIT | `pipeline/recipe/vendor/dialkit-2.0.2/LICENSE` |
| Sonner | 2.0.8 | MIT | `pipeline/recipe/vendor/sonner-2.0.8/LICENSE-sonner.md` |
| React and ReactDOM, bundled with Sonner | 19.3.1 | MIT | `pipeline/recipe/vendor/sonner-2.0.8/LICENSE-react` |
| Film grain rendering (Newson, Faraj, Galerne, Delon; IPOL) | — | GPL v3+ | `portrait-qa/tools/film_grain/README.txt`. Build with `make`; needs libpng and libtiff. |

`vendor/sonner-2.0.8/entry.js` is the source of `sonner.global.js`, the one-file build that puts Sonner and React on `window` without a bundler in the page.

The style references in `pipeline/recipe/references.py` are public press images from Stripe, Ramp, Apple Newsroom, Robinhood, Public, Nothing and Linear. Only their URLs and credits are listed; no images are included. A project that picks one imports it from its URL as SKILL.md step 4 says.
