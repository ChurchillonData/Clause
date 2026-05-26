"""Tests for PDF extraction safety checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from clauseguard.parsing.pdf_extractor import PdfExtractionError, extract_pdf_pages


def test_extract_pdf_pages_rejects_missing_file(tmp_path: Path) -> None:
    """Fail clearly when a PDF is missing."""

    with pytest.raises(PdfExtractionError, match="PDF does not exist"):
        extract_pdf_pages(tmp_path / "missing.pdf")
