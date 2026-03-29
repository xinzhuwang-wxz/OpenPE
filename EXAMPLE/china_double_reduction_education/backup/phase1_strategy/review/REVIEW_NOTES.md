# Arbiter Adjudication: Phase 1 — Strategy

## Input Reviews
- Domain Review: `phase1_strategy/review/DOMAIN_REVIEW.md`
- Logic Review: reviewer findings summary (inline)
- Methods Review: reviewer findings summary (inline)

---

## Issue Adjudication Table

| ID | Finding | Domain | Logic | Methods | Adjudicated Cat. | Rationale |
|----|---------|--------|-------|---------|-------------------|-----------|
| 1 | ITS over-parameterized: 6 params from 10 obs yields ~4 df | A | -- | A | **A** | Two independent reviewers agree. The strategy specifies a COVID indicator (2020) + recovery parameter (2021) alongside intercept, trend, level-shift, and trend-change — 6 parameters from 10 observations. This is statistically indefensible. A minimal 3-parameter model (intercept, pre-trend, level-shift) is the maximum defensible specification; COVID should be handled by exclusion, not by spending degrees of freedom on indicators. |
| 2 | Urban-rural quasi-DiD overclaimed: parallel trends likely violated by convergence trend; n=2 units | A | -- | B | **B** | Domain reviewer rates this A; Methods reviewer rates B with fallback planned. The strategy already includes a parallel-trends test (Section 7, line 397) and a contingency plan to abandon quasi-DiD if trends are violated (Section 11, line 546). The issue is real but the strategy already documents the risk and fallback. Downgrade to B: the strategy must explicitly acknowledge that "quasi-DiD" is an optimistic label and reframe it as "urban-rural stratified ITS with formal comparison" unless parallel trends can be demonstrated in Phase 2. |
| 3 | EP truncation override needs formal feasibility evaluation per methodology/09-downscoping.md | -- | A | -- | **A** | Only the Logic reviewer raised this, but it is a valid structural issue. All chains fall below hard truncation (0.05), yet the strategy overrides truncation with a "pragmatic classification" (lines 251-264). The methodology spec (09-downscoping.md Section 12.2) requires: (1) document the constraint, (2) choose the best achievable method, (3) quantify the impact, (4) carry it through to the analysis note. The strategy does items 1-2 informally but lacks the formal feasibility evaluation structure. The override is arguably defensible — individual edges above 0.15 can be tested — but the argument must be formalized as a downscoping decision, not presented as a casual "pragmatic" override. |
| 4 | ITS/BSTS cannot discriminate DAG 2 vs DAG 3 — need DAG identifiability assessment | -- | A | -- | **B** | The Logic reviewer is correct that both DAG 2 (displacement) and DAG 3 (compositional irrelevance) predict "no/small decline in total spending," making them observationally equivalent at the aggregate level. However, this is a fundamental data limitation, not a strategy error. The strategy already notes compositional analysis as the partial discriminator (Section 4, line 259). Downgrade to B: the strategy must add an explicit identifiability discussion acknowledging that ITS/BSTS on aggregate data cannot distinguish DAG 2 from DAG 3, and must specify what observable differences (if any) the compositional analysis could exploit. |
| 5 | BSTS covariates unspecified | -- | -- | B | **B** | Methods reviewer (B1) raised this. The strategy names BSTS as a secondary method and mentions covariates (income, demographics) in passing (line 309) but does not specify the covariate set, prior structure, or how feasibility will be assessed given only 5 pre-treatment observations. Must specify candidate covariates and acknowledge the n=5 pre-treatment constraint. |
| 6 | Only 2 clean pre-policy observations in 8-category data | B | -- | -- | **B** | Domain reviewer (B2). If 2016-2018 are back-calculated and 2020 is COVID-disrupted, only 2019 and possibly 2021H1 are clean pre-policy observations for the 8-category compositional analysis. The strategy must acknowledge this constraint on the compositional structural-break test and temper expectations. |
| 7 | Crowding-in relies on single-paper support | B | -- | -- | **B** | Domain reviewer (B3). The crowding-in mechanism is classified as lightweight, which is appropriate, but its evidence base should be documented more explicitly as thin. Minor — already classified as lightweight. |
| 8 | CIEFR-HS vs NBS trend contradiction unaddressed | B | -- | -- | **B** | Domain reviewer (B4). CIEFR-HS shows per-student spending declining pre-policy while NBS shows the proxy rising. This contradiction is noted in passing (line 172-175, Baseline 5) but not explicitly reconciled. The strategy should note this as a proxy-composition indicator: if CIEFR-HS education spending was declining while the NBS proxy was rising, the culture/recreation component was likely growing faster than education, which directly bears on proxy bias magnitude. |
| 9 | Truncation thresholds applied inconsistently (chain vs edge) | -- | B | -- | **B** | Logic reviewer (B1). The strategy applies 0.05 hard truncation to chains (Section 4) but then uses different thresholds for individual edges (Section 6, line 366-368: hard truncation 0.05 for edges, soft 0.15, full >= 0.15). The chain-to-edge switch is the core of the "pragmatic override" and must be formalized (see Issue 3). |
| 10 | Proxy penalty 0.05 is ad hoc | -- | B | -- | **C** | Logic reviewer (B2). The 0.05 truth penalty for proxy variables (line 195) lacks derivation. However, for a Phase 1 strategy document, exact calibration of EP adjustments is less critical than directional correctness. The penalty is conservative and small. Downgrade to C: note the ad hoc nature in experiment log. |
| 11 | Panel conventions not checked | -- | B | -- | **C** | Logic reviewer (B3). The conventions compliance table (lines 19-48) covers causal inference and time series but not panel analysis. With n=2 units (urban/rural) and the quasi-DiD being downgraded to stratified comparison, formal panel conventions are less applicable. Downgrade to C. |
| 12 | Economic slowdown not explicitly controlled | -- | B | -- | **B** | Logic reviewer (B4). The economic slowdown (property crisis, youth unemployment) is listed as a confounder (line 126-127) and in untestable assumptions (line 534) but no explicit control variable is planned. Income is noted as a partial proxy, but the strategy should state whether income growth adequately captures the slowdown channel or whether additional indicators are needed. |
| 13 | Refutation test power not quantified | -- | B | -- | **C** | Logic reviewer (B5). The strategy already acknowledges this (line 530: "Refutation tests may not have power to detect violations" and "Use refutation tests qualitatively"). Power quantification for n=10 refutation tests is itself infeasible — you cannot meaningfully power-analyze a placebo test with 10 observations. The qualitative framing is appropriate. Downgrade to C. |
| 14 | DoWhy refutation tests not designed for n=10 | -- | -- | B | **B** | Methods reviewer (B2). Related to Issue 13 but distinct: the concern is not just low power but that DoWhy's refutation API may produce misleading results at n=10 (e.g., data-subset refutation removing 2-3 of 10 points). The strategy should specify which refutation tests are feasible at this sample size and which should be replaced or adapted. |
| 15 | Synthetic control needs clean category selection | -- | -- | B | **C** | Methods reviewer (B3). The strategy does not propose synthetic control as a method (it is not in the method selection table). This finding appears to reference the compositional analysis, which is not synthetic control. Not applicable to the current strategy. |
| 16 | EP uncertainty underspecified | -- | -- | B | **B** | Methods reviewer (B4). EP values are presented as point estimates without confidence bands or uncertainty ranges. The strategy should specify how EP uncertainty will be represented — at minimum, a qualitative confidence tier (high/medium/low confidence in the EP estimate). |
| 17 | "Corroboration" framing too strong | A | -- | -- | **C** | Domain reviewer (A3). The strategy uses "corroboration/extension study" (line 248) to describe its relationship to reference analyses. The domain reviewer argues this should be "consistency check." This is a labeling preference at the strategy stage — the actual causal claims will be determined in Phase 3 based on refutation results. The framing does not affect analytical decisions. Downgrade to C: change "corroboration" to "consistency check" in final text. |

