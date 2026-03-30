# Methods Review: Phase 3 Analysis

## Review Summary
- **Phase**: Phase 3 (Causal Analysis)
- **Artifact reviewed**: `phase3_analysis/exec/ANALYSIS.md` and all scripts in `phase3_analysis/scripts/`
- **Date**: 2026-03-29
- **Category A issues**: 2
- **Category B issues**: 6
- **Category C issues**: 5
- **Positive markers**: 8

## What Works Well

[+] **Toda-Yamamoto implementation is structurally correct.** The VAR(p+d_max) procedure in `step1_granger_causality.py` correctly fits the augmented VAR in levels and restricts the Wald test to the first p lags only, which is faithful to the original Toda & Yamamoto (1995) specification. The bootstrap p-value procedure follows the Hacker & Hatemi-J (2006) residual resampling approach. This is the right primary method for T=24 with I(1) variables.

[+] **Honest treatment of sign reversal.** The analysis does not suppress the finding that the DE-industry relationship is positive (complementary) rather than negative (substitution). This contradicts the original hypothesis, and the document clearly states the contradiction and classifies accordingly. This intellectual honesty strengthens the analysis.

[+] **Dual cointegration confirmation.** Using both Johansen trace/max-eigenvalue and ARDL bounds test to confirm cointegration is methodologically sound and addresses the concern that Johansen has low power at T=24. The ARDL bounds test is valid regardless of the I(0)/I(1) mix, making it a genuine robustness check.

[+] **Comprehensive refutation battery coverage.** Seven edge-specification combinations are tested with all three refutation tests. The refutation summary heatmap (Figure: `refutation_summary.pdf`) provides an effective visual overview of PASS/FAIL patterns.

[+] **EP propagation is mechanical and traceable.** Each classification maps to a fixed truth update rule, and the EP propagation table shows Phase 0 through Phase 3 values with explicit change reasons. No subjective overrides are visible.

[+] **Power analysis context for null results.** The document consistently notes that at T=24, power is approximately 35% for medium effects, preventing over-interpretation of null findings. The creation channel null is appropriately described as "inconclusive" rather than "evidence of absence."

[+] **Structural break sensitivity analysis across break years.** Testing the POST interaction coefficient at 2013, 2014, 2015, 2016, and 2017 (Section 6.6) strengthens the structural break analysis by showing the result is not an artifact of a single break date choice.

[+] **Signal injection tests pass cleanly.** The three-level injection protocol (observed magnitude, 2x observed, null) all recover correctly, confirming the statistical model is well-specified for the DID-inspired regression framework.

---

## Suggested Improvements

### Category A (Blocking)

1. **[A1]: Bootstrap procedure in Toda-Yamamoto uses i.i.d. resampling of residuals instead of block bootstrap**
   - Current state: In `step1_granger_causality.py` (lines 182-200), the bootstrap loop draws residual indices as `np.random.randint(0, len(resid_centered), size=len(resid_centered))`, which is i.i.d. resampling. The same issue appears in the VAR IRF bootstrap in `step4_var_mediation.py` (lines 88-108) and `step8_uncertainty_quantification.py` (lines 127-170).
   - Suggested improvement: Use a block bootstrap (e.g., circular block bootstrap with block size 2-3) for the Granger causality bootstrap. Time series residuals from a VAR may retain serial correlation even after fitting, particularly with T=24 where lag selection is imprecise. The DID-inspired regression bootstrap in `step8_uncertainty_quantification.py` correctly uses block bootstrap (block_size=3), but the Granger and IRF bootstraps do not.
   - Why it matters: i.i.d. resampling of serially correlated residuals underestimates the variance of the bootstrap distribution, producing artificially narrow confidence intervals and overly optimistic p-values. The bootstrap p-values reported in ANALYSIS.md (e.g., p_boot=0.087, p_boot=0.012) may be biased downward. Given that several results are at marginal significance levels, this bias could change classifications.
   - Effort: Medium. Replace `np.random.randint` resampling with a block bootstrap in three scripts. The block bootstrap is already implemented in `step8_uncertainty_quantification.py` and can be adapted.

