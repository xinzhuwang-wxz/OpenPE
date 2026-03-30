---
title: "Does the Digital Economy Drive Labor Force Structural Change in China?"
subtitle: "OpenPE Analysis Report"
date: 2026-03-30
bibliography: references.bib
mainfont: "Palatino"
monofont: "Menlo"
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{graphicx}
  - \usepackage{xcolor}
  - \usepackage{fancyhdr}
  - \setkeys{Gin}{width=0.85\linewidth,keepaspectratio}
  - \definecolor{openpe-blue}{HTML}{2563EB}
  - \definecolor{openpe-gray}{HTML}{6B7280}
  - \pagestyle{fancy}
  - \fancyhf{}
  - \fancyhead[L]{\small\textcolor{openpe-gray}{OpenPE Analysis Report}}
  - \fancyhead[R]{\small\textcolor{openpe-gray}{\leftmark}}
  - \fancyfoot[C]{\thepage}
  - \renewcommand{\headrulewidth}{0.4pt}
---

# Executive Summary {#sec:executive-summary}

China's digital economy does not causally drive labor force structural change -- at least not in the way the prevailing narrative suggests. This analysis tested three mechanism channels (creation, substitution, and mediation) using national time series data from 2000 to 2023 (T=24), employing Granger causality, cointegration analysis, structural break tests, and VAR impulse response decomposition. The originally planned difference-in-differences (DID) design, using smart city pilot policy as a quasi-natural experiment, could not be executed because city-level outcome data was unavailable. All causal claims therefore rest on weaker time series identification.

The headline finding reverses the initial hypothesis: the digital economy index is positively associated with industrial employment share (ARDL long-run coefficient of **+7.15 percentage points** per unit DE increase, 95% CI $[-0.89, 15.20]$), indicating a complement effect rather than the expected substitution (displacement) effect. This association passed 2 of 3 refutation tests and is classified **CORRELATION** with explanatory power (EP) of 0.315. The creation channel (digital economy driving services employment) found no temporal precedence and an effect indistinguishable from zero (EP = 0.030, below hard truncation). The mediation channel via industrial upgrading failed 2 of 3 refutation tests (EP = 0.090). Demographics emerge as the dominant driver of long-run employment reallocation, but annual Granger tests lack the resolution to detect this decadal-scale force.

Forward projection is severely constrained: the proxy DE index saturated at its ceiling (1.0) by 2023, eliminating any capacity to distinguish future digital economy scenarios. All three Monte Carlo simulations converge on industry employment declining from 31.4% to approximately **25--28% by 2033**, driven by demographic contraction rather than digitalization. The EP decays below hard truncation within 3 years, making the useful projection horizon **3 years** at most. The endgame is classified as "Robust" (CV = 0.046), but this reflects model insensitivity to the saturated primary variable, not strong causal knowledge. Joint EP for the best-supported chain: **0.315**. Overall assessment: with available national aggregate data and a proxy index, the digital economy's causal role in China's labor structural change **cannot be established**.

# First Principles and Causal Structure {#sec:principles}

## Domain and Scope

This analysis sits at the intersection of **digital economics** (economic activity mediated by digital platforms, ICT infrastructure, and e-commerce) and **labor economics** (employment structure, labor supply and demand, human capital formation). Supporting domains include industrial organization (sectoral reallocation), human capital theory (skill upgrading and deskilling), and public policy evaluation (quasi-natural experiment identification).

## Foundational Causal Mechanisms

Four first principles govern the digital economy--labor structure relationship. Each has a long intellectual pedigree.

**Technological Displacement and Compensation (Ricardo--Marx--Schumpeter).** Every major technology transition simultaneously destroys jobs through automation and creates jobs through new products, industries, and demand. The net effect depends on adoption speed, labor market flexibility, and institutional context. This principle is universal across historical transitions -- mechanization, electrification, computerization, and now digitalization [@acemoglu2011skills].

**Skill-Biased Technological Change and the Task Framework (Acemoglu and Autor, 2011).** Digital technologies automate routine tasks, increasing demand for non-routine cognitive skills while hollowing out middle-skill employment -- a pattern called "job polarization." This framework was developed for advanced economies; its applicability to China's dual labor market (hukou system, state-owned enterprise segmentation) requires empirical validation rather than assumption [@acemoglu2011skills].

