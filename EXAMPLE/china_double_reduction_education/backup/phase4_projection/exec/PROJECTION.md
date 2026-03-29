# Projection: china_double_reduction_education

**Analysis:** china_double_reduction_education
**Question:** Did China's Double Reduction policy truly reduce household education expenditure?
**Generated:** 2026-03-29
**Agent:** projector_agent (Phase 4)

---

## Summary

Forward projection of household education spending under three scenarios yields wide, overlapping confidence bands driven by exogenous macroeconomic factors (income growth, demographic decline) rather than policy parameters. The endgame classification is **Fork-dependent**: whether spending remains below the pre-policy trajectory or rebounds depends primarily on the unmeasurable underground market displacement rate and the real income growth path -- neither of which the policy directly controls. The useful projection horizon is **2032** (7 years); beyond that, EP decays below the hard truncation threshold (0.05) and projections become speculative. All projections are conditional extrapolations from empirically weak foundations (primary edge EP = 0.20, CORRELATION classification, 1.7 sigma with systematics), and none should be interpreted as forecasts.

---

## Pre-Projection Audit

### Established Relationships

| Causal Edge | Phase 3 EP | Classification | Effect Size | CI (90%) | Input Type |
|-------------|-----------|---------------|-------------|----------|------------|
| Policy -> Aggregate Spending (net) | 0.20 | CORRELATION | -483 yuan | [-793, -174] | Empirical (ITS) |
| Policy -> Industry Collapse | 0.56 | CORRELATION | 92-96% closure rate | Literature only | Literature-based |
| Industry Collapse -> Reduced Tutoring | 0.15 | CORRELATION | -0.7pp share drop | z = -1.05 | Empirical (weak) |
| Reduced Tutoring -> Total Expenditure | 0.02 | HYPOTHESIZED | Eliminated by demographic normalization | p = 0.48 | Assumed (no signal) |
| Competitive Pressure -> Inelastic Demand | 0.42 | CORRELATION | Pre-policy evidence only | N/A | Literature-based |
| Income -> Differential Access | 0.42 | CORRELATION | Urban 3.7x > Rural shift | Parallel trends violated | Empirical (descriptive) |
| Policy -> Underground Market | 0.14 | HYPOTHESIZED | Anecdotal only | N/A | Assumed |
| Underground -> Higher Prices | 0.08 | HYPOTHESIZED | +43-50% price increase | Media reports | Assumed |
| Public Spending -> Crowding-In | 0.12 | HYPOTHESIZED | >4% GDP maintained | N/A | Literature-based |

### Chain-Level Joint EP

All multi-step causal chains remain below hard truncation (Joint EP < 0.05). No chain-level causal claims are supportable. Projections inherit this constraint: they are scenario-conditional extrapolations of aggregate trends, not causal predictions of policy effects.

### Quality Constraints Inherited from Phase 0/3

1. **PRIMARY OUTCOME IS A PROXY.** NBS "education, culture and recreation" bundles non-education spending. Projection uncertainty inflated accordingly (proxy variable systematic: 60-85% education share range).
2. **NO POST-POLICY MICRODATA.** Cannot validate compositional assumptions for projection.
3. **UNDERGROUND TUTORING IS UNMEASURABLE.** Underground displacement parameter uses a wide uniform prior (0-60%).
4. **COVID CONFOUNDING IS DOMINANT.** COVID handling accounts for 61% of Phase 3 systematic variance. Projection base value (2025) partially absorbs this, but structural uncertainty persists.
5. **DEMOGRAPHIC DECLINE CONFOUNDS AGGREGATE.** Per-birth normalization eliminates the Phase 3 signal. Projections must model demographic decline as an independent driver.
6. **SYSTEMATIC UNCERTAINTY DOMINATES (80%).** Now propagated into MC as a correlated bias term (N(0, 254 yuan) drawn once per iteration, constant across years). More observations will not improve projection precision. Better data (household microdata) or better identification is needed.

### Assumption Boundaries

| Relationship | Valid Under | Would Change If |
|-------------|-----------|----------------|
| Income elasticity ~1.0 | Stable macro environment, no major recession | Property market collapse, youth unemployment surge, or structural shift in consumption preferences |
| Demographic decline -6%/yr | Continuation of current fertility trends | Pronatalist policy success, immigration, or fertility stabilization |
| Policy persistence 0-80% | Current enforcement posture maintained | Major policy reversal, new regulation wave, or enforcement collapse |
| Underground displacement 0-60% | Current informal market dynamics | Systematic crackdown success, digital surveillance expansion, or complete enforcement failure |

