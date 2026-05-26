"""Load parsed bill documents."""

from __future__ import annotations

from pathlib import Path

from clauseguard.parsing.metadata import load_bill_metadata
from clauseguard.parsing.schemas import BillDocument


class BillStoreError(ValueError):
    """Raised when a parsed bill cannot be loaded."""


def load_parsed_bill(bill_dir: Path) -> BillDocument:
    """Load parsed bill JSON from a bill folder."""

    metadata = load_bill_metadata(bill_dir)
    path = bill_dir / metadata.parsed_file
    if not path.exists():
        raise BillStoreError(f"Parsed bill file does not exist: {path}")
    return BillDocument.model_validate_json(path.read_text(encoding="utf-8"))
