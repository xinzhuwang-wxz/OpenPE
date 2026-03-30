# Methods Review: Phase 1 Strategy

## Review Summary
- **Phase**: Phase 1 (Strategy)
- **Artifact reviewed**: `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase1_strategy/exec/STRATEGY.md`
- **Date**: 2026-03-29
- **Category A issues**: 1
- **Category B issues**: 6
- **Category C issues**: 4
- **Positive markers**: 8

---

## What Works Well

[+] **Toda-Yamamoto selection for T=24.** The choice of Toda-Yamamoto over standard Granger causality is the correct response to the T<30 conventions violation. The procedure is valid for small samples with unknown integration order, and the strategy correctly cites the original simulations (T=25) and the Hacker & Hatemi-J (2006) bootstrap correction. This is textbook-appropriate.

[+] **ARDL bounds test as secondary method.** Including ARDL alongside Johansen is exactly right for T=24 where unit root test power is low. The ARDL bounds test's agnosticism about I(0)/I(1) classification is a genuine methodological advantage here, not just a robustness check.

[+] **Honest EP adjustments.** Phase 1 EP values are uniformly lower than Phase 0, and every reduction has an explicit justification. The construct validity penalty for the DE index and the method credibility adjustments are well-calibrated. The analysis does not inflate its own confidence.

[+] **Complete DATA_QUALITY.md cross-reference.** All seven warnings from the data quality gate are mapped to systematic uncertainty entries. No silent omissions. This is exactly what the conventions require.

[+] **VAR impulse response for mediation instead of Baron-Kenny.** The strategy correctly identifies that Baron-Kenny mediation is invalid for time series data (i.i.d. violation, serial correlation). The VAR-based decomposition is the appropriate time series equivalent. The citation of Blanchard & Quah (1989) for structural VAR decomposition is apt.

[+] **Proxy DID limitations are prominently stated.** Section 2.5 explicitly lists four limitations of the proxy DID design, including the absence of a control group and confounding concurrent events. This is honest and prevents downstream overinterpretation.

[+] **Segmentation vs. inclusive assessment.** The decision to segment by sector rather than use an aggregate employment index is well-reasoned. The argument that creation and substitution effects operate in opposite directions and would cancel in aggregate is correct and supported by reference to Zhao & Li (2022).

[+] **Fallback strategy.** Section 8.2 provides a concrete plan for what to do if the primary approach fails. This is rare in strategy documents and reflects mature analytical planning.

---

## Suggested Improvements

### Category A (Blocking)

1. **[A1]: Proxy DID regression specification is econometrically invalid for trending time series**
   - Current state: Section 2.5 specifies the proxy DID as `LS_t = alpha + beta_1 * DE_t + beta_2 * POST_t + beta_3 * (DE_t * POST_t) + gamma * DEMO_t + epsilon_t`. This is an OLS regression in levels on two trending, likely I(1) variables (DE and LS) with a binary indicator.
   - Suggested improvement: The proxy DID regression must either (a) use cointegration-aware estimation (i.e., confirm cointegration first, then estimate in VECM framework with the POST interaction), or (b) be specified in first differences: `Delta_LS_t = ... + beta_3 * (Delta_DE_t * POST_t) + ...`. Running OLS in levels on I(1) variables produces spurious regression regardless of the interaction term. The strategy already identifies spurious regression as "existential risk" in Section 5.2 but does not connect this to the proxy DID specification itself.
   - Why it matters: If the proxy DID is estimated as written, the results will be uninterpretable. The t-statistics and confidence intervals will be invalid. This directly undermines the figure that addresses the user's DID request.
   - Effort: Low. Revise the specification to either condition on cointegration results or use first differences.

### Category B (Important)

2. **[B1]: Bootstrap Granger procedure needs explicit specification of the resampling scheme**
   - Current state: The strategy mentions "bootstrap critical values (Hacker & Hatemi-J, 2006)" and "10,000 resamples, seed=42" but does not specify whether this is a residual bootstrap, a wild bootstrap, or a recursive/fixed-regressor bootstrap. For time series with T=24, the choice matters considerably.
   - Suggested improvement: Specify the residual-based bootstrap under the null (as in Hacker & Hatemi-J): fit the restricted VAR, obtain residuals, resample residuals with replacement, reconstruct the series under the null, re-estimate and compute the test statistic. The wild bootstrap (e.g., Webb 6-point distribution) is preferable for heteroskedasticity robustness at very small T. State which variant will be used and why.
   - Why it matters: Different bootstrap schemes have different small-sample properties. At T=24, the choice between residual and wild bootstrap can shift p-values by 0.05-0.10, which is decision-relevant given the planned significance threshold.
   - Effort: Low. Add a paragraph specifying the bootstrap algorithm.

