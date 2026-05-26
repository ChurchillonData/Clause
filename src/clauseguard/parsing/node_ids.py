"""Build stable IDs for parsed bill nodes."""

from __future__ import annotations

import re


def clause_id(number: str) -> str:
    """Return a clause ID."""

    return f"cl_{normalise_part(number)}"


def child_id(parent_id: str, prefix: str, number: str) -> str:
    """Return a child node ID."""

    return f"{parent_id}_{prefix}_{normalise_part(number)}"


def schedule_id(number: str) -> str:
    """Return a schedule ID."""

    return f"sch_{normalise_part(number)}"


def normalise_part(value: str) -> str:
    """Normalise a bill node number for IDs."""

    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return cleaned.strip("_") or "unnumbered"