---

## Scenario Simulations

### Projection Model

The projection model propagates from the 2025 observed value (2,986 yuan, real 2015 terms) using six stochastic parameters and two noise terms:

$$Y(t) = Y_{2025} \cdot (1 + g \cdot \eta)^t \cdot (1 + \delta)^t + Y_{2025} \cdot \gamma \cdot t + \Delta\pi(t) + \beta + \varepsilon(t)$$

where:
- $Y_{2025}$ = 2,986 yuan (observed 2025 value, already embeds the current policy effect)
- $g$ = real income growth rate, $\eta$ = income elasticity of education spending
- $\delta$ = demographic decline rate (full pass-through to per-capita aggregate)
- $\gamma$ = culture/recreation recovery rate (proxy confound)
- $\Delta\pi = L \cdot (p - 1) \cdot (1 - u)$ = marginal policy deviation from 2025 baseline, where $L$ = -483 yuan (ITS level shift), $p$ = policy persistence fraction, $u$ = underground displacement fraction. When $p = 1$, the current embedded effect persists unchanged ($\Delta\pi = 0$). When $p < 1$, the effect partially reverses (spending rebounds). When $p > 1$, the effect deepens. The underground displacement fraction $u$ offsets any policy savings recaptured by informal markets.
- $\beta \sim N(0, 254)$ = correlated systematic bias, drawn once per MC iteration and applied to all years (reflects persistent measurement biases in the NBS proxy variable)
- $\varepsilon(t) \sim N(0, 127 \cdot \sqrt{t})$ = independent statistical noise (bootstrap SE, scaled by projection distance)

**Key model corrections (v2):** (1) The policy term models only the *marginal deviation* from the 2025 observed state, avoiding double-counting the policy effect already embedded in $Y_{2025}$. (2) Demographic decline uses full pass-through (no dampening factor). (3) The policy effect is constant over time (no unjustified deepening trend). (4) Systematic uncertainty is propagated as a correlated term across all projection years.

10,000 Monte Carlo iterations per scenario. Random seed: 42. All scenarios confirmed converged (running-mean tail deviation < 0.5% of final mean).

---

### Scenario A: Policy Succeeds

**Narrative:** The Double Reduction policy effect is real and persists near current levels. Formal tutoring remains suppressed, underground market is contained by enforcement. Spending declines from the 2025 base due to demographic forces and minimal policy reversal. Demographic decline reinforces the downward trajectory.

**Conditional probability:** Unlikely (15-25%). This requires the aggregate signal to be predominantly policy-driven despite COVID confounding evidence, and underground markets to remain small -- both contradicted by available evidence.

| Parameter | Distribution | Rationale |
|-----------|-------------|-----------|
| Income growth | N(3.5%, 1.0%) | Slower growth assumption |
| Income elasticity | N(0.9, 0.10) | Lower responsiveness |
| Policy persistence | Beta(mean=0.8, std=0.15) on [0, 1.5] | Most of the -483 yuan shift is real; near-full persistence means minimal reversal from 2025 state |
| Demographic decline | N(-7%, 2%) | Steeper decline |
| Underground displacement | Uniform(0.0, 0.15) | Minimal underground activity |
| Culture/rec recovery | N(1.0%, 0.5%) | Modest recovery |

**Results (real 2015 yuan):**

| Year | Median | 50% CI | 90% CI | 95% CI |
|------|--------|--------|--------|--------|
| 2026 | 2,985 | [2,785, 3,186] | [2,490, 3,482] | [2,392, 3,579] |
| 2030 | 2,677 | [2,345, 3,007] | [1,875, 3,487] | [1,716, 3,643] |
| 2035 | 2,391 | [1,927, 2,861] | [1,278, 3,575] | [1,091, 3,831] |

Under this scenario, spending *declines* (median -20% over 10 years, CAGR -2.2%) due to steep demographic decline with full pass-through and minimal policy reversal. The decline is more pronounced than in v1 because demographic effects are no longer dampened (30% factor removed) and the policy double-counting bias has been corrected. Spending remains well below the ITS counterfactual (4,596 yuan at 2030).