---

## EP Adjudication

### 1. EP Assessment Reasonableness
The EP assessment is internally consistent and well-documented. All Phase 0-to-Phase 1 changes have explicit justifications. The systematic depression of EP values due to MEDIUM/LOW data quality and proxy penalties is honest and appropriate. No concerns.

### 2. Truncation Decision Validity
This is the critical EP issue. All chains fall below hard truncation (0.05), yet the analysis proceeds. The strategy's "pragmatic classification" is substantively reasonable — testing individual high-EP edges against aggregate data is defensible even when chains are short. However, this override must be formalized as a downscoping decision per methodology/09-downscoping.md. **Category A (Issue 3).**

### 3. Label Consistency
Edge labels (LITERATURE_SUPPORTED, THEORIZED) are consistent with the evidence base described. No mislabeling detected. Labels will be updated to the refutation-based taxonomy (DATA_SUPPORTED/CORRELATION/HYPOTHESIZED/DISPUTED) in Phase 3, as stated.

### 4. Confidence Band Appropriateness
EP values are presented as point estimates without uncertainty bands. This is flagged as Issue 16 (Category B). At the strategy stage, qualitative confidence tiers would suffice.

### 5. Causal DAG Validity
The DAG structure is defensible. The addition of economic slowdown as an explicit confounder (noted in DAG modifications table) is appropriate. The missing explicit edge from economic slowdown to education spending decisions (beyond income) is noted in Issue 12 (Category B). No missing edges rise to Category A.

