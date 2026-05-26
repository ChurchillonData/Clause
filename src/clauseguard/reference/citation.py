"""Parse common Ghana legal citation strings."""

from __future__ import annotations

import re

from clauseguard.reference.schemas import Citation

ACT_NUMBER_RE = re.compile(r"\bAct\s+(?P<number>\d+)\b", re.IGNORECASE)
ARTICLE_RE = re.compile(r"\b(?:Article|Art\.)\s*(?P<article>\d+(?:\([^)]+\))*)", re.IGNORECASE)
SECTION_RE = re.compile(r"\b(?:section|s\.)\s*(?P<section>\d+(?:\([^)]+\))*)", re.IGNORECASE)
YEAR_RE = re.compile(r"(?:,\s*|\bof\s+)(?P<year>\d{4})\b", re.IGNORECASE)


def parse_citation(text: str) -> Citation:
    """Parse one citation string into structured fields."""

    raw = " ".join(text.split())
    qualifier = _extract_qualifier(raw)
    article_ref = _extract_article_ref(raw)
    section_ref = _extract_section_ref(raw)
    is_constitution = article_ref is not None or _mentions_constitution(raw)
    return Citation(
        raw=raw,
        act_number=_extract_act_number(raw),
        year=_extract_year(raw),
        title=_extract_title(raw, section_ref, article_ref, is_constitution),
        section_ref=section_ref,
        article_ref=article_ref,
        qualifier=qualifier,
        is_constitution=is_constitution,
    )


def node_id_from_ref(prefix: str, reference: str) -> str:
    """Convert a section or article reference to a TextNode id."""

    parts = re.findall(r"\d+|[A-Za-z]+", reference)
    return "_".join([prefix, *[part.lower() for part in parts]])


def _extract_qualifier(text: str) -> str | None:
    """Return a citation qualifier when present."""

    return "as amended" if "as amended" in text.casefold() else None


def _extract_article_ref(text: str) -> str | None:
    """Return an article reference from text."""

    match = ARTICLE_RE.search(text)
    return match.group("article") if match else None


def _extract_section_ref(text: str) -> str | None:
    """Return a section reference from text."""

    match = SECTION_RE.search(text)
    return match.group("section") if match else None


def _extract_act_number(text: str) -> int | None:
    """Return an Act number from text."""

    match = ACT_NUMBER_RE.search(text)
    return int(match.group("number")) if match else None


def _extract_year(text: str) -> int | None:
    """Return a cited year from text."""

    match = YEAR_RE.search(text)
    return int(match.group("year")) if match else None


def _mentions_constitution(text: str) -> bool:
    """Return whether text refers to the Constitution."""

    return "constitution" in text.casefold()


def _extract_title(
    text: str,
    section_ref: str | None,
    article_ref: str | None,
    is_constitution: bool,
) -> str | None:
    """Return the document title portion of a citation."""

    if is_constitution:
        return "Constitution"
    without_prefix = _remove_leading_section(text, section_ref)
    without_article = _remove_article(without_prefix, article_ref)
    return _clean_title(without_article)


def _remove_leading_section(text: str, section_ref: str | None) -> str:
    """Remove a leading section phrase from a citation."""

    if not section_ref:
        return text
    return SECTION_RE.sub("", text, count=1).removeprefix(" of ").strip()


def _remove_article(text: str, article_ref: str | None) -> str:
    """Remove an article phrase from a citation."""

    if not article_ref:
        return text
    return ARTICLE_RE.sub("", text, count=1).strip()


def _clean_title(text: str) -> str | None:
    """Clean remaining citation text into a possible title."""

    cleaned = ACT_NUMBER_RE.sub("", text)
    cleaned = YEAR_RE.sub("", cleaned)
    cleaned = cleaned.replace("( )", "").replace("()", "")
    cleaned = cleaned.replace("as amended", "")
    cleaned = cleaned.strip(" ,()")
    cleaned = re.sub(r"^the\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned or None