---

### Scenario B: Status Quo (Displacement)

**Narrative:** The policy reduced formal tutoring, but spending displaced to underground channels, non-academic enrichment, in-school supplementary costs, and digital platforms. Net household education burden is unchanged or slightly lower. Demographic decline is the dominant secular trend driving per-capita aggregate numbers. This is the most probable scenario based on Phase 3 evidence: the aggregate signal is a mix of COVID recovery, demographics, and a modest (possibly zero) policy contribution.

**Conditional probability:** Likely (45-55%). Consistent with Chen et al. (2025) findings of compositional shift (tutoring down, in-school costs up), the per-birth normalization result (p=0.48), and the COVID placebo failure.

| Parameter | Distribution | Rationale |
|-----------|-------------|-----------|
| Income growth | N(4.0%, 1.5%) | Current trend continuation |
| Income elasticity | N(1.0, 0.15) | Literature central value |
| Policy persistence | Beta(mean=0.3, std=0.25) on [0, 1.5] | Small real policy effect; pol_p=0.3 means 70% reversal from current state, adding back ~270 yuan |
| Demographic decline | N(-6%, 3%) | Current trend with uncertainty |
| Underground displacement | Uniform(0.0, 0.60) | Wide uniform prior reflecting unmeasurability |
| Culture/rec recovery | N(1.5%, 1.0%) | Gradual normalization |

**Results (real 2015 yuan):**

| Year | Median | 50% CI | 90% CI | 95% CI |
|------|--------|--------|--------|--------|
| 2026 | 3,202 | [2,985, 3,414] | [2,681, 3,736] | [2,566, 3,840] |
| 2030 | 3,137 | [2,721, 3,578] | [2,135, 4,236] | [1,962, 4,456] |
| 2035 | 3,108 | [2,448, 3,834] | [1,619, 5,089] | [1,374, 5,592] |

Spending is approximately flat in median terms (median +4% over 10 years, CAGR +0.4%), as income growth and policy reversal approximately offset demographic decline. The 90% CI widens substantially by 2035, spanning from near-halving to strong recovery. Confidence bands are wider than v1 due to inclusion of correlated systematic uncertainty (254 yuan) and full demographic pass-through.

---

### Scenario C: Rebound

**Narrative:** Spending returns to or exceeds the pre-policy trajectory. Underground tutoring expands beyond containment, enforcement weakens as political attention shifts, new enrichment channels (AI tutoring, overseas programs, "study abroad prep") emerge. Competitive pressure (Gaokao, employment anxiety) reasserts and drives spending upward. The aggregate dip was predominantly COVID-driven and self-corrects.

**Conditional probability:** Plausible (25-35%). Consistent with DAG 2 (regulatory displacement) and the 2025 observed recovery (education share at 11.8%, exceeding pre-policy 11.7%).

| Parameter | Distribution | Rationale |
|-----------|-------------|-----------|
| Income growth | N(4.5%, 1.5%) | Stronger growth |
| Income elasticity | N(1.1, 0.12) | Higher elasticity (catch-up) |
| Policy persistence | Beta(mean=0.0, std=0.15) on [0, 1.5] | No real policy effect; pol_p near 0 means near-full reversal, adding back ~483 yuan |
| Demographic decline | N(-5%, 2%) | Slower decline (stabilizing) |
| Underground displacement | Uniform(0.0, 0.60) | Wide uniform prior reflecting unmeasurability |
| Culture/rec recovery | N(2.0%, 1.0%) | Strong proxy inflation |

**Results (real 2015 yuan):**

| Year | Median | 50% CI | 90% CI | 95% CI |
|------|--------|--------|--------|--------|
| 2026 | 3,115 | [2,892, 3,348] | [2,570, 3,668] | [2,476, 3,772] |
| 2030 | 3,326 | [2,930, 3,722] | [2,396, 4,336] | [2,217, 4,536] |
| 2035 | 3,580 | [2,984, 4,269] | [2,182, 5,435] | [1,921, 5,897] |

Spending grows moderately (median +20% over 10 years, CAGR +1.8%), driven by stronger income growth and near-full policy reversal. Growth is more modest than v1 because full demographic pass-through creates a stronger headwind. By 2035, the median exceeds the 2025 base by 594 yuan but remains below the ITS counterfactual.

---