---

## Adjudicated Category A Issues

### A1: ITS Over-Parameterization (Issues 1)
**Source:** Domain reviewer (A2), Methods reviewer (A1). Agreement between two independent reviewers.

The strategy proposes an ITS model with intercept, pre-trend, level-shift, trend-change, COVID-2020 indicator, and COVID-recovery parameter — 6 parameters from 10 annual observations, leaving approximately 4 residual degrees of freedom. This is statistically indefensible and will produce unreliable standard errors and inflated Type I error rates.

**Required fix:** Specify a minimal ITS model with at most 3 freely estimated parameters from the 10-observation series. The recommended specification is: intercept, pre-trend, and level-shift. COVID confounding should be handled by the exclusion robustness check (already planned as Method B), not by adding indicator variables. If a trend-change parameter is desired, it replaces the level-shift (not added alongside). The 6-parameter model may be presented as a sensitivity check with explicit acknowledgment that it is over-fit, but it cannot be the primary specification.

### A2: EP Truncation Override Requires Formal Feasibility Evaluation (Issue 3)
**Source:** Logic reviewer (A1). Single reviewer, but validated against methodology spec.

All causal chains have Joint EP below the hard truncation threshold of 0.05. The strategy overrides this with an informal "pragmatic classification." Methodology/09-downscoping.md requires a formal feasibility evaluation for any scope deviation: document the constraint, choose the best achievable method, quantify the impact of the limitation, and commit to carrying the limitation through to the analysis note.

**Required fix:** Rewrite the "Critical Assessment of Chain EP Results" and "Pragmatic Chain Classification" sections as a formal downscoping decision. Specifically: (a) state that chain-level EP truncation is triggered, (b) document why strict truncation would eliminate all analysis, (c) justify the fallback to edge-level testing with explicit criteria for what "edge-level analysis" can and cannot conclude about chain-level causal claims, (d) quantify the epistemic cost (chain-level causal conclusions are not supported; only individual edge assessments are possible), (e) commit to carrying this limitation prominently into the Phase 6 analysis note.

---

## Adjudicated Category B Issues

### B1: Urban-rural quasi-DiD framing (Issue 2)
The strategy must reframe "quasi-DiD" as "urban-rural stratified ITS with formal comparison" unless Phase 2 EDA demonstrates parallel pre-trends. The contingency plan for parallel-trends failure is already present and adequate.

### B2: DAG 2 vs DAG 3 identifiability (Issue 4)
Add an explicit identifiability discussion to the strategy. State clearly: ITS/BSTS on the aggregate NBS proxy cannot distinguish DAG 2 (displacement) from DAG 3 (compositional irrelevance) because both predict small or zero change in total spending. Specify what the compositional analysis (8-category shares) could discriminate, if anything, and what would remain unresolvable.

### B3: BSTS covariates and feasibility (Issue 5)
Specify the candidate covariate set for BSTS (income, enrollment, CPI components). Acknowledge that with only 5 pre-treatment observations (or 2 clean ones if back-calculated data is excluded), BSTS may not converge or may produce uninformative posteriors. State the feasibility gate: if BSTS does not achieve adequate pre-treatment fit, it will be reported as infeasible rather than forced.

### B4: 8-category pre-policy observation constraint (Issue 6)
Acknowledge that the compositional structural-break test has at most 2-4 clean pre-policy observations (depending on back-calculation treatment) and temper the expected discriminatory power accordingly.

