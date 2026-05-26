"""Smoke checks for lexical indexes."""

from __future__ import annotations

from pathlib import Path

from clauseguard.retrieval.index_store import load_index
from clauseguard.retrieval.schemas import IndexCheckReport, LexicalIndex


def check_index_file(path: Path) -> IndexCheckReport:
    """Check a lexical index file."""

    try:
        return check_index(load_index(path))
    except ValueError as exc:
        return IndexCheckReport(index_id=None, chunk_count=0, issues=[str(exc)])


def check_index(index: LexicalIndex) -> IndexCheckReport:
    """Check a loaded lexical index."""

    issues = index_issues(index)
    return IndexCheckReport(index_id=index.index_id, chunk_count=len(index.chunks), issues=issues)


def index_issues(index: LexicalIndex) -> list[str]:
    """Return index smoke check issues."""

    issues: list[str] = []
    if not index.chunks:
        issues.append("Index has no chunks.")
    if not index.postings:
        issues.append("Index has no postings.")
    issues.extend(duplicate_chunk_issues(index))
    return issues


def duplicate_chunk_issues(index: LexicalIndex) -> list[str]:
    """Return duplicate chunk ID issues."""

    seen: set[str] = set()
    issues: list[str] = []
    for chunk in index.chunks:
        if chunk.chunk_id in seen:
            issues.append(f"Duplicate chunk id: {chunk.chunk_id}")
        seen.add(chunk.chunk_id)
    return issues


def index_check_passed(report: IndexCheckReport) -> bool:
    """Return whether an index check passed."""

    return not report.issues
