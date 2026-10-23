// Ubica las caras de una foto con Vision (el detector de macOS): solo donde estan, nada se genera.
// Uso: faces_vision <imagen>  ->  JSON [{"x","y","w","h"}] en pixeles, origen arriba a la izquierda.
// Lo compila import_photo.py en work/bin/ (regenerable).
import Foundation
import Vision
import ImageIO

let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let src = CGImageSourceCreateWithURL(url as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else { print("[]"); exit(0) }
let W = Double(img.width), H = Double(img.height)
let req = VNDetectFaceRectanglesRequest()
try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
let faces = (req.results ?? []).map { f -> [String: Int] in
  let b = f.boundingBox
  return ["x": Int(b.minX * W), "y": Int((1 - b.maxY) * H), "w": Int(b.width * W), "h": Int(b.height * H)]
}
print(String(data: try! JSONSerialization.data(withJSONObject: faces), encoding: .utf8)!)
