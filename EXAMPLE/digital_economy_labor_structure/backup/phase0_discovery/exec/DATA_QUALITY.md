# Data Quality Assessment

## Summary

The acquired data portfolio has significant structural limitations that constrain the analysis to **national-level time series only**. The two datasets the user explicitly requested -- EPS provincial panel and CFPS microdata -- both failed acquisition (commercial and registration-gated, respectively). The available World Bank and ILO data provide adequate national aggregate coverage (2000--2023, 24 years) for macro-level trend analysis, but cannot support the city-level DID analysis or individual-level mechanism testing that the causal DAGs require. The smart city pilot treatment indicator is well-constructed but has no corresponding outcome variables at the city level. The ILO skill-composition variables (education-based labor force breakdown) are effectively unusable -- only 1 of 24 years has data. The overall gate decision is **PROCEED WITH WARNINGS**.

## Gate Decision

**Verdict: PROCEED WITH WARNINGS**

**Justification:** The merged national panel (24 years x 40 variables) provides sufficient data for national-level time series analysis of the digital economy--labor structure relationship. However, three critical constraints bind:

1. **No city-level DID is possible.** The smart city pilot treatment indicator exists (286 cities, 3 batches), but there are no city-level outcome variables (employment structure, digital economy index). Without EPS data or PKU-DFIIC, the DID design -- which is central to all three causal DAGs -- cannot be executed. The analysis must downscope to national time series and Granger causality / structural break methods.

2. **No individual-level mechanism testing.** Without CFPS microdata, DAG 2 (institutional mediation via human capital) and DAG 3 (labor market segmentation) cannot be tested at the mechanism level. The analysis can only test aggregate proxies of these channels.

3. **ILO skill-composition data is effectively missing.** The three education-based labor force columns (advanced/basic/intermediate education) have only 1 observation each (year 2000). These variables are critical for testing the SBTC / skill-polarization predictions of DAG 1 and cannot support any time series analysis.

**Constraints on conclusions (binding for all downstream phases):**
- Causal claims must be limited to national aggregate relationships; no city-level or individual-level causal identification is available
- DID estimates cannot be produced; the analysis must rely on weaker identification strategies (time series, structural breaks, Granger causality)
- Skill-polarization analysis is limited to sectoral employment shares as a proxy (not actual skill-level data)
- EP.truth for any edge requiring city-level or individual-level data is capped at 0.30
- Any conclusion about heterogeneity across labor market segments (DAG 3) must be flagged as speculative without CFPS verification
- The digital economy composite index is a national-level proxy, not the validated PKU-DFIIC; its construct validity is weaker

---

## Per-Dataset Assessment

### Dataset: worldbank_china_indicators

**Source:** World Bank (World Development Indicators), CC-BY 4.0
**Status:** Acquired
**Shape:** 24 rows x 25 columns (2000--2023, annual)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 82    | HIGH    | 2.33% overall missing rate. 23/25 variables fully complete. Two gaps: `secondary_enrollment_gross` missing 13/24 years (54%), `rd_expenditure_pct_gdp` missing 1/24 years (4%). Core employment and GDP variables have zero missing values. |
| Consistency  | 88    | HIGH    | No duplicate rows. All percentage variables within plausible ranges. `domestic_credit_private_pct_gdp` exceeds 100% (range 100--190%) which is expected for China's credit-heavy economy, not a data error. No unexplained structural breaks. Monotonic trends in GDP, urbanization, internet penetration are internally consistent. |
| Bias         | 75    | MEDIUM  | ILO-modeled employment estimates (not survey-based) may smooth short-term fluctuations. China's official unemployment rate (3.3--5.0%) is known to understate true unemployment due to exclusion of rural migrants and informal workers. Reporting methodology changed for some variables around 2015 (PPP revision). |
| Granularity  | 55    | MEDIUM  | National-level, annual frequency. Adequate for national time series. Insufficient for provincial panel or city-level DID required by the causal DAGs. The analysis question requires subnational variation that this dataset cannot provide. |
| **Overall**  | **75**| **MEDIUM** | Adequate for national aggregate trend analysis |

**Conclusion support:** This dataset supports identifying the direction and approximate magnitude of national-level relationships between digital economy indicators and employment structure. It supports time series analysis (Granger causality, cointegration, structural breaks) but not panel regression or DID. Cannot support claims about subnational heterogeneity or causal identification via policy quasi-experiments.

