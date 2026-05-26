"""Command helpers for lexical index smoke checks."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.retrieval.smoke import check_index_file, index_check_passed

app = typer.Typer(help="Check a local lexical index.")


@app.command()
def main(index_path: Annotated[Path, typer.Argument(help="Index JSON path.")]) -> None:
    """Run lexical index smoke checks."""

    report = check_index_file(index_path)
    typer.echo(f"Index: {report.index_id or 'unknown'}")
    typer.echo(f"Chunks: {report.chunk_count}")
    typer.echo(f"Issues: {len(report.issues)}")
    for issue in report.issues:
        typer.echo(f"- {issue}")
    if not index_check_passed(report):
        raise typer.Exit(code=1)
