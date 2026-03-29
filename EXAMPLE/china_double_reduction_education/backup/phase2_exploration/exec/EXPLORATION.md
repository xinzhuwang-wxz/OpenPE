# Data Exploration: china_double_reduction_education

**Analysis:** china_double_reduction_education
**Question:** Did China's Double Reduction policy truly reduce household education expenditure?
**Generated:** 2026-03-29
**Agent:** data-explorer (Phase 2)

---

## 1. Data Cleaning Log

All 12 acquired datasets were loaded and verified against the Phase 0 registry. No modifications to raw data were performed. All datasets were stored in Parquet format during Phase 0 acquisition with explicit missing values preserved (never zero-filled). The table below summarizes the cleaning status.

| Dataset | ID | Original Rows | Final Rows | Missing Treatment | Outlier Treatment | Notes |
|---|---|---|---|---|---|---|
| NBS Education Expenditure | ds_001 | 10 | 10 | 0 missing | None needed | 2016-2018 flagged as back-calculated |
| CIEFR-HS Spending Composition | ds_002 | 3 | 3 | 0 missing | None needed | Summary statistics only |
| World Bank Education Indicators | ds_003 | 15 | 15 | 38.1% missing | Retained as-is | GDP per capita complete; education indicators sparse |
| Tutoring Industry Collapse | ds_004 | 19 | 19 | 0 missing | None needed | Mixed metrics; not time-aligned |
| Policy Timeline | ds_005 | 8 | 8 | 0 missing | N/A | Event data |
| China Demographics | ds_006 | 9 | 9 | 6.7% missing | Retained as-is | Enrollment missing for 2016-2017 and 2024 |
| Public Education Expenditure | ds_007 | 8 | 8 | 0 missing | None needed | Ends at 2023 |
| NBS Consumption Categories | ds_008 | 7 | 7 | 0 missing | None needed | 2019-2025 only |
| NBS Disposable Income | ds_009 | 10 | 10 | 0 missing | None needed | Complete 2016-2025 |
| Underground Tutoring Prices | ds_011 | 14 | 14 | 0 missing | None needed | Anecdotal data |
| NBS CPI Deflator | ds_013 | 10 | 10 | 0 missing | None needed | Complete 2016-2025 |
| Tutoring Company Financials | (sub) | 9 | 9 | 0 missing | None needed | Fiscal year misalignment noted |

**Key cleaning decisions:**

1. **No imputation performed.** With only 10 annual observations for the primary series, imputation would introduce more noise than it resolves. Missing enrollment data (2016-2017, 2024) is retained as NaN.
2. **Back-calculated data flagged.** NBS education expenditure for 2016-2018 was back-calculated from YoY growth rates during Phase 0 acquisition. These values carry approximately +/- 2-3% error. They are included in the analysis but flagged in the `data_source` column.
3. **No outlier removal.** The 2020 COVID dip (-19.1% national) and 2021 rebound (+27.9%) are extreme values but are genuine pandemic effects, not measurement errors. They are retained and explicitly modeled.
4. **Temporal alignment verified.** All NBS series (expenditure, income, CPI) share the same 2016-2025 annual index. The consumption categories dataset begins in 2019. Demographics begins in 2016 but ends in 2024. Public education expenditure ends in 2023.

---

## 2. Feature Engineering

