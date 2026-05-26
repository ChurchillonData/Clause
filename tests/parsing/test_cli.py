"""Tests for bill parsing CLI helpers."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from clauseguard.parsing import check_bill_cli, parse_bill_cli
from clauseguard.parsing.bill_smoke import BillSmokeReport


def test_parse_bill_cli_prints_output(monkeypatch, tmp_path: Path) -> None:
    """Run the parse bill CLI."""

    monkeypatch.setattr(parse_bill_cli, "parse_and_write_bill_folder", lambda path: tmp_path / "parsed.json")

    result = CliRunner().invoke(parse_bill_cli.app, [str(tmp_path)])

    assert result.exit_code == 0
    assert "parsed.json" in result.output


def test_check_bill_cli_exits_one_for_issues(monkeypatch, tmp_path: Path) -> None:
    """Run the check bill CLI."""

    report = BillSmokeReport(title="Sample Bill", node_count=0, clause_count=0, issues=["bad"])
    monkeypatch.setattr(check_bill_cli, "run_bill_smoke", lambda path: report)

    result = CliRunner().invoke(check_bill_cli.app, [str(tmp_path)])

    assert result.exit_code == 1
    assert "- bad" in result.output
