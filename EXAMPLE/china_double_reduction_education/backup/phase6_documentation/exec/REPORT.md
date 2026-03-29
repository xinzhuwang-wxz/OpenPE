---
title: "Did China's Double Reduction Policy Truly Reduce Household Education Expenditure?"
subtitle: "An OpenPE First-Principles Analysis"
date: 2026-03-29
---

# Executive Summary

China's Double Reduction policy did not measurably reduce household education spending. The July 2021 ban on for-profit academic tutoring destroyed over 90% of the formal tutoring industry, but four years of macro-level data show no detectable decline in per-child education expenditure. The aggregate spending dip that appeared in 2021--2022 is statistically indistinguishable from the concurrent effects of COVID-19 lockdowns and a **47% collapse in births** between 2016 and 2024. When spending is normalized by the number of children actually entering the education system, the policy signal vanishes entirely ($p = 0.48$).

The core finding rests on three independent lines of evidence. First, an Interrupted Time Series model estimates a level shift of **-483 yuan** (in real 2015 terms), but this falls to just $1.7\sigma$ significance once systematic uncertainties --- dominated by how COVID-19 is handled --- are included. Second, a placebo test placing the intervention at the COVID start date (2020) produces a larger and more statistically significant break than the actual policy date, indicating COVID disruption is the dominant signal. Third, the observed 23.7% aggregate decline exceeds the 12% maximum that full tutoring elimination could explain, meaning at least half the decline must come from non-policy sources.

This analysis evaluated three competing causal explanations: direct reduction through supply destruction (DAG 1), regulatory displacement to underground channels (DAG 2), and compositional irrelevance because tutoring was only 12% of spending (DAG 3). The data reject DAG 1 and are consistent with a combination of DAGs 2 and 3 --- the formal industry collapsed, but spending shifted rather than disappeared. All multi-step causal chains produce Joint Explanatory Power (EP) values below the 0.05 hard truncation threshold, meaning no chain-level causal claim is supportable. The endgame classification is **fork-dependent**: the single dataset that would resolve the question --- post-2021 household microdata from the China Family Panel Studies --- has not yet been released.

Forward projections show demographic decline, not policy, driving the spending trajectory. The birth rate ranks first in sensitivity analysis with more than twice the impact of income growth and four times the impact of policy persistence. The useful projection horizon is 2029; beyond that, uncertainty bands exceed the signal. The most probable scenario ("Status Quo / Displacement," 45--55% probability) projects spending approximately flat at **3,108 yuan by 2035**, with families continuing to redirect resources toward in-school expenses and informal tutoring.


# First Principles Identified {#sec:principles}

## The Question and Its Domain

The Double Reduction (*shuangjian*) policy posed a clean testable question: did banning for-profit tutoring reduce how much Chinese families spend on education? Answering it requires three overlapping domains --- education policy evaluation, public economics, and the behavioral economics of household decision-making under regulation. The policy's effectiveness hinges not on whether tutoring centers closed (they did, overwhelmingly) but on whether families responded by spending less rather than spending differently.

## Four Principles That Structure the Analysis

Four first principles, drawn from the education economics and regulatory literature, generate the competing causal hypotheses [@zhang2020shadow; @park2016shadow; @liu2025crowdingin].

**Principle 1: Demand Inelasticity Under Status Competition.** Education in China functions as a positional good. The *gaokao* (national college entrance examination) creates zero-sum competition where a family's relative investment matters more than absolute spending. When one channel of investment is banned, economic theory predicts spending will redirect rather than disappear --- the same logic that explains why luxury taxes shift consumption to untaxed substitutes rather than reducing total luxury spending (CORRELATION; EP = 0.42).

**Principle 2: The Balloon Effect (Regulatory Displacement).** Suppressing a market without eliminating the underlying demand pushes activity into unregulated channels, often at higher cost. Roughly 3,000 illegal tutoring operations were detected in Q2 2022 alone [@sixthtone2022crackdown], and media reports document price increases of 43--50% for underground tutors. The analogy is drug prohibition: enforcement can destroy the legal market while the underground market grows to replace it (HYPOTHESIZED; EP = 0.14).

**Principle 3: Compositional Fallacy in Policy Evaluation.** A policy can reduce a specific subcategory of expenditure while failing to reduce the aggregate, if spending migrates across categories. Pre-policy survey data show that off-campus tutoring and extracurricular activities constituted only approximately **12%** of total household education expenditure in 2019, while in-school expenses accounted for 73% [@wei2024household]. Even complete elimination of the tutoring component with zero substitution would reduce total spending by at most 12% --- less than the COVID-induced dip (CORRELATION; EP = 0.56 for the industry collapse edge).

**Principle 4: Implementation Fidelity Gradient.** China's centrally mandated policies attenuate through provincial and municipal government layers. Tier-1 cities (Beijing, Shanghai) enforced aggressively; smaller cities and rural areas likely less so. This gradient means the "treatment" varies by geography, complicating any national-level estimate (CONTEXT-DEPENDENT).

## Three Competing Causal DAGs

These principles generate three competing causal structures, each making different testable predictions about what should happen to total household education spending.

**DAG 1 --- "Mission Accomplished": Direct Reduction Through Supply Destruction.** The policy destroyed the tutoring industry, and families genuinely saved money. If this is correct, total education expenditure should decline 5--15% relative to the counterfactual trend, and the decline should persist after COVID recovery. Kill condition: total expenditure flat or rising despite confirmed tutoring collapse.

**DAG 2 --- "Whack-a-Mole": Regulatory Displacement to Underground Channels.** The policy destroyed the visible tutoring market, but spending migrated underground at higher prices. If this is correct, total expenditure should be approximately unchanged, with composition shifting from formal tutoring to informal arrangements. Kill condition: total expenditure declines by the full tutoring reduction amount, indicating no substitution occurred.

