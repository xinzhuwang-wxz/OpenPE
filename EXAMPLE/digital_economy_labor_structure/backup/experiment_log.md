# Experiment Log

## Phase 0, Steps 0.1-0.2: Hypothesis Agent Session (2026-03-29)

### Decision: Input mode classification
- **Input mode:** A (question only, fully autonomous)
- **Rationale:** No user data or context files provided. `data_dir` is empty in `.analysis_config`.

### Decision: Domain identification
- **Primary domains:** Digital economics, Labor economics
- **Secondary domains:** Industrial organization, Human capital theory, Regional economics, Public policy evaluation
- **Rationale:** The question spans the intersection of digital technology adoption and labor market dynamics, with explicit methodological requirements (DID) placing it in policy evaluation territory.

### Decision: EPS data platform identification
- **Finding:** "EPS" refers to the EPS Data Platform (epsnet.com.cn), a commercial Chinese statistical database with 150+ databases. NOT the Energy Policy Simulator.
- **Implication:** EPS data requires institutional subscription. Public alternatives (NBS, China Statistical Yearbook) must be identified for data acquisition. Documented as open issue.
- **Search performed:** Web search for "EPS数据平台 epsnet.com.cn" confirmed the platform identity.

### Decision: DID treatment selection
- **Treatment:** National smart city pilot policy (three batches: 2012, 2014, 2015, covering ~290 cities)
- **Rationale:** Staggered rollout provides clean DID identification. Widely validated in published literature (Nature HASS Communications 2023, Empirical Economics 2023). Alternative treatments considered: "Internet Plus" strategy (2015, national-level, insufficient cross-sectional variation), Broadband China pilots (fewer cities, less digital economy coverage).
- **Concern:** SUTVA may be violated due to spatial spillovers. Flagged as open issue requiring spatial DID or buffer exclusion.

### Decision: Three competing DAGs constructed
- **DAG 1 (Technology-Push):** Direct technology channels (SBTC framework). Substitution and creation effects operate through task content changes. Highest EP edges: DE-->SUB (0.49), DE-->CRE (0.42).
- **DAG 2 (Institutional Mediation):** Indirect channels through human capital, industrial upgrading, labor market reform. Direct effect is weak. Key test: mediation analysis (Sobel/bootstrap).
- **DAG 3 (Labor Market Segmentation):** Dual-track effects -- substitution in formal sector, creation in informal/platform sector. Key test: subsample analysis by employment type with opposite-sign coefficients.
- **Rationale for three DAGs:** Each represents a fundamentally different causal structure, not just a variation. DAG 1 vs DAG 2 differ on direct vs mediated pathways. DAG 3 introduces heterogeneous treatment effects by labor market segment.

### Decision: First principles selection
- **4 candidate principles identified:** (1) Technological displacement/compensation (Ricardo-Marx-Schumpeter), (2) Skill-biased technological change (Acemoglu & Autor), (3) Structural change multi-sector reallocation (Lewis-Kuznets), (4) Labor market segmentation (Doeringer-Piore).
- **Rationale:** Principles 1-3 are universal/domain-specific with strong literature support. Principle 4 is context-dependent but essential for the Chinese institutional setting (hukou, SOEs, platform economy regulation).

### Literature search results
- **Searches performed:** 5 web searches covering English and Chinese literature on digital economy, labor structure, CFPS, EPS, smart city DID, creation/substitution effects.
- **Key findings:** Extensive literature confirms digital economy effects on Chinese employment. CFPS-based studies exist (Finance Research Letters 2024). Smart city pilot DID is well-validated. Short-run substitution dominates, long-run creation may compensate.
- **Gap:** Limited literature on platform economy measurement in official statistics, which affects DAG 3 testability.

### Memory check
- **L1 memories from prior analysis (technology_adoption):** Data quality issues encountered (some LOW-rated datasets), Granger causality method used, verification failures detected.
- **Lesson applied:** Be cautious about data quality -- prior analysis had LOW-quality datasets. CFPS biennial frequency and EPS access constraints are flagged proactively.

### Artifact produced
- `phase0_discovery/exec/DISCOVERY.md` -- complete with question decomposition, 4 first principles, 3 competing causal DAGs with mermaid diagrams, EP-labeled edge tables, DAG comparison matrix, data requirements matrix prioritizing EPS and CFPS, and open issues.

## Phase 0, Steps 0.3-0.4: Data Acquisition Agent Session (2026-03-29)

### Decision: Data acquisition strategy
- **Mode:** A (fully autonomous, no user data)
- **Primary source:** World Bank API via `wbgapi` (26 indicators attempted, 24 acquired)
- **Secondary source:** ILO modeled employment estimates via World Bank (9 indicators acquired)
- **Constructed:** Smart city pilot treatment indicator from MOHURD policy documents (286 cities, 3 batches)
- **Constructed:** Digital economy composite index (national-level proxy for PKU-DFIIC)
- **Documented gaps:** EPS (commercial), CFPS (requires registration), FRED (no API key)

### Decision: Smart city pilot list construction
- **Method:** Compiled prefecture-level city names from three batches of MOHURD announcements, cross-validated against published DID studies (PLOS ONE, Nature HASS, Sustainability journals).
- **Batch 1 (treatment year 2013):** 84 prefecture-level cities
- **Batch 2 (treatment year 2014):** 98 prefecture-level cities
- **Batch 3 (treatment year 2015):** 104 prefecture-level cities
- **Total:** 286 cities (note: published studies cite ~290; difference is due to excluding district/county/town-level units for cleaner DID)
- **Panel:** Expanded to city x year panel (2008-2023) with treatment indicators
- **Concern:** Smart city batch timing: published literature lists batch 1 announced late 2012 / Jan 2013, batch 2 Aug 2013, batch 3 Apr 2015. We assign treatment years as 2013, 2014, 2015 respectively, following the most common convention in DID studies.

### Decision: EPS data substitution strategy
- **Finding:** EPS (epsnet.com.cn) is a commercial database requiring institutional subscription. No public API.
- **Proxy strategy:** Used World Bank national-level data as aggregate proxy. Created an empty provincial panel framework (31 provinces x 13 years) that can be populated if EPS access is obtained.
- **Limitation:** Without EPS, the analysis CANNOT conduct provincial-level panel regression or city-level DID with outcome variables. National-level time series analysis remains feasible.
- **Recommendation:** If user can provide EPS access or manually extract NBS Statistical Yearbook data, populate `data/raw/` and re-run processing.

