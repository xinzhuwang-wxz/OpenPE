# Domain Review

## Summary
- **Artifact reviewed**: `phase6_documentation/exec/ANALYSIS_NOTE.md`
- **Date**: 2026-03-29
- **Overall assessment**: Ready for acceptance
- **Category A issues**: 0
- **Category B issues**: 2
- **Category C issues**: 5

## First Principles Assessment

The four first principles are well-chosen and defensible for the education policy evaluation domain.

**Principle 1 (Demand Inelasticity)** is solidly grounded in the shadow education literature (Zhang & Bray 2020; Park et al. 2016). The gaokao-driven positional competition framing is standard in the field and correctly identifies the core behavioral mechanism that would undermine supply-side regulation.

**Principle 2 (Regulatory Displacement / Balloon Effect)** is a universal regulatory economics principle applied appropriately. The citation to approximately 3,000 illegal tutoring operations detected in Q2 2022 (Sixth Tone) is anecdotal but honestly labeled as such.

**Principle 3 (Compositional Fallacy)** is the strongest structural insight in the analysis. The 73/12/15 decomposition from CIEFR-HS provides a quantitative ceiling on the policy's possible effect, which is a genuinely useful analytical contribution. The Wei (2024) citation is appropriate.

**Principle 4 (Implementation Fidelity Gradient)** is reasonable as a context-dependent principle. It correctly notes tier-1 versus smaller-city enforcement variation, which is well-documented in the policy implementation literature.

The competing DAG structure (three DAGs testing direct reduction, displacement, and compositional irrelevance) is well-designed for this domain. The DAGs represent genuinely different mechanisms rather than parameter variations. The causal DAG is consistent with established understanding of how supply-side education regulation interacts with household demand.

No critical domain relationships are missing from the DAG. One could argue for an explicit "macroeconomic slowdown" node separate from COVID, given China's broader economic deceleration in 2022-2024, but this is partially captured through the income control variable.

## Data Source Validity Assessment

The data portfolio is appropriate but constrained. The analysis correctly identifies its binding limitation: the NBS "education, culture and recreation" proxy is a composite category that bundles education with non-education spending. This is honestly flagged throughout.

**NBS data (ds_001, ds_008, ds_009, ds_013):** These are authoritative sources from China's national statistical office. The quality scores (68-81) are reasonable. The back-calculation caveat for 2016-2018 data (Constraint 8) is an important and honest disclosure.

**CIEFR-HS (ds_002):** Appropriate source for pre-policy spending composition. The limitation to 2017 and 2019 waves (no post-policy data) is correctly flagged as a binding constraint.

**Tutoring industry data (ds_004):** MEDIUM quality (53) is appropriately conservative. The 92-96% closure rate is documented across multiple sources (Huang et al. 2025; Chen et al. 2025) and is the most robust finding in the entire analysis.

**Underground tutoring prices (ds_011):** LOW quality (33) is honest and appropriate. The analysis correctly limits its use to anecdotal evidence without building quantitative claims on it.

The failed acquisition of CFPS post-2021 microdata and CIEFR-HS Wave 3 is the most consequential data gap. The analysis correctly identifies this as the single most valuable future data acquisition.

## Methodology Assessment

**ITS model specification.** The 3-parameter segmented regression is appropriate for a nationwide policy with no untreated control group. The choice of ITS over DiD is correctly justified (no parallel untreated region exists). The 2020 exclusion for COVID is defensible and the analysis confirms algebraic equivalence with a COVID-indicator specification.

**Sample size concern.** With 9 observations and 3 parameters (6 degrees of freedom), the analysis operates at the minimum for OLS inference. The analysis is transparent about this: diagnostics have "very low statistical power" and bootstrap estimates from 4 pre-period observations are "biased downward." This honesty is appropriate.

**Per-birth normalization.** This is the most important analytical test in the document. The finding that normalizing by births eliminates the level shift (p=0.48) is a clean and powerful result that correctly undermines the policy attribution. The analysis appropriately elevates this as "the single most important finding."

**Compositional ceiling argument.** The logic is sound: if tutoring is 12% of total education spending, the observed 23.7% decline cannot be solely policy-driven. This arithmetic constraint is a valuable contribution independent of the statistical modeling.

**Refutation battery.** The 3 core tests plus the supplementary COVID-date placebo are well-designed. The honest acknowledgment that the random common cause test is "mechanically uninformative" at n=9 is a mark of analytical rigor rarely seen.

**OLS counterfactual as "secondary method."** The analysis correctly notes that both methods are OLS-based, providing "less independent corroboration than a true Bayesian structural time series model would." This is an honest and important caveat.