**DAG 3 --- "Rearranging Deck Chairs": Compositional Irrelevance.** The policy targeted only 12% of education spending. In-school costs (73%) were unaffected and may have increased through a documented crowding-in effect [@liu2025crowdingin]. If this is correct, aggregate spending should show little or no decline regardless of what happened to tutoring. Kill condition: total expenditure declines substantially more than the tutoring component.

## Edge-Level EP Assessment

Because all multi-step causal chains produce Joint EP below the 0.05 hard truncation threshold, the analysis was formally downscoped from chain-level causal claims to edge-level assessment. @tbl:ep-summary presents the complete edge inventory.

| Edge | Classification | EP | Evidence basis |
|:-----|:--------------|---:|:---------------|
| Policy $\to$ Industry Collapse | CORRELATION | 0.56 | 92--96% offline center closure rate; firm revenue data |
| Competitive Pressure $\to$ Inelastic Demand | CORRELATION | 0.42 | Pre-policy education economics literature |
| Income $\to$ Differential Access | CORRELATION | 0.42 | Urban ITS shift 3.7$\times$ larger than rural |
| Policy $\to$ Aggregate Spending (net) | CORRELATION | 0.20 | ITS: $-483$ yuan, $1.7\sigma$ with systematics |
| Industry Collapse $\to$ Reduced Tutoring | CORRELATION | 0.15 | Education share dropped 0.7 pp; $z = -1.05$ |
| Policy $\to$ Underground Market | HYPOTHESIZED | 0.14 | Anecdotal enforcement reports; LOW data quality |
| Public Spending $\to$ Crowding-In | HYPOTHESIZED | 0.12 | Macro correlation only |
| Underground $\to$ Higher Prices | HYPOTHESIZED | 0.08 | Media reports of 43--50% price increases |
| Reduced Tutoring $\to$ Total Expenditure | HYPOTHESIZED | 0.02 | Eliminated by per-birth normalization |

