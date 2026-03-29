# Arbiter Adjudication: Phase 3 (Causal Analysis)

## Input Reviews
- Domain Review: `phase3_analysis/review/DOMAIN_REVIEW.md`
- Logic Review: provided as summary (1A + 2A, 5B, 3C)
- Methods Review: provided as summary (2A, 5B, 4C)

---

## Issue Adjudication Table

| ID | Finding | Domain | Logic | Methods | Adjudicated Category | Rationale |
|----|---------|--------|-------|---------|---------------------|-----------|
| 1 | "Policy -> Industry Collapse" labeled DATA_SUPPORTED without running refutation tests | A | A | -- | **A** | Confirmed in artifact (line 176 of ep_update script: "No refutation needed") and conventions (causal_inference.md line 10-11: "every causal claim must survive at least 3 refutation tests"). The CLAUDE.md Phase 3 non-negotiable rule 1 is explicit: "An edge classified as DATA_SUPPORTED without all 3 refutation tests passing is a Category A finding. No exceptions." Literature evidence alone cannot produce DATA_SUPPORTED; it should be LITERATURE_SUPPORTED or at most CORRELATION. Two reviewers agree; clear protocol violation. |
| 2 | "BSTS" is actually OLS with income covariate -- mislabeled throughout | -- | -- | A | **A** | Confirmed by reading step3_bsts_analysis.py. Lines 97-102: "Method 1: Simple approach -- fit linear model on pre-period, predict post / Using OLS with income as predictor for simplicity given n=4". The UnobservedComponents model is attempted (lines 128-153) but wrapped in try/except and its results are not used for the reported estimates. The returned values (mean_effect, boot_ci_90) come entirely from the OLS path. Calling this "BSTS" throughout ANALYSIS.md (Section 2, Section 3.3.3, Section 7) is a material mislabeling that misleads about the secondary method's sophistication. |
| 3 | HYPOTHESIZED edges bypass mechanical truth update formula -- 3 edges with EP increases despite HYPOTHESIZED or NOT_TESTED classification | -- | A | -- | **B** | Examined the EP propagation table. The three edges in question: (a) "Policy -> Underground Market" 0.20 -> 0.21, (b) "Underground -> Higher Prices" 0.10 -> 0.12, (c) "Competitive Pressure -> Inelastic Demand" 0.40 -> 0.42. The ep_update script (line 148-152) shows the default path is "no change" for untested edges, so these small increases come from relevance adjustments only (truth unchanged). The CLAUDE.md rule says "CORRELATION: truth = phase1_truth (unchanged)" and "HYPOTHESIZED: truth = min(0.3, phase1_truth - 0.1)". For edges classified HYPOTHESIZED (a, b), truth should decrease, not stay constant. Edge (c) is labeled CORRELATION but was not tested -- this is a label consistency issue. However, the magnitude is small (0.01-0.02 EP change) and does not alter any truncation decision or DAG classification. Downgraded to B because the material impact on conclusions is negligible, but the protocol violation is real and must be corrected. |
| 4 | Jackknife leave-one-out substituted for required "data subset" refutation test | -- | B | A | **A** | Confirmed by reading step5_refutation.py (lines 175-209). The code implements jackknife leave-one-out (drop one year at a time), NOT the convention-required "data subset" test (randomly drop 20-30% of observations). With only 9 observations, jackknife drops 1 observation (11%), while the convention requires 20-30%. More critically, jackknife is deterministic and tests sensitivity to individual observations, while data subset tests stability under random subsampling. The conventions file (causal_inference.md line 10-11) explicitly names "data subset" as one of the three required tests. The CLAUDE.md refutation table (Section 3.3.4) specifies: "Randomly drop 20-30% of observations and re-estimate." This substitution means the refutation battery is incomplete, and the CORRELATION classification for "Policy -> Aggregate Spending" rests on only 2/3 valid tests (placebo plus random common cause). Upgrading from Methods B to A because (a) two reviewers flagged it and (b) it directly affects classification validity. |
| 5 | Income -> Differential Access EP increased from 0.30 to 0.42 despite parallel trends violation | B | -- | -- | **B** | The parallel trends violation (urban CAGR -0.31% vs rural +3.36%) is documented in Phase 2 and noted in the signal extraction. The EP increase is driven by a relevance increase (urban effect 3.7x larger than rural). The truth value is unchanged (CORRELATION). The concern is valid: if parallel trends are violated, the urban-rural comparison is descriptive, and increasing relevance based on a potentially spurious differential is questionable. However, this edge is a single-link chain and does not propagate into any multi-step Joint_EP calculation that drives conclusions. Category B is appropriate. |
| 6 | COVID and intervention systematics correlated but combined by quadrature | B | -- | -- | **B** | The uncertainty breakdown (Section 7) combines COVID handling (221 yuan) and intervention date (96 yuan) by quadrature. These are clearly correlated: the COVID specification directly affects which years anchor the intervention. However, the analysis already acknowledges that "systematic uncertainty dominates (80%)" and the dominant source is COVID handling (61%). The quadrature combination produces a total systematic of 254 yuan; a correlated combination would be larger (up to 317 yuan if perfectly correlated). This would reduce significance from 1.7 sigma to 1.5 sigma -- the conclusion (CORRELATION, below 2 sigma) would not change. Category B: should be noted but does not alter findings. |
| 7 | 24% aggregate decline exceeds 12% compositional ceiling -- not discussed | B | -- | -- | **C** | The domain reviewer notes that if education is 73% of the proxy category and the compositional analysis finds only a 0.7pp share drop, the implied education-specific decline is bounded. However, the analysis does discuss proxy sensitivity (Section 7, "Proxy Variable Sensitivity") with a range of 60-85% education share producing implied education-only shifts of 290-411 yuan. The 24% vs 12% tension is implicitly addressed by the proxy uncertainty range and the compositional z-score of -1.05. A more explicit discussion would be useful but is not a material gap. Downgraded to C. |
| 8 | No quantitative Chen et al. (2025) comparison | B | -- | -- | **C** | The analysis mentions Chen et al. (2025) in the summary and positions itself as a "macro-level consistency check." A table comparing Chen et al.'s household-level finding with this analysis's aggregate finding would strengthen the discussion, but the absence is a presentation gap, not a methodological one. Downgraded to C. |
| 9 | No synthetic control across categories considered | -- | B | -- | **C** | With only 8 consumption categories and the proxy bundling education/culture/recreation, synthetic control across categories is not feasible. The compositional analysis (step4) serves a similar purpose by comparing education's trajectory to other categories. The suggestion has merit for future work but is not actionable with available data. |
| 10 | No secondary method for Industry Collapse edge | -- | B | -- | **B** | The edge is labeled DATA_SUPPORTED based on literature alone (see Issue 1). Even setting aside the label issue, the conventions require at least 2 estimation methods per primary edge. No quantitative estimation of industry collapse magnitude was performed -- the 92-96% closure rate comes from secondary references, not from the analysis's own data. This is a distinct issue from Issue 1: the edge lacks both refutation tests AND a secondary method. Retained as B because it is downstream of Issue 1. |
| 11 | Urban/rural uncertainty breakdown missing | -- | B | -- | **C** | The uncertainty breakdown (Section 7) is provided only for the national series. Urban and rural breakdowns are not presented. However, the national series is explicitly the primary result, and urban/rural are presented as supporting evidence. A brief note that the breakdown structure is qualitatively similar across series would suffice. Downgraded to C. |
| 12 | Permutation p-value not in refutation battery | -- | B | -- | **C** | The permutation test (p=0.14) is reported in signal extraction but not as a formal refutation test. The conventions specify three named tests (placebo, random common cause, data subset). The permutation test is supplementary diagnostic information, not a missing refutation. It is correctly reported and its implications are discussed. |
| 13 | Residual bootstrap biased at n=9 | -- | -- | B | **B** | The bootstrap resamples pairs (line 163-166 of step3_bsts_analysis.py) from 4 pre-period observations. With n=4, bootstrap variance estimates are known to be biased downward. The analysis notes that bootstrap SEs are 17-20% smaller than analytical SEs (Section 6) but attributes this to the bootstrap not inflating variance for extreme residuals, rather than acknowledging small-sample bias. This affects the reported confidence intervals for the BSTS secondary method. Category B is appropriate. |
| 14 | Signal injection uses single noise realization | -- | -- | B | **B** | The signal injection table (Section 6) shows two cases where 2x-magnitude injection falls outside 1 sigma. The analysis dismisses this as "expected given the single random noise realization." With n=9, a single realization is indeed limiting, but the proper response is multiple realizations to compute coverage, not dismissal. The model does pass all injections within 2 sigma, so this is not a failure, but the validation is weaker than claimed. Category B. |
| 15 | Random common cause test mechanically passes | -- | -- | B | **B** | Adding a random variable to a 3-parameter OLS model with 9 observations will almost never change the coefficient of interest meaningfully, because the random variable is orthogonal in expectation and the model is saturated. The 0.1-1.9% changes reported are exactly what would be expected by construction. The test provides no information about sensitivity to real confounders. Category B: the test implementation is technically correct but diagnostically vacuous given the model structure. |
| 16 | Only one pre-period window tested | -- | -- | B | **B** | The sensitivity analysis (Section 6) tests pre-period restriction to 2018-2019 only, finding a 3.3% difference. No other window variations are tested. With only 4 pre-period observations, window testing options are limited (2016-2019 full, 2017-2019, 2018-2019, 2019 only). The 2018-2019 restriction is the most informative alternative. More windows would be valuable but the space is inherently constrained. Category B. |
| 17 | BSTS bootstrap resamples pairs not residuals | -- | -- | B | **C** | The step3 script (lines 162-170) resamples observation pairs from the pre-period, not residuals. Pair resampling is a valid bootstrap variant (nonparametric bootstrap) that does not require the model to be correctly specified. Residual bootstrap would preserve the covariate distribution but assumes the model is correct. With n=4, neither variant is well-calibrated. This is a methodological choice, not an error. Downgraded to C given the already-noted n=4 limitation (Issue 13). |

