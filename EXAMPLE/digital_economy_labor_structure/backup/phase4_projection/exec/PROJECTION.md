# Projection: digital_economy_labor_structure

## Summary

The forward projection of China's digital economy--labor structure relationship is severely constrained by two compounding limitations: (1) the only empirically supported causal edge (DE-->SUB, CORRELATION, EP=0.315) has a positive sign (complement, not substitution), making it directionally opposite to the original hypothesis; and (2) the proxy digital economy index has saturated at its ceiling (1.0) by 2023, eliminating any capacity to project differential DE growth effects. As a result, all three Monte Carlo scenarios (baseline, high-digital, low-digital) converge on a similar 10-year trajectory for industry employment share: a decline from 31.4% to approximately 25--28% driven almost entirely by demographic contraction (working-age population declining at 0.31 pp/year). The endgame classification is **Robust** (CV=0.046 across scenarios), but this robustness reflects model insensitivity to the primary variable of interest (the digital economy) rather than strong causal knowledge. EP decays from 0.315 to below hard truncation (0.05) within 3 years of projection, and the useful projection horizon is constrained to approximately 3 years before EP drops below soft truncation. These projections are conditional extrapolations, not predictions.

---

## Pre-Projection Audit

### Established Relationships

| Causal Edge | Classification | EP (Phase 3) | Effect Size | 95% CI | Input Classification | Validity Conditions |
|-------------|---------------|:---:|-------------|--------|---------------------|---------------------|
| DE --> SUB (industry emp) | CORRELATION | 0.315 | +7.15 pp/unit DE (bivariate ARDL LR) | [-0.89, 15.20] | Empirical | T=24 national time series; ILO modeled estimates; post-structural-break regime; assumes no omitted time-varying confounders beyond demographics |
| DE --> SUB (with DEMO) | CORRELATION | 0.315 | +12.57 pp/unit DE (controlled ARDL LR) | [8.94, 16.21] | Empirical | Same as above plus correct demographic specification; DEMO weakly exogenous |
| DE --> CRE (services emp) | HYPOTHESIZED | 0.030 | ~0 (no Granger signal, no cointegration) | N/A | N/A -- below hard truncation | Beyond analytical horizon |
| DE --> IND_UP (mediation) | HYPOTHESIZED | 0.090 | Significant with controls (W=15.81, p=0.008) but 1/3 refutation PASS | N/A | Empirical (fragile) | Fails refutation; result unstable to data subset and random confounder |
| DEMO --> LS | HYPOTHESIZED | 0.120 | No Granger causality at annual frequency | N/A | Literature-based | Demographic effects likely operate at decadal frequency |

**Key finding carried into projection:** The DE-->SUB edge is the only relationship above soft truncation (EP=0.315). Its sign is **positive** (complement effect: DE growth associated with higher industry employment), contradicting the substitution hypothesis. All other edges fall below soft or hard truncation and contribute only to scenario spread, not to the central projection.

### Quality Constraints Inherited (from DATA_QUALITY.md)

1. **DE composite index is a proxy of uncertain construct validity** (Bias score: LOW, 45/100). It measures ICT infrastructure penetration, not the broader digital economy. The index has reached its normalized ceiling (1.0) by 2023, meaning it cannot capture further digital economy development. This is the most consequential constraint for projection: the primary causal variable has no further variance to project.

2. **T=24 limits statistical power to ~35% for medium effects.** All effect size estimates carry wide confidence intervals. The ARDL LR coefficient ranges from 7.15 (bivariate, marginally significant) to 12.57 (controlled, significant but sensitive to specification).

3. **ILO modeled employment estimates may be partially endogenous** to GDP and urbanization controls. The partial correlation reversal from +0.981 (levels) to -0.400 (residuals) signals severe endogeneity concern.

4. **No cross-sectional variation.** National time series cannot identify heterogeneous effects across regions, industries, or skill groups. The projection is for the national aggregate only.

