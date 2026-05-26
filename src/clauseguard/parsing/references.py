"""Extract legal reference strings from bill text."""

from __future__ import annotations

import re

from clauseguard.parsing.schemas import BillReference

REFERENCE_PATTERNS = [
    re.compile(r"\bArticle\s+\d+(?:\([^)]+\))*", re.IGNORECASE),
    re.compile(r"\bsection\s+\d+(?:\([^)]+\))*\s+of\s+Act\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bAct\s+\d+\b", re.IGNORECASE),
]


def extract_references(text: str) -> list[BillReference]:
    """Return legal references found in text."""

    seen: set[str] = set()
    references: list[BillReference] = []
    for match in reference_matches(text):
        value = " ".join(match.split())
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            references.append(BillReference(text=value))
    return references


def reference_matches(text: str) -> list[str]:
    """Return raw regex matches for known legal references."""

    matches: list[str] = []
    for pattern in REFERENCE_PATTERNS:
        matches.extend(match.group(0) for match in pattern.finditer(text))
    return sorted(matches, key=lambda value: text.casefold().find(value.casefold()))