**Statistics:**
- GDP per capita: $969--$12,971 (2000--2023), consistent upward trend
- Employment agriculture: 50.0%-->22.8%, employment services: 25.3%-->45.8% (expected structural transformation)
- Internet users: 1.8%-->90.6%, broadband: 0.002-->44.7 per 100 (rapid digitalization)
- Missing: `secondary_enrollment_gross` has only 11/24 observations (available from ~2013)
- Missing: `rd_expenditure_pct_gdp` missing year 2000 only (1 year)

---

### Dataset: ilo_china_employment_structure

**Source:** ILO modeled estimates via World Bank, CC-BY 4.0
**Status:** Acquired
**Shape:** 24 rows x 10 columns (2000--2023, annual)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 35    | LOW     | 28.75% overall missing rate. Three critical skill-composition columns (`labor_force_advanced_education_pct`, `labor_force_basic_education_pct`, `labor_force_intermediate_education_pct`) each have only 1/24 non-null values (95.83% missing). The remaining 6 employment-form variables are fully complete. |
| Consistency  | 80    | HIGH    | No duplicates. Employment-form variables (self-employed, wage-salaried, vulnerable, contributing family) are internally consistent: self_employed + wage_salaried approximately equals 100%. Trends are monotonic and plausible: wage-salaried rising from 48% to 62%, self-employed declining from 52% to 38%. |
| Bias         | 60    | MEDIUM  | ILO modeled estimates, not direct survey data. Models extrapolate from periodic labor force surveys. The single data point for education-based skill composition (year 2000: advanced=73.4%, basic=79.4%, intermediate=70.8%) appears to be labor force participation rates within each education group, not shares of the total labor force -- semantically different from what the DAG requires (skill shares). Youth unemployment (6.8--15.6%) is higher than overall unemployment (3.3--5.0%), consistent with known patterns. |
| Granularity  | 55    | MEDIUM  | National-level, annual. Adequate for national time series of employment forms. Insufficient for subnational analysis. The education-based columns, even if complete, would not provide the occupation-based skill decomposition that DAG 1 (SBTC) requires. |
| **Overall**  | **58**| **MEDIUM** | Employment-form variables (6 of 9) are usable at MEDIUM quality for national time series. Skill-composition variables are effectively unusable (LOW). |

**Conclusion support:** The employment-form variables (self-employed, wage-salaried, vulnerable employment, contributing family workers, female employment ratio, youth unemployment) support directional analysis of formal vs. informal employment trends. They CANNOT support quantitative claims about skill-level polarization or the magnitude of creation vs. substitution effects by skill group. The education-based skill variables are effectively missing and must not be used.

**Statistics:**
- Self-employed: 51.7%-->38.4% (declining trend, consistent with formalization)
- Wage/salaried: 48.3%-->61.6% (rising, mirrors self-employment decline)
- Vulnerable employment: 48.0%-->34.2% (declining, positive trend)
- Youth unemployment: 6.8%-->15.6% (peak during COVID era)
- Education columns: 1 observation each (year 2000 only) -- UNUSABLE for time series

---

### Dataset: smart_city_pilots_list

**Source:** MOHURD policy announcements, compiled from published DID studies
**Status:** Acquired
**Shape:** 286 rows x 4 columns

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 95    | HIGH    | Zero missing values. 286 prefecture-level cities with batch assignment and treatment year. Published studies cite ~290 cities; difference (4 cities) is due to intentional exclusion of district/county/town-level units for cleaner DID design. |
| Consistency  | 85    | HIGH    | Batch distribution plausible: batch 1 = 84 cities, batch 2 = 98, batch 3 = 104 (note: panel shows 285 unique cities, suggesting one city name may have been deduplicated during panel expansion -- minor discrepancy). Treatment years (2013, 2014, 2015) align with published literature conventions. All `is_pilot` values are 1 (as expected for a pilot list). |
| Bias         | 70    | MEDIUM  | Smart city pilot selection was not random -- cities were selected based on application quality, local government capacity, and existing infrastructure. This is a known limitation for DID analysis: treatment cities may systematically differ from control cities on unobservables. Published DID studies address this via propensity score matching and parallel trends tests. Additionally, the list was compiled from secondary sources (published papers, policy announcements), not from a single authoritative database. |
| Granularity  | 90    | HIGH    | City-level with batch assignment enables staggered DID design. This is exactly the granularity needed for the analysis, PROVIDED city-level outcome data is available. |
| **Overall**  | **85**| **HIGH** | Well-constructed treatment indicator, but useless without corresponding city-level outcome data |

