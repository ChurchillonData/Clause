"""Command helpers for parsing bill folders."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.parsing.bill_parser import parse_and_write_bill_folder

app = typer.Typer(help="Parse a bill folder into clause-level JSON.")


@app.command()
def main(bill_dir: Annotated[Path, typer.Argument(help="Bill folder path.")]) -> None:
    """Parse a bill folder."""

    output_path = parse_and_write_bill_folder(bill_dir)
    typer.echo(f"Wrote {output_path}")
