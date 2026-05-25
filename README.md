# ClauseGuard

Evidence grounded legislative risk analysis for Ghana.

ClauseGuard reads bills, preserves clause hierarchy, and prepares evidence cards for analyst review. The system is designed for Ghanaian industry analysts who need to produce defensible position papers within days of a bill being published.

The project is not a legal opinion engine. It does not predict parliamentary outcomes. It surfaces evidence so a human analyst can decide.

## Repository Map

```text
docs/
  methodology/              Shared taxonomy, scoring, labelling, and evidence rules
  reference/                Fixed reference corpus, starting with the 1992 Constitution
  bills/                    Ministry, year, and bill level corpus folders
  reports/                  Public artefacts
src/clauseguard/            Future application package
frontend/                   Future human review interface
tests/                      Future tests aligned to package boundaries
scripts/                    Future corpus and maintenance scripts
data/                       Local generated data, labels, and vector stores
notebooks/                  Exploratory analysis
```

## Build Order

1. Lock methodology and assemble the corpus.
2. Parse bills into clause level JSON.
3. Index the Constitution and bill clauses.
4. Add risk classification and constitutional checks.
5. Build the human review interface.
6. Publish the NITA Bill launch report.

## Evidence Rule

No score appears without a bill excerpt and a constitutional excerpt. If retrieval is empty, the system must return insufficient evidence.
