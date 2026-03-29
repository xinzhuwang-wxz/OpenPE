# Data Quality Assessment

**Analysis:** china_double_reduction_education
**Question:** Did China's Double Reduction policy truly reduce household education expenditure?
**Assessment date:** 2026-03-29
**Agent:** data-quality-agent (Phase 0, Step 0.5)

---

## Summary

The data portfolio for this analysis is structurally incomplete in ways that constrain the strength of any causal conclusions. The most critical gap is the absence of post-policy household-level microdata with education spending decomposition: both CFPS (post-2021 waves) and CIEFR-HS (Wave 3, 2021-2022) failed acquisition. The analysis must therefore rely on NBS macro-level aggregates that bundle education with culture and recreation spending, supplemented by pre-policy micro-level composition data from CIEFR-HS (2017 and 2019 only). Underground tutoring data is anecdotal, drawn from media reports rather than systematic surveys. These limitations collectively mean the analysis can identify directional trends and test compositional hypotheses at the macro level, but cannot produce precise quantitative estimates of the policy's causal effect on household education expenditure. The gate decision is PROCEED WITH WARNINGS.

---

## Gate Decision

**Verdict: PROCEED WITH WARNINGS**

**Justification:** Three of four CRITICAL variables (total education expenditure, off-campus tutoring expenditure, in-school fees) are supported only by LOW or MEDIUM quality data for the post-policy period. Specifically:

1. **Total household education expenditure** -- the primary outcome variable -- is available only as the NBS "education, culture and recreation" proxy, which bundles non-education spending and is scored MEDIUM. No household-level decomposition exists post-2021.
2. **Off-campus tutoring expenditure** post-policy has no direct measurement. The CIEFR-HS data covers 2017 and 2019 only (pre-policy). Underground tutoring data is anecdotal and scored LOW.
3. **In-school fees** post-policy have no separate measurement.
4. **Household income** (NBS disposable income) is scored HIGH -- the one CRITICAL variable with adequate data.

The analysis can proceed because: (a) the NBS education/culture/recreation series provides a reasonable upper-bound proxy for education spending trends; (b) the CIEFR-HS pre-policy composition data grounds the decomposition analysis; (c) the tutoring industry collapse is well-documented. However, the analysis CANNOT:
- Precisely quantify the policy's effect on pure education spending (vs. culture/recreation)
- Directly measure underground tutoring spending or substitution effects
- Decompose post-policy spending into in-school vs. out-of-school components
- Produce household-level heterogeneous treatment effects by income

**Constraints on conclusions that downstream agents MUST respect:**
1. All post-policy spending analysis is based on a PROXY that overstates education spending. Conclusions must be hedged accordingly.
2. Underground tutoring effects can only be assessed directionally from anecdotal data. No quantitative underground market sizing is supportable.
3. Pre-post comparisons must prominently acknowledge COVID-19 confounding (2020-2022 overlap) and demographic decline as alternative explanations.
4. Income-stratified analysis is limited to urban/rural splits at the macro level; quintile-level analysis is not possible with available data.
5. The 73/12/15 spending composition (in-school/tutoring/other) is from 2019 and may have shifted post-policy; it cannot be treated as a stable structural parameter.

---

## Per-Dataset Assessment

### Dataset 1: NBS Per Capita Consumption Expenditure on Education, Culture and Recreation

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 90    | HIGH    | 10 years (2016-2025), 0% missing values, national/urban/rural splits all present |
| Consistency  | 75    | MEDIUM  | 2016-2018 values back-calculated from YoY growth rates (+/- 2-3% error). 2020 COVID dip (-19.1% national) and 2021 rebound (+27.9%) are internally consistent with pandemic timing. No impossible values. |
| Bias         | 45    | LOW     | **CRITICAL: This is a proxy variable, not a direct measure of education spending.** The NBS category bundles education with culture and recreation. Post-COVID recovery in culture/recreation spending (tourism, entertainment) inflates this series relative to pure education. Direction of bias: likely overstates education spending growth post-2021. The magnitude of the proxy error is unknown and may vary over time. |
| Granularity  | 60    | MEDIUM  | Annual national/urban/rural is adequate for trend analysis but insufficient for causal identification. No provincial disaggregation. No income-level disaggregation. No within-education decomposition. |
| **Overall**  | 68    | **MEDIUM** | Simple average of (90+75+45+60)/4 = 67.5 |

**Conclusion support:** This dataset supports identifying the direction and approximate magnitude of trends in a broad spending category that includes education. It does NOT support precise claims about education spending specifically, nor causal attribution to the Double Reduction policy.

