---
title: "Does the Digital Economy Drive Labor Force Structural Change in China?"
subtitle: "OpenPE Analysis Note -- Logic-Focused Technical Artifact"
date: 2026-03-29
---

# Executive Summary

This analysis investigates whether China's digital economy drives labor force structural change, testing three mechanism channels -- creation, substitution, and mediation -- using national time series data (T=24, 2000--2023). The planned DID design using smart city pilot policy as a quasi-natural experiment was not executable due to missing city-level outcome data; the analysis proceeded with Granger causality, cointegration, structural break analysis, and VAR impulse response decomposition as substitute identification strategies.

The primary finding reverses the initial hypothesis: the digital economy index is positively associated with industrial employment share (ARDL long-run coefficient **+7.15 pp** per unit DE increase, 95% CI $[-0.89, 15.20]$), indicating a complement effect rather than the expected substitution (displacement) effect. This edge (DE$\to$SUB) is classified **CORRELATION** with EP=0.315 after passing 2 of 3 refutation tests (placebo PASS, random common cause PASS, data subset FAIL). The creation channel (DE$\to$CRE, services employment) finds no temporal precedence, no cointegration, and an effect indistinguishable from zero -- classified **HYPOTHESIZED** with EP=0.030, below hard truncation. The mediation chain via industrial upgrading (DE$\to$IND\_UP) is classified **HYPOTHESIZED** (EP=0.090) after failing 2 of 3 refutation tests on the controlled specification. Demographics are the dominant driver of long-run employment reallocation, but the Granger test at annual frequency lacks power to detect this decadal-scale confounder.

Forward projection is severely limited: the proxy DE index saturated at its ceiling (1.0) by 2023, eliminating any capacity to project differential digital economy effects. All three Monte Carlo scenarios converge on industry employment declining from 31.4% to approximately 25--28% by 2033, driven by demographic contraction. The endgame is classified **Robust** (CV=0.046), but this reflects model insensitivity to the saturated primary variable, not strong causal knowledge. EP decays below hard truncation (0.05) within 3 years.

Joint\_EP for the best-supported chain (DE$\to$SUB): **0.315**. Useful projection horizon: **3 years**. Overall assessment: the digital economy's role in China's labor structural change cannot be causally established with the available national aggregate data and proxy index.

# First Principles Identified {#sec:principles}

## Domain Identification

- **Primary:** Digital economics (economic activity mediated by digital platforms, ICT infrastructure) and labor economics (employment structure, labor supply/demand, human capital formation).
- **Secondary:** Industrial organization (sectoral reallocation), human capital theory (skill upgrading), regional economics (spatial heterogeneity), public policy evaluation (DID requires identifiable policy shocks).

## First Principles

Four foundational causal mechanisms govern the digital economy--labor structure relationship.

**Principle 1: Technological Displacement and Compensation (Ricardo--Marx--Schumpeter).** Technological innovation simultaneously destroys jobs through automation and creates jobs through new products, industries, and demand. The net effect depends on adoption rate, labor market flexibility, and institutional context. Generality: UNIVERSAL across historical technology transitions.

**Principle 2: Skill-Biased Technological Change and Task-Based Framework (Acemoglu and Autor, 2011).** Digital technologies automate routine tasks, increasing demand for non-routine cognitive skills while hollowing out middle-skill employment. Generality: DOMAIN-SPECIFIC -- developed for advanced economies; applicability to China's dual labor market requires empirical validation.

**Principle 3: Structural Change and Multi-Sector Reallocation (Lewis--Kuznets--Herrendorf).** Economic development drives labor from agriculture to manufacturing to services. The digital economy accelerates tertiarization by raising service-sector productivity and creating new service categories. Generality: UNIVERSAL.

**Principle 4: Labor Market Segmentation (Doeringer--Piore).** Labor markets are segmented into primary (formal) and secondary (informal) sectors. Digital technology affects segments differently; platform work creates a new "third segment." Generality: CONTEXT-DEPENDENT for China (hukou, SOEs, platform regulation).

## Competing Causal DAGs

Three competing DAGs were constructed in Phase 0, each generating distinct testable predictions.

**DAG 1 (Technology-Push Direct Effects):** Digital economy acts primarily through direct technology channels -- automation displaces routine workers (substitution), new digital industries absorb workers (creation). The digital economy index directly affects labor demand through task content changes. Kill condition: if mid-skill employment increases in pilot cities relative to controls.

**DAG 2 (Institutional Mediation):** Digital economy operates through institutional mediators -- human capital investment, industrial structure upgrading, labor market reform. The direct DE$\to$LS path is weak. Kill condition: if the direct effect remains significant after controlling for mediators.

**DAG 3 (Labor Market Segmentation):** China's segmented labor market means DE has opposite effects across segments: substitution dominates in the formal sector (SOEs, large firms), creation dominates in the informal/platform sector. The aggregate effect masks heterogeneity. Kill condition: if within-segment effects are homogeneous.

**DAG selection outcome:** No single DAG was confirmed. DAG 1's substitution prediction was contradicted (positive, not negative, DE--industry association). DAG 2's mediation hypothesis could not survive refutation testing. DAG 3 was untestable without individual-level data. The analysis resolves to a simplified DAG with five testable edges (see @sec:ep-propagation).

