"""Tests for deterministic bill clause splitting."""

from __future__ import annotations

from pathlib import Path

import pytest

from clauseguard.parsing.clause_splitter import parse_bill_text
from clauseguard.parsing.lines import TextLine
from clauseguard.parsing.clause_splitter import parse_bill_lines
from clauseguard.parsing.parser_state import BillParseError

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def fixture_text(name: str) -> str:
    """Return one text fixture."""

    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_bill_text_preserves_clause_hierarchy() -> None:
    """Parse clauses, subclauses, paragraphs, and subparagraphs."""

    document = parse_bill_text(fixture_text("sample_bill.txt"), "Sample Bill", "raw.pdf")

    assert document.root_node_ids == ["cl_1", "cl_2", "sch_first"]
    assert document.nodes["cl_1"].heading == "Establishment of the Authority"
    assert document.nodes["cl_1_subcl_2_para_b_subpara_i"].text.startswith("The property")
    assert document.nodes["cl_2_subcl_1"].references[0].text == "Act 769"
    assert document.nodes["cl_2_subcl_2"].references[0].text == "Article 19(2)(d)"


def test_parse_bill_lines_records_page_spans() -> None:
    """Preserve PDF page numbers as fallback citations."""

    document = parse_bill_lines(
        [
            TextLine("Clause 1—Objects", 1),
            TextLine("(1) First page text.", 1),
            TextLine("continued on second page.", 2),
        ],
        "Sample Bill",
        "raw.pdf",
    )

    node = document.nodes["cl_1_subcl_1"]
    assert node.page_start == 1
    assert node.page_end == 2


def test_arrangement_lines_before_bill_body_are_skipped() -> None:
    """Skip arrangement of sections before the actual bill body."""

    text = """
    ARRANGEMENT OF SECTIONS
    1. Objects
    A BILL
    1. (1) There is established an Authority.
    """

    document = parse_bill_text(text, "Sample Bill", "raw.pdf")

    assert document.root_node_ids == ["cl_1"]
    assert document.nodes["cl_1_subcl_1"].text == "There is established an Authority."


def test_clause_lines_accept_compact_pdf_numbering() -> None:
    """Parse common PDF extraction forms such as 6.(1) and 8 (1)."""

    text = """
    A BILL
    6.(1) The Board consists of members.
    8 (1) A member has fiduciary duties.
    53(1) The Authority shall maintain an architecture.
    """

    document = parse_bill_text(text, "Sample Bill", "raw.pdf")

    assert document.root_node_ids == ["cl_6", "cl_8", "cl_53"]
    assert document.nodes["cl_6_subcl_1"].text == "The Board consists of members."
    assert document.nodes["cl_8_subcl_1"].text == "A member has fiduciary duties."
    assert document.nodes["cl_53_subcl_1"].text == "The Authority shall maintain an architecture."


def test_preamble_lines_are_recorded_as_issues() -> None:
    """Record ignored preamble lines instead of failing silently."""

    document = parse_bill_text("A BILL\nClause 1—Objects\n(1) Text.", "Sample Bill", "raw.pdf")

    assert document.issues == ["Ignored preamble line: A BILL"]


def test_duplicate_bill_node_ids_are_preserved_with_issue() -> None:
    """Preserve duplicate numbering without overwriting text."""

    text = "Clause 1—Objects\n(1) Text.\n1. Duplicate"

    document = parse_bill_text(text, "Sample Bill", "raw.pdf")

    assert document.root_node_ids == ["cl_1", "cl_1_dup_2"]
    assert "Duplicate bill node id renamed: cl_1 -> cl_1_dup_2" in document.issues


def test_empty_bill_text_fails_loudly() -> None:
    """Reject text with no parsable clauses or schedules."""

    with pytest.raises(BillParseError, match="No clauses or schedules"):
        parse_bill_text("A BILL\nNo clauses here.", "Sample Bill", "raw.pdf")


def test_four_digit_year_does_not_become_clause() -> None:
    """Avoid parsing year references as clause numbers."""

    document = parse_bill_text(
        "A BILL\n1. Text under the Companies Act, 2025 (Act ...).",
        "Sample Bill",
        "raw.pdf",
    )

    assert document.root_node_ids == ["cl_1"]