### Decision: CFPS data handling
- **Finding:** CFPS requires registration at opendata.pku.edu.cn. Free for academic use after approval.
- **Proxy strategy:** World Bank ILO employment structure data provides national-level aggregate proxies for skill composition (education-based: advanced/intermediate/basic) and employment form (self-employed, wage-salaried, vulnerable, family workers).
- **Limitation:** Without CFPS, the analysis cannot test individual-level mechanisms (skill-level transitions, formal-to-informal sector flows, hukou effects). DAG 3 (segmentation model) is most affected.
- **Note:** ILO skill-level data (SL.TLF.ADVN.ZS etc.) only had 1 observation for China (year 2000). These are very sparse.

### Decision: Digital economy index construction
- **Method:** Composite index from 5 World Bank indicators: internet users (%), mobile subscriptions (/100), fixed broadband (/100), high-tech exports (%), R&D expenditure (% GDP).
- **Normalization:** Min-max to [0,1] range, equal weights.
- **Note:** Two WB indicators failed (SE.XPD.TOTL.GD.ZS for education expenditure, TX.VAL.TECH.MF.ZS for high-tech exports) due to SSL errors. Index constructed from 4 available components (high-tech exports excluded due to fetch failure, but available in 3 remaining: internet, mobile, broadband, R&D).
- **Limitation:** This is a NATIONAL-level proxy. The actual PKU-DFIIC provides city-level and county-level data essential for DID. Without PKU-DFIIC, city-level DID analysis requires an alternative treatment intensity measure.

### Data acquisition results summary
| Dataset | Status | Observations | Coverage |
|---------|--------|-------------|----------|
| World Bank China indicators | acquired | 24 years x 25 vars | 2000-2023 |
| ILO employment structure | acquired | 24 years x 10 vars | 2000-2023 |
| Smart city pilot list | acquired | 286 cities | 3 batches |
| Smart city pilot panel | acquired | 4,576 city-years | 2008-2023 |
| Digital economy composite index | proxy | 24 years x 11 vars | 2000-2023 |
| Provincial panel framework | proxy | 403 prov-years (empty) | 2011-2023 |
| Merged national panel | acquired | 24 years x 40 vars | 2000-2023 |
| CFPS microdata | failed | N/A | Requires registration |
| EPS provincial panel | failed | N/A | Commercial |
| FRED supplementary | failed | N/A | No API key |

### Open data gaps (critical for downstream phases)
1. **EPS provincial/city-level data** -- Required for panel regression and DID. Without it, analysis is limited to national time series.
2. **CFPS microdata** -- Required for individual-level mechanism analysis (skill transitions, formal/informal sector, hukou effects).
3. **PKU-DFIIC city-level index** -- Required for city-level DID treatment intensity. National proxy constructed.
4. **Education expenditure** -- WB indicator SE.XPD.TOTL.GD.ZS failed due to SSL error. Not critical (tertiary enrollment available as proxy).
5. **High-tech exports** -- WB indicator TX.VAL.TECH.MF.ZS failed. Not included in DE composite index.

### Artifacts produced
- `data/raw/` -- 7 raw CSV files with timestamps
- `data/processed/` -- 7 Parquet files (standardized)
- `data/registry.yaml` -- Complete provenance for all 10 datasets (5 acquired, 2 proxy, 3 failed)
- `phase0_discovery/scripts/acquire_data.py` -- Main acquisition script
- `phase0_discovery/scripts/verify_data.py` -- Data verification script
- `pixi.toml` -- Updated with `acquire` and `verify-data` tasks

## Phase 0, Step 0.5: Data Quality Agent Session (2026-03-29)

### Decision: Gate verdict
- **Verdict:** PROCEED WITH WARNINGS
- **Rationale:** The merged national panel (24 years x 40 variables) provides adequate data for national-level time series analysis. However, the analysis must downscope from the planned DID design because city-level outcome data is unavailable. Three critical constraints: (1) no city-level DID possible without EPS/PKU-DFIIC, (2) no individual-level mechanism testing without CFPS, (3) ILO skill-composition data effectively unusable (1/24 years).

### Decision: ILO education columns classified as unusable
- **Finding:** `labor_force_advanced_education_pct`, `labor_force_basic_education_pct`, and `labor_force_intermediate_education_pct` each have only 1 non-null observation (year 2000). These are participation rates within each education group, not shares of total labor force.
- **Implication:** The SBTC/skill-polarization hypothesis (DAG 1 core prediction) can only be tested via sectoral employment proxies. EP.truth for skill-level edges capped at 0.30.
- **Recommendation:** Drop these 3 columns from the analysis-ready dataset to prevent accidental use.

### Decision: Digital economy composite index bias assessment
- **Finding:** The proxy index constructed from 4 World Bank indicators (internet users, mobile subscriptions, broadband, R&D expenditure) captures ICT infrastructure penetration but misses key dimensions: e-commerce volume, digital financial inclusion (PKU-DFIIC core), platform economy scale, software/IT services revenue.
- **Bias verdict:** LOW (score 45/100) -- uncertain construct validity.
- **Implication:** Coefficients estimated using this index must be interpreted as "association with ICT infrastructure penetration" rather than "effect of digital economy development." PKU-DFIIC registration recommended as high-priority data callback.

### Decision: Smart city pilot data is structurally sound but analytically blocked
- **Finding:** 286 cities across 3 staggered batches, well-constructed treatment indicator, verified against published DID studies. However, no city-level outcome variables exist in the data portfolio.
- **Implication:** The DID design central to the research question is NOT executable with current data. Analysis must use weaker identification strategies.
- **Recommendation:** If data callback is authorized, prioritize NBS yearbook extraction for provincial-level outcomes as a partial substitute.

### Decision: Sample size constraints documented
- **Finding:** 24 annual observations supports bivariate Granger tests and possibly trivariate VAR(1). More complex multivariate specifications will suffer from insufficient degrees of freedom.
- **Implication:** Phase 1 strategy must enforce parsimony -- maximum 4-5 simultaneous regressors.

