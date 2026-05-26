"""Command helpers for lexical search."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from clauseguard.retrieval.index_store import load_index
from clauseguard.retrieval.lexical_index import search_index

app = typer.Typer(help="Search a local lexical index.")


@app.command()
def main(
    index_path: Annotated[Path, typer.Argument(help="Index JSON path.")],
    query: Annotated[str, typer.Argument(help="Search query.")],
    limit: Annotated[int, typer.Option(help="Maximum results.")] = 5,
) -> None:
    """Search a local lexical index."""

    results = search_index(load_index(index_path), query, limit=limit)
    if not results:
        typer.echo("insufficient evidence")
        raise typer.Exit(code=1)
    for item in results:
        typer.echo(format_result(item.score, item.chunk.document_id, item.chunk.node_id, item.chunk.text))


def format_result(score: float, document_id: str, node_id: str, text: str) -> str:
    """Return one compact search result line."""

    preview = text[:160].replace("\n", " ")
    return f"{score:.4f} {document_id}:{node_id} {preview}"
