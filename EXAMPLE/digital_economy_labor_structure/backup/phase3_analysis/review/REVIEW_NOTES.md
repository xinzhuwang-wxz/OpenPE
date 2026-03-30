# Arbiter Adjudication: Phase 3 (Causal Analysis)

## Input Reviews
- Logic Review: `phase3_analysis/review/logic_review.md`
- Methods Review: `phase3_analysis/review/methods_review.md`
- Domain Review: `phase3_analysis/review/domain_review.md`

---

## Issue Adjudication Table

| ID | Finding | Logic | Methods | Domain | Adjudicated Category | Rationale |
|----|---------|:-----:|:-------:|:------:|:--------------------:|-----------|
| 1 | Refutation tests for DE-->IND_UP run on bivariate spec, not the controlled spec used for inference | A (A-1) | A (A2) | A (A2) | **A** | All three reviewers agree. The controlled specification (p=0.008) is the basis for inference, but refutations tested only the bivariate (p=0.132). This is a protocol violation: the specification being classified must be the one refuted. |
| 2 | DID coefficient values inconsistent between Sections 2.4 and 6.4 | A (A-3) | -- | -- | **A** | Logic reviewer identified material discrepancies: substitution beta_1 is 21.00 vs 20.51, beta_2 is -12.53 vs -5.90, and creation beta_2 reverses sign (+17.67 vs -10.38). Reading the artifact confirms this. Section 2.4 appears to use a different specification (different SE estimator or break year) than Section 6.4, but neither section labels the distinction. Two sections reporting materially different coefficients for ostensibly the same regression is a correctness issue that must be reconciled. |
| 3 | Bootstrap for Granger causality uses i.i.d. resampling instead of block bootstrap | -- | A (A1) | -- | **B** | Methods reviewer correctly identifies that i.i.d. residual resampling may underestimate variance when residuals retain serial correlation. However, the VAR residuals at T=24 with p=2 have very few effective autocorrelation lags, and the DID bootstrap already uses block bootstrap correctly. The magnitude of bias from i.i.d. resampling of VAR residuals is likely small relative to the already-wide confidence intervals. Downgraded from A to B because: (a) the primary Granger results are not at razor-thin significance margins -- the controlled substitution p=0.012 has margin, and (b) the analysis already reports bootstrap and asymptotic p-values, providing a cross-check. The fix (switching to block bootstrap) should still be implemented. |
| 4 | DE-->CRE relevance not reduced to 0.1 per "effect near zero" rule | A (A-2) | -- | -- | **A** | Logic reviewer correctly identifies that the EP update rules require relevance = 0.1 when the effect is near zero. The creation channel has no Granger signal at any level, no cointegration, and the effect estimate is indistinguishable from zero. Relevance was set to 0.40 instead of 0.10. With correct relevance, EP = 0.30 x 0.10 = 0.03, which falls below hard truncation (0.05). This changes the classification and downstream chain computations. |
| 5 | Compositional constraint between industry and services employment not addressed | -- | -- | A (A1) | **B** | Domain reviewer raises a valid point: industry and services shares are mechanically linked through the adding-up constraint (with agriculture). However, the analysis tests DE against industry and services separately as distinct hypothesized channels (substitution vs. creation), which is standard in the reference literature (Li et al. 2024, Zhao and Li 2022). The finding that DE-->industry is positive while DE-->services is null is informative precisely because the compositional constraint means these are not fully independent -- it tells us the DE effect concentrates in industry, not services. Downgraded from A to B. The analysis should acknowledge the compositional linkage and note that these are not fully independent tests, but restructuring the entire analysis around industry-services ratios is not warranted. |
| 6 | Theoretically motivated nonlinearity (inverted-U) not tested | -- | B (B-5) | A (A3) | **B** | Domain reviewer assigns A; logic reviewer assigns B. The inverted-U from Zhao and Li (2022) is theoretically motivated, and the quadratic sensitivity in Section 6.6 is dismissed without adequate justification. However, at T=24 with a quadratic term, there are extremely few effective degrees of freedom, making any nonlinear test unreliable. The piecewise-linear test at the structural break (which is already implemented as the POST interaction) effectively captures the nonlinearity -- the negative POST x DE interaction (-11.62 pp) is evidence that the relationship weakened in the later period, consistent with the downward portion of the inverted-U. The analysis already has the relevant test; it needs better synthesis, not a new specification. Downgraded from A to B. Add a paragraph synthesizing the temporal narrative (pre-2015 complement, post-2015 weakening) as consistent with the inverted-U hypothesis. |
| 7 | Restricted model in Toda-Yamamoto zeros columns instead of dropping them | -- | B (B1) | -- | **B** | Methods reviewer identifies a potential implementation error in the Wald test construction. Zeroing columns instead of deleting them produces incorrect restricted RSS. This could bias the W statistic. The fix is low-effort and should be implemented. |
| 8 | ARDL bounds test uses Pesaran (2001) asymptotic critical values at T=24 | -- | B (B2) | -- | **B** | Valid concern. Pesaran asymptotic bounds over-reject at small T. Narayan (2005) small-sample critical values exist for this case. At minimum, add a note that the bounds may be liberal. |
| 9 | VAR mediation decomposition methodology invalid (bivariate vs trivariate comparison) | -- | B (B3) | B (B3) | **B** | Both methods and domain reviewers flag this. The comparison of IRFs across VARs of different dimensionality conflates shock rescaling with transmission mechanism changes. The FEVD (already computed at ~15%) is the appropriate mediation metric. The analysis already flags the negative mediation as anomalous; it should reframe around FEVD as the primary mediation measure. |
| 10 | Data subset refutation drops random rows, destroying temporal structure | -- | B (B4) | -- | **B** | Methods reviewer correctly identifies that random row deletion violates time series assumptions. This explains the universal subset test failure and makes the refutation battery effectively 2 tests, not 3. A contiguous subsample approach would be more informative. |
| 11 | Lag selection uncertainty excluded from total uncertainty | -- | -- | B (B4) | **B** | Domain reviewer raises a valid point. The result's significance depends on lag order (p=1 significant, p=3 not). Excluding this from the quadrature combination understates total uncertainty. At minimum, report a second total uncertainty value that includes lag sensitivity. |
| 12 | DE index composition not explored as alternative explanation for positive sign | -- | -- | B (B1) | **B** | Domain reviewer's suggestion to decompose the DE index into its four components is informative but represents additional analysis beyond Phase 3 scope. Add a paragraph discussing how index composition may explain the positive sign. |
| 13 | ILO modeling endogeneity not fully traced | -- | -- | B (B2) | **C** | Domain reviewer raises a valid but speculative concern. The ILO endogeneity is already flagged as Warning 5. Tracing the exact ILO modeling methodology for China requires accessing ILO methodological notes, which may not be available. The concern is documented; further investigation is a Phase 5 verification task. Downgraded to C. |
| 14 | Out-of-sample validation not reported | B (B-3) | -- | -- | **B** | Logic reviewer notes that STRATEGY.md planned a train-on-2000-2019 / test-on-2020-2023 split. This is not reported. Even if COVID disrupts the test, the omission should be documented. |
| 15 | No IV or endogeneity correction attempted | B (B-4) | -- | -- | **C** | Logic reviewer notes all references use GMM/IV. However, at T=24 with national data, no valid external instrument exists. This is a known limitation already documented. Downgraded to C. |
| 16 | DEMO-->LS relevance reduction not fully justified | B (B-1) | -- | C (C2) | **B** | Logic reviewer correctly notes the mechanical EP rule would set relevance to 0.1 (giving EP=0.03). The analysis sets it to 0.40. Either apply the rule mechanically or explicitly justify the override. The domain reviewer's note about the DEMO-->LS EP being overly mechanical is the opposite concern -- that the truth reduction is too aggressive. On balance, the EP update should follow the mechanical rules consistently (as required by non-negotiable rule 4), with a qualitative note about the frequency mismatch. |
| 17 | Bootstrap replications inconsistent across procedures | -- | B (B5) | -- | **C** | Valid but low-impact. Standardizing bootstrap replications is a minor code cleanup. The inconsistency (10,000 vs 1,000 vs 500 vs 2,000) does not change conclusions. |
| 18 | Uncertainty tornado includes ill-defined systematics without visual distinction | -- | B (B6) | -- | **C** | Valid presentation concern. The figure should visually distinguish ill-defined bars. This is a figure revision, not a methodological issue. |
| 19 | Specification selection for DE-->SUB may involve implicit data snooping | B (B-2) | -- | -- | **C** | Logic reviewer asks for a note that the controlled specification was pre-committed. The DAG-driven selection is already implicit in the causal model (DEMO is a confounder per the DAG). A brief note suffices. |
| 20 | Negative mediation share not adequately investigated | B (B-6) | -- | -- | **B** | Overlaps with ID 9. Test alternative Cholesky orderings or reframe around FEVD. |

