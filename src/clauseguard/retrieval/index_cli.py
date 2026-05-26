"""Command helpers for building lexical indexes."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.retrieval.builders import (
    build_bill_index,
    build_reference_index,
    default_bill_index_path,
    default_reference_index_path,
)
from clauseguard.retrieval.index_store import write_index

app = typer.Typer(help="Build local lexical indexes.")


@app.command()
def bill(
    bill_dir: Annotated[Path, typer.Argument(help="Bill folder path.")],
    output: Annotated[Path | None, typer.Option(help="Output index path.")] = None,
) -> None:
    """Build an index for one parsed bill."""

    path = output or default_bill_index_path(bill_dir)
    write_index(build_bill_index(bill_dir), path)
    typer.echo(f"Wrote {path}")


@app.command()
def references(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    output: Annotated[Path | None, typer.Option(help="Output index path.")] = None,
) -> None:
    """Build an index for local reference documents."""

    path = output or default_reference_index_path()
    write_index(build_reference_index(repo_root), path)
    typer.echo(f"Wrote {path}")
