"""CLI entry point for checking a parsed bill folder."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.parsing.check_bill_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