3. **[B2]: Cholesky ordering sensitivity for VAR mediation is understated**
   - Current state: Section 2.3 specifies the ordering DE --> IND_UP --> employment and mentions generalized impulse responses (Pesaran & Shin 1998) as a "robustness check." Section 5.2 rates ordering sensitivity as "MEDIUM."
   - Suggested improvement: With T=24 and 3 variables, the Cholesky decomposition imposes a strong contemporaneous causal structure. The strategy should commit to reporting results for all feasible orderings (there are only 3! = 6 permutations for a trivariate system) and presenting generalized impulse responses as the primary result, not merely a robustness check. The severity should be upgraded to HIGH because mediation share estimates are directly determined by the ordering assumption.
   - Why it matters: The mediation share estimate (benchmarked at ~22% from Li et al. 2024) is the primary output of the mediation analysis. If this estimate flips sign or changes by a factor of 2 across orderings, the mediation result is uninformative. Reporting only one ordering risks presenting an ordering-dependent artifact as a finding.
   - Effort: Low. Commit to all 6 orderings and elevate generalized IRFs.

4. **[B3]: No explicit power analysis is planned despite repeated acknowledgment of low power**
   - Current state: Risk assessment (Section 8.1) estimates a 50% probability of low power preventing detection of moderate effects. Section 12 milestone M2 references p<0.10 bootstrap thresholds. But no formal power calculation is specified in the strategy or Phase 2 deliverables.
   - Suggested improvement: Include a Monte Carlo power analysis in Phase 2 or early Phase 3. Simulate VAR(p+d) processes at T=24 with effect sizes calibrated from reference analyses (e.g., Zhu et al. 2023 DID coefficient ~0.03-0.05) and compute rejection rates under the Toda-Yamamoto test. This tells the analyst what minimum effect size is detectable before running the actual test. If detectable effect sizes are implausibly large, the analyst can report "insufficient power to detect effects of the magnitude found in panel studies" rather than "no effect found."
   - Why it matters: Without power analysis, a null Granger result is uninterpretable -- it could mean no effect or insufficient power. The strategy acknowledges this conceptually but does not operationalize it.
   - Effort: Medium. Requires a simulation script, but the VAR framework is already specified.

5. **[B4]: COVID-19 handling deferred entirely to Phase 2 without a default**
   - Current state: Section 11 (Open Issues, item 3) lists three options for COVID handling and says "Decision deferred to Phase 2 EDA." No default is specified.
   - Suggested improvement: Specify a default approach now and allow Phase 2 to override it. The recommended default: include a COVID impulse dummy (2020=1) in all VAR/VECM specifications, and report sensitivity with sample truncation at 2019 (T=20). Deferring entirely risks Phase 2 making an ad-hoc choice without strategic justification.
   - Why it matters: COVID-19 is a structural break that coincides with digital economy acceleration. If it is not handled explicitly in the strategy, Phase 3 results may be driven by a single outlier year. The choice between dummy, truncation, and inclusion materially affects Granger test results at T=24.
   - Effort: Low. Add one paragraph specifying the default.

6. **[B5]: Joint_EP for the mediation chain uses link-by-link multiplication but the VAR method does not decompose link-by-link**
   - Current state: Section 3.3 computes the mediation chain Joint_EP as 0.23 x 0.30 x 0.30 = 0.021 (below hard truncation). Section 3.3 then resolves this by testing "reduced-form relationships" instead. But Section 4.1 still assigns the mediation analysis to "Lightweight" treatment based on EP=0.23 (the first link only).
   - Suggested improvement: Clarify the EP accounting for VAR-based mediation. The VAR impulse response decomposition estimates the mediation share as a system, not link-by-link. The relevant EP for the mediation analysis is not the product of three links but the EP of the system-level mediation test. This should be explicitly stated as a methodological note: "VAR-based mediation EP is assessed at the system level (EP=0.23 for the DE-->IND_UP link, which is the identification-critical edge) rather than as a chain product." Otherwise the strategy creates an internal contradiction: the chain is "beyond horizon" but the analysis proceeds anyway.
   - Why it matters: EP accounting that contradicts the actual method creates confusion for Phase 3 executors and Phase 5 verifiers.
   - Effort: Low. Add a clarifying paragraph.

