"""Parser state helpers for bill clause splitting."""

from __future__ import annotations

from re import Match

from clauseguard.parsing.references import extract_references
from clauseguard.parsing.schemas import BillNode, BillNodeLevel


class BillParseError(ValueError):
    """Raised when bill text cannot be parsed safely."""


class ParseState:
    """Mutable state for deterministic bill parsing."""

    def __init__(self) -> None:
        """Create empty parser state."""

        self.nodes: dict[str, BillNode] = {}
        self.root_ids: list[str] = []
        self.current_clause: str | None = None
        self.current_subclause: str | None = None
        self.current_paragraph: str | None = None
        self.current_node: str | None = None
        self.issues: list[str] = []


def add_child(
    state: ParseState,
    node_id: str,
    parent_id: str,
    level: BillNodeLevel,
    match: Match[str],
    page: int | None,
) -> str:
    """Add a matched child node to parser state."""

    actual_id = add_node(state, node_id, parent_id, level, match.group("number"), match.group("text"), None, page)
    state.nodes[parent_id].children_ids.append(actual_id)
    return actual_id


def add_node(
    state: ParseState,
    node_id: str,
    parent_id: str | None,
    level: BillNodeLevel,
    number: str,
    text: str,
    heading: str | None,
    page: int | None,
) -> str:
    """Add one node and return its final ID."""

    if node_id in state.nodes:
        node_id = next_duplicate_id(state, node_id)
    state.nodes[node_id] = BillNode(
        id=node_id,
        parent_id=parent_id,
        level=level,
        number=number,
        heading=heading,
        text=text,
        page_start=page,
        page_end=page,
        references=extract_references(text),
    )
    if parent_id is None:
        state.root_ids.append(node_id)
    state.current_node = node_id
    return node_id


def next_duplicate_id(state: ParseState, node_id: str) -> str:
    """Return a deterministic duplicate ID and record an issue."""

    index = 2
    candidate = f"{node_id}_dup_{index}"
    while candidate in state.nodes:
        index += 1
        candidate = f"{node_id}_dup_{index}"
    state.issues.append(f"Duplicate bill node id renamed: {node_id} -> {candidate}")
    return candidate


def append_continuation(state: ParseState, text: str, page: int | None) -> None:
    """Append text to the current node."""

    if state.current_node is None:
        state.issues.append(f"Ignored preamble line: {text}")
        return
    node = state.nodes[state.current_node]
    node.text = " ".join(part for part in [node.text, text] if part)
    node.page_end = page or node.page_end
    node.references = extract_references(node.text)


def reset_clause_context(state: ParseState, node_id: str) -> None:
    """Reset nested context after a new clause."""

    state.current_clause = node_id
    state.current_subclause = None
    state.current_paragraph = None
    state.current_node = node_id


def reset_nested_context(state: ParseState, node_id: str) -> None:
    """Reset all clause context after a schedule."""

    state.current_clause = None
    state.current_subclause = None
    state.current_paragraph = None
    state.current_node = node_id


def validate_state(state: ParseState) -> None:
    """Validate parser output before returning it."""

    if not state.nodes:
        raise BillParseError("No clauses or schedules found in bill text.")
    if not any(node.level == "clause" for node in state.nodes.values()):
        state.issues.append("No clause nodes found.")
