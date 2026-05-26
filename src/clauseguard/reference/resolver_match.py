"""Match parsed citations against registry entries."""

from __future__ import annotations

from clauseguard.reference.schemas import Citation, RegistryEntry


def act_matches(
    entries: list[RegistryEntry],
    aliases: dict[str, int],
    citation: Citation,
) -> list[RegistryEntry]:
    """Return Act entries matching a citation."""

    matches = matches_by_number(entries, citation)
    if not matches:
        matches = matches_by_title(entries, citation)
    if not matches:
        matches = matches_by_alias(entries, aliases, citation)
    return filter_year(matches, citation.year)


def matches_by_number(entries: list[RegistryEntry], citation: Citation) -> list[RegistryEntry]:
    """Return matches for an Act number."""

    if citation.act_number is None:
        return []
    return [entry for entry in entries if entry.act_number == citation.act_number]


def matches_by_title(entries: list[RegistryEntry], citation: Citation) -> list[RegistryEntry]:
    """Return matches for an exact title or short title."""

    if citation.title is None:
        return []
    target = citation.title.casefold()
    return [entry for entry in entries if title_match(entry, target)]


def matches_by_alias(
    entries: list[RegistryEntry],
    aliases: dict[str, int],
    citation: Citation,
) -> list[RegistryEntry]:
    """Return matches for a configured alias."""

    if citation.title is None:
        return []
    act_number = aliases.get(citation.title.casefold())
    if act_number is None:
        return []
    return matches_by_number(entries, Citation(raw="", act_number=act_number))


def constitution_entry(entries: list[RegistryEntry]) -> RegistryEntry | None:
    """Return the Constitution registry entry when present."""

    for entry in entries:
        if entry.doc_type == "constitution":
            return entry
    return None


def filter_year(entries: list[RegistryEntry], year: int | None) -> list[RegistryEntry]:
    """Filter entries by year when the citation includes one."""

    return entries if year is None else [entry for entry in entries if entry.year == year]


def title_match(entry: RegistryEntry, target: str) -> bool:
    """Return whether an entry matches a title-like citation."""

    titles = [entry.title.casefold()]
    if entry.short_title:
        titles.append(entry.short_title.casefold())
    return target in titles
