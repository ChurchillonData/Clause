"""Write human-readable markdown from parsed legal documents."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.schemas import LegalDocument, TextNode


def write_node_markdown(document: LegalDocument, output_dir: Path) -> None:
    """Write article or section markdown files for a document."""

    output_dir.mkdir(parents=True, exist_ok=True)
    for node_id in document.root_node_ids:
        node = document.nodes[node_id]
        if node.level in {"article", "section"}:
            write_one_node(document, node, output_dir)


def write_one_node(document: LegalDocument, node: TextNode, output_dir: Path) -> None:
    """Write one top-level article or section file."""

    path = output_dir / f"{node.id}.md"
    path.write_text(markdown_for_node(document, node), encoding="utf-8")


def markdown_for_node(document: LegalDocument, node: TextNode) -> str:
    """Return markdown text for one node and its children."""

    lines = [heading_line(node), ""]
    lines.extend(body_lines(document, node))
    return "\n".join(lines).rstrip() + "\n"


def heading_line(node: TextNode) -> str:
    """Return a markdown heading for a legal text node."""

    label = "Article" if node.level == "article" else "Section"
    heading = f". {node.heading}" if node.heading else ""
    return f"# {label} {node.number}{heading}"


def body_lines(document: LegalDocument, node: TextNode, indent: int = 0) -> list[str]:
    """Return markdown body lines for a node tree."""

    lines: list[str] = []
    if node.text:
        lines.append(f"{'  ' * indent}{node.text}")
    for child_id in node.children_ids:
        child = document.nodes[child_id]
        lines.extend(body_lines(document, child, indent + 1))
    return lines
