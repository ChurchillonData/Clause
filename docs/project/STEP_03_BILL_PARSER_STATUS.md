# Step 3 Bill Parser Status

Status. Initial production parser implemented.

Scope.

- Parse bill PDFs from the standard `docs/bills/<ministry>/<year>/<bill>/` folder layout.
- Preserve clause, subclause, paragraph, subparagraph, and schedule hierarchy.
- Produce clause-level JSON with stable IDs.
- Preserve PDF page numbers as fallback citations.
- Capture visible legal references such as Acts, sections of Acts, and Constitution Articles.
- Validate parsed bills before downstream retrieval and analysis.

Completed.

- PDF text extraction with `pdfplumber`.
- Deterministic text-to-hierarchy parser.
- Parsed bill schemas.
- Bill metadata loading.
- Parsed bill store.
- Bill folder parser and writer.
- Bill smoke checker.
- CLI wrappers under `scripts/parse_bill.py` and `scripts/check_bill.py`.
- Unit tests for hierarchy, page spans, references, duplicate IDs, missing parsed output, and CLI behavior.

Commands.

```powershell
python scripts\parse_bill.py docs\bills\mocdt\2025\nita_bill
python scripts\check_bill.py docs\bills\mocdt\2025\nita_bill
```

Audit hardening.

- Duplicate bill node IDs are preserved with deterministic suffixes and warnings instead of overwriting text.
- Preamble lines and duplicate bill numbering are recorded as parser warnings.
- Missing or invalid metadata fails clearly.
- Missing parsed JSON fails clearly in the smoke checker.
- Empty or unparseable text fails clearly.
- NITA Bill real-PDF audit parses clauses 1 through 104, one schedule, and passes with zero blocking issues.

Known limits.

- The parser is deterministic and layout-based. Very unusual PDFs may need fixture-driven parser improvements.
- Tables are not yet represented as structured table data.
- Schedules are captured as schedule nodes, but nested schedule-specific clause numbering may need future expansion after real examples are collected.