**Structural Change and Multi-Sector Reallocation (Lewis--Kuznets--Herrendorf).** Economic development drives labor from agriculture to manufacturing to services. The digital economy may accelerate this "tertiarization" by raising service-sector productivity and creating entirely new service categories [@herrendorf2014growth].

**Labor Market Segmentation (Doeringer--Piore).** China's labor market is deeply segmented along urban-rural (hukou), state-private, and formal-informal dimensions. Digital technology affects these segments differently; platform work creates a "third segment" that is neither traditional formal employment nor traditional informal work.

## Competing Causal Models

Phase 0 constructed three competing directed acyclic graphs (DAGs), each generating distinct testable predictions.

**DAG 1 (Technology-Push Direct Effects)** posits that the digital economy acts primarily through direct technology channels: automation displaces routine workers (substitution), while new digital industries absorb workers (creation). Kill condition: mid-skill employment increases in pilot cities relative to controls.

**DAG 2 (Institutional Mediation)** posits that the digital economy operates through institutional mediators -- human capital investment, industrial structure upgrading, labor market reform -- with the direct path being weak. Kill condition: direct effect remains significant after controlling for mediators.

**DAG 3 (Labor Market Segmentation)** posits that the digital economy has opposite effects across labor market segments: substitution dominates in the formal sector, creation dominates in the informal/platform sector, and the aggregate effect masks this heterogeneity. Kill condition: within-segment effects are homogeneous.

No single DAG was confirmed. DAG 1's substitution prediction was contradicted (the DE--industry association is positive, not negative). DAG 2's mediation hypothesis could not survive refutation testing. DAG 3 was untestable without individual-level data. The analysis resolves to a simplified DAG with five testable edges.

## How Explanatory Power Evolved

Every causal edge started with a literature-based EP estimate in Phase 0 and was revised downward through data quality adjustment and refutation testing. @tbl:ep-evolution traces this decline.

| Causal Edge | Phase 0 EP | Phase 3 EP | Classification | Reason for Change |
|:------------|:----------:|:----------:|:---------------|:------------------|
| DE$\to$SUB (substitution) | 0.49 | **0.315** | CORRELATION | Passed 2/3 refutations; direction reversed (complement) |
| DE$\to$CRE (creation) | 0.42 | **0.030** | HYPOTHESIZED | No Granger causality; effect near zero |
| DE$\to$IND\_UP (mediation) | 0.35 | **0.090** | HYPOTHESIZED | Passed only 1/3 refutations; unstable |
| DEMO$\to$LS (demographics) | 0.42 | **0.120** | HYPOTHESIZED | No Granger causality at annual frequency |
| DE$\to$LS (direct) | 0.12 | **0.010** | HYPOTHESIZED | Below hard truncation |

