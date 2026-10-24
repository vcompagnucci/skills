# Delivery

## Masters

16-bit TIFF with ICC at native resolution (`editadas/<photo>[-<style>].tif`), next to its 8-bit dithered PNG. Write them atomically (temporary file, then rename): the editor may read while a render runs.

## Exports

- PNG or TIFF 16-bit, lossless WebP, and JPEG only at q100 4:4:4 where the project allows JPEG.
- Full size is a bit-exact crop of the master; smaller sizes are downscaled in linear light (in sRGB, fine hair over a light wall darkens).
- **"RAW export"** is a linear DNG with the same data as the TIFF (Format DNG in the editor). Say plainly it holds no more quality.
- **Circle** (Shape in the editor) is transparency outside the inscribed circle, in PNG, TIFF and WebP only; **Flip** mirrors the pixels, with no orientation tag.
- **To a named folder:** a full-size 16-bit TIFF or 8-bit PNG is the master itself: `cp editadas/<photo>[-<style>].tif` (or `.png`) into the folder and `cmp` each copy. Any other format, size, crop or adjustment comes from the editor's server, the two calls `tools/export_check.py` makes (`POST /api/prepare`, then `GET /api/file/<id>`), with the file saved straight into the folder.
- Anything that leaves the project goes to the delivery folder the photographer names, never `~/Downloads`, `~` or `~/Desktop` (Desktop syncs to the cloud on macOS).
