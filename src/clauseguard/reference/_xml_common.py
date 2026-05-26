"""Small XML helper functions used by reference parsers."""

from __future__ import annotations

from typing import cast

from lxml import etree


def local_name(element: etree._Element) -> str:
    """Return an element local name without its namespace."""

    return cast(str, etree.QName(element).localname)


def direct_children(element: etree._Element, tag_name: str) -> list[etree._Element]:
    """Return direct children with a matching local name."""

    return [child for child in element if local_name(child) == tag_name]


def direct_child_text(element: etree._Element, tag_name: str) -> str | None:
    """Return normalised text from the first matching direct child."""

    for child in direct_children(element, tag_name):
        text = normalise_space(" ".join(child.itertext()))
        if text:
            return text
    return None


def normalise_id(text: str) -> str:
    """Return a stable lowercase identifier."""

    cleaned = text.replace("-", "_").replace(".", "_").replace("(", "_").replace(")", "")
    return "_".join(part for part in cleaned.lower().split("_") if part)


def normalise_space(text: str) -> str:
    """Collapse repeated whitespace in text."""

    collapsed = " ".join(text.split())
    for mark in [".", ",", ";", ":", "?", "!"]:
        collapsed = collapsed.replace(f" {mark}", mark)
    return collapsed


def clean_number(text: str) -> str:
    """Return a legal number without punctuation wrappers."""

    return text.strip().strip(".").strip("()")
