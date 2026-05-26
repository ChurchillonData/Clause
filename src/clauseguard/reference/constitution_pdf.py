"""Parse the local Constitution PDF into reference models."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pdfplumber

from clauseguard.reference.citation import node_id_from_ref
from clauseguard.reference.constitution_pdf_nodes import parse_constitution_nodes
from clauseguard.reference.mirror_markdown import write_node_markdown
from clauseguard.reference.mirror_paths import constitution_dir
from clauseguard.reference.mirror_registry import constitution_registry_entry, write_mirror_registry
from clauseguard.reference.schemas import LegalDocument, TextNode


def mirror_constitution_pdf(repo_root: Path = Path(".")) -> LegalDocument:
    """Parse the local Constitution PDF and write mirror outputs."""

    output_dir = constitution_dir(repo_root)
    pdf_path = output_dir / "raw.pdf"
    text = extract_pdf_text(pdf_path)
    document = parse_constitution_text(text, str(pdf_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "parsed.json").write_text(document.model_dump_json(indent=2) + "\n", encoding="utf-8")
    write_node_markdown(document, output_dir / "articles")
    write_mirror_registry([constitution_registry_entry(document, repo_root)], repo_root)
    return document


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a Constitution PDF."""

    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def parse_constitution_text(text: str, source_url: str) -> LegalDocument:
    """Parse Constitution text into article and clause nodes."""

    nodes, root_ids = parse_constitution_nodes(text)
    return build_document(text, source_url, nodes, root_ids)


def build_document(
    text: str,
    source_url: str,
    nodes: dict[str, TextNode],
    root_ids: list[str],
) -> LegalDocument:
    """Build a Constitution legal document."""

    ensure_article_19_alias(nodes)
    return LegalDocument(
        doc_type="constitution",
        act_number=None,
        year=1992,
        title="Constitution of the Republic of Ghana, 1992",
        short_title="Constitution",
        source_url=source_url,
        content_hash=sha256(text.encode("utf-8")).hexdigest(),
        fetched_at=datetime.now(timezone.utc),
        nodes=nodes,
        root_node_ids=root_ids,
    )


def ensure_article_19_alias(nodes: dict[str, TextNode]) -> None:
    """Add normalized aliases for Article 19 nested references when available."""

    source = nodes.get("art_19_2_d")
    if source is not None:
        nodes[node_id_from_ref("art", "19(2)(d)")] = source.model_copy(
            update={"id": node_id_from_ref("art", "19(2)(d)")}
        )

