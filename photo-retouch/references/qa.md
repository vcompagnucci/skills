# QA gates

The tools and their thresholds live in `templates/portrait-qa/tools/`; the thresholds are in each tool's docstring. Keep the numbers when you copy a tool.

- **Edge gate** (`edge_gate.py`): normal profiles every 8 px along the contour, the edit against the same render with the wall unbrightened, per class (skin, dark, mixed). It is the checkable form of "contours identical to the camera original": edge defects are sub-pixel and invisible at fit.
- **Color zones** (`color_zones.py`): fixed face zones against the camera JPEG. Register the camera JPEG to the RAW develop per crop first (phase correlation): it is offset ~3 px, and unregistered comparisons show fake differences at edges.
- **Gradual corrections:** at most 0.09 EV between neighbouring pixels at a correction's border. Steeper transitions showed as visible steps.
- **Wall-only changes leave people untouched:** after one, `tools/compare_masters.py` shows people's pixels identical. A background edit must never move a person.
