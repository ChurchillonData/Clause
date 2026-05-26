"""Command helpers for reference mirror smoke checks."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.reference.registry import DEFAULT_REGISTRY_PATH
from clauseguard.reference.resolver import DEFAULT_ALIASES_PATH
from clauseguard.reference.smoke import run_reference_smoke, smoke_passed

app = typer.Typer(help="Check the local reference mirror and resolver.")


@app.command()
def main(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    registry_path: Annotated[Path, typer.Option(help="Registry JSON path.")] = DEFAULT_REGISTRY_PATH,
    aliases_path: Annotated[Path, typer.Option(help="Aliases YAML path.")] = DEFAULT_ALIASES_PATH,
) -> None:
    """Run local reference mirror smoke checks."""

    report = run_reference_smoke(repo_root, registry_path, aliases_path)
    print_report(report.registry_entries, report.parsed_documents, len(report.issues))
    for issue in report.issues:
        typer.echo(f"- {issue}")
    if not smoke_passed(report):
        raise typer.Exit(code=1)


def print_report(registry_entries: int, parsed_documents: int, issue_count: int) -> None:
    """Print a compact smoke check summary."""

    typer.echo(f"Registry entries: {registry_entries}")
    typer.echo(f"Parsed documents: {parsed_documents}")
    typer.echo(f"Issues: {issue_count}")