### B5: CIEFR-HS vs NBS contradiction (Issue 8)
Add a brief reconciliation noting that diverging CIEFR-HS (declining per-student education spending) and NBS proxy (rising education/culture/recreation spending) trends are themselves evidence of proxy composition shift, and quantify the implication for proxy bias.

### B6: Truncation threshold consistency (Issue 9)
Resolve by formalizing the downscoping decision (Issue A2 fix). The chain-to-edge threshold switch must be explicit and justified, not implicit.

### B7: Economic slowdown control (Issue 12)
State whether income growth is considered a sufficient proxy for the economic slowdown channel. If not, identify what additional indicator could be used (e.g., consumer confidence index, property price index) or acknowledge this as an untestable assumption with explicit language.

### B8: DoWhy refutation test feasibility at n=10 (Issue 14)
Specify which of the three planned refutation tests (placebo, random common cause, data subset) are feasible at n=10. Data-subset refutation removing 30% of 10 observations leaves 7 points for a 6-parameter model — clearly infeasible. Adapt the refutation plan to the sample size.

### B9: EP uncertainty representation (Issue 16)
Add at minimum a qualitative confidence tier (high/medium/low) to each EP estimate, reflecting confidence in the truth and relevance components.

---

## Adjudicated Category C Issues

- C1 (Issue 10): Proxy penalty 0.05 is ad hoc — note in experiment log, no strategy change needed.
- C2 (Issue 11): Panel conventions not checked — not applicable given n=2 units and stratified design.
- C3 (Issue 13): Refutation test power not quantified — qualitative framing already adequate.
- C4 (Issue 15): Synthetic control category selection — not applicable; SC not proposed.
- C5 (Issue 17): "Corroboration" should be "consistency check" — editorial change before commit.

---

## Regression Assessment

No regressions from Phase 0 detected. All Phase 0 data quality warnings are mapped to systematic uncertainty sources (Section 7 of the strategy, lines 401-415). The EP values trace cleanly from Phase 0 to Phase 1 with documented justifications. The DAG modifications from Phase 0 are documented and defensible.

---

## Verdict Rationale

Two Category A findings remain after adjudication:

**A1 (ITS over-parameterization)** is a clear methodological error that, if uncorrected, would produce unreliable results in Phase 3. The fix is straightforward: specify a 3-parameter primary model and relegate the 6-parameter specification to a sensitivity check. This is resolvable within the current phase.

**A2 (EP truncation override formalization)** is a structural compliance issue. The pragmatic decision to proceed despite chain EP below threshold is substantively correct but procedurally non-compliant. The fix is to rewrite two subsections as a formal downscoping decision. This is also resolvable within the current phase.

Nine Category B findings require attention, but all are addressable through targeted additions and clarifications to the existing strategy text. None require rethinking the analytical approach.

The strategy is fundamentally sound: the method selection is appropriate for the data, the reference analysis survey is thorough, the systematic uncertainty inventory is complete, and the risk assessment is honest. The issues are about specification precision and procedural compliance, not about analytical direction.

**ITERATE** is the correct verdict. Both A findings have clear, actionable fixes. The B findings can be addressed in the same revision pass. No escalation is needed.

---

## Fix Requirements for Iteration

The fix agent must address all A and B issues in a single revision:

1. **[A1]** Replace the 6-parameter ITS specification with a 3-parameter primary model (intercept, pre-trend, level-shift). COVID handling via exclusion robustness, not indicators in the primary model.
2. **[A2]** Rewrite "Critical Assessment" and "Pragmatic Chain Classification" as a formal downscoping decision per methodology/09-downscoping.md Section 12.2.
3. **[B1]** Reframe "quasi-DiD" as "stratified ITS with formal comparison" pending parallel-trends verification.
4. **[B2]** Add DAG 2 vs DAG 3 identifiability discussion.
5. **[B3]** Specify BSTS covariates and feasibility gate.
6. **[B4]** Acknowledge 8-category pre-policy observation constraint.
7. **[B5]** Reconcile CIEFR-HS vs NBS trend contradiction explicitly.
8. **[B6]** Resolved by fix for A2.
9. **[B7]** Clarify economic slowdown control strategy.
10. **[B8]** Adapt refutation test plan to n=10 feasibility.
11. **[B9]** Add qualitative confidence tiers to EP estimates.
12. **[C5]** Change "corroboration" to "consistency check."

DECISION: ITERATE
