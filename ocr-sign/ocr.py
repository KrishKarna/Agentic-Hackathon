import os
import shutil
import cv2
import pytesseract
from PIL import Image


if not shutil.which("tesseract"):
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if os.path.isfile(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            break


def read_sign(frame):
    if frame is None:
        return ""

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)

        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception:
        return ""