2. **[A2]: Refutation tests for the controlled (with DEMO) specification run refutations on the bivariate specification only**
   - Current state: ANALYSIS.md Section 3.1.3 reports refutation results for DE-->SUB both bivariate and with demographic control. However, `step5_refutation_tests.py` lines 37-47 show that `ty_granger` uses a fixed `p_opt=1` and `d_max=1` for all refutation runs, while the primary test in `step1_granger_causality.py` selects the optimal lag via AIC. More critically, Section 3.3 (DE-->IND_UP) states: "refutation tests were run on the bivariate specification per protocol. The controlled specification was not separately refuted because it requires trivariate refutation testing which would reduce effective sample size further."
   - Suggested improvement: The classification for DE-->SUB with demographic control is CORRELATION based on controlled refutation results (2/3 PASS). But the edge EP=0.315 is driven by the controlled specification (p_boot=0.012). The refutation battery must match the specification being classified. If the controlled result is used for classification and EP, the controlled specification must be refuted. For DE-->IND_UP, the strongest signal (p=0.008) is the controlled specification, yet refutation was only run on the bivariate (p=0.132) specification. The classification of HYPOTHESIZED is thus based on refuting a weaker signal rather than the one being used for inference.
   - Why it matters: This is a methodological inconsistency that could lead to either over- or under-classification. The conventions require that "every causal claim must survive at least 3 refutation tests." If the claim is based on the controlled specification, the refutation must test that specification.
   - Effort: Medium. Run the refutation battery with `control_cols=["population_15_64_pct"]` for edges where the controlled specification is the basis for the reported result.

### Category B (Important)

1. **[B1]: Restricted model in Toda-Yamamoto Wald test zeros columns instead of dropping them**
   - Current state: In `step1_granger_causality.py` (lines 159-165), the restricted model is constructed by setting columns of the design matrix to zero: `X_r[:, col_idx] = 0.0`. Then OLS is fitted on this modified matrix. This does not produce the correct restricted OLS estimate, because the zeroed columns still consume degrees of freedom and the lstsq solution interprets zero columns differently than omitted columns.
   - Suggested improvement: Construct X_r by deleting the restricted columns entirely, then fit OLS on the reduced design matrix. The correct restricted residual sum of squares comes from regressing y on X with those columns removed.
   - Why it matters: The current implementation may produce incorrect SSR_r values, which would bias the F-statistic and Wald W. The magnitude of the bias depends on the correlation structure of the regressors. With T=24, even small biases in W can shift marginal results across significance thresholds.
   - Effort: Low. Replace column zeroing with column deletion using `np.delete(X, cause_rows, axis=1)`.

2. **[B2]: ARDL bounds test critical values are from Pesaran (2001) asymptotic tables, which are unreliable at T=24**
   - Current state: `step2_cointegration_vecm.py` (lines 205-212) hardcodes Pesaran et al. (2001) Table CI(iii) critical values. These are asymptotic bounds derived for large samples.
   - Suggested improvement: Use the Narayan (2005) small-sample critical values for the ARDL bounds test, which are specifically tabulated for T=30-80. Alternatively, bootstrap the F-statistic distribution under the null to obtain sample-specific critical values. At minimum, note in ANALYSIS.md that the Pesaran bounds may be liberal at T=24.
   - Why it matters: The Pesaran asymptotic bounds tend to over-reject at small sample sizes. The ARDL F=6.51 for substitution and F=8.59 for mediation may clear the asymptotic bound but not a small-sample-corrected bound. Since ARDL is used as the secondary confirmation of cointegration, its credibility matters for the overall assessment.
   - Effort: Medium. Narayan tables can be hardcoded for the relevant k and T. Bootstrap is more work but more precise.

3. **[B3]: VAR mediation decomposition uses an invalid comparison between trivariate and bivariate VARs to compute mediation share**
   - Current state: `step4_var_mediation.py` (lines 153-179) computes the "indirect effect" as the difference between the cumulative IRF of employment to a DE shock in the trivariate VAR (DE, services VA, employment) and the bivariate VAR (DE, employment). The result is negative (-90% to -95% mediation share).
   - Suggested improvement: The comparison of impulse responses across VARs of different dimensionality is not a valid mediation decomposition. The Cholesky decomposition normalizes the shock to one standard deviation of the orthogonalized residual, and this normalization changes when variables are added or removed. The correct approach is either: (a) use the structural VAR approach where the mediation channel is shut off by setting specific structural coefficients to zero within the same model, or (b) use variance decomposition (FEVD) as the mediation metric -- this is already computed and shows DE explains ~15% of employment forecast error variance. The FEVD is the appropriate mediation quantity for this model structure.
   - Why it matters: The negative mediation share is correctly flagged as anomalous in the document, but it is reported as a result rather than diagnosed as a methodological artifact. The comparison across different-dimensionality VARs conflates the change in shock scaling with the change in transmission mechanism. This undermines the mediation analysis entirely.
   - Effort: Medium. Either implement the structural VAR channel-shutdown approach (set specific coefficients to zero and re-compute IRF within the trivariate system) or reframe the mediation analysis around FEVD, which is already computed.

