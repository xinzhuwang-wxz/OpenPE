# Arbiter Adjudication: Phase 0 Discovery

## Input Reviews
- Logic Review: `phase0_discovery/review/logic_review.md`
- Methods Review: `phase0_discovery/review/methods_review.md`
- Domain Review: `phase0_discovery/review/domain_review.md`

## Issue Adjudication Table

| ID | Finding | Logic | Methods | Domain | Adjudicated Category | Rationale |
|----|---------|-------|---------|--------|---------------------|-----------|
| 1 | Joint_EP not computed; data quality EP caps not propagated back to DAG edge tables | A (A1) | -- | -- | **A** | Logic reviewer is correct. DISCOVERY.md presents EP values that do not reflect the DATA_QUALITY.md caps (e.g., SUB-->MID_DECLINE shows EP=0.42 but skill-level data is unavailable, so truth should be capped at 0.30). Without Joint_EP computation, Phase 1 cannot apply truncation thresholds. This is an internal consistency failure between the two Phase 0 artifacts. |
| 2 | All instrumented chains (SCP-->...-->LS) have Joint_EP below soft truncation threshold 0.15 | A (A2) | -- | -- | **B** | The logic reviewer correctly identifies the arithmetic issue but also correctly notes this is likely a conceptual problem with how Joint_EP applies to IV/DID chains, not evidence that the DID strategy lacks explanatory power. The SCP-->DE edge is an instrument, not a mechanism edge. The fix is to document how truncation thresholds apply to IV chains vs. mechanism chains. This is important but does not block advancement -- it requires a clarifying note in DISCOVERY.md, not a redesign. Downgraded from A to B because the resolution is definitional, not substantive. |
| 3 | Collider bias in DAG 2 (conditioning on HC_INV opens GOV--DE path) | A (A3) | -- | -- | **B** | The logic reviewer raises a valid structural concern. However, this issue becomes operative only in Phase 3 when mediation analysis is run. Phase 0 DAGs are hypothesized structures; the collider issue should be documented as a methodological note for Phase 3 but does not block Phase 0 advancement. The concern is that GOV and DE share a common cause (economic development). This is plausible but can be addressed by adding the common cause to the DAG or noting the identification assumption. Downgraded to B: must be documented before Phase 3, not before Phase 1. |
| 4 | Demographic transition omitted as confounder in all DAGs | -- | -- | A (A1) | **A** | The domain reviewer is correct and this was missed by both other reviewers. China's working-age population peaked around 2012, coinciding exactly with the smart city pilot period. Population aging independently drives labor structure change (more service employment, automation incentives, reduced labor supply). The variables exist in the dataset (population_65plus_pct, population_15_64_pct) but appear in no DAG. This is a significant confounder omission that could lead to spurious attribution of demographic-driven changes to the digital economy. Must be added to all three DAGs before Phase 1. |
| 5 | NBS Statistical Yearbook data not attempted despite being publicly available | -- | -- | A (A2) | **A** | The domain reviewer raises a valid point that the five-strategy fallback cascade was not fully executed. The NBS publishes provincial-level employment by sector, GDP, and internet users in publicly accessible yearbook tables. The experiment log does not document any attempt. If successful, this would upgrade the analysis from national time series (T=24) to a provincial panel (31 provinces x ~13 years), which is a qualitative improvement in identification strength. This is blocking because it represents an incomplete execution of the Phase 0 data acquisition protocol. |
| 6 | ILO modeled employment estimates partially endogenous to proposed controls | -- | -- | A (A3) | **B** | The domain reviewer correctly identifies that ILO models use GDP and urbanization as inputs, creating potential mechanical correlation when these variables are used as controls. This is a genuine concern for the national time series analysis. However, the fix is documentation and sensitivity analysis design, not a Phase 0 rework. The concern should be noted in DATA_QUALITY.md warnings and carried forward as a binding constraint for Phase 3 methodology. Downgraded to B because it does not require new data or DAG restructuring -- it requires acknowledgment and a sensitivity analysis plan. |
| 7 | Granger causality requires >=30 observations per time series conventions; data has 24 | -- | A (A1) | -- | **A** | The methods reviewer correctly flags a direct violation of the project's own conventions (`conventions/time_series.md`). The primary fallback identification strategy (Granger causality) does not meet the minimum sample size requirement. If Phase 1 builds around Granger causality and Phase 3 reviewers flag the violation, it forces regression. This must be acknowledged now, with either a justification for why 24 is acceptable (citing small-sample procedures) or an alternative strategy (structural breaks, BVAR, or data callback for quarterly indicators). |
| 8 | Staggered DID methodological concerns not discussed (Goodman-Bacon 2021, Callaway-Sant'Anna 2021) | B (B4) | -- | B (B1) | **C** | Both the logic and domain reviewers flag the absence of staggered DID literature. However, DID is currently blocked by data unavailability. If DID becomes feasible via data callback, the concern is valid, but documenting a methodological requirement for an analysis that may never run is low priority. A brief note in Open Issues is sufficient. Downgraded to C. |
| 9 | DAG 2 direct effect tautologically weak (truth=0.3 for edge being tested) | B (B1) | -- | -- | **B** | The logic reviewer correctly identifies that encoding truth=0.3 for the direct DE-->LS edge presupposes the mediation hypothesis. The kill condition ("direct effect is small") is partially baked into the prior. Setting truth=0.5 (agnostic) would be more honest. This is a real but contained issue. |
| 10 | Quantitative DAG discrimination criteria missing | B (B2) | -- | -- | **B** | Valid. Kill conditions are qualitative. Phase 1 needs quantitative thresholds (e.g., mediation share >60% for DAG 2 preference). Should be documented as an open item for Phase 1. |
| 11 | No SPECULATIVE edges despite plausible candidates (WAGE_POL-->LS, DE-->LM_REF) | B (B3) | -- | -- | **C** | The logic reviewer identifies borderline edges. The current THEORIZED labels with low truth values (0.3-0.4) already produce low EP values. Relabeling to SPECULATIVE would change truth from ~0.4 to ~0.2, modestly lowering already-low EP values. The practical impact on analysis prioritization is negligible. Downgraded to C. |
| 12 | Alternative micro-datasets not explored (CHFS, CHIP, CLDS) | B (B5) | -- | -- | **C** | While these are valid alternative sources, their accessibility constraints are similar to CFPS (registration-gated). Documenting them in Open Issues is useful but not blocking. |
| 13 | Relevance values not normalized for edges entering LS node | B (B6) | -- | -- | **C** | The logic reviewer notes relevance values sum to >1.0 at the LS node. This is a valid observation but relevance in the EP framework represents marginal contribution, not variance partitioning. A clarifying note is sufficient. |
| 14 | DID-to-time-series downscoping lacks formal feasibility evaluation | -- | B (B1) | -- | **B** | The methods reviewer correctly notes that `methodology/09-downscoping.md` exists for this purpose and was not invoked. A structured mapping of which edges can be tested with T=24 national time series would prevent Phase 1 from attempting untestable analyses. |
| 15 | Digital economy composite index lacks sensitivity analysis guidance | -- | B (B2) | B (B2) | **B** | Both methods and domain reviewers flag the need for milestone validation and component sensitivity analysis. Elevating this to a binding Phase 1/2 requirement (not a suggestion) is appropriate. |
| 16 | Mediation analysis design needs stronger specification (time series context) | -- | B (B3) | B (B3) | **B** | Both reviewers converge: Baron-Kenny/Sobel mediation is inappropriate for T=24 time series data. VAR-based mediation or impulse response decomposition is needed. The 60% threshold needs justification. Should be documented as a methodological constraint for Phase 3. |
| 17 | SUTVA mitigation strategy not pre-specified | -- | B (B4) | -- | **C** | DID is currently blocked. Pre-specifying buffer zones and spatial DID for a hypothetical data callback is low priority. A brief note suffices. |
| 18 | Refutation test design for time series fallback not specified | -- | B (B5) | -- | **B** | The methods reviewer correctly notes that DoWhy refutation tests are designed for cross-sectional/panel data. Time series equivalents (placebo treatment, random common cause, subsample stability) need explicit design. This prevents Phase 3 from applying meaningless refutation tests. |
| 19 | Platform economy measurement makes DAG 3 essentially untestable | -- | -- | B (B4) | **B** | The domain reviewer correctly notes that ILO self-employment data conflates traditional self-employment with platform workers. DAG 3's core prediction (opposite-sign effects by segment) cannot be meaningfully tested without micro-data distinguishing platform workers. DAG 3 should be explicitly labeled as a theoretical framework rather than a testable hypothesis with current data. |
| 20 | Digital economy treated as unidimensional in all DAGs | -- | -- | (in text) | **C** | The domain reviewer notes DE should decompose into e-commerce, industrial automation, and digital finance channels. This is a valid refinement but would substantially increase DAG complexity. The composite index approach, while imperfect, is standard in the literature. A note acknowledging this limitation is sufficient for Phase 0. |
| 21 | EP definitional edges (MID_DECLINE-->LS) should be truth=1.0 | -- | C (C1) | -- | **C** | Valid minor point. These are definitional relationships, not empirical claims. |
| 22 | Smart city panel treated/post columns identical | -- | C (C2) | -- | **C** | Minor naming issue. |
| 23 | DAG 3 hukou/SOE labeled as "Moderators" vs confounders | -- | C (C3) | -- | **C** | Notation issue for Phase 3 clarity. |
| 24 | CNNIC provincial internet data not considered | -- | -- | C (C1) | **C** | Minor supplementary source suggestion. |
| 25 | Smart city batch timing sensitivity | -- | -- | C (C2) | **C** | Minor robustness check item. |
| 26 | Edge table citations lack author names | -- | -- | C (C3) | **C** | Minor traceability improvement. |

## EP Adjudication

### 1. EP Assessment Reasonableness
The EP arithmetic is verified correct across all 36 edges (logic reviewer confirmed). Truth and relevance values are consistently mapped to the label taxonomy. The overall EP calibration is reasonable: high-EP edges correspond to well-documented relationships, low-EP edges to speculative ones. DAG 3 appropriately has the lowest EP values, reflecting its more speculative nature.

### 2. Truncation Decision Validity
Joint_EP was not computed in the artifact (Issue 1, Category A). The logic reviewer's computation shows all full-chain Joint_EP values (from SCP through to LS) fall below 0.15. However, this reflects a conceptual issue with applying product-chain truncation to IV designs, not a genuine analytical concern. The resolution should distinguish instrument-relevance chains from mechanism chains and apply truncation only to the latter. Mechanism chains starting from DE are above the hard truncation threshold (e.g., DE-->SUB-->MID_DECLINE-->LS = 0.072). This distinction must be documented.

### 3. Label Consistency
Pre-analysis labels (LITERATURE_SUPPORTED, THEORIZED) are used correctly throughout. No DATA_SUPPORTED labels appear, which is appropriate for Phase 0. The absence of SPECULATIVE labels is a minor concern (Issue 11, downgraded to C) since the affected edges already have low EP values.

### 4. Confidence Band Appropriateness
No confidence bands are produced in Phase 0. The EP truth ranges are used appropriately as qualitative uncertainty indicators. The DATA_QUALITY.md cap of EP.truth at 0.30 for edges lacking adequate data is a sound approach but has not been propagated back to the DAG tables (Issue 1, Category A).

### 5. Causal DAG Validity
The three DAGs are genuinely distinct and represent substantively different causal theories. The DAG structures are acyclic and confounders are appropriately represented. Two structural issues were identified: (a) missing demographic confounder in all DAGs (Issue 4, Category A), and (b) potential collider structure in DAG 2 (Issue 3, Category B). The demographic omission is the more consequential gap.

## Adjudicated Category A Issues

### A-1: Joint_EP not computed and data quality EP caps not propagated (from Logic A1)
DISCOVERY.md presents EP values that are inconsistent with DATA_QUALITY.md constraints. Edges requiring city-level or skill-level data have EP.truth capped at 0.30 in DATA_QUALITY.md, but the DISCOVERY.md edge tables still show uncapped values. Joint_EP values for major chains are not computed, preventing Phase 1 from applying truncation thresholds. **Required action:** (a) Add a data-adjusted EP column or section reflecting the caps. (b) Compute Joint_EP for all major chains (from DE, not SCP -- see Issue 2 rationale). (c) Flag chains below truncation thresholds.

### A-2: Demographic transition omitted as confounder in all DAGs (from Domain A1)
China's working-age population peaked around 2012, precisely when smart city pilots began. Population aging independently drives: increased service sector employment, higher automation incentives, reduced labor supply. The variables population_65plus_pct and population_15_64_pct exist in the dataset but do not appear in any DAG. Omitting this confounder risks attributing demographic-driven structural change to the digital economy. **Required action:** Add a demographic transition node as an explicit confounder in all three DAGs. Include population aging variables as mandatory controls in the Phase 1 strategy.

### A-3: NBS Statistical Yearbook data not attempted (from Domain A2)
The Phase 0 data acquisition protocol specifies a five-strategy fallback cascade before declaring "no data found." The NBS publishes provincial-level employment by sector, GDP, and internet users in publicly accessible yearbook tables (stats.gov.cn). The experiment log documents no attempt to acquire this data. If successful, this would upgrade the analysis from national time series to provincial panel, a qualitative improvement in identification strength. **Required action:** Attempt NBS yearbook data acquisition for key provincial variables. Document the attempt and outcome. If successful, update the downscoping assessment.

### A-4: Granger causality violates conventions minimum of 30 observations (from Methods A1)
The time series conventions file explicitly requires >=30 observations for Granger causality. The available data has T=24. The primary fallback identification strategy does not meet the project's own standards. If unaddressed, this guarantees a regression trigger when Phase 3 reviewers check conventions compliance. **Required action:** Acknowledge the conventions violation explicitly. Either (a) justify why 24 observations is acceptable with citations to small-sample procedures (Toda-Yamamoto), (b) specify alternative methods that work with T=24 (structural break tests at known policy dates, Bayesian VAR), or (c) evaluate whether quarterly sub-indicators could increase T via data callback.

## Adjudicated Category B Issues

| ID | Finding | Status |
|----|---------|--------|
| B-1 | DID chain Joint_EP conceptual issue (from Logic A2) | Must document how truncation applies to IV vs. mechanism chains |
| B-2 | DAG 2 collider bias (from Logic A3) | Must document for Phase 3; does not block Phase 1 |
| B-3 | ILO model endogeneity (from Domain A3) | Must add to DATA_QUALITY.md warnings; sensitivity analysis plan needed |
| B-4 | DAG 2 direct effect tautologically weak (from Logic B1) | Should set truth=0.5 for agnostic prior |
| B-5 | Quantitative DAG discrimination criteria missing (from Logic B2) | Document as binding input for Phase 1 |
| B-6 | Formal feasibility evaluation for downscoping missing (from Methods B1) | Should invoke downscoping protocol per methodology/09-downscoping.md |
| B-7 | Composite index sensitivity analysis guidance needed (from Methods B2, Domain B2) | Elevate to binding Phase 1/2 requirement |
| B-8 | Mediation analysis inappropriate for time series context (from Methods B3, Domain B3) | Document that Phase 3 must use VAR-based mediation, not Baron-Kenny |
| B-9 | Time series refutation test design needed (from Methods B5) | Pre-specify time series equivalents of required refutation tests |
| B-10 | DAG 3 essentially untestable with current data (from Domain B4) | Label as theoretical framework; reduce to secondary priority |

All B items should be addressed in the iteration cycle. They are individually non-blocking but collectively represent significant gaps in the analysis readiness.

## Adjudicated Category C Issues

- C-1: Staggered DID literature note (from Logic B4, Domain B1) -- add brief note to Open Issues
- C-2: No SPECULATIVE labels (from Logic B3) -- minor; current low truth values achieve similar effect
- C-3: Alternative micro-datasets (from Logic B5) -- document in Open Issues
- C-4: Relevance normalization at LS node (from Logic B6) -- add clarifying note
- C-5: DE unidimensional treatment (from Domain text) -- acknowledge as limitation
- C-6: Definitional edge EP values (from Methods C1) -- minor calibration
- C-7: Panel column naming (from Methods C2) -- minor
- C-8: DAG 3 moderator notation (from Methods C3) -- minor notation
- C-9: CNNIC data (from Domain C1) -- supplementary source
- C-10: Batch timing sensitivity (from Domain C2) -- robustness check item
- C-11: Citation specificity (from Domain C3) -- traceability improvement

## Regression Assessment

No regressions detected. This is the first review of Phase 0; no prior versions exist.

## Verdict Rationale

Four Category A issues remain after adjudication:

1. **Joint_EP and data quality caps not propagated** -- an internal consistency failure between DISCOVERY.md and DATA_QUALITY.md that would cause downstream agents to use incorrect EP values.

2. **Demographic confounder omission** -- a substantive gap in all three DAGs that risks confounding the core research question. The required variables already exist in the dataset.

3. **NBS yearbook data not attempted** -- an incomplete execution of the data acquisition protocol that prematurely constrains the analysis to national time series when publicly available provincial data could enable panel methods.

4. **Granger causality conventions violation** -- the primary fallback strategy does not meet the project's own minimum sample size requirement, creating a guaranteed regression trigger if unaddressed.

All four issues are resolvable within Phase 0:
- Issues 1 and 2 require edits to DISCOVERY.md (adding demographic confounder, computing Joint_EP, propagating caps).
- Issue 3 requires a data acquisition attempt (NBS yearbook scraping) with documented outcome.
- Issue 4 requires documentation of the conventions tension and specification of alternative/complementary methods.

None require fundamental redesign of the analysis strategy or upstream changes. The iteration scope is well-defined. The ten Category B items should also be addressed during iteration, as they collectively represent significant analytical gaps.

The underlying Phase 0 work is of high quality: the question decomposition is thorough, the three DAGs are genuinely distinct, the EP calibration is reasonable, and the data quality assessment is commendably honest. The issues identified are addressable additions and corrections, not fundamental flaws.

DECISION: ITERATE
