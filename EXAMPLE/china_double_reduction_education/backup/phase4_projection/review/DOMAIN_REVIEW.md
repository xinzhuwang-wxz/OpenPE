# Domain Review

## Summary
- **Artifact reviewed**: `phase4_projection/exec/PROJECTION.md`
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 2
- **Category B issues**: 4
- **Category C issues**: 3

## First Principles Assessment

The projection correctly inherits Phase 3's CORRELATION classification and all-chains-below-hard-truncation finding. The pre-projection audit table is accurate and comprehensive. The identification of income growth, demographic decline, and underground displacement as the key projection drivers is well-grounded in the education economics literature on China. The assumption boundaries table (income elasticity ~1.0, demographic decline -6%/yr) is consistent with available evidence.

The framing of the question as "conditional extrapolation, not forecast" is appropriate given the empirical weakness (1.7 sigma with systematics). This is a strength of the artifact.

## Data Source Validity Assessment

The projection anchors on the 2025 NBS observed value (2,986 yuan in real 2015 terms), which is the correct anchor given the available data. The projection correctly inherits the Phase 0/3 proxy warning: the NBS "education, culture and recreation" category bundles non-education spending.

The parameter distributions draw on Phase 3 empirical estimates (level shift, bootstrap SE) and literature-based priors (income elasticity, demographic decline rates). These are appropriate sources. The underground displacement parameter (uniform 0-60%) is acknowledged as pure assumption, which is honest.

## Methodology Assessment

The Monte Carlo simulation (10,000 iterations, 6 stochastic parameters) is a reasonable approach for this domain. The projection model structure is a multiplicative income/demographic model with additive policy and proxy-confound terms. This is a standard reduced-form approach for household expenditure projection.

However, there are methodological concerns detailed in the issues below regarding the sensitivity analysis baseline parameters and the interaction between model structure and the sensitivity rankings.

## Systematic Uncertainty Assessment

The projection correctly identifies that systematic uncertainty dominates (80% from Phase 3) and that more time series observations will not improve precision. The EP decay schedule applies the 2x CORRELATION penalty correctly (standard multipliers squared). The noise term scales as sqrt(t), which is a standard random-walk assumption -- appropriate for this domain given annual data.

The culture/recreation recovery parameter is a good addition that acknowledges the proxy confound, and it correctly ranks 3rd in sensitivity. COVID handling uncertainty from Phase 3 is partially absorbed into the 2025 base year, which the artifact acknowledges.

## Verification Assessment

The interaction check (pairwise among top 3 parameters) finds no nonlinear interactions exceeding 10%, which is consistent with the approximately linear model structure. The useful projection horizon calculation (2032, based on 90% CI exceeding 50% of plausible range) is a reasonable heuristic.

No independent validation against external forecasts (e.g., IMF/World Bank projections of Chinese household consumption, or Chinese Academy of Social Sciences education spending projections) is provided. This would strengthen the result.

## EP and Causal Claim Assessment

The EP decay schedule is correctly constructed. The CORRELATION 2x decay penalty is applied as documented: standard multipliers of [1.0, 0.7, 0.4, 0.2] become [1.0, 0.49, 0.16, 0.04]. Starting from EP=0.20, this yields [0.20, 0.098, 0.032, 0.008]. The near-term EP of 0.098 falling below soft truncation (0.15) by year 1 is a correct and important finding.

The decision to present projections as "scenario-conditional extrapolations" rather than causal predictions is appropriate and well-justified. The constraints-on-conclusions section is unusually honest and well-written.

The EP decay chart (right panel) correctly shows the decay curve with truncation thresholds marked. The left panel shows widening confidence bands consistent with the decay schedule.

## Result Plausibility

The 2030 median projections (2,886 / 3,421 / 3,822 yuan for scenarios A/B/C) are plausible given a 2025 base of 2,986 yuan. Scenario A implies slight decline then recovery (CAGR +0.6%), Scenario B implies moderate growth (CAGR +3.0%), and Scenario C implies strong growth (CAGR +4.7%). These CAGRs bracket the historical pre-policy growth rate and post-COVID recovery dynamics.

