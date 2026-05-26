"""Tests for resolving citations against local reference documents."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.resolver import ReferenceResolver

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "registry"


def resolver() -> ReferenceResolver:
    """Return a resolver backed by synthetic fixtures."""

    return ReferenceResolver(
        registry_path=FIXTURE_DIR / "registry_resolver.json",
        aliases_path=FIXTURE_DIR / "aliases.yaml",
        repo_root=FIXTURE_DIR,
    )


def test_resolve_act_by_number_and_year() -> None:
    """Resolve an Act citation using number and year."""

    document = resolver().resolve_act("Act 769 of 2008")

    assert document is not None
    assert document.title == "National Communications Authority Act, 2008"


def test_resolve_act_by_title_and_alias() -> None:
    """Resolve Act citations using title and alias."""

    title_match = resolver().resolve_act("the Data Protection Act, 2012")
    alias_match = resolver().resolve_act("NCA Act")

    assert title_match is not None
    assert title_match.act_number == 843
    assert alias_match is not None
    assert alias_match.act_number == 769


def test_resolve_section_by_nested_reference() -> None:
    """Resolve a nested section in a matched Act."""

    node = resolver().resolve_section("Act 769 of 2008", "12(3)(b)")

    assert node is not None
    assert node.text == "The operator shall comply with the request."


def test_resolve_constitution_article() -> None:
    """Resolve a nested Constitution article."""

    node = resolver().resolve_constitution_article("19(2)(d)")

    assert node is not None
    assert node.text.startswith("The person shall be permitted")


def test_resolve_bare_article_reference_to_constitution() -> None:
    """Resolve Article citations without an explicit Constitution phrase."""

    report = resolver().resolve_references(["Article 19(2)(d)"])

    assert len(report.resolved) == 1
    assert report.resolved[0].node is not None


def test_bulk_resolution_groups_results() -> None:
    """Group resolved, unresolved, and ambiguous references."""

    report = resolver().resolve_references(
        [
            "section 12(3)(b) of Act 769 of 2008",
            "Article 19(2)(d) of the Constitution",
            "Act 999",
            "Act 769",
        ]
    )

    assert len(report.resolved) == 2
    assert report.resolved[0].node is not None
    assert report.unresolved == ["Act 999"]
    assert report.ambiguous[0].citation == "Act 769"


def test_ambiguous_act_returns_none_for_single_resolution() -> None:
    """Avoid silently selecting one Act when multiple match."""

    assert resolver().resolve_act("Act 769") is None
