# Arbiter Adjudication: Phase 0 — Discovery

## Input Reviews
- Domain Review: 3A, 5B, 3C findings
- Logic Review: 2A, 6B, 4C findings
- Methods Review: 1A, 5B, 4C findings

---

## Issue Adjudication Table

| ID | Finding | Domain | Logic | Methods | Adjudicated Category | Rationale |
|----|---------|--------|-------|---------|---------------------|-----------|
| 1 | CIEFR-HS internal inconsistency: 2017-2019 data shows expenditure decline (10,372 to 6,090 yuan) yet static 73/12/15 composition not reconciled | A | -- | B3 | B | The DATA_QUALITY.md Warning #7 already flags the pre-existing downward trend and Warning #5 notes the 73/12/15 composition may have shifted. The inconsistency is acknowledged but the composition is used only as an approximate structural parameter, not a precise constant. Downgrade from A to B: add explicit note that composition may differ between 2017 and 2019 waves, and downstream phases must not treat it as invariant. |
| 2 | "56.8% of income" claim may be share of expenditure, not income | A | -- | -- | B | Examined the artifact: DISCOVERY.md line 233 says "lowest-income quartile spends 56.8% of income on education vs. 10.6% for highest." The registry.yaml variable is "education_pct_of_income." The VoxChina source uses this framing. The figure is sourced from CIEFR-HS via VoxChina and appears to be education spending as a percentage of income. Without access to the original paper, there is ambiguity, but the claim is attributed and directionally valid (large income share for poor families). Downgrade to B: add a caveat noting this figure should be verified against the original Wei (2024) paper in Phase 1. |
| 3 | No CPI deflation — nominal data over 10 years is unreliable for trend analysis | A | B4 | B2 | A | Three reviewers converge on this. DATA_QUALITY.md Open Issue #4 acknowledges the gap ("All spending figures are nominal. A CPI-adjusted real spending series would be more informative"). However, it is listed only as an open issue, not as a binding constraint. Over 2016-2025, China's cumulative CPI inflation was approximately 15-20%, which is material for interpreting spending trends. NBS CPI data is publicly available and should have been acquired. This is a data acquisition gap that weakens all three DAGs' testable predictions. Retained as Category A: CPI data must be acquired and nominal-vs-real distinction must be added as a binding constraint for downstream phases. |
| 4 | Joint EP truncation paradox — all multi-step chains fall below hard truncation (0.05) | -- | A | -- | B | Examined the artifact. The Logic reviewer correctly notes that multiplying EP values along chains (e.g., 0.63 * 0.24 * 0.16 = 0.024) puts all multi-step chains below the 0.05 hard truncation. However, this reflects a misunderstanding of how truncation operates at Phase 0. The truncation thresholds (per Phase 0 CLAUDE.md) apply to sub-chain expansion decisions in Phase 3, not to top-level DAG viability. The EP values on individual edges are what matter for Phase 0 prioritization, and the joint EP calculation is relevant for deciding whether to expand sub-chains during causal testing. The DAGs themselves are not "truncated" — they are candidate hypotheses to be tested. Downgrade to B: add a clarifying note in DISCOVERY.md that joint EP along full chains is low by construction at Phase 0 (pre-data estimates are conservative), and truncation thresholds apply to Phase 3 sub-chain expansion, not Phase 0 DAG selection. |
| 5 | "Number of children" classified as IMPORTANT but should be CRITICAL | -- | A | -- | B | The Logic reviewer argues that demographic decline is a first-order confounder that should be CRITICAL. Examining the artifact: the Data Requirements Matrix lists "Number of children per household" as IMPORTANT, while "Household income level" is CRITICAL. However, DATA_QUALITY.md Warning #5 already makes demographic decline confounding a binding constraint, and the demographics dataset (#6) is scored MEDIUM (78/100) with good coverage. The variable is adequately covered even at IMPORTANT priority. Downgrade to B: reclassify to CRITICAL in a revision, but this does not block advancement since the data was already acquired and the confounding is already flagged as binding. |
| 6 | No explicit feasibility assessment mapping identification strategies to available data | -- | -- | A | B | The Methods reviewer correctly notes that DISCOVERY.md Section "Methodological Note on Causal Identification" lists 5 identification strategies but does not assess which are feasible given the acquired data. DATA_QUALITY.md partially addresses this — it notes that enforcement-intensity variation is not possible (Dataset #5 granularity: LOW for regional detail), and income-stratified analysis is limited to urban/rural. However, a systematic feasibility mapping is a Phase 1 responsibility, not Phase 0. Phase 0 identifies strategies and data; Phase 1 maps them together into an analysis plan. Downgrade to B: add a note flagging which strategies are clearly infeasible given data gaps, but the full mapping is Phase 1 scope. |
| 7 | CHFS survey not searched as data source | -- | B1 (domain) | -- | B | The China Household Finance Survey (CHFS) from Southwestern University of Finance and Economics is a relevant microdata source that could provide post-policy household spending data. It was not mentioned in the failed datasets or the experiment log. This is a legitimate gap in the data acquisition search. Category B: should be noted as a potential data callback target. |
| 8 | Provincial yearbook data not searched | -- | B2 (domain) | -- | C | Provincial statistical yearbooks may contain education-only spending breakdowns at the subnational level. However, these are typically in Chinese only, behind paywalls, and would require significant manual extraction effort. Reasonable to omit in initial acquisition. Category C: note as a potential enhancement. |
| 9 | Missing liquidity constraint as first principle | -- | B3 (domain) | -- | C | The domain reviewer suggests that liquidity constraints should be a separate first principle. Principle 1 already notes "less applicable if families are liquidity-constrained" as a boundary condition. The concept is present but not elevated to a standalone principle. This is a matter of analytical framing, not a gap. Category C. |
| 10 | Industry size cherry-picks $300B figure | -- | B4 (domain) | -- | B | DISCOVERY.md line 32 uses "USD 300 billion industry pre-policy" while DATA_QUALITY.md notes the range is $70-300B. The $300B figure is at the high end and may overstate the industry's scale. Category B: should use a range or the more conservative estimate. |
| 11 | PISA 2022 results not considered | -- | B5 (domain) | -- | C | PISA 2022 could provide international comparison of student outcomes, but the analysis question is about expenditure, not outcomes. Student outcomes are a secondary variable listed as USEFUL priority. Reasonable to deprioritize. Category C. |
| 12 | Registry uses name not id field | -- | B1 (logic) | B5 (methods) | B | Two reviewers agree. The registry.yaml uses `name` as the identifier rather than a structured `id` field (e.g., ds_001). The Phase 0 CLAUDE.md Step 0.4 specifies that each entry must include an `id` field. This is a schema compliance issue. Category B: add id fields to registry entries. |
| 13 | Economic slowdown missing as confounder | -- | B2 (logic) | -- | B | The DAGs include COVID-19 and demographic decline as confounders but not China's broader economic slowdown (property crisis, youth unemployment, consumer confidence decline). These factors independently affect household spending patterns and are contemporaneous with the policy. Category B: add economic slowdown as an explicit confounder node in the DAGs. |
| 14 | Redundant edges in DAG 2 | -- | B3 (logic) | -- | C | The Logic reviewer notes that Policy -> Underground Market and Industry Collapse -> Underground Market are potentially redundant. Both pathways are theoretically distinct (direct regulatory displacement vs. supply-side labor market displacement), though they are hard to empirically distinguish. This is a DAG design choice, not an error. Category C. |
| 15 | DAG 3 compositional edge (In-School Costs 73% -> Total Expenditure) is definitional not causal | -- | B6 (logic) | -- | B | The Logic reviewer correctly notes that the edge "In-School Costs (73% of Total) -> Total Expenditure Composition Shifts" is a compositional identity, not a causal relationship. An accounting relationship does not belong as a causal edge in a DAG. Category B: restructure this as contextual information rather than a causal edge. |
| 16 | THEORIZED edge truth=0.70 matches LITERATURE_SUPPORTED default | -- | -- | B1 (methods) | C | The Methods reviewer notes some THEORIZED edges use truth=0.70, which is the default for LITERATURE_SUPPORTED. Examining the artifact: the edges in question (Industry Collapse -> Underground Market at 0.70, Competitive Pressure -> Inelastic Demand at 0.70) are labeled LITERATURE_SUPPORTED in the edge tables, not THEORIZED. The edge from Industry Collapse -> Underground Market in DAG 2 is labeled THEORIZED with truth=0.70, which is at the top of the THEORIZED range (0.3-0.7). This is within the allowed range and reflects strong theoretical grounding. Category C: the value is defensible within the specified range. |
| 17 | COVID confounding not operationalized | -- | -- | B4 (methods) | B | DATA_QUALITY.md Warning #4 flags COVID as a binding constraint, but DISCOVERY.md does not specify how COVID will be modeled (dummy variable? interaction term? exclusion of 2020-2021?). This is partially a Phase 1 responsibility, but the DAGs should at minimum specify the confounding mechanism more precisely. Category B. |

---

## EP Adjudication

### 1. EP Assessment Reasonableness
The individual edge EP values are reasonable and well-justified. Truth values align with the label taxonomy (LITERATURE_SUPPORTED at 0.70-0.90, THEORIZED at 0.30-0.70, SPECULATIVE at 0.20). Relevance assessments are appropriately conservative. The overall EP landscape correctly identifies the Policy -> Industry Collapse edge as the strongest (EP=0.63) and downstream chains as progressively weaker.

### 2. Truncation Decision Validity
No chains were truncated at Phase 0, which is correct. The hard/soft truncation thresholds are for Phase 3 sub-chain expansion decisions. The Logic reviewer's concern about all chains falling below 0.05 joint EP reflects Phase 0's conservative pre-data estimates — these will be updated with actual data in Phase 3. No Category A issue here.

### 3. Label Consistency
Edge labels are generally consistent with their justifications. The LITERATURE_SUPPORTED labels cite specific publications. The THEORIZED labels are appropriately used for theoretically grounded but empirically untested edges. No SPECULATIVE edges are over-labeled. One minor issue: the Homework -> Total Expenditure edge (SPECULATIVE, EP=0.08) is appropriately conservative.

### 4. Confidence Band Appropriateness
Phase 0 does not produce formal confidence bands — only point EP estimates. The ranges provided in the methodology (e.g., THEORIZED: 0.3-0.7) serve as implicit bands. Adequate for Phase 0 purposes.

### 5. Causal DAG Validity
The three DAGs represent genuinely different causal hypotheses (direct reduction, regulatory displacement, compositional shift). They share the Policy -> Industry Collapse edge appropriately. The DAG comparison table and kill conditions are well-specified. Issue #15 (definitional edge in DAG 3) is the only structural concern, classified as Category B.

---

## Adjudicated Category A Issues

### A1: CPI Deflation Data Not Acquired (ID #3)
**Three-reviewer consensus.** All spending data is nominal. Over the 2016-2025 analysis window, cumulative inflation is material (15-20%). NBS CPI data is publicly available and was not acquired. DATA_QUALITY.md acknowledges this as an open issue but does not make it a binding constraint. This must be fixed: (1) acquire NBS CPI data (overall and education sub-index), (2) add CPI deflation as a binding constraint in DATA_QUALITY.md warnings, (3) note that all trend analysis in downstream phases must use real (CPI-adjusted) values or explicitly justify using nominal values.

---

## Adjudicated Category B Issues

| ID | Finding | Blocking? | Action Required |
|----|---------|-----------|-----------------|
| 1 | CIEFR-HS 73/12/15 composition inconsistency | No | Add caveat that composition may differ between 2017 and 2019; do not treat as invariant |
| 2 | "56.8% of income" claim ambiguity | No | Add verification note; flag for Phase 1 |
| 4 | Joint EP truncation clarification | No | Add explanatory note about truncation scope |
| 5 | Number of children priority reclassification | No | Reclassify to CRITICAL in data requirements matrix |
| 6 | Identification strategy feasibility note | No | Add brief feasibility flags; full mapping is Phase 1 |
| 7 | CHFS survey not searched | No | Log as potential data callback target |
| 10 | Industry size $300B cherry-pick | No | Use range ($70-300B) instead of upper bound |
| 12 | Registry missing id field | No | Add id fields per schema spec |
| 13 | Economic slowdown confounder missing | No | Add to DAG confounder nodes |
| 15 | DAG 3 definitional edge | No | Restructure as contextual annotation |
| 17 | COVID operationalization | No | Add brief mechanism specification |

None of these B issues individually block advancement. Collectively, they represent normal Phase 0 refinement work. All can be addressed in a single iteration pass.

---

## Adjudicated Category C Issues

- C1: Provincial yearbook data not searched (ID #8) — reasonable to omit
- C2: Liquidity constraint not a standalone principle (ID #9) — already covered as boundary condition
- C3: PISA 2022 not considered (ID #11) — secondary to expenditure focus
- C4: Redundant DAG 2 edges (ID #14) — theoretically distinct pathways
- C5: THEORIZED edge truth=0.70 (ID #16) — within allowed range

---

## Regression Assessment

No regressions detected. This is the initial Phase 0 pass — there are no prior phases from which regression could occur.

---

## Verdict Rationale

The Phase 0 artifacts are substantively strong. The question decomposition is thorough, the three competing DAGs represent genuinely different causal hypotheses with clear kill conditions, the data acquisition covers the feasible public sources, and the DATA_QUALITY.md is unusually honest about limitations (PROCEED WITH WARNINGS gate, 8 binding constraints for downstream phases, 6 failed datasets documented).

**One Category A issue remains after adjudication: the absence of CPI deflation data.** This is a clear data acquisition gap — NBS CPI data is publicly available, the analysis covers a 10-year nominal spending window, and three independent reviewers flagged it. It can be resolved within Phase 0 by running a targeted data acquisition for CPI data and adding a binding deflation constraint.

The 11 Category B issues are all addressable in a single iteration pass and do not require rethinking the analytical approach. They are refinements (clarifying notes, schema fixes, priority reclassifications) rather than structural changes.

The verdict is **ITERATE** because one Category A issue (CPI data) must be resolved before Phase 1 can proceed. Phase 1's strategy formulation depends on knowing whether real vs. nominal analysis is feasible, and the CPI data acquisition is straightforward.

**Iteration scope:**
1. Acquire NBS CPI data (overall index and education sub-index if available, 2016-2025)
2. Add CPI deflation as binding constraint #9 in DATA_QUALITY.md
3. Address the 11 Category B items (all are minor edits to existing artifacts)
4. Re-review after iteration

DECISION: ITERATE
