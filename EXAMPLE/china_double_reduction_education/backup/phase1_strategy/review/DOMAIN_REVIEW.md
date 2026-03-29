# Domain Review

## Summary
- **Artifact reviewed**: `phase1_strategy/exec/STRATEGY.md`
- **Upstream artifacts**: `phase0_discovery/exec/DISCOVERY.md`, `phase0_discovery/exec/DATA_QUALITY.md`
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 3
- **Category B issues**: 4
- **Category C issues**: 3

---

## First Principles Assessment

The four first principles identified in Phase 0 (demand inelasticity under status competition, regulatory displacement / balloon effect, compositional fallacy in policy evaluation, implementation fidelity gradient) are well-chosen and defensible. They cover the major domain-relevant mechanisms. The causal DAGs are genuinely competing rather than trivial variants of each other, which is good practice.

The three DAGs are structurally sound. DAG 1 (policy success via supply destruction) represents the official narrative. DAG 2 (regulatory displacement) represents the standard economics critique. DAG 3 (compositional irrelevance + crowding-in) represents the measurement-focused critique. The shared edge (Policy -> Industry Collapse) across all three DAGs is appropriate because the industry collapse is the least contested empirical fact.

One domain concern: DAG 3's crowding-in edge (public spending raises household spending) draws on a single ScienceDirect 2025 paper using CHIP county-level matching. The strategy correctly notes this but still classifies it as LITERATURE_SUPPORTED with truth = 0.55. Given this is a single study with a specific identification strategy that may not generalize temporally (pre-policy CHIP data applied to a post-policy context), THEORIZED at truth = 0.40 would be more appropriate.

---

## Data Source Validity Assessment

The data source assessment in DATA_QUALITY.md is honest and well-calibrated. The strategy correctly inherits all nine binding warnings. The proxy variable problem (NBS "education, culture and recreation" bundling non-education spending) is correctly identified as the dominant data limitation. The CIEFR-HS pre-policy composition data (73/12/15 split) is appropriately caveated as a national average that varies by income and geography.

One concern: The strategy relies on the NBS 8-category consumption data (ds_008) for compositional analysis, but this dataset only covers 2019-2025 (7 years). For the pre-policy period, only 3 years (2019-2021) are available, and 2020 is a COVID outlier. This leaves effectively 2 clean pre-policy observations for compositional trend analysis. The strategy does not flag this as a power constraint for the compositional analysis arm.

---

## Methodology Assessment

### ITS Approach for This Policy Question

The choice of Interrupted Time Series as the primary method is the correct call given the constraints. The policy was implemented nationally and simultaneously, ruling out standard DiD with a geographic control group. No valid instrument exists for IV estimation. No sharp cutoff with a running variable exists for RDD (the grade 9/10 boundary is not exploitable without microdata). ITS with a known intervention date is the textbook approach for this setting.

However, the strategy must be more candid about ITS power with n=10 annual observations. The strategy states ITS "can detect a level shift of approximately 5-8%," but this requires approximately normal, homoskedastic residuals with no autocorrelation -- conditions that are unlikely with a COVID-disrupted, trending annual series of 10 points. With effectively 5 pre-policy and 5 post-policy observations (and the pre-policy period including 2 back-calculated years and a COVID year), the degrees of freedom for a segmented regression with level shift, trend change, and a COVID indicator are dangerously low. A model with intercept, slope, level shift at 2021, slope change at 2021, and a COVID dummy uses 5 parameters on 10 observations. This leaves 5 residual degrees of freedom, which is marginal for any meaningful inference.

The BSTS secondary method is appropriate in principle. However, the strategy does not specify which covariates will feed the structural time series model. With only 10 observations, the number of covariates that can be included is severely limited (rule of thumb: no more than n/10 to n/5 predictors, so 1-2 covariates). The strategy lists income, demographics, and CPI as potential covariates but does not prioritize. This needs to be resolved before Phase 3.

### Urban-Rural Quasi-DiD

This is the most domain-problematic element of the strategy. The strategy proposes using rural households as a quasi-control group for urban households under the assumption that the Double Reduction policy disproportionately affected urban areas (where tutoring participation was 47% vs. 18% rural, per CIEFR-HS).

Domain concerns with this design:

1. **The parallel trends assumption is almost certainly violated.** The strategy acknowledges an "urban-rural convergence trend" but treats it as a testable nuisance. In reality, urban-rural convergence in spending and income is one of the dominant secular trends in Chinese economic development over the past decade. The NBS data itself shows the urban-rural income ratio declining from 2.72 (2016) to 2.30 (2025). Education spending follows a similar convergence pattern driven by rural school infrastructure investment, hukou reform, and rural income growth. This convergence is structural, not incidental, and it operates on the same spending series the analysis uses as the outcome. A formal parallel trends test with 5 annual observations will have no power to detect convergence-driven violation.

2. **Rural areas are not untreated.** The Double Reduction policy applied nationally, including to rural areas. Rural tutoring participation was 18%, not zero. Rural areas also experienced the policy's effects on school-based after-school services, homework reduction mandates, and the cultural shift around education. Using rural as a "control" requires assuming the policy effect was zero in rural areas, which is not justified.

3. **The COVID shock was differential across urban and rural areas.** Urban lockdowns were more severe and prolonged (especially under zero-COVID through early 2022), creating differential COVID confounding that coincides with differential policy exposure. The quasi-DiD cannot separate differential COVID recovery from differential policy effect.

4. **n=2 units.** With only urban and rural as units (not a panel of provinces or cities), the quasi-DiD is not a true difference-in-differences. It is a comparison of two time series. Standard DiD inference requires multiple units to estimate treatment effects with valid standard errors. With 2 units, any formal DiD regression produces estimates but the inference is unreliable.

The strategy should reframe this analysis as a descriptive comparison of urban vs. rural trajectories, not as a quasi-DiD with causal identification claims.

### Reference Analyses

The three reference analyses are well-chosen:
- Huang et al. (2025) for labor market / industry-side evidence
- Chen et al. (2025) for direct household spending measurement
- Liu et al. (2022) for family behavioral responses

The strategy correctly identifies that Chen et al. (2025) "directly answers our question" with household microdata. This is an important admission. The cross-reference implications section honestly states that "our analysis cannot replicate this because we lack household microdata post-policy."

However, the strategy underplays a critical implication: if Chen et al. (2025) already answers the question using superior data (panel analysis of nationally representative household survey 2017-2023), the value-added of this macro-level analysis needs to be articulated more precisely. The strategy claims value through "(a) CPI-adjusted real spending trends through 2025, (b) compositional analysis across all 8 NBS consumption categories, (c) formal causal DAG framework with EP propagation, (d) explicit COVID confounding treatment." Of these, (a) is the most defensible contribution -- extending the time series to 2025. Items (c) and (d) are methodological framing that do not add empirical content. Item (b) is interesting but the NBS categories bundle education with culture/recreation, so the "compositional analysis" operates on proxy categories, not education sub-components.

---

## Systematic Uncertainty Assessment

The systematic uncertainty inventory is thorough. All nine DATA_QUALITY warnings map to identified uncertainty sources, with no silent omissions. The proxy variable bias is correctly flagged as HIGH impact and irreducible. The COVID confounding is correctly flagged as HIGH.

One gap: the strategy does not quantify the interaction between proxy variable bias and COVID confounding. Post-COVID recovery in culture and recreation spending (tourism, entertainment) likely accelerated faster than education spending recovery, meaning the NBS proxy's composition shifted post-COVID. This is not a simple additive bias -- it is a time-varying confound within the proxy variable. The strategy acknowledges culture/recreation recovery inflating the proxy (Baseline 4) but does not plan a specific quantitative bound on this effect.

---

## Verification Assessment

The refutation battery is reasonable: placebo treatment (2019), random common cause, data subset (excluding back-calculated years), and a COVID-date placebo (2020). The COVID-date placebo is particularly well-designed -- if moving the intervention to 2020 produces a similar or larger effect, the "policy signal" is actually COVID recovery.

The strategy correctly notes that refutation tests at n=10 have limited power and should be used "qualitatively rather than as strict pass/fail." This is an honest and domain-appropriate caveat.

---

## EP and Causal Claim Assessment

The EP update mechanics are traceable and justified. The data quality penalties (truth -0.1 for MEDIUM, cap at 0.3 for LOW) and proxy penalty (-0.05 for all edges terminating in Total Expenditure) are reasonable.

The chain EP analysis produces an important and honest result: **all multi-step chains fall below the hard truncation threshold (0.05)**. The strategy's response to this is the most important domain judgment call in the document. It applies a "pragmatic classification" that shifts from chain-level EP to individual-edge testability. This is defensible, but the strategy should be explicit that this represents a deviation from the standard EP truncation protocol and that the analysis is accordingly weaker in its causal claims.