---

## EP Adjudication

### 1. EP Assessment Reasonableness
The overall EP trajectory (most edges declining or stable, one edge increasing from 0.60 to 0.70) is broadly reasonable given the data quality constraints. However, the DATA_SUPPORTED label on "Policy -> Industry Collapse" (EP 0.70) is not earned through the analysis's own refutation battery -- it relies on external literature. The EP value itself (0.70) is defensible given overwhelming literature evidence of industry collapse, but the label violates protocol.

### 2. Truncation Decision Validity
Chain truncation decisions are valid. DAG 1 Joint_EP = 0.002 (hard truncation), DAG 2 Joint_EP = 0.025 (hard truncation). These are driven by genuinely low downstream edge EPs. No important sub-chains are being discarded -- the analysis correctly identifies that the multi-step chains cannot support causal claims.

### 3. Label Consistency
**Category A violation identified.** "Policy -> Industry Collapse" is labeled DATA_SUPPORTED without any refutation tests being run. The conventions and CLAUDE.md are unambiguous: DATA_SUPPORTED requires 3/3 refutation tests passing. Additionally, three HYPOTHESIZED edges show small EP increases (Issues 3), violating the mechanical update formula. For the primary tested edge ("Policy -> Aggregate Spending"), the CORRELATION label is consistent with the 2/3 pass rate -- though the substitution of jackknife for data subset (Issue 4) means this 2/3 count is itself questionable.

