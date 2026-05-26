"""Shared retrieval index models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["bill", "constitution", "act"]


class RetrievalChunk(BaseModel):
    """One searchable text chunk with a scoped citation."""

    chunk_id: str
    source_type: SourceType
    document_id: str
    document_title: str
    node_id: str
    level: str
    text: str
    heading: str | None = None
    page_start: int | None = None
    page_end: int | None = None


class LexicalIndex(BaseModel):
    """A local deterministic lexical search index."""

    index_id: str
    created_at: datetime
    chunks: list[RetrievalChunk]
    postings: dict[str, dict[str, int]] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """One lexical search result."""

    chunk: RetrievalChunk
    score: float
    matched_terms: list[str]


class IndexCheckReport(BaseModel):
    """Result of index smoke checks."""

    index_id: str | None
    chunk_count: int
    issues: list[str]
