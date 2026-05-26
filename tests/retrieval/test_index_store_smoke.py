"""Tests for index storage and smoke checks."""

from __future__ import annotations

from clauseguard.retrieval.index_store import load_index, write_index
from clauseguard.retrieval.lexical_index import build_lexical_index
from clauseguard.retrieval.schemas import RetrievalChunk
from clauseguard.retrieval.smoke import check_index_file, index_check_passed


def test_write_load_and_check_index(tmp_path) -> None:
    """Write, load, and smoke-check an index."""

    chunk = RetrievalChunk(
        chunk_id="bill:test:cl_1",
        source_type="bill",
        document_id="test",
        document_title="Test",
        node_id="cl_1",
        level="clause",
        text="Digital services.",
    )
    path = tmp_path / "index.json"

    write_index(build_lexical_index("test", [chunk]), path)
    report = check_index_file(path)

    assert load_index(path).index_id == "test"
    assert index_check_passed(report)


def test_check_index_file_reports_missing_file(tmp_path) -> None:
    """Fail clearly when an index is missing."""

    report = check_index_file(tmp_path / "missing.json")

    assert not index_check_passed(report)
    assert "does not exist" in report.issues[0]
