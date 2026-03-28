# Phase 2: Exploration

> Read `methodology/03-phases.md` → "Phase 2" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.

You are exploring the data and MC samples for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before loading any data, produce a plan: which files
to inspect first, what variables to survey, what plots to make. Execute
after the plan is set.

## Output artifact

`exec/EXPLORATION.md` — sample inventory, data quality assessment, key
variable distributions, variable ranking, and preselection cutflow.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 2
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/11-coding.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Standard object definitions for this experiment (lepton ID, jet clustering, etc.)
2. Known data quality issues or detector effects relevant to the observables

Cite sources in the artifact.

## Data discovery

Expect to discover the data format at runtime. See
`methodology/03-phases.md` → Phase 2 "Data discovery" for the protocol
(metadata first → small slice → identify jagged structure → document schema).

## PDF build test (independent — can run in parallel)

Run a stub PDF build (`pixi run build-pdf`) to verify the toolchain. This
is independent of exploration and can be sub-delegated. See
`methodology/03-phases.md` → Phase 2 "PDF build test" for details.

## Key requirements

These are the critical actionable items for Phase 2. See
`methodology/03-phases.md` → Phase 2 for full details.

- **Inventory samples completely.** For each file: tree names, branch names
  and types, number of events, cross-section, luminosity. Document the
  schema — this is artifact content.
- **Validate data quality.** Check for pathologies: empty branches, outliers,
  discontinuities, unphysical values. Document all findings.
- **Apply standard object definitions.** Retrieve from the experiment corpus
  (RAG). Verify data/MC agreement in inclusive distributions.
- **Survey discriminating variables.** Produce signal vs. background
  distributions for all candidate kinematic variables. Rank by separation
  power (ROC AUC, significance improvement, or equivalent).
- **Establish baseline yields.** Report event counts after preselection for
  data and each MC sample, with cross-section normalization.
- **PDF build test.** Run a stub `pixi run build-pdf` at the end of this
  phase to catch toolchain issues early.

## Rules

- Prototype on small subsets (~1000 events). Do not process full data to
  "see what's there."
- Append findings to experiment_log.md as you go.

## Review

**Self-review.** Explicitly check: sample inventory complete? Data quality
checked? Experiment log updated? Distributions look physical?
Write findings to `review/REVIEW_NOTES.md`.
