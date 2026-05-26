"""Tests for reference smoke CLI helpers."""

from __future__ import annotations

from typer.testing import CliRunner

from clauseguard.reference import smoke_cli
from clauseguard.reference.schemas import ResolutionReport
from clauseguard.reference.smoke import ReferenceSmokeReport


def test_smoke_cli_exits_zero_when_report_passes(monkeypatch) -> None:
    """Return success for a clean smoke report."""

    report = ReferenceSmokeReport(
        registry_entries=1,
        parsed_documents=1,
        sample_references=[],
        resolution_report=ResolutionReport(),
        issues=[],
    )
    monkeypatch.setattr(smoke_cli, "run_reference_smoke", lambda *args: report)

    result = CliRunner().invoke(smoke_cli.app)

    assert result.exit_code == 0
    assert "Issues: 0" in result.output


def test_smoke_cli_exits_one_when_report_fails(monkeypatch) -> None:
    """Return failure for a smoke report with issues."""

    report = ReferenceSmokeReport(
        registry_entries=0,
        parsed_documents=0,
        sample_references=[],
        resolution_report=ResolutionReport(),
        issues=["Registry has no entries."],
    )
    monkeypatch.setattr(smoke_cli, "run_reference_smoke", lambda *args: report)

    result = CliRunner().invoke(smoke_cli.app)

    assert result.exit_code == 1
    assert "- Registry has no entries." in result.output
