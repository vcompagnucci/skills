# Editor

Optional. Build one only when the photographer asks to review, tweak or export the edits themselves. The working editor is in [templates/pipeline/](../templates/README.md): start from it and change it, never from a blank page.

## What it is

- **A local server** (`recipe/editor_server.py`, Python stdlib) on `127.0.0.1` only, started by a `.command` launcher on the next free port. It serves the page, the display copies, the versions file and every export.
- **One page** (`recipe/viewer_template.html`, vanilla HTML and WebGL), rebuilt by the server on each request so an imported photo appears without rerunning a generator.
- **One shader** that applies the panel's adjustments to an 8-bit display copy of each master, and a control panel (DialKit) on the right.
- **Versions**: one list of names shared by every photo, with values stored per photo, in `editadas/versiones.json`.

## Screen equals export

The promise is that the file downloaded is what the screen showed. Each rule below keeps it.

- **One reference implementation.** The server's Python is the reference; the shader is a line-by-line copy of it. Change one, change the other, run `tools/download_parity.mjs`. Measured at most 1 level of 255 apart on the same input.
- **Export from the 16-bit master on the server**, applying the adjustments in linear light. The canvas works from a dithered 8-bit copy; the file must carry the master's full precision.
- **Start the panel at the master.** Styles made with curves, local light and grain can't be written as panel values (mean error 1.7–4.2 L*). So the starting values are the panel settings closest to the master, solved per photo and style by least squares and rounded to each control's step, and the editor applies only the difference from that start over the untouched master.
- **Versions store absolute values.** When starting values are recomputed, check the saved versions: each one now applies a different difference.
- **Feed the browser rounded 8-bit copies of 16-bit PNG layers.** Chrome reads 16-bit PNG as `v>>8` without rounding, which biased the wall layers.

Done when `tools/export_check.py` passes and `tools/download_parity.mjs` shows no region over 1 level.

## Versions

- **Saved through the server into the project's JSON file**, never browser storage. Browser storage is per origin, the server takes the next free port, and versions vanished when the port changed.
- **Pressing Save version on the hidden base switches to the new version.** The cross-browser run found it kept editing the base after saving.
- **Seeding versions from code replaces only versions a photo still has**, and removes dropped looks through an explicit retired list. A re-seed must never bring back a version the photographer deleted.
- **Per-face controls are keyed by person, not by position** (`Under-eyes.<face label>`), and the old single number keeps meaning "every face". Copying a version from a portrait to a group photo must change the same face. Migrate old keys on load, after backing up the versions file.

## Server

- **The page detects a server older than its features** and shows "reopen the launcher" in place of the export summary. An old server can't export adjustments and can overwrite the versions file. The photographer's running server is theirs: ask before stopping it (practices.md > Shared machine).
- **Re-ask for the master list when the window regains focus**, and when a master is being rewritten, wait and retry. A master re-rendered by the pipeline reloads without rebuilding the page.
- **Imports** accept any RAW LibRaw reads and any image macOS opens, refuse JPEG in a `.sin-jpg` project, and convert to 16-bit sRGB with ColorSync (`sips` dropped to 8 bits). Features that depend on the hand inventory (retouch, under-eyes) stay off until it's done.
- **Heavy work started from the editor** runs as a child of the server, one photo at a time, with `MallocLargeCache=0 nice -n 19`, waiting while the machine is saturated. One RAW import reaches 2.8 GB.

## Tests

- Proof, refactors and shared-machine rules: [practices.md](practices.md) > Every change (step 4) and > Shared machine. Here, each suite gets a copy of the versions file through `EDITOR_VERSIONS`. Per-feature checks (per-face under-eyes, `apply_version` 41 of 41, `export_check` 36 of 36) caught what the general suite missed; the performance and export rewrites were kept on preview identical at Fit, 100 % and 50 %, 7 export cases and 36 of 36 checks.
- Chrome, WebKit and Firefox at several viewports, plus reduced motion: `tools/editor_test/browsers.mjs`.
- **The suites are the spec of this version:** one check per feature, from zoom and the before/after divider to export crop and per-face controls. A rebuilt or changed editor is this version when they all pass.

Done when every suite in `tools/editor_test/` passes and the new feature's own test is among them.

## Interface

The rest of the interface (zoom, before/after divider, export panel and crop, version menu, tooltips, Sonner notices, offline libraries) is in the template's code. Change it by the photographer's taste, and follow the project's UI conventions.
