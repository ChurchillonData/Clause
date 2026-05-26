"""Command helpers for mirroring the local Constitution PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.reference.constitution_pdf import mirror_constitution_pdf

app = typer.Typer(help="Mirror the local Constitution PDF.")


@app.command()
def main(repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path(".")) -> None:
    """Parse and mirror the local Constitution PDF."""

    document = mirror_constitution_pdf(repo_root)
    typer.echo(f"Mirrored {document.title} with {len(document.nodes)} nodes")
