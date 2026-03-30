# Arbiter Adjudication: Phase 1 Strategy

## Input Reviews
- Logic Review: `phase1_strategy/review/logic_review.md`
- Methods Review: `phase1_strategy/review/methods_review.md`
- Domain Review: `phase1_strategy/review/domain_review.md`

All three reviewers recommend ITERATE. The logic reviewer identified 2 Category A issues, the methods reviewer identified 1 Category A issue, and the domain reviewer identified 3 Category A issues. The total pool of unique findings, after deduplication, is adjudicated below.

---

## Issue Adjudication Table

| ID | Finding | Logic | Methods | Domain | Adjudicated Category | Rationale |
|----|---------|-------|---------|--------|---------------------|-----------|
| 1 | Summary contains stale Phase 0 EP values conflicting with body | A (L-A1) | -- | -- | **A** | Verified against artifact. Summary line 5 cites EP=0.12 for DE-->LS and Joint_EP=0.043 for mediation, but Section 3.2 gives 0.06 and Section 3.3 gives 0.021. Also claims "all mechanism-level Joint_EP values fall below hard truncation" when DE-->SUB=0.32 and DE-->CRE=0.27 are well above. Downstream agents read the Summary first; incorrect EP values here will propagate wrong truncation decisions. Clear blocking issue. |
| 2 | DE-->LS truth derivation inconsistency (starts from 0.30 without applying data quality penalty applied to other edges) | A (L-A2) | -- | -- | **B** | Examined the artifact. The Phase 0 THEORIZED truth for DE-->LS was already 0.30 (not the 0.70 LITERATURE_SUPPORTED base). The strategy applies method (-0.05) and construct (-0.10) penalties but not the data quality (-0.10) penalty. However, the Phase 0 truth of 0.30 already reflects the THEORIZED label, which itself embodies uncertainty about data and theory. Applying the full stack of penalties on top of an already-reduced base risks double-penalizing. The correct fix is to add a sentence explaining why the data quality penalty is not applied to edges whose Phase 0 truth was already capped at the THEORIZED level (0.30). The resulting EP=0.06 vs. the alternative EP=0.02 does not change the chain classification (both are below soft truncation, both above hard truncation), so the analytical consequence is limited. Downgraded from A to B because the classification does not change and the fix is a clarifying sentence, not a recalculation. |
| 3 | Proxy DID labeling creates misleading causal framing | -- | -- | A (D-A1) | **A** | The methods reviewer also flags the proxy DID specification as problematic (M-A1) but focuses on the econometric invalidity rather than the labeling. The domain reviewer's point is well-taken: "proxy DID" implies a level of causal identification (treatment vs. control comparison) that does not exist. The strategy's own limitations section (Section 2.5) is honest, but the DID label persists throughout the document and into the analysis tree. Renaming to "structural break analysis" or "pre/post comparison" while retaining the Chow/Bai-Perron methodology is low-effort and high-value. Accepted as Category A. |
| 4 | Proxy DID regression specification is econometrically invalid for I(1) series | -- | A (M-A1) | -- | **A** | The OLS specification in Section 2.5 regresses levels of I(1) variables with a binary indicator. This produces spurious regression regardless of the interaction term. The strategy identifies spurious regression as "existential risk" (Section 5.2) but does not connect this to the proxy DID specification. The fix is straightforward: condition the proxy DID on cointegration results or specify in first differences. Accepted as Category A. |
| 5 | ILO model endogeneity requires primary treatment, not sensitivity-check treatment | -- | -- | A (D-A2) | **B** | The domain reviewer argues this should be elevated from Open Issue 6 to a primary systematic uncertainty. The concern is valid: if ILO modeled estimates mechanically incorporate GDP/urbanization, regressions on GDP-correlated regressors produce mechanical coefficients. However, the strategy already plans specifications with and without GDP/urbanization controls (Section 5.3, Open Issue 6). The domain reviewer's request to investigate the ILO modeling methodology and consider NBS census cross-checks is a good enhancement but is more appropriate as a Phase 2 investigation task than a Phase 1 strategy rewrite. The strategy should elevate this from Open Issue 6 to the systematic uncertainty table (Section 5.2) at severity HIGH, and add an explicit Phase 2 deliverable to document the ILO methodology for China. Downgraded from A to B because the core mitigation (with/without controls) is already planned; what is missing is prominence and a Phase 2 investigation commitment. |
| 6 | Reverse causality missing from systematic uncertainty inventory | -- | -- | A (D-A3) | **B** | The domain reviewer notes that reverse causality (employment structure driving DE adoption) is identified in DISCOVERY.md Hidden Assumption 5 but absent from the Section 5 uncertainty inventory. This is a gap, but the Toda-Yamamoto Granger test is bidirectional by design (tests both DE-->employment and employment-->DE). The fix is a single row addition to the uncertainty table. Downgraded from A to B because the test is already planned; the issue is documentation completeness, not an analytical gap. |
| 7 | Cholesky-ordered mediation should not be primary method at annual frequency | -- | B (M-B2) | B (D-B1) | **B** | Both methods and domain reviewers agree. At annual frequency, the contemporaneous restriction in Cholesky ordering is hard to defend. Both recommend generalized impulse responses (Pesaran and Shin 1998) as primary. The methods reviewer additionally proposes reporting all 6 permutations and VECM-based mediation. Accepted as B with strong recommendation to implement. |
| 8 | Power analysis should be ex ante, not ex post | -- | B (M-B3) | B (D-B3) | **B** | All three effectively agree (logic reviewer also raises this as L-B2). Power analysis in Phase 2 would set minimum detectable effect sizes before testing. Without it, null results are uninterpretable. Accepted as B. |
| 9 | Pre-labeling DE-->LS as HYPOTHESIZED before refutation | B (L-B1) | -- | -- | **C** | The strategy states the edge will be "labeled as HYPOTHESIZED regardless of statistical significance." Given EP=0.06, this is a reasonable prior expectation. The fix is minor wording: "Expected to be classified as HYPOTHESIZED given low EP; actual classification determined by Phase 3 refutation results." Downgraded to C as it is a phrasing improvement. |
| 10 | No data callback trigger criterion for NBS provincial data | B (L-B3) | -- | -- | **C** | The logic reviewer asks for a specific trigger. This is good practice but not blocking. The strategy already identifies the callback option (Section 11, Open Issue 1). A concrete trigger (e.g., "if M2 fails for all sectors") would be better but is a refinement. Downgraded to C. |
| 11 | No nonlinearity test despite Reference 3 inverted-U finding | B (L-B4) | -- | -- | **B** | Reference 3 (Zhao and Li 2022) documents an inverted-U relationship. The strategy does not plan any nonlinearity test. A quadratic DE term or threshold test is low-effort and addresses a finding from a directly relevant reference analysis. Accepted as B. |
| 12 | Collider bias mitigation is insufficient (generalized IRFs do not address collider bias) | B (L-B5) | -- | -- | **B** | The logic reviewer correctly notes that generalized impulse responses address ordering sensitivity, not collider bias. These are different problems. The fix is to explicitly draw the potential collider path and assess plausibility, or note the mediation finding should be labeled CORRELATION at best. Accepted as B. |
| 13 | Lewis-Kuznets structural transformation confounding underweighted | -- | -- | B (D-B2) | **B** | The domain reviewer argues that sectoral employment shifts conflate DE effects with the broader structural transformation. The strategy acknowledges this in Section 12 (Domain Context) but does not elevate it to the uncertainty inventory. The suggested specification (testing whether DE loses significance after partialling out GDP/urbanization growth) is a valuable addition. Accepted as B. |
| 14 | Out-of-sample validation plan needs revision (COVID in test period) | -- | -- | B (D-B4) | **C** | The strategy already acknowledges the COVID problem in the test window. With T=24, formal out-of-sample validation is effectively infeasible. The domain reviewer's suggestion of leave-one-out within pre-COVID sample is reasonable but optional. Downgraded to C. |
| 15 | Bootstrap resampling scheme not specified | -- | B (M-B1) | -- | **B** | The methods reviewer correctly notes that "bootstrap" is underspecified. Residual vs. wild bootstrap matters at T=24. A paragraph specifying the algorithm is needed. Accepted as B. |
| 16 | COVID-19 handling deferred without a default | -- | B (M-B4) | -- | **C** | The methods reviewer wants a default specified now. The domain reviewer (C2) also mentions this. Having a default is good practice but the three options listed are all reasonable. Phase 2 EDA is the right place to make this decision with data in hand. Downgraded to C. |
| 17 | Joint_EP accounting for VAR mediation is internally contradictory | -- | B (M-B5) | -- | **B** | The mediation chain is "below hard truncation" (Joint_EP=0.021) but analysis proceeds anyway at "Lightweight" level using the first-link EP (0.23). The strategy needs a clarifying note that VAR-based mediation EP is assessed at the system level, not as a chain product. Accepted as B. |
| 18 | No multicollinearity diagnostics for VAR system | -- | B (M-B6) | -- | **B** | At T=24 with trending variables, VIF or condition number diagnostics should be a Phase 2 deliverable. The parsimony constraint (no more than 3 endogenous variables at T=24 with lag=2) should be explicit. Accepted as B. |
| 19 | Section numbering inconsistency / hand-numbering | C (L-C1) | -- | -- | **C** | Per CLAUDE.md, pandoc adds numbering. Hand-numbered sections will double-number in PDF. Minor formatting fix. |
| 20 | "Lightweight-to-moderate" is not a defined tier | C (L-C2) | -- | -- | **C** | Use standard tier names from methodology. |
| 21 | Mermaid style directives may not render universally | C (L-C3) | C (M-C3) | -- | **C** | Add shape differentiation for accessibility. |
| 22 | Reference analysis survey lacks a time series precedent | -- | C (M-C1) | -- | **C** | Would strengthen the methodological grounding. |
| 23 | Bootstrap seed sensitivity: 3 seeds is minimal | -- | C (M-C2) | -- | **C** | Report IQR across 50 seeds rather than point estimates from 3. |
| 24 | EP update notation could use explicit formula | -- | C (M-C4) | -- | **C** | Minor clarity improvement. |
| 25 | Bai-Perron implementation gap | -- | -- | C (D-C1) | **C** | Confirm ruptures in Phase 2; fallback to Chow at known dates is acceptable. |
| 26 | Collider bias needs explicit DAG representation | -- | -- | C (D-C3) | **C** | Subsumed by adjudicated issue 12 (B). |

