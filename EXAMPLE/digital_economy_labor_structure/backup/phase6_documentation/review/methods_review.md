# Methods Review: Phase 6 Documentation

## Review Summary
- **Phase**: Phase 6 (Documentation)
- **Artifacts reviewed**:
  - `/phase6_documentation/exec/REPORT.md`
  - `/phase6_documentation/exec/ANALYSIS_NOTE.md`
  - `/phase6_documentation/audit_trail/methodology.yaml`
  - Upstream: `/phase1_strategy/exec/STRATEGY.md`, `/phase3_analysis/exec/ANALYSIS.md`
- **Date**: 2026-03-30
- **Category A issues**: 0
- **Category B issues**: 4
- **Category C issues**: 5
- **Positive markers**: 8

---

## What Works Well

[+] **Toda-Yamamoto selection and justification.** The choice of Toda-Yamamoto over standard Granger causality at T=24 is well-justified across all documents. The original paper's simulation evidence (T=25) is correctly cited. The bootstrap p-values provide the necessary small-sample correction. This is a textbook-appropriate adaptation.

[+] **ARDL bounds test as complement to Johansen.** Using both Johansen and ARDL for cointegration is sound methodology for ambiguous integration orders. The REPORT correctly explains why both are needed and what each contributes.

[+] **VAR mediation over Baron-Kenny.** Rejecting Baron-Kenny for time series mediation and substituting VAR impulse response decomposition is the correct methodological call. The justification (i.i.d. violation) is accurate and the Blanchard-Quah reference is appropriate.

[+] **Refutation test transparency.** Both REPORT.md and ANALYSIS_NOTE.md report all refutation test results including failures. The data subset FAIL for DE->SUB is not hidden or minimized. The honest treatment of 2/3 PASS leading to CORRELATION (not DATA_SUPPORTED) follows the protocol correctly.

[+] **Power caveat on null results.** The creation channel null result is consistently accompanied by the 35% power caveat throughout both documents. The REPORT's framing ("cannot be interpreted as evidence that the digital economy does not create services employment") is epistemically honest and correctly prevents misinterpretation.

[+] **EP decay with CORRELATION penalty.** The 2x decay rate for CORRELATION edges is correctly applied and the resulting 3-year useful projection horizon is a defensible consequence.

[+] **Structural break framing.** The REPORT is clear that structural break analysis is not DID. The distinction between "before-and-after" and "treatment-vs-control" is stated explicitly multiple times. This prevents the most likely misinterpretation a reader might make.

[+] **Uncertainty decomposition with exclusion justification.** The ANALYSIS_NOTE's exclusion of lag selection and functional form from the quadrature sum (on grounds that they represent model redefinitions, not perturbations) is a defensible methodological choice that is transparently documented.

---

## Suggested Improvements

### Category A (Blocking)

None.

### Category B (Important)

1. **[B1]: ARDL bounds F-statistic divergence inadequately resolved in REPORT.md**
   - Current state: The REPORT (Section 11, Verification Summary) notes the 78.5% divergence between primary F=6.51 and independent F=1.40, then states "Cointegration is independently confirmed by the Johansen trace test (19.04, reproduced exactly), so the cointegration conclusion is robust." The ANALYSIS_NOTE repeats the same framing.
   - Suggested improvement: The divergence is not merely a "specification-dependent difference" -- it is a fundamental disagreement about whether the ARDL bounds test confirms cointegration. F=1.40 falls below the lower bound (4.04 at 10%), meaning the independent replication finds *no evidence* of cointegration via ARDL. The report should (a) state explicitly that the ARDL cointegration result is non-reproducible, (b) note that the Johansen result *is* reproducible and independently supports cointegration, and (c) downweight the ARDL bounds test accordingly in the method comparison table (REPORT Section 4.1 and ANALYSIS_NOTE Section 3, DE->SUB). Relying on Johansen alone for the cointegration conclusion is defensible, but the current text obscures the severity of the ARDL failure.
   - Why it matters: A reader who sees "ARDL confirms cointegration" in the findings sections and then "78.5% divergence" in the verification section encounters a contradiction. The findings sections should reflect the verification outcome.
   - Effort: Low. Adjust the wording in the substitution channel section of both documents to qualify the ARDL bounds result.