---

## EP Adjudication

### EP Assessment Reasonableness

The overall EP framework is applied mechanically and traceably, which is a strength. However, two specific EP values require correction:

1. **DE-->CRE EP=0.120 is too high.** Per the "effect near zero" rule, relevance should be 0.1, giving EP=0.03. This edge should fall below hard truncation. The current value of 0.120 overstates the evidence for the creation channel. (Finding ID 4.)

2. **DEMO-->LS EP=0.120 is internally inconsistent.** The same "effect near zero" rule applies (Granger causality not significant at any level). If the mechanical rule is applied, EP drops to 0.03. However, the domain context (demographic transitions are well-documented drivers of structural change in China, and the null Granger result reflects frequency mismatch rather than absence of causation) argues for a qualitative note explaining why the mechanical reduction is conservative. The EP value itself should follow the mechanical rule per non-negotiable rule 4.

### Truncation Decision Validity

The sub-chain expansion decision (DEFER for DE-->SUB due to data constraints) is well-justified. The SKIP decisions for other edges are consistent with EP thresholds. No issues.

### Label Consistency

DE-->SUB as CORRELATION (2/3 refutation pass) is consistent with the classification table. DE-->CRE as HYPOTHESIZED (1/3 pass bivariate) is consistent. DE-->IND_UP as HYPOTHESIZED is the contested classification -- it is based on the bivariate refutation (1/3 pass) while the controlled specification (p=0.008) was not refuted. This must be resolved (Finding ID 1).

