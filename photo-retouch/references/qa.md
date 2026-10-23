# QA gates

The gate tools live in `templates/portrait-qa/tools/` (`compare_masters.py` in `templates/pipeline/tools/`); each tool's docstring holds its thresholds. Keep the numbers when you copy a tool.

- **Edge gate** (`edge_gate.py`): normal profiles every 8 px along the contour, the edit against the same render with the wall unbrightened, per class (skin, dark, mixed). It is the checkable form of "contours identical to the camera original": edge defects are sub-pixel and invisible at fit.
- **Color zones** (`color_zones.py`), for what a style leaves at the camera's color: fixed face zones against the camera JPEG. Register it to the RAW develop per crop first (phase correlation): it is offset ~3 px, and unregistered comparisons show fake differences at edges.
- **Gradual corrections:** at most 0.09 EV between neighbouring pixels at a correction's border. Steeper transitions showed as visible steps.
- **Wall-only changes leave people untouched:** after one, `tools/compare_masters.py` shows people's pixels identical.
