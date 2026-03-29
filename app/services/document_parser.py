from pathlib import Path

import fitz
from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub

from app.core.config import get_settings
from app.services.ocr_service import OCRService


class DocumentParser:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.ocr_service = OCRService()

    def parse(self, path: Path) -> list[dict]:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._parse_pdf(path)
        if suffix == ".epub":
            return self._parse_epub(path)
        if suffix == ".txt":
            return self._parse_txt(path)
        raise ValueError(f"Unsupported file type: {path.suffix}")

    def _parse_pdf(self, path: Path) -> list[dict]:
        result: list[dict] = []
        doc = fitz.open(path)
        try:
            for page_index, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if not text and self.settings.ocr_enabled and self.ocr_service.is_available():
                    text = self.ocr_service.page_to_text(page)
                result.append({"page_label": str(page_index), "text": text})
        finally:
            doc.close()
        return result

    def _parse_epub(self, path: Path) -> list[dict]:
        book = epub.read_epub(str(path))
        result: list[dict] = []
        page_index = 1
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_body_content(), "lxml")
            text = soup.get_text("\n", strip=True)
            if text:
                result.append({"page_label": f"section-{page_index}", "text": text})
                page_index += 1
        return result

    def _parse_txt(self, path: Path) -> list[dict]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return [{"page_label": "txt-1", "text": text}]
