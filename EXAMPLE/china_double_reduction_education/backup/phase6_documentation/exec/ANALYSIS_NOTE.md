---
title: "Did China's Double Reduction Policy Truly Reduce Household Education Expenditure?"
subtitle: "An OpenPE First-Principles Analysis"
date: 2026-03-29
---

# Executive Summary

China's Double Reduction (*shuangjian*) policy, issued July 2021, banned for-profit academic tutoring for compulsory-education students with the stated goal of reducing family education burden. This analysis asks whether the policy achieved its expenditure-reduction goal. The answer, grounded in macro-level aggregate data and constrained by the absence of post-policy household microdata, is that **the policy's effect on total household education expenditure is not distinguishable from the concurrent effects of COVID-19 disruption and demographic decline** (CORRELATION classification; all chain-level Joint EP values below the 0.05 hard truncation threshold).

The primary quantitative result is an Interrupted Time Series (ITS) level shift of **-483 yuan** (real 2015 terms) in the NBS "education, culture and recreation" proxy, with total uncertainty of $\pm 284$ yuan ($1.7\sigma$ significance when systematic uncertainties are included). Three pieces of evidence undermine the attribution of this shift to the policy: (1) a COVID-date placebo test produces a larger and more significant break at 2020 than the policy break at 2021; (2) normalizing by the declining number of births eliminates the signal entirely ($p = 0.48$); and (3) the observed **23.7%** aggregate decline exceeds the **12%** compositional ceiling implied by the pre-policy share of tutoring in total education spending, meaning the policy cannot be the sole cause even if its effect were real.

The analysis constructed and evaluated three competing causal DAGs: (1) direct reduction through supply destruction, (2) regulatory displacement through underground migration and substitution, and (3) compositional irrelevance because the policy targeted only 12% of total education spending. The data are most consistent with DAGs 2 and 3 -- the formal tutoring industry collapsed (92--96% closure rate, well-documented), but this supply-side destruction did not translate into a detectable reduction in per-child household education spending. Forward projection is fork-dependent, with a useful horizon of 2029; demographic decline ($-6\%$/year births) is the dominant driver, ranking first in sensitivity with more than twice the impact of income growth and four times the impact of policy persistence. The single most valuable future data acquisition would be post-2021 household microdata (CFPS or CIEFR-HS Wave 3) to resolve the per-child spending question.

# First Principles and Causal Framework {#sec:principles}

## Domain Identification

This analysis spans education policy, public economics, and behavioral economics. The primary domain is **education policy evaluation** -- assessing whether a specific regulatory intervention achieved its stated outcome. The secondary domain is **behavioral economics of household decision-making under regulation**, because the policy's effectiveness depends on whether families redirect spending or genuinely reduce it.

## First Principles

Four first principles ground the causal reasoning [@zhang2020shadow; @park2016shadow; @liu2025crowdingin].

**Principle 1: Demand Inelasticity Under Status Competition.** When education is a positional good used for social stratification, demand for educational investment is highly inelastic with respect to regulatory supply restrictions. China's *gaokao* system creates intense zero-sum competition; banning one channel of investment redirects spending rather than eliminating it (DOMAIN-SPECIFIC).

**Principle 2: Regulatory Displacement (The Balloon Effect).** When regulation suppresses a market without eliminating underlying demand, the activity migrates to unregulated channels, often at higher cost and lower quality. Reports of approximately 3,000 illegal tutoring operations detected in Q2 2022 alone support this mechanism [@sixthtone2022crackdown] (UNIVERSAL).

**Principle 3: Compositional Fallacy in Policy Evaluation.** A policy can reduce a specific subcategory of expenditure while failing to reduce the aggregate, if spending shifts across categories. Off-campus tutoring represented only approximately **12%** of total household education expenditure pre-policy; in-school expenses constituted approximately **73%** [@wei2024household] (UNIVERSAL).

**Principle 4: Implementation Fidelity Gradient.** The actual effect of a centrally mandated policy attenuates through layers of government, with local conditions modulating enforcement. Tier-1 cities likely enforced more strictly than smaller cities or rural areas (CONTEXT-DEPENDENT).

## Competing Causal DAGs

Three competing causal structures were constructed in Phase 0 and refined through the analysis. Figure @fig:its-primary shows the ITS model results that tested the primary edge.

