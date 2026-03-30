# Data Exploration: digital_economy_labor_structure

## 1. Data Cleaning Log

### 1.1 Dataset Inventory

The primary analysis dataset is the merged national panel at `data/processed/china_national_panel_merged.parquet`.

| Dataset | Original Shape | Usable Shape | Missing Treatment | Outlier Treatment | Notes |
|---------|---------------|--------------|-------------------|-------------------|-------|
| china_national_panel_merged | 24 rows x 40 cols | 24 rows x 37 cols | 3 columns dropped (96% missing); `secondary_enrollment_gross` 54% missing (retained but excluded from primary analysis); `rd_expenditure_pct_gdp` 1 obs missing (retained) | No outliers removed; `domestic_credit_private_pct_gdp` exceeds 100% (expected for China) | Usable missing rate: 1.69% |

### 1.2 Columns Dropped

Three ILO education-based labor force columns were dropped due to 95.83% missing rates (only 1 observation each, year 2000):

- `labor_force_advanced_education_pct`
- `labor_force_basic_education_pct`
- `labor_force_intermediate_education_pct`

**Justification:** Per DATA_QUALITY.md, these variables have only 1/24 non-null values. They provide zero time series information and their retention would risk accidental use. The single data point (year 2000) represents labor force participation rates by education group, not shares of total labor force -- semantically different from what the DAG requires.

### 1.3 Missing Value Treatment

| Variable | Missing Count | Missing % | Treatment |
|----------|--------------|-----------|-----------|
| `secondary_enrollment_gross` | 13/24 | 54.17% | Retained but excluded from primary analysis. Available only 2013-2023 (11 obs). Too short for reliable time series. |
| `rd_expenditure_pct_gdp` | 1/24 | 4.17% | Retained. Single missing year (2000). Affects normalized version as well. |
| `rd_expenditure_pct_gdp_normalized` | 1/24 | 4.17% | Same as above (derived variable). |

**No imputation was performed.** Missing values are left as NaN and handled by individual analysis methods (listwise deletion within each test). No zero-filling was applied.

### 1.4 Outlier Assessment

No 3-sigma outliers were detected in any numeric variable. `domestic_credit_private_pct_gdp` ranges from 100% to 190%, which exceeds 100% but is expected for China's credit-intensive financial system. This is not an outlier -- it reflects genuine economic structure.

### 1.5 Temporal Integrity

- **Year range:** 2000-2023 (24 annual observations)
- **Missing years:** None
- **Duplicate rows:** 0
- **Temporal continuity:** Complete, no gaps

---

## 2. Feature Engineering

### 2.1 Constructed Variables

| Feature | Formula / Logic | Source Variables | Purpose |
|---------|----------------|-----------------|---------|
| `log_gdp_pc` | $\ln(\text{gdp\_per\_capita\_usd})$ | `gdp_per_capita_usd` | Log-linearize GDP for regression; standard in growth literature |
| `post_pilot` | $1$ if year $\geq$ 2016, else $0$ | `year` | Structural break period indicator (post-smart-city-pilot) |
| `transition_window` | $1$ if year $\in \{2013, 2014, 2015\}$, else $0$ | `year` | Treatment window indicator for structural break analysis |
| `d_digital_economy_index` | $\Delta \text{DE}_t = \text{DE}_t - \text{DE}_{t-1}$ | `digital_economy_index` | First difference for stationary analysis |
| `d_employment_services_pct` | $\Delta \text{EmpServ}_t$ | `employment_services_pct` | First difference |
| `d_employment_industry_pct` | $\Delta \text{EmpInd}_t$ | `employment_industry_pct` | First difference |
| `d_employment_agriculture_pct` | $\Delta \text{EmpAgri}_t$ | `employment_agriculture_pct` | First difference |
| `d_services_value_added_pct_gdp` | $\Delta \text{ServVA}_t$ | `services_value_added_pct_gdp` | First difference |
| `d_population_15_64_pct` | $\Delta \text{Pop1564}_t$ | `population_15_64_pct` | First difference for demographic control |
| `d_population_65plus_pct` | $\Delta \text{Pop65}_t$ | `population_65plus_pct` | First difference |
| `d_urban_population_pct` | $\Delta \text{Urban}_t$ | `urban_population_pct` | First difference |
| `d_log_gdp_pc` | $\Delta \ln(\text{GDP/cap})_t$ | `log_gdp_pc` | GDP per capita growth rate (log diff) |
| `g_gdp_per_capita_usd` | $(GDP_t - GDP_{t-1}) / GDP_{t-1} \times 100$ | `gdp_per_capita_usd` | GDP growth rate (%) |
| `g_labor_force_total` | $(LF_t - LF_{t-1}) / LF_{t-1} \times 100$ | `labor_force_total` | Labor force growth rate (%) |