| Feature | Formula / Logic | Source Variables | Purpose |
|---|---|---|---|
| `real_national` | `education_culture_recreation_national_yuan * deflator_education` | ds_001, ds_013 | CPI-deflated real education spending (2015 yuan) |
| `real_urban` | `education_culture_recreation_urban_yuan * deflator_education` | ds_001, ds_013 | Real urban education spending |
| `real_rural` | `education_culture_recreation_rural_yuan * deflator_education` | ds_001, ds_013 | Real rural education spending |
| `edu_share_income_national` | `(edu_culture_rec / disposable_income) * 100` | ds_001, ds_009 | Education spending as share of income |
| `edu_share_income_urban` | `(edu_urban / income_urban) * 100` | ds_001, ds_009 | Urban education-to-income ratio |
| `edu_share_income_rural` | `(edu_rural / income_rural) * 100` | ds_001, ds_009 | Rural education-to-income ratio |
| `spending_per_birth` | `real_national / births_millions` | ds_001, ds_006, ds_013 | Per-child spending intensity proxy |
| `spending_per_enrollment` | `real_national / enrollment_millions` | ds_001, ds_006, ds_013 | Per-enrolled-student spending intensity |
| `urban_rural_gap` | `real_urban - real_rural` | derived | Urban-rural spending differential |
| `indexed_urban_2019` | `(real_urban / real_urban_2019) * 100` | derived | Urban spending index (2019=100) |
| `indexed_rural_2019` | `(real_rural / real_rural_2019) * 100` | derived | Rural spending index (2019=100) |

**Validation of engineered features:**

- All real values are positive (no division by zero or negative deflators).
- `spending_per_birth` is computable for 2016-2024 (births available for 9 years); the ratio increases over time due to declining births, which is the expected demographic effect.
- `spending_per_enrollment` is computable only for 2018-2023 (enrollment data missing for 2016-2017 and 2024).
- No NaN or Inf values were introduced by any computation.

---

## 3. Exploratory Analysis

### 3.1 Real Education Expenditure Time Series (2016-2025)