### 4. Confidence Band Appropriateness
The total uncertainty bands (284 yuan on a 483 yuan estimate, or 1.7 sigma) are reasonable and reflect the genuine uncertainty. The systematic uncertainty dominance (80%) is correctly identified and discussed. The bands may be slightly too narrow due to the correlated-systematics issue (Issue 6), but the qualitative conclusion (below 2 sigma) is robust.

### 5. Causal DAG Validity
The DAG structure is defensible. The domain reviewer's suggestion to add a post-COVID culture/recreation recovery path is valid but would not change conclusions (it would widen uncertainty, reinforcing the CORRELATION finding). No missing edges affect conclusions materially.

---

## Adjudicated Category A Issues

### A1: "Policy -> Industry Collapse" labeled DATA_SUPPORTED without refutation tests
- **Source:** Domain reviewer, Logic reviewer (both A)
- **Evidence:** ep_update script line 176: "No refutation needed." Conventions causal_inference.md line 10-11: "every causal claim must survive at least 3 refutation tests (placebo, random common cause, data subset)." CLAUDE.md non-negotiable rule 1: "An edge classified as DATA_SUPPORTED without all 3 refutation tests passing is a Category A finding. No exceptions."
- **Impact:** The EP propagation table and DAG show this edge as DATA_SUPPORTED (EP=0.70). While the underlying claim is likely true (92-96% industry closures are well-documented), the classification violates the analysis protocol. The edge should be relabeled CORRELATION or a new label like LITERATURE_SUPPORTED should be introduced with a note that refutation tests are infeasible due to the edge not being tested with the analysis's own data.
- **Required fix:** Either (a) run the refutation battery on this edge using available data, or (b) relabel to CORRELATION/LITERATURE_SUPPORTED and apply the corresponding mechanical truth update, or (c) document explicitly why this edge is exempt from refutation (with the understanding that the label cannot be DATA_SUPPORTED).

### A2: "BSTS" method is actually OLS with income covariate -- mislabeled throughout
- **Source:** Methods reviewer (A)
- **Evidence:** step3_bsts_analysis.py lines 97-102 implement OLS. UnobservedComponents is attempted in a try/except block (lines 128-153) but its results are stored in a separate `uc_result` dict and are not used for any reported values. The function returns OLS-derived estimates. Throughout ANALYSIS.md, this is called "BSTS" (Bayesian Structural Time Series).
- **Impact:** The method agreement assessment ("ITS and BSTS agree") is actually "ITS and OLS-with-income agree." These are much more similar methods than ITS and BSTS, so the apparent method agreement provides less independent corroboration than claimed. The 20.9% magnitude disagreement is expected for two linear models with overlapping specifications rather than evidence of robustness.
- **Required fix:** Rename the secondary method to "OLS income-conditioned counterfactual" (or similar accurate label) throughout ANALYSIS.md. Re-evaluate whether this constitutes a genuinely independent secondary method per the "at least 2 estimation methods per primary edge" requirement.

