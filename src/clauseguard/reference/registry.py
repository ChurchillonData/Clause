"""Read, write, and query the local legal reference registry."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from clauseguard.reference.schemas import RegistryEntry

DEFAULT_REGISTRY_PATH = Path("docs/reference/ghana_acts/registry.json")
DEFAULT_ACTS_ROOT = Path("docs/reference/ghana_acts")


class RegistryError(ValueError):
    """Raised when registry data is missing or invalid."""


def load_registry(path: Path = DEFAULT_REGISTRY_PATH) -> list[RegistryEntry]:
    """Load registry entries from JSON.

    Args:
        path: Registry JSON path.

    Returns:
        Validated registry entries.

    Raises:
        RegistryError: If the file is missing or invalid.
    """

    if not path.exists():
        raise RegistryError(f"Registry file does not exist: {path}")
    return parse_registry(path.read_text(encoding="utf-8"))


def parse_registry(registry_json: str) -> list[RegistryEntry]:
    """Parse registry JSON into validated entries."""

    try:
        raw_entries = json.loads(registry_json)
        if not isinstance(raw_entries, list):
            raise RegistryError("Registry JSON must be a list.")
        return [RegistryEntry.model_validate(entry) for entry in raw_entries]
    except (json.JSONDecodeError, ValidationError) as exc:
        raise RegistryError(f"Invalid registry JSON: {exc}") from exc


def write_registry(entries: list[RegistryEntry], path: Path = DEFAULT_REGISTRY_PATH) -> None:
    """Write registry entries as stable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [entry.model_dump(mode="json") for entry in sort_entries(entries)]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sort_entries(entries: list[RegistryEntry]) -> list[RegistryEntry]:
    """Return entries in stable document order."""

    return sorted(entries, key=lambda entry: (entry.doc_type, entry.act_number or 0, entry.year))


def list_act_directories(acts_root: Path = DEFAULT_ACTS_ROOT) -> list[Path]:
    """List mirrored Act folders under the Acts root."""

    if not acts_root.exists():
        return []
    return sorted(path for path in acts_root.iterdir() if path.is_dir() and path.name.startswith("act_"))


def missing_registry_directories(
    entries: list[RegistryEntry],
    acts_root: Path = DEFAULT_ACTS_ROOT,
) -> list[Path]:
    """Return Act folders that have no registry entry."""

    registered = {normalise_path(entry.file_path) for entry in entries}
    missing: list[Path] = []
    for folder in list_act_directories(acts_root):
        parsed_path = normalise_path(str(folder / "parsed.json"))
        if parsed_path not in registered:
            missing.append(folder)
    return missing


def find_by_act_number(entries: list[RegistryEntry], act_number: int) -> list[RegistryEntry]:
    """Return entries with the requested Act number."""

    return [entry for entry in entries if entry.act_number == act_number]


def find_by_title(entries: list[RegistryEntry], title: str) -> list[RegistryEntry]:
    """Return entries whose title matches case-insensitively."""

    target = title.casefold()
    return [entry for entry in entries if entry.title.casefold() == target]


def find_by_path(entries: list[RegistryEntry], file_path: str) -> RegistryEntry | None:
    """Return one entry by parsed document path."""

    target = normalise_path(file_path)
    for entry in entries:
        if normalise_path(entry.file_path) == target:
            return entry
    return None


def normalise_path(file_path: str) -> str:
    """Return a comparable POSIX-style path string."""

    return file_path.replace("\\", "/").strip("/")
