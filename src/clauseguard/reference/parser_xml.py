"""Parse Akoma Ntoso XML into ClauseGuard reference models."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Literal

from lxml import etree

from clauseguard.reference._xml_metadata import (
    extract_act_number,
    extract_optional_text,
    extract_title,
    extract_year,
)
from clauseguard.reference._xml_nodes import parse_node, top_level_nodes
from clauseguard.reference.schemas import LegalDocument, TextNode

DocTypeInput = Literal["constitution", "act"]


def parse_xml_file(
    file_path: Path,
    source_url: str,
    doc_type: DocTypeInput,
    fetched_at: datetime | None = None,
) -> LegalDocument:
    """Parse an Akoma Ntoso XML file from disk.

    Args:
        file_path: Path to the XML file.
        source_url: URL where the XML source came from.
        doc_type: Legal document type.
        fetched_at: Optional fetch timestamp.

    Returns:
        Parsed legal document.
    """

    xml_text = file_path.read_text(encoding="utf-8")
    return parse_xml_document(xml_text, source_url, doc_type, fetched_at)


def parse_xml_document(
    xml_text: str,
    source_url: str,
    doc_type: DocTypeInput,
    fetched_at: datetime | None = None,
) -> LegalDocument:
    """Parse Akoma Ntoso XML text into a legal document.

    Args:
        xml_text: Akoma Ntoso XML as text.
        source_url: URL where the XML source came from.
        doc_type: Legal document type.
        fetched_at: Optional fetch timestamp.

    Returns:
        Parsed legal document.
    """

    root = _parse_root(xml_text)
    nodes: dict[str, TextNode] = {}
    root_ids = _parse_root_nodes(root, nodes)
    return _build_document(root, xml_text, source_url, doc_type, nodes, root_ids, fetched_at)


def _build_document(
    root: etree._Element,
    xml_text: str,
    source_url: str,
    doc_type: DocTypeInput,
    nodes: dict[str, TextNode],
    root_ids: list[str],
    fetched_at: datetime | None,
) -> LegalDocument:
    """Build a legal document model from parsed XML parts."""

    fetched_time = fetched_at or datetime.now(timezone.utc)
    return LegalDocument(
        doc_type=doc_type,
        act_number=extract_act_number(root, source_url, doc_type),
        year=extract_year(root, source_url, doc_type),
        title=extract_title(root),
        short_title=extract_optional_text(root, "shortTitle"),
        long_title=extract_optional_text(root, "longTitle"),
        source_url=source_url,
        content_hash=sha256(xml_text.encode("utf-8")).hexdigest(),
        fetched_at=fetched_time,
        nodes=nodes,
        root_node_ids=root_ids,
    )


def _parse_root(xml_text: str) -> etree._Element:
    """Build an XML root element from source text."""

    parser = etree.XMLParser(resolve_entities=False, recover=False)
    return etree.fromstring(xml_text.encode("utf-8"), parser=parser)


def _parse_root_nodes(root: etree._Element, nodes: dict[str, TextNode]) -> list[str]:
    """Parse top-level nodes and return their IDs."""

    root_ids: list[str] = []
    for element in top_level_nodes(root):
        node = parse_node(element, None, [], nodes)
        root_ids.append(node.id)
    return root_ids
