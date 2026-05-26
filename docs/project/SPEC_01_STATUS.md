# SPEC 01 Status

Status. Implementation complete for the deterministic mirror and resolver foundation.

Scope.

- GhaLII mirror for the 1992 Constitution and Ghana Acts.
- Akoma Ntoso XML parsing with HTML fallback.
- Local registry for mirrored Acts and the Constitution.
- Citation parsing and reference resolution for Acts, sections, and Constitution articles.
- CLI entry points for mirroring, refreshing, and local smoke verification.

Completed.

- Shared legal document schemas in `src/clauseguard/reference/schemas.py`.
- XML parser in `src/clauseguard/reference/parser_xml.py`.
- HTML fallback parser in `src/clauseguard/reference/parser_html.py`.
- Registry loading, writing, and lookup helpers.
- Citation parser and resolver.
- Polite GhaLII HTTP client with robots checks, retry handling, and request pacing.
- Mirror orchestration for the Constitution and Acts.
- Legislation index parser for discovering Act links.
- CLI wrappers under `scripts/`.
- Local smoke checker for registry, parsed documents, and resolver samples.

Validation.

- Unit tests cover parsers, registry behavior, citation parsing, resolver behavior, client behavior, mirror orchestration, CLI helpers, and smoke checks.
- Static checks are expected to pass with Ruff and mypy.
- The local smoke checker should be run after mirroring reference data.
- Audit hardening covers non-destructive registry updates, Constitution registry entries, duplicate node detection, safer HTML fallback parsing, bare Article citation resolution, and malformed XML date fallback.

Commands.

```powershell
python scripts\mirror_ghalii.py --target constitution
python scripts\mirror_ghalii.py --target act --number 769 --year 2008
python scripts\check_reference.py
```

Current repository note.

`docs/reference/ghana_acts/registry.json` may be empty in source control until a local mirror is run. In that state, `check_reference.py` is expected to fail with clear registry and unresolved-reference issues.

Step 3 gate.

Move to bill parsing only after `python scripts\check_reference.py` passes against the local mirrored corpus needed for the first bill analysis.
