"""Path helpers for mirrored legal reference documents."""

from __future__ import annotations

import re
from pathlib import Path


def constitution_dir(repo_root: Path) -> Path:
    """Return the local Constitution reference directory."""

    return repo_root / "docs" / "reference" / "constitution_1992"


def acts_dir(repo_root: Path) -> Path:
    """Return the local Acts reference directory."""

    return repo_root / "docs" / "reference" / "ghana_acts"


def act_dir(repo_root: Path, act_number: int, title: str, year: int) -> Path:
    """Return the local folder for one mirrored Act."""

    slug = slugify(title)
    return acts_dir(repo_root) / f"act_{act_number:04d}_{slug}_{year}"


def slugify(text: str) -> str:
    """Convert title text to a simple folder slug."""

    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    useful = [word for word in words if word not in {"act", "the"}]
    return "_".join(useful[:5]) or "untitled"