### 2.2 Validation of Engineered Features

All first-differenced variables have exactly 1 NaN (first observation, as expected). No Inf values were introduced by log transformation (all GDP values are positive). Growth rates have 1 NaN each (first observation).

**Final analysis-ready dataset:** 24 rows x 51 columns, saved to `data/processed/analysis_ready.parquet`.

---

## 3. Exploratory Analysis

### 3.1 Stationarity Tests (ADF + KPSS)

Joint ADF/KPSS protocol: a variable is classified as I(0) only if both tests agree (ADF rejects unit root AND KPSS fails to reject stationarity). If they disagree, classification is "ambiguous" and the ARDL bounds test approach is recommended for Phase 3.

| Variable | ADF stat (level) | ADF p (level) | KPSS stat (level) | KPSS p (level) | Level Verdict | ADF p (diff) | I(d) |
|----------|----------------:|---------------:|-----------------:|---------------:|---------------|-------------:|------|
| `digital_economy_index` | 1.144 | 0.996 | 0.120 | 0.099 | Ambiguous | 0.728 | I(1)* |
| `employment_services_pct` | -1.827 | 0.367 | 0.085 | 0.100 | Ambiguous | 0.003 | I(1) |
| `employment_industry_pct` | -0.927 | 0.779 | 0.134 | 0.073 | Ambiguous | 0.292 | I(1)* |
| `employment_agriculture_pct` | -1.174 | 0.685 | 0.157 | 0.041 | Non-stationary | 0.031 | I(1) |
| `services_value_added_pct_gdp` | -0.045 | 0.955 | 0.121 | 0.097 | Ambiguous | 0.665 | I(1)* |
| `population_15_64_pct` | -4.149 | 0.001 | 0.183 | 0.023 | Ambiguous | 0.697 | Ambiguous |
| `population_65plus_pct` | 1.626 | 0.998 | 0.186 | 0.021 | Non-stationary | 0.998 | Ambiguous |
| `urban_population_pct` | -1.871 | 0.346 | 0.142 | 0.057 | Ambiguous | 0.011 | I(1) |
| `log_gdp_pc` | -2.586 | 0.096 | 0.177 | 0.025 | Non-stationary | 0.826 | Ambiguous |
| `internet_users_pct` | 1.117 | 0.995 | 0.087 | 0.100 | Ambiguous | 0.084 | I(1)* |
| `mobile_subscriptions_per100` | -9.653 | 0.000 | 0.132 | 0.076 | I(0) | -- | I(0) |
| `fixed_broadband_per100` | 1.410 | 0.997 | 0.193 | 0.019 | Non-stationary | 0.032 | I(1) |

*Asterisked I(1) classifications are "likely" based on one test in first differences; the other test was borderline.

**Key findings:**

1. **Most variables are I(1).** The employment shares, DE index, services VA/GDP, urbanization, and broadband are all non-stationary in levels but stationary (or nearly so) in first differences. This is expected for trending macroeconomic time series.

2. **Demographic variables are ambiguous.** `population_15_64_pct` shows ADF rejection at levels (p=0.001) but KPSS rejection too (p=0.023), and first differences are NOT stationary by either test. `population_65plus_pct` is similarly problematic. This is likely due to the hump-shaped trajectory of working-age population (peaking ~2010, then declining) -- neither a unit root nor a simple trend. **Implication for Phase 3:** Demographic controls should use the ARDL bounds test approach, which is valid for I(0)/I(1) mixtures.

3. **Mobile subscriptions is I(0).** This is the only clearly stationary variable, likely because it reached saturation (~120/100) and plateaued. It should NOT be included in cointegration analysis with I(1) variables.