**Statistics:**
- Rows: 10, Columns: 14, Missing: 0%
- Education/culture/recreation national: 1,825 yuan (2016) to 3,489 yuan (2025), steady upward trend
- Sharp COVID dip in 2020 (2,032 yuan, -19.1% YoY) followed by strong rebound in 2021 (2,599 yuan, +27.9%)
- Post-policy trajectory: 2,599 (2021) -> 2,469 (2022, -5.0%) -> 2,904 (2023, +17.6%) -> 3,189 (2024, +9.8%) -> 3,489 (2025, +9.4%)
- Education share of total consumption: range 9.6% (2020) to 11.8% (2025), relatively stable at ~10.5-11.5%
- 2016-2018 flagged as "back_calculated" data source; 2019-2025 from NBS press releases
- **Suspicious finding:** 0% missing values across 10 years and 14 columns. The 2016-2018 back-calculation fills what would otherwise be gaps, masking the true completeness. Effective completeness for directly reported data is 70% (7 of 10 years).

---

### Dataset 2: CIEFR-HS Education Spending Decomposition

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 30    | LOW     | Only 2 survey waves (2017, 2019) -- both pre-policy. No post-2021 data. 13 observations (summary statistics, not microdata). 5% missing values. |
| Consistency  | 85    | HIGH    | Internal consistency is strong: shares sum to 100% (73+12+15), expenditure figures are plausible and consistent with VoxChina cross-reference. 2017-to-2019 trends are coherent (total spending declined, per-participant tutoring costs rose). |
| Bias         | 65    | MEDIUM  | Survey is nationally representative (CIEFR-HS is a well-designed probability sample). However, these are summary statistics extracted from a published paper, not the underlying microdata. Aggregation may mask important distributional information. The 73/12/15 composition is a national average that may not hold across income groups or regions. |
| Granularity  | 50    | MEDIUM  | Provides the critical decomposition (in-school vs. tutoring vs. other) that NBS data lacks. Has urban/rural, income quintile, and education level splits. But only 2 time points and only summary statistics -- insufficient for time-series analysis or panel methods. |
| **Overall**  | 58    | **MEDIUM** | Simple average of (30+85+65+50)/4 = 57.5 |

**Conclusion support:** This dataset supports characterizing the pre-policy composition of household education spending and identifying the structural constraint that tutoring represents only ~12% of total education costs. It does NOT support pre-post policy comparisons (no post-policy wave available) and cannot be used to track post-policy compositional shifts.

**Statistics:**
- Main composition file: 3 rows, 3 columns (in-school 73%, tutoring 12%, other 15%)
- Sub-files provide richer detail: ciefr_compulsory_education_2017_vs_2019 (4 rows, 14 columns), ciefr_spending_by_income_quintile (rich income stratification), ciefr_tutoring_2017_vs_2019 (participation trends)
- Critical pre-trend finding: Total education expenditure per student DECLINED from 10,372 yuan (2017) to 6,090 yuan (2019) -- BEFORE the policy. This pre-existing downward trend complicates causal attribution.
- Income inequality data: lowest quartile spends 56.8% of income on education vs. 10.6% for highest quartile (caveat: this figure may represent share of household expenditure rather than income; verify against original Wei (2024) paper in Phase 1)

---

### Dataset 3: World Bank Education Indicators - China

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 35    | LOW     | 15 rows but 38.1% overall missing rate. Government education spending (% GDP and % govt expenditure) has data for only 1 of 15 years (2023) -- effectively useless. Secondary enrollment missing for 12 of 15 years. GDP per capita and population 0-14% are complete. |
| Consistency  | 70    | MEDIUM  | GDP per capita shows smooth upward trend (plausible). Population 0-14% shows steady decline (consistent with known demographic transition). The single data point for govt education spending (4.0% GDP in 2023) is consistent with NBS/MoF data. |
| Bias         | 75    | MEDIUM  | World Bank is an authoritative source with standardized methodology. However, China's education spending data reported to World Bank may differ from domestic figures due to classification differences. 1-2 year reporting lag documented. |
| Granularity  | 55    | MEDIUM  | Annual national data. Adequate for macro context variables (GDP, demographics) but no subnational detail. |
| **Overall**  | 59    | **MEDIUM** | Simple average of (35+70+75+55)/4 = 58.8 |

**Conclusion support:** This dataset provides reliable GDP per capita and demographic trend data for use as control variables. The education spending indicators are too sparse (1 data point) to be analytically useful -- the separate NBS public education expenditure dataset should be used instead.

