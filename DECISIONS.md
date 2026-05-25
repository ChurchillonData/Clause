# DECISIONS

Architectural decision log for ClauseGuard.

Future decisions are appended. Decisions are not deleted. Superseded decisions stay visible.

## D-001 Project Name

Date. 2026-05-25

Decision. Name the project ClauseGuard.

Rationale. The name makes the clause level review task clear. It signals evidence, scrutiny, and protection without implying legal advice.

## D-002 Primary User

Date. 2026-05-25

Decision. Build v1 for a mid level analyst at a Ghanaian industry association.

Rationale. Industry analysts are repeat users with short deadlines and a direct need for cited position papers.

## D-003 Two Corpus Retrieval

Date. 2026-05-25

Decision. Index the 1992 Constitution once as the fixed reference corpus. Treat each bill as the variable target corpus.

Rationale. The Constitution is the spine of the analysis. Every clause level finding must be checked against constitutional text.

## D-004 Clause IDs As Primary Citations

Date. 2026-05-25

Decision. Use clause IDs as primary citations and page numbers as fallback.

Rationale. Clause hierarchy is more stable than PDF layout.

## D-005 Multi Label Classification

Date. 2026-05-25

Decision. A clause can have one or more risk categories.

Rationale. Real bills create overlapping risks. Forced single labels hide useful information.

## D-006 Separate Severity And Likelihood

Date. 2026-05-25

Decision. Severity and likelihood remain separate ordinal bands.

Rationale. A single score hides disagreements that analysts need to see.

## D-007 No Default Overall Bill Score

Date. 2026-05-25

Decision. Do not collapse a bill into one default score.

Rationale. Different stakeholders weight risk categories differently.

## D-008 Risk Categories

Date. 2026-05-25

Decision. Use eleven risk categories plus two cross cutting categories.

Rationale. The taxonomy reflects Ghanaian legislative and industry analysis needs.

## D-009 Human Review First

Date. 2026-05-25

Decision. The system proposes risks and citations. The analyst reviews, edits, or rejects before export.

Rationale. The domain is high stakes and the labelled dataset must mature before automation increases.

## D-010 Inter Rater Agreement Gate

Date. 2026-05-25

Decision. Compute Cohen kappa after the first thirty labelled clauses.

Rationale. If agreement is below 0.6, sharpen the taxonomy before scaling.

## D-011 Ministry Year Bill Structure

Date. 2026-05-25

Decision. Organise `docs/bills/` by ministry, year, then bill.

Rationale. Analysts ask ministry first, then year, then bill.

## D-012 Parser Preserves Hierarchy

Date. 2026-05-25

Decision. Parsed output must preserve clauses, sub clauses, schedules, and cross references.

Rationale. Clause level citations lose meaning if hierarchy is flattened.

## D-013 Methodology Before Frontend

Date. 2026-05-25

Decision. Lock methodology and parsing before building the interface.

Rationale. The project value depends on defensible evidence, not screen polish.

## D-014 Chroma Local

Date. 2026-05-25

Decision. Use Chroma locally for vector storage.

Rationale. The expected corpus is small enough for local storage and should not require cloud vector infrastructure.

## D-015 NITA Bill Launch Artefact

Date. 2026-05-25

Decision. Use the National Information Technology Authority Bill, 2025 as the first public report.

Rationale. It is timely, sector relevant, and suited to clause cited analysis.

## D-016 Non Partisan Stance

Date. 2026-05-25

Decision. Keep the project non partisan at the project level.

Rationale. Trust matters more than persuasion in public analysis of active bills.