2. **[B2]: Bootstrap CI for ARDL long-run coefficient is missing**
   - Current state: The ARDL long-run coefficient (+7.15 pp) is reported with a delta-method SE (4.10) and corresponding 95% CI of [-0.89, 15.20]. The block bootstrap is applied to the DID-inspired regression (ANALYSIS_NOTE Section 7), but no bootstrap CI is reported for the ARDL long-run coefficient itself.
   - Suggested improvement: The ARDL long-run coefficient is derived via the delta method (the ratio $(\theta_0 + \theta_1)/(1-\phi)$). At T=24, the delta-method approximation for ratio estimators can be unreliable, especially when $\phi$ is near 1 (here $\phi = 0.816$). A block bootstrap CI for the long-run coefficient would provide a more trustworthy interval. If already computed but not reported, include it. If not computed, note this as a limitation of the reported CI.
   - Why it matters: The ARDL long-run coefficient is the headline result (+7.15 pp). Its CI is the primary basis for assessing whether the complement effect is statistically distinguishable from zero. A potentially unreliable CI on the headline number is a material gap.
   - Effort: Medium. Requires either running a bootstrap on the ARDL specification or adding an explicit caveat about delta-method limitations at small T.

3. **[B3]: Refutation test for DE->IND_UP (mediation) EP value inconsistency between documents**
   - Current state: REPORT.md and ANALYSIS_NOTE.md both report EP=0.090 for the mediation edge. Phase 5 verification found a rule-based value of 0.075 (Category C discrepancy, documented in verification.yaml). The REPORT does not mention this discrepancy in the mediation section, only in the verification summary.
   - Suggested improvement: Either (a) correct the EP to 0.075 per the mechanical rule, or (b) explicitly justify why 0.090 is retained despite the Phase 5 flag. Since the ANALYSIS_NOTE documents the discrepancy in Section 9 (verification), the REPORT should at minimum note it in the mediation subsection or in the EP evolution table.
   - Why it matters: Consistency of EP values across documents is a core audit requirement. The discrepancy is small and has no downstream impact, but leaving it unaddressed in the REPORT weakens the audit trail.
   - Effort: Low. Add a footnote or parenthetical in the mediation section.

4. **[B4]: methodology.yaml is too sparse -- does not capture all non-trivial analytical choices**
   - Current state: methodology.yaml contains 5 entries (M_auto_1 through M_auto_5), covering the five method selections from Phase 1. It does not capture several non-trivial choices documented in the REPORT and ANALYSIS_NOTE.
   - Suggested improvement: Add entries for at least:
     - Lag order selection (AIC-based, p=2 for primary specifications)
     - Break year definition (2013-2015 transition window exclusion vs. all-years HAC specification)
     - Cholesky ordering in VAR mediation (DE first, then VA, then employment)
     - EP decay rate multiplier (2x for CORRELATION edges)
     - Equal-weight construction of DE composite index
     - COVID-period handling (exclusion as systematic uncertainty, not baseline)
     - Monte Carlo parameters (10,000 iterations, seed 20260329)
   - Why it matters: The audit trail's purpose is to make every analytical choice traceable. The methodology.yaml currently captures only the highest-level method selections, missing the implementation-level choices that actually drive results.
   - Effort: Low-medium. The information exists in the REPORT and ANALYSIS_NOTE; it needs to be extracted into YAML format.

### Category C (Minor)

1. **[C1]: REPORT uses "pp" (percentage points) without defining the abbreviation on first use**
   - Suggested improvement: Define "pp" parenthetically at first occurrence in the Executive Summary: "+7.15 percentage points (pp) per unit DE increase."
   - Effort: Low.

2. **[C2]: Sensitivity tornado description omits sign information**
   - Current state: The sensitivity table (REPORT Section 7) shows "impact" as unsigned magnitudes. For the demographic parameters, the reader cannot tell whether increasing the demographic effect size shifts the projection up or down.
   - Suggested improvement: Report signed sensitivities or add a direction column.
   - Effort: Low.

3. **[C3]: The ANALYSIS_NOTE's DID specification (Equation 1) omits the demographic control present in the preferred specification**
   - Current state: Equation 1 in ANALYSIS_NOTE Section 6 shows the bivariate DID model without the demographic control term. The preferred specification (with demographic control) is only shown in the results table.
   - Suggested improvement: Show the full preferred specification as the equation, or present both bivariate and controlled specifications as separate numbered equations.
   - Effort: Low.

