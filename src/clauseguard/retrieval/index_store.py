"""Read and write lexical index files."""

from __future__ import annotations

from pathlib import Path

from clauseguard.retrieval.schemas import LexicalIndex


class IndexStoreError(ValueError):
    """Raised when an index cannot be loaded."""


def write_index(index: LexicalIndex, path: Path) -> Path:
    """Write an index as stable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(index.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def load_index(path: Path) -> LexicalIndex:
    """Load a lexical index from JSON."""

    if not path.exists():
        raise IndexStoreError(f"Index file does not exist: {path}")
    return LexicalIndex.model_validate_json(path.read_text(encoding="utf-8"))
