"""Tests for retrieval tokenisation."""

from __future__ import annotations

from clauseguard.retrieval.tokenizer import tokenize


def test_tokenize_normalises_and_removes_stopwords() -> None:
    """Return useful lexical tokens."""

    assert tokenize("The Authority shall regulate digital services.") == [
        "authority",
        "regulate",
        "digital",
        "services",
    ]