4. **[B4]: Data subset refutation drops random rows, destroying temporal structure**
   - Current state: `step5_refutation_tests.py` (lines 200-207) drops random indices from the DataFrame, then resets the index. For a time series, dropping random years creates gaps that violate the temporal ordering assumption of the Toda-Yamamoto test. A VAR fitted on data with years {2000, 2002, 2003, 2005, ...} treats these as consecutive observations, which biases the lag coefficients.
   - Suggested improvement: Use contiguous subsample tests instead: (a) rolling window stability (e.g., drop first 3 years, last 3 years, middle years), (b) leave-one-out jackknife on influence diagnostics, or (c) if random dropping is retained, interpolate gaps to preserve temporal spacing. The rolling window approach is more informative for time series because it reveals whether the result depends on a specific regime (e.g., pre-2005 takeoff vs. post-2015 maturity).
   - Why it matters: Every single edge fails the data subset test. While the document attributes this to T=24 instability, part of the universal failure may be an artifact of the test design (destroying temporal structure) rather than genuine instability. This makes the subset refutation uninformative, reducing the effective refutation battery from 3 tests to 2.
   - Effort: Medium. Implement rolling window and leave-k-out designs. This would also produce a more informative stability diagnostic.

5. **[B5]: Bootstrap replications are inconsistent across procedures**
   - Current state: The Granger bootstrap uses 10,000 replications (`step1_granger_causality.py`), the IRF bootstrap uses 1,000 (`step4_var_mediation.py`), the bivariate IRF CI uses 500 (same script, line 208), and the DID bootstrap uses 2,000 (`step8_uncertainty_quantification.py`). The Granger W bootstrap in the uncertainty script uses 1,000 (`step8_uncertainty_quantification.py`, line 127).
   - Suggested improvement: Standardize at 5,000 replications for all bootstrap procedures, or at minimum justify the variation. 500 replications for the IRF confidence intervals is low -- percentile-based 90% CIs from 500 draws have substantial Monte Carlo error (the 5th percentile is estimated from only 25 draws).
   - Why it matters: The IRF confidence bands in `var_irf_mediation.pdf` are visually very wide, and part of this width may be Monte Carlo noise rather than true sampling variability. Increasing to 2,000-5,000 would tighten the estimate of the confidence bands and produce more reliable inference.
   - Effort: Low. Change the `n_boot` parameter in each script. Computational cost at T=24 is negligible.

6. **[B6]: Uncertainty tornado chart includes ill-defined systematics that dominate the visual**
   - Current state: The tornado chart (`uncertainty_tornado.pdf`) shows "Functional form" at ~95 pp, which is larger than all other sources combined. The text (Section 7.2) correctly notes this is "not a well-defined perturbation" and excludes it from the quadrature combination. However, the figure shows it as a bar of equal visual weight.
   - Suggested improvement: Either (a) split the tornado into two panels -- "well-defined perturbations" and "model-structure changes" -- or (b) visually distinguish the ill-defined bars (hatched fill, gray color, separate grouping) with a clear annotation explaining why they are excluded from the total. The current figure, taken in isolation, suggests the total uncertainty is ~99 pp, which contradicts the text.
   - Why it matters: Figures must stand alone. A reviewer looking at the tornado chart without reading the surrounding text would conclude the results are meaningless (total uncertainty ~5x the estimate). The figure as currently rendered actively undermines the analysis.
   - Effort: Low. Add hatching or a separate panel grouping in `step9_did_comparison_figure.py`.

### Category C (Minor)

1. **[C1]: Johansen cointegration rank determination logic may over-count**
   - Current state: `step2_cointegration_vecm.py` (lines 72-82) determines rank by iterating from i=0 upward and setting `rank = len(cols) - i` at the first rejection. For a bivariate system, if the trace statistic at r=0 exceeds the critical value, rank is set to 2 (full rank). This means no cointegration testing at r<=1 is performed -- the test immediately declares full rank.
   - Suggested improvement: The standard sequential procedure tests r=0 first; if rejected, test r<=1; if rejected, declare full rank. The current code should break after the first rejection only if it also checks the next hypothesis.
   - Effort: Low. Adjust the loop to test sequentially and report the first non-rejection.

