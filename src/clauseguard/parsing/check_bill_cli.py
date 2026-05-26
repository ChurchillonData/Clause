"""Command helpers for parsed bill smoke checks."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.parsing.bill_smoke import bill_smoke_passed, run_bill_smoke

app = typer.Typer(help="Check a parsed bill folder.")


@app.command()
def main(bill_dir: Annotated[Path, typer.Argument(help="Bill folder path.")]) -> None:
    """Run parsed bill smoke checks."""

    report = run_bill_smoke(bill_dir)
    typer.echo(f"Title: {report.title or 'unknown'}")
    typer.echo(f"Nodes: {report.node_count}")
    typer.echo(f"Clauses: {report.clause_count}")
    typer.echo(f"Issues: {len(report.issues)}")
    typer.echo(f"Warnings: {len(report.warnings)}")
    for issue in report.issues:
        typer.echo(f"- {issue}")
    for warning in report.warnings:
        typer.echo(f"! {warning}")
    if not bill_smoke_passed(report):
        raise typer.Exit(code=1)