4. **DE index has borderline stationarity results.** ADF strongly fails to reject unit root (p=0.996), but KPSS also fails to reject stationarity (p=0.099). First differences are NOT clearly stationary (ADF p=0.728). This is concerning -- the DE index may have a more complex time series structure (possible I(2) or trend break). **Implication:** ARDL bounds test is essential as robustness. Toda-Yamamoto is valid regardless of integration order.

### 3.2 Structural Break Detection

**Chow tests at known smart city pilot dates:**

| Variable | Break at 2013 (F / p) | Break at 2015 (F / p) | Sup-Wald break year |
|----------|:--------------------:|:--------------------:|:-------------------:|
| DE Index | 2.942 / 0.076 | 2.710 / 0.091 | 2009 |
| Services Employment | 13.544 / 0.000 | 19.167 / 0.000 | **2014** |
| Industry Employment | 9.381 / 0.001 | 9.038 / 0.002 | 2006 |

**Findings:**

1. **Services employment shows a strong structural break at smart city pilot dates.** The Chow test is highly significant at both 2013 (p<0.001) and 2015 (p<0.001), and the sup-Wald procedure identifies 2014 as the maximum F-statistic break point -- exactly within the smart city pilot window. This is the strongest preliminary evidence for a structural change in employment coinciding with digital economy policy.

2. **Industry employment also breaks at pilot dates** (p=0.001 at 2013, p=0.002 at 2015), but the sup-Wald places the maximum break at 2006. The 2006 break likely reflects China's WTO accession adjustment and the mid-2000s manufacturing peak. The pilot-date break is secondary.

3. **DE index itself shows only marginal breaks at pilot dates** (p=0.076, 0.091). The sup-Wald identifies 2009 as the structural break -- coinciding with China's 3G mobile rollout and the post-GFC fiscal stimulus that accelerated ICT infrastructure investment. This suggests the DE index trajectory changed before the smart city program, which weakens the structural break interpretation for the DE-->employment relationship.

4. **Zivot-Andrews unit root test** failed due to numerical instability at T=24 (insufficient observations for reliable break-point estimation with trend and intercept breaks). This is a known limitation at small T.

### 3.3 DE Index Milestone Validation

The DE composite index (equal-weight average of normalized internet users, mobile subscriptions, broadband, and R&D expenditure) was validated against known digital economy milestones:

- **Pre-2015 growth rate:** 0.0443 per year (2005-2014 average)
- **Post-2015 growth rate:** 0.0501 per year (2016-2023 average)
- **Difference:** +0.0058 (marginal acceleration)

The index shows a smooth, monotonically increasing trajectory from 0.006 (2000) to 1.000 (2023). The "Internet Plus" strategy (2015) does not produce a visible inflection. COVID (2020) shows a +6.3% jump in DE index, consistent with digital acceleration, but this is within the range of normal year-over-year variation.

**Assessment:** The DE composite index captures the long-run ICT infrastructure build-out but does NOT show clear responsiveness to policy milestones. This is consistent with the DATA_QUALITY.md warning that the index measures ICT infrastructure penetration rather than digital economy activity. A validated PKU-DFIIC index would likely show sharper responses to the Internet Plus strategy and platform economy growth.

### 3.4 COVID Impact Assessment

| Variable | 2019 | 2020 | Change (%) | 2021 |
|----------|-----:|-----:|----------:|-----:|
| Services employment (%) | 44.52 | 45.27 | +1.68 | 45.60 |
| Industry employment (%) | 30.76 | 31.13 | +1.21 | 31.53 |
| DE index | 0.79 | 0.84 | +6.28 | 0.88 |
| GDP per capita (USD) | 10,343 | 10,627 | +2.75 | 12,887 |
| Labor force (total) | 775.9M | 760.9M | -1.94 | 781.2M |

**Assessment:** COVID had a measurable impact on total labor force (-1.94% in 2020), but sectoral employment shares continued their pre-existing trends without visible disruption. The ILO modeled estimates may smooth the actual COVID shock, which is consistent with the endogeneity concern (ILO models may not capture short-term fluctuations). **Decision for Phase 3:** Include 2020-2023 in the sample but test sensitivity by excluding 2020. The structural break analysis already excludes 2013-2015 from both pre and post periods, and 2020 falls in the post period.

### 3.5 Correlation Structure

**Level correlations** (all trending time series, T=24):

