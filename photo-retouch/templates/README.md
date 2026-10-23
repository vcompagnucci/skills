# Photo-retouch templates

Starter code for a portrait-retouching project: RAW in, 16-bit masters and a local browser editor out. It was taken from two real retouching projects and scrubbed. Every per-photo table now holds one made-up example entry (`PHOTO_A`), so none of it describes a real photo.

Code comments are in Spanish. They explain why each number is what it is, and that reasoning is the most valuable part.

## What is here

| Folder | What it is |
|---|---|
| `pipeline/` | The full RAW-to-editor pipeline: develop, retouch (spots, hot pixels, wall marks, lint, under-eyes, skin), grade, wall matting and backdrop styles, plus the local editor (`recipe/editor_server.py` + `recipe/viewer_template.html`) and its tests (`tools/editor_test/`). |
| `portrait-qa/` | The QA tools from an earlier square-avatar project: edge gate and montage, alpha check, color zones, before/after sheets, frequency-band skin retouch (`recipe/skin_retouch.py`, `recipe/measure.py` `band_energy`), the matte it was validated on, and a film-grain renderer. It has its own `recipe/`, which is not the same as `pipeline/recipe/`. |

Both folders use the same layout. `recipe/` holds the steps and shared modules. `tools/` holds the one-off measurements and contact sheets you read before changing a number.

## How to start

1. Copy `pipeline/` into a new project folder. Put the RAWs in `originales/` (`develop.py` expects `<photo>.RAF`, so change the extension there for other cameras).
2. Create a venv: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Fill in `recipe/photos.py` by hand. Replace `PHOTO_A` with one entry per photo, keyed by the file name without its extension. The docstring explains every field. For group photos, also give each face id a label in `FACE_NAMES` in `recipe/viewer_template.html` (`{ "face-id": "Label" }`): saved versions key the per-face controls by those labels. Measure the fields on the developed image, using the sheets that `tools/grid.py`, `tools/check_faces.py`, `recipe/spots.py` and `recipe/wall.py` write to `proceso/`.
4. Run the steps in order, one photo per process: `recipe/develop.py`, then `recipe/retouch.py`, then `recipe/grade.py`, then `recipe/styles.py <photo>` (optional backdrop styles; `--seed` writes them as editor versions), and, only if an editor is wanted ([editor.md](../references/editor.md)), `recipe/viewer.py` and `Abrir editor.command`.
5. Delete `.sin-jpg` unless the brief says no JPG. While it exists, the editor only produces JPEG as a download.

`portrait-qa/` is a second reference, not a second pipeline. Copy the tools you need, together with the `recipe/` modules they import.

### Tests

- `tools/editor_test/test_server.py` runs against the Python server alone. The JS tests (`test.mjs`, `import.mjs`, `apply_version.mjs`, `styles_check.mjs`, `eyes_per_face.mjs`, `browsers.mjs`) need Playwright and Chrome. Set `PW_PATH` to the `node_modules` folder that contains `playwright`.
- By default the tests use the first photo in `recipe/photos.py`. Override it with `EDITOR_TEST_PHOTO=<key>`. For `import.mjs`, `EDITOR_TEST_RAW=<file in originales/>` picks the RAW, which needs a studio wall.
- Every test starts its own server on a fixed port and works on a copy of the versions (`EDITOR_VERSIONS`, `EDITOR_IMPORTS`).
- `test.mjs` needs at least two photos. `eyes_per_face.mjs` needs one group photo (two or more faces).

### Platform

The pipeline is built for macOS:

- The two `.swift` files (Vision face detection and image decoding) are compiled with `swiftc` the first time they are needed.
- `sips`, `memory_pressure` and `sysctl` are called from the code, and `Abrir editor.command` uses `open` and `lsof`.
- `portrait-qa/recipe/output.py` reads the camera's embedded JPEG with `exiftool`.

### Requirements

Python 3.12. The dependencies are whatever the code imports: `numpy`, `opencv-python-headless` (cv2), `pillow` (PIL), `tifffile`, `rawpy`, `scipy` and `pymatting`, which brings `numba` and `llvmlite`. They are pinned in `pipeline/requirements.txt`. `portrait-qa/` uses the same set.

## Vendored code and licenses

| Code | Version | License | Where |
|---|---|---|---|
| DialKit | 2.0.2 | MIT | `pipeline/recipe/vendor/dialkit-2.0.2/LICENSE` |
| Sonner | 2.0.8 | MIT | `pipeline/recipe/vendor/sonner-2.0.8/LICENSE-sonner.md` |
| React and ReactDOM, bundled with Sonner | 19.3.1 | MIT | `pipeline/recipe/vendor/sonner-2.0.8/LICENSE-react` |
| Film grain rendering (Newson, Faraj, Galerne, Delon; IPOL) | — | GPL v3+ | `portrait-qa/tools/film_grain/README.txt`. Build with `make`; needs libpng and libtiff. |

`vendor/sonner-2.0.8/entry.js` is the source of `sonner.global.js`, the one-file build that puts Sonner and React on `window` without a bundler in the page.

The style references in `pipeline/recipe/references.py` are public press images from Stripe, Ramp, Apple Newsroom, Robinhood, Public, Nothing and Linear. Only their URLs and credits are listed; no images are included, so download them yourself.
