"""Read bill folder metadata."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError
from pydantic import BaseModel


class BillFolderMetadata(BaseModel):
    """Metadata required to parse one bill folder."""

    title: str
    source_file: str = "raw.pdf"
    parsed_file: str = "parsed.json"


class BillMetadataError(ValueError):
    """Raised when bill metadata is missing or invalid."""


def load_bill_metadata(bill_dir: Path) -> BillFolderMetadata:
    """Load bill metadata from a bill folder."""

    path = bill_dir / "metadata.yaml"
    if not path.exists():
        raise BillMetadataError(f"Missing metadata file: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return BillFolderMetadata.model_validate(raw)
    except (OSError, TypeError, ValidationError, yaml.YAMLError) as exc:
        raise BillMetadataError(f"Invalid metadata file: {path}") from exc