**Conclusion support:** This dataset is a necessary but not sufficient input for DID analysis. It provides clean treatment assignment for 286 cities across 3 staggered batches. However, without city-level outcome variables (employment structure, digital economy index from EPS or PKU-DFIIC), it cannot produce any DID estimates. Its current analytical value is LIMITED TO describing the treatment structure and potentially being used in a data callback if city-level data becomes available.

---

### Dataset: smart_city_pilots_panel

**Source:** Derived from smart_city_pilots_list
**Status:** Acquired
**Shape:** 4,576 rows x 7 columns (286 cities x 16 years, 2008--2023)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 95    | HIGH    | Zero missing values. Balanced panel: 285 unique cities x 16 years = 4,560 expected (close to 4,576; the 16 extra rows likely from one duplicate city across batches). Treatment indicator correctly assigned: 1,736 pre-treatment observations (0), 2,840 post-treatment observations (1). |
| Consistency  | 82    | HIGH    | `treated` and `post` columns are identical, which is correct for a pilot-only panel (all cities are treated; `post` indicates post-treatment-year). Staggered treatment timing is correctly encoded. The "large jump" alert at index 16 is a false positive from the script -- it reflects the panel structure (city changes), not a data anomaly. |
| Bias         | 70    | MEDIUM  | Same selection bias concerns as the pilot list. Panel only contains treatment cities, not control cities. For DID, control cities would need to be constructed from non-pilot prefecture-level cities using a separate source. |
| Granularity  | 85    | HIGH    | City x year panel, exactly the structure needed for staggered DID. Missing only the outcome variables and control-city observations. |
| **Overall**  | **83**| **HIGH** | Structurally sound DID panel, but lacks outcome variables and control group |

**Conclusion support:** Same as smart_city_pilots_list -- structurally complete treatment panel, but cannot produce any analytical output without city-level outcome data.

---

### Dataset: digital_economy_composite_index

**Source:** Constructed from World Bank indicators (proxy for PKU-DFIIC)
**Status:** Proxy
**Shape:** 24 rows x 11 columns (2000--2023, annual)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 90    | HIGH    | 0.76% missing rate. Only `rd_expenditure_pct_gdp` and its normalized version missing 1/24 years each. All other components (internet users, mobile subscriptions, broadband) fully complete. |
| Consistency  | 78    | MEDIUM  | Normalized components correctly scaled to [0,1]. Composite index is simple equal-weight average -- no methodological anomalies. However, the index was constructed with only 4 components (internet, mobile, broadband, R&D) due to SSL fetch failures for high-tech exports and education expenditure. The original design called for 5--6 components. The missing components reduce the index's comprehensiveness. |
| Bias         | 45    | LOW     | **This is the critical weakness.** The index is a national-level proxy constructed from readily available World Bank indicators. It captures ICT infrastructure penetration and R&D intensity but MISSES key dimensions of China's digital economy: (1) e-commerce transaction volume, (2) digital financial inclusion (the PKU-DFIIC core metric), (3) platform economy scale, (4) software/IT services revenue. The actual PKU-DFIIC, which is the standard measure in Chinese digital economy research, covers 31 provinces and 2,800+ counties with validated sub-indices. This proxy has uncertain construct validity -- it may measure "ICT infrastructure maturity" rather than "digital economy development level." Equal weighting is arbitrary; the PKU-DFIIC uses principal component weights. |
| Granularity  | 40    | LOW     | National-level only. The analysis requires at minimum provincial-level (for panel regression) and ideally city-level (for DID) digital economy measures. This proxy cannot be disaggregated. It captures national trends but cannot identify cross-sectional variation. |
| **Overall**  | **63**| **MEDIUM** | Usable as a national trend indicator with substantial caveats about construct validity and granularity |

**Conclusion support:** This dataset supports ONLY identifying the national temporal trend in digital economy development. It can be used as a time-series independent variable in national aggregate regressions. It CANNOT support claims about the differential impact of digital economy development across regions, cities, or time periods. Any coefficient estimated using this index must be interpreted as "association with ICT infrastructure penetration and R&D spending" rather than "effect of digital economy development." Downstream phases must note the construct validity gap explicitly.

