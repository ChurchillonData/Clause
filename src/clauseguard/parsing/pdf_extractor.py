"""Extract text from bill PDFs."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from clauseguard.parsing.schemas import ExtractedPage


class PdfExtractionError(ValueError):
    """Raised when a bill PDF cannot be read safely."""


def extract_pdf_pages(pdf_path: Path) -> list[ExtractedPage]:
    """Extract text page by page from a PDF."""

    if not pdf_path.exists():
        raise PdfExtractionError(f"PDF does not exist: {pdf_path}")
    try:
        return read_pdf_pages(pdf_path)
    except Exception as exc:
        raise PdfExtractionError(f"Could not extract PDF text: {pdf_path}") from exc


def read_pdf_pages(pdf_path: Path) -> list[ExtractedPage]:
    """Read PDF pages using pdfplumber."""

    pages: list[ExtractedPage] = []
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            pages.append(ExtractedPage(page_number=index, text=text))
    if not any(page.text.strip() for page in pages):
        raise PdfExtractionError(f"No extractable text found: {pdf_path}")
    return pages
