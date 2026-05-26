"""Make local src imports work when scripts are run directly."""

from __future__ import annotations

import sys
from pathlib import Path


def add_src_to_path() -> None:
    """Add the repository src directory to sys.path."""

    src_path = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_path))