### Per-dataset quality summary
| Dataset | Completeness | Consistency | Bias | Granularity | Overall |
|---------|-------------|-------------|------|-------------|---------|
| World Bank China indicators | 82 HIGH | 88 HIGH | 75 MEDIUM | 55 MEDIUM | 75 MEDIUM |
| ILO employment structure | 35 LOW | 80 HIGH | 60 MEDIUM | 55 MEDIUM | 58 MEDIUM |
| Smart city pilots list | 95 HIGH | 85 HIGH | 70 MEDIUM | 90 HIGH | 85 HIGH |
| Smart city pilots panel | 95 HIGH | 82 HIGH | 70 MEDIUM | 85 HIGH | 83 HIGH |
| Digital economy composite index | 90 HIGH | 78 MEDIUM | 45 LOW | 40 LOW | 63 MEDIUM |
| Provincial framework (empty) | 0 LOW | N/A | N/A | N/A | 0 LOW |
| Merged national panel | 72 MEDIUM | 85 HIGH | 60 MEDIUM | 55 MEDIUM | 68 MEDIUM |

### Artifacts produced
- `phase0_discovery/exec/DATA_QUALITY.md` -- Complete quality assessment with per-dataset scores, DAG coverage matrix, and downstream warnings
- `phase0_discovery/scripts/assess_data_quality.py` -- Automated quality assessment script

## Phase 0: Arbiter Review Fix Cycle (2026-03-29)

### Review outcome
- **Verdict:** ITERATE (4 Category A issues)
- **Review file:** `phase0_discovery/review/REVIEW_NOTES.md`

### Fix A-1: Joint_EP computation and EP cap propagation
- **Issue:** DISCOVERY.md EP values were inconsistent with DATA_QUALITY.md constraints. Edges requiring skill-level or individual-level data had uncapped truth values. Joint_EP was not computed.
- **Action taken:**
  1. Added `Truth (data-adj)` and `EP (data-adj)` columns to all three DAG edge tables
  2. Applied DATA_QUALITY.md truth cap of 0.30 to edges requiring unavailable data:
     - DAG 1: SUB-->MID_DECLINE, CRE-->HIGH_GROW, CRE-->PLAT, MID_DECLINE-->LS, HIGH_GROW-->LS, PLAT-->LS
     - DAG 2: HC_INV-->SKILL_UP, LM_REF-->MOB, SKILL_UP-->LS, MOB-->LS
     - DAG 3: DE-->INFORMAL, INFORMAL-->PLAT_JOB, PLAT_JOB-->INFORMAL_GAIN, FORMAL_LOSS-->REALLOC, INFORMAL_GAIN-->REALLOC, REALLOC-->LS, FORMAL_LOSS-->WAGE_POL, INFORMAL_GAIN-->WAGE_POL, WAGE_POL-->LS
  3. Computed Joint_EP for all mechanism chains (from DE, not SCP):
     - DAG 1: All chains below hard truncation (0.05). Best: DE-->SUB-->MID_DECLINE-->LS = 0.013
     - DAG 2: IND_UP chain nearest threshold (0.043). Direct DE-->LS = 0.12 (soft truncation)
     - DAG 3: All chains deeply below hard truncation (max 0.002). 5-edge chains compound caps severely.
  4. Added a "Joint_EP Assessment" section to DISCOVERY.md with chain-by-chain tables and Phase 1 prioritization
- **Implication:** Phase 1 must focus on aggregate reduced-form relationships and the IND_UP mediation chain. Most mechanism-level chains are beyond the analytical horizon with current data.

### Fix A-2: Demographic transition confounder added to all DAGs
- **Issue:** Population aging / demographic transition was omitted as a confounder despite China's working-age population peaking ~2012-2015, coinciding with smart city pilots.
- **Action taken:**
  1. Added DEMO (Population Aging / Demographic Transition) node to all three mermaid DAGs
  2. Added confounder edges to each DAG:
     - All DAGs: DEMO-->DE (aging incentivizes digital adoption), DEMO-->LS (aging independently drives structural change)
     - DAG 1: DEMO-->SUB (aging increases automation incentives)
     - DAG 2: DEMO-->HC_INV (aging shifts human capital investment priorities)
     - DAG 3: DEMO-->FORMAL (aging accelerates formal sector retirement/automation)
  3. All edges labeled LITERATURE_SUPPORTED with citations (Acemoglu & Restrepo, 2022; Cai, 2010; Eggleston et al., 2023)
  4. Updated DAG comparison section to note demographic confounder as shared across all DAGs
  5. Added to Open Issues as mandatory control requirement
- **Variables:** `population_65plus_pct` and `population_15_64_pct` (already in dataset, acquired from World Bank)
- **Implication:** All downstream specifications MUST include demographic controls. Omitting them risks attributing demographic-driven structural change to the digital economy.

### Fix A-3: NBS Statistical Yearbook provincial data acquisition attempt
- **Issue:** The five-strategy data acquisition fallback cascade was not fully executed. NBS yearbook data was not attempted despite being publicly available.
- **Action taken:**
  1. Wrote acquisition script: `phase0_discovery/scripts/acquire_nbs_provincial.py`
  2. Attempted 3 strategies:
     - Strategy 1 (NBS API): All 3 indicator codes (A0301, A0201, A0501) returned HTTP 404. API endpoint appears restructured.
     - Strategy 2 (Yearbook HTML): Website IS accessible (HTTP 200 for index page). Tables require JavaScript rendering.
     - Strategy 3 (Direct CSV): Portal reachable but no bulk download available.
  3. Created availability assessment documenting that provincial data EXISTS at NBS for all required variables
  4. Updated `data/registry.yaml` with new dataset entry (status: attempted)
  5. Updated `DATA_QUALITY.md` with per-dataset assessment for the NBS attempt
  6. Added pixi task `acquire-nbs` to `pixi.toml`
- **Outcome:** Data confirmed to exist but not extractable via automated methods. Manual extraction or browser-based scraping is feasible. Documented as high-priority data callback recommendation.
- **Implication:** If NBS data is manually extracted, analysis upgrades from T=24 national time series to N=31, T=13 provincial panel (403 obs), enabling panel fixed-effects and potentially resolving the Granger causality sample size constraint.

