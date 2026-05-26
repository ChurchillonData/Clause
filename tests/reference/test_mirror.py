"""Tests for mirror orchestration."""

from __future__ import annotations

from pathlib import Path

import pytest

from clauseguard.reference.ghalii_client import GhaliiClientError
from clauseguard.reference.mirror import (
    default_log_path,
    mirror_act,
    mirror_constitution,
)
from clauseguard.reference.mirror_registry import (
    constitution_registry_entry,
    merge_registry_entries,
    mirror_registry_path,
    write_mirror_registry,
)
from clauseguard.reference.registry import RegistryError, load_registry

FIXTURE_ROOT = Path(__file__).parent / "fixtures"


class FakeClient:
    """Small fake client for mirror tests."""

    def __init__(self, responses: dict[str, str | Exception]) -> None:
        """Create a fake client with URL keyed responses."""

        self.responses = responses
        self.calls: list[str] = []

    def absolute_url(self, url: str) -> str:
        """Return a fake absolute URL."""

        return f"https://ghalii.org{url}" if url.startswith("/") else url

    def get_text(self, url: str) -> str:
        """Return configured text or raise configured errors."""

        self.calls.append(url)
        result = self.responses[url]
        if isinstance(result, Exception):
            raise result
        return result


def fixture_text(path: str) -> str:
    """Return fixture text."""

    return (FIXTURE_ROOT / path).read_text(encoding="utf-8")


def test_mirror_constitution_writes_raw_json_and_articles(tmp_path: Path) -> None:
    """Mirror the Constitution XML into local files."""

    client = FakeClient(
        {"/akn/gh/act/1992/constitution/eng@.xml": fixture_text("xml/constitution_article.xml")}
    )
    log_path = tmp_path / "logs" / "mirror.jsonl"

    document = mirror_constitution(client, tmp_path, log_path)

    base = tmp_path / "docs" / "reference" / "constitution_1992"
    assert document.title == "Constitution of the Republic of Ghana, 1992"
    assert (base / "raw.xml").exists()
    assert (base / "parsed.json").exists()
    assert (base / "articles" / "art_19.md").read_text(encoding="utf-8").startswith(
        "# Article 19. Fair trial"
    )
    assert '"event": "fetch"' in log_path.read_text(encoding="utf-8")


def test_mirror_constitution_uses_cached_raw_file(tmp_path: Path) -> None:
    """Use local raw XML when it already exists."""

    base = tmp_path / "docs" / "reference" / "constitution_1992"
    base.mkdir(parents=True)
    (base / "raw.xml").write_text(fixture_text("xml/constitution_article.xml"), encoding="utf-8")
    client = FakeClient({})

    mirror_constitution(client, tmp_path, tmp_path / "logs" / "mirror.jsonl")

    assert client.calls == []


def test_mirror_act_writes_xml_outputs_and_registry_entry(tmp_path: Path) -> None:
    """Mirror one XML Act into local files."""

    client = FakeClient({"/akn/gh/act/2008/769/eng@.xml": fixture_text("xml/simple_act.xml")})
    entry = mirror_act(client, tmp_path, 2008, 769, tmp_path / "logs" / "mirror.jsonl")

    parsed_path = Path(entry.file_path)
    assert entry.act_number == 769
    assert parsed_path.exists()
    assert (parsed_path.parent / "raw.xml").exists()
    assert (parsed_path.parent / "sections" / "sec_1.md").exists()


def test_mirror_act_falls_back_to_html(tmp_path: Path) -> None:
    """Use HTML when the XML source cannot be fetched."""

    client = FakeClient(
        {
            "/akn/gh/act/2008/769/eng@.xml": GhaliiClientError("missing xml"),
            "/akn/gh/act/2008/769": fixture_text("html/simple_act.html"),
        }
    )
    entry = mirror_act(client, tmp_path, 2008, 769, tmp_path / "logs" / "mirror.jsonl")

    parsed_path = Path(entry.file_path)
    assert (parsed_path.parent / "raw.html").exists()
    assert (parsed_path.parent / "sections" / "sec_1.md").exists()
    assert client.calls == ["/akn/gh/act/2008/769/eng@.xml", "/akn/gh/act/2008/769"]


def test_write_mirror_registry_writes_entries(tmp_path: Path) -> None:
    """Write mirrored Act entries to the local registry."""

    client = FakeClient({"/akn/gh/act/2008/769/eng@.xml": fixture_text("xml/simple_act.xml")})
    entry = mirror_act(client, tmp_path, 2008, 769, tmp_path / "logs" / "mirror.jsonl")

    write_mirror_registry([entry], tmp_path)

    registry_path = tmp_path / "docs" / "reference" / "ghana_acts" / "registry.json"
    assert load_registry(registry_path)[0].act_number == 769


def test_write_mirror_registry_preserves_existing_entries(tmp_path: Path) -> None:
    """Update one registry entry without deleting other documents."""

    client = FakeClient(
        {
            "/akn/gh/act/1992/constitution/eng@.xml": fixture_text("xml/constitution_article.xml"),
            "/akn/gh/act/2008/769/eng@.xml": fixture_text("xml/simple_act.xml"),
        }
    )
    constitution = mirror_constitution(client, tmp_path, tmp_path / "logs" / "mirror.jsonl")
    constitution_entry = constitution_registry_entry(constitution, tmp_path)
    write_mirror_registry([constitution_entry], tmp_path)
    act_entry = mirror_act(client, tmp_path, 2008, 769, tmp_path / "logs" / "mirror.jsonl")

    write_mirror_registry([act_entry], tmp_path)

    registry_path = tmp_path / "docs" / "reference" / "ghana_acts" / "registry.json"
    entries = load_registry(registry_path)
    assert {entry.doc_type for entry in entries} == {"constitution", "act"}


def test_merge_registry_entries_replaces_same_document() -> None:
    """Replace matching registry entries by document identity."""

    original = load_registry(FIXTURE_ROOT / "registry" / "registry_resolver.json")[1]
    updated = original.model_copy(update={"content_hash": "new-hash"})

    entries = merge_registry_entries([original], [updated])

    assert len(entries) == 1
    assert entries[0].content_hash == "new-hash"


def test_write_mirror_registry_rejects_invalid_existing_registry(tmp_path: Path) -> None:
    """Do not overwrite a malformed registry silently."""

    path = mirror_registry_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{bad json", encoding="utf-8")

    client = FakeClient({"/akn/gh/act/2008/769/eng@.xml": fixture_text("xml/simple_act.xml")})
    entry = mirror_act(client, tmp_path, 2008, 769, tmp_path / "logs" / "mirror.jsonl")

    with pytest.raises(RegistryError):
        write_mirror_registry([entry], tmp_path)


def test_default_log_path_uses_logs_folder(tmp_path: Path) -> None:
    """Build a timestamped mirror log path."""

    path = default_log_path(tmp_path)

    assert path.parent == tmp_path / "logs"
    assert path.name.startswith("mirror_run_")
