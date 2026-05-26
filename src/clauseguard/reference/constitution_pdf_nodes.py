"""Node parsing helpers for the local Constitution PDF."""

from __future__ import annotations

import re
from re import Match

from clauseguard.reference.schemas import NodeLevel, TextNode

ARTICLE_RE = re.compile(r"^(?P<number>\d+)\.\s*(?P<text>.*)$")
SUBCLAUSE_RE = re.compile(r"^\((?P<number>\d+)\)\s*(?P<text>.*)$")
PARAGRAPH_RE = re.compile(r"^\((?P<number>[a-z])\)\s*(?P<text>.*)$", re.IGNORECASE)


def parse_constitution_nodes(text: str) -> tuple[dict[str, TextNode], list[str]]:
    """Parse Constitution text into nodes and root IDs."""

    nodes: dict[str, TextNode] = {}
    root_ids: list[str] = []
    current_article: str | None = None
    current_subclause: str | None = None
    current_node: str | None = None
    for line in normalised_lines(text):
        current_article, current_subclause, current_node = consume_line(
            nodes, root_ids, current_article, current_subclause, current_node, line
        )
    return nodes, root_ids


def consume_line(
    nodes: dict[str, TextNode],
    root_ids: list[str],
    current_article: str | None,
    current_subclause: str | None,
    current_node: str | None,
    line: str,
) -> tuple[str | None, str | None, str | None]:
    """Consume one Constitution line."""

    if match := ARTICLE_RE.match(line):
        node_id = f"art_{match.group('number')}"
        add_node(nodes, root_ids, node_id, None, "article", match.group("number"), match.group("text"))
        return node_id, None, node_id
    if match := SUBCLAUSE_RE.match(line):
        return consume_subclause(nodes, root_ids, current_article, match)
    if match := PARAGRAPH_RE.match(line):
        return consume_paragraph(nodes, root_ids, current_article, current_subclause, match)
    append_text(nodes, current_node, line)
    return current_article, current_subclause, current_node


def consume_subclause(
    nodes: dict[str, TextNode],
    root_ids: list[str],
    current_article: str | None,
    match: Match[str],
) -> tuple[str | None, str | None, str | None]:
    """Consume one subclause line."""

    if current_article is None:
        return current_article, None, None
    node_id = f"{current_article}_{match.group('number')}"
    add_node(nodes, root_ids, node_id, current_article, "subsection", match.group("number"), match.group("text"))
    return current_article, node_id, node_id


def consume_paragraph(
    nodes: dict[str, TextNode],
    root_ids: list[str],
    current_article: str | None,
    current_subclause: str | None,
    match: Match[str],
) -> tuple[str | None, str | None, str | None]:
    """Consume one paragraph line."""

    if current_subclause is None:
        return current_article, current_subclause, None
    node_id = f"{current_subclause}_{match.group('number').lower()}"
    add_node(nodes, root_ids, node_id, current_subclause, "paragraph", match.group("number"), match.group("text"))
    return current_article, current_subclause, node_id


def add_node(
    nodes: dict[str, TextNode],
    root_ids: list[str],
    node_id: str,
    parent_id: str | None,
    level: NodeLevel,
    number: str,
    text: str,
) -> None:
    """Add one Constitution node."""

    nodes[node_id] = TextNode(id=node_id, parent_id=parent_id, level=level, number=number, text=text)
    if parent_id is None:
        root_ids.append(node_id)
    else:
        nodes[parent_id].children_ids.append(node_id)


def append_text(nodes: dict[str, TextNode], node_id: str | None, text: str) -> None:
    """Append continuation text to a node."""

    if node_id is None or looks_like_noise(text):
        return
    node = nodes[node_id]
    node.text = " ".join(part for part in [node.text, text] if part)


def normalised_lines(text: str) -> list[str]:
    """Return non-empty normalised text lines."""

    return [" ".join(line.split()) for line in text.splitlines() if " ".join(line.split())]


def looks_like_noise(text: str) -> bool:
    """Return whether text is a page header or page number."""

    return text.isdigit() or text in {"The Constitution"}
