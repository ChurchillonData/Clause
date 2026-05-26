"""Registry helpers for mirrored reference documents."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.mirror_paths import constitution_dir
from clauseguard.reference.registry import load_registry, write_registry
from clauseguard.reference.schemas import LegalDocument, RegistryEntry


def registry_entry(document: LegalDocument, output_dir: Path) -> RegistryEntry:
    """Create a registry entry for one mirrored document."""

    return RegistryEntry(
        doc_type=document.doc_type,
        act_number=document.act_number,
        year=document.year,
        title=document.title,
        short_title=document.short_title,
        status=document.status,
        file_path=str(output_dir / "parsed.json"),
        content_hash=document.content_hash,
        fetched_at=document.fetched_at,
    )


def write_mirror_registry(entries: list[RegistryEntry], repo_root: Path) -> None:
    """Write or update entries in the local reference registry."""

    path = mirror_registry_path(repo_root)
    existing = load_existing_registry(path)
    write_registry(merge_registry_entries(existing, entries), path)


def mirror_registry_path(repo_root: Path) -> Path:
    """Return the local reference registry path."""

    return repo_root / "docs" / "reference" / "ghana_acts" / "registry.json"


def load_existing_registry(path: Path) -> list[RegistryEntry]:
    """Load an existing registry, or return an empty one."""

    if not path.exists():
        return []
    return load_registry(path)


def merge_registry_entries(
    existing: list[RegistryEntry],
    updates: list[RegistryEntry],
) -> list[RegistryEntry]:
    """Merge registry updates by document identity."""

    merged = {registry_key(entry): entry for entry in existing}
    for entry in updates:
        merged[registry_key(entry)] = entry
    return list(merged.values())


def registry_key(entry: RegistryEntry) -> tuple[str, int | None, int]:
    """Return the stable identity key for a registry entry."""

    return (entry.doc_type, entry.act_number, entry.year)


def constitution_registry_entry(document: LegalDocument, repo_root: Path) -> RegistryEntry:
    """Create a registry entry for the mirrored Constitution."""

    output_dir = constitution_dir(repo_root)
    return registry_entry(document, output_dir)
