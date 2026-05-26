"""CLI entry point for searching lexical indexes."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.retrieval.search_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