**Statistics:**
- GDP per capita: 31,341 CNY (2010) to 95,749 CNY (2024), complete series
- Population 0-14%: 18.5% (2010) declining to 16.0% (2024), complete series
- Govt education spending % GDP: only 2023 has data (4.0%), all other years NaN
- Govt education spending % govt expenditure: only 2023 has data (11.9%), all other years NaN
- Secondary enrollment: only 3 of 15 years have data

---

### Dataset 4: Tutoring Industry Collapse Indicators

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 60    | MEDIUM  | 10 data points covering 2020-2024. Mix of metrics (market size, job postings, layoffs, closure rates) -- not a consistent time series. Key years covered but sparse. |
| Consistency  | 55    | MEDIUM  | Multiple sources compiled (Mordor Intelligence, academic papers, Ministry of Education, SEC filings). Market size estimate ($100B) is at the high end of published estimates (range $70-300B). Job posting decline (-89%) and layoff figures (3M, 60K New Oriental) are mutually consistent. Closure rates (95% offline, 85% online by 2024) are from official sources. |
| Bias         | 50    | MEDIUM  | Market size estimates vary enormously across sources ($70B to $300B), suggesting significant measurement uncertainty. Government-reported closure rates may overstate enforcement success. Academic paper estimates may reflect publication-time anchoring. The -89% job posting decline is from a single paper. |
| Granularity  | 45    | LOW     | National aggregates only. No provincial variation. Mix of annual and one-time snapshot data points. Fiscal year misalignment for company data. Insufficient for time-series modeling. |
| **Overall**  | 53    | **MEDIUM** | Simple average of (60+55+50+45)/4 = 52.5 |

**Conclusion support:** This dataset supports the qualitative conclusion that the formal tutoring industry experienced a severe collapse post-policy. It provides order-of-magnitude indicators but not a reliable time series for quantitative modeling. The industry destruction is the most well-documented aspect of the policy's effects.

**Statistics:**
- Pre-policy market size: ~$100B (2020, Mordor Intelligence estimate)
- Job posting decline: -89% within 4 months of policy
- Jobs lost: 3,000,000 (national), New Oriental: 60,000
- VAT revenue loss: 11 billion RMB over 18 months
- Closure rates by 2024: 95% offline, 85% online institutions
- Illegal operations detected: ~3,000 in Q2 2022

---

### Dataset 5: Double Reduction Policy Enforcement Timeline

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 70    | MEDIUM  | 8 key events from July 2021 to October 2024. Covers major milestones. But does NOT capture regional variation in enforcement timing, which is critical for identification strategy. |
| Consistency  | 90    | HIGH    | Dates and events are well-documented from official sources and verified against Wikipedia and news reports. Event sequence is internally consistent. |
| Bias         | 55    | MEDIUM  | Compiled from official policy documents and media reports. May over-represent central government actions and under-represent local implementation variation. The October 2024 "easing" event is from VOA, a non-Chinese source -- potentially reflecting different editorial framing. |
| Granularity  | 40    | LOW     | National-level events only. No provincial enforcement timelines. For causal identification using enforcement intensity variation, this dataset is insufficient. |
| **Overall**  | 64    | **MEDIUM** | Simple average of (70+90+55+40)/4 = 63.8 |

**Conclusion support:** This dataset supports establishing the policy timeline and identifying pre/post periods for analysis. It does NOT support enforcement-intensity-based identification strategies due to lack of regional detail.

**Statistics:**
- 8 events, date range: 2021-07-24 to 2024-10-01
- Event types: policy_announcement (1), enforcement_start (1), enforcement_deadline (2), enforcement_milestone (1), enforcement_report (1), enforcement_escalation (1), policy_modification (1)
- No missing values

---

### Dataset 6: China Demographics and Education Enrollment

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 75    | MEDIUM  | 9 years (2016-2024). Birth data complete. Enrollment data missing for 2016-2017 and 2024 (33.3% missing for that column). |
| Consistency  | 90    | HIGH    | Birth rate decline is smooth and monotonic (12.95 per 1000 in 2016 to 6.77 in 2024). Population figures are consistent with NBS communiques. Enrollment data shows expected trend (increasing through 2022, reflecting earlier birth cohorts entering school). |
| Bias         | 80    | HIGH    | NBS demographic data is considered reliable at the national level. Registration-based birth data may slightly undercount but the direction of demographic decline is unambiguous. |
| Granularity  | 65    | MEDIUM  | Annual national data. Adequate for controlling for demographic confounding at the aggregate level. No provincial or urban/rural disaggregation. |
| **Overall**  | 78    | **MEDIUM** | Simple average of (75+90+80+65)/4 = 77.5 |

