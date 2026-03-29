# Domain Review

## Summary
- **Artifact reviewed**: `phase0_discovery/exec/DISCOVERY.md`, `phase0_discovery/exec/DATA_QUALITY.md`, `phase0_discovery/data/registry.yaml`
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 3
- **Category B issues**: 5
- **Category C issues**: 3

## First Principles Assessment

The four first principles are well-chosen and domain-appropriate:

1. **Demand Inelasticity Under Status Competition** -- correctly identifies the gaokao-driven positional goods dynamic. This is well-grounded in the shadow education literature (Bray 2021, Zhang & Bray 2020).

2. **Regulatory Displacement (Balloon Effect)** -- appropriate cross-domain principle. The parallel to prohibition economics is apt. Correctly labeled UNIVERSAL.

3. **Compositional Fallacy in Policy Evaluation** -- a sound methodological principle. The 73/12/15 split is central to the analysis and well-sourced from CIEFR-HS.

4. **Implementation Fidelity Gradient** -- relevant for China's multi-level governance structure. Correctly labeled CONTEXT-DEPENDENT.

**Missing principle:** There is no principle addressing **income effects and wealth constraints**. The analysis mentions income heterogeneity repeatedly but does not elevate it to a first principle. For lower-income families, the tutoring ban may genuinely reduce spending because they were liquidity-constrained and the ban removes a social obligation they could not afford. This is a distinct mechanism from demand inelasticity (which assumes substitution capacity). This omission matters because it means DAG 1 (policy success) lacks a theoretically grounded mechanism -- it currently relies on a simple "supply destruction = savings" logic rather than articulating WHY some households would not substitute.

The causal DAGs represent genuinely distinct hypotheses. DAG 1 (policy success via supply destruction), DAG 2 (regulatory displacement via underground markets), and DAG 3 (compositional shift / narrow targeting) have materially different structures and testable predictions. The shared edge (Policy -> Industry Collapse) is correctly identified as common ground.

The DAG comparison table and kill conditions are well-specified and actionable.

## Data Source Validity Assessment

The data acquisition is thorough given the constraints of this domain. The key sources are appropriate:

- **NBS consumption data** is the standard macro-level source for Chinese household spending. The proxy problem (education bundled with culture and recreation) is correctly identified and prominently flagged.
- **CIEFR-HS** is the authoritative source for education spending decomposition in China. The analysis correctly identifies that only pre-policy waves (2017, 2019) are publicly available.
- **World Bank indicators** are appropriately used for context variables.
- **NBS income data** is the correct source for income controls.

**Critical data interpretation issue (Category A):** The CIEFR-HS data as extracted shows a puzzling pattern. The compulsory education 2017-vs-2019 table shows total expenditure declining from 6,562/8,995 yuan (2017, elementary/junior high) to 4,014/6,103 yuan (2019). DISCOVERY.md reports this as "10,372 yuan (2017) to 6,090 yuan (2019)" which appears to be an average or weighted figure not directly visible in the processed data. More importantly, the 2019 data shows in-school expenditure *dropping dramatically* (e.g., elementary national from 3,999 to 1,679 yuan) while out-of-school expenditure *increased* (5,456 to 6,731 yuan). This pattern is the OPPOSITE of what the 73/12/15 composition split implies. If in-school spending fell and out-of-school spending rose between 2017 and 2019, the pre-policy trend is moving in the wrong direction for the DAG 3 narrative. This needs to be reconciled -- it may reflect a survey methodology change between waves or a genuine structural shift. The analysis does not discuss this internal inconsistency.

**Missing sources (Category B):**

- **China Household Finance Survey (CHFS)** from Southwestern University of Finance and Economics is a major nationally representative household survey that includes education expenditure items. It was not searched for or mentioned. It may have more recent waves than CFPS.
- **Provincial statistical yearbooks** -- some provinces (notably Beijing, Shanghai, Guangdong) publish education spending breakdowns at finer granularity than the national NBS series. These were not searched for.
- **PISA 2022 results** -- China participated in PISA 2022 (though only in select regions). The PISA questionnaire includes household education spending questions and would provide a post-policy data point with international comparability.

## Methodology Assessment

The identification strategies listed in the Methodological Note are appropriate and comprehensive. The grade 9/10 regression discontinuity idea is particularly clever -- compulsory education (grades 1-9) is covered by the policy while high school is not, creating a sharp cutoff.

The data requirements matrix correctly maps variables to DAG edges with appropriate priority levels. The CRITICAL/IMPORTANT/USEFUL classification is reasonable.

**Concern:** The analysis does not discuss the **Engel curve** approach, which is a standard tool in household expenditure analysis. As income grows, the share of education spending follows a predictable pattern. Deviations from the Engel curve post-policy would be informative for distinguishing real spending changes from income effects. This should be flagged for Phase 1.

## Systematic Uncertainty Assessment

The DATA_QUALITY.md document is unusually thorough and honest for a Phase 0 artifact. The proxy variable warning is handled correctly and the eight binding constraints for downstream agents are well-calibrated.