| | DE Index | Serv. Emp. | Ind. Emp. | Agri. Emp. |
|-|--------:|----------:|--------:|----------:|
| DE Index | 1.000 | 0.981 | 0.910 | -0.982 |
| Serv. Emp. | 0.981 | 1.000 | 0.914 | -0.997 |
| Pop 15-64 | -0.813 | -0.858 | -0.680 | 0.844 |
| Pop 65+ | 0.962 | 0.990 | 0.883 | -0.991 |
| Urban % | 0.988 | 0.993 | 0.935 | -0.996 |
| log GDP/cap | 0.988 | 0.995 | 0.909 | -0.994 |

**WARNING: Nearly all level correlations exceed |0.9|.** This is the classic spurious regression setup -- trending variables are mechanically correlated regardless of causal relationship. Level correlations are UNINFORMATIVE for causal inference.

**First-difference correlations** (removes trend, T=23):

| | $\Delta$DE | $\Delta$Serv. Emp. | $\Delta$Ind. Emp. |
|-|-----------:|------------------:|------------------:|
| $\Delta$DE | 1.000 | **-0.377** (p=0.076) | 0.261 (p=0.229) |
| $\Delta$Agri. Emp. | 0.057 (p=0.798) | -- | -- |
| $\Delta$Pop 15-64 | -0.058 (p=0.794) | 0.094 | 0.196 |
| $\Delta$Urban % | -0.213 (p=0.329) | 0.205 | -0.220 |

**Key finding:** After removing trends (first differences), the DE index is NEGATIVELY correlated with services employment growth (r=-0.377, p=0.076). This is the opposite sign from the level correlation (+0.981) and from the expected creation effect. Possible explanations:

1. **Year-to-year fluctuations in DE growth are inversely related to services employment growth** -- this could reflect a genuine short-run substitution dynamic (rapid digitalization temporarily displaces services workers) even as the long-run trend is positive.
2. **The DE index components (internet, broadband, R&D) have different short-run dynamics than employment** -- ICT infrastructure investment may have a delayed effect.
3. **Spurious result at small T=23** -- the correlation is only marginally significant (p=0.076).

The first-difference correlation with industry employment is positive (r=0.261) but insignificant (p=0.229). The agricultural employment correlation is essentially zero (r=0.057).

**Implication for Phase 3:** The reversal from positive level correlation to negative first-difference correlation is a strong signal that cointegration analysis is essential. If a genuine long-run equilibrium exists (cointegration), the short-run negative correlation may reflect adjustment dynamics (overshooting/correction). If no cointegration exists, the positive level correlations are spurious and the weak first-difference correlations represent the true (minimal) association.

### 3.6 Distribution Analysis and Normality

Shapiro-Wilk normality tests (p < 0.05 rejects normality):

| Variable | W statistic | p-value | Verdict |
|----------|:----------:|:-------:|---------|
| `digital_economy_index` | 0.946 | 0.220 | Normal |
| `employment_services_pct` | 0.917 | 0.050 | Borderline |
| `employment_industry_pct` | 0.861 | 0.004 | Non-normal |
| `employment_agriculture_pct` | 0.904 | 0.026 | Non-normal |
| `services_value_added_pct_gdp` | 0.874 | 0.006 | Non-normal |
| `population_15_64_pct` | 0.900 | 0.021 | Non-normal |

Most variables are non-normally distributed in levels, which is expected for trending time series. The distributions are typically skewed (reflecting the directional trends) rather than pathological. Bootstrap inference methods planned for Phase 3 are appropriate for non-normal data.

### 3.7 ILO Endogeneity Assessment

The ILO modeled employment estimates were tested for mechanical correlation with GDP, urbanization, and demographics:

| Employment variable | R-squared (GDP + Urban + Demo) | Durbin-Watson |
|--------------------|:----------------------------:|:------------:|
| Services employment (%) | **0.989** | 1.081 |
| Industry employment (%) | **0.913** | 0.768 |
| Agriculture employment (%) | **0.991** | 0.689 |

**Interpretation:** Services and agriculture employment shares are almost perfectly predicted (R-squared > 0.98) by GDP per capita, urbanization, and working-age population share. Industry employment is somewhat less predictable (R-squared = 0.91). The Durbin-Watson statistics are all below 2.0, indicating positive autocorrelation in residuals -- consistent with model smoothing.

**Partial correlations (DE vs employment, controlling for GDP/urbanization/demographics):**