---

### Dataset: china_provincial_framework

**Source:** Analysis framework (empty shell)
**Status:** Proxy
**Shape:** 403 rows x 2 columns (31 provinces x 13 years, 2011--2023)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 0     | LOW     | The framework contains ONLY province names and years. No data variables whatsoever. It is a scaffold awaiting population from EPS or NBS Statistical Yearbook data. |
| Consistency  | N/A   | N/A     | No data to assess. |
| Bias         | N/A   | N/A     | No data to assess. |
| Granularity  | N/A   | N/A     | Provincial x annual structure is correct, but there is no data in it. |
| **Overall**  | **0** | **LOW** | Empty framework with no analytical value in current state |

**Conclusion support:** This dataset provides zero analytical value. It exists solely to document the data gap and provide a structure for future population if EPS access is obtained. It must NOT be treated as a dataset in any downstream phase.

---

### Dataset: china_national_panel_merged

**Source:** Merged from World Bank + ILO + digital economy composite index
**Status:** Acquired
**Shape:** 24 rows x 40 columns (2000--2023, annual)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 72    | MEDIUM  | 8.75% overall missing rate (84/960 cells). Missing value distribution is concentrated: `secondary_enrollment_gross` (13/24, 54%), three ILO education columns (23/24 each, 96%), `rd_expenditure_pct_gdp` and its normalized version (1/24 each, 4%). If the 3 effectively-empty education columns are excluded, the remaining 37 columns have a missing rate of only 1.7%. |
| Consistency  | 85    | HIGH    | Cross-source consistency verified: World Bank and ILO data share the same temporal index (2000--2023). Variables that appear in both sources (internet users, mobile subscriptions, broadband, R&D expenditure) have identical values in the merged panel and the component datasets. `domestic_credit_private_pct_gdp` exceeds 100% -- expected for China. No duplicate rows. |
| Bias         | 60    | MEDIUM  | Inherits all bias concerns from component datasets. ILO modeled estimates, WB reporting methodology changes, construct validity concerns for the composite digital economy index. The merged panel amplifies the illusion of comprehensiveness -- 40 columns suggest rich data, but 3 of those columns are effectively empty and the digital economy index is a crude proxy. |
| Granularity  | 55    | MEDIUM  | National-level, annual. This is the primary analysis-ready dataset, but its granularity limits the analysis to national time series methods only. The 24-year panel is short for time series econometrics (degrees of freedom concerns with many controls). |
| **Overall**  | **68**| **MEDIUM** | Serviceable for national time series analysis with explicit caveats |

**Conclusion support:** This is the primary working dataset for the analysis. It supports time series analysis (Granger causality, cointegration, VAR/VECM, structural break tests) of the digital economy--employment structure relationship at the national level. With 24 observations and 37 usable variables, the analysis must be parsimonious in model specification -- no more than 4--5 variables simultaneously without risking overfitting. It CANNOT support panel methods, DID, or any analysis requiring cross-sectional variation.

**Statistics:**
- 37 usable columns (excluding 3 education columns with 96% missing)
- Usable missing rate: ~1.7% (concentrated in secondary enrollment and one year of R&D)
- Temporal overlap: all component datasets cover 2000--2023 (full alignment)

---

### Dataset: nbs_provincial_availability (Availability Assessment)

**Source:** NBS Statistical Yearbook acquisition attempt (stats.gov.cn)
**Status:** Attempted but not acquired (automated extraction blocked)
**Shape:** 403 rows x 8 columns (31 provinces x 13 years, 2011--2023) -- availability mapping only, no actual data

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 0     | LOW     | Framework only. No actual variable values acquired. Documents which variables are available in the NBS yearbook. |
| Consistency  | N/A   | N/A     | No data to assess. |
| Bias         | N/A   | N/A     | No data to assess. |
| Granularity  | N/A   | N/A     | Provincial x annual structure is correct, awaiting population. |
| **Overall**  | **0** | **LOW** | Availability assessment only -- confirms data EXISTS at NBS but was not extractable via automated methods |

**Acquisition attempt details (2026-03-29):**

1. **NBS official API (data.stats.gov.cn):** Attempted 3 indicator codes (A0301 employment by sector, A0201 regional GDP, A0501 population). All returned HTTP 404. The API endpoint appears to have been restructured; current API requires session-based authentication and anti-bot handling.