### Confidence Band Appropriateness

The bootstrap confidence bands are appropriately wide given T=24. The discrepancy between OLS and bootstrap CIs for the controlled specification (OLS: [-20.6, -2.6] vs bootstrap: [-34.3, 33.1]) is honestly reported. The bands reflect genuine uncertainty.

### Causal DAG Validity

The simplified DAG (4 edges) is appropriate for T=24. The missing compositional constraint (Finding ID 5) is acknowledged as a B-level concern. No missing edges that would change conclusions at the A level.

---

## Adjudicated Category A Issues

**A-1 (ID 1): Refutation tests for DE-->IND_UP run on wrong specification.**
All three reviewers agree this is blocking. The controlled specification (W=15.81, p=0.008) is the basis for inference, but refutation tests were run only on the bivariate specification (W=4.75, p=0.132). The classification of HYPOTHESIZED is based on refuting a weaker model, not the one used for the claim. Fix: run the refutation battery on the controlled (trivariate) specification. If degrees of freedom are insufficient for reliable refutation at T=24, cap the edge at CORRELATION with a documented power limitation, rather than HYPOTHESIZED based on a misspecified model.

**A-2 (ID 2): DID coefficient values inconsistent between Sections 2.4 and 6.4.**
Section 2.4 reports substitution beta_1=21.00 (SE=10.48, p=0.063), beta_2=-12.53 (SE=14.84, p=0.412). Section 6.4 reports beta_1=20.51 (SE=16.33, p=0.209), beta_2=-5.90 (SE=4.21 implied, p=0.161). The creation channel beta_2 reverses sign between sections (+17.67 in 2.4, -10.38 in 6.4). These appear to be different specifications (possibly different SE estimators -- HAC vs OLS, or different break year defaults), but the document does not label the distinction. Fix: trace both sets to generating scripts, reconcile, and explicitly label different specifications where they exist.

**A-3 (ID 4): DE-->CRE relevance not set to 0.1 per mechanical EP rule.**
The creation channel has no Granger signal, no cointegration, and an effect indistinguishable from zero. The EP update rule (Step 3.4) requires relevance = 0.1 for near-zero effects. Current relevance = 0.40, giving EP = 0.120. Correct relevance = 0.10, giving EP = 0.03 (below hard truncation at 0.05). Fix: set relevance to 0.1, recompute EP, mark as below hard truncation. Update the Joint_EP table and downstream references accordingly.

---

## Adjudicated Category B Issues