The positioning as "macro-level corroboration" (Section "Cross-Reference Implications," point 2) is directionally honest but insufficiently precise. The strategy says "our macro-level analysis can corroborate the direction but not the decomposition." A more honest framing: this analysis can test whether NBS aggregate proxy data is *consistent* with the findings of Chen et al. (2025) and others, but it cannot independently establish any causal claim because (a) the outcome variable is a proxy, (b) the sample size is 10, (c) all chain EPs are below truncation, and (d) better-identified studies already exist. "Consistency check" or "macro-level coherence test" would be more accurate than "corroboration," which implies independent confirmatory evidence.

---

## Result Plausibility

Not yet applicable (Phase 1 is strategy, not results). However, the prior probability estimates are plausible:
- P(total education spending declined) = 0.45: reasonable given Chen et al.'s mixed findings
- P(formal tutoring spending declined) = 0.90: well-supported
- P(underground substitution non-trivial) = 0.70: consistent with enforcement data

The expected effect sizes (5-15% under DAG 1, ~0% under DAG 2/3) are in the right range given the 12% tutoring share ceiling.

---

## Issues by Category

### Category A (Blocking)

1. **[A1]: Urban-rural quasi-DiD is overclaimed as a causal identification strategy**
   - Domain impact: The parallel trends assumption is almost certainly violated due to the dominant urban-rural convergence trend in Chinese economic development. Rural areas are not untreated -- the policy applied nationally. With n=2 units, inference is unreliable. Presenting this as a "quasi-difference-in-differences design" (Strategy summary, line 13; Section 5 method table) risks producing misleading causal claims.
   - Required action: Reframe the urban-rural comparison as a descriptive analysis of differential trajectories. Remove "quasi-DiD" language. State explicitly that the comparison cannot support causal inference due to (a) violated parallel trends from convergence, (b) non-zero rural treatment, (c) differential COVID confounding, and (d) n=2 units. The comparison remains useful as an exploratory decomposition but should not carry causal weight. Update the method table (Section 5) accordingly.

2. **[A2]: ITS degrees of freedom are dangerously low and unacknowledged**
   - Domain impact: A segmented regression with level shift, slope change, and COVID indicator on 10 annual observations leaves approximately 5 residual degrees of freedom. This is insufficient for reliable inference. The strategy's claimed sensitivity ("can detect approximately 5-8% level shift") is over-optimistic for this sample size. If the Phase 3 analyst takes this sensitivity claim at face value, they may over-interpret marginal results.
   - Required action: Add an explicit power/feasibility assessment acknowledging that with 10 observations, 3 back-calculated, and 1 COVID-disrupted, the effective clean pre-policy sample is 2 years (2019, 2020-partial). State that any ITS results must be accompanied by a frank assessment of degrees of freedom. Consider whether the ITS model should be simplified (e.g., level shift only, no slope change, COVID modeled separately) to conserve degrees of freedom. Explicitly state the minimum detectable effect size under realistic conditions.

3. **[A3]: "Macro-level corroboration" framing is insufficiently hedged**
   - Domain impact: The strategy positions this analysis as "corroborating" Chen et al. (2025). Corroboration implies independent confirmation, but this analysis uses a proxy variable with unknown composition, has 10 observations, and all chain EPs are below truncation. If the Phase 6 report uses "corroboration" language, it overstates the analysis's evidential contribution.
   - Required action: Replace "corroboration" with "consistency check" or "macro-level coherence test" throughout. Add a sentence in the Summary and in Section "Cross-Reference Implications" stating: "This analysis cannot independently confirm or disconfirm the household-level findings of Chen et al. (2025). It can only assess whether aggregate NBS proxy trends are consistent with those findings." This distinction must propagate to Phase 6.

### Category B (Important)

1. **[B1]: BSTS covariate strategy is unspecified**
   - Domain impact: With 10 observations, BSTS can accommodate 1-2 covariates. The strategy lists income, demographics, and CPI without prioritizing. An overparameterized BSTS will produce unreliable posterior intervals.
   - Suggested action: Specify that income (real disposable income) is the sole covariate for the primary BSTS model, with a robustness check adding demographic normalization. State explicitly that no more than 2 covariates will be used.

