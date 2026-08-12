import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytesseract
from PIL import Image, UnidentifiedImageError

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore[assignment]


def _extract_docx_text(file_path: str) -> str:
    """Extracts all text from Word (.docx) document XML."""
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            texts = []
            for p in tree.iter(f"{{{ns['w']}}}p"):
                p_text = "".join(node.text for node in p.iter(f"{{{ns['w']}}}t") if node.text)
                if p_text.strip():
                    texts.append(p_text.strip())
            return "\n".join(texts)
    except Exception as exc:
        print(f"[OCR] DOCX extraction error: {exc}")
        return ""


def _mac_vision_ocr(image_path: str) -> str:
    """Uses native macOS Vision framework for 100% accurate text extraction from images."""
    swift_cmd = f"""
import Vision
import AppKit

let path = "{image_path}"
guard let image = NSImage(contentsOfFile: path),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {{
    exit(1)
}}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])

if let results = request.results {{
    let text = results.compactMap {{ $0.topCandidates(1).first?.string }}.joined(separator: "\\n")
    print(text)
}}
"""
    try:
        proc = subprocess.run(
            ["swift", "-"],
            input=swift_cmd,
            text=True,
            capture_output=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except Exception as exc:
        print(f"[OCR] macOS Vision OCR warning: {exc}")
    return ""


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore").strip()

    if suffix in {".docx", ".doc"}:
        docx_text = _extract_docx_text(str(path))
        if docx_text:
            return docx_text

    if suffix == ".pdf":
        if PdfReader is not None:
            try:
                reader = PdfReader(str(path))
                pages = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages).strip()
                if text:
                    return text
            except Exception as exc:
                print(f"[OCR] PDF extraction warning: {exc}")

    if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}:
        vision_text = _mac_vision_ocr(str(path))
        if vision_text:
            return vision_text

    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image).strip()
    except Exception as exc:
        print(f"[OCR] Warning during pytesseract OCR: {exc}")
        text = ""

    if not text:
        raise ValueError("No readable text found. Please upload a clear photo, PDF, or Word document of your pregnancy medical report.")

    return text

