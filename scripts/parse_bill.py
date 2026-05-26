"""CLI entry point for parsing a bill folder."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.parsing.parse_bill_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