### Scenario Summary Table

| Metric | A: Policy Succeeds | B: Status Quo | C: Rebound |
|--------|-------------------|---------------|------------|
| 2030 median (yuan) | 2,677 | 3,137 | 3,326 |
| 2030 90% CI width | 1,612 | 2,100 | 1,940 |
| 2035 median (yuan) | 2,391 | 3,108 | 3,580 |
| 2035 90% CI width | 2,297 | 3,470 | 3,252 |
| 10-yr CAGR | -2.2% | +0.4% | +1.8% |
| Conditional probability | 15-25% | 45-55% | 25-35% |
| Relative to ITS counterfactual 2030 | 58% | 68% | 72% |

**Key observations:** (1) All three scenarios project spending well below the ITS counterfactual at 2030 (4,596 yuan), because the counterfactual assumes the pre-policy linear trend (+183 yuan/year) would have continued indefinitely -- an assumption contradicted by demographic decline. (2) Confidence bands are substantially wider than v1 due to inclusion of correlated systematic uncertainty (254 yuan bias term) and full demographic pass-through (no 30% dampening). (3) Scenario A now projects *declining* spending because full demographic pass-through (-7%/yr births) dominates the income growth effect when policy persistence is high (minimal reversal). (4) The median spread across scenarios at 2030 is 649 yuan (21% of baseline median), growing to 1,189 yuan (38%) at 2035.

---

## Sensitivity Analysis

### Tornado Chart

![Sensitivity tornado chart showing impact of each variable on 2030 projected spending, ranked by magnitude. Income growth rate has the largest impact, followed by demographic decline rate and culture/recreation recovery. Policy persistence ranks fourth. Variables color-coded: red = controllable, orange = semi-controllable, blue = exogenous.](figures/sensitivity_tornado.pdf)

### Variable Ranking

| Rank | Variable | Impact on 2030 (yuan) | Abs Range | Classification |
|------|----------|----------------------|-----------|---------------|
| 1 | Demographic decline rate | [-399, +454] | 853 | Exogenous |
| 2 | Income growth rate | [-187, +198] | 385 | Exogenous |
| 3 | Culture/rec recovery (proxy confound) | [-149, +149] | 299 | Exogenous |
| 4 | Policy persistence | [+97, -97] | 193 | Controllable |
| 5 | Income elasticity | [-76, +78] | 154 | Exogenous |
| 6 | Underground displacement | [+68, -68] | 135 | Semi-controllable |

### Key Levers

**1. Demographic decline rate (Exogenous, impact: 853 yuan).** The single most influential parameter after correcting to full pass-through (v1 used an unjustified 30% dampening factor). A 3pp change in demographic decline rate shifts the 2030 projection by +/-400-450 yuan. With births declining ~6%/year, the school-age population shrinks, reducing aggregate per-capita education spending mechanically. This is the force that Phase 3 found could explain the entire aggregate signal (per-birth normalization p=0.48). Pronatalist policies could influence this, but not education policy.

**2. Income growth rate (Exogenous, impact: 385 yuan).** The second largest driver. A 1.5pp change in real income growth shifts the 2030 projection by +/-190 yuan. This reflects the near-perfect pre-policy correlation (r=0.97) between income and education spending. Neither the Double Reduction policy nor any education-specific intervention controls macroeconomic growth.

**3. Culture/recreation recovery (Exogenous, impact: 299 yuan).** This is a proxy measurement artifact, not a real education spending driver. As post-COVID culture and recreation spending recovers, the NBS proxy category inflates, making education spending appear higher than it is. This underscores the fundamental data quality limitation.

**4. Policy persistence (Controllable, impact: 193 yuan).** The only directly policy-controllable parameter ranks fourth. In the corrected model, policy persistence represents the fraction of the original level shift that persists; varying it from 0.05 to 0.55 shifts the 2030 projection by +/-97 yuan. Note the sign: *higher* persistence means the current (lower) spending state persists, so the impact is negative. This reflects the weak empirical foundation: at 1.7 sigma with systematics, the policy signal is small relative to macroeconomic forces.

**5. Underground displacement (Semi-controllable, impact: 135 yuan).** Larger impact than v1 due to corrected model structure. Even so, enforcement outcomes have modest effects on total spending because the policy-attributable level shift is itself uncertain.

### Interaction Check

Pairwise interactions among the top 3 variables were tested:

