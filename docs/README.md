# Docs

The `docs` folder is the methodological and legal backbone of ClauseGuard.

## Map

```text
docs/
├── project/                 Playbook, source PDFs, and build specs
├── methodology/             Taxonomy, scoring, labelling, and evidence rules
├── reference/               Constitution and Acts of Parliament
├── bills/                   Bill corpus by ministry, year, and bill
└── reports/                 Public outputs
```

## Rules

- Keep source specs in `docs/project/`.
- Keep the Constitution and Acts in `docs/reference/`.
- Keep bills under `docs/bills/<ministry>/<year>/<bill>/`.
- Keep public artefacts in `docs/reports/`.
- Do not edit generated article or section markdown by hand after the mirror exists.