### A3: Jackknife leave-one-out substituted for required "data subset" refutation test
- **Source:** Methods reviewer (A), Logic reviewer (B)
- **Evidence:** step5_refutation.py lines 175-209 implement jackknife (drop one observation at a time), not data subset (randomly drop 20-30%). Conventions causal_inference.md line 10-11 and CLAUDE.md Section 3.3.4 specify "data subset" explicitly.
- **Impact:** The refutation battery is incomplete. The CORRELATION classification for "Policy -> Aggregate Spending" rests on 2 valid tests (placebo, random common cause) plus 1 invalid substitute (jackknife). With n=9, a 20-30% random drop means dropping 2-3 observations -- this is feasible and should have been implemented. The jackknife findings (sensitivity to 2021 and 2022) are valuable diagnostic information but should be presented as supplementary, not as a substitute for the required test.
- **Required fix:** Implement the data subset test as specified (random 20-30% drop, re-estimate, check stability). The jackknife can remain as additional diagnostic. Reclassify the edge based on the updated battery results.

---

## Adjudicated Category B Issues

| ID | Finding | Status |
|----|---------|--------|
| 3 | HYPOTHESIZED edges with small EP increases violate mechanical update formula | Must fix. Apply the correct truth update for HYPOTHESIZED edges (truth = min(0.3, phase1_truth - 0.1)) and recalculate EP. |
| 5 | Income -> Differential Access EP increased despite parallel trends violation | Must fix. Add a note that the relevance increase is conditional on the descriptive comparison being valid, and flag the parallel trends violation as a caveat on this EP. |
| 6 | COVID and intervention systematics combined by quadrature despite correlation | Accepted. The conclusion is unchanged under correlated combination. Add a sentence noting the correlation and its maximum impact on the total. |
| 10 | No secondary method for Industry Collapse edge | Subsumed by A1. Fix alongside the relabeling of this edge. |
| 13 | Residual bootstrap biased at n=4 pre-period | Accepted with caveat. Add a note that bootstrap CIs from the OLS counterfactual are likely too narrow due to small-sample bias. |
| 14 | Signal injection single realization | Must fix. Run 50-100 realizations and report coverage fraction rather than a single pass/fail. |
| 15 | Random common cause test mechanically passes at n=9 | Accepted with caveat. Add a note that the test has low power given the model structure. |
| 16 | Only one pre-period window tested | Accepted. The testing space is inherently constrained. |

---

## Adjudicated Category C Issues

- C7: 24% vs 12% compositional ceiling -- implicit in proxy sensitivity discussion
- C8: No quantitative Chen et al. (2025) comparison table -- presentation improvement
- C9: No synthetic control across categories -- infeasible with available data
- C11: Urban/rural uncertainty breakdown not presented -- add brief note
- C12: Permutation p-value not in refutation battery -- correctly reported as supplementary
- C17: BSTS bootstrap resamples pairs not residuals -- methodological choice, not error

---

## Regression Assessment

No regressions from earlier phases detected. The Phase 1 downscoping decision is confirmed by Phase 3 results (all chain Joint_EPs below hard truncation). The Phase 2 parallel trends finding is correctly carried forward. Data quality warnings from Phase 0 are restated in the Carried-Forward Warnings section.

---

## Verdict Rationale

Three Category A issues remain after adjudication:

1. **A1 (DATA_SUPPORTED without refutation):** A clear protocol violation flagged by two independent reviewers. The fix is straightforward: relabel the edge and apply the correct mechanical truth update. This can be resolved within the current phase.

2. **A2 (BSTS mislabeling):** A factual error in method description throughout the artifact. The fix is mechanical: rename and reassess method independence. This can be resolved within the current phase.

3. **A3 (Jackknife substituted for data subset):** A convention violation in the refutation battery. The fix is to implement the correct test and update classification if needed. This can be resolved within the current phase.

All three Category A issues have clear, actionable fixes that do not require changing the analysis strategy. The underlying analysis is sound -- the CORRELATION classification and the "below 2 sigma with systematics" conclusion are likely to survive correction of these issues. The fixes involve relabeling, renaming, and running one additional test. No regression to earlier phases is needed.

Multiple Category B issues (3, 5, 14) also require fixes but are individually manageable.

The combination of 3 Category A issues and 5 active Category B issues (3 requiring fixes) represents a significant gap that must be addressed before advancement. The phase must be reworked and re-reviewed.

DECISION: ITERATE