The conditional probability assignments (A: 15-25%, B: 45-55%, C: 25-35%) are directionally reasonable. Scenario B is correctly weighted as most probable given the Phase 3 ambiguity.

The sensitivity rankings are plausible: income growth as the dominant driver is consistent with the near-perfect pre-policy income-spending correlation (r=0.97) from Phase 3. Policy persistence ranking 4th is consistent with the 1.7-sigma empirical weakness.

## Issues by Category

### Category A (Blocking)

1. **[A1]: Sensitivity analysis uses inconsistent baseline for underground displacement.**
   - In the sensitivity analysis code (line 316), the baseline for `underground_disp` is set to 0.30, but in Scenario B (the baseline scenario), underground displacement is drawn from N(0.2, 0.50) with mean 0.2. The sensitivity tornado chart therefore measures perturbations around 0.30 rather than the scenario-consistent value of 0.20. This affects the reported impact magnitude for underground displacement (64 yuan) and potentially its ranking.
   - Domain impact: The sensitivity ranking is the primary actionable output of Phase 4. An inconsistent baseline undermines the validity of the ranking and the quantitative impact numbers reported in the text.
   - Required action: Align the sensitivity baseline `underground_disp` to 0.20 (Scenario B mean) and regenerate the tornado chart and reported impact values. If the ranking changes, update the PROJECTION.md discussion accordingly.

2. **[A2]: Policy effect double-counted -- level shift already embedded in 2025 base.**
   - The projection model starts from `OBS_2025` (the observed 2025 value, which already reflects whatever policy effect exists) and then adds `net_policy * (1 + 0.02*t)` on top of it (code line 214). The observed 2025 value already contains the -483 yuan level shift (or whatever fraction of it is real). Adding the policy effect again means the model double-counts the policy contribution in all scenarios where `policy_persistence > 0`.
   - In Scenario A (policy persistence = 0.8), the model adds approximately -483 * 0.8 * (1-0) = -386 yuan on top of a base that already incorporates the shift. This produces the low 2026 median of 2,676 yuan (a 10% drop from 2025 in a single year), which is implausibly steep for a policy that has been in effect since 2021.
   - Domain impact: The Scenario A trajectory is biased downward. The spread between scenarios is artificially inflated. The endgame classification (Fork-dependent) may be affected.
   - Required action: Reformulate the model so that the policy parameter represents the *change* from the embedded-in-base policy effect, not a re-application of the full level shift. One approach: model policy persistence as the fraction of the current embedded effect that will persist forward (persistence=1.0 means no change from current trajectory, persistence=0.0 means full rebound to counterfactual). This changes the parameter interpretation but eliminates the double-counting.

### Category B (Important)

1. **[B1]: Scenario B underground displacement distribution is poorly specified.**
   - Scenario B uses N(0.2, 0.50) clipped to [0,1] for underground displacement. With a standard deviation of 0.50 and mean 0.2, this distribution is heavily clipped: approximately 34% of draws are negative (clipped to 0) and ~6% exceed 1 (clipped to 1). The effective distribution is not Gaussian -- it is a mixture of a point mass at 0, a truncated Gaussian, and a point mass at 1. The mean of the clipped distribution is approximately 0.30-0.35, not 0.2 as reported.
   - Domain impact: The reported parameter distribution does not match the effective distribution used in the simulation. The scenario results for B may be shifted relative to what the reported parameters imply.
   - Suggested action: Either (a) use a Beta distribution (e.g., Beta(1.5, 6) for mean ~0.2 with support on [0,1]), or (b) use a narrower Gaussian (e.g., N(0.2, 0.15)) that avoids heavy clipping, or (c) explicitly report the effective (post-clipping) distribution statistics alongside the nominal parameters.

