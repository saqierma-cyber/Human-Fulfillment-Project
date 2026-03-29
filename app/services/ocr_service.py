import io
import shutil

import fitz
import pytesseract
from PIL import Image

from app.core.config import get_settings


class OCRService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_available(self) -> bool:
        return shutil.which("tesseract") is not None

    def page_to_text(self, page: fitz.Page) -> str:
        matrix = fitz.Matrix(self.settings.ocr_pdf_zoom, self.settings.ocr_pdf_zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(image, lang=self.settings.ocr_language)
        return text.strip()