| Pair | Additive Expectation | Joint Effect | Interaction |
|------|---------------------|-------------|-------------|
| Demographic decline x Income growth | +651 yuan | +685 yuan | 5.2% (linear) |
| Demographic decline x Culture/rec recovery | +603 yuan | +603 yuan | 0.0% (linear) |
| Income growth x Culture/rec recovery | +347 yuan | +347 yuan | 0.0% (linear) |

No nonlinear interactions exceed the 10% threshold. The projection model is approximately additive in its parameters, which is expected given the multiplicative structure with small perturbations.

---

## Endgame Classification

**Category: Fork-dependent**

The classification is Fork-dependent, not Robust, based on the following evidence:

1. **Scenario divergence is moderate and growing.** The coefficient of variation across scenario medians is 0.089 at 2030 and 0.16 at 2035. While below the 0.50 threshold for classic fork-dependence, the divergence is growing with projection distance and the within-scenario uncertainty is large (90% CI widths of 2,100-3,470 yuan at 2035).

2. **90% CI overlap between extreme scenarios is substantial but incomplete.** At 2035, the overlap between Scenario A (90% CI: [1,278, 3,575]) and Scenario C (90% CI: [2,182, 5,435]) is 1,393 yuan, representing 50% of the average span. The wider bands from v2 (systematic uncertainty propagation, full demographic pass-through) increase overlap but the scenarios still produce distinguishable central tendencies (median spread of 1,189 yuan at 2035).

3. **The fork condition is identifiable.** The system outcome depends critically on one binary question: **Does the aggregate spending dip represent a real per-child spending reduction (policy effect), or is it entirely explained by demographic decline and COVID disruption?** Phase 3 could not resolve this question (per-birth normalization: p=0.48). The answer determines whether the trajectory follows Scenario A or Scenario C, with Scenario B as the intermediate.

4. **The system does not meet Robust criteria.** The 90% CI width exceeds 30% of the median at the 2035 horizon for all scenarios (Scenario B: 90% CI width = 3,470 yuan vs median = 3,108 yuan = 112%).

5. **The system is not Unstable.** Variance grows approximately linearly with projection distance, not super-linearly. There are natural bounds: spending cannot fall below zero, and it is constrained by household income (education share historically 9.5-12.0% of total consumption).

6. **The system is not Equilibrium.** No convergence toward a common attractor is observed. Scenarios diverge monotonically.

### Fork Variables

| Fork Variable | Branch A (Policy Succeeds) | Branch C (Rebound) | Observable by |
|--------------|--------------------------|-------------------|---------------|
| Per-child spending trend | Declining in real terms | Returning to growth | CFPS/CIEFR-HS post-2021 microdata (not yet available) |
| Underground market scale | Contained (<10% of formal) | Large (30-50% of formal) | No systematic measurement exists |
| Enforcement sustainability | Maintained/strengthened | Weakened as political attention shifts | Policy announcements, enforcement statistics |

---

## EP Decay

### Confidence Band Chart

![EP decay chart with two panels. Left: projection confidence bands showing widening uncertainty from 2025 to 2035, with EP decay tier boundaries marked. Right: EP decay curve showing the primary edge EP declining from 0.20 at Phase 3 to 0.008 at the long-term horizon, crossing both soft truncation (0.15) and hard truncation (0.05) thresholds.](figures/ep_decay_chart.pdf)

### EP Decay Schedule

The primary edge (Policy -> Aggregate Spending) has Phase 3 EP = 0.20 with CORRELATION classification. CORRELATION edges decay at 2x the standard rate (squared multipliers):

| Projection Tier | Years from 2025 | Standard Multiplier | CORRELATION Multiplier | Effective EP |
|----------------|-----------------|---------------------|----------------------|-------------|
| Empirical (Phase 3) | 0 | 1.00 | 1.00 | 0.200 |
| Near-term (1-3 yr) | 1-3 | 0.70 | 0.49 | 0.098 |
| Mid-term (3-7 yr) | 3-7 | 0.40 | 0.16 | 0.032 |
| Long-term (7-10 yr) | 7-10 | 0.20 | 0.04 | 0.008 |

**EP falls below soft truncation (0.15) by year 1 of projection.** This is because the starting EP is already low (0.20), and the CORRELATION classification applies a steep decay penalty. By the mid-term horizon (2028-2032), EP is 0.032 -- below hard truncation for chain-level claims.

