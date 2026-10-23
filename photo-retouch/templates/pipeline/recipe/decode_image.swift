// Lee una imagen con ImageIO (todo lo que abre macOS) y la pasa a sRGB con ColorSync, a 16 bits por canal: sips lo
// haria en 8. Lo transparente queda sobre blanco. La orientacion no se aplica aca (la aplica import_photo.py).
// Uso: decode_image <entrada> <salida>  ->  salida: ancho y alto (uint32) y despues RGBX de 16 bits, little endian.
// Lo compila import_photo.py en work/bin/ (regenerable).
import Foundation
import ImageIO
import CoreGraphics

let args = CommandLine.arguments
guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
  FileHandle.standardError.write("macOS can't read this file\n".data(using: .utf8)!); exit(1)
}
let w = img.width, h = img.height
let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let info = CGImageAlphaInfo.noneSkipLast.rawValue | CGBitmapInfo.byteOrder16Little.rawValue
guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 16, bytesPerRow: w * 8, space: srgb, bitmapInfo: info) else { exit(2) }
ctx.setFillColor(CGColor(colorSpace: srgb, components: [1, 1, 1, 1])!)
ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
ctx.setRenderingIntent(.relativeColorimetric)
ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
var header = [UInt32(w), UInt32(h)]
var out = Data(bytes: &header, count: 8)
out.append(Data(bytes: ctx.data!, count: w * h * 8))
try! out.write(to: URL(fileURLWithPath: args[2]))
