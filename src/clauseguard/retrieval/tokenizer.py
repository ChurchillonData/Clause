"""Text normalisation for deterministic lexical retrieval."""

from __future__ import annotations

import re

STOPWORDS = {
    "a",
    "an",
    "and",
    "by",
    "for",
    "in",
    "is",
    "of",
    "or",
    "shall",
    "the",
    "to",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Return normalised index tokens."""

    return [token for token in raw_tokens(text) if token not in STOPWORDS]


def raw_tokens(text: str) -> list[str]:
    """Return lower-case alphanumeric tokens."""

    return TOKEN_RE.findall(text.casefold())