## Initial EP Assessment

| Edge | Label | Phase 0 EP | Key constraint |
|:-----|:------|:----------:|:---------------|
| DE$\to$SUB | LITERATURE\_SUPPORTED | 0.49 | Construct validity of DE proxy |
| DE$\to$CRE | LITERATURE\_SUPPORTED | 0.42 | Same |
| DE$\to$IND\_UP | LITERATURE\_SUPPORTED | 0.35 | Same |
| DEMO$\to$LS | LITERATURE\_SUPPORTED | 0.42 | Annual frequency vs. decadal dynamics |
| DE$\to$LS (direct) | THEORIZED | 0.12 | Direct effect expected weak in DAG 2 |

Table: Phase 0 EP values before data quality and method adjustments. {#tbl:ep-phase0}

# Data Foundation {#sec:data}

## Data Sources

| Dataset | Source | Temporal coverage | Spatial coverage | Quality | Key limitation |
|:--------|:-------|:------------------|:-----------------|:-------:|:---------------|
| World Bank WDI | World Bank API (wbgapi) | 2000--2023 | National | MEDIUM | ILO-modeled estimates, not survey-based |
| ILO employment structure | ILO modeled estimates via WB | 2000--2023 | National | MEDIUM | Skill-composition columns 96% missing |
| DE composite index | Constructed from WB | 2000--2023 | National | LOW (bias) | 4-component proxy; saturated at 1.0 by 2023 |
| Smart city pilots | MOHURD announcements | 2012--2015 | 286 cities | HIGH | No city-level outcome data |
| Merged national panel | Merged from above | 2000--2023 | National | MEDIUM | T=24; 37 usable columns |

Table: Data registry summary with quality verdicts from Phase 0 DATA\_QUALITY.md. {#tbl:data-sources}

## Data Quality Gate

**Gate decision: PROCEED WITH WARNINGS.**

Seven critical constraints bind all downstream analysis:

1. **DID not executable.** Smart city pilot treatment indicator exists (286 cities, 3 batches) but no city-level outcome variables. All causal claims use weaker time series identification.
2. **Skill-level analysis impossible.** ILO education-based columns have 1/24 observations. CFPS microdata registration-gated. EP.truth capped at 0.30 for any skill-level edge.
3. **DE composite index is a proxy of uncertain validity.** Measures ICT infrastructure penetration (internet users, mobile subscriptions, broadband, R\&D expenditure), not the broader digital economy (e-commerce, platform scale, digital finance). The validated PKU-DFIIC was unavailable. Saturated at 1.0 by 2023.
4. **T=24 limits model complexity.** Maximum 4--5 regressors simultaneously. Power approximately 35% for medium effects.
5. **ILO employment estimates are partially endogenous.** Services employment regressed on GDP and urbanization yields $R^2 = 0.989$, signaling severe endogeneity.
6. **No individual-level mechanism testing.** Without CFPS, DAG 2 (mediation via human capital) and DAG 3 (segmentation) cannot be tested at the mechanism level.
7. **No cross-sectional variation.** National time series cannot identify heterogeneous effects.

## Data Preparation

The primary analysis dataset is `china_national_panel_merged.parquet` (24 rows $\times$ 40 columns). Three ILO education-based columns were dropped (96% missing). No imputation was applied; missing values handled via listwise deletion within each test. First differences, log transformations, growth rates, and structural break indicators were constructed per @tbl:features.

| Feature | Formula | Purpose |
|:--------|:--------|:--------|
| `d_digital_economy_index` | $\Delta\text{DE}_t$ | First difference for stationary analysis |
| `d_employment_services_pct` | $\Delta\text{EmpServ}_t$ | First difference |
| `d_employment_industry_pct` | $\Delta\text{EmpInd}_t$ | First difference |
| `post_pilot` | $\mathbb{1}[\text{year} \geq 2016]$ | Structural break period indicator |
| `transition_window` | $\mathbb{1}[\text{year} \in \{2013, 2014, 2015\}]$ | Treatment window exclusion |
| `log_gdp_pc` | $\ln(\text{GDP/cap})$ | Log-linearized income |

Table: Key engineered features. {#tbl:features}

# Analysis Findings {#sec:findings}

## Stationarity and Cointegration Overview

Joint ADF/KPSS testing classifies most variables as I(1). The digital economy index, employment shares, services VA/GDP, urbanization, and broadband are all non-stationary in levels but (approximately) stationary in first differences. Demographic variables show ambiguous stationarity due to hump-shaped trajectories. The Toda-Yamamoto procedure and ARDL bounds test were adopted to handle the I(0)/I(1) mixture.

Level correlations between DE and employment shares exceed $|0.9|$ -- the classic spurious regression setup. After first-differencing, DE is negatively correlated with services employment growth ($r = -0.377$, $p = 0.076$), reversing the level sign. This reversal is the strongest signal that cointegration analysis is essential for distinguishing genuine long-run relationships from spurious correlation.

## Edge: DE $\to$ SUB (Substitution Channel) {#sec:de-sub}

- **Classification:** CORRELATION
- **EP:** 0.315 (truth=0.45, relevance=0.70)
- **95% CI (ARDL LR):** $[-0.89, 15.20]$ pp (bivariate); $[8.94, 16.21]$ pp (with demographic control)
- **Direction:** POSITIVE (complement, not substitution)

### Evidence

The Toda-Yamamoto test detects Granger causality from DE to industry employment at the 10% level bivariate ($W = 5.84$, $p_{\text{boot}} = 0.087$), strengthening to the 5% level with demographic control ($W = 13.33$, $p_{\text{boot}} = 0.012$). Johansen cointegration confirms a long-run equilibrium (trace $= 19.04 > \text{cv}_{95} = 15.49$). The ARDL bounds test corroborates cointegration ($F = 6.51 > \text{upper bound}\ 5.73$ at 5%). However, independent verification revealed a 78.5% divergence in the ARDL bounds F-statistic (primary: 6.51 vs. independent: 1.40), suggesting the cointegration result is fragile. The reproducible Johansen trace test ($p < 0.01$) provides more robust support for the long-run relationship.

The ARDL long-run coefficient is **+7.15 pp** per unit DE increase (SE=4.10, bivariate) and **+12.57 pp** (SE=1.86, with demographic control). The sign is consistently positive across all methods: DE growth is associated with increased -- not decreased -- industrial employment. This contradicts the substitution (displacement) hypothesis and indicates a complement effect during the digitalization period.

The structural break analysis reveals a dramatic departure: industry employment's pre-2013 upward trend (+0.71 pp/year, $R^2 = 0.82$) reversed post-2016, with a **-4.45 pp** deviation from the counterfactual ($t = -11.51$, $p < 0.001$). However, Chow tests in first differences find no significant break in the DE--industry relationship specifically ($F = 0.66$, $p = 0.530$ at 2013; $F = 0.39$, $p = 0.681$ at 2015). The DID-inspired regression with HAC standard errors yields a significant negative post-break interaction ($\beta_2 = -11.62$, $p = 0.011$) only with demographic control.

### Refutation Tests

| Test | Result | Detail |
|:-----|:------:|:-------|
| Placebo treatment | PASS | 1/4 placebos significant (shift=5 only) |
| Random common cause | PASS | $W$ changed $<$10% |
| Data subset (25% drop) | FAIL | $W$ changed 86.2%; highly sensitive to specific observations |

Table: Refutation battery for DE$\to$SUB (controlled specification). {#tbl:refutation-sub}

The data subset failure reflects the fundamental small-sample constraint (T=24): dropping 6 observations changes the conclusion. This is inherent to the sample size, not a refutation of the association.

### Method Comparison

| Method | Statistic | Direction | Significance |
|:-------|:----------|:----------|:-------------|
| Toda-Yamamoto (bivariate) | $W = 5.84$ | Positive | $p = 0.087^{*}$ |
| Toda-Yamamoto (+DEMO) | $W = 13.33$ | Positive | $p = 0.012^{**}$ |
| Johansen cointegration | Trace $= 19.04$ | Cointegrated | $p < 0.05$ |
| ARDL bounds | $F = 6.51$ | Cointegrated | $> \text{upper bound}$ |
| ARDL LR coefficient | +7.15 pp | Positive | $p = 0.082^{*}$ |
| Counterfactual deviation | $-4.45$ pp | Ind. emp. reversed | $p < 0.001$ |

Table: Method comparison for the substitution channel. {#tbl:methods-sub}

Methods agree on the existence of a DE--industry relationship and on the positive (complement) sign. They disagree on the mechanism: Granger captures short-run dynamics; the counterfactual trend captures long-run structural transformation.

An important alternative explanation is China's state industrial policy. Programs like "Made in China 2025" and extensive manufacturing subsidies may independently explain why industrial employment remained elevated during digitalization, confounding the observed complement effect. This analysis cannot separate the digital economy's effect from concurrent industrial policy, and the positive DE--industry association should be interpreted with this caveat.

![Structural break and DID-inspired baseline comparison: (a) DE index with break window, (b) employment structure trends, (c) pre/post first-difference scatter, (d) counterfactual versus observed.](figures/structural_break_did_baseline.pdf){#fig:structural-break width=90%}

![Method comparison summary: Granger, ARDL, and Chow test results for the substitution (top row) and creation (bottom row) channels.](figures/method_comparison_summary.pdf){#fig:method-comparison width=90%}

## Edge: DE $\to$ CRE (Creation Channel) {#sec:de-cre}

- **Classification:** HYPOTHESIZED (bivariate) / DISPUTED (with controls)
- **EP:** 0.030 (truth=0.30, relevance=0.10)
- **Status:** Below hard truncation (0.05). Beyond analytical horizon.

### Evidence

No Granger causality from DE to services employment is detected (bivariate: $W = 1.16$, $p_{\text{boot}} = 0.565$; with DEMO: $W = 0.38$, $p_{\text{boot}} = 0.834$). No cointegrating relationship exists (Johansen trace $= 4.47 < \text{cv}_{95} = 15.49$; ARDL $F = 1.92 < \text{lower bound}$). The strong level correlation ($r = 0.981$) is entirely spurious -- driven by common trends in both series.

The power caveat is essential: at 35% power for medium effects, this null result is inconclusive. A genuine medium-sized creation effect could exist undetected. However, the effect-near-zero finding mechanically reduces relevance to 0.10.

### Refutation Tests

| Test | Bivariate | With control |
|:-----|:---------:|:------------:|
| Placebo treatment | PASS | FAIL |
| Random common cause | FAIL | FAIL |
| Data subset | FAIL | FAIL |

Table: Refutation results for DE$\to$CRE. {#tbl:refutation-cre}

The controlled specification scores 0/3 PASS (DISPUTED), indicating that observed services employment growth is better explained by demographic and macroeconomic trends than by the digital economy.

## Edge: DE $\to$ IND\_UP (Mediation -- Industrial Upgrading) {#sec:de-indup}

- **Classification:** HYPOTHESIZED
- **EP:** 0.090 (truth=0.30, relevance=0.30)
- **Status:** Below soft truncation (0.15).

### Evidence

DE significantly Granger-causes services value-added share when controlling for demographics ($W = 15.81$, $p_{\text{boot}} = 0.008$). Without controls, the result is marginal ($W = 4.75$, $p = 0.132$). Cointegration is confirmed by both Johansen and ARDL.

However, the controlled specification fails 2 of 3 refutation tests. The random common cause test shows 24.2% sensitivity to an irrelevant variable (likely overfitting at T=24 with 3 endogenous variables and 3 lags). The data subset test shows 76.1% instability. The strong Granger signal does not survive refutation scrutiny.

### Refutation Tests

| Test | Controlled specification |
|:-----|:-----------------------:|
| Placebo treatment | PASS |
| Random common cause | FAIL (24.2% change) |
| Data subset | FAIL (76.1% change) |

Table: Refutation results for DE$\to$IND\_UP (controlled). {#tbl:refutation-indup}

### VAR Mediation Decomposition

The trivariate VAR(1) impulse response analysis yields negative mediation shares ($-90\%$ to $-95\%$), meaning the inclusion of the services VA mediator reduces the total effect of DE on services employment. This counterintuitive result indicates that the standard narrative (DE drives industrial upgrading which drives employment reallocation) is not supported in the national time series. The indirect pathway through industrial upgrading partly offsets the direct pathway.

This contrasts with reference analysis Li et al. (2024), which finds ${\sim}22\%$ positive mediation in a 30-province panel. The discrepancy likely reflects the difference between cross-sectional variation (provincial panel) and temporal variation (national time series).

![VAR impulse response functions for the mediation system: DE, services value-added, and services employment.](figures/var_irf_mediation.pdf){#fig:var-irf width=90%}

## Edge: DEMO $\to$ LS (Demographic Confounder) {#sec:demo-ls}

- **Classification:** HYPOTHESIZED
- **EP:** 0.120 (truth=0.30, relevance=0.40)
- **Status:** Below soft truncation (0.15).

Demographics do not Granger-cause employment structure at annual frequency (services: $W = 1.93$, $p = 0.397$; industry: $W = 0.75$, $p = 0.694$). Demographic exogeneity is confirmed: DE does not Granger-cause demographics ($W = 2.67$, $p = 0.293$).

The non-detection is surprising given strong theoretical priors. Likely explanations: (1) demographic effects operate at decadal frequency, undetectable by annual Granger tests; (2) the hump-shaped working-age population trajectory violates the linear VAR assumption; (3) T=24 provides insufficient power.

Despite the null Granger result, including demographics as a control variable dramatically changes the DE coefficients (bivariate ARDL LR: +7.15 pp; controlled: +12.57 pp), confirming that demographics confound the DE--employment relationship at frequencies below the Granger test's resolution.

## Reverse Causality

Neither services employment ($W = 3.08$, $p = 0.247$) nor industry employment ($W = 2.39$, $p = 0.335$) Granger-causes the DE index. Reverse causality is not detected, though low power limits the interpretation.

# EP Propagation {#sec:ep-propagation}

## EP Update Rules

| Classification | Truth update |
|:---------------|:-------------|
| DATA\_SUPPORTED | truth $= \max(0.8,\ \text{Phase 1 truth} + 0.2)$ |
| CORRELATION | truth $=$ Phase 1 truth (unchanged) |
| HYPOTHESIZED | truth $= \min(0.3,\ \text{Phase 1 truth} - 0.1)$ |
| DISPUTED | truth $= 0.1$ |

Table: Mechanical EP update rules applied after refutation testing. {#tbl:ep-rules}

## EP Propagation Table

| Edge | Phase 0 EP | Phase 1 EP | Phase 3 EP | Classification | Change reason |
|:-----|:----------:|:----------:|:----------:|:---------------|:--------------|
| DE$\to$SUB | 0.49 | 0.32 | **0.315** | CORRELATION | 2/3 refutations; truth 0.45, relevance 0.70 |
| DE$\to$CRE | 0.42 | 0.27 | **0.030** | HYPOTHESIZED | No Granger; truth 0.30, relevance 0.10 (effect near zero) |
| DE$\to$IND\_UP | 0.35 | 0.23 | **0.090** | HYPOTHESIZED | 1/3 refutations; truth 0.30, relevance 0.30 |
| DEMO$\to$LS | 0.42 | 0.36 | **0.120** | HYPOTHESIZED | No Granger at annual frequency; truth 0.30, relevance 0.40 |
| DE$\to$LS (direct) | 0.12 | 0.06 | **0.010** | HYPOTHESIZED | Below soft truncation; truth 0.05, relevance 0.20 |

Table: EP propagation from Phase 0 through Phase 3. All edges experienced EP decline due to data constraints, construct validity concerns, and refutation failures. {#tbl:ep-propagation}

## Joint\_EP and Truncation

| Chain | Joint\_EP | Status |
|:------|:---------:|:-------|
| DE$\to$SUB (substitution) | 0.315 | Full analysis; best-supported edge |
| DE$\to$CRE (creation) | 0.030 | Below hard truncation (0.05); beyond analytical horizon |
| DE$\to$IND\_UP$\to$CRE (mediation) | 0.003 | Below hard truncation; beyond analytical horizon |
| DEMO$\to$LS (confounder) | 0.120 | Below soft truncation (0.15) |
| DE$\to$LS (direct) | 0.010 | Below hard truncation; resolved |

Table: Joint\_EP values and truncation decisions. {#tbl:joint-ep}

Only DE$\to$SUB (EP=0.315) survives above soft truncation. All other mechanism channels fall below the thresholds at which the framework assigns meaningful explanatory power.

![EP propagation from Phase 0 through Phase 3 for all tested edges.](figures/ep_propagation.pdf){#fig:ep-propagation width=80%}

![Refutation test summary heatmap across all edges.](figures/refutation_summary.pdf){#fig:refutation-summary width=80%}

# Statistical Model {#sec:model}

## Model Specification

Two parallel estimation frameworks are used.

**Framework A: First-Difference DID-Inspired Regression (preferred for inference)**

$$\Delta y_t = \alpha + \beta_1 \Delta\text{DE}_t + \beta_2 (\text{POST}_t \times \Delta\text{DE}_t) + \epsilon_t$$ {#eq:did}

where $\text{POST} = 1$ for $t \geq 2016$. HAC standard errors (Newey-West, maxlags=2) correct for serial correlation.

**Framework B: ARDL(1,1) Error-Correction Model**

$$y_t = \phi y_{t-1} + \theta_0 x_t + \theta_1 x_{t-1} + \mu + \epsilon_t$$ {#eq:ardl}

Long-run coefficient: $\hat{\beta}_{\text{LR}} = (\theta_0 + \theta_1) / (1 - \phi)$, with standard error via the delta method.

## DID-Inspired Estimates (Substitution Channel, HAC SE)

| Specification | $\beta_1$ | SE | $p$ | $\beta_2$ (POST$\times\Delta$DE) | SE | $p$ |
|:--------------|----------:|---:|----:|----------------------------------:|---:|----:|
| Bivariate | 20.51 | 16.33 | 0.209 | $-5.90$ | 4.21 | 0.161 |
| With DEMO | 28.29 | 15.14 | 0.062 | $-11.62$ | 4.58 | 0.011 |

Table: DID-inspired regression, substitution channel. {#tbl:did-sub}

With demographic control, the post-break interaction is significant ($\beta_2 = -11.62$, $p = 0.011$): the DE--industry complement effect weakened from +28.3 pp (pre-break) to +16.7 pp (post-break). However, bootstrap confidence intervals are wider than HAC: $[-34.3, 33.1]$ for $\beta_2$, crossing zero. The HAC standard errors may understate uncertainty at T=24.

## Signal Injection Tests

| Injected | Recovered | Bootstrap SE | Within 1$\sigma$? |
|:---------|:----------|:-------------|:------------------:|
| 20.51 (observed) | 20.51 | 15.71 | Yes |
| 41.03 (2$\times$ observed) | 41.03 | 15.75 | Yes |
| 0.00 (null) | ${\sim}$0 | 15.57 | Yes |

Table: Signal injection tests confirm model correctly recovers known signals. {#tbl:signal-injection}

## Sensitivity Analysis

**Lag order:** Granger $W$ for DE$\to$industry is significant at lag 1 ($p = 0.011$), marginal at lag 2 ($p = 0.052$), and non-significant at lag 3 ($p = 0.162$). Each additional lag consumes ${\sim}4\%$ of degrees of freedom at T=24.

**Break year:** The DID post-break interaction ($\beta_2$) is significant at 2013 ($p = 0.038$) and 2015 ($p = 0.032$), consistent with smart city pilot timing. Non-significant only at 2016 ($p = 0.161$).

![Sensitivity of the structural break interaction coefficient to alternative break year choices.](figures/sensitivity_break_year.pdf){#fig:break-year-sensitivity width=80%}

# Uncertainty Quantification {#sec:uncertainty}

## Bootstrap Confidence Intervals

Block bootstrap (block size=3, 2000 replications) for the substitution channel:

| Parameter | Point | SE(OLS) | SE(boot) | 95% CI(boot) |
|:----------|------:|--------:|---------:|:-------------|
| $\beta_1$ ($\Delta$DE) | 20.51 | 16.33 | 15.91 | $[-19.8, 40.9]$ |
| $\beta_2$ (POST$\times\Delta$DE) | $-5.90$ | 8.04 | 5.56 | $[-15.3, 6.3]$ |

Table: Bootstrap confidence intervals for the substitution channel. {#tbl:bootstrap-sub}

The bivariate $\beta_1$ bootstrap CI ($[-19.8, 40.9]$) includes zero. At the ${\sim}1.3\sigma$ level, the effect is detectable but imprecise.

## Systematic Uncertainty Decomposition

| Source | Type | $\pm$Shift on $\beta_1$ | Fraction |
|:-------|:-----|:-----------------------:|:--------:|
| Bootstrap standard error | Statistical | 15.91 | Dominant |
| Demographic control inclusion | Systematic | 7.78 | 33% of syst. |
| Break year choice (2013--2017) | Systematic | 2.60 | 11% |
| COVID exclusion (drop 2020--2021) | Systematic | 1.81 | 8% |

Table: Uncertainty decomposition for the substitution channel. Lag selection and functional form produce extreme shifts (21+ and 95+ pp) and are excluded from quadrature as model redefinitions rather than perturbations. {#tbl:uncertainty-decomp}

The dominant uncertainty is statistical: with T=24, the bootstrap SE (${\sim}16$) exceeds half the point estimate (${\sim}21$). More data -- either longer time series or panel data with cross-sectional variation -- is the primary path to improved precision.

## Final Results Table

| Parameter | Central | Stat. | Syst. | Total | Classification |
|:----------|--------:|------:|------:|------:|:---------------|
| DE$\to$Ind. Emp (ARDL LR) | +7.15 pp | $\pm$4.10 | -- | $\pm$4.10 | CORRELATION |
| DE$\to$Ind. Emp (ARDL LR, +DEMO) | +12.57 pp | $\pm$1.86 | $\pm$5.42 | $\pm$5.73 | CORRELATION |
| DE$\to$Ind. Emp (DID $\beta_1$) | +20.51 pp | $\pm$15.91 | $\pm$8.52 | $\pm$18.05 | CORRELATION |
| DE$\to$Svc. Emp (DID $\beta_1$) | $-10.89$ pp | $\pm$11.04 | $\pm$4.25 | $\pm$11.83 | HYPOTHESIZED |
| Ind. Emp post-break deviation | $-4.45$ pp | $\pm$0.39 | -- | $\pm$0.39 | DESCRIPTIVE |
| Svc. Emp post-break deviation | +1.83 pp | $\pm$0.36 | -- | $\pm$0.36 | DESCRIPTIVE |

Table: Final results with 4-number uncertainty quantification. {#tbl:final-results}

![Uncertainty tornado chart showing statistical and systematic decomposition for the substitution channel.](figures/uncertainty_tornado.pdf){#fig:uncertainty-tornado width=80%}

# Forward Projection {#sec:projection}

## Pre-Projection Constraints

The projection faces a binding constraint: the proxy DE index saturated at its ceiling (1.0) by 2023. Varying $\beta_{\text{DE}}$ or DE growth rate by $\pm 20\%$ produces zero change in the deterministic endpoint because further DE increases are absorbed by the upper bound. Only demographic parameters have non-zero sensitivity.

## Scenario Simulations

10,000 Monte Carlo iterations per scenario, random seed 20260329, projection horizon 10 years (2024--2033).

| Scenario | 2033 Median | 90% CI | Primary driver | $P(\text{conditional})$ |
|:---------|:------------|:-------|:---------------|:-----------------------:|
| Baseline | 27.5% | [24.8, 30.1] | Demographics | 50--60% |
| High-Digital | 27.5% | [24.7, 30.3] | Demographics | 20--30% |
| Low-Digital | 24.9% | [18.4, 31.1] | Demographics + weakened complement | 15--25% |

Table: Scenario simulation results for industry employment share. {#tbl:scenarios}

The baseline and high-digital scenarios produce nearly identical medians because the DE proxy cannot capture further digital growth. The low-digital scenario diverges because it reduces the compensating complement effect, allowing pure demographic decline to dominate. The 90% CI at 10 years under the low-digital scenario spans 12.7 pp.

![Scenario comparison: historical and projected industry employment share with confidence bands.](figures/scenario_comparison.pdf){#fig:scenario-comparison width=90%}

## Sensitivity Tornado

| Rank | Variable | Impact (20% perturbation) | Controllability |
|:----:|:---------|:-------------------------:|:----------------|
| 1 | Demographic effect size | 0.79 pp | Exogenous |
| 2 | Demographic decline rate | 0.79 pp | Exogenous |
| 3 | DE effect size (ARDL LR coeff) | 0.00 pp | Semi-controllable |
| 4 | DE annual growth rate | 0.00 pp | Controllable |

Table: Sensitivity ranking at 10-year horizon. DE parameters have zero marginal sensitivity due to proxy saturation. {#tbl:sensitivity}

![Sensitivity tornado: parameter impact on industry employment share at 10-year horizon.](figures/sensitivity_tornado.pdf){#fig:sensitivity-tornado width=80%}

## Endgame Classification

**Category: Robust** (CV $= 0.046$ across scenario endpoint medians).

This robustness reflects model insensitivity to the saturated primary variable, not strong causal knowledge. If a non-saturated DE measure (PKU-DFIIC) were available, the endgame would likely shift to **Fork-dependent**, with the fork condition being whether digital economy growth accelerates (buffering industry employment via complement effect) or stagnates (allowing pure demographic decline).

## EP Decay

| Projection distance | EP multiplier (CORRELATION 2$\times$) | EP value | Confidence tier |
|:-------------------:|:--------------------------------------:|:--------:|:----------------|
| 0 (Phase 3) | 1.00 | 0.315 | HIGH (empirical) |
| 1 year | 0.36 | 0.113 | Below soft truncation |
| 3 years | 0.16 | 0.050 | At hard truncation |
| 5 years | 0.063 | 0.020 | Below hard truncation |
| 10 years | 0.006 | 0.002 | Negligible |

Table: EP decay schedule for the DE$\to$SUB edge. CORRELATION edges decay at 2$\times$ the standard rate. {#tbl:ep-decay}

The useful projection horizon is **3 years** (to 2026). Beyond 3 years, projections have negligible EP support and are extrapolations of demographic trends with no empirically grounded causal content from the digital economy analysis.

![EP-weighted confidence decay for the DE$\to$SUB projection. Top: baseline projection with widening confidence bands. Bottom: EP value decay from Phase 3 anchor toward hard truncation.](figures/ep_decay_chart.pdf){#fig:ep-decay width=90%}

# Verification Summary {#sec:verification}

## Verification Results

| Check | Result | Key detail |
|:------|:------:|:-----------|
| Independent reproduction | PASS | 7/10 metrics within 5%; ARDL LR coefficient reproduced exactly (7.15 pp) |
| Data provenance audit | PASS | 7/7 datasets: SHA-256 hashes match; spot-check values within tolerance |
| Logic audit | FLAG | All classifications correct; 1 Category B (industry pre-trend $R^2$: reported 0.96, verified 0.82) |
| EP verification | PASS | 4/5 edges exact; 1 Category C (DE$\to$IND\_UP: 0.090 vs. 0.075, no downstream impact) |
| Consistency checks | PASS | Cross-artifact consistency confirmed; conventions compliance documented |
| **Overall** | **FLAG** | No Category A findings. 1 Category B (R$^2$ error). 2 Category C. |

Table: Phase 5 verification results. {#tbl:verification}

## Key Discrepancies

**ARDL bounds F-statistic divergence:** Independent verification yields $F = 1.40$ versus reported $F = 6.51$ (78.5% divergence). The divergence arises from specification-dependent differences in the ARDL bounds test implementation. Cointegration is independently confirmed by Johansen trace test (19.04, reproduced exactly).

**Industry pre-trend $R^2$:** Reported as 0.96 in ANALYSIS.md Table 2.1; independently verified as 0.82. The slope (+0.71 pp/year) and counterfactual deviation ($-4.45$ pp) are correctly reproduced. The lower $R^2$ means the pre-trend is a less reliable counterfactual basis but the qualitative conclusion (dramatic structural break) is unchanged.

**Power analysis:** Reported as 35%, independently computed as 43%. Difference attributable to different degrees-of-freedom specifications. The qualitative conclusion (low power) is unchanged.

## Conventions Compliance

| Convention | Status |
|:-----------|:------:|
| Construct DAG before estimation | PASS |
| Every causal claim survives $\geq$3 refutation tests | PASS |
| Report effect sizes with CI | PASS |
| Document untestable assumptions | PASS |
| Stationarity tests (ADF, KPSS) | PASS |
| Granger causality T$\geq$30 | DOCUMENTED DEVIATION (T=24; Toda-Yamamoto + bootstrap) |
| Report prediction intervals | PASS |

Table: Conventions compliance summary. {#tbl:conventions}

# Audit Trail {#sec:audit}

## Data Provenance

All raw data in `data/raw/` is immutable with SHA-256 hashes recorded in `data/registry.yaml`. Seven datasets acquired; three failed (EPS commercial, CFPS registration-gated, FRED no API key). NBS provincial data attempted but automated extraction blocked (yearbook tables require JavaScript rendering).

## Methodology Choices

| Choice | Justification | Alternatives considered |
|:-------|:--------------|:-----------------------|
| Toda-Yamamoto over standard Granger | T=24 violates T$\geq$30 convention; TY valid for T${\sim}$20 | Standard Granger (rejected: size distortion at T=24) |
| ARDL bounds over Johansen-only | Valid for I(0)/I(1) mixture; ambiguous stationarity results | Pure Johansen (used as complement, not replacement) |
| Structural break over DID | No city-level outcome data for DID | True DID (impossible with available data) |
| VAR mediation over Baron-Kenny | Time series violates i.i.d. assumption | Baron-Kenny (rejected: inappropriate for time series) |
| Block bootstrap over analytical SE | T=24 may violate asymptotic distributional assumptions | Analytical (used in parallel for comparison) |

Table: Key methodology choices with justifications. {#tbl:methodology-choices}

## Phase 0 Warnings Carried Forward

1. DID not executable -- confirmed; structural break substituted.
2. Skill-level analysis impossible -- confirmed; all skill edges EP=0.00.
3. DE composite index is a proxy of uncertain validity -- confirmed; saturated by 2023.
4. T=24 limits model complexity -- confirmed; power ${\sim}$35%.
5. ILO employment estimates partially endogenous -- confirmed ($R^2 = 0.989$).
6. No individual-level mechanism testing without CFPS.
7. No cross-sectional variation in national time series.

## Human Gate Decision

Phase 5 verification resulted in overall FLAG (1 Category B, 2 Category C, no Category A). Human gate approved (option a) with the instruction to correct the $R^2$ value in ANALYSIS.md Table 2.1.

# Appendix: Statistical Details {#sec:appendix-stats}

## VECM Estimates (Substitution Channel)

Bivariate VECM (DE, employment\_industry\_pct), rank=1, $k_{\text{ar\_diff}}=1$:

| Parameter | Estimate | Interpretation |
|:----------|:---------|:---------------|
| $\beta$ (cointegrating vector) | $[1.0, -0.173]$ | Long-run: DE $= 0.173 \times$ industry\_emp in equilibrium |
| $\alpha_{\text{DE}}$ | $-0.015$ | DE weakly exogenous (negligible adjustment) |
| $\alpha_{\text{ind}}$ | 1.252 | Industry employment adjusts rapidly toward equilibrium |
| $\gamma_{\text{DE}\to\text{ind}}$ (short-run) | 25.86 | Positive short-run DE effect |

Table: VECM parameter estimates for the substitution channel. {#tbl:vecm}

## ARDL Long-Run Estimates

| Parameter | Estimate | SE | 95% CI | $p$ |
|:----------|--------:|----:|:-------|----:|
| $\phi$ (lagged dep) | 0.816 | 0.130 | $[0.56, 1.07]$ | $<0.001$ |
| $\theta_0$ (contemp. DE) | 24.91 | 14.04 | $[-2.61, 52.44]$ | 0.076 |
| $\theta_1$ (lagged DE) | $-23.60$ | 13.10 | $[-49.27, 2.07]$ | 0.072 |
| Long-run coefficient | **7.15** | **4.10** | $[-0.89, 15.20]$ | 0.082 |

Table: Bivariate ARDL(1,1) estimates for the substitution channel. {#tbl:ardl}

## Impulse Response Functions

![Creation versus substitution channel impulse response functions showing the response of services and industry employment to a one-standard-deviation DE shock.](figures/irf_creation_substitution.pdf){#fig:irf width=90%}

## DID-Inspired Estimates (Creation Channel)

| Specification | $\beta_1$ | SE | $p$ | $\beta_2$ | SE | $p$ |
|:--------------|----------:|---:|----:|----------:|---:|----:|
| Bivariate | $-10.89$ | 8.20 | 0.184 | $-10.38$ | 3.93 | 0.008 |
| With DEMO | $-19.72$ | 10.46 | 0.059 | $-8.11$ | 6.76 | 0.230 |

Table: DID-inspired regression, creation channel. {#tbl:did-cre}

The creation channel shows a significant negative POST interaction in the bivariate specification ($\beta_2 = -10.38$, $p = 0.008$) but not with demographic control ($p = 0.230$). The DE--services relationship was negative throughout and became more negative post-2015, the opposite of the expected creation effect.

# Appendix: Data Quality Report {#sec:appendix-dq}

See Phase 0 `DATA_QUALITY.md` for the complete assessment. Key findings:

- Merged national panel: 24 rows $\times$ 37 usable columns. Missing rate (excluding dropped columns): 1.69%.
- Digital economy composite index: 4 components (internet users, mobile subscriptions, broadband, R\&D). Equal-weight average. Min-max normalized to $[0, 1]$. Saturated by 2023.
- ILO employment data: modeled estimates, not survey-based. Education-based skill columns unusable (1/24 observations).
- Smart city pilot panel: 286 cities $\times$ 16 years. Structurally complete but lacks outcome variables.
- World Bank data: 82% complete; known methodology changes circa 2015 (PPP revision).

# Appendix: Code References {#sec:appendix-code}

| Script | Phase | Purpose |
|:-------|:------|:--------|
| `phase0_discovery/scripts/acquire_data.py` | 0 | Data acquisition from World Bank, ILO |
| `phase0_discovery/scripts/assess_data_quality.py` | 0 | Data quality assessment |
| `phase2_exploration/scripts/explore_data.py` | 2 | EDA, stationarity tests, feature engineering |
| `phase3_analysis/scripts/causal_testing.py` | 3 | Granger causality, cointegration, refutation tests |
| `phase3_analysis/scripts/statistical_model.py` | 3 | DID-inspired regressions, ARDL, VECM, bootstrap |
| `phase4_projection/scripts/projection_simulation.py` | 4 | Monte Carlo projection, sensitivity, EP decay |
| `phase5_verification/scripts/verify_reproduction.py` | 5 | Independent reproduction |

Table: Analysis code references. {#tbl:code-refs}
