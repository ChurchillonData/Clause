"""Mirror legal reference documents into the local corpus."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from clauseguard.reference.ghalii_client import GhaliiClient, GhaliiClientError
from clauseguard.reference.mirror_log import log_event
from clauseguard.reference.mirror_markdown import write_node_markdown
from clauseguard.reference.mirror_paths import act_dir, constitution_dir
from clauseguard.reference.parser_html import parse_html_document
from clauseguard.reference.parser_xml import parse_xml_document
from clauseguard.reference.registry import write_registry
from clauseguard.reference.schemas import LegalDocument, RegistryEntry

CONSTITUTION_XML_URL = "/akn/gh/act/1992/constitution/eng@.xml"


def mirror_constitution(client: GhaliiClient, repo_root: Path, log_path: Path) -> LegalDocument:
    """Fetch, parse, and write the Constitution mirror."""

    output_dir = constitution_dir(repo_root)
    raw_path = output_dir / "raw.xml"
    xml_text = fetch_if_needed(client, CONSTITUTION_XML_URL, raw_path, log_path)
    document = parse_xml_document(xml_text, client.absolute_url(CONSTITUTION_XML_URL), "constitution")
    write_document(document, output_dir, "articles", log_path)
    return document


def mirror_act(
    client: GhaliiClient,
    repo_root: Path,
    year: int,
    act_number: int,
    log_path: Path,
) -> RegistryEntry:
    """Fetch, parse, and write one Act mirror."""

    xml_url = f"/akn/gh/act/{year}/{act_number}/eng@.xml"
    html_url = f"/akn/gh/act/{year}/{act_number}"
    source_text, source_url, raw_name = fetch_act_source(client, xml_url, html_url, log_path)
    document = parse_act_source(source_text, source_url, raw_name)
    output_dir = act_dir(repo_root, act_number, document.title, document.year)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / raw_name).write_text(source_text, encoding="utf-8")
    write_document(document, output_dir, "sections", log_path)
    return registry_entry(document, output_dir)


def fetch_act_source(
    client: GhaliiClient,
    xml_url: str,
    html_url: str,
    log_path: Path,
) -> tuple[str, str, str]:
    """Fetch XML for an Act and fall back to HTML on XML failure."""

    try:
        text = client.get_text(xml_url)
        log_event(log_path, "fetch", url=client.absolute_url(xml_url), format="xml")
        return text, client.absolute_url(xml_url), "raw.xml"
    except GhaliiClientError:
        text = client.get_text(html_url)
        log_event(log_path, "fetch", url=client.absolute_url(html_url), format="html")
        return text, client.absolute_url(html_url), "raw.html"


def fetch_if_needed(client: GhaliiClient, url: str, path: Path, log_path: Path) -> str:
    """Return cached text or fetch it when no local raw file exists."""

    if path.exists():
        log_event(log_path, "cache_hit", path=str(path))
        return path.read_text(encoding="utf-8")
    text = client.get_text(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    log_event(log_path, "fetch", url=client.absolute_url(url), path=str(path))
    return text


def parse_act_source(source_text: str, source_url: str, raw_name: str) -> LegalDocument:
    """Parse Act source text according to its raw source type."""

    if raw_name.endswith(".xml"):
        return parse_xml_document(source_text, source_url, "act")
    return parse_html_document(source_text, source_url, "act")


def write_document(document: LegalDocument, output_dir: Path, node_dir: str, log_path: Path) -> None:
    """Write parsed JSON and markdown node files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    parsed_path = output_dir / "parsed.json"
    parsed_path.write_text(document.model_dump_json(indent=2) + "\n", encoding="utf-8")
    write_node_markdown(document, output_dir / node_dir)
    log_event(log_path, "write", path=str(parsed_path), title=document.title)


def registry_entry(document: LegalDocument, output_dir: Path) -> RegistryEntry:
    """Create a registry entry for one mirrored Act."""

    return RegistryEntry(
        doc_type=document.doc_type,
        act_number=document.act_number,
        year=document.year,
        title=document.title,
        short_title=document.short_title,
        status=document.status,
        file_path=str(output_dir / "parsed.json"),
        content_hash=document.content_hash,
        fetched_at=document.fetched_at,
    )


def write_mirror_registry(entries: list[RegistryEntry], repo_root: Path) -> None:
    """Write the Acts registry for mirrored documents."""

    write_registry(entries, repo_root / "docs" / "reference" / "ghana_acts" / "registry.json")


def default_log_path(repo_root: Path) -> Path:
    """Return a timestamped mirror log path."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return repo_root / "logs" / f"mirror_run_{timestamp}.jsonl"