5. **EP.truth capped at 0.30** for any edge requiring city-level, individual-level, or skill-level data.

### Projection Input Classification Summary

| Parameter | Value | Source | Classification |
|-----------|-------|--------|---------------|
| ARDL LR coefficient (bivariate) | 7.15 (SE=4.10) | Phase 3 estimation | Empirical |
| ARDL LR coefficient (controlled) | 12.57 (SE=1.86) | Phase 3 estimation | Empirical |
| Demographic effect (beta_DEMO) | 1.29 | Phase 3 estimation | Empirical (SE not precisely reported) |
| DE annual growth rate | 0.051 (SD=0.011) | Post-2016 trend | Empirical |
| Demographic decline rate | -0.307/yr | Post-2016 trend | Empirical (UN projections for literature adjustment) |
| Innovation noise std | 0.5 pp | Assumed | Assumed (calibrated to residual scale) |

---

## Scenario Simulations

**Simulation parameters:** 10,000 Monte Carlo iterations per scenario; random seed 20260329; projection horizon 10 years (2024--2033). All parameters sampled from stated distributions. Physical bounds enforced: industry employment share clipped to [5%, 60%], DE index clipped to [0, 1].

**Critical caveat:** The DE index has reached its ceiling of 1.0 (the maximum of its min-max normalized range) by 2023. This means that in the baseline and high-digital scenarios, DE cannot increase further, and the ARDL long-run coefficient (beta_DE) has no additional DE variation to act upon. The projection is therefore driven almost entirely by demographic dynamics, not by the digital economy variable. This is a direct consequence of the proxy index construction (Phase 0, DATA_QUALITY.md) and represents a fundamental limitation of forward projection with this data.

### Scenario 1: Baseline (Current Trends Continue)

**Narrative:** The digital economy index remains at or near its ceiling. Demographics continue their post-2016 decline at -0.31 pp/year. The ARDL long-run relationship (bivariate, conservative) persists.

**Parameter distributions:**

| Parameter | Distribution | Values |
|-----------|-------------|--------|
| beta_DE | Normal | mean=7.15, SD=4.10 |
| beta_DEMO | Normal | mean=1.29, SD=0.50 |
| DE annual growth | Normal | mean=0.051, SD=0.011 (capped at DE=1.0) |
| Demo slope | Linear + noise | slope=-0.307/yr, residual SD=0.220 |
| Innovation | Normal | SD=0.50 pp/year |

**Results:**

| Horizon | Median | 50% CI | 90% CI | 95% CI |
|---------|--------|--------|--------|--------|
| 2024 (1 yr) | 31.0% | [30.6, 31.4] | [30.0, 32.0] | [29.8, 32.2] |
| 2028 (5 yr) | 29.5% | [28.8, 30.1] | [27.8, 31.0] | [27.5, 31.3] |
| 2033 (10 yr) | 27.5% | [26.4, 28.6] | [24.8, 30.1] | [24.2, 30.6] |

**Conditional probability:** Likely (50--60%). This scenario represents the continuation of established trends and is the most probable trajectory absent major policy or structural changes.

### Scenario 2: High-Digital (Accelerated Digital Adoption)

**Narrative:** China accelerates digital infrastructure investment (AI, 5G, industrial internet). The DE growth rate increases by 50%. The stronger controlled ARDL coefficient (12.57) is used as the central estimate, reflecting the hypothesis that deeper digitalization has a stronger complement effect on industry employment. Wider uncertainty reflects model dependence on the controlled specification.

**What distinguishes this from baseline:**
- DE growth rate: 1.5x baseline (0.077/yr vs 0.051/yr) -- but DE is at ceiling, so this only matters if DE were below 1.0
- beta_DE: uses controlled estimate (12.57, SE=2.79) instead of bivariate (7.15, SE=4.10)
- Innovation noise: 0.7 (40% higher, reflecting greater structural change)

**Results:**

