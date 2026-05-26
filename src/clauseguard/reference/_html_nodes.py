"""Node extraction helpers for GhaLII HTML fallback parsing."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from clauseguard.reference._xml_common import clean_number, normalise_id, normalise_space
from clauseguard.reference.schemas import TextNode, TextReference


def section_blocks(soup: BeautifulSoup) -> list[Tag]:
    """Return HTML elements that look like legal sections."""

    blocks: list[Tag] = []
    for element in soup.find_all(True):
        if not isinstance(element, Tag):
            continue
        if looks_like_section(element):
            blocks.append(element)
    return blocks


def looks_like_section(element: Tag) -> bool:
    """Return whether an element appears to be a section boundary."""

    element_id = str(element.get("id", "")).lower()
    data_name = str(element.get("data-name", "")).lower()
    return any(
        [
            any(value in {"section", "sec"} for value in class_values(element)),
            data_name in {"section", "sec"},
            element_id.startswith(("section", "sec_")),
        ]
    )


def class_values(element: Tag) -> list[str]:
    """Return lower-case class values for a tag."""

    value = element.get("class")
    if isinstance(value, list):
        return [str(item).lower() for item in value]
    return [str(value).lower()] if value else []


def parse_section_block(element: Tag) -> TextNode:
    """Parse one HTML section block into a text node."""

    number = section_number(element)
    node_id = section_id(element, number)
    return TextNode(
        id=node_id,
        parent_id=None,
        level="section",
        number=number,
        heading=section_heading(element),
        text=section_text(element),
        references=section_references(element),
    )


def section_number(element: Tag) -> str:
    """Return a section number from a section block."""

    explicit = element.get("data-number") or element.get("num")
    if explicit:
        return clean_number(str(explicit))
    heading = first_heading_text(element)
    parts = heading.split()
    if len(parts) >= 2 and parts[0].casefold() == "section":
        return clean_number(parts[1])
    return "unnumbered"


def section_id(element: Tag, number: str) -> str:
    """Return a stable section id."""

    element_id = element.get("id")
    if element_id:
        return normalise_id(str(element_id))
    return normalise_id(f"s_{number}")


def section_heading(element: Tag) -> str | None:
    """Return section heading text without the section number."""

    heading = first_heading_text(element)
    if heading.lower().startswith("section "):
        parts = heading.split(".", 1)
        return normalise_space(parts[1]) if len(parts) == 2 else None
    return heading or None


def section_text(element: Tag) -> str:
    """Return normalised paragraph text from a section block."""

    paragraphs = [normalise_space(item.get_text(" ", strip=True)) for item in element.find_all("p")]
    return normalise_space(" ".join(item for item in paragraphs if item))


def section_references(element: Tag) -> list[TextReference]:
    """Return links found in a section block."""

    refs: list[TextReference] = []
    for link in element.find_all("a", href=True):
        text = normalise_space(link.get_text(" ", strip=True))
        href = str(link.get("href"))
        if text and href:
            refs.append(TextReference(text=text, href=href))
    return refs


def first_heading_text(element: Tag) -> str:
    """Return the first heading text inside a section block."""

    heading = element.find(["h1", "h2", "h3", "h4"])
    return normalise_space(heading.get_text(" ", strip=True)) if isinstance(heading, Tag) else ""
