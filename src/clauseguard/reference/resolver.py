"""Resolve legal citations against the local reference registry."""

from __future__ import annotations

from pathlib import Path

from clauseguard.reference.aliases import load_aliases
from clauseguard.reference.citation import node_id_from_ref, parse_citation
from clauseguard.reference.document_store import load_document
from clauseguard.reference.registry import load_registry
from clauseguard.reference.resolver_match import act_matches, constitution_entry
from clauseguard.reference.schemas import (
    AmbiguousMatch,
    Citation,
    LegalDocument,
    RegistryEntry,
    ResolutionReport,
    ResolvedReference,
    TextNode,
)

DEFAULT_ALIASES_PATH = Path("src/clauseguard/reference/aliases.yaml")
DEFAULT_REGISTRY_PATH = Path("docs/reference/ghana_acts/registry.json")


class ReferenceResolver:
    """Resolve legal citations using local parsed reference documents."""

    def __init__(
        self,
        registry_path: Path = DEFAULT_REGISTRY_PATH,
        aliases_path: Path = DEFAULT_ALIASES_PATH,
        repo_root: Path = Path("."),
    ) -> None:
        """Create a resolver from registry and alias files."""

        self.repo_root = repo_root
        self.entries = load_registry(registry_path)
        self.aliases = load_aliases(aliases_path)

    def resolve_act(self, citation: str) -> LegalDocument | None:
        """Resolve an Act citation to one local legal document."""

        matches = self._act_matches(parse_citation(citation))
        return load_document(matches[0], self.repo_root) if len(matches) == 1 else None

    def resolve_section(self, citation: str, section_ref: str) -> TextNode | None:
        """Resolve a section within an Act."""

        document = self.resolve_act(citation)
        if document is None:
            return None
        return document.nodes.get(node_id_from_ref("s", section_ref))

    def resolve_constitution_article(self, article_ref: str) -> TextNode | None:
        """Resolve an article within the Constitution."""

        entry = constitution_entry(self.entries)
        if entry is None:
            return None
        document = load_document(entry, self.repo_root)
        return document.nodes.get(node_id_from_ref("art", article_ref))

    def resolve_references(self, references: list[str]) -> ResolutionReport:
        """Bulk resolve citations into resolved, unresolved, and ambiguous groups."""

        report = ResolutionReport()
        for reference in references:
            self._add_resolution(reference, report)
        return report

    def _add_resolution(self, reference: str, report: ResolutionReport) -> None:
        """Resolve one reference and update a report."""

        citation = parse_citation(reference)
        matches = self._matches(citation)
        if not matches:
            report.unresolved.append(reference)
        elif len(matches) > 1:
            report.ambiguous.append(AmbiguousMatch(citation=reference, matches=matches))
        else:
            node = self._node_for(citation, matches[0])
            report.resolved.append(ResolvedReference(citation=reference, document=matches[0], node=node))

    def _matches(self, citation: Citation) -> list[RegistryEntry]:
        """Return matching registry entries for a citation."""

        if citation.is_constitution:
            entry = constitution_entry(self.entries)
            return [entry] if entry else []
        return self._act_matches(citation)

    def _act_matches(self, citation: Citation) -> list[RegistryEntry]:
        """Return Act entries matching a citation."""

        return act_matches(self.entries, self.aliases, citation)

    def _node_for(self, citation: Citation, entry: RegistryEntry) -> TextNode | None:
        """Return a node when a citation points to a section or article."""

        document = load_document(entry, self.repo_root)
        if citation.article_ref:
            return document.nodes.get(node_id_from_ref("art", citation.article_ref))
        if citation.section_ref:
            return document.nodes.get(node_id_from_ref("s", citation.section_ref))
        return None
