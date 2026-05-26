# Step 4 Retrieval Status

Status. Initial deterministic lexical retrieval implemented.

Scope.

- Build scoped retrieval chunks for parsed bills, Constitution articles, and Act sections.
- Keep bill, Constitution, and Act citations in separate namespaces.
- Build local JSON lexical indexes.
- Search indexes with deterministic token matching and simple ranking.
- Return `insufficient evidence` when a search has no matches.
- Smoke-check index files before downstream analysis.

Completed.

- Retrieval chunk schema with `source_type`, `document_id`, `node_id`, text, heading, and page fields.
- Bill chunk builder from parsed bill JSON.
- Reference chunk builder from parsed Constitution and Act documents.
- Lexical tokenizer and index builder.
- Ranked lexical search.
- Index read/write helpers.
- Index smoke checker.
- CLI wrappers under `scripts/index_corpus.py`, `scripts/search_corpus.py`, and `scripts/check_index.py`.
- Unit tests for tokenisation, chunk scoping, ranking, storage, smoke checks, and CLI behavior.

Commands.

```powershell
python scripts\index_corpus.py bill docs\bills\mocdt\2025\nita_bill
python scripts\check_index.py data\indexes\bills\nita_bill_2025.json
python scripts\search_corpus.py data\indexes\bills\nita_bill_2025.json "digital services" --limit 3
python scripts\index_corpus.py references
```

Audit hardening.

- Indexes with no chunks or postings fail smoke checks.
- Missing index files fail clearly.
- Stopword-only searches return insufficient evidence.
- Search results carry fully scoped citations.
- NITA Bill index builds successfully with 464 chunks and zero index issues.

Current repository note.

The reference registry is empty in source control, so `python scripts\index_corpus.py references` should be run only after the reference mirror is populated and `python scripts\check_reference.py` passes.

Known limits.

- This is lexical retrieval, not semantic retrieval.
- Chroma/vector storage is still future work.
- Retrieval quality will improve when Constitution and Act reference mirrors are populated locally.
