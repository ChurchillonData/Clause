"""Parse GhaLII legislation index pages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from clauseguard.reference._xml_common import normalise_space

ACT_URL_RE = re.compile(r"/akn/gh/act/(?P<year>\d{4})/(?P<number>\d+)")


@dataclass(frozen=True)
class ActListing:
    """One Act listed on the GhaLII legislation index."""

    act_number: int
    year: int
    title: str
    url: str


def parse_legislation_index(html_text: str, base_url: str) -> list[ActListing]:
    """Extract Act listings from a GhaLII legislation index page."""

    soup = BeautifulSoup(html_text, "lxml")
    listings = [listing for link in soup.find_all("a", href=True) if (listing := parse_link(link, base_url))]
    return sorted(unique_listings(listings), key=lambda item: (item.year, item.act_number, item.title))


def parse_link(link: Tag, base_url: str) -> ActListing | None:
    """Parse one index link into an Act listing."""

    href = str(link.get("href"))
    match = ACT_URL_RE.search(href)
    if match is None:
        return None
    title = normalise_space(link.get_text(" ", strip=True))
    if not title:
        return None
    return ActListing(
        act_number=int(match.group("number")),
        year=int(match.group("year")),
        title=title,
        url=urljoin(base_url, href),
    )


def unique_listings(listings: list[ActListing]) -> list[ActListing]:
    """Remove duplicate index listings while preserving first entries."""

    seen: set[tuple[int, int, str]] = set()
    unique: list[ActListing] = []
    for listing in listings:
        key = (listing.act_number, listing.year, listing.url)
        if key not in seen:
            seen.add(key)
            unique.append(listing)
    return unique
