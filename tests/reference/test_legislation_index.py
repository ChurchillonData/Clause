"""Tests for GhaLII legislation index parsing."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.legislation_index import parse_legislation_index

FIXTURE_ROOT = Path(__file__).parent / "fixtures"


def fixture_text(path: str) -> str:
    """Return fixture text."""

    return (FIXTURE_ROOT / path).read_text(encoding="utf-8")


def test_parse_legislation_index_extracts_unique_act_links() -> None:
    """Extract unique Acts and ignore non-Act links."""

    listings = parse_legislation_index(
        fixture_text("html/legislation_index.html"),
        "https://ghalii.org/legislation/",
    )

    assert [item.act_number for item in listings] == [769, 843]
    assert listings[0].year == 2008
    assert listings[0].url == "https://ghalii.org/akn/gh/act/2008/769"
    assert listings[1].title == "Data Protection Act, 2012"
