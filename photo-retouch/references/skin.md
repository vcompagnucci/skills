# Skin

Reference implementation: `heal.py`, `skin.py`, `undereye.py`, `lint.py` in `templates/pipeline/recipe/`; `templates/portrait-qa/recipe/skin_retouch.py` has the rejected one-number under-eye.

- **Heal, never blur.** Telea inpainting for the tone, a texture patch from the evenest neighbouring skin, and frequency-split dodge & burn. Blur reads as plastic skin.
- **Skin chroma cap:** measurement.md > Tolerances. Matching hue and chroma blindly over-saturated the skin.
- **Under-eyes: measure each eye against a smooth membrane** through the surrounding skin, not against one cheek number. Apply gain only, so the texture stays, and leave the lid strip untouched at 100 %. Deliver at 70 %, the approved delivery (`INTENSITY` in `recipe/undereye.py`, baked into the master by `grade.py`). It is a pure gain, so the editor's slider scales it exactly. Without an editor, `INTENSITY` is the global strength, for every face; one face's strength is its `under_eye.light` and `under_eye.color` in `recipe/photos.py` (0–1, default 0.8; `under_eye.eyes` for one eye; the editor's 200 % end ignores both). Either one means a re-render. One-number fixes either covered the eyes or did nothing, and the under-eyes took 5 rounds.
- **Lint on black clothing:** isolated light points at least 5 L* over the fabric. Skip clusters, colored things, hair and faces. Fill from the edge, never copy texture: it repeats visibly.
- **Kept marks stay out of the skin mask:** every `kept` circle in `recipe/photos.py` is cut out of it after the hole-filling close, so redness, tone and shine leave it pixel-identical. The under-eye correction has its own mask: a kept mark inside the under-eye crescent is not protected, so check it on the step 3 crops.
- **Hot pixels get a local median.** A global median erases the catchlights.
- **Fill the holes in skin masks.** Specular forehead highlights read as "not skin" and leave flat grey patches.