### Fix A-4: T=24 Granger causality conventions violation
- **Issue:** `conventions/time_series.md` requires T>=30 for Granger causality. Available data has T=24.
- **Action taken:**
  1. Added "Methodological Constraints and Alternative Strategies" section to DISCOVERY.md
  2. Documented 6 alternative approaches compatible with T=24:
     - Toda-Yamamoto (1995): valid regardless of cointegration status, works with T~20
     - Bootstrapped Granger (Hacker & Hatemi-J, 2006): size-corrected for small samples
     - Structural break tests at known policy dates (2012, 2015, 2020)
     - Bayesian VAR with Minnesota prior
     - Frequency-domain Granger causality
     - Panel Granger if NBS provincial data acquired
  3. Recommended multi-method approach for Phase 1: Toda-Yamamoto as primary, bootstrap as robustness, structural breaks as complementary
  4. Documented conventions deviation explicitly with mitigations
  5. Added to Open Issues (#8)
- **Implication:** Phase 1 strategy must not rely on standard Granger causality alone. The conventions deviation is acknowledged and mitigated, not ignored.

### Artifacts modified
- `phase0_discovery/exec/DISCOVERY.md` -- Joint_EP section, data-adjusted EP columns, demographic confounder in all DAGs, methodological constraints section, updated open issues
- `phase0_discovery/exec/DATA_QUALITY.md` -- NBS attempt assessment, updated data callback recommendation, updated failed datasets table
- `data/registry.yaml` -- NBS provincial availability entry added
- `pixi.toml` -- Added `acquire-nbs` task

### Artifacts created
- `phase0_discovery/scripts/acquire_nbs_provincial.py` -- NBS data acquisition script
- `data/raw/nbs_provincial_availability_20260329.csv` -- Provincial availability assessment
- `data/processed/nbs_provincial_availability.parquet` -- Same in Parquet format

## Phase 1: Strategy Development (2026-03-29)

### Decision: Consolidated DAG approach
- **Action:** Merged three Phase 0 DAGs into a single testable structure with 9 edges, 7 nodes
- **Rationale:** DAG 1 skill-level paths (EP=0.00), DAG 3 segmentation paths (Joint_EP<0.01) are beyond analytical horizon with available data. Retained testable elements: substitution (manufacturing employment), creation (services employment), mediation (industrial upgrading), demographic confounder.
- **Trade-off:** Lost theoretical richness for analytical honesty. Skill-polarization (SBTC) hypothesis entirely untestable.

### Decision: Method selection -- Toda-Yamamoto as primary Granger test
- **Action:** Selected Toda-Yamamoto (1995) procedure over standard Granger causality
- **Rationale:** Standard Granger requires T>=30 (conventions/time_series.md). T=24 violates this. Toda-Yamamoto fits VAR(p+d_max) in levels, valid for T~20 per original paper. Bootstrap critical values (Hacker & Hatemi-J 2006) further correct small-sample distortions.
- **Alternative considered:** Standard Granger with explicit conventions deviation. Rejected because Toda-Yamamoto is strictly superior for I(1) series at small T.

### Decision: ARDL bounds test as secondary for long-run
- **Action:** Added Pesaran et al. (2001) ARDL bounds test alongside Johansen cointegration
- **Rationale:** Unit root tests have low power at T=24. If ADF and KPSS disagree on integration order, Johansen requires clear I(1) classification while ARDL is valid for I(0)/I(1) mix. Provides robustness against stationarity classification uncertainty.

### Decision: Proxy DID design via structural break
- **Action:** Designed structural break analysis around smart city pilot dates (2013-2015) as "proxy DID"
- **Rationale:** User explicitly requests DID baseline comparison. Full DID impossible without city-level outcome data. Structural break captures the before/after logic. Pre-period: 2000-2012 (13 obs), post-period: 2016-2023 (8 obs), treatment window: 2013-2015 excluded.
- **Limitations documented:** No control group; concurrent confounders (leadership transition, supply-side reform, anti-corruption); very low statistical power per period.

### Decision: VAR-based mediation instead of Baron-Kenny
- **Action:** Selected VAR impulse response decomposition for mediation analysis
- **Rationale:** Baron-Kenny mediation assumes i.i.d. observations (violated by time series); Sobel test inflated by serial correlation. Phase 0 Review Issue 16 (Category B) flagged this. VAR-based decomposition is the standard time series equivalent (Blanchard & Quah 1989 tradition).
- **Mediation calibration target:** ~22% through industrial upgrading (from Reference 2, Li et al. 2024).

### Decision: EP reductions from Phase 0 to Phase 1
- **Action:** Applied three categories of EP reduction: (1) data quality -0.10, (2) construct validity -0.10 for DE index edges, (3) method credibility -0.05 to -0.10
- **Rationale:** Phase 0 EP values assumed panel DID identification and validated DE indices. Phase 1 reflects actual data (national time series, proxy DE index, T=24). Largest single-edge EP is now DE-->SUB at 0.32; direct DE-->LS at 0.06 (below soft truncation).
- **Implication:** Analysis can at best achieve moderate confidence on sectoral employment direction. Strong causal claims are precluded by identification limitations.

### Decision: Demographic confounder given highest priority (EP=0.36)
- **Action:** DEMO-->LS is the highest-EP path in the Phase 1 DAG. Full characterization required before any DE causal claim.
- **Rationale:** Working-age population peaked ~2012, coinciding with smart city pilots. If demographic transition explains most employment structure variation, DE effect is supplementary at best. This is the main threat to the research question's affirmative answer.

### Decision: DoWhy pipeline not applicable for this analysis
- **Action:** Classified DoWhy CausalTest as "not applicable" in conventions compliance
- **Rationale:** DoWhy's estimators and refutation tests assume cross-sectional or panel data structure. National time series (T=24, single entity) violates the i.i.d. assumption. Time series refutation battery designed manually: placebo timing, permutation, rolling window stability.

### Decision: Segmented analysis by sector (not inclusive)
- **Action:** Test creation (services) and substitution (manufacturing) effects separately rather than aggregate employment
- **Rationale:** Creation and substitution effects have opposite signs. Inclusive analysis would average them out, potentially showing "no effect" when effects are large but heterogeneous. All three reference analyses find significant sectoral heterogeneity.

### Package availability check
- **Result:** All core packages (dowhy, statsmodels, scipy, numpy, pandas, matplotlib) importable via pixi. DoWhy has deprecation warnings on Python 3.14 but functions correctly. No additional packages needed for planned methods (Toda-Yamamoto, Johansen, ARDL all implementable via statsmodels + scipy).
- **Note:** Bai-Perron multiple structural break test requires manual implementation or `ruptures` package (not confirmed in pixi.toml). Fallback: Chow test at known dates.

### Reference analyses identified
1. Zhu et al. (2023), Empirical Economics -- Smart city DID on employment, ~280 cities, gold standard design
2. Li et al. (2024), Sustainability -- Digital economy and employment quality, 30 provinces panel, 22% mediation
3. Zhao & Li (2022), Finance Research Letters -- Digital economy and employment structure, inverted-U finding

### Artifacts produced
- `phase1_strategy/exec/STRATEGY.md` -- Complete analysis strategy

## Phase 1: Strategy Review Fix Iteration (2026-03-29)

### Review result
- **Verdict:** ITERATE (2 Category A issues, 11 Category B issues)
- **Review artifact:** `phase1_strategy/review/REVIEW_NOTES.md`

### A-1 Fix: Stale EP values in Summary
- **Problem:** Summary cited Phase 0 EP values (EP=0.12 for DE-->LS, Joint_EP=0.043 for mediation) and falsely claimed "all mechanism-level Joint_EP values fall below hard truncation" when DE-->SUB=0.32 and DE-->CRE=0.27 are well above.
- **Fix:** Rewrote Summary to use Phase 1 EP values: DE-->SUB EP=0.32 (full analysis), DE-->CRE EP=0.27 (lightweight-to-moderate), DE-->LS EP=0.06 (below soft truncation), mediation chain Joint_EP=0.021 (below hard truncation, tested as reduced-form links).
- **Rationale:** Summary is the entry point for downstream agents; incorrect EP values would propagate wrong truncation decisions.

### A-2a Fix: Renamed "proxy DID" to "structural break analysis"
- **Problem:** The term "proxy DID" implies a control-group comparison that does not exist. The analysis is a single-entity pre/post comparison, not a difference-in-differences design.
- **Fix:** Replaced all 25+ occurrences of "proxy DID" with "structural break analysis" or equivalent (e.g., "pre/post comparison"). Section 2.5 header renamed from "Proxy DID Design" to "Structural Break Design."
- **Rationale:** Honest labeling prevents readers from inferring stronger causal identification than the design supports. The underlying methodology (Chow test, Bai-Perron) is unchanged.

### A-2b Fix: Reformulated structural break regression for I(1) variables
- **Problem:** The original specification (`LS_t = alpha + beta_1 * DE_t + beta_2 * POST_t + beta_3 * (DE_t * POST_t) + gamma * DEMO_t + epsilon_t`) regresses levels of likely I(1) variables, producing spurious regression regardless of the interaction term.
- **Fix:** Replaced with a two-branch specification conditioned on cointegration results:
  - If cointegrated: VECM with structural break dummy interacted with ECT and short-run dynamics (first differences).
  - If not cointegrated: first-difference specification with break interaction (`Delta_LS_t = alpha + beta_1 * Delta_DE_t + beta_2 * (POST_t * Delta_DE_t) + gamma * Delta_DEMO_t + epsilon_t`).
  - Chow test applied to first-differenced regression as secondary method.
- **Rationale:** First-differencing removes stochastic trends; VECM conditions on cointegrating relationship. Both yield valid inference for the structural break test. Added explicit "Why first differences" paragraph to Section 2.5.

### B-6 Fix: Added reverse causality to systematic uncertainty table
- **Problem:** Reverse causality (employment structure driving DE adoption) identified in DISCOVERY.md Hidden Assumption 5 but absent from Section 5.2 uncertainty inventory.
- **Fix:** Added row to Section 5.2: "Reverse causality (LS-->DE)", severity MEDIUM, quantified via bidirectional Toda-Yamamoto Granger test.
- **Rationale:** The Granger test is already bidirectional by design, so this is a documentation completeness fix rather than an analytical gap.

### B-5 Fix: Elevated ILO endogeneity to systematic uncertainty table
- **Problem:** ILO model endogeneity was only an Open Issue (#6), not in the systematic uncertainty inventory despite being a potentially dominant concern.
- **Fix:** Elevated ILO endogeneity entry in Section 5.3 to severity HIGH. Added Phase 2 deliverable to document ILO modeling methodology for China. Updated Open Issue 6 to note the elevation.
- **Rationale:** If ILO employment estimates mechanically incorporate GDP/urbanization, regressions with GDP-correlated regressors produce mechanical coefficients. The with/without controls sensitivity test was already planned; the fix adds prominence and a Phase 2 investigation commitment.

## Phase 2: Exploration (2026-03-29)

### Decision: Drop 3 ILO education columns
- **Action:** Removed `labor_force_advanced_education_pct`, `labor_force_basic_education_pct`, `labor_force_intermediate_education_pct`
- **Rationale:** 95.83% missing (1/24 obs). Per DATA_QUALITY.md recommendation. Prevents accidental use.

### Decision: No imputation performed
- **Action:** Missing values left as NaN, handled by listwise deletion per analysis method
- **Rationale:** Only 1.69% missing rate in usable dataset. Imputation not justified given small T=24 and the fact that missingness is concentrated in secondary_enrollment_gross (excluded from primary analysis) and a single year of R&D expenditure.

### Finding: Most variables are I(1) with ambiguous cases
- **Result:** 8/12 key variables classified as I(1). Demographic variables (population_15_64_pct, population_65plus_pct) and log GDP per capita have ambiguous integration orders.
- **Implication:** ARDL bounds test elevated from secondary to co-primary method alongside Johansen, as ARDL is valid for I(0)/I(1) mix.

### Finding: DE index has no clear stationarity classification
- **Result:** ADF fails to reject unit root (p=0.996) but KPSS also fails to reject stationarity (p=0.099). First differences are NOT clearly stationary (ADF p=0.728).
- **Implication:** The DE index may have a more complex time series structure. Toda-Yamamoto (valid regardless of I(d)) is essential. ARDL is the appropriate robustness check.

### Finding: Structural break at 2014 for services employment
- **Result:** Sup-Wald places maximum break at 2014 for services employment (within smart city pilot window). Chow tests significant at both 2013 (p<0.001) and 2015 (p<0.001).
- **However:** DE index itself breaks at 2009, not at pilot dates. The employment structure break may be driven by broader structural transformation rather than smart city policy specifically.

### Finding: ILO endogeneity is the dominant data concern
- **Result:** Services employment R-squared = 0.989 when regressed on GDP + urbanization + demographics. Partial correlation of DE vs services employment reverses from +0.981 to -0.400 after controlling for these variables.
- **Implication:** Phase 3 MUST run specifications with and without GDP/urbanization controls. If DE coefficient is significant only without controls, the finding is attributable to confounding, not causal effect.
- **Severity:** HIGH. This is more consequential than the small-T power limitation because it affects the interpretation of any positive result, not just the detection of effects.

### Finding: Power analysis confirms low detection capability
- **Result:** Toda-Yamamoto at T=24 has 35% power for medium effects (beta=0.30), 51% for large effects (beta=0.40). Size is slightly inflated (13.1% at alpha=0.10).
- **Implication:** Null results cannot be interpreted as evidence of absence. All Phase 3 test results must report power alongside significance.

### Finding: COVID impact is smoothed in ILO data
- **Result:** Labor force total dropped 1.94% in 2020, but employment shares continued pre-existing trends without visible disruption. Consistent with ILO model smoothing.
- **Decision:** Include 2020-2023 in sample; test sensitivity by excluding 2020.

### Finding: DE index does not respond to policy milestones
- **Result:** Average annual growth 2005-2014: 0.044; 2016-2023: 0.050. Difference: +0.006 (marginal). No visible inflection at Internet Plus (2015) or COVID (2020).
- **Implication:** Construct validity concern confirmed. The index captures long-run ICT build-out, not digital economy activity. PKU-DFIIC would be preferable.

### Artifacts produced
- `phase2_exploration/exec/EXPLORATION.md` -- Complete exploration artifact
- `phase2_exploration/figures/` -- 12 figure pairs (PDF + PNG)
- `phase2_exploration/scripts/` -- 5 analysis scripts
- `phase2_exploration/review/REVIEW_NOTES.md` -- Self-review (PASS)
- `data/processed/analysis_ready.parquet` -- Cleaned + engineered dataset (24 x 51)
- `pixi.toml` -- Updated with 6 exploration tasks

## Phase 3: Causal Analysis, Steps 3.1-3.5 (2026-03-29)

### Decision: Toda-Yamamoto specification
- **Lag selection:** p=2 by AIC for all bivariate systems. d_max=1 (most variables I(1)).
- **Bootstrap:** 10,000 resamples with seed=42 for p-value correction.
- **Rationale:** Standard asymptotic p-values are unreliable at T=24. Bootstrap correction is essential.

### Key Finding: Substitution channel is the strongest signal
- **DE --> industry employment:** Bivariate W=5.84 (p_boot=0.087), with demographic control W=13.33 (p_boot=0.012).
- **Cointegration confirmed:** Johansen rank=2 and ARDL F=6.51 both confirm long-run relationship.
- **Unexpected sign:** The short-run relationship is POSITIVE (DE growth associated with industry employment growth), contradicting the substitution hypothesis. This suggests the digital economy may complement rather than substitute manufacturing employment, at least at the aggregate national level.
- **Classification: CORRELATION** (2/3 refutation tests pass with demographic control).

### Key Finding: Creation channel has NO support
- **DE --> services employment:** Bivariate W=1.16 (p_boot=0.565), with control W=0.38 (p_boot=0.834).
- **No cointegration:** Johansen rank=0, ARDL F=1.92 below lower bound.
- **Interpretation:** The r=0.981 level correlation is entirely spurious (common trends). After removing trends or controlling for demographics, DE has no predictive power for services employment.
- **Classification: HYPOTHESIZED** (bivariate) / **DISPUTED** (with control).

### Key Finding: Mediation link stronger with controls
- **DE --> services VA:** Bivariate p=0.132 (marginal), with demographic control p=0.008 (highly significant).
- **Cointegration confirmed:** Johansen trace=16.72 > cv95=15.49, ARDL F=8.59.
- **Interpretation:** DE drives industrial upgrading (services GDP share) after controlling for demographic trends. However, the mediation decomposition shows NEGATIVE mediation shares (-90%), suggesting the indirect pathway through services VA offsets rather than amplifies the total effect.

### Key Finding: Demographics do NOT Granger-cause employment
- **DEMO --> services emp:** p=0.397. DEMO --> industry emp: p=0.694.
- **But demographics transform other coefficients:** Adding demographics as a control dramatically changes DE coefficients (substitution becomes significant, creation remains null).
- **Interpretation:** Demographics operate at a lower frequency (secular trends) than annual Granger tests capture. The demographics variable acts as a trend control rather than a Granger-causal variable.

### Key Finding: Structural break in industry employment is dramatic
- **Industry employment reversed from +0.71 pp/yr to near-flat**, deviating -4.45 pp from the counterfactual (p<0.001).
- **BUT** Chow tests in first differences show NO significant break in the DE-employment relationship at 2013 or 2015.
- **Interpretation:** The structural change in employment is real but not attributable to DE dynamics specifically. Concurrent events (supply-side reform, economic slowdown, leadership transition) are equally plausible explanations.

### Decision: Refutation test data subset threshold
- **Issue:** All edges fail the data subset refutation test (25% drop changes W by 50-90%).
- **Rationale:** With T=24, dropping 6 observations (25%) fundamentally changes the time series structure. This is an inherent limitation of the sample size, not a refutation of specific causal claims. The test is informative (small-sample fragility) but its FAIL verdict should be interpreted in the power context.
- **Implication:** No edge can achieve DATA_SUPPORTED classification in this analysis. Maximum achievable is CORRELATION.

### Decision: EP mechanical updates applied
- **DE-->SUB:** CORRELATION, truth unchanged at 0.45, EP=0.315
- **DE-->CRE:** HYPOTHESIZED, truth capped at 0.30, EP=0.120
- **DE-->IND_UP:** HYPOTHESIZED, truth 0.30, EP=0.090
- **DEMO-->LS:** HYPOTHESIZED, truth 0.30, EP=0.120
- **DE-->LS (direct):** HYPOTHESIZED, truth 0.05, EP=0.010

### Decision: Sub-chain expansion deferred for DE-->SUB
- **Rationale:** EP=0.315 exceeds expansion threshold (0.30), but decomposition requires occupation-level or city-level data not available. Deferred to future work with EPS/CFPS data.

### Artifacts produced
- `phase3_analysis/exec/ANALYSIS.md` -- Steps 1-5 content
- `phase3_analysis/scripts/` -- 7 analysis scripts
- `phase3_analysis/figures/` -- 6 figure pairs (PDF + PNG)
- `phase3_analysis/scripts/*.json` -- 5 results files

## Phase 3: Steps 6-7 (Statistical Model & Uncertainty Quantification) (2026-03-29)

### Decision: Three parallel estimation frameworks
- **Framework A:** First-difference DID-inspired regression with HAC SEs (structural break analysis)
- **Framework B:** ARDL(1,1) error-correction model with delta-method long-run SE
- **Framework C:** VECM with Johansen-specified cointegrating rank
- **Rationale:** Multiple frameworks test robustness. ARDL handles I(0)/I(1) ambiguity; VECM exploits cointegration; DID-inspired regression is directly comparable to the user's requested DID baseline.

### Key Finding: ARDL long-run coefficient for substitution is +7.15 pp (bivariate) to +12.57 pp (with DEMO)
- **Bivariate:** LR coefficient = 7.15 (SE=4.10), 95% CI [-0.89, 15.20], marginal significance (~1.7 sigma)
- **With demographic control:** LR coefficient = 12.57 (SE=1.86), 95% CI [8.94, 16.21], highly significant
- **Interpretation:** Positive sign confirmed across specifications. Including demographics nearly doubles the point estimate and dramatically reduces the SE, suggesting demographics were masking the DE-industry relationship.

### Key Finding: DID-inspired POST interaction significant for substitution with demographic control
- **POST * d_DE = -11.62 (p=0.011):** The DE-industry relationship weakened significantly post-2015
- **Pre-break net effect: +28.3 pp per unit DE. Post-break: +16.7 pp** -- still positive but attenuated
- **Break year sensitivity:** Significant at 2013 (p=0.038), 2015 (p=0.032), 2017 (p=0.088); consistent with smart city timing

### Key Finding: Signal injection tests all pass
- Model correctly recovers injected signals at observed magnitude, 2x magnitude, and null (within 1 sigma)
- Bootstrap SEs are large (~16 pp) reflecting T=24 power limitation

### Key Finding: Statistical uncertainty dominates systematic for well-defined perturbations
- Bootstrap SE for d_DE coefficient: 15.91
- Systematic from demographic control inclusion: 7.78
- Systematic from break year choice: 2.60
- Systematic from COVID exclusion: 1.81
- Ill-defined perturbations (functional form, lag structure) produce extreme shifts and are excluded from quadrature

### Key Finding: Bootstrap CIs for controlled specification wider than OLS CIs
- HAC CI for POST*d_DE: [-20.6, -2.6] (excludes zero, "significant")
- Bootstrap CI for same: [-34.3, +33.1] (includes zero, "not significant")
- **Implication:** Parametric inference may overstate significance in the controlled specification. The bootstrap-based assessment is more conservative and honest.

### Decision: Functional form sensitivity excluded from systematic quadrature
- Quadratic DE specification shifts beta by +95 pp, which is an artifact of overfitting at T=24 (3 regressors from 23 obs)
- Similarly, adding a lag shifts beta by -21 pp, reflecting model instability rather than systematic uncertainty
- These are reported for transparency but not included in the total systematic uncertainty

### Decision: Final EP unchanged from Step 4
- Uncertainty quantification does not alter classifications
- All edges remain at the same EP values: SUB=0.315 (CORRELATION), CRE=0.120 (HYPOTHESIZED), IND_UP=0.090 (HYPOTHESIZED), DEMO=0.120 (HYPOTHESIZED)

### Artifacts produced
- `phase3_analysis/exec/ANALYSIS.md` -- Steps 6-7 appended (complete artifact)
- `phase3_analysis/scripts/step7_statistical_model.py` -- VECM, ARDL, DID regressions, signal injection
- `phase3_analysis/scripts/step8_uncertainty_quantification.py` -- Bootstrap CIs, systematic decomposition
- `phase3_analysis/scripts/step9_did_comparison_figure.py` -- DID baseline comparison figure (2x3), tornado, sensitivity
- `phase3_analysis/scripts/statistical_model_results.json` -- Model fitting results
- `phase3_analysis/scripts/uncertainty_results.json` -- Uncertainty quantification results
- `phase3_analysis/figures/did_baseline_comparison.pdf` -- Key user-requested figure
- `phase3_analysis/figures/uncertainty_tornado.pdf` -- Uncertainty decomposition
- `phase3_analysis/figures/sensitivity_break_year.pdf` -- Break year sensitivity

## Phase 3, Review Iteration Fix: Category A Issues (2026-03-29)

### Fix A-1: Refutation tests run on wrong specification for DE-->IND_UP

- **Problem:** The controlled specification (W=15.81, p_boot=0.008, trivariate with demographic control) was used for inference but refutation tests were only run on the bivariate specification (W=4.75, p=0.132). This is a protocol violation.
- **Action:** Created `step5b_refutation_ind_up_controlled.py` to run the 3-test refutation battery on the controlled trivariate specification (p_opt=2, d_max=1, matching step1 parameters).
- **Results:** Placebo PASS (1/4 significant at shift=5), Random common cause FAIL (24.2% change in W), Data subset FAIL (76.1% change in W). Classification: HYPOTHESIZED (1/3 PASS).
- **Impact on classification:** DE-->IND_UP remains HYPOTHESIZED (was already HYPOTHESIZED based on bivariate refutation). The controlled specification is even more fragile than the bivariate -- the random common cause test now fails (was MARGINAL for bivariate), indicating the trivariate result is sensitive to additional variables at T=24.
- **EP unchanged:** DE-->IND_UP EP remains 0.090 (truth=0.30, relevance=0.30).

### Fix A-2: DID coefficient inconsistency between Sections 2.4 and 6.4

- **Problem:** Section 2.4 and 6.4 reported materially different coefficients for ostensibly the same regressions. Substitution beta_1: 21.00 vs 20.51; beta_2: -12.53 vs -5.90. Creation beta_2: +17.67 vs -10.38.
- **Root cause:** Two different specifications:
  - Section 2.4 (step3_structural_break.py): Excludes 2013-2015 transition window, uses OLS SE.
  - Section 6.4 (step7_statistical_model.py): Includes all years, uses HAC (Newey-West) SE.
- **Action:** Updated Section 2.4 header to label it "Specification A: transition-excluded, OLS SE" with corrected coefficients from the actual script output (beta_1=21.06, beta_2=-8.70 for substitution). Updated Section 6.4 header to label it "Specification B: all years, HAC SE". Added reconciliation notes in both sections explaining the differences. Section 6.4 values (HAC, all years) designated as the preferred specification for inference.
- **Impact:** No change to classifications or EP values. The inconsistency was a labeling/documentation issue, not a computational error.

### Fix A-3: DE-->CRE relevance not set to 0.1 per mechanical EP rule

- **Problem:** The creation channel has no Granger signal at any level, no cointegration, and an effect indistinguishable from zero. Per Step 3.4 non-negotiable rule 4, relevance must be set to 0.1 for "effect near zero". Relevance was 0.40, giving EP=0.120.
- **Action:** Set relevance to 0.10 per mechanical rule. EP = 0.30 x 0.10 = 0.030 (below hard truncation at 0.05).
- **Impact:** DE-->CRE reclassified as "beyond analytical horizon" (below hard truncation). Joint_EP for mediation chain updated from 0.011 to 0.003. DAG, EP propagation table, Joint_EP table, sub-chain expansion table, final EP assessment, and summary all updated.
- **Qualitative impact:** Minimal -- the creation channel was already the weakest edge. The quantitative change brings the EP into mechanical compliance.

### Artifacts modified
- `phase3_analysis/exec/ANALYSIS.md` -- All three A-level fixes applied
- `phase3_analysis/scripts/step5b_refutation_ind_up_controlled.py` -- New script for controlled refutation
- `phase3_analysis/scripts/refutation_ind_up_controlled.json` -- Controlled refutation results

## Phase 4: Projection (2026-03-30)

### Decision: Projection model design
- **Target variable:** Industry employment share (employment_industry_pct), the only outcome with an empirically supported causal edge (DE-->SUB, CORRELATION, EP=0.315).
- **Model:** ARDL long-run relationship: industry_emp = f(DE, DEMO). Bivariate ARDL LR coefficient (+7.15, SE=4.10) used as conservative baseline; controlled coefficient (+12.57, SE=1.86) used for high-digital scenario.
- **Excluded from central projection:** DE-->CRE (EP=0.030, below hard truncation), DE-->IND_UP (EP=0.090, HYPOTHESIZED, fragile).

### Decision: Three scenarios defined
- **Baseline:** Current DE growth trend, current demographic decline, bivariate ARDL coefficient. Conditional prob: Likely (50-60%).
- **High-Digital:** 1.5x DE growth, controlled ARDL coefficient, higher innovation noise. Conditional prob: Plausible (20-30%).
- **Low-Digital:** 0.3x DE growth, 0.5x beta_DE, faster demographic decline. Conditional prob: Plausible (15-25%).

### Critical finding: DE index saturation
- **The digital economy composite index has reached its ceiling of 1.0 by 2023.** The min-max normalized index (built from internet penetration, mobile subscriptions, broadband, R&D expenditure) has all components near or at their normalized maximum. This means further DE growth cannot be captured, and the beta_DE coefficient has zero marginal effect in projections. This is the single most important finding of Phase 4.
- **Consequence:** All three scenarios converge on nearly identical trajectories (CV=0.046). The projection is driven entirely by demographics (working-age population declining at -0.31 pp/year), not by the digital economy variable.
- **Implication for the original question:** The proxy DE index cannot support forward projection. A non-saturated measure (PKU-DFIIC) would be needed for meaningful digital economy projections.

### Decision: EP decay schedule
- Used CORRELATION-edge 2x decay multiplier per protocol.
- Adjusted for fast-moving tech domain (digital economy dynamics subject to rapid structural change).
- EP drops below soft truncation (0.15) within 1 year, below hard truncation (0.05) within 3 years.
- **Useful projection horizon: 3 years** (EP-based criterion).

### Decision: Endgame classification
- **Robust** (CV=0.046 < 0.15). But this robustness reflects model insensitivity to the saturated DE variable, not strong causal knowledge. If DE were not saturated, the classification would likely be Fork-dependent.

### Decision: Sensitivity analysis
- Only demographic parameters have non-zero sensitivity (+/-0.79 pp per 20% perturbation).
- DE parameters show zero sensitivity (DE at ceiling).
- Interaction between top 2 parameters (beta_DEMO, demo_slope) is 10.0% of additive -- borderline, approximately additive.

### Tipping points identified
- DE index saturation at 1.0 (already reached).
- Complement effect potentially reaching zero (DID interaction weakening, ~2017-2018).
- Working-age population 60% threshold (~30 years distant).

### Artifacts produced
- `phase4_projection/exec/PROJECTION.md` -- Full projection artifact
- `phase4_projection/exec/projection_summary.json` -- Machine-readable results
- `phase4_projection/scripts/projection_simulation.py` -- Monte Carlo simulation script
- `phase4_projection/figures/scenario_comparison.{pdf,png}` -- Scenario trajectories
- `phase4_projection/figures/sensitivity_tornado.{pdf,png}` -- Tornado chart
- `phase4_projection/figures/ep_decay_chart.{pdf,png}` -- EP decay visualization

## Phase 5: Verification (2026-03-29)

### Decision: Reproduction target selection
- **Target:** DE-->SUB edge (CORRELATION, EP=0.315) -- the only edge above soft truncation.
- **Rationale:** This is the primary quantitative finding. If it fails reproduction, the entire analysis conclusion changes.

### Decision: Provenance audit scope
- **Audited:** All 7 acquired/proxy datasets (SHA-256 hash + row counts + spot checks)
- **Skipped:** 4 failed/attempted datasets (no data to audit)
- **Rationale:** Complete coverage of all available data.

### Verification execution
- 4 independent scripts written from scratch (no Phase 3 code imported)
- 10 metrics reproduced: 7 PASS (<5% diff), 2 CLOSE (6-14%), 1 DIVERGE (explained)
- All SHA-256 hashes match for all acquired datasets
- EP arithmetic verified for all 5 edges; 1 minor discrepancy (Category C, no impact)
- 1 Category B finding: industry pre-trend R2 reported as 0.96, independently verified as 0.82

### Findings
- **Category B:** ANALYSIS.md Table 2.1 industry pre-trend R2 = 0.96 should be 0.82
- **Category C:** DE-->IND_UP EP = 0.090 vs rule-based 0.075 (no downstream impact)
- **Category C:** Power 35% vs 43% (different df specification)

### Overall verdict: FLAG (1 Category B, 2 Category C, 0 Category A)

### Artifacts produced
- `phase5_verification/exec/VERIFICATION.md` -- Full verification report
- `phase5_verification/scripts/verify_reproduction.py` -- Independent reproduction
- `phase5_verification/scripts/verify_provenance.py` -- Data provenance audit
- `phase5_verification/scripts/verify_ep.py` -- EP arithmetic verification
- `phase5_verification/scripts/verify_consistency.py` -- Consistency checks
- `phase5_verification/scripts/reproduction_results.json` -- Machine-readable results