4. **[C4]: Block bootstrap block size (3) is not justified**
   - Current state: ANALYSIS_NOTE Section 7 states "Block bootstrap (block size=3, 2000 replications)" without justifying the block size choice.
   - Suggested improvement: Add brief justification. At T=24, the standard cube-root rule gives $T^{1/3} \approx 2.9 \approx 3$. Stating this would preempt reviewer questions about an arbitrary-seeming parameter.
   - Effort: Low.

5. **[C5]: Minor notation inconsistency for regression coefficients between REPORT and ANALYSIS_NOTE**
   - Current state: The REPORT uses $\beta_{\text{DE}}$ in the projection section and $\beta_1$ in the substitution channel. The ANALYSIS_NOTE uses $\beta_1$/$\beta_2$ consistently for the DID specification but the mapping to the REPORT's named parameters is implicit.
   - Suggested improvement: Use a consistent notation scheme across both documents, or add a brief mapping note.
   - Effort: Low.

---

## Method Appropriateness Assessment

### Causal Inference Methods

The analysis faces a fundamental identification challenge: T=24 national time series with no cross-sectional variation. The chosen methods (Toda-Yamamoto Granger, Johansen cointegration, ARDL bounds, structural break analysis) represent the appropriate toolkit for this data structure. The decision to deviate from the DoWhy pipeline (designed for i.i.d. or panel data) is well-justified and correctly documented in the conventions compliance table.

The Toda-Yamamoto procedure is the correct small-sample adaptation for Granger causality with potentially integrated series. The bootstrap p-values add a necessary layer of robustness. The dual cointegration approach (Johansen + ARDL) is conservative and appropriate given ambiguous unit root test results at T=24.

The structural break analysis as a DID substitute is the weakest methodological link, but this is acknowledged transparently. The REPORT correctly emphasizes that "there is no control group" and that concurrent events confound the estimate. The Chow test in first differences (rather than levels) is the correct specification to avoid spurious regression.

One methodological concern worth noting: the ARDL long-run coefficient changes from +7.15 (bivariate) to +12.57 (with demographic control), a 76% increase. This sensitivity to a single control variable, while interpretable as confounding removal, also raises the possibility of multicollinearity or instability at T=24 with limited degrees of freedom. The REPORT discusses this as a confounding effect, which is one valid interpretation, but does not discuss the alternative interpretation (model instability). This is captured in the uncertainty decomposition (demographic control inclusion = 7.78 pp shift, 33% of systematic uncertainty), so the numerical impact is accounted for, but the interpretive ambiguity could be acknowledged.

### Refutation Tests

The three-test battery (placebo treatment, random common cause, data subset) is well-designed and correctly adapted for time series. The placebo treatment test uses shifted treatment timing rather than spatial placebos -- the correct adaptation. The random common cause test adds a noise variable to the VAR system. The data subset test (25% drop) is aggressive but appropriate for T=24 where each observation is approximately 4% of the sample.

The reporting of refutation results is thorough. Both the bivariate and controlled specifications are tested separately, with the controlled specification's results used for classification. This is correct procedure.

One gap: the refutation tests are all applied to the Granger causality results (Toda-Yamamoto W statistics). No refutation tests are reported for the ARDL long-run coefficient or the cointegration rank. While Granger causality is the primary directional test, the long-run coefficient from ARDL is the headline effect size. Robustness of that coefficient to placebo timing and data subsets would strengthen the analysis.

### Uncertainty Propagation

The four-number reporting (central, statistical, systematic, total) follows the framework correctly. The dominant source identification (bootstrap SE > 50% of point estimate) is informative and correctly highlights that more data, not better methods, is the primary path to improved precision.

The exclusion of lag selection and functional form from the quadrature sum is documented but deserves scrutiny. Lag selection shifts the estimate by 21+ pp (more than the point estimate itself), and functional form shifts by 95+ pp. Calling these "model redefinitions rather than perturbations" is a judgment call. An alternative framing would report the full envelope including these sources, clearly separated from the perturbative systematics. The current approach is defensible but conservative in its reported uncertainty.

