"""
vision.py — OCR (read text from images/screenshots) + object/face detection.
Adapted from Farhan's own project: smart-vision-assistant-pro
(github.com/Farhanillahiclass/smart-vision-assistant-pro), rebuilt here as a
local module instead of a notebook so Gyrus can call it directly.

Requires the Tesseract OCR *engine* installed separately (not just the pip
package): https://github.com/UB-Mannheim/tesseract/wiki (Windows) or
`sudo apt install tesseract-ocr` (Linux) / `brew install tesseract` (Mac).
"""

import cv2
import pytesseract

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def read_text_from_image(image_path: str) -> str:
    """OCR: extract text from an image file (photo, screenshot, scanned doc)."""
    img = cv2.imread(image_path)
    if img is None:
        return f"Image load nahi ho saki: {image_path}"
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresh)
    return text.strip() or "Koi text nahi mila."


def detect_faces(image_path: str) -> int:
    """Face detection via Haar Cascade — no extra model download needed,
    matches the automatic-fallback approach from the original project."""
    img = cv2.imread(image_path)
    if img is None:
        return 0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(read_text_from_image(sys.argv[1]))
