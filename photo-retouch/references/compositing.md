# Compositing and edges

Image model: I = αF + (1−α)B. Reference implementation: `templates/portrait-qa/recipe/matte.py` (closed-form matting, guided upsample, color-line projection).

- **Brighten the wall additively by its share of each pixel:** I' = I + (1−α)(g−1)B. Multiplying the whole pixel left a light rim on skin and a dark one on hair and clothing.
- **Opaque dark clothing gets α exactly 1.** In a black, a 1 % wall share already adds 2–3 L*.
- **Clamp the wall share per channel**, so it is never brighter than the pixel in any channel. A luminance clamp let blue and green through and greyed brown hair.
- **After a tone curve, the wall inside an edge pixel is (1−α)B·k_pixel/k_wall**, not (1−α)B. Using (1−α)B gave one portrait a grey crown.
- **Estimate the wall light without the person and a margin around them.** Otherwise the hair gets a +1.5–3 L* aura.
- **Where person and wall colors are close** (shadowed skin against the wall), the color projection fails because |F−B| is small. Take the edge from the shape there, ramped over the sensor width.
- **Judge an edge on the edited render** against the same render with the wall left unbrightened, plus a camera-vs-edit montage at fixed points: eyelid, temple, lips, chin, clothing, hair. An alpha-only preview looked fine while the render had rims.
- **Hand-drawn keep polygons go after the matting solve, never inside it**, and the layers record which polygons built them so a change rebuilds them. Inside the closed-form solve they pushed nearby wall to 0.4–0.8 alpha and flipped a lace tip; after it, 0 of 88,674 pixels stayed under alpha 1.