---

## EP Adjudication

### 1. EP Assessment Reasonableness
All edge-level EP calculations verified correct by the logic reviewer. The Phase 1 values are uniformly lower than Phase 0, reflecting data quality, construct validity, and method credibility penalties. The highest single-edge EP (DEMO-->LS at 0.36) appropriately reflects the demographic confounder's dominance. The EP framework is applied rigorously.

### 2. Truncation Decision Validity
Truncation decisions are correct at the edge level. DE-->SUB (0.32) receives full analysis. DE-->CRE (0.27) receives lightweight treatment. The mediation chain (Joint_EP=0.021) is correctly below hard truncation; the workaround of testing reduced-form relationships is reasonable but needs better EP accounting (Issue 17). The Summary paragraph (Issue 1) contradicts the body by claiming all mechanism-level Joint_EP values fall below hard truncation, which is factually wrong.

### 3. Label Consistency
No labels are assigned yet (Phase 1 is strategy). The pre-labeling of DE-->LS as HYPOTHESIZED (Issue 9) is downgraded to C with a wording fix. The planned refutation-based classification protocol is sound.

### 4. Confidence Band Appropriateness
Not yet applicable (no estimation in Phase 1). The strategy's plan for bootstrap confidence intervals is appropriate for T=24.

### 5. Causal DAG Validity
The Phase 1 DAG is acyclic, consistent with chain planning, and defensible. The consolidation from three Phase 0 DAGs to one testable DAG is well-motivated. Missing edges: reverse causality (employment-->DE) is not in the DAG but should be noted in the uncertainty inventory (Issue 6). The Lewis-Kuznets confounding path (Issue 13) is acknowledged in prose but not in the DAG.