### Useful Projection Horizon

**2029** (4 years from 2025).

Justification: At 2029, the 90% CI of the baseline scenario (B) spans approximately 1,822 yuan, exceeding 50% of the plausible outcome range (1,500-5,000 yuan = 3,500 yuan range). Beyond 2029, the confidence bands are so wide that the projection adds no information beyond "spending will be somewhere in the historically observed range."

This is notably shorter than v1 (which reported 2032) because:
1. The starting EP is low (0.20) due to COVID confounding
2. CORRELATION classification imposes 2x decay
3. The proxy variable introduces irreducible measurement uncertainty
4. Macroeconomic parameters (income, demographics) dominate the projection and are themselves uncertain
5. Correlated systematic uncertainty (254 yuan bias term, new in v2) widens all bands uniformly
6. Full demographic pass-through (no 30% dampening) amplifies uncertainty propagation

### EP Across Analysis Phases

| Phase | EP (Policy -> Agg. Spending) | Key Change |
|-------|------|------------|
| Phase 0 (Discovery) | 0.30 | Initial qualitative assessment |
| Phase 1 (Strategy) | 0.30 | Unchanged; downscoping to edge-level |
| Phase 3 (Analysis) | 0.20 | COVID placebo FAIL; relevance decreased |
| Phase 4 near-term | 0.098 | CORRELATION 2x decay applied |
| Phase 4 mid-term | 0.032 | Below hard truncation |
| Phase 4 long-term | 0.008 | Speculative |

---

## Tipping Points and Phase Transitions

### Threshold Scan

| Threshold | Parameter | Behavioral Change | Current Position | Proximity EP |
|-----------|-----------|-------------------|-----------------|-------------|
| Income growth < 1% real | Income growth rate | Spending stagnation or decline regardless of policy | Current ~4%; distance ~3pp | Low (0.10) |
| Demographic stabilization (births > 10M) | Birth rate | Removes demographic confound; policy effect becomes testable | Current 9.5M; near threshold | Medium (0.25) |
| Policy reversal | Government announcement | Full rebound to pre-policy tutoring levels | No indication currently | Low (0.10) |
| ITS counterfactual crossing | N/A | Spending exceeds what ITS predicts without policy | No scenario median crosses by 2035 | Very low (0.05) |
| Underground > formal market | Underground displacement | Shadow economy dominates; survey data becomes meaningless | Unknown; possibly already near | Low (assessment impossible) |

### Phase Transitions

No sharp phase transitions were identified. The system exhibits smooth, approximately linear dynamics within the projection horizon. This is expected: household spending aggregates are inherently smooth, and the NBS annual resolution cannot capture within-year dynamics.

### Feedback Loops

**Positive feedback (amplifying):**
- Competitive pressure -> more tutoring demand -> higher underground prices -> more spending: This loop would amplify rebound, but cannot be quantified with available data.
- Income growth -> education spending -> labor market returns -> income growth: Very long time constant (20+ years); negligible within the 10-year projection horizon.

**Negative feedback (dampening):**
- Demographic decline -> fewer students -> less aggregate spending pressure: Acts as a natural ceiling on total education burden growth.
- Income saturation -> Engel curve flattening: At higher income levels, education's share of consumption may decline (as observed in high-income countries). This provides a long-run bound.

---

## Constraints on Conclusions

### What the projections CAN claim

1. **Aggregate education spending may decline or grow depending on demographic trajectory.** With full demographic pass-through, Scenario A (policy persists) projects median 2,391 yuan by 2035 (-20% from 2025). Even Scenario C (rebound) reaches only 3,580 yuan (+20%). The previous v1 projections overstated growth because they dampened demographic effects by 70%.

2. **Demographic decline is the dominant driver.** The birth rate trajectory has the largest sensitivity impact (853 yuan range at 2030), exceeding income growth (385 yuan) by more than 2x. This is the single most important exogenous factor.

3. **The policy effect is small relative to macroeconomic forces.** Policy persistence ranks 4th in sensitivity, with less than a quarter of the impact of demographics. Policy-controllable parameters explain a minority of the projection variance.

