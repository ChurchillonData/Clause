# ClauseGuard

Evidence grounded legislative risk analysis for Ghana.

ClauseGuard reads bills, preserves clause hierarchy, resolves legal references, and prepares evidence cards for analyst review. The system is designed for Ghanaian industry analysts who need to produce defensible position papers within days of a bill being published.

The project is not a legal opinion engine. It does not predict parliamentary outcomes. It surfaces evidence so a human analyst can decide.

## Root Map

```text
.
├── CLAUDE.md                AI assistant rules and project constraints
├── DECISIONS.md             Architectural decision log
├── SKILLS.md                Capability map for the portfolio and repo
├── docs/                    Methodology, legal references, bills, reports, specs
├── src/                     Future Python package
├── tests/                   Tests aligned to package boundaries
├── scripts/                 CLI and maintenance entry points
├── frontend/                Future human review interface
├── data/                    Local generated data and vector stores
├── notebooks/               Exploration only
└── logs/                    Local mirror run logs
```

The root stays small on purpose. Source documents and specs live under `docs/project/`. Legal source material lives under `docs/reference/`. Bills live under `docs/bills/`.

## Current Build Target

SPEC 01 is the active build target.

It covers two deterministic components:

- GhaLII mirror for the 1992 Constitution and Acts of Parliament.
- Reference resolver for citations such as `Act 769`, `NCA Act`, `section 12 of Act 769`, and `Article 19(2)(d)`.

It does not include the bill parser, risk classifier, API, frontend, or LLM calls.

## Build Order

1. Lock methodology and assemble the corpus.
2. Mirror GhaLII reference materials and resolve Act and Constitution citations.
3. Parse bills into clause level JSON.
4. Index the Constitution and bill clauses.
5. Add risk classification and constitutional checks.
6. Build the human review interface.
7. Publish the NITA Bill launch report.

## Evidence Rule

No score appears without a bill excerpt and a constitutional excerpt. If retrieval is empty, the system must return insufficient evidence.

## Key Paths

- `docs/project/` stores the playbook and build specs.
- `docs/methodology/` stores taxonomy, scoring, labelling, and evidence rules.
- `docs/reference/constitution_1992/` stores the Constitution reference corpus.
- `docs/reference/ghana_acts/` stores mirrored Acts of Parliament.
- `docs/bills/mocdt/2025/nita_bill/` stores the launch bill.
- `src/clauseguard/reference/` will hold the SPEC 01 mirror and resolver.
