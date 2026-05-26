"""Command helpers for the GhaLII mirror CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, cast

import typer

from clauseguard.reference.ghalii_client import GhaliiClient
from clauseguard.reference.legislation_index import ActListing, parse_legislation_index
from clauseguard.reference.mirror import (
    default_log_path,
    mirror_act,
    mirror_constitution,
    write_mirror_registry,
)

Target = Literal["all", "constitution", "act"]
LEGISLATION_INDEX_URL = "/legislation/"

app = typer.Typer(help="Mirror GhaLII reference documents.")


@app.command()
def main(
    target: Annotated[str, typer.Option(help="Mirror target.")] = "all",
    number: Annotated[int | None, typer.Option(help="Act number for --target act.")] = None,
    year: Annotated[int | None, typer.Option(help="Act year for --target act.")] = None,
    dry_run: Annotated[bool, typer.Option(help="List work without mirroring documents.")] = False,
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
) -> None:
    """Run the GhaLII mirror command."""

    client = GhaliiClient()
    log_path = default_log_path(repo_root)
    run_mirror(client, repo_root, log_path, parse_target(target), number, year, dry_run)


def parse_target(target: str) -> Target:
    """Validate and return a mirror target."""

    if target not in {"all", "constitution", "act"}:
        raise typer.BadParameter("target must be all, constitution, or act.")
    return cast(Target, target)


def run_mirror(
    client: GhaliiClient,
    repo_root: Path,
    log_path: Path,
    target: Target,
    number: int | None,
    year: int | None,
    dry_run: bool,
) -> None:
    """Run one mirror target."""

    if target == "constitution":
        mirror_constitution(client, repo_root, log_path)
    elif target == "act":
        mirror_one_act(client, repo_root, log_path, number, year)
    else:
        mirror_all(client, repo_root, log_path, dry_run)


def mirror_one_act(
    client: GhaliiClient,
    repo_root: Path,
    log_path: Path,
    number: int | None,
    year: int | None,
) -> None:
    """Mirror one Act from CLI options."""

    if number is None or year is None:
        raise typer.BadParameter("--target act requires --number and --year.")
    entry = mirror_act(client, repo_root, year, number, log_path)
    write_mirror_registry([entry], repo_root)


def mirror_all(client: GhaliiClient, repo_root: Path, log_path: Path, dry_run: bool) -> None:
    """Mirror or list all Acts from the legislation index."""

    listings = fetch_listings(client)
    if dry_run:
        print_dry_run(listings)
        return
    entries = [mirror_act(client, repo_root, item.year, item.act_number, log_path) for item in listings]
    write_mirror_registry(entries, repo_root)


def fetch_listings(client: GhaliiClient) -> list[ActListing]:
    """Fetch and parse the legislation index."""

    html_text = client.get_text(LEGISLATION_INDEX_URL)
    return parse_legislation_index(html_text, client.absolute_url(LEGISLATION_INDEX_URL))


def print_dry_run(listings: list[ActListing]) -> None:
    """Print dry-run listings for the CLI."""

    for item in listings:
        typer.echo(f"{item.year} Act {item.act_number}: {item.title}")
