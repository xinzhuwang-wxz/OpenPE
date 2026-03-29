# Arbiter Adjudication: Phase 4 (Projection)

## Input Reviews
- Domain Review: provided in reviewer summary (2A, 4B, 3C)
- Logic Review: provided in reviewer summary (2A, 5B, 3C)
- Methods Review: provided in reviewer summary (1A, 5B, 4C)

## Issue Adjudication Table

| ID | Finding | Domain | Logic | Methods | Adjudicated Category | Rationale |
|----|---------|--------|-------|---------|---------------------|-----------|
| 1  | Sensitivity baseline underground_disp=0.30 vs Scenario B mean=0.20 | A | A | A | **A** | Three-reviewer consensus. Code line 314 sets `underground_disp: 0.30` for the sensitivity baseline, but Scenario B (the stated baseline scenario) uses mean=0.20 (line 154). The tornado chart and sensitivity rankings are computed against an inconsistent baseline, invalidating the reported impact magnitudes and potentially the variable ranking. |
| 2  | Policy effect double-counted: OBS_2025 already contains the policy shift, yet net_policy is added again | A | -- | -- | **A** | Domain reviewer correctly identified this. Code line 194 sets `base = OBS_2025` (2,986 yuan, which already reflects any policy-induced reduction since the policy took effect in 2021). Line 214 then adds `net_policy * (1 + 0.02*t)` where `net_policy = LEVEL_SHIFT * pol_p * (1 - ug_d)`. In Scenario A (pol_p=0.8), this subtracts an additional ~386 yuan that is already embedded in the observed value. This is a structural model error. |
| 3  | Formula-code mismatch / notation ambiguity; 2%/yr policy deepening hidden | -- | A | B | **B** | The formula in PROJECTION.md (line 62) does contain the `(1 + 0.02t)` term, so it is not truly "hidden" -- it is present in the equation. However, the 2% deepening rate has no empirical justification documented anywhere. The formula's notation is also somewhat misleading (additive presentation vs. the code's structure). Downgraded from A to B because the term is visible in the formula, but the lack of justification for the 2% value is a real gap. |
| 4  | Clipped Gaussian used for underground displacement; PROJECTION.md states "wide uniform prior (0-60%)" | -- | -- | B | **A (upgraded)** | PROJECTION.md line 41 explicitly says "wide uniform prior (0-60%)" but code line 184 uses `np.clip(np.random.normal(...), 0, 1)`. For Scenario B, this is Normal(0.2, 0.50) clipped to [0,1] -- heavily right-skewed and concentrated near zero, not uniform at all. This is a direct contradiction between the documented methodology and the implementation, and it affects the underground displacement contribution in all scenarios. The mislabeling of the distribution is a Category A finding because it misrepresents the model to the reader. |
| 5  | 30% demographic dampening factor unjustified | B | -- | -- | **B** | Code line 207 uses `demo_d * 0.3` to dampen the demographic decline's pass-through to per-capita spending. This 0.3 factor appears nowhere in the documentation or literature citations. Demographic decline ranked 2nd in sensitivity; an unjustified dampening factor directly affects a high-impact parameter. |
| 6  | No external validation of projections | B | -- | -- | **B** | No comparison to World Bank, IMF, or Chinese government forecasts for education spending or related macroeconomic parameters. For a projection exercise, some external anchoring is expected. |
| 7  | Scenario conditional probabilities sum to 85-115% (ranges overlap) | -- | B | -- | **C** | Probability ranges (15-25%, 45-55%, 25-35%) overlap and could sum to less or more than 100%. However, these are explicitly labeled as ranges, not point estimates, and the document does not claim they must sum to exactly 100%. In practice this is a minor presentation issue -- the midpoints sum to 95%, which is reasonable given rounding. |
| 8  | Clipped Gaussian distributions truncate without renormalization | B | B | -- | **B** | Code lines 182-185 clip Normal draws for policy_persistence ([-0.2, 1.5]) and underground_disp ([0, 1.0]) without renormalizing. This biases the effective distribution means and variances. For underground_disp in Scenario B (Normal(0.2, 0.50) clipped [0,1]), approximately 34% of draws are clipped at 0, shifting the effective mean upward from the stated 0.20. |
| 9  | CV=0.16 classified as Fork-dependent despite threshold being CV>0.50 | -- | B | -- | **B** | The Phase 4 CLAUDE.md spec defines Fork-dependent as CV > 0.50. PROJECTION.md acknowledges CV=0.16 is below this threshold but classifies as Fork-dependent anyway using qualitative arguments (growing divergence, limited CI overlap, identifiable fork condition). The qualitative reasoning is not unreasonable -- the Robust criterion (CV < 0.15) is barely missed, and the within-scenario uncertainty is large. But this is a deviation from the stated methodology that should be documented more rigorously, or the classification should be adjusted to "borderline Robust/Fork-dependent." |
| 10 | Counterfactual value mismatch | -- | B | -- | **C** | Logic reviewer flagged a mismatch in counterfactual values. The ITS counterfactual at 2030 is computed as `PRE_POLICY_MEAN + PRE_TREND * (2030-2016) = 2038 + 183*14 = 4600`, reported as 4,596 yuan. The ~4 yuan difference is negligible rounding. |
| 11 | Monte Carlo not vectorized (uses row-by-row loop) | -- | B | B | **C** | Code uses a Python for-loop over 10,000 iterations (line 178) and a nested loop over years (line 195). This is a code quality issue (slow), not a correctness issue. The results are unaffected. |
| 12 | No convergence diagnostic for MC | -- | -- | B | **C** | Methods reviewer noted absence of convergence checks (e.g., running mean stability). With 10,000 iterations for a 6-parameter model, convergence is virtually guaranteed. Would be good practice to include but does not affect results. |
| 13 | Systematic uncertainty not propagated to MC | -- | -- | B | **B** | The MC simulation uses only `STAT_UNC` (127 yuan) for the noise term (line 217), not `TOTAL_UNC` (284 yuan) which includes systematics. PROJECTION.md line 43 notes systematic uncertainty is 80% of total. Scenario parameter variation captures some systematic effects indirectly, but the noise term is underestimated by a factor of ~2x. |

