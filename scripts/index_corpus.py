"""CLI entry point for building lexical indexes."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.retrieval.index_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