| Horizon | Median | 50% CI | 90% CI | 95% CI |
|---------|--------|--------|--------|--------|
| 2024 (1 yr) | 31.0% | [30.5, 31.6] | [29.7, 32.3] | [29.5, 32.5] |
| 2028 (5 yr) | 29.5% | [28.7, 30.2] | [27.6, 31.2] | [27.3, 31.5] |
| 2033 (10 yr) | 27.5% | [26.3, 28.6] | [24.7, 30.3] | [24.1, 30.8] |

**Conditional probability:** Plausible (20--30%).

**Key observation:** The high-digital scenario produces almost identical medians to the baseline. This is because the DE index is at its ceiling -- accelerated digital growth cannot be captured by the proxy. The only difference is slightly wider confidence intervals from higher innovation noise and the controlled beta_DE.

### Scenario 3: Low-Digital (Stagnation/Regulation)

**Narrative:** Digital economy growth slows due to tech regulation (antitrust enforcement, data governance), US-China tech decoupling, or market saturation. The DE-industry complement effect weakens to half the bivariate estimate. Demographics decline faster (-0.2 pp/yr additional). This scenario represents the downside where both digital and demographic headwinds compound.

**What distinguishes this from baseline:**
- beta_DE: 0.5x bivariate (3.575, SE=8.20) -- much weaker and more uncertain complement effect
- DE growth: 0.3x baseline (0.015/yr) -- near stagnation
- Demographic decline: 0.2 pp/yr faster
- Innovation noise: 0.8 (60% higher, reflecting greater structural disruption)

**Results:**

| Horizon | Median | 50% CI | 90% CI | 95% CI |
|---------|--------|--------|--------|--------|
| 2024 (1 yr) | 30.8% | [30.1, 31.4] | [29.2, 32.3] | [28.8, 32.5] |
| 2028 (5 yr) | 28.2% | [26.7, 29.5] | [24.6, 31.5] | [24.0, 32.2] |
| 2033 (10 yr) | 24.9% | [22.2, 27.5] | [18.4, 31.1] | [17.2, 32.4] |

**Conditional probability:** Plausible (15--25%).

**Key observation:** The low-digital scenario diverges from the baseline primarily because of faster demographic decline and the weaker beta_DE (which reduces the compensating complement effect). The 95% CI at 10 years spans 15.2 pp (17.2--32.4%), reflecting genuine uncertainty about the trajectory if the complement effect weakens.

### Scenario Comparison Summary

| | Baseline | High-Digital | Low-Digital |
|---|:---:|:---:|:---:|
| 2033 median | 27.5% | 27.5% | 24.9% |
| 2033 90% CI width | 5.3 pp | 5.6 pp | 12.7 pp |
| Primary driver | Demographics | Demographics | Demographics + weakened complement |
| DE sensitivity | None (saturated) | None (saturated) | Moderate (via beta_DE) |

---

## Sensitivity Analysis

### Critical Finding: DE Index Saturation

The sensitivity analysis reveals a striking result: **the digital economy index has zero marginal sensitivity at the projection horizon.** Varying beta_DE or de_growth by +/-20% produces zero change in the deterministic endpoint because the DE index has already reached its ceiling of 1.0. All further changes in DE are absorbed by the clip at the upper bound. The only parameters with non-zero sensitivity are the demographic variables (beta_DEMO and demo_slope), each producing +/-0.79 pp impact per 20% perturbation.

This is not a bug in the model -- it is a direct consequence of the proxy index construction. The real digital economy continues to evolve beyond 2023, but the min-max normalized proxy cannot capture this variation. Any projection of DE's future effect on labor structure requires either: (1) a non-saturated digital economy measure (such as PKU-DFIIC, which has wider range), or (2) structural model parameters that capture the relationship's evolution independent of the index level.

### Tornado Chart