**Conclusion support:** This dataset supports controlling for demographic decline as a confounder in aggregate spending analysis. The falling birth rate (from 17.86M births in 2016 to 9.02M in 2023) is a first-order confounder that must be addressed. Per-child spending rather than aggregate spending should be the analytical target where possible.

**Statistics:**
- Births: 17.86M (2016) declining to 9.54M (2024), -47% decline
- Birth rate: 12.95 per 1000 (2016) to 6.77 per 1000 (2024)
- Compulsory education enrollment: 148.23M (2018) to 160.65M (2022), then declining
- Enrollment missing for 2016, 2017, and 2024

---

### Dataset 7: China Public Education Expenditure

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 85    | HIGH    | 8 years (2016-2023), 0% missing values. Missing 2024-2025. |
| Consistency  | 90    | HIGH    | Steady upward trend from 3.89T yuan (2016) to 6.46T yuan (2023). GDP share stable at 4.0-4.2%, consistent with China's >4% policy commitment. Cross-validates with World Bank's single data point (4.0% in 2023). |
| Bias         | 70    | MEDIUM  | Government self-reported fiscal data. May include items that are not strictly "education" under international definitions. The >4% GDP target creates incentive to report at or above threshold. However, NBS/MoF data is widely used and cited in international literature. |
| Granularity  | 55    | MEDIUM  | National annual totals. No provincial breakdown. No breakdown between compulsory education and other levels (though 2023 has a one-time breakdown in notes). |
| **Overall**  | 75    | **MEDIUM** | Simple average of (85+90+70+55)/4 = 75.0 |

**Conclusion support:** This dataset supports testing the DAG 3 crowding-in hypothesis at the macro level (does public spending growth correlate with household spending growth?). It provides the independent variable for the public spending -> household spending causal edge.

**Statistics:**
- Total education spending: 3.89T yuan (2016) to 6.46T yuan (2023), +66% nominal growth
- GDP share: 4.22% (2016), dipping to 4.01% (2021-2022), recovering to 4.12% (2023)
- 2023 breakdown: compulsory education 2.84T, higher education 1.76T, high school 1.02T, preschool 0.54T
- No missing values, no anomalies

---

### Dataset 8: NBS Per Capita Consumption - All 8 Categories

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 80    | HIGH    | 7 years (2019-2025), 0% missing values across all 18 columns (8 categories in yuan + 8 shares + year + total). |
| Consistency  | 85    | HIGH    | Category shares sum to ~100% in each year (verified: e.g., 2019: 28.2+6.2+23.4+5.9+13.3+11.7+8.8+2.4 = 99.9%). Absolute values are internally consistent with the NBS education expenditure dataset (education_culture_recreation column matches). COVID 2020 dip visible across relevant categories. |
| Bias         | 50    | MEDIUM  | Same proxy problem as Dataset 1 for the education category. However, this dataset's VALUE is in enabling compositional analysis -- detecting whether education/culture/recreation share changed relative to other categories. The bias from bundling is partially mitigated when analyzing shares rather than levels. |
| Granularity  | 65    | MEDIUM  | Annual national data with 8-category breakdown. Useful for compositional shift analysis but no urban/rural split and no within-education decomposition. |
| **Overall**  | 70    | **MEDIUM** | Simple average of (80+85+50+65)/4 = 70.0 |

**Conclusion support:** This dataset supports analyzing whether the education/culture/recreation spending share shifted relative to other consumption categories post-policy. It is most useful for the compositional analysis (DAG 3) -- detecting crowding effects and spending substitution across broad categories.

**Statistics:**
- Education/culture/recreation share: 11.7% (2019) -> 9.6% (2020, COVID) -> 10.8% (2021) -> 10.1% (2022) -> 10.8% (2023) -> 11.3% (2024) -> 11.8% (2025)
- Healthcare share increased: 8.8% (2019) -> 8.7% (2020) -> 9.2% (2023) -> 8.7% (2025)
- Transport/telecom share: 13.3% (2019) -> 14.6% (2025), steady increase
- Food share declining: 30.2% (2020) -> 29.3% (2025)

---

