"""Node extraction for Akoma Ntoso documents."""

from __future__ import annotations

from lxml import etree

from clauseguard.reference._xml_common import (
    clean_number,
    direct_child_text,
    direct_children,
    local_name,
    normalise_id,
    normalise_space,
)
from clauseguard.reference.schemas import NodeLevel, TextNode, TextReference

NODE_LEVELS: dict[str, NodeLevel] = {
    "article": "article",
    "section": "section",
    "subsection": "subsection",
    "paragraph": "paragraph",
    "subparagraph": "subparagraph",
}


def top_level_nodes(root: etree._Element) -> list[etree._Element]:
    """Return article or section elements that are not nested in another node."""

    candidates = descendants_by_names(root, {"article", "section"})
    return [node for node in candidates if parent_node_level(node) is None]


def parse_node(
    element: etree._Element,
    parent_id: str | None,
    parent_numbers: list[str],
    nodes: dict[str, TextNode],
) -> TextNode:
    """Parse one XML node and add it to the node map."""

    level = NODE_LEVELS[local_name(element)]
    number = node_number(element)
    node_id = node_id_for(element, level, parent_numbers, number)
    child_numbers = [*parent_numbers, number]
    node = build_text_node(element, node_id, parent_id, level, number)
    if node.id in nodes:
        raise ValueError(f"Duplicate XML node id: {node.id}")
    nodes[node.id] = node

    for child in direct_legal_children(element):
        child_node = parse_node(child, node.id, child_numbers, nodes)
        node.children_ids.append(child_node.id)
    return node


def build_text_node(
    element: etree._Element,
    node_id: str,
    parent_id: str | None,
    level: NodeLevel,
    number: str,
) -> TextNode:
    """Build a text node from one XML element."""

    return TextNode(
        id=node_id,
        parent_id=parent_id,
        level=level,
        number=number,
        heading=direct_child_text(element, "heading"),
        text=content_text(element),
        references=references(element),
    )


def node_id_for(
    element: etree._Element,
    level: str,
    parent_numbers: list[str],
    number: str,
) -> str:
    """Return a stable node id from eId or hierarchy."""

    eid = element.get("eId")
    if eid:
        return normalise_id(eid)
    prefix = "art" if level == "article" else "s"
    return normalise_id("_".join([prefix, *parent_numbers, number]))


def node_number(element: etree._Element) -> str:
    """Return the displayed number for an XML node."""

    num = direct_child_text(element, "num")
    if num:
        return clean_number(num)
    eid = element.get("eId")
    if eid:
        return str(eid).split("_")[-1]
    return "unnumbered"


def direct_legal_children(element: etree._Element) -> list[etree._Element]:
    """Return direct child nodes that should become text nodes."""

    return [child for child in element if local_name(child) in NODE_LEVELS]


def content_text(element: etree._Element) -> str:
    """Return normalised text from direct content paragraphs."""

    parts: list[str] = []
    for content in direct_children(element, "content"):
        for paragraph in direct_children(content, "p"):
            parts.append(normalise_space(" ".join(paragraph.itertext())))
    return normalise_space(" ".join(part for part in parts if part))


def references(element: etree._Element) -> list[TextReference]:
    """Return cross-references found inside direct content."""

    refs: list[TextReference] = []
    for content in direct_children(element, "content"):
        for ref in content.xpath(".//*[local-name()='ref']"):
            href = ref.get("href")
            text = normalise_space(" ".join(ref.itertext()))
            if href and text:
                refs.append(TextReference(text=text, href=href))
    return refs


def parent_node_level(element: etree._Element) -> str | None:
    """Return the nearest parent legal node level."""

    parent = element.getparent()
    while parent is not None:
        name = local_name(parent)
        if name in NODE_LEVELS:
            return name
        parent = parent.getparent()
    return None


def descendants_by_names(root: etree._Element, names: set[str]) -> list[etree._Element]:
    """Return descendants whose local names are in the provided set."""

    return [node for node in root.iter() if local_name(node) in names]
