"""Normalise extracted bill text into page-aware lines."""

from __future__ import annotations

from dataclasses import dataclass

from clauseguard.parsing.schemas import ExtractedPage


@dataclass(frozen=True)
class TextLine:
    """One non-empty bill text line with its source page."""

    text: str
    page_number: int | None


def lines_from_pages(pages: list[ExtractedPage]) -> list[TextLine]:
    """Return normalised lines from extracted pages."""

    lines: list[TextLine] = []
    for page in pages:
        lines.extend(TextLine(clean_line(line), page.page_number) for line in page.text.splitlines())
    return [line for line in lines if line.text]


def lines_from_text(text: str) -> list[TextLine]:
    """Return normalised lines from plain text."""

    return [TextLine(clean_line(line), None) for line in text.splitlines() if clean_line(line)]


def clean_line(text: str) -> str:
    """Normalise one extracted text line."""

    return " ".join(text.replace("\u00a0", " ").split())
