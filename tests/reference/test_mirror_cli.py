"""Tests for mirror command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import typer

from clauseguard.reference import mirror_cli
from clauseguard.reference.legislation_index import ActListing
from clauseguard.reference.schemas import LegalDocument, RegistryEntry


class FakeClient:
    """Small fake client for CLI tests."""

    def __init__(self, html_text: str = "") -> None:
        """Create a fake client."""

        self.html_text = html_text

    def absolute_url(self, url: str) -> str:
        """Return a fake absolute URL."""

        return f"https://ghalii.org{url}"

    def get_text(self, url: str) -> str:
        """Return fake index HTML."""

        return self.html_text


def entry(act_number: int, year: int) -> RegistryEntry:
    """Create a minimal registry entry."""

    return RegistryEntry(
        doc_type="act",
        act_number=act_number,
        year=year,
        title=f"Act {act_number}",
        short_title=f"Act {act_number}",
        status="active",
        file_path=f"docs/reference/ghana_acts/act_{act_number}/parsed.json",
        content_hash="abc",
        fetched_at="2026-05-26T00:00:00Z",
    )


def constitution_document() -> LegalDocument:
    """Create a minimal Constitution document."""

    return LegalDocument(
        doc_type="constitution",
        act_number=None,
        year=1992,
        title="Constitution of the Republic of Ghana, 1992",
        short_title="Constitution",
        status="in_force",
        source_url="https://ghalii.org/akn/gh/act/1992/constitution",
        content_hash="constitution-hash",
        fetched_at="2026-05-26T00:00:00Z",
        nodes={},
        root_node_ids=[],
    )


def test_fetch_listings_reads_legislation_index() -> None:
    """Fetch and parse the legislation index."""

    html = '<a href="/akn/gh/act/2012/843">Data Protection Act, 2012</a>'
    listings = mirror_cli.fetch_listings(FakeClient(html))  # type: ignore[arg-type]

    assert listings[0].act_number == 843
    assert listings[0].url == "https://ghalii.org/akn/gh/act/2012/843"


def test_mirror_all_dry_run_prints_without_mirroring(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Dry runs list work without writing mirrored Acts."""

    listings = [ActListing(843, 2012, "Data Protection Act, 2012", "https://example.test/843")]
    calls: list[str] = []
    monkeypatch.setattr(mirror_cli, "fetch_listings", lambda client: listings)
    monkeypatch.setattr(mirror_cli, "mirror_act", lambda *args: calls.append("mirror"))

    mirror_cli.mirror_all(
        FakeClient(),  # type: ignore[arg-type]
        tmp_path,
        tmp_path / "mirror.jsonl",
        dry_run=True,
    )

    assert "2012 Act 843: Data Protection Act, 2012" in capsys.readouterr().out
    assert calls == []


def test_run_mirror_constitution_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Run the Constitution target."""

    calls: list[Path] = []
    written: list[list[RegistryEntry]] = []
    monkeypatch.setattr(
        mirror_cli,
        "mirror_constitution",
        lambda client, repo_root, log_path: calls.append(repo_root) or constitution_document(),
    )
    monkeypatch.setattr(
        mirror_cli,
        "write_mirror_registry",
        lambda entries, repo_root: written.append(entries),
    )

    mirror_cli.run_mirror(
        FakeClient(),  # type: ignore[arg-type]
        tmp_path,
        tmp_path / "mirror.jsonl",
        "constitution",
        None,
        None,
        False,
    )

    assert calls == [tmp_path]
    assert written[0][0].doc_type == "constitution"


def test_run_mirror_act_target_writes_registry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Run one Act target and write its registry entry."""

    mirrored: list[tuple[int, int]] = []
    written: list[list[RegistryEntry]] = []

    def fake_mirror_act(*args: Any) -> RegistryEntry:
        mirrored.append((args[2], args[3]))
        return entry(args[3], args[2])

    monkeypatch.setattr(mirror_cli, "mirror_act", fake_mirror_act)
    monkeypatch.setattr(
        mirror_cli,
        "write_mirror_registry",
        lambda entries, repo_root: written.append(entries),
    )

    mirror_cli.run_mirror(
        FakeClient(),  # type: ignore[arg-type]
        tmp_path,
        tmp_path / "mirror.jsonl",
        "act",
        843,
        2012,
        False,
    )

    assert mirrored == [(2012, 843)]
    assert written[0][0].act_number == 843


def test_mirror_all_writes_constitution_and_acts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Mirror all discovered Acts plus the Constitution registry entry."""

    listings = [ActListing(843, 2012, "Data Protection Act, 2012", "https://example.test/843")]
    written: list[list[RegistryEntry]] = []
    monkeypatch.setattr(mirror_cli, "fetch_listings", lambda client: listings)
    monkeypatch.setattr(mirror_cli, "mirror_constitution", lambda *args: constitution_document())
    monkeypatch.setattr(mirror_cli, "mirror_act", lambda *args: entry(843, 2012))
    monkeypatch.setattr(
        mirror_cli,
        "write_mirror_registry",
        lambda entries, repo_root: written.append(entries),
    )

    mirror_cli.mirror_all(
        FakeClient(),  # type: ignore[arg-type]
        tmp_path,
        tmp_path / "mirror.jsonl",
        dry_run=False,
    )

    assert [item.doc_type for item in written[0]] == ["act", "constitution"]


def test_act_target_requires_number_and_year(tmp_path: Path) -> None:
    """Reject Act mirroring without both identifying values."""

    with pytest.raises(typer.BadParameter):
        mirror_cli.run_mirror(
            FakeClient(),  # type: ignore[arg-type]
            tmp_path,
            tmp_path / "mirror.jsonl",
            "act",
            843,
            None,
            False,
        )


def test_parse_target_rejects_unknown_target() -> None:
    """Reject unknown mirror targets."""

    with pytest.raises(typer.BadParameter):
        mirror_cli.parse_target("unknown")
