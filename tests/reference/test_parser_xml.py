"""Tests for the Akoma Ntoso XML parser."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from clauseguard.reference.parser_xml import parse_xml_document, parse_xml_file

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "xml"


def read_fixture(name: str) -> str:
    """Return one XML fixture as text."""

    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_simple_act_metadata_and_section() -> None:
    """Parse a simple Act with one section."""

    document = parse_xml_document(
        read_fixture("simple_act.xml"),
        "https://ghalii.org/akn/gh/act/2008/769/eng@.xml",
        "act",
    )

    section = document.nodes["sec_1"]
    assert document.doc_type == "act"
    assert document.act_number == 769
    assert document.year == 2008
    assert document.title == "National Communications Authority Act, 2008"
    assert document.root_node_ids == ["sec_1"]
    assert section.heading == "Establishment of the Authority"
    assert section.text == "There is established by this Act the National Communications Authority."


def test_parse_nested_nodes_preserves_parent_child_links() -> None:
    """Parse nested subsections and paragraphs without flattening them."""

    document = parse_xml_document(
        read_fixture("nested_act.xml"),
        "https://ghalii.org/akn/gh/act/2020/1038/eng@.xml",
        "act",
    )

    section = document.nodes["sec_12"]
    subsection = document.nodes["sec_12_subsec_3"]
    paragraph = document.nodes["sec_12_subsec_3_para_b"]
    assert section.children_ids == ["sec_12_subsec_3"]
    assert subsection.parent_id == "sec_12"
    assert subsection.children_ids == ["sec_12_subsec_3_para_b"]
    assert paragraph.parent_id == "sec_12_subsec_3"
    assert paragraph.text == "The directive shall be published in the Gazette."


def test_parse_references_inside_content() -> None:
    """Capture link hrefs while preserving the visible text."""

    document = parse_xml_document(
        read_fixture("references_act.xml"),
        "https://ghalii.org/akn/gh/act/2012/843/eng@.xml",
        "act",
    )

    section = document.nodes["sec_4"]
    assert section.text == "This section applies despite section 12 of Act 769."
    assert len(section.references) == 1
    assert section.references[0].text == "section 12 of Act 769"
    assert section.references[0].href == "/akn/gh/act/2008/769/section/12"


def test_parse_constitution_article() -> None:
    """Parse Constitution articles separately from Acts."""

    fetched_at = datetime(2026, 5, 26, tzinfo=timezone.utc)
    document = parse_xml_document(
        read_fixture("constitution_article.xml"),
        "https://ghalii.org/akn/gh/act/1992/constitution/eng@.xml",
        "constitution",
        fetched_at,
    )

    article = document.nodes["art_19"]
    assert document.doc_type == "constitution"
    assert document.act_number is None
    assert document.year == 1992
    assert document.fetched_at == fetched_at
    assert article.level == "article"
    assert article.heading == "Fair trial"


def test_parse_xml_file_reads_from_disk() -> None:
    """Parse a fixture through the file based API."""

    document = parse_xml_file(
        FIXTURE_DIR / "simple_act.xml",
        "https://ghalii.org/akn/gh/act/2008/769/eng@.xml",
        "act",
    )

    assert document.content_hash
    assert "sec_1" in document.nodes


def test_parse_fallback_metadata_and_constructed_ids() -> None:
    """Use URL metadata and constructed IDs when XML metadata is absent."""

    document = parse_xml_document(
        read_fixture("fallback_act.xml"),
        "https://ghalii.org/akn/gh/act/2021/999/eng@.xml",
        "act",
    )

    assert document.title == "Untitled legal document"
    assert document.year == 2021
    assert document.act_number == 999
    assert document.root_node_ids == ["s_5", "s_unnumbered"]
    assert document.nodes["s_5"].children_ids == ["s_5_6"]
    assert document.nodes["s_unnumbered"].number == "unnumbered"


def test_parse_missing_year_and_act_number_falls_back_safely() -> None:
    """Return safe empty metadata values when no source contains them."""

    document = parse_xml_document(
        read_fixture("fallback_act.xml"),
        "https://example.test/no-year/not-number",
        "act",
    )

    assert document.year == 0
    assert document.act_number is None


def test_invalid_xml_metadata_year_falls_back_to_url() -> None:
    """Use the URL year when XML date metadata is malformed."""

    xml = """
    <akomaNtoso>
      <act>
        <meta>
          <identification>
            <FRBRWork><FRBRdate date="bad-date"/></FRBRWork>
          </identification>
        </meta>
        <preface><p><shortTitle>Example Act</shortTitle></p></preface>
        <body>
          <section eId="sec_1"><num>1.</num><content><p>Text one.</p></content></section>
        </body>
      </act>
    </akomaNtoso>
    """

    document = parse_xml_document(xml, "https://ghalii.org/akn/gh/act/2024/1", "act")

    assert document.year == 2024


def test_duplicate_xml_node_ids_fail_loudly() -> None:
    """Reject duplicate XML node IDs instead of overwriting text."""

    xml = """
    <akomaNtoso>
      <act>
        <meta>
          <identification>
            <FRBRWork><FRBRdate date="2024-01-01"/></FRBRWork>
          </identification>
        </meta>
        <preface><p><shortTitle>Example Act</shortTitle></p></preface>
        <body>
          <section eId="sec_1"><num>1.</num><content><p>Text one.</p></content></section>
          <section eId="sec_1"><num>1.</num><content><p>Text two.</p></content></section>
        </body>
      </act>
    </akomaNtoso>
    """

    with pytest.raises(ValueError, match="Duplicate XML node id"):
        parse_xml_document(xml, "https://ghalii.org/akn/gh/act/2024/1", "act")
