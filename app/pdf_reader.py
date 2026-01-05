from __future__ import annotations

from dataclasses import dataclass
from typing import List
import pdfplumber
from pypdf import PdfReader


@dataclass
class PageText:
    page_number: int
    text: str


def read_pdf_pages(path: str) -> List[PageText]:
    """
    Returns list of pages with extracted text.
    Uses pdfplumber primarily; falls back to pypdf.
    """
    pages: List[PageText] = []

    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                txt = page.extract_text() or ""
                pages.append(PageText(page_number=i, text=txt))
        return pages
    except Exception:
        # fallback
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages, start=1):
            txt = page.extract_text() or ""
            pages.append(PageText(page_number=i, text=txt))
        return pages
