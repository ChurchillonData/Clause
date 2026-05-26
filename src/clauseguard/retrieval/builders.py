"""Build lexical indexes from parsed local corpora."""

from __future__ import annotations

from pathlib import Path

from clauseguard.parsing.bill_store import load_parsed_bill
from clauseguard.reference.document_store import load_document
from clauseguard.reference.registry import DEFAULT_REGISTRY_PATH, load_registry
from clauseguard.retrieval.chunkers import chunks_from_bill, chunks_from_legal_document
from clauseguard.retrieval.ids import bill_id_from_dir, legal_document_id
from clauseguard.retrieval.lexical_index import build_lexical_index
from clauseguard.retrieval.schemas import LexicalIndex, RetrievalChunk

DEFAULT_INDEX_ROOT = Path("data/indexes")


def build_bill_index(bill_dir: Path) -> LexicalIndex:
    """Build a lexical index for one parsed bill folder."""

    document = load_parsed_bill(bill_dir)
    document_id = bill_id_from_dir(bill_dir)
    chunks = chunks_from_bill(document, document_id)
    return build_lexical_index(f"bill:{document_id}", chunks)


def build_reference_index(
    repo_root: Path = Path("."),
    registry_path: Path = DEFAULT_REGISTRY_PATH,
) -> LexicalIndex:
    """Build a lexical index for mirrored reference documents."""

    entries = load_registry(repo_path(repo_root, registry_path))
    chunks: list[RetrievalChunk] = []
    for entry in entries:
        document = load_document(entry, repo_root)
        chunks.extend(chunks_from_legal_document(document, legal_document_id(document)))
    return build_lexical_index("reference:local", chunks)


def default_bill_index_path(bill_dir: Path, index_root: Path = DEFAULT_INDEX_ROOT) -> Path:
    """Return the default bill index path."""

    return index_root / "bills" / f"{bill_id_from_dir(bill_dir)}.json"


def default_reference_index_path(index_root: Path = DEFAULT_INDEX_ROOT) -> Path:
    """Return the default reference index path."""

    return index_root / "references" / "ghana_reference.json"


def repo_path(repo_root: Path, path: Path) -> Path:
    """Return an absolute or repo-relative path."""

    return path if path.is_absolute() else repo_root / path