**DAG 1 -- Policy Success: Direct Reduction Through Supply Destruction.** The policy destroyed the formal tutoring industry, translating into genuine household savings. Testable prediction: total education expenditure declines 5--15% post-policy relative to counterfactual. Kill condition: total expenditure flat or rising despite formal tutoring decline.

**DAG 2 -- Regulatory Displacement: Substitution and Underground Migration.** The policy destroyed visible tutoring but spending migrated underground at higher prices. Testable prediction: total expenditure unchanged; composition shifts. Kill condition: total expenditure declines by the full amount of formal tutoring reduction (no substitution).

**DAG 3 -- Compositional Shift: In-School Cost Crowding-In.** The policy targeted only 12% of education spending. In-school costs (73%) were unaffected, and public spending has a documented crowding-in effect on household spending [@liu2025crowdingin]. Testable prediction: small or zero decline in total expenditure. Kill condition: total expenditure declines substantially more than the tutoring component.

The primary EP-bearing edges and their Phase 3 classifications are shown in @tbl:ep-summary.

| Edge | Classification | Phase 3 EP | Evidence |
|:-----|:--------------|----------:|:---------|
| Policy $\to$ Industry Collapse | CORRELATION | 0.56 | 92--96% offline center closure rate; literature-based |
| Competitive Pressure $\to$ Inelastic Demand | CORRELATION | 0.42 | Pre-policy evidence from education economics |
| Income $\to$ Differential Access | CORRELATION | 0.42 | Urban shift 3.7$\times$ larger than rural |
| Policy $\to$ Aggregate Spending (net) | CORRELATION | 0.20 | ITS: $-483$ yuan, 1.7$\sigma$ with systematics |
| Industry Collapse $\to$ Reduced Tutoring | CORRELATION | 0.15 | Education share dropped 0.7 pp; $z = -1.05$ |
| Policy $\to$ Underground Market | HYPOTHESIZED | 0.14 | Anecdotal; LOW data quality |
| Public Spending $\to$ Crowding-In | HYPOTHESIZED | 0.12 | Macro correlation only |
| Underground $\to$ Higher Prices | HYPOTHESIZED | 0.08 | Media reports of 43--50% increases |
| Reduced Tutoring $\to$ Total Expenditure | HYPOTHESIZED | 0.02 | Eliminated by per-birth normalization |

