"""Run local reference mirror smoke checks."""

from _bootstrap import add_src_to_path

add_src_to_path()

from clauseguard.reference.smoke_cli import app  # noqa: E402


if __name__ == "__main__":
    app()