## Systematic Uncertainty Assessment

The uncertainty decomposition is thorough and well-structured. The finding that systematic uncertainty constitutes 80% of total variance, with COVID handling alone at 60.9%, is plausible and important. It correctly implies that more observations will not improve precision -- better data quality is needed.

The seven uncertainty sources cover the relevant dimensions: COVID handling, statistical noise, intervention timing, proxy variable error, method disagreement, pre-period window, and CPI deflator choice. The ranking is reasonable: COVID handling should dominate given the temporal overlap.

Total uncertainty of +/-284 yuan on a -483 yuan estimate producing 1.7 sigma significance is internally consistent and honestly reported.

## Verification Assessment

Phase 5 verification is thorough. The independent reproduction of the ITS level shift (exact match using numpy-based OLS) and all 4 refutation test outcomes provides confidence in the numerical results. The SHA-256 hash verification for all 13 datasets is appropriate provenance auditing.

The PARTIAL status on signal injection (verified from primary analysis output rather than independently re-run) is a minor gap but documented transparently.

## EP and Causal Claim Assessment

**EP values are reasonable.** The primary edge (Policy to Aggregate Spending) at EP=0.20 with CORRELATION classification is defensible given the COVID placebo failure and per-birth normalization null result. The downgrade from what would have been DATA_SUPPORTED (3/3 core refutation PASS) to CORRELATION based on the supplementary COVID-date placebo is a conservative and appropriate judgment call.

**All edges classified CORRELATION or HYPOTHESIZED.** No edge achieves DATA_SUPPORTED. This is honest given the data limitations (proxy outcome, no microdata, COVID confounding).

**Chain truncation is appropriate.** All multi-step chain Joint EP values below 0.05 (DAG 1 at 0.0017, DAG 2 at 0.011) reflect the multiplicative decay through weak edges. The formal downscoping from chain-level to edge-level claims is well-justified.

**EP decay schedule.** The CORRELATION 2x decay rate (squared multipliers) produces a useful horizon of 2029 (4 years). This is reasonable. The PROJECTION.md mentions a useful horizon of 2032 (7 years), which is inconsistent with the ANALYSIS_NOTE.md's 2029 figure. See Category B issue below.

**One concern:** The Policy to Industry Collapse edge has EP=0.56 with CORRELATION classification but was never subjected to the refutation battery (literature-based only). This is disclosed, but the EP=0.56 seems high for an edge that has not been empirically tested within this analysis. In the EP summary table, it is the highest-EP edge, yet it rests entirely on literature synthesis rather than original empirical work. This does not invalidate the analysis (the downstream chain Joint EP is 0.0017 regardless), but it could mislead a reader about where evidence is strongest.

## Result Plausibility

**ITS level shift of -483 yuan (national).** This represents approximately 23.7% of pre-policy mean spending. The magnitude is large but plausible as a composite of COVID, demographic, and possible policy effects. The analysis correctly argues it cannot all be policy-driven.

**Urban-rural differential (3.7x).** Directionally consistent with the roughly 2.6x ratio in tutoring participation rates (47% urban / 18% rural). The slightly larger spending ratio (3.7x vs 2.6x participation ratio) is plausible because urban tutoring was more expensive per session.

**Per-birth normalization null result (p=0.48).** This is the cleanest result in the analysis. It directly tests whether the aggregate decline reflects per-child spending changes or demographic composition effects. The null finding is internally consistent with the 47% birth decline over 2016-2024.

**Scenario projections.** The conditional probability assignments (15-25% / 45-55% / 25-35%) sum to 95-115%, which is acceptable given they are ranges. Scenario B (Status Quo) as most probable is consistent with the empirical evidence.

**Birth figure.** The analysis note states births declined to 9.54 million in 2024 (line 91) but Figure 4 caption mentions 9.0 million in 2024. The verification report confirms 9.54 million from ds_006. This discrepancy in the figure caption needs correction.

**Internal consistency check on the 23.7% figure.** The ITS level shift is -483 yuan. The pre-policy mean (rough estimate from the counterfactual at 2025 of 3,469 yuan minus the gap of 483) is approximately 2,037 yuan at the pre-period mean or approximately 2,039 yuan for 2019. The 23.7% figure relative to the pre-policy mean appears to be computed relative to a counterfactual, not a raw pre-period mean. The analysis should clarify which denominator produces 23.7%.

## Issues by Category

### Category A (Blocking)

None.

### Category B (Important)

