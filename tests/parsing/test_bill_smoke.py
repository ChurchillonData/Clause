"""Tests for parsed bill smoke checks."""

from __future__ import annotations

from pathlib import Path

from clauseguard.parsing.bill_smoke import bill_smoke_passed, run_bill_smoke
from clauseguard.parsing.clause_splitter import parse_bill_text


def write_metadata(bill_dir: Path) -> None:
    """Write minimal bill metadata."""

    bill_dir.mkdir(parents=True, exist_ok=True)
    (bill_dir / "metadata.yaml").write_text(
        'title: "Sample Bill"\nsource_file: "raw.pdf"\nparsed_file: "parsed.json"\n',
        encoding="utf-8",
    )


def test_bill_smoke_passes_for_parsed_bill(tmp_path: Path) -> None:
    """Pass when parsed bill hierarchy is usable."""

    write_metadata(tmp_path)
    document = parse_bill_text("Clause 1—Objects\n(1) Text.", "Sample Bill", "raw.pdf")
    (tmp_path / "parsed.json").write_text(document.model_dump_json(indent=2), encoding="utf-8")

    report = run_bill_smoke(tmp_path)

    assert bill_smoke_passed(report)
    assert report.clause_count == 1
    assert report.warnings == []


def test_bill_smoke_reports_missing_parsed_file(tmp_path: Path) -> None:
    """Fail clearly when parsed JSON is missing."""

    write_metadata(tmp_path)

    report = run_bill_smoke(tmp_path)

    assert not bill_smoke_passed(report)
    assert "Parsed bill file does not exist" in report.issues[0]
