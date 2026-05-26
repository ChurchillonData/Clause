"""Tests for the GhaLII HTML fallback parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from clauseguard.reference.parser_html import HtmlParseError, parse_html_document, parse_html_file

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "html"


def read_fixture(name: str) -> str:
    """Return one HTML fixture as text."""

    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_simple_html_act() -> None:
    """Parse simple section blocks from HTML."""

    document = parse_html_document(
        read_fixture("simple_act.html"),
        "https://ghalii.org/akn/gh/act/2008/769",
        "act",
    )

    section = document.nodes["sec_1"]
    assert document.title == "National Communications Authority Act, 2008"
    assert document.act_number == 769
    assert document.year == 2008
    assert document.root_node_ids == ["sec_1", "sec_2"]
    assert section.heading == "Establishment of the Authority"
    assert section.text == "There is established by this Act the National Communications Authority."


def test_parse_html_references() -> None:
    """Capture visible links as references."""

    document = parse_html_document(
        read_fixture("references_act.html"),
        "https://ghalii.org/akn/gh/act/2012/843",
        "act",
    )

    section = document.nodes["sec_4"]
    assert section.text == "This section applies despite section 12 of Act 769."
    assert len(section.references) == 1
    assert section.references[0].text == "section 12 of Act 769"
    assert section.references[0].href == "/akn/gh/act/2008/769/section/12"


def test_parse_html_file_reads_from_disk() -> None:
    """Parse a fixture through the file based API."""

    document = parse_html_file(
        FIXTURE_DIR / "simple_act.html",
        "https://ghalii.org/akn/gh/act/2008/769",
        "act",
    )

    assert document.content_hash
    assert "sec_2" in document.nodes


def test_unclear_html_fails_loudly() -> None:
    """Reject HTML without confident section boundaries."""

    with pytest.raises(HtmlParseError, match="No confident section"):
        parse_html_document(
            read_fixture("unclear.html"),
            "https://ghalii.org/akn/gh/act/2026/1000",
            "act",
        )


def test_html_title_falls_back_to_title_tag() -> None:
    """Use the title tag when no h1 is present."""

    html = """
    <html>
      <head><title>Fallback Title Act</title></head>
      <body>
        <section class="section" data-number="1">
          <p>Section text.</p>
        </section>
      </body>
    </html>
    """

    document = parse_html_document(html, "https://example.test/act/2026/1001", "act")

    assert document.title == "Fallback Title Act"


def test_html_section_detection_accepts_common_class_and_id_variants() -> None:
    """Parse common section markers used by web HTML."""

    html = """
    <html><body>
      <h1>Example Act</h1>
      <div class="section current"><h2>Section 1. First</h2><p>Text one.</p></div>
      <div id="sec_2"><h2>Section 2. Second</h2><p>Text two.</p></div>
    </body></html>
    """

    document = parse_html_document(html, "https://ghalii.org/akn/gh/act/2024/1", "act")

    assert list(document.nodes) == ["s_1", "sec_2"]


def test_html_heading_without_number_does_not_crash() -> None:
    """Use an unnumbered fallback when a section heading has no number."""

    html = """
    <html><body>
      <h1>Example Act</h1>
      <div class="section"><h2>Section</h2><p>Text one.</p></div>
    </body></html>
    """

    document = parse_html_document(html, "https://ghalii.org/akn/gh/act/2024/1", "act")

    assert document.nodes["s_unnumbered"].number == "unnumbered"


def test_duplicate_html_section_ids_fail_loudly() -> None:
    """Reject duplicate HTML section IDs instead of overwriting text."""

    html = """
    <html><body>
      <h1>Example Act</h1>
      <div id="sec_1"><h2>Section 1. First</h2><p>Text one.</p></div>
      <div id="sec_1"><h2>Section 1. Duplicate</h2><p>Text two.</p></div>
    </body></html>
    """

    with pytest.raises(HtmlParseError, match="Duplicate section id"):
        parse_html_document(html, "https://ghalii.org/akn/gh/act/2024/1", "act")