1. **[B1]: Useful projection horizon inconsistency between ANALYSIS_NOTE.md and PROJECTION.md.**
   - The ANALYSIS_NOTE states the useful horizon is **2029** (4 years, Section on EP Decay). PROJECTION.md states the useful horizon is **2032** (7 years, Summary paragraph). These are inconsistent. The EP decay table in the ANALYSIS_NOTE itself shows EP falling below hard truncation (0.05) at the mid-term horizon (3-7 years from 2025), which would be 2028-2032, with the exact crossing depending on interpolation. The 2029 figure and 2032 figure are both within this range but should be reconciled to a single consistent number with a stated basis.
   - Domain impact: Readers relying on the projection horizon for planning purposes would get different guidance depending on which section they read.
   - Suggested action: Pick one defensible number, state it consistently in both documents, and explain the calculation (e.g., the year at which effective EP crosses 0.05).

2. **[B2]: Birth figure discrepancy between text and figure caption.**
   - Line 91 states births fell to 9.54 million in 2024. The caption for Figure 4 (fig:per-child, line 115) states births declining to 9.0 million in 2024. The verification report confirms 9.54 million from ds_006. The figure caption appears incorrect.
   - Domain impact: Incorrect demographic figures undermine the credibility of the demographic confounding argument, which is the analysis's most important finding.
   - Suggested action: Correct the figure caption to 9.54 million (or whatever the verified 2024 figure is from ds_006). If 9.0 million is a projection for a later year, label it accordingly.

### Category C (Minor)

1. **[C1]: The 23.7% aggregate decline denominator is not explicitly stated.**
   - The text says "observed aggregate decline of 23.7%" (line 166) but does not specify whether this is relative to the pre-policy mean, the 2019 value, or the counterfactual. Clarifying the denominator would improve reproducibility.
   - Suggested action: Add a parenthetical specifying the reference value.

2. **[C2]: The @sixthtone2022crackdown citation for "approximately 3,000 illegal tutoring operations" would benefit from a more precise attribution.**
   - The Sixth Tone article is a news report. If the 3,000 figure originates from the Ministry of Education or another official source cited within that article, the primary source should be cited.
   - Suggested action: Add the primary government source if identifiable.

3. **[C3]: The Policy to Industry Collapse edge (EP=0.56) was not subjected to a refutation battery but has the highest EP in the summary table.**
   - This is disclosed in the EP table ("literature-based") and in Phase 3, but a brief explicit note in the analysis note explaining why this edge was not refutation-tested (industry-level data on closures is not suitable for the ITS framework designed for spending outcomes) would preempt reader confusion.
   - Suggested action: Add one sentence explaining the methodological reason this edge was assessed via literature synthesis rather than the standard refutation pipeline.

4. **[C4]: The wei2024household BibTeX entry attributes the CIEFR-HS findings to "Wei, Shangjin" as sole author.**
   - The CIEFR-HS (China Institute for Educational Finance Research Household Survey) data is typically reported by multiple authors. The BibTeX entry should be verified against the actual publication.
   - Suggested action: Verify the author list for the cited ECNU Review of Education article and correct if needed.

5. **[C5]: The analysis note uses "shuangjian" as the romanization of Double Reduction.**
   - The standard pinyin is "shuang jian" (two words). This is a minor transliteration point but could matter to domain specialists.
   - Suggested action: Use "shuang jian" or the more common full form "shuangjian" with a note that it abbreviates "jian fu" (reduce burden) applied to both homework and tutoring.

## Acceptance Readiness

This analysis note is ready for acceptance after addressing the two Category B issues. Both are straightforward corrections (reconcile the projection horizon number; fix the birth figure in one caption) that do not require re-analysis.

The analysis is unusually honest about its limitations. The framing is careful: every causal claim is hedged appropriately, the CORRELATION classifications are well-justified, the downscoping from chain-level to edge-level claims is principled, and the data quality constraints are carried through every section. The per-birth normalization null result and the compositional ceiling argument are genuinely valuable analytical contributions that go beyond standard ITS reporting.

The policy context is accurate. The Double Reduction policy details (July 2021, for-profit academic tutoring ban for compulsory education, stated goal of reducing family burden) are correct. The tutoring industry collapse metrics (92-96% offline closure, New Oriental and TAL revenue declines) are consistent with published sources. The references are appropriate and span peer-reviewed articles (Huang et al. 2025, Chen et al. 2025, Liu et al. 2025), working papers, and institutional data sources.

The central conclusion -- that the policy's effect on total household education expenditure is not distinguishable from COVID and demographic confounding -- is the most defensible conclusion available from macro-level aggregate data. The analysis does not overclaim, and it clearly identifies what data would be needed to resolve the remaining uncertainty (CFPS post-2021 microdata). This is a well-executed analysis operating honestly within severe data constraints.
