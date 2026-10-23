# Skin

Reference implementation: `templates/portrait-qa/recipe/skin_retouch.py`.

- **Heal, never blur.** Telea inpainting for the tone, a texture patch from the evenest neighbouring skin, and frequency-split dodge & burn. Blur reads as plastic skin.
- **Skin chroma stays at or under 1.25× the skin's natural chroma** when matching a reference's color. Matching hue and chroma blindly over-saturated the skin.
- **Under-eyes: measure each eye against a smooth membrane** through the surrounding skin, not against one cheek number. Apply gain only, so the texture stays, and leave the lid strip untouched at 100 %. Deliver below the maximum with a slider. One-number fixes either covered the eyes or did nothing, and the under-eyes took 5 rounds.
- **Lint on black clothing:** isolated light points at least 5 L* over the fabric. Skip clusters, colored things, hair and faces. Fill from the edge, without copying texture: copied texture repeats visibly.
- **Hot pixels get a local median.** A global median erases the catchlights.
- **Fill the holes in skin masks.** Specular forehead highlights read as "not skin" and leave flat grey patches.