The correlation between systematic sources is not discussed. Demographic control inclusion and break year choice may be correlated (both relate to the structural break timing), which would mean the quadrature sum slightly overstates the combined systematic uncertainty. At the current precision level this is unlikely to be consequential, but noting the assumption of uncorrelated systematics would improve methodological transparency.

---

## Alternative Approaches to Consider

1. **Wavelet coherence analysis.** The REPORT identifies a key tension: demographics operate at decadal frequency while Granger tests capture annual dynamics. Wavelet coherence analysis decomposes the co-movement between DE and employment structure across multiple frequency bands simultaneously, potentially detecting the demographic signal at low frequency and the DE signal at higher frequency. This is a medium-effort addition that could strengthen the frequency-mismatch discussion in Section 5 (demographics). Package: `pywt` (available via PyPI).

2. **Spectral Granger causality.** Related to the wavelet suggestion: frequency-domain Granger causality (Breitung-Candelon test) would test whether DE Granger-causes employment at specific frequency bands. If the DE signal is present at business-cycle frequency (3-7 years) but absent at decadal frequency, this would sharpen the interpretation of why demographics fail the annual Granger test. Effort: medium.

3. **Synthetic control using other developing economies.** Although the REPORT states DID is infeasible due to missing city-level data, a synthetic control approach using other developing economies as donors (matched on pre-2013 employment structure, GDP, and urbanization) could provide a counterfactual for China's post-2013 trajectory. This does not require city-level data -- it uses country-level data with China as the single treated unit. The WDI data already acquired includes other countries. Effort: medium-high.

4. **Recursive or rolling-window Granger causality.** Rather than a single data subset refutation test, computing expanding-window or rolling-window Granger W statistics (e.g., from T=15 onward) would show how the causal evidence accumulates or deteriorates over time. This directly visualizes the data subset instability and provides more diagnostic information than a single PASS/FAIL verdict. Effort: low.

---

## Figure and Table Assessment

All 19 figures referenced in the documents exist in both `phase6_documentation/exec/figures/` and `phase6_documentation/figures/`. Based on the figure references in the text:

- **EP decay chart** (`ep_decay_chart.pdf`): Referenced prominently in both documents as the "core figure." The dual-panel layout (projection with bands + EP decay curve) is the correct structure per the framework. The description mentions confidence tier transition markers.

- **Structural break figure** (`structural_break_did_baseline.pdf`): Four-panel layout (DE index, employment trends, scatter, counterfactual). Follows the Phase 1 strategy specification exactly.

- **Method comparison** (`method_comparison_summary.pdf`): Two-row layout (substitution top, creation bottom) with Granger, ARDL, and Chow results. Valuable summary figure.

- **Sensitivity tornado** (`sensitivity_tornado.pdf`): Appropriately shows the zero-sensitivity result for DE parameters. Color coding by controllability is a good design choice.

- **Uncertainty tornado** (`uncertainty_tornado.pdf`): Shows the statistical vs. systematic decomposition for the substitution channel.

- **VAR IRF mediation** (`var_irf_mediation.pdf`): Shows the counterintuitive negative mediation result. Important for the mediation section's argument.

Tables in both documents are well-organized with consistent formatting. The EP evolution table in the REPORT provides a clear Phase 0 to Phase 3 progression. Refutation tables use a consistent format across all edges.

One suggestion: a ratio panel (observed/counterfactual) in the structural break figure would make the -4.45 pp deviation more visually immediate. This is a low-priority enhancement.

---

## Notation and Consistency

- **EP notation is consistent.** EP = truth x relevance is used throughout. Joint_EP as the product along chains is applied correctly.

- **Classification labels are consistent.** DATA_SUPPORTED, CORRELATION, HYPOTHESIZED, DISPUTED are used identically across both documents and match the refutation outcomes.

- **Statistical notation is standard.** $W$ for Wald statistic, $F$ for F-statistic, $p$ and $p_{\text{boot}}$ for asymptotic and bootstrap p-values. The subscript convention is clear.

- **Minor inconsistencies.** (a) The REPORT uses both "pp" and "percentage points" without standardizing. (b) Regression coefficient notation differs slightly between the REPORT and ANALYSIS_NOTE (see C5 above). Neither affects comprehension but both reduce polish.
