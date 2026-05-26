"""Smoke checks for the local reference mirror and resolver."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from clauseguard.reference.document_store import load_document
from clauseguard.reference.registry import DEFAULT_REGISTRY_PATH, load_registry
from clauseguard.reference.resolver import DEFAULT_ALIASES_PATH, ReferenceResolver
from clauseguard.reference.resolver_match import constitution_entry
from clauseguard.reference.schemas import RegistryEntry, ResolutionReport

DEFAULT_SAMPLE_REFERENCES = [
    "Act 769 of 2008",
    "section 12 of Act 769 of 2008",
    "Article 19(2)(d) of the Constitution",
]


class ReferenceSmokeReport(BaseModel):
    """Result of a local reference mirror smoke check."""

    registry_entries: int
    parsed_documents: int
    sample_references: list[str]
    resolution_report: ResolutionReport
    issues: list[str]


def run_reference_smoke(
    repo_root: Path = Path("."),
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    aliases_path: Path = DEFAULT_ALIASES_PATH,
    sample_references: list[str] | None = None,
) -> ReferenceSmokeReport:
    """Check that the local mirror and resolver are usable."""

    samples = sample_references or DEFAULT_SAMPLE_REFERENCES
    registry_file = repo_path(repo_root, registry_path)
    aliases_file = repo_path(repo_root, aliases_path)
    entries = load_registry(registry_file)
    issues = registry_issues(entries)
    parsed_count = count_loadable_documents(entries, repo_root, issues)
    resolution_report = resolve_samples(repo_root, registry_file, aliases_file, samples, issues)
    issues.extend(resolution_issues(resolution_report))
    return ReferenceSmokeReport(
        registry_entries=len(entries),
        parsed_documents=parsed_count,
        sample_references=samples,
        resolution_report=resolution_report,
        issues=issues,
    )


def repo_path(repo_root: Path, path: Path) -> Path:
    """Return an absolute or repo-relative path."""

    return path if path.is_absolute() else repo_root / path


def registry_issues(entries: list[RegistryEntry]) -> list[str]:
    """Return registry-level smoke issues."""

    issues: list[str] = []
    if not entries:
        issues.append("Registry has no entries.")
    if constitution_entry(entries) is None:
        issues.append("Registry has no Constitution entry.")
    return issues


def count_loadable_documents(
    entries: list[RegistryEntry],
    repo_root: Path,
    issues: list[str],
) -> int:
    """Load all registry documents and collect failures."""

    count = 0
    for entry in entries:
        try:
            load_document(entry, repo_root)
            count += 1
        except ValueError as exc:
            issues.append(f"Cannot load {entry.file_path}: {exc}")
    return count


def resolve_samples(
    repo_root: Path,
    registry_path: Path,
    aliases_path: Path,
    sample_references: list[str],
    issues: list[str],
) -> ResolutionReport:
    """Resolve sample citations and collect resolver failures."""

    try:
        resolver = ReferenceResolver(registry_path, aliases_path, repo_root)
        return resolver.resolve_references(sample_references)
    except ValueError as exc:
        issues.append(f"Resolver failed: {exc}")
        return ResolutionReport()


def resolution_issues(report: ResolutionReport) -> list[str]:
    """Return issues found in a resolution report."""

    issues = [f"Unresolved reference: {reference}" for reference in report.unresolved]
    issues.extend(f"Ambiguous reference: {match.citation}" for match in report.ambiguous)
    for reference in report.resolved:
        if reference.node is None and has_node_target(reference.citation):
            issues.append(f"Resolved without text node: {reference.citation}")
    return issues


def has_node_target(reference: str) -> bool:
    """Return whether a reference should resolve to a text node."""

    lowered = reference.casefold()
    return "section" in lowered or "article" in lowered


def smoke_passed(report: ReferenceSmokeReport) -> bool:
    """Return whether a smoke report passed."""

    return not report.issues