---

## Adjudicated Category A Issues

**A-1 (from Logic L-A1): Summary contains stale Phase 0 EP values.**
The Summary paragraph cites EP=0.12 for DE-->LS (Phase 1 value is 0.06), Joint_EP=0.043 for mediation (Phase 1 value is 0.021), and claims "all mechanism-level Joint_EP values fall below hard truncation" when DE-->SUB=0.32 and DE-->CRE=0.27 are well above. This is the highest-priority fix because the Summary is the first thing downstream agents read. Required action: rewrite the Summary to use Phase 1 EP values from Section 3.2/3.3.

**A-2 (from Domain D-A1, partially supported by Methods M-A1): Proxy DID labeling and specification.**
Two distinct sub-issues that are related:
- (a) The label "proxy DID" implies causal identification that does not exist. Rename to "structural break analysis" or "pre/post comparison" throughout.
- (b) The OLS specification in Section 2.5 regresses levels of I(1) variables, producing spurious regression. Either condition on cointegration or specify in first differences.
Both sub-issues are blocking. The methodology is legitimate (Chow test, Bai-Perron); only the framing and the specific regression specification need correction.

---

## Adjudicated Category B Issues

| ID | Finding | Blocks? | Action |
|----|---------|---------|--------|
| 2 | DE-->LS truth derivation needs clarifying sentence | No | Add explicit reasoning for why data quality penalty is not double-applied to THEORIZED edges |
| 5 | ILO model endogeneity needs elevation to systematic uncertainty table | No | Move from Open Issue 6 to Section 5.2 at HIGH severity; add Phase 2 investigation deliverable |
| 6 | Reverse causality missing from uncertainty inventory | No | Add one row to Section 5.2 cross-referenced to bidirectional Granger test |
| 7 | Cholesky ordering: generalized IRFs should be primary | No | Swap Cholesky to secondary; generalized IRFs as primary; report all 6 orderings |
| 8 | Power analysis should be ex ante (Phase 2 deliverable) | No | Add MDES computation to Phase 2 deliverables list (Section 7.2) |
| 11 | No nonlinearity test despite Reference 3 finding | No | Add quadratic DE term or threshold test as Phase 3 robustness check |
| 12 | Collider bias mitigation conflates ordering with collider problem | No | Draw potential collider path; assess plausibility; note mediation finding capped at CORRELATION |
| 13 | Lewis-Kuznets confounding underweighted | No | Add to uncertainty inventory; include specification that partials out GDP/urbanization growth |
| 15 | Bootstrap resampling scheme unspecified | No | Add paragraph specifying residual bootstrap under the null |
| 17 | VAR mediation EP accounting internally contradictory | No | Add clarifying note that VAR mediation EP is system-level, not chain-product |
| 18 | No multicollinearity diagnostics or parsimony constraint | No | Add VIF/condition number to Phase 2 deliverables; explicit parsimony rule for VAR at T=24 |

