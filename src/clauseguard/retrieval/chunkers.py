"""Convert parsed documents into retrieval chunks."""

from __future__ import annotations

from clauseguard.parsing.schemas import BillDocument, BillNode
from clauseguard.reference.schemas import LegalDocument, TextNode
from clauseguard.retrieval.schemas import RetrievalChunk


def chunks_from_bill(document: BillDocument, document_id: str) -> list[RetrievalChunk]:
    """Build retrieval chunks from a parsed bill."""

    return [
        bill_chunk(document, document_id, node)
        for node in document.nodes.values()
        if node.text.strip()
    ]


def bill_chunk(document: BillDocument, document_id: str, node: BillNode) -> RetrievalChunk:
    """Build one retrieval chunk from a bill node."""

    return RetrievalChunk(
        chunk_id=f"bill:{document_id}:{node.id}",
        source_type="bill",
        document_id=document_id,
        document_title=document.title,
        node_id=node.id,
        level=node.level,
        heading=node.heading,
        text=node.text,
        page_start=node.page_start,
        page_end=node.page_end,
    )


def chunks_from_legal_document(document: LegalDocument, document_id: str) -> list[RetrievalChunk]:
    """Build retrieval chunks from a parsed legal reference document."""

    return [
        legal_chunk(document, document_id, node)
        for node in document.nodes.values()
        if node.text.strip()
    ]


def legal_chunk(document: LegalDocument, document_id: str, node: TextNode) -> RetrievalChunk:
    """Build one retrieval chunk from a reference document node."""

    return RetrievalChunk(
        chunk_id=f"{document.doc_type}:{document_id}:{node.id}",
        source_type=document.doc_type,
        document_id=document_id,
        document_title=document.title,
        node_id=node.id,
        level=node.level,
        heading=node.heading,
        text=node.text,
    )
