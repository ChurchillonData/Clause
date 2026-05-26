"""Shared models for parsed bill documents."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

BillNodeLevel = Literal["clause", "subclause", "paragraph", "subparagraph", "schedule"]


class BillReference(BaseModel):
    """A legal reference found in bill text."""

    text: str


class BillNode(BaseModel):
    """One addressable unit of bill text."""

    id: str
    parent_id: str | None
    level: BillNodeLevel
    number: str
    heading: str | None = None
    text: str
    page_start: int | None = None
    page_end: int | None = None
    children_ids: list[str] = Field(default_factory=list)
    references: list[BillReference] = Field(default_factory=list)


class BillDocument(BaseModel):
    """A parsed bill with clause hierarchy preserved."""

    title: str
    source_file: str
    parsed_at: datetime
    parser_version: str
    nodes: dict[str, BillNode]
    root_node_ids: list[str]
    issues: list[str] = Field(default_factory=list)


class ExtractedPage(BaseModel):
    """Text extracted from one PDF page."""

    page_number: int
    text: str
