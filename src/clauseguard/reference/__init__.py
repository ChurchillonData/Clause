"""Reference corpus tools for ClauseGuard."""

from clauseguard.reference.parser_xml import parse_xml_document, parse_xml_file
from clauseguard.reference.schemas import LegalDocument, TextNode

__all__ = ["LegalDocument", "TextNode", "parse_xml_document", "parse_xml_file"]
