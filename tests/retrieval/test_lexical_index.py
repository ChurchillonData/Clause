"""Tests for lexical index search."""

from __future__ import annotations

from clauseguard.retrieval.lexical_index import build_lexical_index, search_index
from clauseguard.retrieval.schemas import RetrievalChunk


def chunk(chunk_id: str, text: str, source_type: str = "bill") -> RetrievalChunk:
    """Create a retrieval chunk."""

    return RetrievalChunk(
        chunk_id=chunk_id,
        source_type=source_type,  # type: ignore[arg-type]
        document_id="doc",
        document_title="Document",
        node_id=chunk_id,
        level="clause",
        text=text,
    )


def test_search_index_ranks_matching_chunks() -> None:
    """Return ranked lexical matches."""

    index = build_lexical_index(
        "test",
        [
            chunk("a", "digital services digital regulation"),
            chunk("b", "board appointments"),
        ],
    )

    results = search_index(index, "digital regulation")

    assert results[0].chunk.chunk_id == "a"
    assert results[0].matched_terms == ["digital", "regulation"]


def test_search_index_returns_empty_for_no_terms() -> None:
    """Return no evidence for stopword-only queries."""

    index = build_lexical_index("test", [chunk("a", "digital services")])

    assert search_index(index, "the and of") == []


def test_search_index_filters_by_source_type() -> None:
    """Filter matches to selected source types."""

    index = build_lexical_index(
        "test",
        [chunk("bill", "rights", "bill"), chunk("constitution", "rights", "constitution")],
    )

    results = search_index(index, "rights", source_types={"constitution"})

    assert [item.chunk.source_type for item in results] == ["constitution"]


def test_search_index_boosts_explicit_article_reference() -> None:
    """Rank explicitly referenced article nodes above broad definition matches."""

    index = build_lexical_index(
        "test",
        [
            chunk("art_295_1", "article means a provision of the Constitution", "constitution"),
            chunk("art_19_1", "fair hearing by a court", "constitution"),
        ],
    )

    results = search_index(index, "fair hearing article 19")

    assert results[0].chunk.chunk_id == "art_19_1"