### Dataset 9: NBS Per Capita Disposable Income

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 95    | HIGH    | 10 years (2016-2025), 0% missing values across all 5 columns. Full temporal overlap with expenditure data. |
| Consistency  | 90    | HIGH    | Smooth monotonic upward trend. Urban-rural ratio declining steadily (2.72 in 2016 to 2.30 in 2025), consistent with known convergence trend. No anomalies. |
| Bias         | 80    | HIGH    | NBS household survey methodology is well-established. Per capita figures are nationally representative. However, this is mean income, not median -- may overstate typical household purchasing power due to skewness. No income quintile breakdown. |
| Granularity  | 60    | MEDIUM  | Annual national/urban/rural. Adequate for macro-level income controls. Insufficient for income-stratified analysis of policy effects (need quintile-level data from CFPS, which is unavailable). |
| **Overall**  | 81    | **HIGH** | Simple average of (95+90+80+60)/4 = 81.3 |

**Conclusion support:** This dataset supports controlling for income growth in spending trend analysis and examining urban-rural differential effects at the macro level. It is the strongest dataset in the portfolio.

**Statistics:**
- National income: 23,821 yuan (2016) to 43,145 yuan (2025), +81% nominal growth
- Urban income: 33,616 yuan (2016) to 56,311 yuan (2025)
- Rural income: 12,363 yuan (2016) to 24,525 yuan (2025)
- Urban-rural ratio: 2.72 (2016) declining to 2.30 (2025)
- No missing values, no duplicates

---

### Dataset 10: International Comparison of Household Education Spending

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 40    | LOW     | 5 countries, single time point (2019). 3 of 5 values are "approximate" from VoxChina summary. |
| Consistency  | 50    | MEDIUM  | China value (7.9%) from CIEFR-HS is well-sourced. Other values (Japan ~2%, Mexico ~2%, USA ~1%, South Korea 5.3%) are approximate and may use different definitions of "education expenditure." Cross-country comparability is questionable. |
| Bias         | 40    | LOW     | Definition inconsistency across countries. "Education as % of household expenditure" may include or exclude different items in each country's national accounts. China figure includes the 73% in-school component that may be differently classified elsewhere. |
| Granularity  | 30    | LOW     | Single snapshot, 5 countries. No time series. No within-country variation. |
| **Overall**  | 40    | **LOW** | Simple average of (40+50+40+30)/4 = 40.0 |

**Conclusion support:** This dataset provides only rough context for China's relative position. It supports the qualitative statement that Chinese households spend a higher share on education than most comparators. It does NOT support precise cross-country comparisons due to definitional inconsistencies.

---

### Dataset 11: Underground Tutoring Price and Activity Indicators

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 35    | LOW     | 9 price data points and 5 activity indicators. Event-based, not systematic. No standardized time series. Covers 2021-2024 but with large gaps. |
| Consistency  | 40    | LOW     | Prices from different media sources using different definitions (per hour, per session, per 2-hour class, group vs. one-on-one). Not directly comparable across rows. The 3,000 yuan/hour "premium" outlier is 10x the median, suggesting extreme heterogeneity or different market segments. |
| Bias         | 25    | LOW     | **SEVERE: Selection bias in media reporting.** Media outlets disproportionately report extreme cases (very high prices, dramatic crackdowns). The sample is not representative of the typical underground tutoring transaction. Self-selection: parents willing to speak to media about illegal activity are not typical. Government enforcement data (3,000 illegal operations) is a lower bound -- detection rate is unknown. |
| Granularity  | 30    | LOW     | Individual anecdotes, not systematic data. No geographic coverage information. No participation rates. No total market size estimate possible from this data. |
| **Overall**  | 33    | **LOW** | Simple average of (35+40+25+30)/4 = 32.5 |

**Conclusion support:** This dataset supports ONLY the directional conclusion that underground tutoring emerged post-policy and that prices increased relative to pre-ban levels. It provides anecdotal evidence of a 43-50% average price increase for comparable services, corroborated across multiple independent media sources. It does NOT support any quantitative estimate of underground market size, participation rates, or total spending. Any numerical claims about underground tutoring must carry prominent "anecdotal evidence only" warnings.

**Statistics:**
- Pre-ban prices: 200-350 yuan (group/one-on-one)
- Post-ban prices: 400-3,000 yuan (wide range reflecting market heterogeneity)
- Price increase for comparable one-on-one: ~300 yuan (pre) to ~450 yuan (post), ~50% increase
- Extreme case: 3,000 yuan/hour for premium tutors (high-end market segment)
- Teacher earnings: 300 yuan/institutional class (pre) to 800 yuan/secret course (post), ~167% increase

---

