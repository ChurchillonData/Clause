"""Regex patterns for bill hierarchy parsing."""

from __future__ import annotations

import re

CLAUSE_RE = re.compile(
    r"^(?P<prefix>Clause\s+)?(?P<number>\d{1,3}[A-Z]?)(?:(?P<sep>[\.\-–—])\s*|\s+|(?=\())(?P<body>.+)$",
    re.IGNORECASE,
)
SUBCLAUSE_RE = re.compile(r"^\((?P<number>\d+[A-Z]?)\)\s*(?P<text>.*)$")
PARAGRAPH_RE = re.compile(r"^\((?P<number>[a-z])\)\s*(?P<text>.*)$")
SUBPARAGRAPH_RE = re.compile(r"^\((?P<number>[ivxlcdm]+)\)\s*(?P<text>.*)$", re.IGNORECASE)
SCHEDULE_RE = re.compile(
    r"^(?:(?P<number>FIRST|SECOND|THIRD|FOURTH|FIFTH|\d+(?:ST|ND|RD|TH)?)\s+)?SCHEDULE\b",
    re.IGNORECASE,
)


def clause_match(text: str) -> re.Match[str] | None:
    """Return a clause heading match."""

    return CLAUSE_RE.match(text)


def subclause_match(text: str) -> re.Match[str] | None:
    """Return a subclause match."""

    return SUBCLAUSE_RE.match(text)


def paragraph_match(text: str) -> re.Match[str] | None:
    """Return a paragraph match."""

    return PARAGRAPH_RE.match(text)


def subparagraph_match(text: str) -> re.Match[str] | None:
    """Return a subparagraph match."""

    return SUBPARAGRAPH_RE.match(text)


def schedule_match(text: str) -> re.Match[str] | None:
    """Return a schedule match."""

    return SCHEDULE_RE.match(text)