| Variable | Simple r with DE | Partial r (controlling GDP, urban, demo) | Change |
|----------|:---------------:|:---------------------------------------:|:------:|
| Services employment | +0.981 | **-0.400** | -1.381 |
| Industry employment | +0.910 | **+0.105** | -0.805 |

**Critical finding:** After controlling for GDP, urbanization, and demographics, the correlation between DE index and services employment REVERSES from +0.981 to -0.400. The correlation with industry employment drops from +0.910 to near-zero (+0.105). This strongly suggests that:

1. **The level correlation between DE and employment is driven by shared trends** (GDP growth, urbanization, demographic transition) rather than a direct DE-->employment causal link.
2. **ILO employment estimates are substantially endogenous** to the very macroeconomic variables that would be used as controls in a regression. This means that including GDP/urbanization as controls "absorbs" most of the employment variation, leaving little for the DE index to explain.
3. **Phase 3 must run all specifications with AND without GDP/urbanization controls** to bracket the ILO endogeneity effect. If DE is significant only without controls but not with them, the finding is attributable to confounding/endogeneity rather than genuine causal effect.

**ILO modeling methodology note:** For China, the ILO uses econometric models that incorporate GDP, demographic trends, and educational attainment as inputs, calibrated against periodic labor force surveys. Between survey years, employment estimates are model extrapolations. This creates mechanical correlation between employment estimates and the very macroeconomic indicators used as explanatory variables in our analysis. This is documented as a HIGH-severity systematic uncertainty per STRATEGY.md Section 5.3.

### 3.8 Power Analysis (Monte Carlo)

A Monte Carlo simulation was conducted to estimate the power of the Toda-Yamamoto Granger causality test at T=24 with a bivariate VAR(1+1) specification:

| True effect size ($\beta$) | Power (rejection rate at $\alpha$=0.10) | Interpretation |
|:-------------------------:|:--------------------------------------:|---------------|
| 0.00 | 0.131 | Size (slightly above nominal 0.10 -- mild over-rejection) |
| 0.10 | 0.153 | Minimal power gain over size |
| 0.15 | 0.192 | Power = 19% -- very low |
| 0.20 | 0.236 | Power = 24% -- low |
| 0.30 | 0.349 | Power = 35% -- moderate |
| 0.40 | 0.512 | Power = 51% -- borderline adequate |
| 0.50 | 0.644 | Power = 64% -- still below 80% threshold |

**Key findings:**

1. **The test achieves 80% power only for very large effects** (estimated $\beta > 0.6$, not simulated but extrapolated). For published reference effect sizes (DID coefficients of 0.03-0.05 from Zhu et al. 2023), the Toda-Yamamoto test at T=24 has essentially no power to detect effects of that magnitude.

2. **Size distortion is mild.** The empirical size (13.1% at $\alpha$=0.10) is slightly above nominal, suggesting minor over-rejection under the null. Bootstrap critical values (planned for Phase 3) should correct this.

3. **For medium effects ($\beta$=0.30), power is only 35%.** This means a non-significant Granger test result cannot be interpreted as evidence against causation -- it may simply reflect insufficient power. Phase 3 must report power alongside all null results.

4. **Implication:** If the Toda-Yamamoto test fails to reject, the analysis should frame this as "insufficient evidence with power limitations" rather than "no effect." The power analysis makes the T=24 constraint's consequences explicit and quantitative.

---

## 4. Variable Ranking

### 4.1 Ranking by DAG Role and EP

