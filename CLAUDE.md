# CLAUDE

Working context for AI assistants operating on ClauseGuard.

## What This Project Is

ClauseGuard is an evidence grounded legislative risk analysis system for Ghana. It reads bills, splits them into clauses, classifies risks across eleven categories, and checks each clause against the 1992 Constitution of Ghana.

Every output is backed by a cited excerpt. The primary user is a mid level analyst at a Ghanaian industry association who has seven to fourteen days to produce a position paper on a newly gazetted bill.

## What This Project Is Not

It is not a legal opinion engine. It is not partisan. It does not predict parliamentary outcomes. It does not give advice.

It surfaces evidence. The human decides.

## Hard Rules

- Read `docs/methodology/01_taxonomy.md` before classifying anything.
- Read `DECISIONS.md` before suggesting an architectural change.
- Cite clause IDs as primary citations.
- Use page numbers only as fallback.
- Validate every constitutional article against `docs/reference/constitution_1992/articles/`.
- Preserve clause hierarchy in every output.
- Return insufficient evidence when retrieval is empty.
- Quote bill text verbatim in evidence cards.

## Coding Standards For Later

- Python 3.11.
- Type hints on every public function.
- `pdfplumber` for PDF extraction.
- `spaCy` for sentence boundaries.
- Chroma for local vectors.
- FastAPI for the API.
- Streamlit for the v1 review interface.
- LLM calls go through `src/clauseguard/analysis/llm.py`.
- Prompts live in `src/clauseguard/analysis/prompts/`.

No implementation exists yet. This repository currently contains the structure required by the playbook.