7. **[B6]: No discussion of multicollinearity diagnostics for the VAR system**
   - Current state: Section 7.2 lists correlation matrix as a Phase 2 deliverable and Section 5.2 mentions omitted variable bias, but there is no discussion of multicollinearity within the VAR system. With T=24 and variables that are all trending (DE index, services employment, industrial upgrading, urbanization), multicollinearity in the VAR coefficient matrix is likely severe.
   - Suggested improvement: Add VIF or condition number diagnostics to the Phase 2 deliverables. If VIF > 10 for any variable pair in the VAR system, reduce the variable set or use ridge-regularized VAR estimation. Specify a parsimony constraint: no more than 3 endogenous variables in any single VAR system at T=24 with lag=2 (which consumes 3*2 = 6 parameters per equation from 24 observations).
   - Why it matters: At T=24, degrees of freedom are the binding constraint. A trivariate VAR(2) with a constant has 7 parameters per equation and only 22 observations -- this is already marginal. Adding a demographic control makes it 9 parameters from 22 observations, which is underpowered.
   - Effort: Low. Add diagnostics to Section 7.2 and a parsimony rule to Section 2.3.

### Category C (Minor)

8. **[C1]: Reference analysis survey could include a time series precedent**
   - Suggested improvement: All three reference analyses use panel methods (DID, two-way FE, GMM). Consider adding a reference that uses national time series methods for a similar macro-structural question (e.g., Herrendorf, Rogerson & Valentinyi 2014 on structural transformation, or Jorgenson & Vu 2016 on ICT and growth in time series). This would provide a methodological benchmark for the time series approach, not just a subject-matter benchmark.
   - Effort: Low.

9. **[C2]: Bootstrap seed sensitivity check is listed but three seeds is minimal**
   - Suggested improvement: Report the interquartile range of p-values across 50 different seeds rather than point estimates from 3 seeds. With 10,000 resamples per seed, the computational cost is modest.
   - Effort: Low.

10. **[C3]: The mermaid DAG uses color but no pattern/shape differentiation**
    - Suggested improvement: Add shape differentiation (e.g., rectangles for observed variables, diamonds for latent constructs, dashed borders for confounders) in addition to color. This improves accessibility for colorblind readers and is more informative when printed in grayscale.
    - Effort: Low.

11. **[C4]: Notation for EP updates mixes additive and multiplicative adjustments**
    - Suggested improvement: Section 3.1 applies additive truth adjustments (e.g., "truth: 0.30 - 0.05 - 0.10 = 0.15") while EP itself is multiplicative (EP = truth x relevance). This is internally consistent but could be made clearer by presenting a single update formula: `truth_phase1 = max(0.10, truth_phase0 - delta_data - delta_method - delta_construct)`, then `EP_phase1 = truth_phase1 x relevance_phase1`. The formula would prevent errors in Phase 3 updates.
    - Effort: Low.

---

## Method Appropriateness Assessment

### Toda-Yamamoto Procedure Validity

The Toda-Yamamoto procedure is appropriate for T=24 with potentially integrated variables. The procedure's validity rests on three conditions: (1) the true lag order p is correctly identified, (2) the maximum integration order d_max is correctly specified, and (3) the augmented VAR(p+d_max) is estimated in levels. The strategy addresses all three: lag selection via AIC/BIC/HQ with sensitivity reporting (condition 1), d_max sensitivity for d=1 and d=2 (condition 3 in Section 5.2), and levels estimation (implicit in the method description).

One concern: at T=24, if d_max=1 and the AIC-selected lag is p=2, the VAR(3) in levels consumes 3k+1 parameters per equation (where k is the number of endogenous variables). For a bivariate system this is 7 parameters from 21 effective observations -- feasible but tight. For a trivariate system it is 10 from 21 -- problematic. The strategy should enforce bivariate Toda-Yamamoto tests as the primary specification and use trivariate systems only for robustness.

### Proxy DID Design

The proxy DID is the weakest element of the strategy. As noted in A1, the OLS specification in levels is invalid for trending I(1) series. Beyond the specification issue, the fundamental problem is that the "treatment" (smart city pilots) is a national policy environment shift, not a city-specific shock. The pre-period (2000-2012, n=13) and post-period (2016-2023, n=8) are small, and the treatment window (2013-2015) absorbs 3 of 24 observations.

The proxy DID should be reframed as what it actually is: a structural break test with a known candidate break date, interpreted through a policy lens. The DID language risks overstating the identification strength. The figure specification (Section 2.5) is well-designed and addresses the user's request appropriately -- the issue is the econometric specification, not the presentation.

### VAR Mediation Approach

The VAR-based mediation via impulse response decomposition is methodologically sound for time series data. The approach correctly avoids Baron-Kenny and uses structural VAR mechanics. The main risk is the Cholesky ordering dependence, addressed in B2 above.

An alternative worth considering: if cointegration is confirmed between DE, IND_UP, and employment, a VECM-based mediation analysis using the cointegrating vectors themselves can decompose long-run mediation without imposing a Cholesky ordering on contemporaneous relationships. The long-run structure is identified from the cointegrating space, and the short-run adjustment coefficients (alpha matrix) show the speed of mediation. This would be a stronger identification strategy than Cholesky-based IRFs for the mediation question.

