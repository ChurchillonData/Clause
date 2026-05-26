# SKILLS

Capability map for ClauseGuard.

Each capability links the intended demonstration to repository paths and decisions.

## Domain Grounded RAG

Demonstrated by a fixed Constitution corpus and a variable bill corpus.

Paths.

- `src/clauseguard/retrieval/`
- `docs/reference/constitution_1992/`

Decision. D-003

## Hierarchical Legal Parsing

Demonstrated by clause level JSON that preserves clauses, sub clauses, schedules, and cross references.

Paths.

- `src/clauseguard/parsing/`
- `docs/bills/mocdt/2025/nita_bill/parsed.json`

Decisions. D-004, D-012

## Multi Label Risk Classification

Demonstrated by eleven risk categories, two cross cutting categories, and inter rater agreement.

Paths.

- `src/clauseguard/analysis/`
- `src/clauseguard/eval/`
- `docs/methodology/04_labelling_guide.md`

Decisions. D-005, D-010

## Transparent Ordinal Scoring

Demonstrated by separate severity and likelihood bands.

Paths.

- `docs/methodology/03_scoring.md`
- `frontend/`

Decisions. D-006, D-007

## Constitutional Checks With Validation

Demonstrated by article validation before any constitutional citation is shown.

Paths.

- `src/clauseguard/analysis/validators/`
- `src/clauseguard/analysis/prompts/`
- `docs/reference/constitution_1992/articles/`

Decision. D-003

## Evidence First Output

Demonstrated by evidence cards built from verbatim bill excerpts and constitutional excerpts.

Paths.

- `src/clauseguard/evidence/`
- `docs/methodology/05_evidence_format.md`
- `docs/bills/mocdt/2025/nita_bill/evidence/`

Decision. D-009

## Human Review Workflow

Demonstrated by analyst confirmation before export.

Paths.

- `src/clauseguard/api/`
- `frontend/`
- `src/clauseguard/eval/`

Decision. D-009

## Multi Ministry Repository Design

Demonstrated by the `docs/bills/` ministry, year, and bill structure.

Paths.

- `docs/bills/`
- `docs/bills/mocdt/2025/nita_bill/metadata.yaml`
- `scripts/`

Decision. D-011

## Legal Reference Resolution

Demonstrated by the planned GhaLII mirror and resolver layer.

Paths.

- `src/clauseguard/reference/`
- `docs/reference/ghana_acts/`
- `tests/reference/`

Spec. SPEC 01