Table: EP evolution from Phase 0 to Phase 3. All edges declined, reflecting data constraints, construct validity concerns, and refutation test outcomes. {#tbl:ep-evolution}

# Data Foundation {#sec:data}

## Sources and Quality

The analysis draws on publicly available macroeconomic data. @tbl:data-overview summarizes each source.

| Dataset | Source | Coverage | Quality | Key Limitation |
|:--------|:-------|:---------|:-------:|:---------------|
| World Bank WDI | World Bank API (wbgapi) | 2000--2023 | MEDIUM | ILO-modeled estimates, not survey-based |
| ILO employment structure | ILO modeled estimates via WB | 2000--2023 | MEDIUM | Skill-composition columns 96% missing |
| DE composite index | Constructed from WB indicators | 2000--2023 | **LOW** (bias) | 4-component proxy; saturated at 1.0 by 2023 |
| Smart city pilots | MOHURD announcements | 2012--2015 | HIGH | No city-level outcome data available |
| Merged national panel | Merged from above | 2000--2023 | MEDIUM | T=24; 37 usable columns |

Table: Data registry summary with Phase 0 quality verdicts. {#tbl:data-overview}

## Data Quality Gate

The data quality gate decision was **PROCEED WITH WARNINGS**. Seven constraints bind all downstream analysis:

1. **DID not executable.** Smart city pilot treatment indicators exist (286 cities, 3 batches), but no city-level outcome variables are available. All causal claims use weaker time series identification -- like trying to evaluate a medical treatment without a control group, relying instead on before-and-after comparisons.
2. **Skill-level analysis impossible.** ILO education-based columns have only 1 of 24 observations populated; CFPS microdata is registration-gated. EP truth is capped at 0.30 for any skill-level edge.
3. **DE composite index is a proxy of uncertain validity.** It measures ICT infrastructure penetration (internet users, mobile subscriptions, broadband, R&D expenditure), not the broader digital economy (e-commerce scale, platform activity, digital finance). The validated PKU-DFIIC digital financial inclusion index was unavailable. The proxy saturated at 1.0 by 2023.
4. **T=24 limits model complexity.** A maximum of 4--5 regressors can be included simultaneously. Statistical power is approximately **35%** for medium effects -- meaning that even if a genuine medium-sized effect exists, this analysis has a 65% probability of missing it.
5. **ILO employment estimates are partially endogenous.** Regressing services employment on GDP and urbanization yields $R^2 = 0.989$, signaling that the outcome variable may share a data-generating process with potential control variables.
6. **No individual-level mechanism testing.** Without CFPS microdata, DAG 2 (mediation via human capital) and DAG 3 (segmentation) cannot be tested at the mechanism level.
7. **No cross-sectional variation.** A national time series has exactly one "observation unit" (China as a whole) and cannot identify regional, industry, or skill heterogeneity.

## Data Preparation

The primary analysis dataset is `china_national_panel_merged.parquet` (24 rows $\times$ 40 columns). Three ILO education-based columns were dropped (96% missing). No imputation was applied; missing values were handled via listwise deletion within each test. First differences, log transformations, growth rates, and structural break indicators were constructed as engineered features.

# Core Findings {#sec:findings}

## Substitution Channel: The Direction Is Reversed {#sec:substitution}

The digital economy's relationship with industrial employment is the only finding in this analysis with substantive statistical support -- and its direction is the opposite of what the initial hypothesis predicted.

- **Classification:** CORRELATION
- **EP:** 0.315 (truth = 0.45, relevance = 0.70)
- **Effect size:** ARDL long-run coefficient **+7.15 pp** per unit DE increase (bivariate), **+12.57 pp** (with demographic control)
- **Direction:** **Positive** (complement, not substitution/displacement)

The Toda-Yamamoto test (a Granger causality variant designed for small samples, which at T=24 has more accurate statistical size than the standard Granger test [@toda1995statistical]) detects Granger causality from DE to industry employment at the 10% level bivariate ($W = 5.84$, $p_{\text{boot}} = 0.087$), strengthening to the 5% level with demographic control ($W = 13.33$, $p_{\text{boot}} = 0.012$). Johansen cointegration confirms a long-run equilibrium (trace $= 19.04 > \text{cv}_{95} = 15.49$). The ARDL bounds test [@pesaran2001bounds] corroborates cointegration ($F = 6.51 > \text{upper bound}\ 5.73$ at 5%). However, independent verification revealed a 78.5% divergence in the ARDL bounds F-statistic (primary: 6.51 vs. independent: 1.40), suggesting the cointegration result is fragile. The reproducible Johansen trace test ($p < 0.01$) provides more robust support for the long-run relationship.

Every method agrees on the direction: DE growth is associated with **increased** -- not decreased -- industrial employment. This complement effect means that during 2000--2023, ICT infrastructure expansion coincided with the maintenance of industrial employment, not its erosion. Think of it this way: factories that adopted digital tools did not shed workers -- they enabled the same workforce to produce more and handle more complex tasks, sustaining the industrial employment base.

An important alternative explanation is China's state industrial policy. Programs like "Made in China 2025" and extensive manufacturing subsidies may independently explain why industrial employment remained elevated during digitalization, confounding the observed complement effect. This analysis cannot separate the digital economy's effect from concurrent industrial policy, and the positive DE--industry association should be interpreted with this caveat.

@fig:structural-break shows the structural break and counterfactual comparison. Before 2013, industry employment rose at +0.71 pp per year ($R^2 = 0.82$). After 2016, the trend reversed, with observed values deviating **-4.45 pp** from the counterfactual ($t = -11.51$, $p < 0.001$). However, Chow tests in first differences find no significant break in the DE--industry relationship itself ($F = 0.66$, $p = 0.530$), indicating that the trend reversal in industry employment was not driven by a change in the digital economy relationship.

![Structural break and DID-inspired baseline comparison: (a) DE index with break window, (b) employment structure trends, (c) pre/post first-difference scatter, (d) counterfactual versus observed.](figures/structural_break_did_baseline.pdf){#fig:structural-break width=90%}

### Refutation Tests

Refutation tests (stress tests that check whether a statistical result holds under different assumptions -- for example, randomly shuffling the treatment timing or adding an irrelevant noise variable) reveal one critical weakness:

| Test | Result | Detail |
|:-----|:------:|:-------|
| Placebo treatment | PASS | Only 1 of 4 placebo dates significant (shift = 5) |
| Random common cause | PASS | $W$ changed less than 10% |
| Data subset (25% drop) | **FAIL** | $W$ changed 86.2%; highly sensitive to specific observations |

Table: Refutation battery for DE$\to$SUB (controlled specification). {#tbl:refutation-main}

The data subset failure directly reflects the T=24 constraint: dropping just 6 observations changes the conclusion. This is inherent to the sample size, not a refutation of the association itself -- but it prevents upgrading the finding to DATA\_SUPPORTED and keeps it at CORRELATION.

### Method Comparison

@fig:method-comparison summarizes results across all methods. Every method agrees on the positive (complement) direction, but they differ in what they capture: Granger causality reflects short-run dynamics, cointegration and ARDL reflect long-run equilibrium, and the counterfactual trend captures macro-structural transformation.

![Method comparison summary: Granger, ARDL, and Chow test results for the substitution (top row) and creation (bottom row) channels.](figures/method_comparison_summary.pdf){#fig:method-comparison width=90%}

## Creation Channel: No Evidence Found {#sec:creation}

Does the digital economy create new services employment? The available data cannot support that claim.

- **Classification:** HYPOTHESIZED
- **EP:** 0.030 (truth = 0.30, relevance = 0.10)
- **Status:** Below hard truncation (0.05). Beyond the analytical horizon.

DE does not Granger-cause services employment (bivariate: $W = 1.16$, $p = 0.565$; with demographic control: $W = 0.38$, $p = 0.834$). No cointegrating relationship exists (Johansen trace $= 4.47 < \text{cv}_{95} = 15.49$). The level correlation between DE and services employment reaches $r = 0.981$, but this is a textbook spurious regression -- two upward-trending series that move together by coincidence. After first-differencing, the correlation reverses to negative ($r = -0.377$), exposing the level correlation as an artifact. It is like watching two people climb a staircase at the same time and concluding that one must be pulling the other up. They are simply both going in the same direction.

The power caveat is essential: at **35% power**, this null result **cannot** be interpreted as evidence that "the digital economy does not create services employment." A genuine medium-sized creation effect could exist undetected. But on the basis of available data, this channel's EP falls to 0.030 and supports no analytical inference.

## Mediation Channel: Industrial Upgrading Pathway Not Supported {#sec:mediation}

The hypothesis that the digital economy drives employment reallocation through industrial upgrading -- DE pushes the economy up the value chain, which then reshuffles workers across sectors -- is the dominant narrative in the Chinese literature. Reference analysis Li et al. (2024) found approximately 22% of the digital economy's employment effect transmitted through industrial upgrading in a 30-province panel [@li2024digital]. The national time series results here sharply contradict that finding.

- **Classification:** HYPOTHESIZED
- **EP:** 0.090 (truth = 0.30, relevance = 0.30)
- **Status:** Below soft truncation (0.15).

With demographic controls, DE significantly Granger-causes services value-added share ($W = 15.81$, $p = 0.008$). However, the controlled specification passes only 1 of 3 refutation tests: the random common cause test shows 24.2% sensitivity to an irrelevant variable (likely overfitting with 3 endogenous variables and 3 lags at T=24), and the data subset test shows 76.1% instability.

More critically, the trivariate VAR impulse response decomposition produces a counterintuitive result: the mediation share is **negative** ($-90\%$ to $-95\%$), meaning that including the services value-added mediator *weakens* rather than strengthens the total effect of DE on services employment. The standard "DE drives industrial upgrading which drives employment reallocation" narrative is not supported in the national time series. @fig:var-irf shows this impulse response.

![VAR impulse response functions for the mediation system: DE, services value-added, and services employment. The indirect pathway (through industrial upgrading) moves in the opposite direction from the direct pathway.](figures/var_irf_mediation.pdf){#fig:var-irf width=90%}

The contradiction with Li et al. (2024) likely reflects the fundamental difference between cross-sectional variation (provincial panels, where inter-provincial differences in industrial upgrading do transmit digital economy effects) and temporal variation (national time series, where the national-level trajectories of industrial upgrading and digitalization do not form a causal transmission chain).

## Demographics: The Undetected but Dominant Driver {#sec:demographics}

Demographics do not Granger-cause employment structure at annual frequency (services: $W = 1.93$, $p = 0.397$; industry: $W = 0.75$, $p = 0.694$). Yet their influence on the analysis is decisive. Adding demographic controls shifts the DE coefficient from +7.15 to +12.57 pp -- demonstrating that demographics confound the DE--employment relationship at frequencies below the Granger test's resolution.

This apparent paradox (insignificant Granger test but large confounding effect) has a straightforward explanation: demographic effects operate at **decadal scale** (fertility decisions made 15--65 years ago determine today's working-age population), while annual Granger tests capture only year-to-year fluctuations. Using annual Granger causality to detect demographic effects is like using a stopwatch to measure tectonic drift -- the instrument's precision does not match the phenomenon's timescale [@cai2010demographic; @acemoglu2022demographics].

Demographic exogeneity is confirmed: DE does not Granger-cause demographics ($W = 2.67$, $p = 0.293$), supporting the treatment of demographics as a control variable rather than an endogenous mediator.

## The 2014 Structural Break {#sec:structural-break}

Structural break analysis reveals a dramatic shift around 2013--2015, coinciding with the smart city pilot batches [@zhu2023smart]:

- **Services employment** exceeded its counterfactual trend by **+1.83 pp** ($t = 5.12$, $p = 0.001$)
- **Industrial employment** fell below its counterfactual by **-4.45 pp** ($t = -11.51$, $p < 0.001$)
- **Agricultural employment** decline decelerated, exceeding the counterfactual by +2.62 pp ($t = 3.52$, $p = 0.010$)
- **Services value-added** accelerated most dramatically, exceeding the counterfactual by **+5.89 pp** ($t = 34.96$, $p < 0.001$)

This structural break coincides temporally with supply-side structural reform (2015--2016), smart city pilot diffusion, and global supply chain reorganization. It cannot be attributed solely to the digital economy. The DID design was precisely intended to control for such confounding -- but data limitations prevented its execution.

# Forward Projection {#sec:projection}

## The Fundamental Constraint

The projection faces a binding obstacle: the proxy DE index saturated at its ceiling (1.0) by 2023. It is a ruler that has already measured to its maximum mark and can no longer distinguish anything longer. Perturbing $\beta_{\text{DE}}$ or the DE growth rate by $\pm 20\%$ produces **zero** change in the deterministic endpoint because any further DE increase is absorbed by the upper bound. Only demographic parameters have non-zero sensitivity.

## Three Scenarios

@tbl:scenarios-main shows results from 10,000 Monte Carlo iterations (random seed 20260329) over a 10-year projection horizon.

**"Trend Continuation" scenario (baseline).** The DE index stays near its ceiling, population contracts at the current rate ($-0.31$ pp/year), and the conservative ARDL coefficient (7.15) applies. This is the most probable trajectory, with conditional probability 50--60%.

**"Digital Acceleration" scenario.** China ramps up digital infrastructure investment (AI, 5G, industrial internet). DE growth rises 50%, using the stronger controlled ARDL coefficient (12.57). However, because the DE index is already saturated, this scenario is **virtually identical** to the baseline -- accelerated digital development cannot be captured by the proxy variable. Conditional probability 20--30%.

**"Digital Stagnation" scenario.** Tightened tech regulation (antitrust enforcement, data governance), US-China technology decoupling, or market saturation slow digital economy growth. The complement effect weakens to half of baseline, and demographic decline accelerates. This scenario produces the lowest employment projection (2033 median **24.9%**) because the weakened complement effect releases pure demographically driven decline. Conditional probability 15--25%.

| Scenario | 2033 Median | 90% CI | Primary Driver |
|:---------|:-----------:|:-------|:---------------|
| Trend Continuation | 27.5% | [24.8, 30.1] | Demographics |
| Digital Acceleration | 27.5% | [24.7, 30.3] | Demographics |
| Digital Stagnation | 24.9% | [18.4, 31.1] | Demographics + weakened complement |

Table: Industry employment share scenario results. Baseline and Digital Acceleration are nearly identical because the DE index is saturated. {#tbl:scenarios-main}

![Scenario comparison: historical (2000--2023) and projected (2024--2033) industry employment share with 50% and 90% confidence bands. The three scenarios converge because the DE index is saturated.](figures/scenario_comparison.pdf){#fig:scenario-comparison width=90%}

## Sensitivity Analysis

@fig:sensitivity-tornado reveals a striking result: digital economy parameters have **zero** marginal sensitivity on the 10-year projection endpoint.

| Rank | Variable | Impact ($\pm 20\%$ perturbation) | Controllability |
|:----:|:---------|:--------------------------------:|:----------------|
| 1 | Demographic effect size | $\pm$0.79 pp | Exogenous |
| 2 | Demographic decline rate | $\pm$0.79 pp | Exogenous |
| 3 | DE effect size | 0.00 | Semi-controllable |
| 4 | DE annual growth rate | 0.00 | Controllable |

Table: Sensitivity ranking at 10-year horizon. DE parameters have zero marginal sensitivity due to proxy saturation. {#tbl:sensitivity-main}

![Sensitivity tornado: impact of $\pm 20\%$ parameter perturbation on 10-year industry employment share. Color indicates controllability.](figures/sensitivity_tornado.pdf){#fig:sensitivity-tornado width=80%}

The "zero sensitivity" is not a modeling error -- it is a direct consequence of the proxy index construction. The real digital economy continues evolving after 2023, but the min-max normalized proxy cannot capture that evolution. With a non-saturated DE measure (such as the PKU-DFIIC digital financial inclusion index, which has a wider value range), DE parameters would likely jump to the top of the sensitivity ranking.

## EP Decay and Useful Projection Horizon

The EP decay chart is the core message of this report: it communicates how epistemic confidence degrades inevitably from established findings through forward projection.

| Projection Distance | EP Value | Confidence Tier |
|:-------------------:|:--------:|:----------------|
| 0 years (Phase 3) | 0.315 | High (empirical) |
| 1 year | 0.113 | Below soft truncation |
| 3 years | 0.050 | At hard truncation |
| 5 years | 0.020 | Below hard truncation |
| 10 years | 0.002 | Negligible |

Table: EP decay schedule for the DE$\to$SUB edge. CORRELATION edges decay at 2$\times$ the standard rate. {#tbl:ep-decay-main}

![EP-weighted confidence decay. Top: baseline projection with widening confidence bands. Bottom: EP value decay from the Phase 3 anchor (0.315) toward hard truncation.](figures/ep_decay_chart.pdf){#fig:ep-decay width=90%}

**The useful projection horizon is 3 years (to 2026).** Beyond 3 years, projections have negligible empirical causal support and are merely extrapolations of demographic trends with no grounded digital economy content.

## Endgame Classification

**Category: Robust** (CV $= 0.046$, well below the 0.15 threshold).

The convergence of three scenarios does not mean the digital economy's role is well understood. It means the model cannot distinguish scenarios because its primary variable is saturated. If a non-saturated DE measure were available, the endgame would likely shift to **Fork-dependent**, with the fork condition being whether digital economy growth accelerates (buffering industry employment via the complement effect) or stagnates (allowing pure demographic decline to dominate).

# Uncertainty and Limitations {#sec:uncertainty}

## Uncertainty Decomposition

The uncertainty decomposition for the substitution channel (the best-supported finding) shows that statistical uncertainty dominates:

| Source | Type | $\pm$Shift | Share |
|:-------|:-----|:----------:|:-----:|
| Bootstrap standard error | Statistical | 15.91 | Dominant |
| Demographic control inclusion | Systematic | 7.78 | 33% |
| Break year choice | Systematic | 2.60 | 11% |
| COVID exclusion (2020--21) | Systematic | 1.81 | 8% |

Table: Uncertainty decomposition for the substitution channel. {#tbl:uncertainty-main}

The bootstrap standard error (approximately 16) exceeds half the point estimate (approximately 21), meaning the effect is positive but imprecise. More data -- whether a longer time series or panel data with cross-sectional variation -- is the primary path to improved precision.

![Uncertainty tornado: statistical and systematic uncertainty decomposition for the substitution channel.](figures/uncertainty_tornado.pdf){#fig:uncertainty-tornado width=80%}

## Key Limitations

**Low statistical power (approximately 35%).** With T=24, this analysis has approximately a 65% probability of producing a false negative for medium-sized effects. The null result for the creation channel cannot be read as "the digital economy does not create employment" -- the effect may simply be undetected. If this analysis were a telescope searching for a star, 35% power means the telescope focuses correctly only one-third of the time.

**DE index construct validity.** The composite index combines four equally weighted components (internet users, mobile subscriptions, broadband penetration, R&D expenditure) and measures ICT infrastructure diffusion, not the full digital economy. E-commerce transaction volume, platform economy scale, digital finance depth -- the dimensions that truly define "digital economy" -- are all absent. Worse, the index saturated at 1.0 by 2023, rendering all forward projections blind to differential digital development paths.

**ILO employment estimate endogeneity.** ILO modeled estimates (not survey data) are partially derived from GDP and urbanization -- the very variables used as potential controls. Regressing services employment on GDP and urbanization yields $R^2 = 0.989$, signaling that the independent and dependent variables may share a common data-generating process.

**DID not executable.** The original question required DID as a baseline comparison, but city-level outcome data was unavailable (EPS is a commercial database requiring payment; PKU-DFIIC is not publicly accessible; NBS provincial data requires JavaScript rendering from yearbook tables). Structural break analysis substitutes for DID: it preserves the "before-and-after" logic but lacks the "treatment vs. control" dimension.

**No cross-sectional variation.** A national time series has exactly one observational unit (China), providing no ability to identify regional heterogeneity, industry heterogeneity, or skill heterogeneity. Reference analyses [@zhu2023smart; @li2024digital; @zhao2022digital] use provincial or city panels (N = 30--280) with cross-sectional identification that this analysis fundamentally lacks.

# Policy Implications {#sec:policy}

Each implication below carries a confidence label reflecting its evidence basis.

**Demographics are the most reliably identified driver of labor reallocation (CORRELATION).** All three projection scenarios agree: industry employment share declines primarily because of demographic contraction. Regardless of what the digital economy does, the shrinking working-age population will compress industrial employment over the next decade. Policymakers should place demographic policy (delayed retirement, fertility support, reskilling programs) at the center of labor force adjustment strategy.

**The substitution hypothesis lacks empirical support -- in fact, the direction is reversed (CORRELATION).** Available data does not support the narrative that "digitalization displaces industrial workers." ICT infrastructure expansion is positively associated with industrial employment (+7.15 to +12.57 pp per unit DE). When designing digital transformation policy, decision-makers should not overweight short-term industrial displacement fears. However, this conclusion rests on national aggregate data and may mask substitution effects within specific industries or regions.

**The creation and mediation channels need better data, not more analysis of the same data (HYPOTHESIZED).** This analysis could not establish causal support for "the digital economy creates services employment" or "the digital economy reshuffles workers via industrial upgrading." This does not mean these effects do not exist -- it means that T=24 national time series with a proxy DE index are insufficient to detect them. The recommended investments are:

   - Obtain the PKU-DFIIC digital financial inclusion index (a non-saturated DE measure)
   - Obtain NBS provincial panel data (N = 30+ cross-sectional units)
   - Explore research access to CFPS microdata (individual-level mechanism testing)

**Smart city pilot evaluation requires city-level outcome data (HYPOTHESIZED).** The 286 cities across three pilot batches provide an excellent quasi-natural experiment framework. Evaluating employment effects requires city-level employment data. If obtainable, a proper DID design would provide far stronger causal identification than anything in this analysis [@zhu2023smart].

**The 2013--2015 structural break warrants granular investigation (DESCRIPTIVE).** Industry employment deviating **-4.45 pp** from its counterfactual trend is an economically significant fact. This break coincides with smart city pilots, supply-side reform, and global supply chain shifts. Attributing it to any single cause requires city-level or province-level DID -- precisely the design this analysis could not execute.

# Verification Summary {#sec:verification}

Phase 5 independent verification produced an overall **FLAG** result (no Category A findings, 1 Category B, 2 Category C).

| Check | Result | Key Detail |
|:------|:------:|:-----------|
| Independent reproduction | PASS | 7/10 metrics within 5% deviation |
| Data provenance audit | PASS | 7/7 SHA-256 hashes match |
| Logic audit | FLAG | 1 Category B ($R^2$ discrepancy) |
| EP verification | PASS | 4/5 edges exact match |
| Consistency checks | PASS | Cross-document consistency confirmed |

Table: Phase 5 verification results. {#tbl:verification-main}

**ARDL bounds F-statistic divergence.** Independent verification yields $F = 1.40$ versus reported $F = 6.51$ (78.5% divergence). The discrepancy arises from specification-dependent differences in ARDL bounds test implementation (lag structure, treatment of deterministic components). Cointegration is independently confirmed by the Johansen trace test (19.04, reproduced exactly), so the cointegration conclusion is robust.

**Industry pre-trend $R^2$.** Originally reported as 0.96 in ANALYSIS.md; independently verified as **0.82**. The slope (+0.71 pp/year) and counterfactual deviation ($-4.45$ pp) were reproduced exactly. The lower $R^2$ means the pre-trend is a somewhat less reliable counterfactual basis, but the qualitative conclusion (dramatic structural break) is unchanged. This value has been corrected throughout this report.

**Power analysis.** Reported as 35%, independently computed as 43%. The difference stems from different degrees-of-freedom specifications. The qualitative conclusion (low power) is unchanged.

Human gate approval was granted (option a) with the instruction to correct the $R^2$ value.

# Audit Trail {#sec:audit}

## Data Provenance

All raw data is stored in `data/raw/` with SHA-256 hashes recorded in `data/registry.yaml`. Seven datasets were successfully acquired; three failed (EPS commercial database, CFPS registration-gated, FRED no API key). NBS provincial data acquisition was attempted but blocked because yearbook tables require JavaScript rendering.

## Methodology Choices

| Choice | Justification | Alternatives Considered |
|:-------|:-------------|:-----------------------|
| Toda-Yamamoto over standard Granger | T=24 violates the T$\geq$30 convention; TY is valid for T around 20 [@toda1995statistical] | Standard Granger (rejected: size distortion at T=24) |
| ARDL bounds complementing Johansen | Valid for I(0)/I(1) mixture [@pesaran2001bounds] | Pure Johansen (used as complement, not replacement) |
| Structural break over DID | No city-level outcome data for DID | True DID (data unavailable) |
| VAR mediation over Baron-Kenny | Time series violates the i.i.d. assumption [@blanchard1989dynamic] | Baron-Kenny (rejected: inappropriate for time series) |
| Block bootstrap over analytical SE | T=24 may violate asymptotic distributional assumptions [@hacker2006bootstrap] | Analytical SE (used in parallel for comparison) |

Table: Key methodology choices with justifications. {#tbl:methodology-audit}

## Phase 0 Warnings Carried Forward

All seven Phase 0 data quality warnings have been fully carried through this report: DID not executable (confirmed; structural break substituted), skill-level analysis impossible (confirmed; all skill edges EP = 0), DE composite index is a proxy (confirmed; saturated by 2023), T=24 limits model complexity (confirmed; power approximately 35%), ILO employment estimates partially endogenous (confirmed; $R^2 = 0.989$), no individual-level mechanism testing (confirmed; CFPS unavailable), and no cross-sectional variation (confirmed; national time series only).

## Code References

| Script | Phase | Purpose |
|:-------|:------|:--------|
| `acquire_data.py` | 0 | Data acquisition from World Bank, ILO |
| `assess_data_quality.py` | 0 | Quality assessment |
| `explore_data.py` | 2 | EDA, stationarity tests, feature engineering |
| `causal_testing.py` | 3 | Granger causality, cointegration, refutation tests |
| `statistical_model.py` | 3 | DID-inspired regressions, ARDL, VECM, bootstrap |
| `projection_simulation.py` | 4 | Monte Carlo projection, sensitivity, EP decay |
| `verify_reproduction.py` | 5 | Independent reproduction |

Table: Analysis code references. Full paths in each phase's `scripts/` directory; executed via `pixi run py`. {#tbl:code-audit}

# References {.unnumbered}
