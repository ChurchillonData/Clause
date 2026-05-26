"""Tests for reference mirror smoke checks."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.smoke import run_reference_smoke, smoke_passed

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "registry"


def test_run_reference_smoke_passes_for_loadable_fixture_mirror() -> None:
    """Pass when registry files load and sample citations resolve."""

    report = run_reference_smoke(
        repo_root=FIXTURE_DIR,
        registry_path=FIXTURE_DIR / "registry_resolver.json",
        aliases_path=FIXTURE_DIR / "aliases.yaml",
    )

    assert smoke_passed(report)
    assert report.registry_entries == 5
    assert report.parsed_documents == 5
    assert len(report.resolution_report.resolved) == 3


def test_run_reference_smoke_reports_empty_registry(tmp_path: Path) -> None:
    """Fail clearly when the local registry has not been populated."""

    registry_path = tmp_path / "registry.json"
    aliases_path = tmp_path / "aliases.yaml"
    registry_path.write_text("[]\n", encoding="utf-8")
    aliases_path.write_text("{}\n", encoding="utf-8")

    report = run_reference_smoke(tmp_path, registry_path, aliases_path)

    assert not smoke_passed(report)
    assert "Registry has no entries." in report.issues
    assert "Registry has no Constitution entry." in report.issues
    assert "Unresolved reference: Act 769 of 2008" in report.issues
