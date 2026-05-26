"""Tests for legal citation parsing."""

from __future__ import annotations

from clauseguard.reference.citation import node_id_from_ref, parse_citation


def test_parse_act_number_and_year() -> None:
    """Parse Act number and year signals."""

    citation = parse_citation("Act 769 of 2008")

    assert citation.act_number == 769
    assert citation.year == 2008


def test_parse_title_and_parenthesised_act() -> None:
    """Parse title citations with a parenthesised Act number."""

    citation = parse_citation("the National Communications Authority Act (Act 769)")

    assert citation.act_number == 769
    assert citation.title == "National Communications Authority Act"


def test_parse_section_and_qualifier() -> None:
    """Parse section references and amendment qualifiers."""

    citation = parse_citation("section 12 of Act 769, as amended")

    assert citation.section_ref == "12"
    assert citation.act_number == 769
    assert citation.qualifier == "as amended"


def test_parse_constitution_article() -> None:
    """Parse Constitution article citations."""

    citation = parse_citation("Article 19(2)(d) of the Constitution")

    assert citation.is_constitution
    assert citation.article_ref == "19(2)(d)"


def test_node_id_from_nested_reference() -> None:
    """Convert nested legal references to node IDs."""

    assert node_id_from_ref("s", "12(3)(b)") == "s_12_3_b"
    assert node_id_from_ref("art", "19(2)(d)") == "art_19_2_d"
