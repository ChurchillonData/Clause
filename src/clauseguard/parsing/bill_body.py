"""Helpers for identifying bill body lines."""

from __future__ import annotations

from clauseguard.parsing.lines import TextLine


def bill_body_lines(lines: list[TextLine]) -> list[TextLine]:
    """Return lines from the bill body, skipping arrangement pages."""

    for index, line in enumerate(lines):
        if line.text.casefold() == "a bill":
            return lines[index:]
    return lines


def clause_heading(prefix: str | None, separator: str | None, body: str) -> str | None:
    """Return clause heading text when the line clearly contains a heading."""

    if body.startswith("("):
        return None
    if prefix or separator in {"-", "–", "—"}:
        return body or None
    return None