### Conventions Compliance

The strategy demonstrates thorough conventions compliance. The deviation from T>=30 for Granger causality is properly documented with specific mitigation (Toda-Yamamoto, bootstrap). The DoWhy pipeline exemption is justified (time series structure incompatible with cross-sectional estimators). The refutation battery is adapted for time series context (placebo timing, permutation, rolling window) rather than using standard DoWhy refutations -- this is appropriate.

One gap: the conventions require "every causal claim survives at least 3 refutation tests." The strategy specifies the refutation types but does not map them to specific edges. Phase 3 should ensure that each edge with EP > soft truncation receives all three refutation types.

---

## Alternative Approaches to Consider

1. **VECM-based mediation instead of (or alongside) Cholesky IRFs.** If Johansen cointegration confirms a cointegrating relationship among DE, IND_UP, and employment, the cointegrating vector itself decomposes the long-run relationship. The loading matrix (alpha) reveals which variables adjust to disequilibrium, providing a mediation interpretation without ordering assumptions. Effort: Medium (requires Johansen results from the cointegration step, which is already planned).

2. **Wavelet coherence analysis as a complementary verification.** For T=24 with trending variables, continuous wavelet transform coherence can reveal time-frequency dependencies between DE and employment variables without requiring stationarity. This would provide a visual complement to the Granger tests showing whether the DE-employment relationship strengthened after 2013-2015. Effort: Medium (requires `pywt` package, straightforward implementation).

3. **Synthetic counterfactual via Bayesian structural time series (CausalImpact).** Google's CausalImpact methodology (Brodersen et al. 2015) constructs a synthetic counterfactual for a single treated time series using contemporaneous control series. If DEMO and GDP are treated as control series (unaffected by smart city pilots), the method can estimate the causal impact of the 2013-2015 policy shift on employment structure. This is a stronger version of the proxy DID that uses a model-based counterfactual rather than linear extrapolation. Effort: Medium (requires `causalimpact` Python package or manual implementation with `pymc`).

4. **Rolling-window Toda-Yamamoto for time-varying causality.** With T=24, a rolling window of size 15-18 would produce 6-9 window estimates, showing whether the DE-->employment Granger relationship emerged or strengthened over time. This directly tests the hypothesis that smart city pilots initiated a causal relationship that did not exist before. Effort: Low (wraps the existing Toda-Yamamoto implementation in a loop).

---

## Figure and Table Assessment

### Proxy DID Figure (Section 2.5)

The four-panel specification is well-designed:
- Panel (a): DE index time series with shading -- standard and clear.
- Panel (b): Employment structure time series with same shading -- good for visual comparison.
- Panel (c): Scatter of DE vs. services employment by period -- effectively communicates slope change.
- Panel (d): Counterfactual extrapolation -- this is the most informative panel and should be the largest.

Suggestions: Panel (d) should include bootstrap confidence bands for the counterfactual extrapolation, not just a point estimate. Without uncertainty bands, the visual gap between counterfactual and observed could appear significant when it is within estimation uncertainty. The strategy should specify that this figure uses `figsize=(10*2, 10*2)` for 2x2 panels per plotting standards.

### Mermaid DAG (Section 6.1)

The DAG is readable and informative. Color coding distinguishes treatment (blue), outcome (red), confounder (orange), mechanism (green/purple), and instrument (gray). See C3 above for accessibility improvement.

### EP Comparison Table (Section 3.4)

Well-organized with Phase 0 vs. Phase 1 columns and explicit change reasons. No precision issues. Would benefit from a "Classification" column (DATA_SUPPORTED / CORRELATION / HYPOTHESIZED) to preview the Phase 3 labeling.

---

## Notation and Consistency

- EP notation is consistent throughout: EP = truth x relevance, Joint_EP = product along chains.
- The use of `-->` for causal edges and `-.->` for confounder paths in the mermaid DAG is consistent.
- Variable naming follows a clear convention: `employment_services_pct`, `services_value_added_pct_gdp`, `population_15_64_pct`.
- Minor inconsistency: the strategy uses both "DE --> LS" and "DE --> employment_services_pct" to refer to similar relationships. The DAG consolidation (Section 6.1) resolves this by operationalizing "LS" into specific employment share variables, but Sections 2.2 and 3.2 still use the abstract "LS" in some rows. Recommend standardizing to the operationalized variable names throughout to avoid ambiguity.
- All mathematical expressions are inline text rather than LaTeX notation. This is acceptable for a strategy document but should transition to proper `$...$` notation in Phase 3 and Phase 6 artifacts.