![CPI-deflated real per capita education/culture/recreation expenditure by area. National (blue), urban (red), rural (green). Vertical dashed line marks July 2021 Double Reduction policy. Orange band highlights COVID disruption period (2020-2021). Urban spending shows the deepest COVID dip and strongest recovery, with 2022 dip potentially reflecting policy effects. Rural spending shows steadier growth with less COVID disruption.](../figures/fig01_real_education_expenditure_timeseries.pdf){#fig:real-edu-ts}

**Key observations:**

- **No sustained decline post-policy.** Real national spending dipped in 2020 (COVID) and again mildly in 2022 (-5.0% nominal YoY), but by 2023-2025 it exceeds all pre-policy levels.
- **The 2022 dip is the candidate policy signal.** Nominal growth turned negative (-5.0%) in 2022, the first full calendar year under the policy. However, 2022 was also a year of severe COVID lockdowns (Shanghai lockdown, zero-COVID policy), making causal separation difficult.
- **Urban spending more volatile than rural.** Urban real spending fell from 3,130 (2019 real yuan) to 2,377 (2020) and recovered to 2,977 (2021), then dipped to 2,704 (2022) before resuming growth. Rural spending shows less disruption.
- **CPI deflation reduces apparent growth slightly.** Cumulative education CPI inflation of 16.8% over 2016-2025 means nominal growth overstates real growth. The difference is modest (1.5pp vs overall CPI) but directionally important.

### 3.2 Nominal vs Real Comparison

![Side-by-side comparison of nominal (left) and CPI-deflated real (right) per capita education/culture/recreation expenditure. The real series shows slightly flatter post-policy growth, but the qualitative pattern is identical: COVID dip, recovery, mild 2022 dip, resumed growth.](../figures/fig02_nominal_vs_real_expenditure.pdf){#fig:nominal-vs-real}

The difference between nominal and real trajectories is modest. CPI deflation does not change the qualitative conclusion: spending has grown in both nominal and real terms, with the 2022 dip as the only candidate policy effect.

### 3.3 Education Share of Consumption and Income

![Education/culture/recreation as share of total consumption (left) and disposable income (right). The consumption share dropped from 11.7% (2019) to 9.6% (2020, COVID) and has gradually recovered to 11.8% (2025). The income share follows a similar pattern, indicating the spending ratio is relatively stable over time.](../figures/fig03_education_share_consumption_income.pdf){#fig:edu-shares}

**Key observations:**

- **Education's consumption share recovered to pre-COVID levels by 2025.** The 2020 drop to 9.6% was COVID-driven, not policy-driven. The gradual recovery from 10.8% (2021) through 11.8% (2025) shows no permanent downward shift.
- **Urban share consistently higher than rural.** Urban households allocate 10-12% vs rural 9.5-11.5% of consumption to this category, consistent with higher urban tutoring participation.
- **Income share is slightly declining long-term.** The ratio of education spending to income has been roughly flat (~7-8%), suggesting spending grows in line with income, not faster or slower.

### 3.4 Eight-Category Consumption Composition

![Stacked area chart showing shares of total consumption across 8 NBS categories (2019-2025). Education/culture/recreation (yellow) occupies a relatively stable 10-12% band. Food/tobacco/liquor (red) dominates at 28-30%. The most notable compositional shift is the COVID-driven decline in transport/telecom (2020) and its subsequent recovery.](../figures/fig04_consumption_composition_stacked.pdf){#fig:composition-stacked}

![Line chart of consumption category shares. Education/culture/recreation (highlighted in bold) dipped in 2020 and recovered. Its trajectory is unremarkable compared to other categories -- no unique structural break.](../figures/fig05_consumption_shares_lines.pdf){#fig:composition-lines}

**Key observations:**

- **Education's share does not behave differently from other categories post-2021.** The 2020 dip and 2021-2025 recovery pattern is shared by multiple categories.
- **The largest compositional shifts are in food (rising from 28.2% to 30.5%) and transport/telecom (declining from 13.3% to 13.0% then recovering to 14.6%).** Education's movements are within the normal range of category fluctuations.
- **No evidence of a compositional structural break at 2021** in the education category specifically.

### 3.5 Per-Child Normalized Spending

![Panel (a): Annual births (declining from 17.9M in 2016 to 9.0M in 2024) and compulsory education enrollment (stable at ~157-161M where available). Panel (b): Per-birth spending intensity (real spending divided by births in millions) shows strong upward trend driven by demographic decline -- fewer children means higher per-capita education spending intensity even if per-household spending is flat.](../figures/fig06_per_child_spending.pdf){#fig:per-child}

**Key observations:**

- **Per-child spending intensity is rising sharply** due to the 47% decline in births (17.9M to 9.0M). This confounds any per-capita analysis: even if aggregate education spending were flat, per-child spending would appear to rise.
- **Enrollment-normalized spending** (where available, 2018-2023) shows a different picture because enrollment is more stable than births (~157-161M in compulsory education). This is the more relevant denominator for current education burden.
- **The demographic decline is a critical confounder.** Any reduction in aggregate education spending could be partially or wholly attributable to fewer children entering the education system, not to the policy reducing per-child costs.

### 3.6 Tutoring Industry Collapse

![Panel (a): Revenue of New Oriental and TAL Education (billion USD). Both companies show sharp revenue declines in FY2022 (New Oriental: $4.3B to $2.0B, TAL: $4.5B to $1.5B), with partial recovery for New Oriental but not TAL. Panel (b): Tutoring center closures and other industry metrics showing 92-96% offline center closure rates.](../figures/fig07_tutoring_industry_collapse.pdf){#fig:tutoring-collapse}

**Key observations:**

- **The supply-side collapse is unambiguous.** 92-96% of offline tutoring centers closed. Major company revenues fell 50-70%. This is the strongest evidence for DAG 1's first link (Policy -> Industry Collapse).
- **New Oriental pivoted and partially recovered**, suggesting firm-level adaptation rather than total industry destruction.
- **The supply-side evidence does not tell us about demand-side effects.** Center closures and revenue losses are consistent with both DAG 1 (demand reduced) and DAG 2 (demand shifted underground).

### 3.7 CIEFR-HS Pre-Policy Spending Decomposition

![Horizontal bar chart showing the pre-policy (2019) decomposition of household education spending: in-school expenses 73%, extracurricular/tutoring 12%, other education expenses 15%. This is the key structural parameter for DAG 3 -- the policy targeted a component representing only ~12% of total education spending.](../figures/fig08_ciefr_spending_decomposition.pdf){#fig:ciefr-decomp}

**Key observation:**

- **The 73/12/15 split is the most important structural finding for this analysis.** Even if the Double Reduction policy achieved 100% elimination of tutoring spending with zero substitution, the maximum possible reduction in total household education expenditure would be approximately 12%. Under realistic assumptions of partial substitution to underground tutoring, non-academic enrichment, and in-school fee increases, the expected effect on total spending is 3-8%.

### 3.8 YoY Growth Rates

![Bar chart of year-over-year nominal growth rates for national education/culture/recreation spending. Pre-policy: steady 10-13% growth (2016-2019). COVID: -19.1% (2020). Recovery: +27.9% (2021). Post-policy: -5.0% (2022), +17.6% (2023), +9.8% (2024), +9.4% (2025). The 2022 dip is the only negative non-COVID year.](../figures/fig12_yoy_growth_rates.pdf){#fig:yoy-growth}

**Key observations:**

- **2022 is the candidate policy-effect year** with -5.0% nominal growth. This is the first full year under the policy. However, 2022 also saw the most restrictive COVID lockdowns (Shanghai, zero-COVID peak).
- **By 2023-2025, growth resumes at 10-18%.** If the policy had a permanent level effect, we would expect growth to resume at the pre-policy rate (~11%) from a lower base. The 2023 jump of 17.6% is partly catch-up from the depressed 2022 base.
- **Pre-policy growth was 10-13% per year (nominal).** Post-2022 growth rates (9.4-9.8%) are slightly below the pre-policy average, which could indicate a modest permanent effect or simply economic slowdown in the broader economy.

### 3.9 COVID Confounding Analysis

The temporal overlap between the pandemic and the policy is severe:

| Year | Event | Nominal growth |
|---|---|---|
| 2020 | COVID-19 pandemic | -19.1% |
| 2021 | COVID recovery + Double Reduction (July) | +27.9% |
| 2022 | Zero-COVID peak + first full year under policy | -5.0% |
| 2023 | COVID exit + policy enforcement continues | +17.6% |

The 2022 decline cannot be cleanly attributed to the Double Reduction policy because: (a) Shanghai lockdown and zero-COVID enforcement suppressed all consumer spending in 2022, (b) the 8-category composition analysis shows no unique behavior for education relative to other categories, and (c) the 2023 rebound (+17.6%) is consistent with COVID catch-up rather than a policy reversal. This remains the most important confounding problem for Phase 3.

### 3.10 Urban-Rural Divergence

![Panel (a): Urban and rural real spending indexed to 2019=100. Urban fell to 76 (2020) and rural to 88 (2020), then both recovered, but urban shows a post-policy dip in 2022 that rural does not. Panel (b): The urban-rural gap in absolute 2015 yuan shows the gap widening post-policy.](../figures/fig10_urban_rural_divergence.pdf){#fig:urban-rural-div}

**Key observations:**

- **Urban spending was more affected than rural** in both the COVID dip and the 2022 post-policy dip. This is consistent with the CIEFR-HS finding that urban tutoring participation (~47%) was much higher than rural (~18%).
- **The urban-rural gap widened post-2021**, which is the opposite of what DAG 1 would predict (if the policy reduced the urban tutoring premium, the gap should narrow). However, this may reflect faster urban recovery from COVID or other economic factors.

### 3.11 Pre-Trend Parallel Trends Check

![Pre-policy trends (2016-2020) for urban and rural real spending indexed to 2016=100. Both follow roughly similar trajectories through 2018, then diverge in 2019 (rural grows faster) and sharply diverge in 2020 (urban crashes more). Pre-policy CAGR: urban -0.31%, rural +3.36%.](../figures/fig14_parallel_trends_precheck.pdf){#fig:parallel-trends}

**Key finding: Parallel trends assumption is violated.**

- Urban and rural pre-policy growth rates diverge substantially: urban CAGR of -0.31% vs rural CAGR of +3.36% over 2016-2020.
- The COVID year (2020) creates additional divergence as urban spending is more severely affected.
- **This means the urban-rural comparison cannot be used as a quasi-DiD design.** The Phase 1 strategy already anticipated this possibility and designated it as a "descriptive stratified ITS with formal comparison" rather than a true DiD. The parallel trends violation confirms this was the correct framing.

### 3.12 Public vs Household Education Spending

![Dual-axis plot showing public education spending as % of GDP (left axis, blue) and household education/culture/recreation as % of consumption (right axis, red). Both are relatively stable, with public spending maintained at 4.0-4.2% of GDP and household share at 10-12%.](../figures/fig11_public_vs_household_spending.pdf){#fig:public-household}

**Key observation:**

- Public education spending has been maintained above the 4% of GDP target. There is no evidence of public spending decline that could confound household spending trends. The crowding-in hypothesis (DAG 3) -- that increased public spending crowds in rather than crowds out household spending -- is consistent with the data but cannot be directly tested with aggregate data.

### 3.13 Correlation Structure

![Correlation heatmap of key variables. Real education spending (all areas) is strongly positively correlated with income (r=0.94-0.97) and negatively correlated with births (r=-0.86 to -0.93). The CPI deflator is negatively correlated with spending (r=-0.91 to -0.97), which is mechanical (deflator decreases over time as prices rise).](../figures/fig13_correlation_heatmap.pdf){#fig:corr-heatmap}

**Key finding:**

- **Income and education spending are near-perfectly correlated (r > 0.94).** This means income is the dominant covariate and must be controlled in any causal analysis. It also means the policy effect (if any) operates within the residual variance after income is accounted for.
- **Births and spending are strongly negatively correlated (r = -0.86 to -0.93).** This reflects the demographic decline confound: as births fall, per-capita spending rises mechanically.

### 3.14 Stationarity and Autocorrelation Tests

**ADF Tests (Augmented Dickey-Fuller):**

| Series | Test Statistic | p-value | Verdict |
|---|---|---|---|
| Real national (levels) | 0.4432 | 0.9830 | NON-stationary (unit root not rejected) |
| Real urban (levels) | -1.1964 | 0.6751 | NON-stationary |
| Real rural (levels) | 1.0356 | 0.9946 | NON-stationary |
| Real national (first differences) | -5.0943 | 0.0000 | Stationary |

**KPSS Test:**

| Series | Test Statistic | p-value | Verdict |
|---|---|---|---|
| Real national (levels) | 0.1288 | 0.0819 | Marginal (borderline at 10% level) |

**Interpretation:**

- The levels series are I(1) -- integrated of order 1, with a unit root. First differencing produces stationarity. This is consistent with a trending time series (education spending grows over time with income).
- For the ITS analysis in Phase 3, this means: (a) working with levels requires trend terms in the regression to avoid spurious regression, and (b) the 3-parameter ITS specification (intercept, pre-trend, level-shift) from the strategy is appropriate for this data structure.
- With only 10 observations, ADF and KPSS tests have very low power. The results should be interpreted with extreme caution.

**ACF/PACF plots** (@fig:acf-pacf) show strong persistence in levels (ACF decays slowly) and no significant autocorrelation in first differences, consistent with the I(1) characterization.

![ACF and PACF plots for real national education spending in levels (top) and first differences (bottom). Levels show strong persistence. First differences show no significant autocorrelation, consistent with I(1) process.](../figures/fig09_acf_pacf_stationarity.pdf){#fig:acf-pacf}

---

## 4. Variable Ranking

### Variable Ranking by EP Contribution

| Rank | Variable | DAG Role | Type | Quality | Association with Outcome | EP Relevance | Include? | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `real_national` / `real_urban` / `real_rural` | Outcome | Numerical | MEDIUM | N/A (is outcome) | Primary outcome | Yes | Proxy for education spending |
| 2 | `national_yuan` (income) | Confounder | Numerical | HIGH | r = 0.97 | Must control | Yes | Near-perfect correlation with spending |
| 3 | `births_millions` | Confounder | Numerical | MEDIUM | r = -0.93 | Must control | Yes | Demographic decline confound |
| 4 | Policy indicator (2021+) | Treatment | Binary | HIGH | N/A | Primary treatment | Yes | Constructed from policy timeline |
| 5 | `education_share_national_pct` | Outcome (alt) | Numerical | MEDIUM | Derived from outcome | Compositional analysis | Yes | Tests whether share changed |
| 6 | `deflator_education` | Adjustment | Numerical | MEDIUM | Mechanical | CPI deflation | Yes | Required for all real values |
| 7 | 8-category composition | Context | Numerical | MEDIUM | Moderate | Compositional test | Yes | Tests whether education uniquely shifted |
| 8 | CIEFR 73/12/15 decomposition | Structural parameter | Numerical | MEDIUM | High (theoretical) | DAG 3 key parameter | Yes | Pre-policy only |
| 9 | Tutoring company revenues | Supply-side evidence | Numerical | MEDIUM | Indirect | DAG 1 first link | Yes | Industry collapse evidence |
| 10 | `compulsory_education_enrollment` | Normalization | Numerical | MEDIUM | r = -0.60 (partial) | Per-child normalization | Conditional | Missing 4 of 9 years |
| 11 | `pct_of_gdp` (public edu) | Context | Numerical | MEDIUM | Low | Crowding-in test | Conditional | Ends 2023 |
| 12 | Underground tutoring prices | Anecdotal | Mixed | LOW | Not quantifiable | DAG 2 evidence | Descriptive only | Selection bias |
| 13 | International comparison | Context | Numerical | LOW | Cross-sectional only | Benchmarking | No | Single snapshot (2019) |

**Red flags:**

- **Near-perfect multicollinearity** between income and education spending (r = 0.97). Including both in a regression will create instability. Strategy: use income as the sole covariate in BSTS; in ITS, use the spending series directly without income controls (trend captures income growth).
- **Near-zero variation in education consumption share** (std = 0.7 pp over range 9.6-11.8%). The signal-to-noise ratio for detecting compositional shifts is very low.
- **Enrollment data missing 4 of 9 years.** Per-enrollment-student analysis is restricted to 2018-2023.

---

## 5. Data Readiness Assessment

### Method Prerequisites

| Edge | Method | Data Ready? | Assumptions Pre-Check | Risk Level | Notes |
|---|---|---|---|---|---|
| Policy -> Total Spending (DAG 1) | ITS (3-param) | Yes | Levels are I(1); trend term required | MEDIUM | COVID confounding severe |
| Policy -> Total Spending (DAG 1) | BSTS | Marginal | Only 5 pre-policy obs (4 if 2020 excluded) | HIGH | BSTS feasibility depends on pre-treatment fit |
| Urban vs Rural comparison | Descriptive stratified ITS | Yes | **Parallel trends VIOLATED** | HIGH | Cannot upgrade to DiD |
| Policy -> Industry Collapse (all DAGs) | Descriptive | Yes | N/A | LOW | Well-documented in data |
| Tutoring share ceiling (DAG 3) | Structural parameter | Yes | Pre-policy CIEFR data only | MEDIUM | Cannot verify post-policy |
| Underground market (DAG 2) | Anecdotal | Marginal | N/A | HIGH | No systematic data |

### Readiness Summary

1. **ITS is feasible** with the 3-parameter specification (intercept, pre-trend, level-shift). The I(1) nature of the series confirms that a trend term is required. COVID can be handled via 2020 exclusion (primary) or indicator variable (sensitivity).

2. **BSTS feasibility is marginal.** With only 4-5 pre-treatment observations, BSTS can support at most 1 covariate (disposable income). If pre-treatment fit is poor, BSTS should be reported as infeasible rather than forced. This was anticipated in the Phase 1 strategy.

3. **Urban-rural DiD is not feasible.** Parallel trends are violated (urban CAGR -0.31% vs rural +3.36%). The comparison remains descriptive: separate ITS models with informal coefficient comparison, not a formal DiD test.

4. **COVID confounding remains the dominant threat.** The 2022 candidate policy effect cannot be cleanly separated from zero-COVID lockdown effects. The strategy's approach of using both 2020-exclusion and COVID-indicator specifications is the best available mitigation.

### Phase 0 Data Quality Warnings Carried Forward

All warnings from DATA_QUALITY.md remain binding:

1. **PRIMARY OUTCOME IS A PROXY.** NBS "education, culture and recreation" bundles non-education spending. Post-COVID culture/recreation recovery likely inflates the education trend. No post-policy decomposition data exists.
2. **NO POST-POLICY MICRODATA.** CFPS post-2021 and CIEFR-HS Wave 3 failed acquisition. Cannot test heterogeneous effects or verify compositional shifts at the household level.
3. **UNDERGROUND TUTORING DATA IS ANECDOTAL.** Cannot quantify underground market size or spending.
4. **COVID-19 CONFOUNDING IS SEVERE.** Temporally coincides with policy; larger in magnitude than expected policy effect.
5. **PRE-EXISTING DOWNWARD TREND.** CIEFR-HS shows per-student education spending was declining before the policy.
6. **DEMOGRAPHIC DECLINE AS CONFOUNDER.** Births fell 47% from 2016 to 2024.

### Method Pivots

**Urban-rural DiD downgraded to descriptive comparison.** The parallel trends violation (identified in Phase 1 as a contingency) is now confirmed by EDA. No formal DiD coefficient or p-value will be reported for the urban-rural comparison. Instead, separate ITS models will be run for each area with qualitative comparison of level-shift coefficients.

No other method pivots are required. The ITS and BSTS specifications remain as planned.

---

## 6. Figures Index

| Figure | File | Description |
|---|---|---|
| @fig:real-edu-ts | `fig01_real_education_expenditure_timeseries` | CPI-deflated real education spending time series (2016-2025) |
| @fig:nominal-vs-real | `fig02_nominal_vs_real_expenditure` | Nominal vs real spending comparison |
| @fig:edu-shares | `fig03_education_share_consumption_income` | Education share of consumption and income |
| @fig:composition-stacked | `fig04_consumption_composition_stacked` | 8-category consumption stacked area |
| @fig:composition-lines | `fig05_consumption_shares_lines` | 8-category consumption shares line chart |
| @fig:per-child | `fig06_per_child_spending` | Per-child normalized spending with demographics |
| @fig:tutoring-collapse | `fig07_tutoring_industry_collapse` | Tutoring industry collapse (revenues, closures) |
| @fig:ciefr-decomp | `fig08_ciefr_spending_decomposition` | CIEFR-HS 73/12/15 spending decomposition |
| @fig:acf-pacf | `fig09_acf_pacf_stationarity` | ACF/PACF stationarity diagnostics |
| @fig:urban-rural-div | `fig10_urban_rural_divergence` | Urban-rural spending divergence |
| @fig:public-household | `fig11_public_vs_household_spending` | Public vs household education spending |
| @fig:yoy-growth | `fig12_yoy_growth_rates` | Year-over-year nominal growth rates |
| @fig:corr-heatmap | `fig13_correlation_heatmap` | Correlation matrix of key variables |
| @fig:parallel-trends | `fig14_parallel_trends_precheck` | Pre-policy parallel trends check |

## 7. Summary Statistics

| Variable | Unit | N | Mean | Std | Min | Max |
|---|---|---|---|---|---|---|
| Real edu/culture/rec (national) | 2015 yuan | 10 | 2,281 | 389 | 1,796 | 2,986 |
| Real edu/culture/rec (urban) | 2015 yuan | 10 | 2,914 | 423 | 2,376 | 3,679 |
| Real edu/culture/rec (rural) | 2015 yuan | 10 | 1,449 | 315 | 1,051 | 1,987 |
| Disposable income (national) | nominal yuan | 10 | 33,663 | 6,567 | 23,821 | 43,145 |
| Disposable income (urban) | nominal yuan | 10 | 45,447 | 7,645 | 33,616 | 56,311 |
| Disposable income (rural) | nominal yuan | 10 | 18,196 | 4,166 | 12,363 | 24,525 |
| Education share (national) | % of consumption | 10 | 10.9 | 0.7 | 9.6 | 11.8 |
| Annual births | millions | 9 | 12.9 | 3.5 | 9.0 | 17.9 |
| CPI education deflator | ratio (2015=1) | 10 | 0.92 | 0.03 | 0.86 | 0.98 |