4. **Scenarios are distinguishable by 2035 but not by 2030.** At 2030, the median spread across scenarios is 649 yuan (21% of the baseline median). By 2035, it grows to 1,189 yuan (38%). However, the within-scenario uncertainty (90% CI width 2,100-3,470 yuan at 2035) dwarfs the between-scenario spread.

### What the projections CANNOT claim

1. **Whether the policy "worked" or not.** The projection inherits the Phase 3 ambiguity: the aggregate signal is not uniquely attributable to the policy (1.7 sigma with systematics; per-birth normalization eliminates it).

2. **What per-child education spending will be.** The NBS proxy cannot decompose education vs. culture/recreation, and aggregate per-capita figures conflate demographic decline with per-child spending changes.

3. **The scale of underground tutoring.** The underground displacement parameter is pure assumption (uniform 0-60%). No systematic data exists to constrain it.

4. **Anything beyond 2029 with meaningful confidence.** EP decays below hard truncation by the mid-term horizon. Projections beyond 2029 are included for completeness but are explicitly speculative (90% CI exceeds 50% of plausible range).

5. **Distributional effects.** These projections are for the national aggregate. They say nothing about urban vs. rural, rich vs. poor, or provincial variation -- all of which may matter more than the aggregate trajectory.

---

## Open Issues

1. **CFPS post-2021 microdata.** When released, this would resolve the fork variable (per-child spending trend) and dramatically narrow projection uncertainty. This is the single most valuable future data acquisition.

2. **CIEFR-HS Wave 3.** Would provide the spending decomposition (in-school vs. tutoring vs. enrichment) needed to validate or refute the displacement hypothesis.

3. **Underground market measurement.** No systematic survey of underground tutoring exists. Without it, the displacement parameter remains unconstrained. This is the largest irreducible uncertainty in the projection model.

4. **NBS proxy decomposition.** Provincial-level data that separates education from culture/recreation would eliminate the proxy confound that ranks 3rd in sensitivity.

5. **Structural break in demographics.** China's birth rate may stabilize (2024 births of 9.54M were slightly above 2023's 9.02M). If stabilization occurs, the demographic confound diminishes and the policy signal (if any) becomes more identifiable in aggregate data.

6. **COVID hangover.** The projection base year (2025) may still reflect post-COVID normalization dynamics. The 2025 observation shows education share at 11.8%, above 2019's 11.7%, suggesting full recovery. But the recovery could overshoot, and one additional year of data would improve the base.

---

## Code Reference

| Script | Purpose | Key Output |
|--------|---------|------------|
| `phase4_projection/scripts/projection_simulation.py` | Monte Carlo simulation (10,000 iter), sensitivity analysis, EP decay, convergence detection | `phase4_projection/data/projection_results.json` |
| `phase4_projection/scripts/inspect_data.py` | Data inspection utility | Console output |

| Figure | File | Description |
|--------|------|-------------|
| Scenario comparison | `figures/scenario_comparison.pdf` | Three scenarios with 50% and 90% CI bands, historical data, ITS counterfactual |
| Sensitivity tornado | `figures/sensitivity_tornado.pdf` | Parameter impact ranking, color-coded by controllability |
| EP decay chart | `figures/ep_decay_chart.pdf` | Left: confidence bands with EP tier boundaries; Right: EP decay curve with truncation thresholds |

---

## Carried-Forward Warnings

All Phase 0/3 warnings remain in force and constrain these projections:

1. **PRIMARY OUTCOME IS A PROXY.** The NBS category bundles non-education spending. Proxy confound ranks 3rd in sensitivity analysis.
2. **NO POST-POLICY MICRODATA.** Cannot validate any projection assumption about per-child spending composition.
3. **UNDERGROUND TUTORING IS UNMEASURABLE.** Displacement parameter is pure assumption.
4. **COVID CONFOUNDING IS SEVERE.** The 2025 base year may still carry COVID recovery dynamics.
5. **DEMOGRAPHIC DECLINE CONFOUNDS AGGREGATE.** Ranks 2nd in sensitivity. Cannot be separated from policy effects in aggregate data.
6. **ALL CHAINS BELOW HARD TRUNCATION.** No chain-level causal projections are supportable. These are edge-level extrapolations only.
7. **SYSTEMATIC UNCERTAINTY DOMINATES.** Now propagated as correlated noise in MC (v2). More time series observations will not materially improve projection precision. The binding constraint is data quality (proxy, underground, microdata), not sample size.