![Sensitivity of industry employment share to +/-20% parameter perturbation at 10-year horizon. Color indicates controllability classification.](figures/sensitivity_tornado.pdf){#fig:tornado}

### Variable Ranking

| Rank | Variable | Impact (+/-20%) | Classification |
|:---:|----------|:---:|:-:|
| 1 | Demographic effect size (beta_DEMO) | +/-0.79 pp | Exogenous |
| 2 | Demographic decline rate (demo_slope) | +/-0.79 pp | Exogenous |
| 3 | DE effect size (ARDL LR coeff) | 0.00 pp | Semi-controllable |
| 4 | DE annual growth rate | 0.00 pp | Controllable |
| 5 | Model innovation noise | 0.00 pp | Exogenous |

### Key Levers

**1. Demographic decline rate (Exogenous, dominant).** The rate at which China's working-age population (15--64) contracts is the single most influential parameter for the 10-year trajectory. This is not controllable in the short term (it reflects fertility decisions made 15--65 years ago) but could be partially influenced over decades through pronatalist policies, retirement age reform, or immigration policy. At the projection horizon, every 20% acceleration in demographic decline produces an additional 0.79 pp decline in industry employment share.

**2. Demographic effect size (Exogenous).** The coefficient linking demographics to industry employment (beta_DEMO=1.29) is estimated from the ARDL model but with limited precision (SE not precisely reported). If the true demographic sensitivity is higher or lower, the trajectory shifts accordingly. This is a structural parameter of the economy, not directly controllable.

**3. DE effect size (Semi-controllable, zero sensitivity at saturation).** In principle, the strength of the digital economy--industry employment complement effect could be influenced through industrial policy (e.g., Made in China 2025, digital infrastructure investment). However, because the DE proxy index has saturated, this lever has no marginal effect in the projection. If a non-saturated DE measure were available, this parameter would likely rank higher.

### Interaction Check

The top two parameters (beta_DEMO and demo_slope) have an interaction effect of -0.16 pp, which is 10.0% of the additive expectation. This is borderline at the 10% threshold, suggesting approximate additivity. The interaction is negative (compounding): faster demographic decline combined with higher demographic sensitivity produces slightly more than additive decline in industry employment.

---

## Endgame Classification

**Category: Robust** (with critical caveats)

**Quantitative evidence:**

- Coefficient of variation across scenario endpoint medians: CV = 0.046 (well below the 0.15 threshold for Robust classification)
- Scenario endpoint medians: Baseline 27.5%, High-Digital 27.5%, Low-Digital 24.9%
- Variance growth rate across scenarios: 0.16 per year (linear, not accelerating)
- Substantial 90% CI overlap between baseline and high-digital scenarios (24.8--30.1 vs 24.7--30.3)

**Justification:** The three scenarios converge on a similar trajectory: industry employment declining from 31.4% toward 25--28% over 10 years, driven by demographic contraction. The CV of 0.046 is well below the Robust threshold of 0.15. Even the low-digital scenario, which produces a lower median (24.9%), has a 90% CI that substantially overlaps with the baseline.

**Critical caveat -- Robustness reflects model limitation, not causal certainty:**

The convergence of scenarios is NOT evidence that the digital economy's role in labor structure is well-understood. It reflects the fact that the DE proxy index has saturated, making the model insensitive to its primary variable of interest. If the DE index had a wider range (as the PKU-DFIIC would provide), scenarios might diverge significantly. The Robust classification applies to the model's projection given its inputs; it does not apply to the underlying causal question.

**If DE index were not saturated:** The scenarios would likely be reclassified as **Fork-dependent**, with the fork condition being whether digital economy growth accelerates (favoring the complement effect and buffering industry employment) or stagnates (allowing pure demographic decline to dominate). The fork variable would be the DE growth trajectory, and the decision point would be industrial digitalization policy (Made in China 2025 continuation, AI adoption incentives, platform economy regulation).

---

## EP Decay

### Confidence Band Chart

![EP-weighted confidence decay for the DE-->SUB (industry employment) projection. Top panel: baseline projection with widening confidence bands. Bottom panel: EP value decay from Phase 3 anchor (0.315) toward hard truncation. CORRELATION edges decay at 2x the standard rate per protocol.](figures/ep_decay_chart.pdf){#fig:ep_decay}

### EP Decay Schedule

| Projection Distance | EP Multiplier (raw) | EP Multiplier (CORRELATION 2x) | EP Value | Confidence Tier |
|:---:|:---:|:---:|:---:|:---:|
| 0 (Phase 3 finding) | 1.00 | 1.00 | 0.315 | HIGH (empirical) |
| 1 year | 0.60 | 0.36 | 0.113 | MEDIUM (below soft truncation) |
| 3 years | 0.40 | 0.16 | 0.050 | LOW-MEDIUM (at hard truncation) |
| 5 years | 0.25 | 0.063 | 0.020 | LOW (beyond hard truncation) |
| 7 years | 0.15 | 0.023 | 0.007 | Negligible |
| 10 years | 0.08 | 0.006 | 0.002 | Negligible |

**Decay rate justification:** The standard EP decay schedule is applied with the CORRELATION-edge 2x multiplier specified in the Phase 4 protocol. The base decay rate is further adjusted for the fast-moving technology domain: digital economy dynamics are subject to rapid structural change (platform regulation shifts, AI disruption, trade policy), making parameter stability assumptions weaker than in slow-moving domains. The resulting decay is aggressive but honest: EP drops below soft truncation (0.15) within 1 year and below hard truncation (0.05) within 3 years.

### Useful Projection Horizon

**Formal criterion (90% CI > 50% of plausible range):** The 90% CI for the baseline scenario at 10 years spans 5.3 pp, which is 9.7% of the plausible range (5--60%). By this criterion, the useful horizon extends to the full 10-year projection period. However, this criterion is misleading because the projection is driven by demographics (a smooth secular trend), not by the causal variable of interest.

**EP-based criterion (recommended):** EP drops below soft truncation (0.15) at approximately 1 year. EP drops below hard truncation (0.05) at approximately 3 years. Beyond 3 years, the projection has negligible epistemic support from the Phase 3 causal findings.

**Recommended useful horizon: 3 years (to 2026)**, based on the EP decay criterion. Beyond 3 years, the projection is an extrapolation of demographic trends with no empirically grounded causal content from the digital economy analysis. The 4--10 year projections are included for completeness but must be treated as speculative.

### Scenario Comparison

![Scenario comparison: historical industry employment share (2000--2023) and three projected trajectories (2024--2033) with 50% and 90% confidence bands. All scenarios converge due to DE index saturation.](figures/scenario_comparison.pdf){#fig:scenario_comparison}

---

## Tipping Points and Phase Transitions

| Threshold | Behavioral Change | Proximity EP | Notes |
|-----------|-------------------|:---:|-------|
| DE index = 1.0 (saturation) | Proxy loses discriminating power; further digital economy development cannot be captured | Already reached (2023) | This is the most consequential tipping point for the analysis. The min-max normalized index has saturated, eliminating the primary causal variable's projection capacity. |
| Beta_DE = 0 (complement-to-neutral transition) | The positive DE-industry relationship extinguishes. If the DID post-break weakening ($\beta_2$=-5.90/period) continues, this occurs ~1.2 periods from the 2016 break date (i.e., approximately 2017--2018). | LOW (the weakening may have already occurred) | The DID interaction term suggests the complement effect is already weakening. Whether it has reached zero or reversed cannot be determined from the current data. |
| Working-age population < 60% | Accelerated demographic pressure on labor supply; potential labor shortages in manufacturing | ~30 years at current decline rate | Not an imminent concern but relevant for long-run industrial employment projections. |
| Structural break (new policy regime) | Analogous to 2013--2015 smart city/supply-side reform period. Would invalidate the current linear extrapolation. | Unquantifiable | Any major policy shift (common prosperity, AI regulation, demographic stimulus) could create a new structural break. The projection assumes no such break occurs. |

**Feedback loops identified:**

1. **Demographic-digital positive feedback:** Working-age population decline increases labor costs, incentivizing automation/digitalization, which in turn changes employment structure. This feedback is not modeled (would require a simultaneous equations framework) but could amplify the projected decline.

2. **DE saturation ceiling effect:** As the DE index saturates, the complement effect maxes out, potentially exposing the underlying substitution dynamics that were masked by the complement effect during the rapid digitalization period (2000--2020).

---

## Constraints on Conclusions

### What the projections CAN claim

1. **Industry employment share is on a declining trajectory,** driven primarily by demographic contraction. All three scenarios agree on this direction.

2. **The decline is approximately 0.4 pp/year** (median), with 90% CI of approximately 0.5--1.0 pp/year depending on the scenario.

3. **The scenarios converge** because the primary causal variable (DE) has saturated, not because the causal relationship is well-established.

### What the projections CANNOT claim

1. **No causal projection of the digital economy's future effect is possible** with this proxy index. The DE variable has saturated, eliminating forward-looking causal content.

2. **No claim about substitution vs. creation** can be projected forward. The historical data shows a complement effect (positive DE-industry association), but this may have already weakened or reversed (DID interaction evidence).

3. **No projection of services employment** is warranted. The creation channel (DE-->CRE) has EP=0.030, below hard truncation. Services employment growth is beyond the analytical horizon of this analysis.

4. **No projection beyond 3 years** has meaningful EP support. The 4--10 year projections are demographic extrapolations dressed in causal language.

5. **No claim about the real digital economy** (as opposed to the proxy) can be sustained. The proxy measures ICT infrastructure penetration, not digital economic activity.

---

## Open Issues

1. **DE index saturation is the binding constraint.** The projection's most important finding is negative: the proxy digital economy index has reached its ceiling, making forward projection of DE effects impossible. A non-saturated measure (PKU-DFIIC, or a broader composite including e-commerce volume, platform economy scale, AI adoption metrics) would fundamentally change the projection's capacity.

2. **Complement effect may have already reversed.** The DID interaction term ($\beta_2$=-5.90, with the effect potentially reaching zero by 2017--2018) suggests the positive DE-industry relationship may be weakening or has already reversed. The projection uses the full-period estimate, which may overstate the current relationship strength.

3. **Demographics dominate but are imprecisely modeled.** The projection uses a simple linear extrapolation of the 2016--2023 demographic trend. UN Population Division medium-variant projections or a cohort-component model would improve the demographic trajectory.

4. **No cross-sectional disaggregation.** The projection is for national aggregates only. Regional heterogeneity (eastern vs. western China), industry heterogeneity (manufacturing subsectors), and skill-level heterogeneity are all unaddressed.

5. **ILO endogeneity propagates into projections.** The ARDL coefficient was estimated from ILO modeled employment data, which may be partially endogenous to GDP and urbanization. This endogeneity is inherited by the projection but not quantified.

6. **Structural break assumption.** The projection assumes no new structural break occurs in 2024--2033. This is a strong assumption given China's policy environment (common prosperity, AI governance, US-China tech competition).

---

## Code Reference

| Script | Purpose |
|--------|---------|
| `phase4_projection/scripts/projection_simulation.py` | Monte Carlo simulation (10,000 iterations x 3 scenarios), sensitivity analysis, endgame detection, EP decay computation, all figure generation |

**Figures:**

| Figure | Path |
|--------|------|
| Scenario comparison | `phase4_projection/figures/scenario_comparison.pdf` |
| Sensitivity tornado | `phase4_projection/figures/sensitivity_tornado.pdf` |
| EP decay chart | `phase4_projection/figures/ep_decay_chart.pdf` |

**Reproducibility:** Random seed = 20260329. All parameter distributions documented above. Simulation uses numpy default_rng for reproducibility.
