"""CLI entry point for mirroring the local Constitution PDF."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.reference.constitution_pdf_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
