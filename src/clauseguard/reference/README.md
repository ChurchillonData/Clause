# Reference Mirror And Resolver

Status. SPEC 01 implementation started.

This package will implement SPEC 01.

Responsibilities.

- Mirror the 1992 Constitution and current Ghana Acts from GhaLII.
- Prefer Akoma Ntoso XML and fall back to HTML only when XML is unavailable.
- Parse legal documents into shared `LegalDocument` and `TextNode` structures.
- Write article and section markdown files for human review.
- Maintain a local registry of mirrored Acts.
- Resolve references such as `Act 769`, `NCA Act`, `section 12 of Act 769`, and `Article 19(2)(d)`.

Current modules.

- `schemas.py`
- `parser_xml.py`
- `parser_html.py`
- `registry.py`
- `citation.py`
- `resolver.py`

Planned modules.

- `mirror.py`
- `ghalii_client.py`
- `logging.py`

The spec names `src/lexlens/reference/`. This repo uses `src/clauseguard/`, so the package path is `src/clauseguard/reference/`.

The first implemented slices define the shared legal document schemas and parse XML or fallback HTML into those schemas.
