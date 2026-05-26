"""Tests for retrieval CLI helpers."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from clauseguard.retrieval import check_index_cli, index_cli, search_cli
from clauseguard.retrieval.lexical_index import build_lexical_index
from clauseguard.retrieval.schemas import RetrievalChunk


def test_index_cli_bill_writes_output(monkeypatch, tmp_path: Path) -> None:
    """Run the bill index CLI."""

    index = build_lexical_index("bill:test", [sample_chunk()])
    monkeypatch.setattr(index_cli, "build_bill_index", lambda bill_dir: index)

    result = CliRunner().invoke(index_cli.app, ["bill", str(tmp_path), "--output", str(tmp_path / "i.json")])

    assert result.exit_code == 0
    assert (tmp_path / "i.json").exists()


def test_search_cli_prints_insufficient_evidence(tmp_path: Path) -> None:
    """Return nonzero when search has no matches."""

    path = tmp_path / "i.json"
    path.write_text(build_lexical_index("test", [sample_chunk()]).model_dump_json(), encoding="utf-8")

    result = CliRunner().invoke(search_cli.app, [str(path), "zzzz"])

    assert result.exit_code == 1
    assert "insufficient evidence" in result.output


def test_check_index_cli_reports_success(tmp_path: Path) -> None:
    """Run the index check CLI."""

    path = tmp_path / "i.json"
    path.write_text(build_lexical_index("test", [sample_chunk()]).model_dump_json(), encoding="utf-8")

    result = CliRunner().invoke(check_index_cli.app, [str(path)])

    assert result.exit_code == 0
    assert "Issues: 0" in result.output


def sample_chunk() -> RetrievalChunk:
    """Return a sample retrieval chunk."""

    return RetrievalChunk(
        chunk_id="bill:test:cl_1",
        source_type="bill",
        document_id="test",
        document_title="Test",
        node_id="cl_1",
        level="clause",
        text="Digital services.",
    )
