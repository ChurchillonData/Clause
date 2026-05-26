"""CLI entry point for the GhaLII mirror."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.reference.mirror_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