2. **NBS Yearbook HTML tables (stats.gov.cn/sj/ndsj/2024/):** The yearbook index page IS accessible (HTTP 200). Individual data tables are published as HTML pages with JavaScript rendering requirements. Manual extraction or browser-based scraping would be feasible but exceeds automated acquisition capabilities.

3. **Direct CSV downloads:** NBS data portal is reachable but does not provide bulk CSV downloads for provincial panel data.

**Key finding:** The NBS Statistical Yearbook **does contain** the required provincial data:
- Provincial GDP (31 provinces, annual, available 2000--2023)
- Employment by sector (primary/secondary/tertiary) by province
- Population by province and age group
- Internet users by province (partial years)
- Education expenditure by province

**Recommendation:** A data callback with manual yearbook extraction (using browser-based tools or the `data_extractor.py` pipeline) or institutional EPS access could populate the provincial framework. If successful, this would upgrade the analysis from national time series (T=24) to provincial panel (31 provinces x 13 years = 403 observations), a qualitative improvement enabling panel fixed-effects estimation and potentially city-level DID.

---

### Failed Datasets (Not Assessed -- No Data Available)

| Dataset | Failure Reason | Impact on Analysis |
|---------|---------------|-------------------|
| **NBS provincial panel** | NBS API returned 404; yearbook tables require JavaScript rendering / manual extraction | Provincial data EXISTS but automated acquisition failed. Data callback recommended. If acquired: 31 provinces x 13 years enables panel methods. |
| **CFPS microdata** | Requires registration at opendata.pku.edu.cn | Cannot test individual-level mechanisms (skill transitions, formal/informal flows, hukou effects). DAG 2 and DAG 3 mechanism testing severely limited. |
| **EPS provincial panel** | Commercial database (institutional subscription required) | Cannot conduct provincial panel regression or city-level DID with outcome variables. Analysis limited to national time series. |
| **FRED supplementary** | No API key set | Minimal impact -- World Bank data provides adequate coverage for the required variables. |

---

## Cross-Dataset Assessment

### DAG Coverage

| DAG Edge | Supporting Dataset(s) | Quality | Can Test? |
|----------|----------------------|---------|-----------|
| SCP --> DE (Smart city pilot --> Digital economy) | smart_city_pilots_panel + **NO city-level DE measure** | Treatment: HIGH, Outcome: MISSING | NO -- treatment exists but no city-level outcome |
| DE --> SUB (Digital economy --> Substitution) | merged national panel (DE index + employment by sector) | MEDIUM | PARTIAL -- national aggregate only, no task-level or occupation-level data |
| DE --> CRE (Digital economy --> Creation) | merged national panel (DE index + services employment, ICT proxy) | MEDIUM | PARTIAL -- can observe sectoral shift, cannot identify specific new job categories |
| SUB --> MID_DECLINE | merged national panel (employment_industry_pct) | MEDIUM | WEAK -- industry employment share is a crude proxy for mid-skill decline; no skill-level data |
| CRE --> HIGH_GROW | merged national panel (services employment, tertiary enrollment) | MEDIUM | WEAK -- tertiary enrollment is an input proxy, not an output measure of high-skill job growth |
| DE --> HC_INV (DAG 2 mediation) | merged national panel (tertiary_enrollment_gross, secondary_enrollment_gross) | MEDIUM | PARTIAL -- education enrollment available; training participation missing (CFPS required) |
| DE --> IND_UP (DAG 2 mediation) | merged national panel (services_value_added_pct_gdp) | HIGH | YES -- services share of GDP is a clean measure of industrial upgrading |
| HC_INV --> SKILL_UP | **MISSING** (ILO education columns unusable, CFPS unavailable) | LOW | NO -- no skill-level employment data |
| DE --> FORMAL/INFORMAL (DAG 3) | merged national panel (self_employed_pct, wage_salaried_workers_pct, vulnerable_employment_pct) | MEDIUM | PARTIAL -- can distinguish broad formal/informal trends, cannot disaggregate by industry or match to digital exposure |
| FORMAL --> AUTO (DAG 3) | merged national panel (employment_industry_pct as proxy) | MEDIUM | WEAK -- manufacturing employment share is a very crude proxy for automation |
| HUKOU moderator (DAG 3) | **MISSING** (CFPS required) | LOW | NO |
| SOE moderator (DAG 3) | **MISSING** (EPS required) | LOW | NO |

