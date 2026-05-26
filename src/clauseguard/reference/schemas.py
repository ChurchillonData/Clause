"""Shared data models for legal reference documents."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


NodeLevel = Literal["article", "section", "subsection", "paragraph", "subparagraph"]
DocumentType = Literal["constitution", "act"]
DocumentStatus = Literal["in_force", "repealed", "partially_repealed"]


class TextReference(BaseModel):
    """A cross-reference found inside legal text."""

    text: str
    href: str


class TextNode(BaseModel):
    """A single addressable unit of legal text."""

    id: str
    parent_id: str | None
    level: NodeLevel
    number: str
    heading: str | None = None
    text: str
    children_ids: list[str] = Field(default_factory=list)
    references: list[TextReference] = Field(default_factory=list)


class LegalDocument(BaseModel):
    """A parsed Constitution or Act of Parliament."""

    model_config = ConfigDict(arbitrary_types_allowed=False)

    doc_type: DocumentType
    act_number: int | None
    year: int
    title: str
    short_title: str | None = None
    long_title: str | None = None
    date_assented: date | None = None
    date_commenced: date | None = None
    last_amended: date | None = None
    status: DocumentStatus = "in_force"
    source_url: str
    content_hash: str
    fetched_at: datetime
    nodes: dict[str, TextNode]
    root_node_ids: list[str]


class RegistryEntry(BaseModel):
    """One document entry in the local reference registry."""

    doc_type: DocumentType
    act_number: int | None
    year: int
    title: str
    short_title: str | None = None
    status: str
    file_path: str
    content_hash: str
    fetched_at: datetime
    parse_failed: bool = False
    parse_error: str | None = None


class Citation(BaseModel):
    """A structured legal citation parsed from text."""

    raw: str
    act_number: int | None = None
    year: int | None = None
    title: str | None = None
    section_ref: str | None = None
    article_ref: str | None = None
    qualifier: str | None = None
    is_constitution: bool = False


class ResolvedReference(BaseModel):
    """A citation matched to a local document and optional text node."""

    citation: str
    document: RegistryEntry
    node: TextNode | None = None


class AmbiguousMatch(BaseModel):
    """A citation that matched more than one local document."""

    citation: str
    matches: list[RegistryEntry]


class ResolutionReport(BaseModel):
    """Bulk reference resolution result."""

    resolved: list[ResolvedReference] = Field(default_factory=list)
    unresolved: list[str] = Field(default_factory=list)
    ambiguous: list[AmbiguousMatch] = Field(default_factory=list)
