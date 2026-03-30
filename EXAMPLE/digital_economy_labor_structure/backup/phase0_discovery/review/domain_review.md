# Domain Review

## Summary
- **Artifact reviewed**: `phase0_discovery/exec/DISCOVERY.md`, `phase0_discovery/exec/DATA_QUALITY.md`, `data/registry.yaml`, `experiment_log.md`
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 3
- **Category B issues**: 4
- **Category C issues**: 3

## First Principles Assessment

The four identified first principles are well-chosen and represent the canonical theoretical pillars for studying digital economy effects on labor markets:

1. **Technological displacement and compensation (Ricardo-Marx-Schumpeter)**: Correctly identified as the foundational tension. The framing appropriately distinguishes displacement from compensation channels and notes that net effects depend on adoption rate and institutional context. This is the standard starting point in the technology-employment literature.

2. **Skill-biased technological change / task-based framework (Acemoglu and Autor 2011)**: Appropriate and well-cited. The caveat that SBTC was developed for advanced economies and may not apply cleanly to China's dual labor market is an important and often-overlooked nuance. However, the analysis should also reference the Routine-Biased Technological Change (RBTC) refinement, which is more directly applicable to digital economy contexts than the original SBTC formulation.

3. **Structural change and multi-sector reallocation (Lewis-Kuznets-Herrendorf)**: Sound choice. China's ongoing Lewis turning point transition and rapid tertiarization make this highly relevant. The note about the hukou system as a potential non-applicability condition is well-taken.

4. **Institutional mediation and labor market segmentation (Doeringer-Piore)**: Essential for the Chinese context. The identification of platform work as a potential "third segment" is a genuinely useful insight that goes beyond standard applications of dual labor market theory.

**Causal DAGs**: The three DAGs represent meaningfully different causal structures, not trivial variations. DAG 1 (technology-push) vs. DAG 2 (institutional mediation) is the classic direct-vs-mediated debate. DAG 3 (segmentation) introduces heterogeneous treatment effects, which is the most novel and China-specific contribution. The DAG comparison table clearly articulates divergence points and data requirements for distinguishing between them. The kill conditions are well-specified and genuinely falsifiable.

**Gap in the DAG framework**: All three DAGs treat the digital economy as a unidimensional treatment. In practice, digital economy effects decompose into at least three distinct channels -- (a) e-commerce and platform economy, (b) industrial digitalization and automation, (c) digital financial inclusion -- each with different labor market implications. The composite index approach conflates these channels. This is partially acknowledged in the "hidden assumptions" section (assumption 1) but not carried through to the DAG structure. At minimum, DAG 1 should distinguish between platform-mediated creation and industrial-automation substitution as separate treatment pathways rather than treating both as downstream of a single "digital economy development level" node.

**Missing confounder**: None of the three DAGs include China's demographic transition (aging population, shrinking working-age cohort) as an explicit confounder. Population aging independently drives labor structure change (reducing labor supply, increasing healthcare/service employment, raising capital-labor substitution incentives) and correlates with the digital economy expansion period. The `population_65plus_pct` and `population_15_64_pct` variables are in the World Bank dataset but are not explicitly positioned in any DAG. This is a notable omission for a country whose working-age population peaked around 2012 -- precisely when the smart city pilots began.

## Data Source Validity Assessment

**World Bank / ILO data**: These are authoritative sources for national aggregate indicators. The analysis correctly identifies that ILO employment figures are modeled estimates rather than direct survey data. The known limitation of China's official unemployment rate (understating true unemployment by excluding rural migrants) is properly flagged. The use of ILO modeled estimates is standard practice in cross-country labor economics research but becomes more problematic for within-country time series analysis where model smoothing may obscure the short-run fluctuations that DID and structural break methods aim to detect.

**Smart city pilot list**: The compilation from MOHURD announcements and published DID studies is the standard approach in this literature. The 286-city count and batch distribution (84/98/104) are consistent with what I have seen in published studies (e.g., Zheng and Huang 2023 in Empirical Economics report similar counts). The exclusion of district/county/town-level units for cleaner DID is methodologically sound.

**Digital economy composite index**: This is the weakest link in the data portfolio, and the DATA_QUALITY.md assessment is honest about it. The proxy captures ICT infrastructure penetration (internet, broadband, mobile) and R&D intensity, but misses the core dimensions that define China's digital economy: e-commerce transaction volumes (Taobao/JD/Pinduoduo), mobile payment penetration (Alipay/WeChat Pay), and the Peking University Digital Financial Inclusion Index (PKU-DFIIC). The PKU-DFIIC is freely available for academic use after registration and covers 31 provinces and 2,800+ counties from 2011 onward. Its omission is understandable given automated acquisition constraints, but it substantially weakens the construct validity of the treatment variable. Equal weighting of index components is arbitrary and inconsistent with the PKU-DFIIC's principal component approach and with the entropy-weight methods common in Chinese digital economy literature.

