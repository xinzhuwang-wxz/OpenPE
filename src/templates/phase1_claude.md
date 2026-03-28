# Phase 1: Strategy

> Read `methodology/03-phases.md` → "Phase 1" for full requirements.

You are developing the analysis strategy for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any code or prose, produce a plan:
what literature you will query, what samples you expect, what the artifact
structure will be. Execute after the plan is set.

## Output artifact

`exec/STRATEGY.md` — analysis strategy with physics motivation, sample
inventory, selection approach, systematic plan, and technique selection.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 1
- Review protocol: `methodology/06-review.md` → §6.2 (4-bot), §6.4
- Artifacts: `methodology/05-artifacts.md`

## RAG queries (mandatory)

Before writing the strategy, query the experiment corpus (via MCP tools):
1. `search_lep_corpus`: prior measurements of the same or similar observables
2. `search_lep_corpus`: standard systematic sources for this analysis technique
3. `compare_measurements`: cross-experiment results if applicable
4. `get_paper`: drill into each reference analysis identified

Cite all retrieved sources in the artifact (paper ID + section).

## Required deliverables

- Physics motivation and observable definition
- Sample inventory (data + MC)
- Selection approach with justification
- Systematic uncertainty plan
- Literature review from RAG corpus
- **Technique selection** — determine the analysis technique (unfolding,
  template fit, etc.) and justify the choice. This determines which
  technique-specific requirements apply in later phases.

## Applicable conventions

{{conventions_files}}

Read these before writing the systematic plan.

## Key requirements

These are the critical actionable items for Phase 1. See
`methodology/03-phases.md` → Phase 1 for full details.

- **Corpus queries are mandatory.** Query the experiment corpus before
  writing anything — prior measurements, standard systematics, reference
  analyses. Cite all retrieved sources.
- **Enumerate backgrounds.** Classify each as irreducible, reducible, or
  instrumental. Estimate relative importance (order of magnitude is fine).
- **Define discriminating variables.** Identify the variable(s) for final
  statistical interpretation (invariant mass, BDT score, event shape, etc.).
- **Systematic plan with conventions enumeration.** Read the applicable
  `conventions/` files listed above. For every required source listed, state
  "Will implement" or "Not applicable because [reason]." This enumeration
  is binding — Phase 4a reviews against it. Silent omissions are Category A
  (must-resolve findings that block advancement — see review protocol).
- **Reference analysis table.** Identify 2-3 published analyses closest in
  technique/observable. Tabulate their systematic programs. This table is a
  binding input to later reviews.

**For measurements additionally:**
- Define the observable(s) and their physical interpretation precisely.
- Identify the correction/unfolding strategy and its required inputs.
- Survey prior measurements — published data points become the primary
  validation target in Phase 4.
- Identify theory predictions or MC generators for comparison.

## Review

**4-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