| Rank | Variable | DAG Role | Phase 1 EP | Quality | Association (level r) | Association (diff r) | Include? | Notes |
|:----:|----------|----------|:----------:|:-------:|:--------------------:|:-------------------:|:--------:|-------|
| 1 | `digital_economy_index` | Primary causal variable | 0.32 (via SUB) | MEDIUM | 0.981 | -0.377 | Yes | ICT infrastructure proxy; construct validity concern |
| 2 | `population_15_64_pct` | Mandatory confounder | 0.36 | HIGH | -0.813 | -0.058 | Yes | Ambiguous I(d); use ARDL |
| 3 | `employment_services_pct` | Creation proxy (outcome) | 0.27 | MEDIUM | 0.981 | -0.377 | Yes | ILO modeled; endogeneity concern |
| 4 | `employment_industry_pct` | Substitution proxy (outcome) | 0.32 | MEDIUM | 0.910 | 0.261 | Yes | ILO modeled |
| 5 | `services_value_added_pct_gdp` | Mediator (industrial upgrading) | 0.23 | HIGH | 0.994 | -0.152 | Yes | Clean WB data, not ILO-modeled |
| 6 | `employment_agriculture_pct` | Structural change baseline | -- | MEDIUM | -0.982 | 0.057 | Yes | Complement to services/industry |
| 7 | `population_65plus_pct` | Alternative demographic control | 0.30 | HIGH | 0.962 | -0.019 | Yes | Ambiguous I(d) |
| 8 | `urban_population_pct` | Secondary control | -- | HIGH | 0.988 | -0.213 | Conditional | Collinear with GDP and DE index |
| 9 | `gdp_per_capita_usd` / `log_gdp_pc` | Secondary control; ILO endogeneity test | -- | HIGH | 0.988 | -0.051 | Conditional | Include for sensitivity tests only |
| 10 | `internet_users_pct` | DE component; alternative measure | -- | HIGH | 0.975 | 0.048 | Sensitivity | Use as alternative DE proxy |
| 11 | `fixed_broadband_per100` | DE component; alternative measure | -- | HIGH | 0.978 | 0.050 | Sensitivity | Use as alternative DE proxy |
| 12 | `self_employed_pct` | Informalization indicator | -- | MEDIUM | -0.960 | 0.183 | Descriptive | For DAG 3 characterization |
| 13 | `wage_salaried_workers_pct` | Formalization indicator | -- | MEDIUM | 0.960 | -0.183 | Descriptive | Mirror of self-employed |
| 14 | `youth_unemployment_pct` | Supplementary outcome | -- | MEDIUM | 0.556 | -0.174 | Descriptive | COVID spike visible |
| 15 | `vulnerable_employment_pct` | Supplementary outcome | -- | MEDIUM | -0.965 | 0.222 | Descriptive | Declining trend |

### 4.2 Variables Excluded

| Variable | Reason |
|----------|--------|
| `labor_force_advanced/basic/intermediate_education_pct` | 95.83% missing; dropped |
| `secondary_enrollment_gross` | 54% missing; only 11 obs (2013-2023); too short |
| `mobile_subscriptions_per100` | I(0); cannot be included in cointegration with I(1) variables |
| Normalized DE components (`*_normalized`) | Redundant with raw components |
| `internet_penetration_index` | Redundant with `digital_economy_index` |

### 4.3 Red Flags

1. **Near-perfect multicollinearity in levels.** DE index, urban population, GDP per capita, and services employment all have pairwise correlations > 0.98. Multivariate regressions in levels will suffer severe multicollinearity. First-differencing and cointegration partially address this.

2. **Partial correlation reversal.** DE vs services employment reverses from +0.98 to -0.40 after controlling for GDP/urbanization/demographics. This means the observed positive association is attributable to shared trends, not to a direct DE-->employment link. Phase 3 must address this explicitly.

3. **Demographic variable integration order is ambiguous.** Neither I(0) nor clearly I(1). This complicates cointegration analysis that assumes all variables are I(1).

---

## 5. Data Readiness Assessment

### 5.1 Method Prerequisites

| Edge | Method | Data Ready? | Assumptions OK? | Risk Level |
|------|--------|:-----------:|:---------------:|:----------:|
| DE --> SUB (substitution) | Toda-Yamamoto Granger | Yes | Lag order determinable; power low (35% at medium effect) | MEDIUM-HIGH |
| DE --> SUB (substitution) | Johansen cointegration + VECM | Yes | Most variables I(1); DE index ambiguous | MEDIUM |
| DE --> CRE (creation) | Toda-Yamamoto Granger | Yes | Same as above | MEDIUM-HIGH |
| DE --> CRE (creation) | ARDL bounds test | Yes | Valid for I(0)/I(1) mix; essential given ambiguous stationarity | LOW |
| DE --> LS (structural break) | Chow test at known dates | Yes | Strong break found for employment at 2013-2015 | MEDIUM |
| DE --> IND_UP (mediation) | VAR impulse response | Yes | Ordering assumption required; T=24 limits lag depth | MEDIUM |
| DEMO --> LS (confounder) | Granger + VECM control | Yes | Ambiguous integration order for demo variables | MEDIUM-HIGH |

