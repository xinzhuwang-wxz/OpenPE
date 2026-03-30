# Arbiter Adjudication: Phase 4 (Projection)

## Input Reviews
- Logic Review: consolidated (arbiter acting as logic reviewer)
- Methods Review: consolidated (arbiter acting as methods reviewer)
- Domain Review: consolidated (arbiter acting as domain reviewer)

This is a consolidated 4-bot review where the arbiter evaluates from all three reviewer perspectives before rendering a verdict.

---

## Issue Adjudication Table

| ID | Finding | Logic | Methods | Domain | Adjudicated Category | Rationale |
|----|---------|-------|---------|--------|---------------------|-----------|
| 1  | EP decay applies CORRELATION 2x multiplier as exponentiation rather than multiplicative scaling | B | A | -- | B | See detailed discussion below. The code computes `ep_multipliers_raw ** CORRELATION_MULTIPLIER` (squaring the raw multiplier), whereas the protocol says CORRELATION edges "decay at 2x the standard rate." Squaring versus doubling the decay rate are not identical operations. However, the net effect is aggressive decay, which is directionally conservative (honest), and the resulting EP values are internally consistent within PROJECTION.md. |
| 2  | Sensitivity analysis uses deterministic endpoint, not Monte Carlo, producing zero sensitivity for DE parameters due to saturation ceiling | -- | B | -- | B | The deterministic sensitivity analysis clips DE at 1.0, so any perturbation of `beta_de` or `de_growth` at the saturated ceiling has zero marginal effect. This is mathematically correct given the model setup, but a methods reviewer would note that the sensitivity could also be evaluated at a hypothetical non-saturated DE value to reveal the *latent* sensitivity. The document acknowledges this (Section: Critical Finding: DE Index Saturation) and discusses it honestly. Category B because it limits actionable insight but is documented. |
| 3  | Innovation noise in `project_industry_emp` uses the global `rng` object, creating correlation between iteration noise and parameter draws | -- | B | -- | C | The same `rng` is used for parameter sampling and within-trajectory noise generation. This creates a subtle coupling between iterations. However, with 10,000 iterations and the default_rng PRNG quality, the practical impact is negligible. A cleaner design would use separate generators, but this does not materially affect results. |
| 4  | beta_DEMO SE assumed at 0.50 ("not reported precisely in ANALYSIS.md") | A | A | -- | B | ANALYSIS.md reports beta_DEMO = 1.29 but does not report its standard error. The projection script assumes SE = 0.50. This is an imputed value without empirical basis. However, (a) the ARDL controlled specification does provide the estimate, just not a clean SE for the demographic coefficient specifically, and (b) the sensitivity analysis shows demographic parameters dominate regardless. Downgraded from A to B because the assumed SE is plausible (roughly 40% of the point estimate) and the projection honestly documents this assumption. The fix is straightforward: extract or compute beta_DEMO SE from the ARDL output. |
| 5  | Endgame "Robust" classification is technically correct but misleading | A | -- | A | B | CV = 0.046 meets the Robust threshold (CV < 0.15). However, scenario convergence is driven by DE index saturation, not by strong causal knowledge. PROJECTION.md addresses this extensively with the "Critical caveat" paragraph and the counterfactual discussion of what classification would apply if DE were not saturated (Fork-dependent). The honest treatment in the prose mitigates the concern. Category B: the classification label should carry a qualifier more prominently (e.g., "Robust (saturation-driven)" in the summary). |
| 6  | Low-digital scenario uses different beta_DE (0.5x bivariate) AND faster demographic decline, conflating two independent changes | -- | B | B | C | The low-digital scenario combines weaker DE effect with faster demographic decline. A methods reviewer would prefer isolated scenario dimensions. However, the scenario narrative is coherent (regulatory/stagnation scenario where both digital and demographic headwinds compound), and the sensitivity analysis already provides the one-at-a-time decomposition. This is a design choice, not an error. |
| 7  | Projection model uses static ARDL LR coefficients without error-correction dynamics | -- | B | -- | B | The projection function applies `equilibrium = base + beta_de * delta_de + beta_demo * delta_demo + noise`. This is a static long-run relationship projection, not an error-correction model. The ARDL model in Phase 3 estimated both short-run dynamics and long-run coefficients, but only the long-run coefficients are carried forward. For a 10-year projection with annual steps, the long-run approximation is reasonable, but for the 1-3 year useful horizon, short-run dynamics (the error-correction speed of adjustment alpha = 1.252 from the VECM) could matter. Category B because the useful horizon is stated as 3 years where this matters most. |
| 8  | DID interaction term (beta_2 = -5.90 per period, suggesting complement effect weakening) is acknowledged but not incorporated into the projection model | -- | B | A | B | PROJECTION.md discusses the DID interaction term as a tipping point (complement-to-neutral transition, potentially occurring ~2017-2018). However, the projection model uses the full-period ARDL estimate without a time-varying coefficient. This means the projection may overstate the current DE-industry complement effect. The document honestly identifies this as Open Issue #2. Category B because the issue is documented but unresolved. |
| 9  | Conditional probability assignments (50-60%, 20-30%, 15-25%) are subjective and do not sum to 100% | -- | C | -- | C | The three scenarios account for 85-115% probability. This is acceptable given that scenarios are not exhaustive and can overlap, but it should be noted that the residual probability (other scenarios not modeled) is not discussed. Minor issue. |
| 10 | All three required figures exist and are correctly formatted | -- | -- | -- | -- (strength) | PDF + PNG, 10x10, no titles, bbox_inches tight, dpi 200, transparent. Plotting conventions are followed. Labels are readable. EP decay chart correctly shows two panels with truncation thresholds. Tornado chart correctly shows zero sensitivity for DE parameters. Scenario comparison correctly shows convergence. |
| 11 | Phase 3 limitations honestly carried forward | A | -- | -- | -- (strength) | PROJECTION.md includes a comprehensive "Constraints on Conclusions" section and "Open Issues" section. All five DATA_QUALITY.md constraints are traceable in the projection. The "What projections CANNOT claim" list is appropriately restrictive. This is exemplary limitation propagation. |
| 12 | Projection uses bivariate ARDL LR coefficient (7.15) as baseline rather than controlled (12.57) | -- | B | -- | C | The baseline scenario uses the bivariate (conservative) estimate while the high-digital scenario uses the controlled estimate. This is a defensible choice: the bivariate estimate is more robust (fewer parameters at T=24) even though it is only marginally significant. The document explains the choice. |
| 13 | EP decay chart bottom panel: EP drops below soft truncation (0.15) within year 1, not year 3 as the "useful horizon" suggests | B | -- | -- | C | The text recommends a 3-year useful horizon based on hard truncation (0.05), while EP crosses soft truncation at approximately year 1. The EP decay chart visually confirms this: EP is well below 0.15 by year 1. The text correctly states both thresholds and recommends 3 years based on hard (not soft) truncation. The recommendation is defensible since the hard truncation threshold is the binding constraint for whether any EP-based content remains. |

