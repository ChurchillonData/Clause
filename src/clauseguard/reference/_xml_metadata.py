"""Metadata extraction for Akoma Ntoso documents."""

from __future__ import annotations

from typing import Literal

from lxml import etree

from clauseguard.reference._xml_common import normalise_space

DocTypeInput = Literal["constitution", "act"]


def extract_title(root: etree._Element) -> str:
    """Return the best available document title."""

    for tag_name in ["docTitle", "shortTitle", "title"]:
        value = extract_optional_text(root, tag_name)
        if value:
            return value
    return "Untitled legal document"


def extract_optional_text(root: etree._Element, tag_name: str) -> str | None:
    """Return the first matching text value for a tag."""

    matches = root.xpath(f".//*[local-name()='{tag_name}']")
    for match in matches:
        text = normalise_space(" ".join(match.itertext()))
        if text:
            return text
    return None


def extract_year(root: etree._Element, source_url: str, doc_type: DocTypeInput) -> int:
    """Return the legal document year."""

    date_node = root.xpath(".//*[local-name()='FRBRdate']/@date")
    if date_node:
        year = year_prefix(str(date_node[0]))
        if year is not None:
            return year
    year = first_integer_part(source_url)
    if year is not None:
        return year
    return 1992 if doc_type == "constitution" else 0


def extract_act_number(
    root: etree._Element,
    source_url: str,
    doc_type: DocTypeInput,
) -> int | None:
    """Return an Act number when the document is an Act."""

    if doc_type == "constitution":
        return None

    number_node = root.xpath(".//*[local-name()='FRBRnumber']/@value")
    if number_node and str(number_node[0]).isdigit():
        return int(str(number_node[0]))

    parts = [part for part in source_url.rstrip("/").split("/") if part]
    for part in reversed(parts):
        if part.isdigit():
            return int(part)
    return None


def first_integer_part(text: str) -> int | None:
    """Return the first four digit integer in a string."""

    for part in text.replace("/", " ").replace("-", " ").split():
        if len(part) == 4 and part.isdigit():
            return int(part)
    return None


def year_prefix(text: str) -> int | None:
    """Return a four digit year from the start of a date string."""

    prefix = text[:4]
    return int(prefix) if len(prefix) == 4 and prefix.isdigit() else None