**Specific strengths:**
- The identification of back-calculated 2016-2018 data with +/- 2-3% error is important and correctly flagged.
- The COVID confounding warning is appropriately prominent.
- The underground tutoring data quality assessment (score 33, LOW) is honest and correct.
- The failed datasets are clearly documented with impact assessments.

**Gap:** The DATA_QUALITY.md does not discuss **CPI adjustment**. All spending figures are nominal. Over the 2016-2025 period, cumulative CPI inflation in China was approximately 15-20%. Without deflation, real spending changes are conflated with price level changes. This is mentioned only as Open Issue #4 rather than as a binding constraint. Given that the education CPI sub-index has risen faster than headline CPI in some years, this matters for interpretation. This should be elevated to a binding downstream constraint.

## Verification Assessment

Not applicable at Phase 0. The cross-dataset consistency checks performed in DATA_QUALITY.md (e.g., NBS education share matching across Datasets 1 and 8, World Bank GDP cross-validating with NBS) are appropriate for this stage.

## EP and Causal Claim Assessment

The EP estimates are generally reasonable. The calculation methodology (EP = truth x relevance) is applied consistently.

**Specific concerns:**

1. The EP for "Policy -> Formal Industry Collapse" (EP=0.63) is appropriate. Truth=0.90 and Relevance=0.70 are well-justified by the strong empirical evidence.

2. The EP for "Industry Collapse -> Reduced Tutoring Spending" (EP=0.24, truth=0.60, relevance=0.40) may be too HIGH for truth. The relevance is correctly set at 0.40 (tutoring is only 12% of total). But truth=0.60 implies moderate confidence that industry collapse translated to reduced per-household tutoring spending. Given the documented underground market emergence, a truth value of 0.40-0.50 would be more defensible.

3. The chain from Policy -> Industry Collapse -> Reduced Tutoring Spending -> Reduced Total Expenditure has Joint_EP = 0.63 * (0.24/0.63) * (0.16/0.24) = 0.63 * 0.38 * 0.67 = approximately 0.16. This is just above the soft truncation threshold of 0.15, which is appropriate -- DAG 1's core chain should receive full analysis but the evidence bar is correctly set as high.

4. DAG 2's "Competitive Pressure -> Inelastic Demand" edge (EP=0.49) is well-justified. This is the strongest theoretically grounded edge in the analysis.

## Result Plausibility

The NBS data shows education/culture/recreation spending at 2,599 yuan in 2021, dropping to 2,469 yuan in 2022 (-5.0%), then rebounding to 2,904 in 2023 (+17.6%). The 2022 dip is notable but could reflect either policy effects OR continued COVID restrictions (China maintained Zero-COVID through much of 2022, with lockdowns in Shanghai and other major cities). By 2023-2025, spending is above pre-policy levels in nominal terms. This trajectory is more consistent with DAGs 2/3 (no lasting reduction) than DAG 1 (genuine reduction), but the proxy variable problem makes this inference weak.

The income quintile data shows household spending per student ranging from 3,000 yuan (lowest 20%) to 25,000 yuan (highest 20%), an 8.3x ratio. This is plausible for China and consistent with the VoxChina finding that lowest-quartile families spend 56.8% of income on education.

**Note on the "56.8% of income" claim:** This figure from VoxChina appears to refer to education as a share of total household *expenditure* for the lowest income quartile, not as a share of *income*. DISCOVERY.md and DATA_QUALITY.md both use it as "percent of income" which may be a misquotation. If these families spend 56.8% of their total consumption expenditure on education, that is extraordinary but mathematically possible. If it is 56.8% of disposable income, it implies education spending exceeds all other spending combined, which would need stronger sourcing. This needs verification.

## Issues by Category

### Category A (Blocking)

1. **[A1]: CIEFR-HS internal inconsistency not addressed.** The 2017-to-2019 data shows in-school expenditure dropping sharply while out-of-school expenditure rose, which contradicts the static 73/12/15 composition narrative that underpins DAG 3. This inconsistency is not discussed or reconciled in either DISCOVERY.md or DATA_QUALITY.md.
   - Domain impact: DAG 3's core premise (in-school costs dominate and are untargeted) depends on the 73/12/15 split being a stable structural feature. If the composition was already shifting pre-policy, the DAG 3 narrative requires revision.
   - Required action: Explain whether the 73/12/15 split is from a different aggregation level than the 2017-vs-2019 table (e.g., all education levels vs. compulsory only), or whether the composition genuinely shifted between waves. Document which figure applies to which population.

2. **[A2]: The "56.8% of income" claim needs verification.** This figure is used in both DISCOVERY.md (DAG 2 edge justification) and DATA_QUALITY.md, but the original VoxChina source may report this as share of expenditure, not share of income. If misquoted, it overstates the income burden.
   - Domain impact: The income-stratified analysis depends on correctly characterizing the education burden by income level. A misquoted figure could bias the analysis toward overstating inequality effects.
   - Required action: Verify the exact metric (share of income vs. share of expenditure) from the VoxChina/Wei 2024 source. Correct all instances if needed.