**EPS and CFPS failures**: Both failures are documented with clear reasons and access instructions. The analysis correctly identifies these as the binding constraints that force downscoping from the planned DID design to national time series. The characterization of both as "failed" rather than "deferred" is appropriate -- the analysis must work with what it has.

**Missing data source that should have been attempted**: China's National Bureau of Statistics (stats.gov.cn) publishes provincial-level Statistical Yearbook data online. While not as comprehensive as EPS, key variables (provincial GDP, employment by sector, internet users by province) are publicly accessible in the China Statistical Yearbook online tables. The experiment log does not document any attempt to scrape or manually extract NBS yearbook data. This is a missed opportunity that could partially fill the provincial panel gap without requiring EPS access. Similarly, the China Internet Network Information Center (CNNIC) publishes semi-annual reports with provincial internet penetration data that could supplement the digital economy index.

## Methodology Assessment

**DID design**: The choice of smart city pilots as the quasi-natural experiment is well-established in the literature and appropriate for the research question. The staggered rollout across three batches (2012/2013, 2013/2014, 2015) enables staggered DID estimation, which is the current best practice. The analysis correctly flags potential SUTVA violations from spatial spillovers and suggests spatial DID or buffer-zone exclusion as remedies.

However, the analysis does not discuss the recent methodological literature on problems with staggered DID (Goodman-Bacon 2021, Callaway and Sant'Anna 2021, Sun and Abraham 2021). In two-way fixed effects DID with staggered treatment, already-treated units serve as controls for later-treated units, which can produce biased estimates when treatment effects are heterogeneous over time. Given that the smart city pilots span three batches over three years, this is directly relevant. The strategy document should mandate the use of heterogeneity-robust DID estimators (e.g., Callaway-Sant'Anna or Sun-Abraham) rather than naive TWFE.

**National time series fallback**: The downscoping from city-level DID to national time series is an honest acknowledgment of data limitations. However, the proposed Granger causality and structural break methods have well-known limitations for causal inference with 24 observations: (a) Granger causality tests have low power with short time series, (b) VAR models consume degrees of freedom rapidly (a VAR(2) with 3 variables uses 18 parameters for 24 observations), and (c) structural break tests (e.g., Bai-Perron) require longer series for reliable break detection. The DATA_QUALITY.md correctly notes the parsimony constraint but does not quantify the implied power limitations.

**Mediation analysis**: The planned Sobel/bootstrap mediation test for DAG 2 is appropriate in principle. However, mediation analysis with time series data raises additional issues not discussed: temporal ordering of mediators, potential feedback loops between mediators and outcomes, and the distinction between contemporaneous and lagged mediation. Baron-Kenny mediation assumes cross-sectional data; time series mediation requires VAR-based decomposition or structural equation modeling with lagged effects.

## Systematic Uncertainty Assessment

The DATA_QUALITY.md provides a structured uncertainty assessment through the per-dataset quality scoring system (completeness, consistency, bias, granularity). This is a reasonable framework. Specific concerns:

**Construct validity uncertainty**: The digital economy composite index has a bias score of 45/100 (LOW), which is appropriate. However, the downstream implications are not fully propagated. If the treatment variable has uncertain construct validity, then ALL causal effect estimates using this variable inherit that uncertainty. The EP cap of 0.30 for edges requiring city-level data is a partial response, but there should also be a construct-validity discount applied to the DE node in all three DAGs at the national level. Currently, the DE --> SUB edge has EP = 0.49 (LITERATURE_SUPPORTED), but this assumes a valid digital economy measure. With the proxy index, the truth component should be downgraded.

**ILO modeling uncertainty**: The modeled nature of ILO employment estimates introduces model specification uncertainty that is distinct from sampling uncertainty. ILO models extrapolate from periodic labor force surveys using economic covariates, meaning that ILO employment structure estimates are partially predicted FROM GDP and urbanization -- the same variables used as controls in the planned regressions. This creates a mechanical correlation / endogeneity concern that is not discussed.

**Temporal coverage uncertainty**: The 2000-2023 window includes significant structural breaks in China's economy (WTO accession 2001, global financial crisis 2008-2009, supply-side reform 2016, COVID-19 2020, tech crackdown 2021-2022). With only 24 observations, it is difficult to control for these breaks while estimating the digital economy effect. The analysis should discuss whether sub-period analysis or break-adjusted estimation is needed.

## Verification Assessment

Phase 0 does not produce verification results per se, but the data quality assessment serves as a verification gate. The assessment is thorough and honest. The "PROCEED WITH WARNINGS" verdict is appropriate given the data limitations. The three critical warnings (no DID, no individual-level mechanisms, no skill-level data) are clearly stated and their downstream implications are well-articulated.

