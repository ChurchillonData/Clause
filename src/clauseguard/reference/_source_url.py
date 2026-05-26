"""Helpers for reading document metadata from source URLs."""

from __future__ import annotations


def year_from_url(source_url: str, default: int) -> int:
    """Return the first four digit year found in a URL."""

    year = first_four_digit_part(source_url)
    return year if year is not None else default


def act_number_from_url(source_url: str) -> int | None:
    """Return the last numeric URL part as an Act number."""

    parts = [part for part in source_url.rstrip("/").split("/") if part]
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
    return None


def first_four_digit_part(text: str) -> int | None:
    """Return the first four digit integer in a string."""

    for part in text.replace("/", " ").replace("-", " ").split():
        if len(part) == 4 and part.isdigit():
            return int(part)
    return None
