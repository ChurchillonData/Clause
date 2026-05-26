"""Build and search a deterministic lexical index."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from math import log

from clauseguard.retrieval.schemas import LexicalIndex, RetrievalChunk, SearchResult, SourceType
from clauseguard.retrieval.tokenizer import tokenize


def build_lexical_index(index_id: str, chunks: list[RetrievalChunk]) -> LexicalIndex:
    """Build a lexical index from retrieval chunks."""

    postings: dict[str, dict[str, int]] = {}
    for chunk in chunks:
        for term, count in Counter(tokenize(chunk_text(chunk))).items():
            postings.setdefault(term, {})[chunk.chunk_id] = count
    return LexicalIndex(
        index_id=index_id,
        created_at=datetime.now(timezone.utc),
        chunks=chunks,
        postings=postings,
    )


def search_index(
    index: LexicalIndex,
    query: str,
    limit: int = 10,
    source_types: set[SourceType] | None = None,
) -> list[SearchResult]:
    """Search an index and return ranked lexical matches."""

    query_terms = tokenize(query)
    if not query_terms:
        return []
    scores: dict[str, float] = {}
    matches: dict[str, set[str]] = {}
    for term in query_terms:
        add_term_scores(index, term, scores, matches)
    chunks = {chunk.chunk_id: chunk for chunk in index.chunks}
    results = [build_result(chunks[key], score, matches[key]) for key, score in scores.items()]
    filtered = [item for item in results if source_types is None or item.chunk.source_type in source_types]
    return sorted(filtered, key=lambda item: (-item.score, item.chunk.chunk_id))[:limit]


def add_term_scores(
    index: LexicalIndex,
    term: str,
    scores: dict[str, float],
    matches: dict[str, set[str]],
) -> None:
    """Add scores for one query term."""

    posting = index.postings.get(term, {})
    if not posting:
        return
    weight = inverse_document_frequency(len(index.chunks), len(posting))
    for chunk_id, count in posting.items():
        scores[chunk_id] = scores.get(chunk_id, 0.0) + count * weight
        matches.setdefault(chunk_id, set()).add(term)


def build_result(chunk: RetrievalChunk, score: float, matched_terms: set[str]) -> SearchResult:
    """Build one search result."""

    return SearchResult(chunk=chunk, score=round(score, 4), matched_terms=sorted(matched_terms))


def inverse_document_frequency(total_chunks: int, matching_chunks: int) -> float:
    """Return a smoothed inverse document frequency."""

    return log((1 + total_chunks) / (1 + matching_chunks)) + 1


def chunk_text(chunk: RetrievalChunk) -> str:
    """Return searchable text for one chunk."""

    return " ".join(part for part in [chunk.heading, chunk.text] if part)