### Dataset 12: Crowding-In Effect Evidence (Academic Literature)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 50    | MEDIUM  | 3 studies, qualitative compilation. Covers the key crowding-in finding. Missing the actual regression coefficients and confidence intervals from the ScienceDirect 2025 paper (only direction and mechanism extracted). |
| Consistency  | 80    | HIGH    | All 3 studies are internally consistent in supporting the crowding-in hypothesis. The ScienceDirect 2025 finding (public spending increases household spending) is corroborated by the CIEFR-HS composition data and the Lu 2025 fiscal spending review. |
| Bias         | 55    | MEDIUM  | Literature compilation may suffer from citation bias -- only studies supporting the crowding-in narrative were included. Conflicting studies (if any) were not searched for or included. The ScienceDirect 2025 study uses CHIP data with county-level matching, which is a credible methodology, but the result may not generalize to all regions/periods. |
| Granularity  | 40    | LOW     | Qualitative findings only. No quantitative effect sizes extracted. Cannot be used directly in statistical models. |
| **Overall**  | 56    | **MEDIUM** | Simple average of (50+80+55+40)/4 = 56.3 |

**Conclusion support:** This dataset supports the DAG 3 hypothesis that public education spending has a crowding-in rather than crowding-out effect on household spending. The evidence is qualitative and from a small number of studies. It provides theoretical grounding but not a quantitative effect size.

---

### Dataset 13: NBS Consumer Price Index (Overall and Education Sub-Index)

| Dimension    | Score | Verdict | Key Finding |
|-------------|-------|---------|-------------|
| Completeness | 90    | HIGH    | 10 years (2016-2025), 0% missing values. Full temporal overlap with expenditure and income data. Both overall CPI and education sub-index present. |
| Consistency  | 80    | HIGH    | Index constructed from published NBS YoY changes. Cumulative overall inflation 15.3% and education inflation 16.8% over 2016-2025 are consistent with known price trends. Cross-validates with independent sources. |
| Bias         | 70    | MEDIUM  | CPI methodology is well-established but has known limitations: basket composition changes over time, CPI may understate true education cost inflation (private tutoring prices not fully captured in official basket), and 2025 values are preliminary estimates. The education sub-index tracks the NBS "Education, Culture and Recreation" category, which includes non-education components (same proxy issue as expenditure data). |
| Granularity  | 60    | MEDIUM  | Annual national data. Adequate for deflating the NBS expenditure series (same temporal and spatial granularity). No urban/rural CPI split (would require additional acquisition for urban/rural real spending analysis). |
| **Overall**  | 75    | **MEDIUM** | Simple average of (90+80+70+60)/4 = 75.0 |