3. **[A3]: No CPI deflation as a binding downstream constraint.** Nominal spending comparisons over a 10-year period conflate real changes with inflation. The education CPI sub-index has behaved differently from headline CPI in some years.
   - Domain impact: A nominal increase in education spending of, say, 10% over 4 years could represent zero real change or even a real decline if education-specific inflation was 10-15%. Without deflation, the analysis cannot distinguish real spending changes from price effects.
   - Required action: Elevate CPI adjustment from "Open Issue" to a binding downstream constraint. Acquire NBS CPI data (at minimum headline, ideally education sub-index) and add to registry.yaml.

### Category B (Important)

1. **[B1]: China Household Finance Survey (CHFS) not searched.** This is a major nationally representative survey with education expenditure items, administered by Southwestern University of Finance and Economics. It may have more recent waves than CFPS.
   - Domain impact: Could provide post-policy household-level microdata that would substantially strengthen the analysis.
   - Suggested action: Search for CHFS public-use data availability. Document the attempt even if access is restricted.

2. **[B2]: Provincial statistical yearbook data not searched.** Several provinces publish education spending at finer granularity than the national NBS series.
   - Domain impact: Provincial data would enable geographic heterogeneity analysis and support the enforcement intensity identification strategy.
   - Suggested action: Search for Beijing, Shanghai, and Guangdong statistical yearbook education spending breakdowns for 2019-2024.

3. **[B3]: Missing "income effect / liquidity constraint" first principle.** DAG 1 lacks a theoretically grounded mechanism for WHY lower-income households would not substitute. The demand inelasticity principle (Principle 1) applies to households with substitution capacity; liquidity-constrained households behave differently.
   - Domain impact: Without this principle, the DAG 1 success narrative is under-theorized. The analysis risks treating all households as identical agents.
   - Suggested action: Add a fifth principle on income/liquidity constraints and incorporate it into DAG 1 as a mechanism explaining genuine savings for lower-income households.

4. **[B4]: Market size estimate of "$300 billion" needs checking.** DISCOVERY.md states "estimated USD 300 billion industry pre-policy" while the Tutoring Industry dataset lists "$100B" (Mordor Intelligence, 2020). The DATA_QUALITY.md notes the range is "$70-300B." The DISCOVERY.md figure cherry-picks the high end, which overstates the industry to make the collapse seem more dramatic.
   - Domain impact: If the industry was closer to $70-100B, the per-household savings potential is correspondingly smaller.
   - Suggested action: Use the range ($70-300B) or the Mordor Intelligence figure ($100B) in DISCOVERY.md rather than the high-end outlier.

5. **[B5]: PISA 2022 data not considered.** China participated in PISA 2022 in select regions. The household questionnaire includes education spending items that would provide a post-policy data point with international comparability.
   - Domain impact: Would provide an independent check on household education spending from a non-Chinese instrument.
   - Suggested action: Search for PISA 2022 household spending data for China. Note that China's participation was limited to specific regions (likely B-S-J-Z or similar subset).

### Category C (Minor)

1. **[C1]: Engel curve methodology not mentioned.** The standard household expenditure analysis tool (Engel curves) is absent from the methodological discussion. For Phase 1 strategy, this should be noted as a candidate approach.
   - Suggested action: Mention Engel curve analysis as a candidate methodology in the open issues or data requirements section.

2. **[C2]: The "160 million compulsory-education students" figure is approximately correct but should be dated.** The processed demographics data shows enrollment peaked around 160.65M in 2022 and is declining. The figure should specify the year.
   - Suggested action: Add "(as of 2022)" after the 160 million figure.

3. **[C3]: Policy evolution beyond October 2024.** The timeline ends at October 2024 (policy easing). Given the analysis date of March 2026, there may be 17 months of additional policy developments not captured. This is noted in Open Issues but could be flagged more prominently as a potential source of period misspecification.
   - Suggested action: Add a note that the enforcement timeline may be incomplete for 2025-2026 and that downstream phases should verify current policy status.

## Acceptance Readiness

I would **not** accept this analysis in its current form. The three Category A issues must be resolved:

- **A1** (CIEFR-HS inconsistency) is the most substantive. The 73/12/15 composition split is foundational to DAG 3 and is cited repeatedly. If the underlying data shows a different pattern at the compulsory education level vs. the all-education level, this distinction must be clearly documented and the DAG 3 narrative adjusted accordingly.

- **A2** (56.8% income claim) is a factual verification that should be quick to resolve but is important because it affects the inequality argument in DAG 2.

- **A3** (CPI deflation) is a methodological requirement that will become critical in Phase 3 but must be established as a binding constraint now so downstream agents do not produce nominal-only analysis.

The Category B issues would strengthen the analysis considerably, particularly B1 (CHFS search) and B3 (liquidity constraint principle), but are not strictly blocking.

Overall, this is a well-structured and honest Phase 0 artifact. The question decomposition is thorough, the competing DAGs are genuinely distinct, the data quality assessment is unusually candid about limitations, and the downstream warnings are well-calibrated. With the Category A fixes resolved, this would be ready for Phase 1.