2. **[C2]: Placebo treatment test uses time-shifted versions of the same variable rather than genuinely unrelated variables**
   - Current state: The placebo test shifts the cause variable by 2-5 years (`step5_refutation_tests.py`, lines 96-132). A shifted version of the digital economy index is still correlated with the original (autocorrelation), which means the "placebo" is not genuinely unrelated.
   - Suggested improvement: Add a second placebo variant that uses a genuinely unrelated macro variable (e.g., a random walk, or an unrelated country's time series) as the placebo treatment. This would complement the time-shift approach with a true null.
   - Effort: Low.

3. **[C3]: Random common cause test adds a white noise variable, but the relevant concern is a confounding trend**
   - Current state: `step5_refutation_tests.py` (line 154) generates `np.random.randn(len(df_rcc))` -- i.i.d. standard normal. For time series with strong trends, a random i.i.d. variable is unlikely to confound anything because it has no serial dependence.
   - Suggested improvement: Generate the random common cause as a random walk or AR(1) process with high persistence. This tests sensitivity to an omitted trending confounder, which is the actual concern for this analysis (e.g., a missing institutional or policy variable that trends with both DE and employment).
   - Effort: Low. Replace `np.random.randn` with a cumulative sum (random walk) or AR(1) simulation.

4. **[C4]: VECM deterministic specification uses `det_order=0` (restricted constant) without sensitivity check**
   - Current state: All Johansen tests use `det_order=0` and `deterministic="ci"` for VECM. For trending macroeconomic data, `det_order=1` (restricted trend) may be more appropriate.
   - Suggested improvement: Run Johansen with both `det_order=0` and `det_order=1` and report whether the rank conclusion changes. The Pantula principle (test from most restrictive to least restrictive specification) is the standard approach for selecting the deterministic component.
   - Effort: Low.

5. **[C5]: The `method_comparison_summary.pdf` figure is referenced in the analysis but not visually verified in this review -- ensure forest plot normalization is consistent**
   - Suggested improvement: Verify that the forest plot panel in `did_baseline_comparison.pdf` normalizes test statistics from different methods (Granger W, ARDL F, Chow F, counterfactual t) to a common scale (e.g., z-scores or p-value equivalents) before plotting side by side. Mixing raw test statistics from different distributions on one axis is misleading.
   - Effort: Low.

---

## Method Appropriateness Assessment

### Toda-Yamamoto Granger Causality
The choice of Toda-Yamamoto over standard Granger causality is well-justified for this setting (I(1) variables, T=24). The procedure avoids the pre-testing problem of differencing (which may remove long-run information) while remaining valid regardless of cointegration status. The AIC-based lag selection is appropriate, though the sensitivity analysis (Section 6.6) reveals that significance is fragile across lag orders -- significant at p=1 but vanishing by p=3. This fragility is correctly documented.

### VECM Specification
Using Johansen cointegration followed by VECM is the standard approach for non-stationary multivariate systems. The ARDL bounds test as a secondary method is a strong choice given the ambiguity of unit root tests at T=24. However, the Pesaran (2001) asymptotic bounds should be supplemented with small-sample critical values (see B2).

### Structural Break Methodology
The Chow test at known dates and the counterfactual trend extrapolation are appropriate for the DID-inspired analysis. The break interaction regression ($\beta_2 = \text{POST} \times \Delta\text{DE}$) is the correct reduced-form specification for a structural break in first differences. The sensitivity to break year (Section 6.6) is a valuable addition. The main limitation -- no control group -- is prominently stated.

### Bootstrap Procedures
The residual bootstrap for Granger causality is methodologically appropriate in principle, but the i.i.d. resampling (A1) is a concern. The block bootstrap for the DID regressions (step8) is correctly implemented. The overall bootstrap strategy is sound; the execution needs the consistency fix described in A1 and B5.

### VAR Mediation
The use of VAR impulse responses and FEVD for mediation decomposition is appropriate for time series. The comparison between trivariate and bivariate VARs for computing mediation share is not valid (B3). The FEVD provides a better measure of the relative importance of DE shocks in explaining employment variation.

### Uncertainty Quantification
The four-number reporting (central, statistical, systematic, total) is followed for the primary results. The systematic uncertainty decomposition covers the key sources (demographic control, break year, COVID, lag selection). The exclusion of ill-defined systematics (functional form, lag structure) from the quadrature total is justified but should be better communicated in the figure (B6).

---

## Alternative Approaches to Consider

1. **Generalized impulse responses (Pesaran & Shin 1998) for VAR mediation.** These are invariant to variable ordering (unlike Cholesky), addressing Warning 7 from STRATEGY.md. The analysis mentions this as a potential robustness check but does not implement it. Given the mediation decomposition issues (B3), generalized IRFs could provide a more robust alternative.

2. **Bayesian VAR with Minnesota prior.** At T=24 with 3 variables, the VAR is estimated with very few effective observations per parameter. A Bayesian VAR with a shrinkage prior (Minnesota/Litterman) would regularize the estimates and produce more stable impulse responses. The wide confidence bands in `var_irf_mediation.pdf` suggest the frequentist VAR is overfitting. This is a medium-effort alternative that would strengthen the IRF analysis.

3. **Time-varying parameter (TVP) specification for the structural break.** Rather than imposing a discrete break at a single date, a TVP model (even a simple rolling-window OLS with window size 10-12) would capture gradual regime changes. This would address the finding that the DE index shows a structural break at 2009 (Warning 9 from Phase 2), which precedes the smart city pilot dates.

4. **Toda-Yamamoto with multiple lag orders reported as sensitivity band.** Rather than selecting a single p via AIC and reporting one W statistic, report the envelope of W statistics across p=1,2,3. This is partially done in Section 6.6 but could be formalized as a "lag-robust" Granger inference following Toda & Phillips (1993).

---

## Figure and Table Assessment

### `structural_break_did_baseline.pdf` (4-panel)
Well-structured and informative. Panel (a) clearly shows the DE index trajectory with the pilot window. Panel (d) effectively communicates the counterfactual deviation. The break window shading (orange) is visible and the color scheme works. Minor: panel (c) scatter plot has overlapping points with small marker size -- consider slight jitter or larger markers. The panel labels (a)-(d) are present and helpful.

### `var_irf_mediation.pdf` (3x3 IRF grid)
The confidence bands are extremely wide, spanning the entire y-axis for most panels. This makes the point estimates essentially uninformative. The figure honestly communicates the uncertainty but is visually overwhelming. Consider: (a) using 68% CI instead of (or in addition to) 90% CI, (b) increasing bootstrap replications to tighten the Monte Carlo component. The monochrome blue scheme is accessible but makes it hard to distinguish the point estimate line from the confidence fill in dense regions.

### `refutation_summary.pdf` (heatmap)
Effective and immediately interpretable. The red/green/orange color scheme communicates the PASS/MARGINAL/FAIL pattern clearly. The classification labels on the right margin are a good addition. This is one of the strongest figures in the analysis. Note: red-green color scheme is not colorblind-friendly. Consider using blue-orange or a diverging colormap with pattern fills for accessibility.

### `uncertainty_tornado.pdf`
As discussed in B6, the inclusion of "Functional form" (~95 pp) without visual distinction from well-defined systematics is misleading. The figure needs revision to separate model-structure changes from parameter perturbations.

### `did_baseline_comparison.pdf` (2x3 grid)
Dense but informative. The forest plot panels (right column) effectively compare methods. The DID-inspired counterfactual panels (left column) clearly show the pre/post separation. The Granger bar plots (middle column) are straightforward. The figure is quite small when rendered -- consider increasing the figure dimensions for the PDF output.

### `ep_propagation.pdf`
Clear progression from P0 through P3. The background shading for EP threshold zones (full analysis, lightweight, below soft, hard truncation) is an excellent design choice. Color scheme is distinguishable. One concern: the green zone is very dominant visually and might give the impression that results are stronger than they are. Consider using a neutral background for the "full analysis" zone and reserving strong color for the threshold lines only.

### `sensitivity_break_year.pdf`
Effective display of coefficient stability across break years. The confidence intervals appropriately convey the uncertainty at each break date. The two-panel layout (substitution vs. creation) enables direct comparison.

---

## Notation and Consistency

- Notation is generally consistent. $\beta_1$, $\beta_2$ are used throughout for the DID-inspired regressions; W for the Wald statistic; $\alpha$, $\beta$ for VECM parameters.
- The symbol "pp" (percentage points) is used consistently for employment share effects.
- One inconsistency: the analysis switches between "p_boot" and "p_bootstrap" in different tables. Standardize to one form.
- The Wald statistic is denoted W in the text but the underlying scripts compute it as `q * F_stat`. The mapping between the F-form and chi-squared form is stated once (line 174 of step1) but not in ANALYSIS.md. Adding a brief note that W = p * F where p is the number of restrictions would aid reproducibility.
- LaTeX math is correctly formatted throughout. Display equations use `$$` consistently.
