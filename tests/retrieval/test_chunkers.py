"""Tests for retrieval chunk builders."""

from __future__ import annotations

from datetime import datetime, timezone

from clauseguard.parsing.schemas import BillDocument, BillNode
from clauseguard.retrieval.chunkers import chunks_from_bill


def test_chunks_from_bill_scope_citations() -> None:
    """Build bill chunks with scoped IDs."""

    document = BillDocument(
        title="Sample Bill",
        source_file="raw.pdf",
        parsed_at=datetime.now(timezone.utc),
        parser_version="test",
        nodes={
            "cl_1": BillNode(
                id="cl_1",
                parent_id=None,
                level="clause",
                number="1",
                heading="Objects",
                text="Digital services.",
                page_start=3,
                page_end=4,
            )
        },
        root_node_ids=["cl_1"],
    )

    chunks = chunks_from_bill(document, "sample_bill_2026")

    assert chunks[0].chunk_id == "bill:sample_bill_2026:cl_1"
    assert chunks[0].page_start == 3
