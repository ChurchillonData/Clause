"""Command helpers for refreshing the GhaLII mirror."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.reference.ghalii_client import GhaliiClient
from clauseguard.reference.mirror import default_log_path
from clauseguard.reference.mirror_cli import mirror_all

app = typer.Typer(help="Refresh the local GhaLII mirror.")


@app.command()
def main(repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path(".")) -> None:
    """Refresh the local mirror."""

    client = GhaliiClient()
    mirror_all(client, repo_root, default_log_path(repo_root), dry_run=False)
