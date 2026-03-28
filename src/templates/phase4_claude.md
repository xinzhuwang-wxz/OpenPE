# Phase 4: Inference

> Read `methodology/03-phases.md` → "Phase 4" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.
> Read `methodology/04-blinding.md` for the blinding protocol.

You are building the statistical model and computing results for a
**{{analysis_type}}** analysis.

**Start in plan mode.** Before writing any code, produce a plan: what
systematics you will evaluate, what validation checks you will run, what
the artifact structure will be. Execute after the plan is set.

## Output artifacts and flow

**Both measurements and searches follow the same 4a → 4b → 4c structure:**
- **4a:** Statistical analysis — systematics, expected results. Artifact: `INFERENCE_EXPECTED.md`. No AN draft here.
- **4b:** 10% data validation. Compare to expected. Write full AN draft with 10% results. Review + PDF render. Human gate after review passes.
- **4c:** Full data. Compare to 10% and expected. Update AN with full results.

| Sub-phase | Artifact | Review |
|-----------|----------|--------|
| 4a | `exec/INFERENCE_EXPECTED.md` | 4-bot |
| 4b | `exec/INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md` | 4-bot → human gate |
| 4c | `exec/INFERENCE_OBSERVED.md` | 1-bot |

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 4
- Technique-specific requirements: `methodology/03-phases.md` → Phase 4 sub-phase descriptions
- Blinding: `methodology/04-blinding.md`
- Review protocol: `methodology/06-review.md` → §6.2 (4-bot / 1-bot), §6.4
- Goodness-of-fit: `methodology/03-phases.md` → Phase 4 GoF requirements
- Plotting: `methodology/appendix-plotting.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Systematic evaluation methods used in reference analyses
2. Published measurements for comparison (use `compare_measurements` for
   cross-experiment results)
3. Theory predictions or MC generator comparisons for the observable

Cite sources in the artifact.

## Applicable conventions

{{conventions_files}}

Re-read these before finalizing systematics.

## Key requirements

These are the critical items for Phase 4. See
`methodology/03-phases.md` → Phase 4 for full details.

- **Systematic completeness table.** Compare your implemented sources
  against the reference analyses from Phase 1 and the applicable
  `conventions/` files (see root CLAUDE.md → Conventions for which files
  apply). Format: `| Source | Conventions | Ref 1 | Ref 2 | This | Status |`.
  Any MISSING source without justification is a blocker. In particular,
  any source listed in the Phase 1 conventions enumeration as "Will
  implement" that is absent here is Category A (must resolve before
  advancing).
- **Statistical model construction.** Build a binned likelihood with all
  samples, Asimov data (pseudo-data generated under the background-only or
  nominal hypothesis), and systematic terms as nuisance parameters (NPs —
  parameters that encode systematic uncertainties in the fit). Validate:
  NP pulls small, fit converges, results physically sensible.
- **Fit validation.** Signal injection tests (searches) or closure tests
  (measurements) to confirm the model recovers known inputs.
- **Goodness-of-fit.** Report **both** chi2/ndf (quick assessment) **and**
  toy-based p-value using the saturated model GoF statistic (the saturated
  model treats each bin as an independent parameter — standard reference in
  pyhf/HistFactory). For pure counting extractions without a binned fit,
  use chi2 across bins or subperiods instead. chi2/ndf ~ 1 is good; >>1
  indicates mismodeling; <<1 indicates overestimated uncertainties.
- **Expected results on Asimov/MC only.** Phase 4a results must come from
  pseudo-data — never real data.
- **MC coverage must match data.** Do not derive MC-dependent quantities
  (efficiencies, corrections, scale factors) for data-taking periods that
  lack corresponding MC simulation. If MC covers only one period, either
  restrict the measurement to that period or justify (with evidence) that
  the MC is applicable to other periods. Silently extrapolating MC-derived
  corrections to uncovered periods underestimates uncertainties.
- **Covariance matrix (measurements).** Full bin-to-bin covariance
  (statistical + each systematic + total) in the artifact and as
  machine-readable files.
- **Theory comparison (measurements).** Compare to at least one theory
  prediction or MC generator using the full covariance. If none available,
  justify and compare to published measurements.

**For extraction measurements:** read `conventions/extraction.md` for
additional required checks (independent closure test, parameter sensitivity
table, operating point stability, per-subperiod consistency, 10% diagnostic
sensitivity). These are technique-specific requirements defined in the
conventions file — do not skip them.

## Review

**4-bot review** (4a, 4b) / **1-bot review** (4c) — see `methodology/06-review.md`
for protocol. Write findings to `review/REVIEW_NOTES.md`.
