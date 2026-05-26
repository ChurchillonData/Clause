"""Parse GhaLII HTML fallback documents into reference models."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Literal

from bs4 import BeautifulSoup

from clauseguard.reference._html_nodes import parse_section_block, section_blocks
from clauseguard.reference._source_url import act_number_from_url, year_from_url
from clauseguard.reference._xml_common import normalise_space
from clauseguard.reference.schemas import LegalDocument, TextNode

DocTypeInput = Literal["constitution", "act"]


class HtmlParseError(ValueError):
    """Raised when HTML cannot be parsed safely."""


def parse_html_file(
    file_path: Path,
    source_url: str,
    doc_type: DocTypeInput,
    fetched_at: datetime | None = None,
) -> LegalDocument:
    """Parse a GhaLII HTML file from disk.

    Args:
        file_path: Path to the HTML file.
        source_url: URL where the HTML source came from.
        doc_type: Legal document type.
        fetched_at: Optional fetch timestamp.

    Returns:
        Parsed legal document.
    """

    html_text = file_path.read_text(encoding="utf-8")
    return parse_html_document(html_text, source_url, doc_type, fetched_at)


def parse_html_document(
    html_text: str,
    source_url: str,
    doc_type: DocTypeInput,
    fetched_at: datetime | None = None,
) -> LegalDocument:
    """Parse GhaLII HTML text into a legal document.

    Args:
        html_text: HTML source text.
        source_url: URL where the HTML source came from.
        doc_type: Legal document type.
        fetched_at: Optional fetch timestamp.

    Returns:
        Parsed legal document.

    Raises:
        HtmlParseError: If section boundaries cannot be identified.
    """

    soup = BeautifulSoup(html_text, "lxml")
    nodes = _parse_nodes(soup)
    root_ids = list(nodes)
    return _build_document(soup, html_text, source_url, doc_type, nodes, root_ids, fetched_at)


def _parse_nodes(soup: BeautifulSoup) -> dict[str, TextNode]:
    """Parse section nodes from an HTML document."""

    blocks = section_blocks(soup)
    if not blocks:
        raise HtmlParseError("No confident section boundaries found in HTML.")
    nodes: dict[str, TextNode] = {}
    for block in blocks:
        node = parse_section_block(block)
        if node.id in nodes:
            raise HtmlParseError(f"Duplicate section id: {node.id}")
        nodes[node.id] = node
    return nodes


def _build_document(
    soup: BeautifulSoup,
    html_text: str,
    source_url: str,
    doc_type: DocTypeInput,
    nodes: dict[str, TextNode],
    root_ids: list[str],
    fetched_at: datetime | None,
) -> LegalDocument:
    """Build a legal document model from parsed HTML parts."""

    default_year = 1992 if doc_type == "constitution" else 0
    return LegalDocument(
        doc_type=doc_type,
        act_number=None if doc_type == "constitution" else act_number_from_url(source_url),
        year=year_from_url(source_url, default_year),
        title=_title(soup),
        source_url=source_url,
        content_hash=sha256(html_text.encode("utf-8")).hexdigest(),
        fetched_at=fetched_at or datetime.now(timezone.utc),
        nodes=nodes,
        root_node_ids=root_ids,
    )


def _title(soup: BeautifulSoup) -> str:
    """Return the best available HTML document title."""

    heading = soup.find("h1")
    if heading:
        return normalise_space(heading.get_text(" ", strip=True))
    title = soup.find("title")
    if title:
        return normalise_space(title.get_text(" ", strip=True))
    return "Untitled legal document"
