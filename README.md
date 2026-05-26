# ClauseGuard

Evidence grounded legislative risk analysis for Ghana.

ClauseGuard reads bills, preserves clause hierarchy, resolves legal references, and prepares evidence cards for analyst review. The system is designed for Ghanaian industry analysts who need to produce defensible position papers within days of a bill being published.

The project is not a legal opinion engine. It does not predict parliamentary outcomes. It surfaces evidence so a human analyst can decide.

## Root Map

```text
.
|-- README.md                Project entry point
|-- pyproject.toml           Python project metadata
|-- docs/                    Governance, methodology, sources, references, bills, reports
|-- src/                     Future Python package
|-- tests/                   Tests aligned to package boundaries
|-- scripts/                 CLI and maintenance entry points
|-- frontend/                Future human review interface
|-- data/                    Local generated data and vector stores
`-- logs/                    Local mirror run logs
```

The root stays small on purpose. Living governance Markdown lives under `docs/governance/`. Source documents and specs live under `docs/project/sources/`. Legal source material lives under `docs/reference/`. Bills live under `docs/bills/`.

## Current Build Target

Step 4 is the active build target.

The SPEC 01 reference foundation and Step 3 bill parser are implemented. The current layer indexes parsed bill and reference text for deterministic retrieval.

It does not include risk classification, constitutional checks, API, frontend, or LLM calls.

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

- `docs/governance/` stores assistant rules, decisions, and capability notes.
- `docs/project/sources/` stores the playbook and source specs.
- `docs/methodology/` stores taxonomy, scoring, labelling, and evidence rules.
- `docs/reference/constitution_1992/` stores the Constitution reference corpus.
- `docs/reference/ghana_acts/` stores mirrored Acts of Parliament.
- `docs/bills/mocdt/2025/nita_bill/` stores the launch bill.
- `src/clauseguard/reference/` will hold the SPEC 01 mirror and resolver.
