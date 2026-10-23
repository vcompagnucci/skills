# Measuring a reference

- **Research and cite before choosing a number;** my taste is not the source. That covers references (SKILL.md step 4), looks and "best practices".
- **The same code measures the reference and my version**, on the same crop at the same face width, one above the other. The photographer rejected eyeballed looks.
- **Skin color by brightness band** (shadow, mid, light) as a*, b*, C* and hue. Real skin is redder in shadow and yellower in light, and a single average hid wrong shadows.
- **Face shadow is measured on skin only.** An ellipse picks up glasses and hair: it read 28 against 47 L* on one portrait.
- **Compare local contrast only in the frequency bands the reference can show.** A ~400 px avatar has no fine bands; matching them removes the subject's skin texture.
- **The reference's softness is the screenshot's, not the look.** A small capture has no fine detail; copying its softness blurs the photo.

## Building a style

- **Looks come from published recipes with their numbers, cited.** An invented batch recolored or flattened the wall; the photographer called them horrible.
- **A style is global light settings plus a wall-only background adjustment.** Temperature and tint stay off people: global tints turned black shirts brown and tanned the skin.
- **From a reference take the wall and the direction, never its light.** Copying a reference's light clipped 12–16 % of the frame and looked washed out or muddy ("no es poner el filtro y ya"). Exposure and blacks are then fitted per photo (`tools/look_fit.py`).

## Tolerances

The exit of step 5. Each comes from a correction or a measured failure.

| What | Tolerance | Tool |
|---|---|---|
| Exposure | skin light toward the reference's, at most ±0.3 EV per photo | `look_fit.py` |
| Blacks | black clothing at L* 5–10, p1 not crushed | `look_fit.py` |
| Face clipping | 0 % of the face clipped in any channel; pull Highlights and Whites first (−20 and −8 cost 1.5 L* of skin) | `look_fit.py` |
| Frame clipping | 0.12 % of the frame at most, as the approved looks measured | `ref_measure.py` |
| Skin hue | 120–126° on the vectorscope, on the skin line (~123°), checked before and after every color step: the develop left 115° (pink), +12° turned a face yellow | `color_check.py` |
| Skin color by band | shadow, mid and light each toward the reference's a*, b* and C*, compared on skin only | `ref_measure.py` |
| Skin histogram match | slope capped at 2.5; uncapped it matched exactly and left dark islands | `ref_measure.py` |
| Neutral wall | a*, b* about 0 unless the style colors it | `wall_measure.py` |
| Fine skin texture | at least 80 % of the base's (SKILL.md step 3) | `band_energy` (`portrait-qa/recipe/measure.py`) |
| Between photos of one set | skin under ΔE 2 apart when they are shown together | `color_check.py` |

A number outside its tolerance is fixed, or written in README > Pendiente with the reason it stays.
