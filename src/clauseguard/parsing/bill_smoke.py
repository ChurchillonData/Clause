"""Smoke checks for parsed bill folders."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from clauseguard.parsing.bill_store import load_parsed_bill
from clauseguard.parsing.schemas import BillDocument


class BillSmokeReport(BaseModel):
    """Result of a parsed bill smoke check."""

    title: str | None
    node_count: int
    clause_count: int
    issues: list[str]
    warnings: list[str] = []


def run_bill_smoke(bill_dir: Path) -> BillSmokeReport:
    """Validate that a parsed bill is usable for analysis."""

    try:
        document = load_parsed_bill(bill_dir)
    except ValueError as exc:
        return BillSmokeReport(title=None, node_count=0, clause_count=0, issues=[str(exc)])
    issues = smoke_issues(document)
    return BillSmokeReport(
        title=document.title,
        node_count=len(document.nodes),
        clause_count=count_clauses(document),
        issues=issues,
        warnings=document.issues,
    )


def smoke_issues(document: BillDocument) -> list[str]:
    """Return issues found in a parsed bill."""

    issues: list[str] = []
    if not document.nodes:
        issues.append("Parsed bill has no nodes.")
    if count_clauses(document) == 0:
        issues.append("Parsed bill has no clauses.")
    issues.extend(hierarchy_issues(document))
    return issues


def count_clauses(document: BillDocument) -> int:
    """Return the number of clause nodes."""

    return sum(1 for node in document.nodes.values() if node.level == "clause")


def hierarchy_issues(document: BillDocument) -> list[str]:
    """Return broken parent or child links."""

    issues: list[str] = []
    for node in document.nodes.values():
        if node.parent_id and node.parent_id not in document.nodes:
            issues.append(f"Missing parent for {node.id}: {node.parent_id}")
        for child_id in node.children_ids:
            if child_id not in document.nodes:
                issues.append(f"Missing child for {node.id}: {child_id}")
    return issues


def bill_smoke_passed(report: BillSmokeReport) -> bool:
    """Return whether a bill smoke report passed."""

    return not report.issues
