# Delivery

## Masters

16-bit TIFF with ICC at native resolution, next to the display file. Write them atomically (temporary file, then rename): the editor may read while a render runs.

## Exports

- PNG or TIFF 16-bit, lossless WebP, and JPEG only at q100 4:4:4 where the project allows JPEG.
- Full size is a bit-exact crop of the master; smaller sizes are downscaled in linear light (in sRGB, fine hair over a light wall darkens).
- **"RAW export"** is a linear DNG with the same data as the TIFF. Say plainly it holds no more quality.
- Anything that leaves the project goes to the delivery folder the photographer names, never `~/Downloads`, `~` or `~/Desktop` (Desktop syncs to the cloud on macOS).

## Editors

A photo editor is a localhost-only tool launched by a `.command` file. How to build one: [editor.md](editor.md).