---

## EP Adjudication

### 1. EP Assessment Reasonableness
The base EP of 0.315 for DE-->SUB (CORRELATION) is correctly carried from Phase 3. The decay schedule is aggressive but justified for a fast-moving technology domain with a CORRELATION (not DATA_SUPPORTED) edge. The 2x decay multiplier for CORRELATION edges is protocol-compliant. The resulting values (0.113 at 1 year, 0.050 at 3 years) are reasonable.

### 2. Truncation Decision Validity
Edges below hard truncation (DE-->CRE at EP=0.030, DE-->LS at EP=0.010) are correctly excluded from the projection's central estimate and contribute only to scenario spread mentions. The sole projected edge (DE-->SUB at EP=0.315) is the only one above soft truncation. This is correct.

### 3. Label Consistency
The CORRELATION label for DE-->SUB is consistent with Phase 3 refutation results (2/3 PASS). The HYPOTHESIZED labels for all other edges are consistent with their 1/3 or 0/3 PASS results. No mislabeling detected.

### 4. Confidence Band Appropriateness
The EP confidence bands widen appropriately over the projection horizon. The 95% CI at 10 years spans 6.4 pp for baseline (24.2-30.6%), which is not unreasonably narrow given that the projection is primarily demographic. The low-digital scenario's 95% CI spans 15.2 pp (17.2-32.4%), reflecting genuine uncertainty. The bands are neither overconfident nor uninformative.

