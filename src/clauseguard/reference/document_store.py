"""Load parsed legal documents from local JSON files."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.registry import normalise_path
from clauseguard.reference.schemas import LegalDocument, RegistryEntry


class DocumentStoreError(ValueError):
    """Raised when a parsed legal document cannot be loaded."""


def load_document(entry: RegistryEntry, repo_root: Path = Path(".")) -> LegalDocument:
    """Load one parsed legal document for a registry entry."""

    path = document_path(entry, repo_root)
    if not path.exists():
        raise DocumentStoreError(f"Parsed document does not exist: {path}")
    return LegalDocument.model_validate_json(path.read_text(encoding="utf-8"))


def document_path(entry: RegistryEntry, repo_root: Path = Path(".")) -> Path:
    """Return the parsed document path for a registry entry."""

    file_path = Path(normalise_path(entry.file_path))
    return file_path if file_path.is_absolute() else repo_root / file_path