## EP Adjudication

1. **EP Assessment Reasonableness**: The EP decay schedule is reasonable given the CORRELATION classification. Starting from EP=0.20 and applying squared multipliers for CORRELATION edges is consistent with the Phase 4 CLAUDE.md guidance. The rapid decay (below soft truncation by year 1) correctly reflects the weak empirical foundation.

2. **Truncation Decision Validity**: Chain-level joint EPs are all below hard truncation (0.05), and the document correctly states no chain-level causal projections are supportable. This is appropriate given Phase 3 results.

3. **Label Consistency**: The document correctly inherits CORRELATION and HYPOTHESIZED labels from Phase 3. HYPOTHESIZED edges contribute only to scenario spread (underground displacement, public spending crowding-in). Consistent.

4. **Confidence Band Appropriateness**: The confidence bands are somewhat narrow because noise uses only STAT_UNC rather than TOTAL_UNC (Issue #13). Combined with the double-counting issue (#2), the central projections and band widths need recalculation. Bands may be both biased (double-counting) and too narrow (missing systematic noise).

5. **Causal DAG Validity**: The projection model is a simplified reduced-form model rather than a full DAG propagation, which is appropriate given that all chains are below hard truncation. The model structure is defensible in principle, though the double-counting error (#2) is a structural flaw.

## Adjudicated Category A Issues

### A1: Sensitivity baseline underground_disp mismatch (consensus: Domain, Logic, Methods)
The sensitivity analysis uses `underground_disp=0.30` as the baseline value (code line 314), while Scenario B -- explicitly called the baseline scenario -- defines `underground_disp` with mean 0.20 (code line 154). The tornado chart, variable ranking table, and all sensitivity impact figures in PROJECTION.md are computed against this inconsistent baseline. The sensitivity ranking could change (underground displacement's impact of 64 yuan may be under- or over-estimated). **Fix**: Set `baseline_params["underground_disp"] = 0.20` to match Scenario B, rerun sensitivity analysis, and update PROJECTION.md tables.

### A2: Policy effect double-counted
The projection model starts from `OBS_2025` (the 2025 observed value of 2,986 yuan), which already reflects any policy-induced spending reduction since the Double Reduction policy took effect in July 2021. The model then adds `net_policy = LEVEL_SHIFT * pol_p * (1 - ug_d)` as an additional level shift. In Scenario A (pol_p=0.8, ug_d~0), this subtracts an additional ~386 yuan from a base that already incorporates the policy's effect. This double-counts the policy contribution and biases Scenario A projections downward. The correct approach is either: (a) start from a counterfactual base and apply the policy shift, or (b) start from the observed base and model only *changes* from the current policy state. **Fix**: Restructure the projection model to avoid double-counting. The simplest fix is to make `net_policy` represent only the *incremental* change in policy effect from the 2025 baseline (e.g., deepening or weakening), not the full level shift.

### A3: Underground displacement distribution mislabeled (upgraded from B)
PROJECTION.md line 41 states the underground displacement parameter uses a "wide uniform prior (0-60%)." The code uses `np.clip(np.random.normal(mean, std), 0, 1)` -- a clipped Normal distribution. For Scenario B, this is Normal(0.2, 0.50) clipped to [0,1], which is heavily concentrated near zero with a long right tail -- fundamentally different from a Uniform(0, 0.6). The documented methodology does not match the implementation. **Fix**: Either change the code to use a uniform distribution as documented, or update PROJECTION.md to accurately describe the distributions used. Given the parameter's acknowledged unmeasurability, a uniform prior may be more defensible.

## Adjudicated Category B Issues

| ID | Finding | Status |
|----|---------|--------|
| B1 | 2%/yr policy deepening rate unjustified | Blocks -- must provide empirical or theoretical justification, or remove the deepening term |
| B2 | 30% demographic dampening unjustified | Blocks -- must cite a source or provide reasoning for the 0.3 pass-through factor |
| B3 | Clipped Gaussians not renormalized | Blocks -- biases effective means; must either renormalize or document the effective distributions |
| B4 | No external validation | Accepted -- would strengthen the analysis but not strictly required given the acknowledged speculative nature |
| B5 | CV=0.16 classified as Fork-dependent despite CV<0.50 threshold | Blocks -- must either adjust classification or formally document the departure from spec criteria with quantitative justification |
| B6 | Systematic uncertainty not propagated to MC noise | Blocks -- noise term uses STAT_UNC (127) instead of TOTAL_UNC (284); underestimates projection uncertainty |

## Adjudicated Category C Issues

- C1: Scenario conditional probabilities sum to 85-115% (presentation issue)
- C2: Counterfactual value ~4 yuan rounding difference (negligible)
- C3: Monte Carlo not vectorized (performance, not correctness)
- C4: No convergence diagnostic (good practice but 10K iterations sufficient)

## Regression Assessment

No regressions from earlier phases detected. The Phase 3 EP values, classifications, and uncertainty estimates are correctly inherited. The issues identified are all Phase 4-local problems in the projection model construction and documentation.

## Verdict Rationale

Three Category A issues remain after adjudication:

1. **Sensitivity baseline mismatch** (three-reviewer consensus) -- invalidates the sensitivity analysis tables and tornado chart.
2. **Policy effect double-counting** -- structural model error that biases scenario projections, particularly Scenario A.
3. **Distribution mislabeling** -- the documented methodology does not match the code, violating the Phase 4 non-negotiable rule that all assumptions must be explicit.

Additionally, four of six Category B issues are blocking: the unjustified 2%/yr deepening, the unjustified 30% demographic dampening, the unrenormalized clipped distributions, and the underpropagated systematic uncertainty. These collectively represent significant gaps in the projection model's justification and uncertainty quantification.

All issues are fixable within Phase 4 without requiring changes to upstream phases. The fixes are well-defined: correct the baseline parameter, restructure the policy effect to avoid double-counting, align documented and implemented distributions, justify or remove the 2% and 30% factors, propagate systematic uncertainty, and reconcile the endgame classification with spec criteria.

DECISION: ITERATE