### Temporal Alignment

All acquired datasets share the 2000--2023 temporal window with annual frequency. There are no temporal misalignment issues. The smart city panel covers 2008--2023 (treatment begins 2013), which is adequate for pre-treatment trends testing if outcome data becomes available.

Key concern: 24 observations is a short time series. With seasonal adjustment not applicable (annual data) and the need for multiple control variables, effective degrees of freedom in multivariate regressions will be low (approximately 15--18 after controls and lags).

### Granularity Alignment

All acquired datasets are at the national level (except the smart city panel, which is city-level but lacks outcome variables). There is no granularity mismatch within the usable portfolio, but there is a fundamental mismatch between the analysis requirements (city-level DID, individual-level mechanisms) and data availability (national aggregate only).

---

## Warnings for Downstream Agents

**CRITICAL (must appear in every subsequent artifact):**

1. **The DID design specified in the research question is NOT executable with current data.** The smart city pilot treatment indicator exists but has no corresponding city-level outcome variables. All causal claims must use weaker identification strategies (time series methods, Granger causality, structural break analysis). Any reference to "DID results" must note that DID was planned but could not be executed.

2. **Skill-level analysis is not possible.** The ILO education-based labor force breakdown has only 1 observation. CFPS microdata was not acquired. The SBTC / skill-polarization hypothesis (DAG 1 core prediction) can only be tested using sectoral employment shares as a crude proxy, not actual skill-level data. EP.truth for the SUB --> MID_DECLINE and CRE --> HIGH_GROW edges is capped at 0.30.

3. **The digital economy composite index is a proxy of uncertain validity.** It measures ICT infrastructure penetration, not the broader digital economy construct. Any coefficient must be interpreted accordingly. The PKU-DFIIC would be strongly preferred.

**IMPORTANT (must be noted in methodology sections):**

4. The merged national panel has only 24 observations. Multivariate models must be parsimonious (maximum 4--5 regressors simultaneously). Asymptotic test statistics may not be reliable at this sample size.

5. DAG 3 (labor market segmentation) can only be tested at a very aggregate level using self-employment vs. wage-salaried worker proportions. Sector-specific and hukou-based heterogeneity analysis requires CFPS data.

6. China's official unemployment rate understates true unemployment. The ILO-modeled estimates partially correct for this but remain model-dependent.

7. The `secondary_enrollment_gross` variable is missing for 2000--2012. Any analysis using this variable is limited to the 2013--2023 window (11 observations).

---

## Open Issues

1. **Data callback recommendation (UPDATED after NBS acquisition attempt):** Automated NBS acquisition was attempted on 2026-03-29 and partially failed (API returned 404; yearbook website is accessible but tables require JavaScript rendering). If Phase 1 determines that national time series is insufficient, a data callback should prioritize:
   - **NBS yearbook manual extraction** (HIGHEST PRIORITY): The yearbook website IS accessible. Browser-based or manual extraction of provincial GDP, employment by sector, and population tables would enable panel methods (31 x 13 = 403 obs vs. current T=24). Script `phase0_discovery/scripts/acquire_nbs_provincial.py` documents the attempt and availability assessment.
   - PKU-DFIIC registration and download (free for academic use after approval)
   - CFPS registration and download (free for academic use after approval)

2. **Construct validity of digital economy index:** Phase 2 EDA should assess whether the composite index correlates strongly with known digital economy milestones (Internet Plus strategy 2015, COVID digital acceleration 2020). If it does not, the index may not capture the intended construct.

3. **ILO skill-composition data:** The 3 education-based columns should be dropped from the analysis-ready dataset to avoid accidental use. They provide no time series information.

4. **Smart city panel completeness:** The panel shows 285 unique cities vs. 286 in the list -- investigate whether one city was lost during panel expansion (minor issue).

5. **Sample size for time series methods:** 24 annual observations supports simple bivariate Granger tests and possibly trivariate VAR(1) models. More complex specifications will have insufficient degrees of freedom. Phase 1 strategy must account for this constraint.

---

## Code Reference

- Assessment script: `phase0_discovery/scripts/assess_data_quality.py`
- Data acquisition script: `phase0_discovery/scripts/acquire_data.py`
- Data verification script: `phase0_discovery/scripts/verify_data.py`
- Registry: `data/registry.yaml`