2. **[B2]: Compositional analysis has only 2 clean pre-policy observations**
   - Domain impact: The 8-category NBS data (ds_008) covers 2019-2025. After excluding the COVID-disrupted 2020, only 2019 and 2021-H1 (pre-July) provide pre-policy baselines. A structural break test on a 7-observation series with 2 pre-intervention points has negligible power.
   - Suggested action: Acknowledge this constraint explicitly in the Chain Planning section. Reframe the compositional analysis as descriptive trend visualization rather than a formal structural break test. Note that the compositional arm has the weakest statistical foundation among the three "full analysis" arms.

3. **[B3]: Crowding-in edge is over-classified as LITERATURE_SUPPORTED**
   - Domain impact: The crowding-in hypothesis rests on a single ScienceDirect 2025 paper using CHIP county-level matching. This is one study, not established literature. Over-classifying it inflates EP for DAG 3's mechanism. The crowding-in finding is also specifically about the relationship between public and private spending in Chinese compulsory education, and the identification strategy (county-level matching on CHIP data) may not generalize to the macro NBS series used here.
   - Suggested action: Reclassify Public Spending -> Crowding-In from LITERATURE_SUPPORTED (truth 0.55) to THEORIZED (truth 0.40). Adjust EP from 0.22 to 0.16. Note in the edge table that this is based on a single study with a specific identification strategy.

4. **[B4]: Pre-existing downward trend (CIEFR-HS) is inconsistent with NBS proxy trajectory**
   - Domain impact: CIEFR-HS shows per-student education expenditure declining from 10,372 yuan (2017) to 6,090 yuan (2019) -- a 41% decline in 2 years. Meanwhile, the NBS proxy shows the education/culture/recreation category rising steadily (1,825 to 2,513 yuan, 2016-2019). These series move in opposite directions during the same period. The strategy lists the pre-existing downward trend as Baseline 5 but does not address this inconsistency. If the micro data (CIEFR-HS) and macro data (NBS) diverge on the direction of pre-policy trends, the NBS proxy's reliability for detecting post-policy changes is further undermined.
   - Suggested action: Add a paragraph in Section 1 (Signal Definition) or Section 2 (Baseline Enumeration) explicitly noting this divergence and discussing its implications. Possible explanations include: (a) the NBS proxy's culture/recreation components grew enough to offset education declines, (b) the CIEFR-HS per-student decline reflects compositional changes in the survey, or (c) the two series measure genuinely different constructs. This divergence should be flagged as an additional systematic uncertainty.

### Category C (Minor)

1. **[C1]: Chen et al. (2025) SSRN status should be noted**
   - Suggested action: Note that Chen et al. (2025) is a working paper (SSRN #5596490), not a peer-reviewed publication. Its findings are suggestive but have not undergone formal peer review. This does not change the strategy but should temper the weight placed on its specific estimates.

2. **[C2]: Missing sensitivity to education-specific vs. overall CPI deflator**
   - Suggested action: The strategy lists CPI deflator choice as a LOW-impact systematic but the cumulative difference is 1.5 percentage points (15.3% vs. 16.8%) over the analysis window. For a 5-12% expected policy effect, a 1.5pp deflator difference is not negligible. Consider upgrading this to MODERATE impact or at minimum reporting all results under both deflators.

3. **[C3]: The strategy could benefit from stating what a null finding means**
   - Suggested action: Expand the contingency plan for "ITS finds no structural break" beyond "report as positive finding for DAG 2/3." A null finding from ITS on a proxy variable with 10 observations and multiple confounders could mean (a) no policy effect, (b) policy effect masked by proxy inflation, (c) policy effect too small to detect at this power, or (d) confounders absorb the signal. Laying out these interpretations now will improve Phase 6 reporting.

---

## Acceptance Readiness

I would not accept this strategy in its current form. The three Category A issues must be addressed:

1. The urban-rural quasi-DiD must be reframed as descriptive, not causal. This is the most important change because it affects how Phase 3 implements and interprets the urban-rural comparison.

2. The ITS degrees-of-freedom problem must be acknowledged with explicit model simplification guidance and realistic sensitivity estimates.

3. The "corroboration" framing must be downgraded to "consistency check." This affects how every downstream phase describes the analysis's contribution.

The four Category B issues would strengthen the analysis but are not blocking. The core analytical approach (ITS + BSTS on NBS proxy data with explicit uncertainty) is sound for this domain and data situation. The reference analysis selection is appropriate. The honest acknowledgment that all chain EPs fall below truncation, and the pragmatic decision to proceed anyway on individual-edge grounds, reflects good domain judgment -- but only if the framing is appropriately modest, which currently it is not.
