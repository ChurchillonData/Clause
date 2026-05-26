"""Split extracted bill text into clause hierarchy."""

from __future__ import annotations

from datetime import datetime, timezone

from clauseguard.parsing.bill_body import bill_body_lines, clause_heading
from clauseguard.parsing.lines import TextLine, lines_from_text
from clauseguard.parsing.node_ids import child_id, clause_id, schedule_id
from clauseguard.parsing.parser_state import (
    ParseState,
    add_child,
    add_node,
    append_continuation,
    reset_clause_context,
    reset_nested_context,
    validate_state,
)
from clauseguard.parsing.patterns import (
    clause_match,
    paragraph_match,
    schedule_match,
    subclause_match,
    subparagraph_match,
)
from clauseguard.parsing.schemas import BillDocument

PARSER_VERSION = "bill-parser-v1"


def parse_bill_text(text: str, title: str, source_file: str) -> BillDocument:
    """Parse plain bill text into a bill document."""

    return parse_bill_lines(lines_from_text(text), title, source_file)


def parse_bill_lines(lines: list[TextLine], title: str, source_file: str) -> BillDocument:
    """Parse page-aware bill lines into a bill document."""

    state = ParseState()
    for line in bill_body_lines(lines):
        consume_line(state, line)
    validate_state(state)
    return BillDocument(
        title=title,
        source_file=source_file,
        parsed_at=datetime.now(timezone.utc),
        parser_version=PARSER_VERSION,
        nodes=state.nodes,
        root_node_ids=state.root_ids,
        issues=state.issues,
    )


def consume_line(state: ParseState, line: TextLine) -> None:
    """Consume one normalised bill line."""

    if try_schedule(state, line):
        return
    if try_clause(state, line):
        return
    if try_subclause(state, line):
        return
    if try_subparagraph(state, line):
        return
    if try_paragraph(state, line):
        return
    append_continuation(state, line.text, line.page_number)


def try_schedule(state: ParseState, line: TextLine) -> bool:
    """Parse a schedule heading when present."""

    match = schedule_match(line.text)
    if match is None:
        return False
    number = match.group("number") or str(len([i for i in state.root_ids if i.startswith("sch_")]) + 1)
    node_id = schedule_id(number)
    add_node(state, node_id, None, "schedule", number, line.text, None, line.page_number)
    reset_nested_context(state, node_id)
    return True


def try_clause(state: ParseState, line: TextLine) -> bool:
    """Parse a clause heading when present."""

    match = clause_match(line.text)
    if match is None:
        return False
    number = match.group("number")
    body = match.group("body")
    heading = clause_heading(match.group("prefix"), match.group("sep"), body)
    node_id = add_node(state, clause_id(number), None, "clause", number, "", heading, line.page_number)
    reset_clause_context(state, node_id)
    if body.startswith("("):
        consume_line(state, TextLine(body, line.page_number))
    elif body and heading is None:
        append_continuation(state, body, line.page_number)
    return True


def try_subclause(state: ParseState, line: TextLine) -> bool:
    """Parse a subclause when present."""

    match = subclause_match(line.text)
    if match is None or state.current_clause is None:
        return False
    node_id = child_id(state.current_clause, "subcl", match.group("number"))
    node_id = add_child(state, node_id, state.current_clause, "subclause", match, line.page_number)
    state.current_subclause = node_id
    state.current_paragraph = None
    state.current_node = node_id
    return True


def try_paragraph(state: ParseState, line: TextLine) -> bool:
    """Parse a paragraph when present."""

    match = paragraph_match(line.text)
    if match is None or state.current_subclause is None:
        return False
    node_id = child_id(state.current_subclause, "para", match.group("number"))
    node_id = add_child(state, node_id, state.current_subclause, "paragraph", match, line.page_number)
    state.current_paragraph = node_id
    state.current_node = node_id
    return True


def try_subparagraph(state: ParseState, line: TextLine) -> bool:
    """Parse a subparagraph when present."""

    match = subparagraph_match(line.text)
    if match is None or state.current_paragraph is None:
        return False
    node_id = child_id(state.current_paragraph, "subpara", match.group("number"))
    node_id = add_child(state, node_id, state.current_paragraph, "subparagraph", match, line.page_number)
    state.current_node = node_id
    return True