### 5.2 Assumption Pre-Check Summary

| Assumption | Status | Evidence | Action |
|------------|:------:|----------|--------|
| Variables are I(1) | Mostly confirmed | 8/12 variables I(1); 3 ambiguous (demo, GDP); 1 I(0) (mobile) | Use ARDL alongside Johansen; exclude mobile from cointegration |
| Structural break at pilot dates | Supported for employment | Services emp break at 2014 (sup-Wald); significant Chow at 2013/2015 | Proceed with structural break analysis |
| DE index captures digital economy | Partially | Smooth trajectory; no clear policy-milestone response | Report as ICT infrastructure proxy; sensitivity with individual components |
| ILO estimates are exogenous | **VIOLATED** | R-squared > 0.98 for services/agriculture vs GDP+urban+demo | Run with/without controls; interpret cautiously |
| Adequate power for Granger test | **Low** | 35% power at medium effect size; 13% size at T=24 | Report power alongside all test results; bootstrap CIs |

### 5.3 Method Pivots

No method pivots are required. The planned Toda-Yamamoto + ARDL + structural break approach is robust to the ambiguous stationarity findings. However, two adjustments are recommended:

1. **Elevate ARDL bounds test from secondary to co-primary** alongside Johansen, given the ambiguous integration orders of demographic variables and DE index.
2. **Add ILO endogeneity sensitivity test as a mandatory deliverable in Phase 3** (run all specifications with and without GDP/urbanization controls, report the coefficient range).

### 5.4 Warnings Carried Forward from DATA_QUALITY.md

1. **DID is NOT executable.** Smart city pilot treatment indicator exists but lacks city-level outcome data. Structural break analysis substitutes.
2. **Skill-level analysis is impossible.** ILO education columns unusable. SBTC hypothesis untestable. EP=0.00 for skill edges.
3. **DE composite index is a proxy of uncertain validity.** Coefficients must be interpreted as "association with ICT infrastructure penetration."
4. **T=24 limits model complexity.** Maximum 4-5 regressors. Power analysis shows 35% power for medium effects.
5. **ILO employment estimates are substantially endogenous** to GDP, urbanization, and demographics (R-squared 0.91-0.99). Phase 3 must bracket this uncertainty.

---

## 6. Figures Index

| Figure | File | Description |
|--------|------|-------------|
| Key time series | `figures/ts_key_variables.pdf` | Six-panel plot of DE index, employment sectors, services VA, demographic variables with smart city pilot window shaded |
| DE index components | `figures/de_index_components.pdf` | DE composite index alongside internet users, mobile subscriptions, broadband with policy milestone markers |
| Employment structure | `figures/employment_structure_stacked.pdf` | Stacked area chart of agricultural, industrial, services employment shares (2000-2023) |
| Correlation matrix (levels) | `figures/correlation_matrix_levels.pdf` | 9x9 heatmap of level correlations among key variables; near-universal |r|>0.9 |
| Correlation matrix (first differences) | `figures/correlation_matrix_first_diffs.pdf` | 9x9 heatmap of first-difference correlations; much weaker, some sign reversals |
| ACF/PACF | `figures/acf_pacf_key_variables.pdf` | ACF and PACF plots for DE index, services employment, industry employment, working-age population |
| Distributions | `figures/distributions_levels.pdf` | Histograms with normal overlay and Shapiro-Wilk p-values for 9 key variables |
| DE vs employment scatter | `figures/scatter_de_vs_employment.pdf` | Scatter plots of DE index vs services/industry employment and services VA, colored by year, with Pearson r |
| Demographic transition | `figures/demographic_transition.pdf` | Dual-axis plot of working-age population (peaking 2010) and elderly population, with pilot window |
| Structural break analysis | `figures/structural_break_analysis.pdf` | Four-panel: (a) DE index with break window, (b) employment sectors with break, (c) first-diff scatter pre/post, (d) counterfactual trend extrapolation |
| Power analysis | `figures/power_analysis_toda_yamamoto.pdf` | Power curve for Toda-Yamamoto test at T=24 across effect sizes 0.0-0.5 |
| ILO endogeneity | `figures/ilo_endogeneity_residuals.pdf` | Residual-vs-fitted plots for employment shares regressed on GDP/urbanization/demographics (R-squared annotated) |
