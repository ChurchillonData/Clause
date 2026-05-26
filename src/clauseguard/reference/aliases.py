"""Load common legal citation aliases."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_aliases(path: Path) -> dict[str, int]:
    """Load aliases as a casefolded alias to Act number map."""

    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    rows = raw.get("aliases", raw) if isinstance(raw, dict) else raw
    return _rows_to_aliases(rows)


def _rows_to_aliases(rows: object) -> dict[str, int]:
    """Convert YAML rows to a lookup map."""

    aliases: dict[str, int] = {}
    if not isinstance(rows, list):
        return aliases
    for row in rows:
        if isinstance(row, dict):
            aliases.update(_row_aliases(row))
    return aliases


def _row_aliases(row: dict[object, object]) -> dict[str, int]:
    """Convert one alias row to lookup entries."""

    act_number = row.get("act_number")
    values = row.get("aliases", [])
    if not isinstance(act_number, int) or not isinstance(values, list):
        return {}
    return {str(value).casefold(): act_number for value in values}