| ID | Finding | Status |
|----|---------|--------|
| 3 | i.i.d. bootstrap for Granger causality | Must fix. Switch to block bootstrap in step1 and step4 scripts. |
| 5 | Compositional constraint not acknowledged | Must fix. Add paragraph acknowledging the adding-up constraint and noting the industry/services findings are not fully independent. |
| 6 | Nonlinearity synthesis missing | Must fix. Add paragraph synthesizing the temporal narrative (POST interaction as evidence of inverted-U) rather than implementing a new specification. |
| 7 | Restricted model column zeroing in Wald test | Must fix. Replace column zeroing with column deletion. |
| 8 | ARDL bounds test critical values | Must fix. Add note about asymptotic bounds at T=24; use Narayan (2005) values if available. |
| 9/20 | VAR mediation methodology | Must fix. Reframe mediation analysis around FEVD. Test at least one alternative Cholesky ordering. |
| 10 | Data subset refutation destroys temporal structure | Must fix. Implement contiguous subsample test. This may change refutation outcomes. |
| 11 | Lag selection excluded from total uncertainty | Must fix. Report a second total uncertainty value including lag sensitivity. |
| 12 | DE index composition as alternative explanation | Must fix. Add discussion paragraph. |
| 14 | Out-of-sample validation not reported | Must fix. Report or document why omitted. |
| 16 | DEMO-->LS relevance inconsistent with mechanical rule | Must fix. Apply mechanical rule (relevance=0.1) with a qualitative note. |

---

## Adjudicated Category C Issues

- C (ID 13): ILO modeling endogeneity tracing -- document as Phase 5 verification task.
- C (ID 15): No IV/endogeneity correction -- add brief justification paragraph.
- C (ID 17): Bootstrap replications inconsistent -- standardize across scripts.
- C (ID 18): Uncertainty tornado visual distinction -- add hatching or separate panel for ill-defined systematics.
- C (ID 19): Specification selection note -- add sentence noting controlled spec was pre-committed per DAG.
- C (Logic C-1): Figure paths from exec/ directory.
- C (Logic C-2): Unnumbered "Warnings Carried Forward" section.
- C (Logic C-4): Tornado chart aspect ratio.
- C (Methods C-1): Johansen rank determination logic.
- C (Methods C-2): Placebo test uses shifted versions rather than genuinely unrelated variables.
- C (Methods C-3): Random common cause test uses white noise instead of trending process.
- C (Methods C-4): VECM deterministic specification sensitivity.
- C (Methods C-5): Forest plot normalization verification.
- C (Domain C-1): Missing temporal narrative synthesis (overlaps with B finding ID 6).
- C (Domain C-3): Bootstrap CI discrepancy for controlled specification.

---

## Regression Assessment

No regressions from earlier phases detected. All Phase 0 and Phase 1 warnings are carried forward in the "Warnings Carried Forward" section. The Phase 2 DE index break at 2009 (Warning 9) is acknowledged. EP values have moved in expected directions given the empirical results. No upstream changes required.

---

## Verdict Rationale

Three Category A issues remain after adjudication:

1. **Refutation on wrong specification (ID 1)**: This is a protocol violation that affects the classification of DE-->IND_UP. The fix is clear: run refutations on the controlled specification or reclassify with a documented justification.

2. **Coefficient inconsistency between sections (ID 2)**: Two sections of the same document report materially different regression coefficients without explanation. This undermines the artifact's internal consistency and must be reconciled.

3. **EP mechanical rule violation (ID 4)**: The DE-->CRE relevance is set to 0.40 when the rule requires 0.10. This changes the EP from 0.120 to 0.03, moving the edge below hard truncation. While this does not change the qualitative conclusion (the creation channel is unsupported), it affects the quantitative EP propagation table and downstream chain computations.

Additionally, 11 Category B issues require attention, several of which involve implementation corrections (column zeroing in Wald test, i.i.d. bootstrap, data subset test design) that could change numerical results.

All three A-level issues are resolvable within Phase 3 without changing the analysis strategy. The B-level issues are addressable through targeted fixes. No fundamental redesign is needed. The analysis is well-executed in its overall structure, honest in its treatment of the unexpected positive sign, and thorough in its sensitivity analysis. After addressing the A and B issues, this should be ready to advance.

DECISION: ITERATE