Table: EP summary for all tested causal edges, ordered by Phase 3 EP. No edge achieved DATA_SUPPORTED classification. All multi-step chain Joint EP values fall below the 0.05 hard truncation threshold. {#tbl:ep-summary}

## Formal Downscoping

All seven multi-step causal chains produce Joint EP values below the hard truncation threshold of 0.05. The highest is DAG 2's demand chain at 0.08. This structural result -- driven by the proxy outcome variable, MEDIUM/LOW data quality, and multiplicative EP decay through chains -- led to a formal downscoping from chain-level causal claims to edge-level assessment. The analysis tests whether observable data are *consistent with* proposed mechanisms, without claiming the full causal chain from policy to total expenditure change has been established.

# Data Sources and Quality {#sec:data}

## Data Portfolio

The analysis draws on 13 acquired datasets, summarized in @tbl:data-sources. Six additional datasets failed acquisition, most critically the CFPS post-2021 microdata and CIEFR-HS Wave 3 [@nbs2025communique; @worldbank2024wdi; @wei2024household].

| ID | Dataset | Quality | Years | Role |
|:---|:--------|:--------|------:|:-----|
| ds\_001 | NBS Education/Culture/Recreation Expenditure | MEDIUM (68) | 2016--2025 | Primary outcome (proxy) |
| ds\_002 | CIEFR-HS Spending Decomposition | MEDIUM (58) | 2017, 2019 | Pre-policy composition |
| ds\_004 | Tutoring Industry Collapse Indicators | MEDIUM (53) | 2020--2024 | Supply-side evidence |
| ds\_006 | China Demographics and Enrollment | MEDIUM (78) | 2016--2024 | Demographic confounder |
| ds\_007 | Public Education Expenditure | MEDIUM (75) | 2016--2023 | Crowding-in test |
| ds\_008 | NBS 8-Category Consumption | MEDIUM (70) | 2019--2025 | Compositional analysis |
| ds\_009 | NBS Disposable Income | HIGH (81) | 2016--2025 | Income control |
| ds\_011 | Underground Tutoring Prices | LOW (33) | 2021--2024 | Anecdotal evidence |
| ds\_013 | NBS CPI Deflator | MEDIUM (75) | 2016--2025 | Real value conversion |

Table: Key datasets with overall quality scores and analytical roles. Quality scores are the simple average of completeness, consistency, bias, and granularity dimensions (0--100 scale). {#tbl:data-sources}

## Binding Data Quality Constraints {#sec:constraints}

Nine constraints from Phase 0 propagated through all downstream phases. Violations of these constraints constitute analytical errors:

1. **PROXY WARNING.** The primary outcome is NBS "education, culture and recreation," not pure education spending. Post-COVID recovery in culture and recreation inflates the series.
2. **NO POST-POLICY MICRODATA.** No household-level education spending decomposition exists for the post-policy period.
3. **UNDERGROUND TUTORING IS ANECDOTAL.** No quantitative underground market sizing is supportable.
4. **COVID-19 CONFOUNDING IS MANDATORY TO ADDRESS.** The 2020 dip ($-19.1\%$) and 2021 rebound ($+27.9\%$) overlap temporally with the policy.
5. **DEMOGRAPHIC DECLINE CONFOUNDING.** Births fell **47%** from 17.86 million (2016) to 9.54 million (2024).
6. **NO PRECISE QUANTITATIVE CLAIMS.** Conclusions must be directional with explicit uncertainty.
7. **PRE-EXISTING DOWNWARD TREND.** CIEFR-HS shows per-student spending was already declining pre-policy (10,372 to 6,090 yuan, 2017--2019).
8. **BACK-CALCULATED 2016--2018 DATA.** Approximately $\pm 2\text{--}3\%$ error from reverse-engineering YoY growth rates.
9. **CPI DEFLATION IS MANDATORY.** Cumulative overall CPI inflation of 15.3% and education-category inflation of 16.8% over 2016--2025.

# Analysis Methods and Results {#sec:analysis}

## Exploratory Findings

CPI-deflated real per capita education/culture/recreation spending shows no sustained post-policy decline. Figure @fig:real-edu-ts displays the national, urban, and rural trajectories. The 2022 dip ($-5.0\%$ nominal) is the only candidate policy signal, but 2022 was also the peak of China's zero-COVID enforcement (Shanghai lockdown), and the 8-category compositional analysis reveals no unique behavior for the education category relative to other consumption categories.

![CPI-deflated real per capita education/culture/recreation expenditure (2015 yuan) by area. National (blue), urban (red), rural (green). Vertical dashed line marks the July 2021 Double Reduction policy. Orange band highlights COVID disruption (2020--2021). Urban spending shows the deepest COVID dip and strongest recovery, with a secondary 2022 dip potentially reflecting policy effects or continued lockdown disruption. By 2023--2025, all series exceed pre-policy levels.](figures/fig01_real_education_expenditure_timeseries.pdf){#fig:real-edu-ts width=90%}

The pre-policy spending composition is the most important structural finding. Figure @fig:ciefr-decomp shows that tutoring and extracurricular spending constituted only approximately **12%** of total household education expenditure in 2019. Even complete elimination of this component with zero substitution would reduce total spending by at most 12% -- less than the COVID-induced dip.

![Pre-policy (2019) decomposition of household education spending from the CIEFR-HS survey: in-school expenses 73%, extracurricular and tutoring 12%, other education expenses 15%. This structural constraint means the Double Reduction policy targeted at most 12% of total household education costs.](figures/fig08_ciefr_spending_decomposition.pdf){#fig:ciefr-decomp width=70%}

The tutoring industry collapse is the best-documented aspect of the policy. Closure rates of 92--96% for offline tutoring centers and revenue declines of 50--70% for major firms (New Oriental, TAL Education) are documented across multiple sources [@huang2025biting; @chen2025bans]. Figure @fig:tutoring-collapse illustrates the magnitude of the supply-side destruction.

![Panel (a): Revenue of New Oriental and TAL Education (billion USD), showing sharp declines in FY2022. Panel (b): Tutoring center closures and industry metrics showing 92--96% offline closure rates. The supply-side collapse is unambiguous, but does not directly measure household spending changes.](figures/fig07_tutoring_industry_collapse.pdf){#fig:tutoring-collapse width=90%}

Per-child normalized spending is rising sharply due to the 47% decline in births, as shown in Figure @fig:per-child. This demographic confound means that even if aggregate spending were flat, per-child spending intensity would appear to increase.

![Panel (a): Annual births (declining from 17.9 million in 2016 to 9.0 million in 2024) and compulsory education enrollment (stable at approximately 157--161 million). Panel (b): Per-birth spending intensity shows a strong upward trend driven by demographic decline -- fewer children means higher per-capita education spending intensity even if per-household spending is flat.](figures/fig06_per_child_spending.pdf){#fig:per-child width=90%}

## ITS Model Specification

The primary model is a 3-parameter segmented regression:

$$Y_t = \beta_0 + \beta_1 \cdot t + \beta_2 \cdot \mathbb{1}(t \ge 2021) + \varepsilon_t$$ {#eq:its}

where $Y_t$ is real per capita education/culture/recreation spending in 2015 yuan, $t$ is a linear time index, and $\mathbb{1}(t \ge 2021)$ is the post-policy indicator. Year 2020 is excluded from estimation to avoid COVID contamination, yielding 9 observations (2016--2019, 2021--2025) with 6 degrees of freedom. The parameter of interest is $\beta_2$ (level shift).

A secondary OLS income-conditioned counterfactual regresses real spending on real disposable income in the pre-policy period and projects the relationship forward. Both methods are OLS-based, providing limited independent corroboration.

## ITS Results

Figure @fig:its-primary presents the ITS model fit with pre-policy trend extrapolation (counterfactual) and observed post-policy values. The level shift estimates and their uncertainties are reported in @tbl:its-results.

![Interrupted Time Series results for national, urban, and rural real education/culture/recreation spending. Solid lines show observed data; dashed lines show the pre-policy trend extrapolation (counterfactual). Shaded regions indicate the post-policy gap. The urban series shows the largest gap, consistent with higher pre-policy urban tutoring participation.](figures/fig_p3_02_its_primary.pdf){#fig:its-primary width=90%}

| Series | Level shift [yuan] | Stat. unc. | Syst. unc. | Total unc. | Significance | Classification |
|:-------|-------------------:|-----------:|-----------:|-----------:|:-------------|:--------------|
| National | $-483$ | $\pm 127$ | $\pm 254$ | $\pm 284$ | 1.7$\sigma$ | CORRELATION |
| Urban | $-711$ | $\pm 197$ | $\pm 346$ | $\pm 398$ | 1.8$\sigma$ | CORRELATION |
| Rural | $-191$ | $\pm 58$ | $\pm 128$ | $\pm 141$ | 1.4$\sigma$ | CORRELATION |

Table: ITS level shift estimates with full uncertainty decomposition. All series show effects below the conventional 2$\sigma$ significance threshold when systematic uncertainties are included. Systematic uncertainty dominates (76--83% of total variance). {#tbl:its-results}

The OLS income-conditioned counterfactual yields a national mean post-period effect of **-382 yuan** ($-18.8\%$; 90% CI: $[-686, -73]$), 21% smaller than ITS, with urban and rural effects directionally consistent. Method agreement is within the 50% threshold, but both methods are OLS-based, limiting independent corroboration.

## Refutation Battery

Each series underwent four refutation tests (three core, one supplementary). Results for the national series are summarized in @tbl:refutation. Figure @fig:refutation visualizes the refutation test outcomes.

| Test | Result | Details |
|:-----|:-------|:--------|
| Placebo treatment (2017, 2018, 2019) | PASS | Max placebo: 41 yuan ($p = 0.83$). True effect 11.8$\times$ larger. |
| Random common cause (200 iterations) | PASS | Mean shift: $-486$ yuan (0.6% change). Power caveat at $n = 9$. |
| Data subset (drop 2 of 9, 200 iterations) | PASS | Mean shift: $-501$ yuan (3.8% deviation). 100% same sign. |
| COVID-date placebo (intervention at 2020) | **FAIL** | Break at 2020: $-591$ yuan ($p = 0.002$), larger than policy break. |

Table: Refutation battery results for national series. Three core tests pass, but the supplementary COVID-date placebo reveals the dominant confound. Permutation $p$-value = 0.14 (2021 break not uniquely the largest). {#tbl:refutation}

![Refutation test results: placebo treatment estimates (left), data subset stability (center), and COVID-date placebo comparison (right). The COVID-date placebo break at 2020 ($-591$ yuan, $p = 0.002$) exceeds the policy break at 2021 ($-483$ yuan, $p = 0.023$), indicating COVID disruption is the dominant signal.](figures/fig_p3_07_refutation.pdf){#fig:refutation width=90%}

The 3/3 core PASS result would normally support DATA_SUPPORTED classification. However, the COVID-date placebo FAIL provides strong evidence that the level shift is not uniquely attributable to the policy, downgrading the classification to **CORRELATION**.

## Per-Birth Normalization: The Critical Test

Normalizing aggregate spending by the declining number of births eliminates the ITS level shift entirely: the per-birth level shift is **+13 yuan** ($p = 0.48$). This result implies that the aggregate decline is fully accounted for by demographic decline -- fewer children entering the education system, not lower spending per child. This is the single most important finding of the analysis (DATA_SUPPORTED for the demographic explanation).

## Compositional Ceiling Inconsistency

The observed aggregate decline of **23.7%** substantially exceeds the **12%** compositional ceiling implied by the CIEFR-HS data. If tutoring represents only 12% of total education spending, even complete elimination with zero substitution could reduce the proxy by at most 12%. The observed 24% decline therefore cannot be solely policy-driven -- at least half must originate from COVID disruption, demographic decline, or macroeconomic deceleration. This arithmetic inconsistency independently reinforces the CORRELATION classification.

## Uncertainty Decomposition

Systematic uncertainty dominates (80% of total variance), as shown in @tbl:uncertainty. COVID handling specification alone accounts for **60.9%** of the national-level variance. More time series observations will not materially improve precision; the binding constraint is data quality.

| Source | Type | $\pm$ Shift [yuan] | Variance fraction |
|:-------|:-----|--------------------:|------------------:|
| COVID handling specification | Systematic | 221 | 60.9% |
| Statistical (bootstrap, 2000 reps) | Statistical | 127 | 20.1% |
| Intervention date (2021 vs. 2022) | Systematic | 96 | 11.3% |
| Proxy variable (education share 60--85%) | Systematic | 60 | 4.5% |
| Method disagreement (ITS vs. OLS) | Systematic | 51 | 3.2% |
| Pre-period window definition | Systematic | 8 | 0.1% |
| CPI deflator choice | Systematic | 7 | 0.1% |

Table: Uncertainty breakdown for the national ITS level shift estimate ($-483$ yuan). COVID handling is the dominant uncertainty source. Systematic uncertainty constitutes 80% of total variance. {#tbl:uncertainty}

## Urban-Rural Differential

The urban ITS level shift ($-711$ yuan) is **3.7 times** larger than the rural shift ($-191$ yuan), directionally consistent with differential exposure: urban tutoring participation was approximately 47% versus 18% rural pre-policy [@wei2024household]. However, the parallel trends assumption is violated (urban CAGR $-0.31\%$ versus rural $+3.36\%$ over 2016--2020), so this comparison is descriptive only, not quasi-causal. Figure @fig:urban-rural shows the urban-rural divergence patterns.

![Panel (a): Urban and rural real spending indexed to 2019=100. Urban fell to 76 (2020) and rural to 88 (2020); both recovered, but urban shows a post-policy dip in 2022 that rural does not. Panel (b): The absolute urban-rural gap widens post-policy. The divergence is consistent with differential exposure but cannot be interpreted causally due to violated parallel trends.](figures/fig10_urban_rural_divergence.pdf){#fig:urban-rural width=90%}

## Compositional Analysis

The education/culture/recreation share of total consumption dropped 0.7 percentage points from 2019 (11.7%) to the post-policy average (11.0%), but recovered to 11.8% by 2025. The $z$-score of education's change relative to other categories is $-1.05$, indicating it was not uniquely affected. No evidence of a compositional structural break specific to education was found.

## Model Diagnostics

The ITS model passes standard diagnostics: Durbin-Watson statistics near 2 (no significant autocorrelation), Shapiro-Wilk $p > 0.36$ (normality not rejected), Breusch-Pagan $p > 0.07$ (no significant heteroscedasticity), and $R^2 > 0.89$ for all series. Signal injection tests confirm model validity -- all injected signals recovered within 2$\sigma$. However, with only 9 observations and 3 parameters, these diagnostics have very low statistical power.

## DAG Discrimination

The aggregate data cannot distinguish DAG 2 (displacement) from DAG 3 (compositional irrelevance) because both predict small or zero decline in total spending. The data are inconsistent with DAG 1 (direct reduction) for two reasons: (1) the per-birth normalization null result, and (2) the compositional ceiling inconsistency. The results are most consistent with a combination of DAGs 2 and 3: the formal tutoring industry collapsed, but the policy's scope was too narrow (12% of spending) and substitution effects too strong to produce a detectable reduction in total per-child education expenditure. This finding aligns with @chen2025bans, who documented declining tutoring spending offset by increased in-school spending in household-level data.

# Forward Projection {#sec:projection}

## Scenario Design

Three scenarios propagate from the 2025 observed base value (2,986 yuan, real 2015 terms) using Monte Carlo simulation (10,000 iterations, seed 42). The scenarios differ primarily in assumptions about policy persistence and demographic decline rate. Figure @fig:scenarios shows the projected trajectories.

**Scenario A -- "Policy Succeeds" (15--25% conditional probability).** The policy effect is real and persists. Combined with steep demographic decline ($-7\%$/year births), spending declines to a median of **2,391 yuan by 2035** ($-20\%$, CAGR $-2.2\%$). This scenario is unlikely because it requires the aggregate signal to be predominantly policy-driven despite COVID confounding evidence.

**Scenario B -- "Status Quo / Displacement" (45--55% conditional probability).** Spending displaced to underground channels and in-school costs. Net spending approximately flat: median **3,108 yuan by 2035** ($+4\%$, CAGR $+0.4\%$). Most probable scenario, consistent with @chen2025bans and the per-birth normalization null result.

**Scenario C -- "Rebound" (25--35% conditional probability).** Enforcement weakens, competitive pressure reasserts. Spending returns to growth: median **3,580 yuan by 2035** ($+20\%$, CAGR $+1.8\%$). Consistent with the 2025 observed recovery (education share 11.8%, exceeding pre-policy 11.7%).

![Three-scenario projection of real per capita education/culture/recreation spending from 2025 to 2035, with 50% and 90% confidence intervals. Historical data shown for context. All scenarios project spending well below the ITS counterfactual (dashed line) because the pre-policy linear trend assumption is contradicted by demographic decline. Confidence bands widen substantially beyond 2029, the useful projection horizon.](figures/scenario_comparison.pdf){#fig:scenarios width=90%}

| Metric | A: Policy Succeeds | B: Status Quo | C: Rebound |
|:-------|-------------------:|--------------:|-----------:|
| 2030 median [yuan] | 2,677 | 3,137 | 3,326 |
| 2030 90% CI width [yuan] | 1,612 | 2,100 | 1,940 |
| 2035 median [yuan] | 2,391 | 3,108 | 3,580 |
| 10-year CAGR | $-2.2\%$ | $+0.4\%$ | $+1.8\%$ |
| Conditional probability | 15--25% | 45--55% | 25--35% |

Table: Scenario comparison at the 2030 and 2035 horizons. Median spread across scenarios is 649 yuan (21% of baseline median) at 2030, growing to 1,189 yuan (38%) at 2035. Within-scenario uncertainty dwarfs between-scenario divergence. {#tbl:scenarios}

## Sensitivity Analysis

Demographics dominate the projection. Figure @fig:tornado-proj shows the sensitivity tornado chart. The demographic decline rate has the largest absolute impact (**853 yuan** range at 2030), exceeding income growth (**385 yuan**) by more than $2\times$ and policy persistence (**193 yuan**) by more than $4\times$. The policy-controllable parameter ranks fourth out of six drivers.

![Sensitivity tornado chart showing the impact of each parameter on 2030 projected spending, ranked by magnitude. Demographic decline rate dominates, followed by income growth and the culture/recreation recovery proxy confound. Policy persistence ranks fourth. Color coding: blue = exogenous, orange = semi-controllable, red = controllable.](figures/sensitivity_tornado.pdf){#fig:tornado-proj width=80%}

## Endgame Classification

The endgame is classified as **Fork-dependent**. The fork condition is a single binary question: does the aggregate spending dip represent a real per-child spending reduction, or is it entirely explained by demographics and COVID? Phase 3 could not resolve this ($p = 0.48$ for per-birth normalization). The coefficient of variation across scenario medians is 0.089 at 2030 and 0.16 at 2035, with within-scenario 90% CI widths exceeding 100% of scenario medians by 2035.

## EP Decay

The primary edge (Policy $\to$ Aggregate Spending) has Phase 3 EP = 0.20 with CORRELATION classification. CORRELATION edges decay at $2\times$ the standard rate (squared multipliers). EP falls below soft truncation (0.15) by year 1 of projection and below hard truncation (0.05) by the mid-term horizon. The useful projection horizon is **2029** (4 years). Figure @fig:ep-decay shows the EP trajectory.

![EP decay chart. Left panel: projection confidence bands showing widening uncertainty from 2025 to 2035, with EP tier boundaries marked. Right panel: EP decay curve showing the primary edge EP declining from 0.20 at Phase 3 to 0.008 at the long-term horizon, crossing both soft truncation (0.15) and hard truncation (0.05) thresholds.](figures/ep_decay_chart.pdf){#fig:ep-decay width=90%}

| Projection tier | Years from 2025 | Standard multiplier | CORRELATION multiplier | Effective EP |
|:----------------|----------------:|--------------------:|-----------------------:|-------------:|
| Empirical (Phase 3) | 0 | 1.00 | 1.00 | 0.200 |
| Near-term (1--3 yr) | 1--3 | 0.70 | 0.49 | 0.098 |
| Mid-term (3--7 yr) | 3--7 | 0.40 | 0.16 | 0.032 |
| Long-term (7--10 yr) | 7--10 | 0.20 | 0.04 | 0.008 |

Table: EP decay schedule for the primary edge. CORRELATION classification applies squared multipliers, causing EP to fall below hard truncation (0.05) by the mid-term horizon. Projections beyond 2029 are explicitly speculative. {#tbl:ep-decay}

# Audit Trail and EP Summary {#sec:audit}

## Verification Summary

Phase 5 verification (5/8 programs PASS, 1/8 PARTIAL, 2/8 N/A) confirmed all quantitative results. The ITS level shift ($-483$ yuan) was reproduced exactly using an independent numpy-based OLS implementation. All 4 refutation test outcomes were independently confirmed. All EP values across all phases were verified as arithmetically correct. SHA-256 hashes matched for all 13 acquired datasets. No Category A or B issues were found.

## EP Propagation Across Phases

| Phase | EP (Policy $\to$ Aggregate Spending) | Key event |
|:------|-------------------------------------:|:----------|
| Phase 0 (Discovery) | 0.30 | Initial qualitative estimate |
| Phase 1 (Strategy) | 0.30 | Unchanged; downscoped to edge-level |
| Phase 3 (Analysis) | 0.20 | COVID placebo FAIL reduced relevance |
| Phase 4 near-term | 0.098 | CORRELATION $2\times$ decay |
| Phase 4 mid-term | 0.032 | Below hard truncation |
| Phase 4 long-term | 0.008 | Speculative |

Table: EP trajectory for the primary edge across all analysis phases. EP declines monotonically, reflecting the accumulation of evidence against a clean policy attribution. {#tbl:ep-trajectory}

## Chain-Level Joint EP

| Chain | Edges | Joint EP | Status |
|:------|:------|:---------|:-------|
| DAG 1: Policy $\to$ Industry $\to$ Tutoring $\to$ Total | $0.56 \times 0.15 \times 0.02$ | 0.0017 | HARD TRUNCATION |
| DAG 2: Policy $\to$ Underground $\to$ Prices | $0.14 \times 0.08$ | 0.011 | HARD TRUNCATION |
| DAG 3: Public $\to$ Crowding-In | 0.12 (single edge) | 0.12 | SOFT TRUNCATION |

Table: Chain-level Joint EP values. All multi-step chains fall below hard truncation (0.05), confirming that chain-level causal claims are not supportable. {#tbl:chain-ep}

## Methodology Choices

| Choice | Justification | Alternatives considered |
|:-------|:-------------|:-----------------------|
| ITS over DiD | No untreated control group; policy was nationwide | DiD requires parallel trends (violated for urban-rural) |
| 2020 exclusion over COVID indicator | Preserves degrees of freedom; algebraically identical results | COVID indicator tested as sensitivity check |
| Edge-level assessment over chain-level claims | All chain Joint EP $< 0.05$ | Chain-level claims would be epistemically dishonest |
| 3-parameter over 6-parameter ITS | 9 observations; 6-parameter model has only 3 df | 6-parameter model tested as overfitting sensitivity |
| Education CPI sub-index for deflation | Closest proxy for education cost inflation | Overall CPI tested; 1.5 pp cumulative difference |

Table: Key methodological decisions with justifications and alternatives considered. {#tbl:methods}

## Reference Analysis Comparison

| Dimension | This analysis | @huang2025biting | @chen2025bans |
|:----------|:-------------|:----------------|:-------------|
| Data | NBS macro aggregates (proxy) | City-level job postings, firm data | Nationally representative household panel |
| Method | ITS, OLS counterfactual | DiD with continuous treatment | Panel pre-post with income stratification |
| Scope | Total education expenditure | Labor market and firm dynamics | Tutoring spending, in-school spending, outcomes |
| Finding | Not distinguishable from COVID/demographics | 3M+ jobs lost; 89% posting decline | Tutoring down, in-school up; inequality effects |
| Agreement | Consistent on industry collapse; consistent on compositional shift | Consistent | Consistent; our macro results corroborate their micro findings |

Table: Comparison with reference analyses. All three analyses agree on the formal tutoring industry collapse. This analysis's macro-level finding of no detectable per-child spending reduction is consistent with @chen2025bans's micro-level finding of compositional shift. {#tbl:reference}

# Limitations and Future Work {#sec:limitations}

## Limitations

**The proxy outcome variable is the single largest source of irreducible uncertainty.** The NBS "education, culture and recreation" category bundles education with culture and recreation spending. Post-COVID recovery in non-education components (tourism, entertainment) inflates the proxy upward, potentially masking an education-specific decline. This proxy error cannot be reduced without sub-category data that NBS does not publicly release.

**No post-policy household microdata exists publicly.** The CFPS (post-2021 waves) and CIEFR-HS Wave 3 both failed acquisition. Without household-level spending decomposition, the analysis cannot verify whether the pre-policy 73/12/15 composition (in-school/tutoring/other) shifted, cannot test heterogeneous effects by income quintile, and cannot directly measure underground tutoring spending.

**COVID-19 confounding is temporally inseparable from the policy.** The policy took effect during COVID recovery; the 2020 disruption ($-19.1\%$) and 2021 rebound ($+27.9\%$) dwarf the expected policy signal (5--12%). No statistical technique can cleanly separate these with annual aggregate data.

**The analysis is limited to 10 annual observations.** Small-sample properties of all statistical tests are compromised. Bootstrap variance estimates from 4 pre-period observations are biased downward. Refutation tests (particularly random common cause) have near-zero power at $n = 9$.

**Underground tutoring is inherently unmeasurable.** Cash-based transactions, underreporting by survey respondents, and the illegality of the activity make systematic measurement impossible with available methods.

## Future Work

**Highest priority: CFPS post-2021 microdata.** This single dataset would resolve the fork variable (per-child spending trend versus demographic artifact), enable income-stratified analysis, and provide direct measurement of spending composition changes. Monitoring CFPS release schedules is the single most valuable action.

**CIEFR-HS Wave 3.** The third survey wave (2021--2022) has been conducted but not published. It would provide the first direct post-policy spending decomposition.

**Provincial NBS data.** Sub-national data that separates education from culture/recreation would eliminate the proxy confound and enable exploitation of enforcement intensity variation across regions.

**Longer time horizon.** By 2028--2029, the post-policy window will be long enough (7--8 years) to distinguish persistent policy effects from transient COVID recovery, provided demographic confounding is properly controlled.

# References {-}
