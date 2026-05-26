"""Stable document IDs for retrieval indexes."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.schemas import LegalDocument


def bill_id_from_dir(bill_dir: Path) -> str:
    """Return a stable bill document ID from a bill folder."""

    year = bill_dir.parent.name
    return f"{bill_dir.name}_{year}"


def legal_document_id(document: LegalDocument) -> str:
    """Return a stable reference document ID."""

    if document.doc_type == "constitution":
        return "constitution_1992"
    number = f"{document.act_number:04d}" if document.act_number is not None else "unknown"
    return f"act_{number}_{document.year}"