The cross-dataset DAG coverage table is a useful verification tool that maps each DAG edge to available data. The "Can Test?" column provides a clear yes/no/partial assessment. This is well-done.

One verification gap: the analysis does not report any basic data validation checks (e.g., do sectoral employment shares sum to approximately 100%? Do sectoral value-added shares sum to approximately 100%? Are trends in the World Bank data consistent with known facts about China's economy?). The DATA_QUALITY.md mentions some statistics but does not perform cross-variable consistency checks systematically.

## EP and Causal Claim Assessment

The EP assessment methodology is sound: EP = truth x relevance, with truth calibrated by evidence type (LITERATURE_SUPPORTED = 0.7, THEORIZED = 0.4, SPECULATIVE = 0.2) and relevance calibrated by theoretical importance (0.2-0.7). The resulting EP values are in plausible ranges.

**Specific EP concerns**:

1. The SCP --> DE edge (smart city pilot to digital economy) has EP = 0.42 across all three DAGs, reflecting its role as the DID instrument. However, given that city-level DID is not executable with current data, this edge's effective EP should be noted as contingent on data availability. The treatment indicator exists but has no corresponding outcome measure.

2. The DE --> SUB edge (EP = 0.49) and DE --> CRE edge (EP = 0.42) are labeled LITERATURE_SUPPORTED, which is appropriate given the cited studies. However, the cited references (Wang and Dong 2023; Li et al. 2024 in Sustainability; Finance Research Letters 2024) should be verified for relevance -- some Chinese labor economics publications in these venues may have quality concerns, and the specific findings should be confirmed against the analysis claims.

3. DAG 3 has lower EP values overall (many THEORIZED edges in the 0.16-0.28 range), which correctly reflects the more speculative nature of the segmentation hypothesis. This appropriate EP calibration suggests the analysis is not over-claiming for the most novel hypothesis.

## Result Plausibility

Phase 0 does not produce analytical results, but the descriptive statistics reported in the data quality assessment are plausible and consistent with established facts about China's economy:

- Employment agriculture declining from 50% to 23% (2000-2023): Consistent with China's rapid structural transformation.
- Employment services rising from 25% to 46%: Consistent with tertiarization trends.
- Internet users rising from 1.8% to 90.6%: Consistent with China's digital leapfrogging.
- Self-employed declining from 52% to 38%: Consistent with formalization trends, though this may also reflect measurement changes.
- Youth unemployment rising to 15.6%: Consistent with the well-documented youth unemployment crisis, though the actual figure may be higher (the NBS suspended publication of the 16-24 age group unemployment rate in mid-2023 after it exceeded 20%).

## Issues by Category

### Category A (Blocking)

1. **[A1]: Demographic transition omitted as confounder in all DAGs**
   - Domain impact: China's working-age population peaked around 2012 and has been declining since -- precisely coinciding with the smart city pilot period. Population aging independently drives labor structure change (increasing service sector employment, raising automation incentives, reducing labor supply). Omitting this confounder risks attributing demographic-driven structural change to the digital economy. The variables exist in the dataset (population_65plus_pct, population_15_64_pct) but are not positioned in any DAG.
   - Required action: Add demographic transition as an explicit confounder node in all three DAGs. Adjust EP estimates for edges where demographic change is a competing explanation. Include population aging variables as mandatory controls in the Phase 1 strategy.

2. **[A2]: NBS Statistical Yearbook data not attempted despite being publicly available**
   - Domain impact: The analysis declares provincial panel analysis impossible due to EPS access failure, but China's National Bureau of Statistics publishes key provincial variables online (provincial GDP, employment by three sectors, internet users, education expenditure). This data could partially fill the provincial panel gap and enable at least a simplified provincial panel regression, substantially strengthening identification beyond national time series. The five-strategy fallback cascade in the methodology was not fully executed.
   - Required action: Before accepting the national-time-series-only constraint, attempt to acquire NBS yearbook provincial data for at minimum: provincial employment by sector, provincial GDP, provincial internet penetration. Document the attempt and its outcome. If successful, update the provincial framework and revise the downscoping assessment.

3. **[A3]: ILO modeled employment estimates are partially endogenous to proposed control variables**
   - Domain impact: ILO modeled estimates for China's employment structure are partially predicted from GDP growth, urbanization, and other economic indicators -- the same variables planned as controls in the regression analysis. This creates mechanical correlation: regressing ILO employment estimates on GDP and urbanization may recover the ILO model's own coefficients rather than true structural relationships. This is a fundamental identification concern for the national time series analysis, which is now the primary analytical approach.
   - Required action: Document this endogeneity concern explicitly. Investigate whether China's labor force survey data (from which ILO models are calibrated) is available directly. At minimum, conduct sensitivity analysis comparing results with and without ILO-model-predicted controls. Consider using only the variables that are NOT inputs to the ILO model as controls.

### Category B (Important)

1. **[B1]: Staggered DID methodological concerns not discussed**
   - Domain impact: The recent econometric literature (Goodman-Bacon 2021, Callaway-Sant'Anna 2021) has shown that naive two-way fixed effects DID with staggered treatment produces biased estimates when treatment effects are heterogeneous. The smart city pilot design with three batches is exactly the setting where this matters. While city-level DID is currently blocked by data limitations, if provincial or city-level data becomes available through a data callback, the strategy must use heterogeneity-robust estimators.
   - Suggested action: Add a note in the Open Issues section acknowledging the staggered DID literature. If DID becomes feasible through data callback, mandate Callaway-Sant'Anna or Sun-Abraham estimators rather than naive TWFE.

2. **[B2]: Digital economy index construct validity not benchmarked against known milestones**
   - Domain impact: The composite index should show visible inflections at known digital economy milestones (2013 Alipay/WeChat Pay mobile payment launch, 2015 Internet Plus strategy, 2020 COVID digital acceleration). If it does not, the index may not capture the intended construct. The DATA_QUALITY.md recommends this check for Phase 2 but it should be flagged as a prerequisite validation, not a downstream nice-to-have.
   - Suggested action: Elevate the milestone validation check to a binding requirement for Phase 1/2. If the index fails milestone validation, trigger a data callback for PKU-DFIIC registration.

3. **[B3]: Time series mediation methodology not appropriate for Baron-Kenny framework**
   - Domain impact: DAG 2's testable prediction relies on mediation analysis (Sobel/bootstrap), but these methods assume cross-sectional data. With 24 annual observations, mediation should use VAR-based Granger mediation or structural equation modeling with lagged effects. Applying cross-sectional mediation methods to time series data can produce spurious mediation findings.
   - Suggested action: Note in the Open Issues that Phase 3 mediation analysis must use time-series-appropriate methods (VAR-based decomposition, impulse response functions) rather than cross-sectional Baron-Kenny.

4. **[B4]: Platform economy measurement limitations understated for DAG 3**
   - Domain impact: DAG 3's core prediction requires distinguishing formal sector automation effects from informal/platform sector creation effects. The available ILO data distinguishes self-employed from wage-salaried workers, but platform/gig workers in China are frequently classified as self-employed or as employees of labor dispatch agencies. The self-employed category conflates traditional self-employment (small shop owners, farmers) with platform workers (Meituan riders, Didi drivers). This measurement contamination makes DAG 3's unique prediction (opposite-sign effects by segment) essentially untestable with current data. The analysis acknowledges this partially but does not explicitly state that DAG 3 is infeasible.
   - Suggested action: State explicitly that DAG 3 cannot be meaningfully tested without CFPS or an equivalent micro-dataset that distinguishes platform employment. Reduce DAG 3 to a theoretical framework rather than a testable hypothesis for this analysis.

### Category C (Minor)

1. **[C1]: CNNIC provincial internet data not considered**
   - Suggested action: The China Internet Network Information Center publishes semi-annual reports with provincial-level internet penetration data. Consider adding this as a supplementary data source in the Open Issues or data callback recommendations.

2. **[C2]: Smart city batch timing conventions could be more precise**
   - Suggested action: The experiment log notes that batch 1 was "announced late 2012 / Jan 2013" with treatment year assigned as 2013. Some published studies use 2012 as the treatment year for batch 1. Document the sensitivity of results to this one-year shift in treatment timing as a robustness check item for Phase 3.

3. **[C3]: Edge table citations could be more specific**
   - Suggested action: Several LITERATURE_SUPPORTED edges cite journals (e.g., "Finance Research Letters, 2024") without specific author names or paper titles. While full bibliographic entries are not required in Phase 0, providing at least first-author surnames would improve traceability and allow reviewers to verify the relevance of the cited evidence.

## Acceptance Readiness

I would **not accept** this analysis in its current state due to three blocking issues. The omission of demographic transition as a confounder (A1) is the most consequential domain gap -- it risks attributing labor structure changes to digitalization when population aging is a competing (and potentially dominant) explanation over the 2000-2023 period. The failure to attempt NBS yearbook data acquisition (A2) prematurely constrains the analysis to national time series when publicly available provincial data could enable panel methods. The ILO model endogeneity concern (A3) undermines the validity of the primary (and now only) analytical approach.

The Phase 0 artifacts are otherwise of high quality. The question decomposition is thorough, the competing DAGs are genuinely distinct, the EP calibration is reasonable, and the data quality assessment is commendably honest about limitations. The analysis team clearly understands the domain and has made thoughtful choices about treatment selection, mechanism channels, and testable predictions. Resolving the three Category A issues and addressing the Category B items would bring this to an acceptable standard for Phase 1 advancement.
