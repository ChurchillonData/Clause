"""Tests for bill reference extraction."""

from __future__ import annotations

from clauseguard.parsing.references import extract_references


def test_extract_references_deduplicates_in_text_order() -> None:
    """Extract common legal references from bill text."""

    refs = extract_references("See Act 769, section 12 of Act 769, and Article 19(2)(d). Act 769 applies.")

    assert [ref.text for ref in refs] == ["Act 769", "section 12 of Act 769", "Article 19(2)(d)"]
