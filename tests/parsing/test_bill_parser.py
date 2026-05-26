"""Tests for bill folder parsing workflow."""

from __future__ import annotations

from pathlib import Path

from clauseguard.parsing import bill_parser
from clauseguard.parsing.schemas import ExtractedPage


def write_metadata(bill_dir: Path) -> None:
    """Write minimal bill metadata."""

    bill_dir.mkdir(parents=True, exist_ok=True)
    (bill_dir / "metadata.yaml").write_text(
        'title: "Sample Bill"\nsource_file: "raw.pdf"\nparsed_file: "parsed.json"\n',
        encoding="utf-8",
    )
    (bill_dir / "raw.pdf").write_bytes(b"%PDF")


def test_parse_and_write_bill_folder(monkeypatch, tmp_path: Path) -> None:
    """Parse a bill folder and write parsed JSON."""

    write_metadata(tmp_path)
    monkeypatch.setattr(
        bill_parser,
        "extract_pdf_pages",
        lambda path: [ExtractedPage(page_number=1, text="Clause 1—Objects\n(1) Text.")],
    )

    output_path = bill_parser.parse_and_write_bill_folder(tmp_path)

    assert output_path == tmp_path / "parsed.json"
    assert '"cl_1_subcl_1"' in output_path.read_text(encoding="utf-8")
