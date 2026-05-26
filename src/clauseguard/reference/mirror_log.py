"""JSONL logging helpers for mirror runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def log_event(log_path: Path, event: str, **fields: object) -> None:
    """Append one mirror event as JSONL."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), **fields}
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