2. **[B2]: Demographic decline modeled with arbitrary 30% pass-through dampening.**
   - The model uses `(1 + demo_decline * 0.3)^t` for the demographic effect (code line 207). The 0.3 dampening factor is not justified empirically or from literature. The rationale is that fewer births reduce aggregate per-capita education spending, but per-child spending may rise, so the aggregate effect is dampened. However, the magnitude of this dampening (30%) is an assumption that ranks 2nd in sensitivity yet has no empirical basis.
   - Domain impact: The demographic decline impact (304 yuan at 2030) could range from ~100 yuan (at 10% pass-through) to ~900 yuan (at 90% pass-through), changing whether demographics or income growth is the dominant driver.
   - Suggested action: Either (a) present the pass-through rate as an additional sensitivity parameter (varying 10-90%), or (b) derive the pass-through empirically from the relationship between birth counts and per-capita education spending in the historical data, or (c) at minimum, acknowledge this as an additional source of structural uncertainty in PROJECTION.md.

3. **[B3]: No external validation of projection magnitudes.**
   - The projection medians (3,168-4,752 yuan at 2035 in 2015 real terms) are not compared against any external forecasts or benchmark. Chinese household consumption growth projections from the IMF, World Bank, or Chinese Academy of Social Sciences would provide a sanity check on whether the income growth and elasticity assumptions produce reasonable total consumption trajectories.
   - Domain impact: Without external validation, there is no way to assess whether the model's income-driven growth trajectory is calibrated to the broader macroeconomic outlook.
   - Suggested action: Include a brief comparison of the projected spending trajectory against at least one external projection of Chinese household consumption or education spending (even if only qualitative).

4. **[B4]: The 0.02*t policy deepening term is unjustified.**
   - The projection formula includes `net_policy * (1 + 0.02*t)` (code line 214), implying the policy effect deepens by 2% per year. No empirical or theoretical justification is provided for this rate. Over 10 years, this compounds to a 22% increase in the policy effect. For the "Policy Succeeds" scenario, this produces an increasingly strong policy effect that lacks empirical support.
   - Domain impact: Inflates the divergence between Scenario A and Scenario C over time, potentially affecting the endgame classification.
   - Suggested action: Either justify the 2%/year deepening from evidence (e.g., enforcement tightening patterns in Chinese regulation), or remove it and let `policy_persistence` alone determine the trajectory. If deepening is modeled, it should be a stochastic parameter with uncertainty.

### Category C (Minor)

1. **[C1]: Scenario comparison figure has a title-like annotation that is redundant.**
   - The "Policy (Jul 2021)" annotation is useful but partially obscures data points. Consider moving it outside the data region.
   - Suggested action: Reposition the annotation to avoid overlap with data.

2. **[C2]: EP decay chart left panel lacks the ITS counterfactual line.**
   - The scenario comparison figure includes the ITS counterfactual, but the EP decay chart (left panel) does not. Including it would help readers assess whether the confidence bands are consistent with the counterfactual trajectory.
   - Suggested action: Add the ITS counterfactual line to the EP decay chart left panel.

3. **[C3]: Conditional probability ranges sum to 85-115%, not 100%.**
   - Scenarios A (15-25%), B (45-55%), C (25-35%) sum to 85-115%. While ranges naturally overlap, the midpoints sum to 100%, which is fine. The text should note that these are approximate and not intended to be exhaustive.
   - Suggested action: Add a footnote that probabilities are approximate and that additional unlisted scenarios (e.g., policy reversal with economic crisis) are possible.

## Acceptance Readiness

I would not accept this analysis in its current form due to two Category A issues. The double-counting of the policy effect (A2) is a model specification error that biases the Scenario A trajectory downward and inflates scenario divergence. The sensitivity baseline inconsistency (A1) is a smaller issue but directly affects the reported sensitivity rankings, which are a key output.

The Category B issues are important but would not individually block acceptance. B2 (demographic pass-through) and B4 (policy deepening term) introduce unjustified constants that could shift results materially, but the wide uncertainty bands partially compensate for these assumptions.

The overall quality of the analysis is high. The pre-projection audit, EP decay treatment, CORRELATION carry-forward, constraints-on-conclusions section, and honest assessment of the projection horizon are all well-executed. After fixing A1 and A2, this projection would be ready for acceptance with B-category improvements applied.
