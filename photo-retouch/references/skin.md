# Skin

Reference implementation: `heal.py`, `skin.py`, `undereye.py`, `lint.py` in `templates/pipeline/recipe/`; `templates/portrait-qa/recipe/skin_retouch.py` has the rejected one-number under-eye.

- **Heal, never blur.** Telea inpainting for the tone, a texture patch from the evenest neighbouring skin, and frequency-split dodge & burn. Blur reads as plastic skin.
- **Skin chroma cap:** measurement.md > Tolerances. Matching hue and chroma blindly over-saturated the skin.
- **Under-eyes: measure each eye against a smooth membrane** through the surrounding skin, not against one cheek number. Apply gain only, so the texture stays, and leave the lid strip untouched at 100 %. Deliver below the maximum with a slider. One-number fixes either covered the eyes or did nothing, and the under-eyes took 5 rounds.
- **Lint on black clothing:** isolated light points at least 5 L* over the fabric. Skip clusters, colored things, hair and faces. Fill from the edge, never copy texture: it repeats visibly.
- **Hot pixels get a local median.** A global median erases the catchlights.
- **Fill the holes in skin masks.** Specular forehead highlights read as "not skin" and leave flat grey patches.
