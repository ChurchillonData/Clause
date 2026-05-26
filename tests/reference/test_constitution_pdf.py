"""Tests for local Constitution PDF fallback parsing."""

from __future__ import annotations

from clauseguard.reference.constitution_pdf import parse_constitution_text


def test_parse_constitution_text_builds_article_hierarchy() -> None:
    """Parse article, subclause, and paragraph hierarchy from text."""

    text = """
    19.
    (1) A person charged with a criminal offence shall be given a fair hearing.
    (2) A person shall be permitted-
    (d) to defend themself before the court.
    """

    document = parse_constitution_text(text, "local.pdf")

    assert document.nodes["art_19"].children_ids == ["art_19_1", "art_19_2"]
    assert document.nodes["art_19_2_d"].text == "to defend themself before the court."
    assert document.nodes["art_19_2_d"].parent_id == "art_19_2"


def test_parse_constitution_text_ignores_schedule_sections() -> None:
    """Do not let schedule section numbers overwrite Constitution articles."""

    text = """
    19.
    (1) Main constitutional article.
    FIRST SCHEDULE
    TRANSITIONAL PROVISIONS
    19.
    (1) Schedule section text.
    """

    document = parse_constitution_text(text, "local.pdf")

    assert document.root_node_ids == ["art_19"]
    assert document.nodes["art_19_1"].text == "Main constitutional article."


def test_parse_constitution_text_ignores_lower_numbered_definitions() -> None:
    """Do not parse numbered definition text as earlier articles."""

    text = """
    156.
    (1) Judicial officers shall take the oath.
    3. "supervisory jurisdiction" includes writs.
    157.
    (1) The rules committee may make rules.
    """

    document = parse_constitution_text(text, "local.pdf")

    assert document.root_node_ids == ["art_156", "art_157"]
    assert "supervisory jurisdiction" in document.nodes["art_156_1"].text