**Conclusion support:** This dataset enables conversion of all nominal spending figures to real (CPI-adjusted) 2015 yuan. It resolves the previously identified data gap (Open Issue #4) and supports the binding constraint that all spending trend analysis must use real values. The education-specific deflator is preferable for education spending series, while the overall deflator should be used for income and cross-category comparisons.

**Statistics:**
- Overall CPI index (2015=100): 102.0 (2016) to 115.3 (2025)
- Education CPI index (2015=100): 101.6 (2016) to 116.8 (2025)
- Cumulative overall inflation: 15.3%
- Cumulative education inflation: 16.8%
- Overall deflator range: 0.867 to 0.980
- Education deflator range: 0.856 to 0.984

---

### Failed Datasets (6 datasets with status: failed)

| Dataset | CRITICAL? | Impact on Analysis |
|---------|-----------|-------------------|
| CFPS Microdata (post-2021) | **YES** | No household-level post-policy data. Cannot test heterogeneous effects by income. Cannot decompose spending changes at micro level. |
| CIEFR-HS Wave 3 (2021-2022) | **YES** | No post-policy spending decomposition. Cannot verify whether the 73/12/15 composition shifted. |
| Underground Tutoring Systematic Survey | YES (for DAG 2) | Cannot quantify underground market. DAG 2 testing relies on anecdotal data only. |
| Regional Enforcement Intensity Index | IMPORTANT | Cannot exploit enforcement variation for causal identification. Eliminates one key identification strategy. |
| Non-Academic Enrichment Spending | IMPORTANT | Cannot test substitution into non-academic channels. |
| Parental Anxiety Index | USEFUL | Cannot assess subjective burden changes. |

---

## Cross-Dataset Assessment

### DAG Coverage

| DAG Edge | Supporting Datasets | Quality Verdict | Can Test? |
|----------|-------------------|----------------|-----------|
| **Policy -> Industry Collapse** (all DAGs) | Tutoring Industry Metrics (#4), Policy Timeline (#5) | MEDIUM | YES -- direction and magnitude well-documented |
| **Industry Collapse -> Reduced Tutoring Spending** (DAG 1) | CIEFR-HS (#2, pre-policy only), NBS proxy (#1) | LOW | PARTIALLY -- can infer from industry data, but no direct household tutoring spending post-policy |
| **Reduced Tutoring -> Reduced Total Expenditure** (DAG 1) | NBS proxy (#1, #8), CIEFR-HS composition (#2) | LOW-MEDIUM | PARTIALLY -- can test direction using NBS proxy trend, but proxy bundles non-education spending |
| **Policy -> Underground Market** (DAG 2) | Underground Tutoring (#11) | LOW | DIRECTIONALLY ONLY -- anecdotal data supports emergence but not quantification |
| **Underground Market -> Higher Prices** (DAG 2) | Underground Tutoring (#11) | LOW | DIRECTIONALLY ONLY -- price increases documented anecdotally |
| **Competitive Pressure -> Inelastic Demand** (DAG 2) | CIEFR-HS income data (#2), Literature (#12) | MEDIUM | YES for pre-policy evidence; no post-policy demand measurement |
| **Income -> Differential Access** (DAG 2) | NBS Income (#9), CIEFR-HS income quintiles (#2) | MEDIUM | PARTIALLY -- macro urban/rural split available; no post-policy quintile data |
| **Policy -> School Service Expansion** (DAG 3) | Policy Timeline (#5) | LOW | NO direct data on school service expansion or associated fees |
| **In-School Costs Dominance** (DAG 3) | CIEFR-HS (#2) | MEDIUM | YES for pre-policy composition (73% finding); no post-policy verification |
| **Public Spending -> Crowding-In** (DAG 3) | Public Education Expenditure (#7), NBS proxy (#1), Literature (#12) | MEDIUM | YES at macro level -- can test correlation between public and household spending trends |
| **COVID Confounder** (all DAGs) | NBS proxy (#1, #8), Demographics (#6) | HIGH | YES -- 2020 COVID dip clearly visible; can control for pandemic timing |
| **Demographic Confounder** (all DAGs) | Demographics (#6), World Bank (#3) | HIGH | YES -- declining births well-documented; enrollment data available |

### Temporal Alignment

| Dataset | Pre-Policy (2016-2021) | Post-Policy (2021-2025) | Overlap Quality |
|---------|----------------------|------------------------|-----------------|
| NBS Education Expenditure | 2016-2021 (6 years) | 2021-2025 (5 years) | GOOD -- full pre-post coverage |
| CIEFR-HS | 2017, 2019 only | NONE | POOR -- pre-policy only |
| World Bank | 2010-2021 | 2022-2024 (partial, sparse) | POOR for education indicators |
| Tutoring Industry | 2020 | 2021-2024 | GOOD for post-policy; minimal pre-policy |
| Demographics | 2016-2021 | 2022-2024 | GOOD |
| Public Expenditure | 2016-2021 | 2022-2023 | ADEQUATE -- missing 2024-2025 |
| NBS Consumption Categories | 2019-2021 | 2022-2025 | GOOD |
| NBS Income | 2016-2021 | 2022-2025 | GOOD |
| Underground Tutoring | NONE | 2021-2024 | N/A -- post-policy only by definition |
| CPI Deflator | 2016-2021 | 2022-2025 | GOOD -- full pre-post coverage, enables real spending analysis |

**Overall temporal alignment:** The NBS datasets (#1, #8, #9) provide the backbone for pre-post comparison with good temporal coverage. The critical CIEFR-HS decomposition data is pre-policy only, creating a structural inability to verify post-policy compositional shifts.

### Granularity Alignment

| Analysis Requirement | Available Granularity | Assessment |
|---------------------|----------------------|------------|
| Household-level spending decomposition | National/urban/rural aggregates only | **INSUFFICIENT** -- cannot do household-level analysis |
| Income-stratified effects | Urban/rural split (NBS), income quintiles (CIEFR-HS, pre-policy only) | **MARGINAL** -- urban/rural is a coarse proxy for income |
| Provincial variation | National only for all datasets | **INSUFFICIENT** -- cannot exploit geographic variation |
| Annual time series | Annual for most datasets | **ADEQUATE** for interrupted time series design |
| Pre-post comparison | 5-6 years pre, 4-5 years post (NBS) | **ADEQUATE** for trend analysis |

---

## Warnings for Downstream Agents

The following constraints are BINDING on all downstream phases. Violations of these constraints constitute Category A review findings.

1. **PROXY WARNING:** The primary outcome variable is NBS "education, culture and recreation," NOT pure education spending. Every figure, table, and conclusion using this variable MUST label it as a proxy and note that it includes non-education spending (culture, recreation, tourism). Post-COVID culture/recreation recovery likely inflates the series relative to education alone.

2. **NO POST-POLICY MICRODATA:** No household-level education spending decomposition exists for the post-policy period. Conclusions about spending composition changes (tutoring vs. in-school vs. other) after July 2021 are INFERRED from macro trends and pre-policy composition, not directly observed.

3. **UNDERGROUND TUTORING IS ANECDOTAL:** Underground tutoring price and participation data comes from media reports with severe selection bias. Do not cite specific price figures as representative. Do not estimate underground market size. Limit claims to: "Evidence suggests underground tutoring emerged with higher per-unit costs, but the scale is not measurable with available data."

4. **COVID-19 CONFOUNDING IS MANDATORY TO ADDRESS:** The 2020 spending dip and 2021 rebound are clearly COVID-driven, not policy-driven. Any pre-post analysis that does not explicitly model COVID as a confounder is invalid. The policy (July 2021) overlaps with China's COVID recovery period, making clean causal attribution extremely difficult.

5. **DEMOGRAPHIC DECLINE CONFOUNDING:** Births fell 47% from 2016 to 2024. Aggregate education spending trends must be normalized by relevant population (per child or per enrolled student, not just per capita total population). Failure to do so will conflate demographic decline with policy effects.

6. **NO PRECISE QUANTITATIVE CLAIMS:** Given the proxy variable, absence of microdata, and multiple confounders, this analysis CANNOT produce precise quantitative estimates (e.g., "the policy reduced education spending by X%"). Conclusions must be framed as directional findings with explicit uncertainty: "The available evidence suggests..." or "Under the assumption that the NBS proxy tracks education spending, the data is consistent with..."

7. **PRE-EXISTING DOWNWARD TREND:** CIEFR-HS data shows total education expenditure per student was ALREADY declining before the policy (10,372 yuan in 2017 to 6,090 yuan in 2019). Any post-policy decline may be a continuation of this pre-existing trend rather than a policy effect. This must be tested with trend-break analysis.

8. **BACK-CALCULATED DATA (2016-2018):** NBS expenditure data for 2016-2018 was back-calculated from YoY growth rates, introducing approximation error of +/- 2-3%. Statistical tests relying on these early years should report sensitivity to this uncertainty.

9. **CPI DEFLATION IS MANDATORY:** All spending comparisons across years MUST use real (CPI-deflated) values, not nominal values. Over the 2016-2025 analysis window, cumulative overall CPI inflation is 15.3% and education-category inflation is 16.8% (Dataset #13, ds_013). Nominal spending growth that does not exceed these thresholds represents real spending decline. Use the education-specific deflator (CPI Education, Culture and Recreation sub-index) for education spending series and the overall CPI deflator for income and cross-category comparisons. Any downstream artifact presenting nominal spending trends without CPI adjustment is invalid.

---

## Open Issues

1. **CFPS post-2021 data availability:** The most impactful improvement to this analysis would be obtaining CFPS microdata for 2022+ waves. If a formal application to Peking University ISSS is feasible during this analysis, it should be attempted as a data callback.

2. **NBS education-only breakdown:** NBS may publish education spending separately from culture/recreation in some subnational statistical yearbooks or supplementary releases. A targeted search for provincial-level education-only spending data could improve the proxy quality.

3. **CIEFR-HS Wave 3 publication timeline:** The 3rd CIEFR-HS wave (2021-2022) has been conducted but not published. Monitoring for its release would be high-value for a future iteration of this analysis.

4. **CPI deflator for real spending:** **RESOLVED.** NBS CPI data (overall and education sub-index, 2016-2025) has been acquired as Dataset #13 (ds_013). Deflators are available in `data/processed/nbs_cpi_deflator.parquet`. Cumulative overall inflation is 15.3% and education-category inflation is 16.8% over the analysis window. CPI deflation is now a binding constraint (Warning #9).

5. **Suspicious completeness in NBS data:** The 0% missing rate across all NBS datasets is consistent with careful data compilation but should prompt awareness that these are official statistics from an authoritarian government with incentives to present complete and favorable data. Sensitivity analysis should consider whether the smooth trends in NBS data may mask volatility visible in microdata.

---

## Code Reference

- Assessment script: `phase0_discovery/scripts/quality_assessment.py`
- Data acquisition scripts: `phase0_discovery/scripts/acquire_data.py`, `phase0_discovery/scripts/extract_ciefr_tables.py`, `phase0_discovery/scripts/acquire_supplementary.py`, `phase0_discovery/scripts/acquire_cpi_data.py`
- Processed data directory: `phase0_discovery/data/processed/`
- Registry: `phase0_discovery/data/registry.yaml`
