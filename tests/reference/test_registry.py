"""Tests for the local legal reference registry."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from clauseguard.reference.registry import (
    RegistryError,
    find_by_act_number,
    find_by_path,
    find_by_title,
    list_act_directories,
    load_registry,
    missing_registry_directories,
    parse_registry,
    write_registry,
)
from clauseguard.reference.schemas import RegistryEntry

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "registry"


def fixture_text(name: str) -> str:
    """Return fixture content as text."""

    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_parse_registry_validates_entries() -> None:
    """Parse registry JSON into typed entries."""

    entries = parse_registry(fixture_text("registry.json"))

    assert len(entries) == 2
    assert entries[0].act_number == 769
    assert entries[0].short_title == "NCA Act"


def test_parse_registry_rejects_non_list_json() -> None:
    """Reject registry JSON that is not a list."""

    with pytest.raises(RegistryError, match="must be a list"):
        parse_registry("{}")


def test_parse_registry_rejects_invalid_entry() -> None:
    """Reject entries that do not match the schema."""

    with pytest.raises(RegistryError, match="Invalid registry JSON"):
        parse_registry(json.dumps([{"title": "Missing required fields"}]))


def test_load_registry_requires_existing_file(tmp_path: Path) -> None:
    """Fail clearly when a registry file does not exist."""

    with pytest.raises(RegistryError, match="does not exist"):
        load_registry(tmp_path / "missing.json")


def test_write_registry_writes_stable_json(tmp_path: Path) -> None:
    """Write sorted registry entries as JSON."""

    path = tmp_path / "registry.json"
    write_registry([entry(843), entry(769)], path)
    loaded = load_registry(path)

    assert [item.act_number for item in loaded] == [769, 843]
    assert path.read_text(encoding="utf-8").endswith("\n")


def test_list_act_directories_only_returns_act_folders(tmp_path: Path) -> None:
    """List only folders with the expected Act prefix."""

    (tmp_path / "act_0769_nca_2008").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "registry.json").write_text("[]", encoding="utf-8")

    folders = list_act_directories(tmp_path)

    assert [folder.name for folder in folders] == ["act_0769_nca_2008"]


def test_missing_registry_directories_finds_unregistered_acts(tmp_path: Path) -> None:
    """Find Act folders that are absent from the registry."""

    registered = tmp_path / "act_0769_nca_2008"
    missing = tmp_path / "act_1038_cybersecurity_2020"
    registered.mkdir()
    missing.mkdir()
    entries = [entry(769, file_path=str(registered / "parsed.json"))]

    result = missing_registry_directories(entries, tmp_path)

    assert result == [missing]


def test_lookup_helpers_return_matching_entries() -> None:
    """Find entries by Act number, title, and file path."""

    entries = parse_registry(fixture_text("registry.json"))

    assert find_by_act_number(entries, 769)[0].title.startswith("National")
    assert find_by_title(entries, "data protection act, 2012")[0].act_number == 843
    assert find_by_path(entries, "docs\\reference\\ghana_acts\\act_0769_nca_2008\\parsed.json")
    assert find_by_path(entries, "missing/parsed.json") is None


def entry(act_number: int, file_path: str | None = None) -> RegistryEntry:
    """Create a registry entry for tests."""

    path = file_path or f"docs/reference/ghana_acts/act_{act_number:04d}/parsed.json"
    return RegistryEntry(
        doc_type="act",
        act_number=act_number,
        year=2000 + act_number % 100,
        title=f"Act {act_number}",
        status="in_force",
        file_path=path,
        content_hash=f"hash-{act_number}",
        fetched_at=datetime(2026, 5, 26, tzinfo=timezone.utc),
    )