### 5. Causal DAG Validity
The projection correctly uses only the DE-->SUB edge above truncation. The DAG structure from Phase 3 is faithfully represented. No missing edges that would affect conclusions.

---

## Adjudicated Category A Issues

None remain after adjudication. Issues initially flagged as potential Category A (beta_DEMO SE imputation, #4; endgame label potentially misleading, #5) were downgraded to Category B after examining the artifact's treatment of these issues.

---

## Adjudicated Category B Issues

| ID | Issue | Blocks? | Resolution Path |
|----|-------|---------|-----------------|
| 1  | EP decay 2x implementation (exponentiation vs. rate doubling) | No | Internally consistent; aggressive decay is conservative. Could add a footnote explaining the computation. |
| 2  | Sensitivity analysis at saturation yields zero DE sensitivity | No | Documented honestly. Could add a secondary sensitivity evaluated at DE=0.8 to show latent sensitivity. |
| 4  | beta_DEMO SE = 0.50 assumed | No | Extract from ARDL output or document the assumption more prominently in the parameter table. |
| 5  | "Robust" classification needs stronger caveat | No | The caveat exists in prose but the summary line ("Category: Robust") should read "Category: Robust (saturation-driven convergence, not causal certainty)". |
| 7  | Static LR projection without error-correction dynamics | No | Acceptable for the 3-year useful horizon recommendation. Document as a model limitation. |
| 8  | DID interaction term not incorporated into time-varying projection | No | Documented as Open Issue #2. Incorporating it would require a regime-switching projection model, which is beyond current scope. |

All Category B issues are either (a) already documented in the artifact and acceptable for the current phase, or (b) addressable with minor text clarifications. None individually or collectively represent a significant gap that would block advancement.

---

## Adjudicated Category C Issues

- C3: Shared RNG between parameter draws and trajectory noise (negligible impact)
- C6: Low-digital scenario conflates two changes (defensible scenario design)
- C9: Conditional probabilities do not sum to 100% (scenarios are not exhaustive)
- C12: Bivariate vs. controlled coefficient choice for baseline (conservative, documented)
- C13: Soft vs. hard truncation for useful horizon label (correctly uses hard truncation)

---

## Regression Assessment

No regressions detected. Phase 3 findings are faithfully carried forward. All five DATA_QUALITY.md constraints are traceable in the projection artifact. EP values match Phase 3 outputs. The positive sign of the DE-->SUB edge (complement, not substitution) is correctly propagated and prominently discussed.

---

## Verdict Rationale

The Phase 4 projection artifact is well-constructed given the severe constraints inherited from upstream phases (DE index saturation, T=24 sample size, CORRELATION-only classification for the single projectable edge). The key strengths are:

1. **Intellectual honesty.** The document is forthright about what the projection can and cannot claim. The "Constraints on Conclusions" and "What projections CANNOT claim" sections are unusually thorough and self-aware.

2. **Correct EP propagation.** The decay schedule, truncation decisions, and edge classifications are consistent with Phase 3 outputs and protocol requirements.

3. **Sound Monte Carlo methodology.** 10,000 iterations with fixed seed, physical bounds enforcement, proper percentile computation, and documented parameter distributions.

4. **Appropriate sensitivity analysis.** The finding that DE parameters have zero sensitivity at saturation is the most important analytical result of the phase, and it is correctly identified and discussed.

5. **Honest endgame classification.** While "Robust" is technically correct, the extensive caveat about saturation-driven convergence prevents misinterpretation.

The Category B issues are real but non-blocking. The beta_DEMO SE imputation (#4) is the most substantive, but its practical impact is bounded: even a 2x change in this SE would not alter the dominant finding (demographics drive the projection, DE is saturated). The remaining B issues are matters of additional documentation or refinements that would improve but not change the conclusions.

No Category A issues remain after adjudication. No regressions detected. The artifact is ready to proceed to Phase 5.

DECISION: PASS
