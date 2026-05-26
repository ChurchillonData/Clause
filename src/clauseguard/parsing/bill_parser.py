"""Parse bill folders into clause-level JSON."""

from __future__ import annotations

from pathlib import Path

from clauseguard.parsing.clause_splitter import parse_bill_lines
from clauseguard.parsing.lines import lines_from_pages
from clauseguard.parsing.metadata import load_bill_metadata
from clauseguard.parsing.pdf_extractor import extract_pdf_pages
from clauseguard.parsing.schemas import BillDocument


def parse_bill_folder(bill_dir: Path) -> BillDocument:
    """Parse one bill folder using its metadata and raw PDF."""

    metadata = load_bill_metadata(bill_dir)
    pdf_path = bill_dir / metadata.source_file
    pages = extract_pdf_pages(pdf_path)
    return parse_bill_lines(lines_from_pages(pages), metadata.title, metadata.source_file)


def write_parsed_bill(bill_dir: Path, document: BillDocument) -> Path:
    """Write a parsed bill document to its configured JSON path."""

    metadata = load_bill_metadata(bill_dir)
    output_path = bill_dir / metadata.parsed_file
    output_path.write_text(document.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return output_path


def parse_and_write_bill_folder(bill_dir: Path) -> Path:
    """Parse a bill folder and write the parsed JSON."""

    document = parse_bill_folder(bill_dir)
    return write_parsed_bill(bill_dir, document)