None of these B issues individually blocks advancement, but collectively they represent a significant set of gaps that should be addressed in the iteration cycle alongside the A issues.

---

## Adjudicated Category C Issues

- C-9: Pre-labeling DE-->LS as HYPOTHESIZED -- fix wording to "expected" classification
- C-10: Data callback trigger criterion -- add concrete trigger to milestone table
- C-14: Out-of-sample validation plan -- acknowledge as pro forma or add leave-one-out
- C-16: COVID-19 default -- add a default preference (COVID dummy) while allowing Phase 2 override
- C-19: Section numbering -- remove hand-numbering per CLAUDE.md instructions
- C-20: "Lightweight-to-moderate" -- use defined tier names
- C-21: Mermaid style directives -- add shape differentiation for accessibility
- C-22: Add a time series reference analysis
- C-23: Bootstrap seed sensitivity -- increase from 3 to 50 seeds
- C-24: EP update formula -- add explicit formula
- C-25: Bai-Perron package -- confirm in Phase 2

---

## Regression Assessment

No regressions detected. All EP values decreased from Phase 0 to Phase 1, which is expected. The Phase 0 data quality warnings are fully propagated. The Summary's citation of Phase 0 values (Issue A-1) is a failure to update, not a regression from a previous phase's quality.

---

## Verdict Rationale

Two Category A issues remain after adjudication:

1. **A-1 (Summary with stale EP values)**: The Summary provides incorrect EP values and truncation classifications that would mislead downstream agents. This is a straightforward fix (rewrite one paragraph) but is blocking because it is the primary entry point for Phase 2 and Phase 3 agents.

2. **A-2 (Proxy DID labeling and specification)**: The "proxy DID" label overstates identification strength, and the OLS specification in levels is econometrically invalid for I(1) series. Both sub-issues are fixable within Phase 1: rename to "structural break analysis" and revise the specification to condition on cointegration or use first differences.

Additionally, 11 Category B issues collectively represent a meaningful gap in the strategy. The most important are: the bootstrap scheme specification (B-15), the Cholesky ordering primary/secondary swap (B-7), the power analysis commitment (B-8), and the ILO endogeneity elevation (B-5). These are all low-effort additions (one paragraph each) that materially improve the strategy.

All issues are resolvable within Phase 1. No upstream regression is detected. No human judgment is required. The appropriate verdict is ITERATE.

DECISION: ITERATE
