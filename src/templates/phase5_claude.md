# Phase 5: Documentation

> Read `methodology/analysis-note.md` for the full AN specification.
> Read `methodology/03-phases.md` → "Phase 5" for phase requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/appendix-checklist.md` for the review checklist.

You are producing the final analysis note for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any prose, produce a plan: the AN
section structure, which figures go where, which results tables are needed.
Execute after the plan is set.

## Output artifact

`exec/ANALYSIS_NOTE.md` — publication-quality analysis note in pandoc-compatible
markdown.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 5
- Review protocol: `methodology/06-review.md` → §6.2 (5-bot), §6.4
- Plotting: `methodology/appendix-plotting.md`
- Checklist: `methodology/appendix-checklist.md`

## Pre-review gate

Before submitting for review, these must succeed:
1. `pixi run all` — full analysis chain reproduces from scratch
2. `pixi run build-pdf` — PDF compiles with all figures rendering

If either fails, fix it before requesting review.

## Analysis note structure

The AN must be **pandoc-compatible markdown** (see root CLAUDE.md for syntax).
See `methodology/analysis-note.md` for the full AN specification including
all 11 required sections, depth calibration, completeness test, and
bibliography requirements.

**Cross-references and citations (quick reference):**
- Figures: `![Caption](figures/name.pdf){#fig:name}` → `@fig:name`
- At sentence start: `Figure @fig:name`. Never `[-@fig:...]`.
- Citations: `[@key]` with `references.bib`. BibTeX must include `doi`,
  `url`, `eprint` fields. Use `unsrt`-style. Use `get_paper` for metadata.
- Tables: `{#tbl:name}` / `@tbl:name`. Equations: `{#eq:name}` / `@eq:name`.

## Key requirements

These are the critical items for the analysis note. See
`methodology/analysis-note.md` for full details.

- **The AN is the complete record — not an executive summary or a
  journal-length paper.** Every detail needed to reproduce the analysis
  from scratch must be in the note. If a reviewer has to read the code to
  understand a choice, the AN has a gap.
- **Depth calibration.** ~50-100 rendered pages for a typical analysis.
  Under 30 pages means detail is missing.
- **Per-systematic subsections.** Each systematic source gets its own
  subsection: description, method, impact figure, per-bin table.
- **Cross-checks with their results.** Each cross-check appears as a
  subsection within the relevant results section (not in a standalone
  "Cross-checks" section). If large (>2 pages), move to appendix.
- **Completeness test.** A physicist unfamiliar with the analysis should be
  able to read the AN alone and reproduce every number.
- **Machine-readable results.** `results/` directory with CSV/JSON for
  spectra, uncertainties, and covariance matrices.

## Figure setup

Symlink phase figures into `phase5_documentation/exec/figures/` so that
`![caption](figures/name.pdf)` references resolve correctly when pandoc
compiles the PDF. The `build_pdf.py` script collects figures automatically;
if setting up manually:
```bash
mkdir -p phase5_documentation/exec/figures
ln -sf ../../phase*/figures/*.pdf phase5_documentation/exec/figures/
```

## Building the PDF

Run `pixi run build-pdf` from the analysis root. This converts
`ANALYSIS_NOTE.md` to PDF via pandoc with xelatex, numbered sections,
TOC, and half-page-width figures.

**Never use an LLM to convert markdown to LaTeX.** Pandoc handles this.

## Review

**5-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