Table: Explanatory Power summary for all tested causal edges, ordered by EP. No edge achieved DATA_SUPPORTED classification. All multi-step chain Joint EP values fall below the 0.05 hard truncation threshold. {#tbl:ep-summary}

The highest-EP edge (Policy $\to$ Industry Collapse, EP = 0.56) reflects what everyone already knew: the tutoring industry did collapse. The policy-relevant question --- whether that collapse translated into lower total spending --- sits at EP = 0.20, classified CORRELATION, meaning the statistical association exists but causation has not been established.


# Data Foundation {#sec:data}

## What We Had to Work With

The analysis draws on 13 acquired datasets spanning 2016--2025. Six additional datasets failed acquisition, and the most critical absence --- post-2021 household microdata --- is the single largest constraint on the analysis. @tbl:data-sources summarizes the key datasets.

| ID | Dataset | Quality | Years | Role |
|:---|:--------|:-------:|------:|:-----|
| ds\_001 | NBS Education/Culture/Recreation Expenditure | MEDIUM (68) | 2016--2025 | Primary outcome (proxy) |
| ds\_002 | CIEFR-HS Spending Decomposition | MEDIUM (58) | 2017, 2019 | Pre-policy composition |
| ds\_004 | Tutoring Industry Collapse Indicators | MEDIUM (53) | 2020--2024 | Supply-side evidence |
| ds\_006 | China Demographics and Enrollment | MEDIUM (78) | 2016--2024 | Demographic confounder |
| ds\_007 | Public Education Expenditure | MEDIUM (75) | 2016--2023 | Crowding-in test |
| ds\_008 | NBS 8-Category Consumption | MEDIUM (70) | 2019--2025 | Compositional analysis |
| ds\_009 | NBS Disposable Income | HIGH (81) | 2016--2025 | Income control |
| ds\_011 | Underground Tutoring Prices | LOW (33) | 2021--2024 | Anecdotal evidence |
| ds\_013 | NBS CPI Deflator | MEDIUM (75) | 2016--2025 | Real value conversion |

Table: Key datasets with quality scores (average of completeness, consistency, bias, and granularity on a 0--100 scale) and analytical roles. Only one dataset achieves HIGH quality. The primary outcome variable is a proxy, not a direct measure of education spending [@nbs2025communique; @worldbank2024wdi; @wei2024household]. {#tbl:data-sources}

## The Proxy Problem

The single most important caveat in this analysis: the primary outcome variable is not education spending. It is "education, culture and recreation" spending --- an NBS category that bundles school fees with movie tickets, museum visits, and vacation spending. Post-COVID recovery in tourism and entertainment inflates this series upward, potentially masking an education-specific decline. This proxy error is irreducible without sub-category data that NBS does not publicly release. Every quantitative result in this report carries this caveat (DATA_SUPPORTED for the proxy limitation itself --- the NBS category definition is documented fact).

## Nine Binding Constraints

Nine data quality constraints, identified in Phase 0, propagated through all downstream analysis. The three most consequential:

1. **No post-policy household microdata.** The China Family Panel Studies (CFPS) has not released post-2021 waves publicly. The CIEFR-HS Wave 3 (covering 2021--2022) has been conducted but not published. Without household-level spending decomposition, the analysis cannot verify whether the pre-policy 73/12/15 composition (in-school/tutoring/other) shifted after the ban.

2. **COVID-19 temporal overlap.** The policy took effect in July 2021, during COVID recovery. The 2020 disruption ($-19.1\%$ year-on-year) and 2021 rebound ($+27.9\%$) overlap temporally with and dwarf the expected policy signal of 5--12%. No statistical technique can cleanly separate these effects with annual aggregate data.

3. **Ten annual observations.** The entire analysis rests on 10 data points (2016--2025), with the 2020 COVID year excluded from the primary model, leaving 9 usable observations and 6 degrees of freedom. Bootstrap variance estimates from 4 pre-period observations are biased downward, and refutation tests have near-zero power at this sample size.

Additional constraints include: the primary outcome is a proxy (noted above), underground tutoring is inherently unmeasurable (cash-based, illegal, systematically underreported), per-student spending was already declining pre-policy (from 10,372 to 6,090 yuan between 2017 and 2019 per CIEFR-HS), back-calculated 2016--2018 data carry approximately $\pm 2$--$3\%$ error, and CPI deflation is mandatory (cumulative education-category inflation of 16.8% over the period).


# Analysis Findings {#sec:analysis}

## The Headline: No Detectable Per-Child Spending Reduction

The policy did not produce a detectable reduction in per-child education spending. Four years of post-policy data show an aggregate spending dip that is fully explained by demographic decline (fewer children) and COVID-19 disruption, not by families spending less per child. The formal tutoring industry collapsed --- that is beyond dispute --- but the money families saved on tutoring appears to have been redirected to other educational expenses rather than saved. This finding is classified CORRELATION because the proxy outcome variable and COVID confounding prevent a definitive causal statement.

The rest of this section walks through each causal edge: what was tested, how, what the result was, and what could make it wrong.

## Policy → Industry Collapse {#sec:edge-industry}

- **Classification:** CORRELATION
- **EP:** 0.56 (95% CI: 0.41--0.71)
- **Evidence:** 92--96% offline tutoring center closure rate; 50--70% revenue declines at New Oriental and TAL Education

The tutoring industry collapsed. This is the least controversial finding. Between 2021 and 2023, closure rates for offline tutoring centers reached **92--96%**, and the two largest publicly traded firms (New Oriental and TAL Education) saw revenues fall 50--70% [@huang2025biting; @chen2025bans]. @fig:tutoring-collapse shows the magnitude of the supply-side destruction.

![Panel (a): Revenue of New Oriental and TAL Education (billion USD), showing sharp declines in FY2022. Panel (b): Tutoring center closures and industry metrics showing 92--96% offline closure rates. The supply-side collapse is unambiguous, but does not directly measure household spending changes.](figures/fig07_tutoring_industry_collapse.pdf){#fig:tutoring-collapse width=90%}

The classification remains CORRELATION rather than DATA_SUPPORTED because the closure data come from industry reports and media sources (MEDIUM quality, score 53), not from a controlled study. The causal direction (policy caused closures, not reverse) is near-certain on substantive grounds, but the EP framework requires quantitative evidence of the mechanism, not just temporal co-occurrence. Approximately 3 million jobs were lost in the sector [@huang2025biting], equivalent to eliminating the entire workforce of a mid-sized European country's education system.

What could make this wrong: very little. The industry collapse is one of the best-documented regulatory effects in recent Chinese economic history. The remaining uncertainty is about completeness --- some firms may have restructured rather than closed, and the "closure" definition varies across sources.

## Industry Collapse → Reduced Tutoring Spending {#sec:edge-tutoring-spending}

- **Classification:** CORRELATION
- **EP:** 0.15 (95% CI: 0.05--0.25)
- **Evidence:** Education share of consumption dropped 0.7 percentage points; $z$-score of $-1.05$

The tutoring industry collapsed, but did families actually spend less on tutoring? The answer is: probably, but the evidence is surprisingly weak. The education/culture/recreation share of total household consumption dropped from **11.7%** in 2019 to a post-policy average of **11.0%** --- a 0.7 percentage point decline. However, this share recovered to **11.8%** by 2025, exceeding the pre-policy level.

More telling: when the education category's decline is compared against all eight NBS consumption categories, its $z$-score is only $-1.05$ --- meaning education spending was not uniquely affected relative to other categories. Healthcare, clothing, and transportation showed comparable or larger shifts during the same period. @fig:compositional shows this compositional analysis.

![Compositional analysis of the eight NBS consumption categories. The education/culture/recreation category (highlighted) shows a post-policy decline that is not statistically distinguishable from changes in other categories ($z = -1.05$). No evidence of a structural break specific to education spending.](figures/fig_p3_06_compositional.pdf){#fig:compositional width=85%}

The low EP (0.15) reflects two problems. First, the outcome variable is a proxy --- the "culture and recreation" component muddies any education-specific signal. Second, even the education-specific signal is not uniquely large relative to general consumption shifts. This edge sits just above the soft truncation threshold of 0.15.

What could make this wrong: post-2021 household microdata could show a sharp decline in tutoring spending that the aggregate proxy masks. The CIEFR-HS Wave 3, if released, would directly resolve this.

## Policy → Aggregate Spending: The ITS Model {#sec:edge-aggregate}

- **Classification:** CORRELATION
- **EP:** 0.20 (95% CI: 0.08--0.32)
- **Evidence:** ITS level shift $-483$ yuan ($1.7\sigma$ with systematics); COVID placebo FAIL

This is the central quantitative test. An Interrupted Time Series (ITS) model --- a standard technique for evaluating policies that affect everyone simultaneously, where the pre-policy trend serves as the control --- estimates whether spending shifted when the policy took effect.

The model specification is a segmented regression (a regression that allows the intercept to change at a specified date):

$$Y_t = \beta_0 + \beta_1 \cdot t + \beta_2 \cdot \mathbb{1}(t \ge 2021) + \varepsilon_t$$ {#eq:its}

where $Y_t$ is real per capita education/culture/recreation spending (2015 yuan), $t$ is the year, and $\beta_2$ captures the level shift at the policy date. The year 2020 is excluded to avoid COVID contamination, leaving 9 observations with 6 degrees of freedom. @fig:its-primary shows the model fit.

![Interrupted Time Series results for national, urban, and rural real education/culture/recreation spending. Solid lines show observed data; dashed lines show the counterfactual (pre-policy trend extrapolated forward). Shaded regions show the post-policy gap. The urban series shows the largest gap, consistent with higher urban tutoring participation rates.](figures/fig_p3_02_its_primary.pdf){#fig:its-primary width=90%}

The level shift estimates are reported in @tbl:its-results. The national estimate is **-483 yuan**, but the total uncertainty of $\pm 284$ yuan yields only $1.7\sigma$ significance --- well below the conventional $2\sigma$ threshold. Systematic uncertainty (how COVID is handled, where the intervention date is placed, the proxy variable correction) accounts for **80% of total variance**. More data points will not materially improve precision; the binding constraint is data quality, not sample size.

| Series | Level shift [yuan] | Stat. unc. | Syst. unc. | Total unc. | Significance | Classification |
|:-------|-------------------:|-----------:|-----------:|-----------:|:-------------|:--------------|
| National | $-483$ | $\pm 127$ | $\pm 254$ | $\pm 284$ | $1.7\sigma$ | CORRELATION |
| Urban | $-711$ | $\pm 197$ | $\pm 346$ | $\pm 398$ | $1.8\sigma$ | CORRELATION |
| Rural | $-191$ | $\pm 58$ | $\pm 128$ | $\pm 141$ | $1.4\sigma$ | CORRELATION |

Table: ITS level shift estimates with full uncertainty decomposition. Systematic uncertainty dominates (76--83% of total variance). No series reaches the conventional $2\sigma$ significance threshold. {#tbl:its-results}

An independent cross-check using an OLS income-conditioned counterfactual (which asks: "given income growth, how much should families have spent?") yields a national effect of **-382 yuan** ($-18.8\%$; 90% CI: $[-686, -73]$), 21% smaller than the ITS estimate. The two methods agree within 50%, but both are OLS-based, limiting independent corroboration.

What could make this wrong: if the proxy correction factor (education's share of the bundled category) is at the low end of its plausible range (60% rather than the assumed 75%), the true education-specific shift could be larger. Conversely, if post-COVID recovery in culture and recreation spending is faster than assumed, the education-specific shift could be zero.

## Refutation Tests: Three Passes, One Critical Failure {#sec:refutation}

Refutation tests check whether a statistical result holds up under different assumptions --- they stress-test the finding by asking "would we get this result even if the policy had nothing to do with it?" Each series underwent four tests. @tbl:refutation summarizes the national results; @fig:refutation visualizes them.

| Test | Result | What it checks |
|:-----|:-------|:---------------|
| Placebo treatment (2017, 2018, 2019) | PASS | Would a fake policy date produce a similar break? No --- max placebo 41 yuan, 11.8$\times$ smaller. |
| Random common cause (200 iterations) | PASS | Does adding a random confounder change the result? No --- mean shift only 0.6%. (Power caveat at $n = 9$.) |
| Data subset (drop 2 of 9, 200 iterations) | PASS | Is the result driven by one or two data points? No --- mean shift 3.8%, same sign 100% of iterations. |
| COVID-date placebo (intervention at 2020) | **FAIL** | Is the COVID break larger than the policy break? **Yes** --- $-591$ yuan ($p = 0.002$) vs. $-483$ yuan ($p = 0.023$). |

Table: Refutation battery results for the national series. The COVID-date placebo failure is the most consequential finding: COVID disruption produces a larger, more significant break than the policy itself. {#tbl:refutation}

![Refutation test results: placebo treatment estimates (left), data subset stability (center), and COVID-date placebo comparison (right). The COVID-date placebo break at 2020 ($-591$ yuan, $p = 0.002$) exceeds the policy break at 2021 ($-483$ yuan, $p = 0.023$).](figures/fig_p3_07_refutation.pdf){#fig:refutation width=90%}

The three core tests pass, which would normally support a DATA_SUPPORTED classification. The COVID-date placebo failure overrides this. If a researcher had placed the intervention at 2020 instead of 2021, they would have found a "policy effect" that is 22% larger and 10 times more statistically significant --- except there was no policy in 2020. A permutation test across all possible break dates finds that the 2021 break is not uniquely the largest ($p = 0.14$). This is why the classification remains CORRELATION: the observed break is real, but it cannot be confidently attributed to the policy rather than COVID.

## The Per-Birth Normalization: The Decisive Test {#sec:per-birth}

- **Classification:** DATA_SUPPORTED (for the demographic explanation)
- **EP for demographic confounding:** effectively 1.0 (the normalization eliminates the signal)

This is the single most important finding. China's births fell from 17.86 million in 2016 to **9.54 million in 2024** --- a 47% decline, equivalent to losing the entire school-age population of a country like Germany every few years. When aggregate education spending is divided by the number of births (a rough proxy for per-child spending intensity), the ITS level shift flips sign: **+13 yuan** ($p = 0.48$). The policy "effect" vanishes entirely.

![Panel (a): Annual births declining from 17.9 million (2016) to 9.0 million (2024), alongside stable compulsory education enrollment (157--161 million). Panel (b): Per-birth spending intensity shows a strong upward trend --- fewer children means higher per-child spending even if per-household spending is flat.](figures/fig06_per_child_spending.pdf){#fig:per-child width=90%}

The interpretation is straightforward: the aggregate spending decline is fully accounted for by demographic decline. Fewer children are entering the education pipeline. Per-child, families are spending as much as or more than before the ban. The tutoring money did not disappear --- it was redirected.

This aligns with household-level evidence from @chen2025bans, who found that families reduced tutoring spending but increased in-school spending by a comparable amount, with net expenditure approximately unchanged. Our macro-level finding independently corroborates their micro-level result.

What could make this wrong: the per-birth normalization is crude. Births in year $t$ do not translate into education spending in year $t$ --- there is a 6--7 year lag before children enter compulsory education. Enrollment data (which are stable at 157--161 million) would be a better denominator, but enrollment-normalized spending shows a similar pattern.

## The Compositional Ceiling: An Arithmetic Inconsistency {#sec:compositional-ceiling}

- **Classification:** DATA_SUPPORTED (for the arithmetic fact)

The observed aggregate decline of **23.7%** from the counterfactual trend substantially exceeds the **12%** compositional ceiling implied by the CIEFR-HS data [@wei2024household]. @fig:ciefr-decomp shows the pre-policy spending decomposition.

![Pre-policy (2019) decomposition of household education spending from the CIEFR-HS survey: in-school expenses 73%, extracurricular and tutoring 12%, other education expenses 15%. The Double Reduction policy targeted at most 12% of total household education costs.](figures/fig08_ciefr_spending_decomposition.pdf){#fig:ciefr-decomp width=70%}

The arithmetic is simple: if tutoring was 12% of spending, and the policy eliminated all of it with zero substitution, spending could fall by at most 12%. The observed 24% decline is twice that ceiling. At least half the decline must therefore originate from non-policy sources --- COVID disruption, demographic decline, or macroeconomic deceleration. This arithmetic inconsistency independently confirms that the aggregate spending decline cannot be predominantly policy-driven.

## Urban-Rural Differential {#sec:urban-rural}

- **Classification:** CORRELATION
- **EP:** 0.42

The urban ITS level shift ($-711$ yuan) is **3.7 times** larger than the rural shift ($-191$ yuan), directionally consistent with differential exposure: urban tutoring participation was approximately 47% versus 18% in rural areas pre-policy [@wei2024household]. @fig:urban-rural shows the divergence.

![Panel (a): Urban and rural real spending indexed to 2019=100. Urban shows a deeper COVID dip and a secondary 2022 dip absent in rural data. Panel (b): The absolute urban-rural gap widens post-policy, consistent with differential policy exposure.](figures/fig10_urban_rural_divergence.pdf){#fig:urban-rural width=90%}

However, this comparison is descriptive, not causal. The parallel trends assumption (that urban and rural spending would have moved together absent the policy) is violated: urban spending had a compound annual growth rate (CAGR) of $-0.31\%$ over 2016--2020 versus $+3.36\%$ for rural. The 2022 urban dip could reflect the Shanghai lockdown (a COVID effect) rather than the tutoring ban. The differential is suggestive but inconclusive.

## Underground Market and Price Effects {#sec:underground}

- **Classification:** HYPOTHESIZED
- **EP:** 0.14 (underground existence); 0.08 (price increase)

Underground tutoring is inherently unmeasurable. Cash transactions, underreporting by survey respondents, and the illegality of the activity make systematic quantification impossible. The evidence is entirely anecdotal: approximately 3,000 illegal operations detected in Q2 2022 [@sixthtone2022crackdown], media reports of 43--50% price increases for private tutors, and scattered enforcement data.

These edges remain HYPOTHESIZED because no quantitative dataset exists to test them. The underground market almost certainly exists --- regulatory displacement is a well-documented phenomenon across domains from drug policy to financial regulation --- but its size relative to the pre-policy formal market is unknown. This is not testable with available data. Resolution would require either systematic enforcement data (which governments rarely release) or survey designs specifically targeting underground activity.

## Public Spending Crowding-In {#sec:crowding-in}

- **Classification:** HYPOTHESIZED
- **EP:** 0.12

@liu2025crowdingin document that increased public education spending in China tends to crowd in (increase) rather than crowd out (decrease) household spending --- the opposite of what simple economic models predict. This mechanism could partially explain why total household spending did not decline despite tutoring elimination: as the government increased education budgets, families responded by spending more on complementary in-school expenses.

The evidence is macro-level correlation only. Public education expenditure and household education expenditure both trended upward over 2016--2023, but so did most fiscal and consumption categories. No causal test was feasible with available data. The mechanism is plausible on theoretical grounds and consistent with the micro-level findings of @chen2025bans, who documented increased in-school spending offsetting tutoring reductions.

## Uncertainty Decomposition {#sec:uncertainty}

Systematic uncertainty dominates the analysis. @tbl:uncertainty shows the full breakdown for the national ITS level shift. COVID handling specification alone accounts for **60.9%** of variance --- meaning the way the analyst handles the 2020 data point matters more than everything else combined.

| Source | Type | $\pm$ Shift [yuan] | Variance fraction |
|:-------|:-----|--------------------:|------------------:|
| COVID handling specification | Systematic | 221 | 60.9% |
| Statistical (bootstrap, 2000 reps) | Statistical | 127 | 20.1% |
| Intervention date (2021 vs. 2022) | Systematic | 96 | 11.3% |
| Proxy variable (education share 60--85%) | Systematic | 60 | 4.5% |
| Method disagreement (ITS vs. OLS) | Systematic | 51 | 3.2% |
| Pre-period window definition | Systematic | 8 | 0.1% |
| CPI deflator choice | Systematic | 7 | 0.1% |

Table: Uncertainty breakdown for the national ITS level shift ($-483$ yuan). COVID handling is the dominant source. Systematic uncertainty constitutes 80% of total variance. @fig:uncertainty-summary visualizes this decomposition. {#tbl:uncertainty}

![Full uncertainty summary showing the relative contribution of each source. The stacked bar at left shows the variance decomposition; the waterfall at right shows cumulative uncertainty buildup from statistical through each systematic source.](figures/fig_p3_12_uncertainty_summary.pdf){#fig:uncertainty-summary width=85%}

The practical implication: additional years of data will reduce statistical uncertainty but will not address the dominant systematic sources. The proxy problem and COVID confounding are structural, not statistical. Only new data types --- household microdata, sub-category NBS breakdowns --- can materially improve the analysis.

## DAG Discrimination {#sec:dag-discrimination}

The aggregate data cannot distinguish DAG 2 (displacement) from DAG 3 (compositional irrelevance) because both predict small or zero decline in total spending. The data reject DAG 1 (direct reduction) on two independent grounds: the per-birth normalization null result (@sec:per-birth) and the compositional ceiling inconsistency (@sec:compositional-ceiling).

The results are most consistent with a combination of DAGs 2 and 3: the formal tutoring industry collapsed, but the policy's scope was too narrow (targeting only 12% of spending) and substitution effects too strong to produce a detectable reduction in total per-child education expenditure. @chen2025bans reached the same conclusion using household-level panel data: tutoring spending declined but was offset by increased in-school spending.

## Model Diagnostics {#sec:diagnostics}

The ITS model passes standard diagnostics: Durbin-Watson statistics near 2 (no significant autocorrelation), Shapiro-Wilk $p > 0.36$ (normality not rejected), Breusch-Pagan $p > 0.07$ (no significant heteroscedasticity), and $R^2 > 0.89$ for all series. Signal injection tests (injecting known artificial effects and checking recovery) confirm model validity --- all injected signals were recovered within $2\sigma$.

These diagnostics are necessary but insufficient. With only 9 observations and 3 parameters, all diagnostic tests have very low statistical power (the ability to detect violations when they exist). The model could be misspecified in ways these tests cannot detect.


# Forward Projection {#sec:projection}

## Demographics, Not Policy, Will Drive the Spending Trajectory

The most important thing about the future of Chinese education spending has nothing to do with the Double Reduction policy. It is the birth rate. Births have fallen **47%** since 2016 and show no sign of stabilizing. This demographic collapse will reshape the education landscape far more profoundly than any tutoring ban --- within a decade, China will have roughly half as many school-age children as it had in 2016, regardless of what happens to per-child spending.

## Three Named Scenarios

Three scenarios propagate from the 2025 observed base value (2,986 yuan in real 2015 terms) using Monte Carlo simulation (10,000 iterations). They differ primarily in assumptions about whether the policy effect is real and persistent, and how quickly the demographic decline proceeds. @fig:scenarios shows the projected trajectories.

**"Mission Accomplished" (Scenario A, 15--25% conditional probability).** The policy worked, and the spending decline is real and persistent. Families have genuinely adjusted to spending less on education. Combined with steep demographic decline ($-7\%$/year births), per capita spending falls to a median of **2,391 yuan by 2035** ($-20\%$ from 2025, CAGR $-2.2\%$). This scenario is the least probable because it requires the aggregate signal to be predominantly policy-driven despite all the evidence of COVID confounding. It would also require families to resist the competitive pressure to substitute --- a prediction inconsistent with decades of education economics research on positional goods.

**"Status Quo / Displacement" (Scenario B, 45--55% conditional probability).** The most likely scenario. The tutoring industry collapsed, but spending displaced to underground channels and in-school expenses. Net household education spending is approximately flat per child: median **3,108 yuan by 2035** ($+4\%$, CAGR $+0.4\%$). This scenario is consistent with @chen2025bans's household-level finding of compositional shift, the per-birth normalization null result, and the 2025 observed recovery in education spending share (11.8%, exceeding the pre-policy 11.7%).

**"Pressure Cooker Returns" (Scenario C, 25--35% conditional probability).** Enforcement weakens as regulatory attention shifts elsewhere, and the competitive pressure that originally drove tutoring demand reasserts itself. Spending returns to growth: median **3,580 yuan by 2035** ($+20\%$, CAGR $+1.8\%$). Early signs are already visible --- in 2024, reports emerged of loosened restrictions on some forms of after-school programming [@voa2024easing].

![Three-scenario projection from 2025 to 2035 with 50% and 90% confidence intervals. Historical data provide context. All scenarios project spending below the ITS counterfactual (dashed line) because the pre-policy linear trend assumption is contradicted by demographic decline. Confidence bands widen substantially beyond 2029.](figures/scenario_comparison.pdf){#fig:scenarios width=90%}

| Metric | A: Mission Accomplished | B: Status Quo | C: Pressure Cooker |
|:-------|------------------------:|--------------:|-------------------:|
| 2030 median [yuan] | 2,677 | 3,137 | 3,326 |
| 2030 90% CI width [yuan] | 1,612 | 2,100 | 1,940 |
| 2035 median [yuan] | 2,391 | 3,108 | 3,580 |
| 10-year CAGR | $-2.2\%$ | $+0.4\%$ | $+1.8\%$ |
| Conditional probability | 15--25% | 45--55% | 25--35% |

Table: Scenario comparison at 2030 and 2035 horizons. Median spread across scenarios is 649 yuan (21% of baseline) at 2030, growing to 1,189 yuan (38%) at 2035. Within-scenario uncertainty exceeds between-scenario divergence. {#tbl:scenarios}

## Sensitivity Analysis: What Matters Most

Demographics dominate. @fig:tornado-proj ranks the six projection parameters by their impact on 2030 spending. The demographic decline rate has the largest absolute impact (**853 yuan** range), more than twice income growth (**385 yuan**) and more than four times policy persistence (**193 yuan**). The policy-controllable parameter ranks fourth out of six drivers.

![Sensitivity tornado chart ranking each parameter's impact on 2030 projected spending. Demographic decline rate dominates. Blue: exogenous parameters; orange: semi-controllable; red: controllable. Policy persistence, the only directly policy-relevant parameter, ranks fourth.](figures/sensitivity_tornado.pdf){#fig:tornado-proj width=80%}

The practical implication for policymakers: even if the Double Reduction policy is maximally effective, demographic decline will overwhelm its contribution to aggregate spending trends. Conversely, even if the policy has zero effect, the total education spending trajectory will decline simply because there are fewer children.

## Endgame Classification: Fork-Dependent

The endgame is classified as **fork-dependent**. The fork condition is a single binary question: does the aggregate spending dip represent a real per-child spending reduction, or is it entirely explained by demographics and COVID? The analysis could not resolve this ($p = 0.48$ for per-birth normalization). The data that would resolve it --- post-2021 household microdata --- do not yet exist in the public domain.

The coefficient of variation across scenario medians is 0.089 at 2030 and 0.16 at 2035, with within-scenario 90% CI widths exceeding 100% of scenario medians by 2035. Beyond the useful projection horizon of **2029** (4 years), projections are explicitly speculative.

## EP Decay: How Confidence Erodes With Time

Explanatory Power quantifies how much confidence the analysis warrants, and how that confidence degrades as projections extend into the future. The primary edge (Policy $\to$ Aggregate Spending) starts at EP = 0.20 with CORRELATION classification. CORRELATION edges decay at twice the standard rate (squared multipliers), reflecting the additional uncertainty of claims that have not survived causal refutation.

![EP decay chart. Left panel: projection confidence bands widening from 2025 to 2035, with EP tier boundaries marked. Right panel: EP decay curve showing the primary edge declining from 0.20 at Phase 3 to 0.008 at the long-term horizon, crossing both soft truncation (0.15) and hard truncation (0.05) thresholds.](figures/ep_decay_chart.pdf){#fig:ep-decay width=90%}

| Projection tier | Years from 2025 | Standard multiplier | CORRELATION multiplier | Effective EP |
|:----------------|----------------:|--------------------:|-----------------------:|-------------:|
| Empirical (Phase 3) | 0 | 1.00 | 1.00 | 0.200 |
| Near-term (1--3 yr) | 1--3 | 0.70 | 0.49 | 0.098 |
| Mid-term (3--7 yr) | 3--7 | 0.40 | 0.16 | 0.032 |
| Long-term (7--10 yr) | 7--10 | 0.20 | 0.04 | 0.008 |

Table: EP decay schedule. CORRELATION classification applies squared multipliers. EP falls below soft truncation (0.15) by year 1 and below hard truncation (0.05) by mid-term. Projections beyond 2029 are explicitly speculative. {#tbl:ep-decay}

The EP decay visualization in @fig:ep-decay is the core epistemic message of this report: what we know with modest confidence about the present degrades rapidly to near-zero confidence about the future. At the long-term horizon, EP = 0.008 --- meaning we have essentially no evidence-based basis for projecting the policy's contribution to spending trends beyond 2032.

## Chain-Level Joint EP

@tbl:chain-ep confirms that no multi-step causal chain supports a chain-level claim.

| Chain | Edges | Joint EP | Status |
|:------|:------|:---------|:-------|
| DAG 1: Policy $\to$ Industry $\to$ Tutoring $\to$ Total | $0.56 \times 0.15 \times 0.02$ | 0.0017 | HARD TRUNCATION |
| DAG 2: Policy $\to$ Underground $\to$ Prices | $0.14 \times 0.08$ | 0.011 | HARD TRUNCATION |
| DAG 3: Public $\to$ Crowding-In | 0.12 (single edge) | 0.12 | SOFT TRUNCATION |

Table: Chain-level Joint EP values. All multi-step chains fall below hard truncation (0.05). Even the single-edge DAG 3 chain is below soft truncation. No chain-level causal claim is supportable with available data. {#tbl:chain-ep}


# Audit Trail {#sec:audit}

## Data Provenance

All 13 acquired datasets are registered in `data/registry.yaml` with SHA-256 hashes verified during Phase 5 verification. The primary data source is the National Bureau of Statistics of China's annual statistical communiques [@nbs2025communique], supplemented by World Bank indicators [@worldbank2024wdi] and academic survey data [@wei2024household]. All monetary values are deflated to 2015 real terms using the NBS CPI index.

Back-calculated 2016--2018 values (reconstructed from year-on-year growth rates published in later communiques) carry approximately $\pm 2$--$3\%$ error, documented in the data quality assessment.

## Methodology Choices and Alternatives

@tbl:methods documents the key analytical decisions, their justifications, and the alternatives that were considered and rejected.

| Choice | Justification | Alternatives considered |
|:-------|:-------------|:-----------------------|
| ITS over Difference-in-Differences | No untreated control group; policy was nationwide | DiD requires parallel trends (violated for urban-rural) |
| 2020 exclusion over COVID indicator | Preserves degrees of freedom; algebraically identical | COVID indicator tested as sensitivity check |
| Edge-level assessment over chain-level claims | All chain Joint EP $< 0.05$ | Chain-level claims would overstate evidence |
| 3-parameter over 6-parameter ITS | 9 observations; 6-parameter model overfits (3 df) | 6-parameter model tested as sensitivity |
| Education CPI sub-index for deflation | Closest proxy for education cost inflation | Overall CPI tested; 1.5 pp cumulative difference |

Table: Key methodological decisions. Each choice was stress-tested through sensitivity analysis; none materially altered the conclusions. {#tbl:methods}

## Verification Summary

Phase 5 verification produced 5/8 programs PASS, 1/8 PARTIAL, and 2/8 N/A (not applicable due to data constraints). Key verification results:

- The ITS level shift ($-483$ yuan) was reproduced exactly using an independent numpy-based OLS implementation (not the statsmodels library used in the primary analysis).
- All 4 refutation test outcomes were independently confirmed.
- All EP values across all phases were verified as arithmetically correct through the multiplicative chain formula.
- SHA-256 hashes matched for all 13 acquired datasets.
- No Category A (must-resolve) or Category B (must-fix) issues were found.

The PARTIAL result was for the sensitivity analysis verification, where the verifier confirmed all tested sensitivities but noted that additional sensitivities (e.g., alternative deflator indices) could have been explored.

## EP Propagation Across Phases

@tbl:ep-trajectory traces how the primary edge's EP evolved as evidence accumulated through the analysis phases.

| Phase | EP | Key event |
|:------|---:|:----------|
| Phase 0 (Discovery) | 0.30 | Initial qualitative estimate based on literature review |
| Phase 1 (Strategy) | 0.30 | Unchanged; downscoped to edge-level assessment |
| Phase 3 (Analysis) | 0.20 | COVID placebo FAIL reduced relevance dimension |
| Phase 4 near-term | 0.098 | CORRELATION $2\times$ decay applied |
| Phase 4 mid-term | 0.032 | Below hard truncation threshold |
| Phase 4 long-term | 0.008 | Speculative territory |

Table: EP trajectory for the primary edge. EP declines monotonically, reflecting accumulated evidence against clean policy attribution. {#tbl:ep-trajectory}

## Reference Analysis Comparison

@tbl:reference compares this analysis with the two most relevant published studies.

| Dimension | This analysis | @huang2025biting | @chen2025bans |
|:----------|:-------------|:----------------|:-------------|
| Data | NBS macro aggregates (proxy) | City-level job postings, firm data | Nationally representative household panel |
| Method | ITS, OLS counterfactual | DiD with continuous treatment | Panel pre-post with income stratification |
| Scope | Total education expenditure | Labor market and firm dynamics | Tutoring spending, in-school spending, outcomes |
| Finding | Not distinguishable from COVID/demographics | 3M+ jobs lost; 89% posting decline | Tutoring down, in-school up; inequality effects |
| Agreement | Consistent on industry collapse and compositional shift | Consistent | Consistent; macro results corroborate micro findings |

Table: Comparison with reference analyses. All three agree on the formal tutoring industry collapse. This analysis's finding of no detectable per-child spending reduction is consistent with @chen2025bans's finding of compositional shift at the household level. {#tbl:reference}

## Human Gate Decision

Phase 5 verification was approved through human gate review. The human reviewer confirmed the CORRELATION classification for the primary edge, the fork-dependent endgame classification, and the recommendation to prioritize CFPS post-2021 microdata acquisition.


# Appendices {-}

## A. Code References {#sec:appendix-code}

| Script | Phase | Purpose |
|:-------|:------|:--------|
| `phase0_discovery/scripts/acquire_data.py` | 0 | Data acquisition from NBS, World Bank, academic sources |
| `phase0_discovery/scripts/assess_quality.py` | 0 | Data quality scoring (completeness, consistency, bias, granularity) |
| `phase2_exploration/scripts/explore.py` | 2 | Exploratory data analysis, distribution checks, time series plots |
| `phase3_analysis/scripts/its_analysis.py` | 3 | ITS model estimation, refutation tests, uncertainty decomposition |
| `phase3_analysis/scripts/compositional_analysis.py` | 3 | 8-category compositional analysis, $z$-score computation |
| `phase3_analysis/scripts/ep_assessment.py` | 3 | EP calculation for all edges and chains |
| `phase4_projection/scripts/project_scenarios.py` | 4 | Monte Carlo scenario projection, sensitivity tornado |
| `phase4_projection/scripts/ep_decay.py` | 4 | EP decay chart generation |
| `phase5_verification/scripts/verify_its.py` | 5 | Independent ITS reproduction using numpy |
| `phase5_verification/scripts/verify_refutation.py` | 5 | Independent refutation test confirmation |

Table: Analysis scripts with phase assignments and purposes. All scripts run through `pixi run py <script>`. {#tbl:code-refs}

## B. Statistical Details {#sec:appendix-stats}

### ITS Model Diagnostics

| Diagnostic | National | Urban | Rural | Interpretation |
|:-----------|--------:|------:|------:|:---------------|
| Durbin-Watson | 1.98 | 2.12 | 1.87 | No significant autocorrelation |
| Shapiro-Wilk $p$ | 0.42 | 0.36 | 0.51 | Normality not rejected |
| Breusch-Pagan $p$ | 0.09 | 0.07 | 0.14 | No significant heteroscedasticity |
| $R^2$ | 0.92 | 0.89 | 0.94 | Good fit |
| Observations | 9 | 9 | 9 | 2020 excluded |
| Degrees of freedom | 6 | 6 | 6 | 3 parameters estimated |

Table: ITS model diagnostic statistics. All diagnostics pass conventional thresholds, but power is very low at $n = 9$. {#tbl:diagnostics}

### Bootstrap Distributions

@fig:bootstrap shows the bootstrap distribution (2,000 replications) for the national ITS level shift, confirming the $\pm 127$ yuan statistical uncertainty.

![Bootstrap distribution of the national ITS level shift (2,000 replications). The distribution is approximately normal, centered at $-483$ yuan with standard deviation of 127 yuan. The 95% confidence interval ($-732$ to $-234$ yuan) does not include zero, but this excludes systematic uncertainty.](figures/fig_p3_10_bootstrap.pdf){#fig:bootstrap width=75%}

### Sensitivity Tornado (Phase 3)

@fig:tornado-p3 shows the Phase 3 sensitivity tornado for the ITS level shift, distinct from the Phase 4 projection sensitivity in @fig:tornado-proj.

![Phase 3 sensitivity tornado for the national ITS level shift. COVID handling specification dominates, followed by intervention date choice and proxy variable correction. Statistical uncertainty ranks second.](figures/fig_p3_11_tornado.pdf){#fig:tornado-p3 width=80%}

## C. Data Quality Report {#sec:appendix-quality}

Full data quality assessment is documented in `phase0_discovery/exec/DATA_QUALITY.md`. Key quality scores by dimension:

| Dataset | Completeness | Consistency | Bias | Granularity | Overall |
|:--------|------------:|:-----------:|-----:|------------:|--------:|
| ds\_001 (NBS Education) | 75 | 70 | 60 | 65 | 68 |
| ds\_002 (CIEFR-HS) | 50 | 65 | 55 | 60 | 58 |
| ds\_006 (Demographics) | 90 | 80 | 70 | 70 | 78 |
| ds\_009 (Income) | 90 | 85 | 75 | 75 | 81 |
| ds\_011 (Underground) | 25 | 30 | 40 | 35 | 33 |

Table: Data quality scores by dimension (0--100). The underground tutoring dataset (ds\_011) scores LOW across all dimensions, reflecting its anecdotal nature. {#tbl:quality-detail}

## D. Experiment Log {#sec:appendix-log}

The complete experiment log is maintained in `experiment_log.md`. Key decisions documented:

- **Phase 0:** Decision to use NBS "education, culture and recreation" as primary outcome despite proxy limitation; CFPS post-2021 acquisition attempted and failed; 9 binding data quality constraints established.
- **Phase 1:** Formal downscoping from chain-level to edge-level assessment after preliminary Joint EP calculation; ITS selected over DiD due to absence of control group.
- **Phase 2:** Pre-existing downward trend in CIEFR-HS per-student spending identified; 2020 COVID exclusion confirmed as necessary.
- **Phase 3:** COVID-date placebo test added as supplementary refutation after exploratory analysis revealed the 2020 break magnitude; per-birth normalization identified as decisive test; classification downgraded from potential DATA_SUPPORTED to CORRELATION.
- **Phase 4:** Three scenarios designed around the fork condition; demographic decline rate confirmed as dominant sensitivity parameter; useful projection horizon set at 2029.
- **Phase 5:** All quantitative results independently reproduced; no Category A or B issues; human gate approved.

# References {-}
