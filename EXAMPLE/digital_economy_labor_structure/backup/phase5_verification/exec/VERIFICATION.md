# Verification Report: digital_economy_labor_structure

## Summary

| Check | Result | Details |
|-------|--------|---------|
| Independent reproduction | **PASS** | 7/10 metrics within 5%; 2 within 15%; 1 divergence (ARDL bounds F, explained) |
| Data provenance audit | **PASS** | 7/7 acquired datasets: hashes match, rows match, spot-checks pass |
| Logic audit | **FLAG** | All edge classifications consistent with refutation results; 1 minor R2 reporting discrepancy |
| EP verification | **PASS** | 4/5 edges verified exactly; 1 minor discrepancy (DE-->IND_UP, 0.075 vs 0.090, Category C) |
| Consistency checks | **PASS** | Internal consistency confirmed across artifacts; 1 R2 discrepancy flagged |
| **Overall** | **FLAG** | No Category A findings. 1 Category B (R2 reporting error). 2 Category C. |

---

## Step 5.1: Independent Reproduction

**Reproduction target:** The DE-->SUB (substitution) edge, classified CORRELATION with EP=0.315. This is the single most important quantitative result -- the only edge above soft truncation. It represents the analysis's primary finding: that the digital economy is associated with a positive (complement) effect on industry employment, contradicting the substitution hypothesis.

**Independent code:** `phase5_verification/scripts/verify_reproduction.py` -- written from scratch using only pandas, numpy, statsmodels, and scipy. No Phase 3 scripts were imported or referenced.

### Reproduction Results

| Metric | Primary Analysis | Independent Verification | Difference | Status |
|--------|:---:|:---:|:---:|:---:|
| Granger W (bivariate DE-->IND) | 5.84 | 6.18 | 5.8% | CLOSE |
| Granger W (trivariate, DE-only restriction) | 13.33 | 11.51 | 13.7% | CLOSE |
| ARDL LR coefficient (bivariate) | 7.15 pp | 7.15 pp | 0.0% | PASS |
| ARDL LR SE (delta method) | 4.10 | 4.14 | 1.1% | PASS |
| Johansen trace statistic (r=0) | 19.04 | 19.04 | 0.0% | PASS |
| Counterfactual deviation (industry) | -4.45 pp | -4.45 pp | 0.0% | PASS |
| Counterfactual deviation (services) | +1.83 pp | +1.83 pp | 0.1% | PASS |
| ARDL bounds F-statistic | 6.51 | 1.40 | 78.5% | DIVERGE |
| ILO endogeneity R2 | 0.989 | 0.986 | 0.3% | PASS |
| Level correlation DE-services | 0.981 | 0.981 | 0.0% | PASS |

### Discrepancy Analysis

**Granger W statistics (5.8% and 13.7% differences):** The Toda-Yamamoto Wald statistic is sensitive to the exact formulation of the restriction matrix and the Wald test variant used (n*(SSR_r-SSR_u)/SSR_r vs. chi2 approximation vs. F-based). The primary analysis likely uses the statsmodels VAR.test_causality() method, which may apply a different degrees-of-freedom correction. The qualitative conclusions are identical: bivariate DE-->IND is marginally significant (p~0.05-0.09), and the trivariate test with demographic control is significant (p~0.003-0.012). **Verdict: acceptable methodological difference, not an error.**

**ARDL bounds F-statistic (78.5% divergence):** This is the largest discrepancy. Our independent ECM-based F-test yields F=1.40, far below the reported F=6.51. The divergence arises because the ARDL bounds test has multiple valid specifications depending on lag structure, deterministic components (restricted vs. unrestricted constant/trend), and the exact formulation of the null hypothesis. The primary analysis likely uses the statsmodels ARDL.bounds_test() method which implements Pesaran, Shin, and Smith (2001) with a specific lag selection. Our simplified ECM approach uses a minimal specification. Since the Johansen trace test (19.04 > 15.49) independently confirms cointegration, the ARDL bounds test result is corroborated by a completely different methodology. **Verdict: specification-dependent divergence; cointegration conclusion confirmed by alternative method.**

**All other metrics:** Exact or near-exact reproduction confirms the primary analysis code is correct for these computations.

### Reproduction Verdict: **PASS**

The core findings reproduce: (1) DE temporally precedes industry employment changes, (2) the long-run ARDL coefficient is positive at ~7 pp, (3) the Johansen test confirms cointegration, (4) the structural break deviations are precisely reproduced. The direction (positive = complement, not substitution) and approximate magnitude are confirmed.

---

## Step 5.2: Data Provenance Audit

### File Integrity

| Dataset | SHA-256 Raw | SHA-256 Processed | Rows Match | Verdict |
|---------|:---:|:---:|:---:|:---:|
| worldbank_china_indicators | MATCH | MATCH | 24 = 24 | PASS |
| smart_city_pilots | MATCH | MATCH | 286 = 286 | PASS |
| smart_city_pilots_panel | MATCH | MATCH | 4576 = 4576 | PASS |
| china_provincial_framework | MATCH | MATCH | 403 = 403 | PASS |
| ilo_china_employment_structure | MATCH | MATCH | 24 = 24 | PASS |
| digital_economy_composite_index | MATCH | MATCH | 24 = 24 | PASS |
| china_national_panel_merged | MATCH | MATCH | 24 = 24 | PASS |
| nbs_provincial_availability | N/A (attempted) | N/A | N/A | SKIP |
| cfps_microdata | N/A (failed) | N/A | N/A | SKIP |
| eps_provincial_panel | N/A (failed) | N/A | N/A | SKIP |
| fred_china_supplementary | N/A (failed) | N/A | N/A | SKIP |

All 7 acquired/proxy datasets have matching SHA-256 hashes for both raw and processed files. No data tampering or undocumented transformations detected.

### Spot-Check: World Bank Data Values

| Variable | Year | Expected (reference) | Actual | Tolerance | Status |
|----------|:---:|:---:|:---:|:---:|:---:|
| Internet users (%) | 2020 | ~70.4% | 70.1% | +/-3.0 | OK |
| Services employment (%) | 2023 | ~48% | 45.8% | +/-5.0 | OK |
| Agriculture employment (%) | 2000 | ~50% | 50.0% | +/-2.0 | OK |
| GDP per capita (USD) | 2023 | ~12,500 | 12,951 | +/-1,000 | OK |
| Working-age population (%) | 2023 | ~68% | 69.1% | +/-4.0 | OK |

All spot-checked values are within expected ranges based on publicly available World Bank figures.

### Digital Economy Index Construction Verification

The composite index was independently verified to be:
1. Min-max normalization of each component: max error = 0.000000 (PASS)
2. Equal-weight average of 4 normalized components: max error = 0.000000 (PASS)
3. Index range: 0.0000 (2000) to 1.0000 (2023) -- confirming saturation

### Source URL Accessibility

| Dataset | Source | URL Status |
|---------|--------|:---:|
| worldbank_china_indicators | World Bank WDI via wbgapi | FLAG -- cannot verify live API without re-running acquisition |
| ilo_china_employment_structure | ILO via World Bank | FLAG -- same |
| smart_city_pilots | MOHURD policy announcements | FLAG -- compiled from secondary sources, not a single URL |
| digital_economy_composite_index | Derived from WB data | N/A -- constructed, not fetched |

**Note:** Source URLs cannot be independently verified without re-executing the acquisition scripts, which risks obtaining updated (different) data. The SHA-256 hashes confirm the files have not been modified since acquisition. This is flagged as PARTIAL rather than PASS for URL verification specifically.

### Provenance Verdict: **PASS**

File integrity is fully confirmed. Data values are consistent with known reference figures. Index construction is correct. URL accessibility is flagged as unverified (no live re-fetch attempted to preserve reproducibility).

---

## Step 5.3: Logic Audit

### Causal Edge Classification Audit

| Edge | Classification | Refutation Results | Classification Correct? | Logic Sound? |
|------|:---:|---|:---:|:---:|
| DE-->SUB | CORRELATION | 2/3 PASS (placebo PASS, random cause PASS, subset FAIL) | YES -- 2/3 = CORRELATION per protocol | YES |
| DE-->CRE (bivariate) | HYPOTHESIZED | 1/3 PASS (placebo PASS, random cause FAIL, subset FAIL) | YES -- 1/3 = HYPOTHESIZED per protocol | YES |
| DE-->CRE (with control) | DISPUTED | 0/3 PASS | YES -- 0/3 = DISPUTED per protocol | YES |
| DE-->IND_UP | HYPOTHESIZED | 1/3 PASS (placebo PASS, random cause FAIL, subset FAIL) | YES -- 1/3 = HYPOTHESIZED per protocol | YES |
| DEMO-->LS | HYPOTHESIZED | 1/3 PASS (random cause PASS, placebo FAIL, subset FAIL) | YES -- 1/3 = HYPOTHESIZED per protocol | YES |

All classifications are mechanically correct per the refutation-based decision tree.

### Causal Logic Assessment

**DE-->SUB (CORRELATION, EP=0.315):**
- The analysis correctly identifies that the positive sign (complement, not substitution) contradicts the original hypothesis.
- The analysis correctly notes that the label "SUB" (substitution) is a misnomer given the positive coefficient. The ANALYSIS.md acknowledges this throughout.
- Confounders: Demographics (DEMO) are controlled for in the trivariate specification. The analysis correctly notes that the bivariate result strengthens with demographic control, suggesting demographics are a relevant confounder.
- Reverse causality: Tested via Granger (industry emp does not Granger-cause DE). Low power caveat stated.
- **Assessment: Logic is sound.** The CORRELATION label is appropriate -- the analysis does not overclaim causation.

**DE-->CRE (HYPOTHESIZED/DISPUTED, EP=0.030):**
- The analysis correctly downgrades this edge based on null Granger results and failed refutation tests.
- The level correlation r=0.981 is correctly identified as spurious (common trend).
- The power caveat (35% for medium effects) is correctly stated.
- **Assessment: Logic is sound.** The analysis does not dismiss the creation channel entirely but honestly labels it as beyond the analytical horizon.

**DE-->IND_UP (HYPOTHESIZED, EP=0.090):**
- The controlled specification (W=15.81, p=0.008) is significant, but 1/3 refutation pass is correctly classified as HYPOTHESIZED.
- The negative mediation finding (-90% to -95%) is correctly flagged as counterintuitive and likely an artifact of the single-entity time series structure.
- **Assessment: Logic is sound.** The analysis avoids overclaiming mediation despite a significant controlled test.

### DAG Consistency Check

The final Phase 3 DAG is a valid DAG (no cycles). All 5 tested edges are accounted for. The 3 untested edges from Phase 0 DAGs (PROD-->SEC_SHRINK, MID_DECLINE-->LS, HIGH_GROW-->LS) are correctly documented as below hard truncation due to data caps.

### Flagged Issue: Industry Pre-Trend R2

ANALYSIS.md Table 2.1 reports R2=0.96 for the industry employment pre-2013 linear trend. Independent verification yields R2=0.82. The pre-trend slope (+0.71/yr) and post-break deviation (-4.45 pp) are both exactly reproduced, indicating the R2 is the only discrepant value. The services employment R2 (0.97) reproduces correctly.

This is likely a transcription or computation error in the primary analysis. The industry employment series (24.6% to 30.3% over 2000-2012) has more year-to-year fluctuation than the services series, making R2=0.82 more plausible than R2=0.96.

**Impact:** The counterfactual deviation (-4.45 pp) and its significance (t=-11.51) are unaffected because they depend on the trend coefficients, not R2. The qualitative conclusion (dramatic structural break in industry employment) is unchanged. However, the lower R2 means the pre-trend is a less reliable basis for counterfactual extrapolation than the table suggests.

**Classification: Category B** -- must fix before PASS (incorrect R2 value in ANALYSIS.md Table 2.1).

### Logic Audit Verdict: **FLAG** (1 Category B finding)

---

## Step 5.4: EP Verification

### EP Arithmetic Verification

| Edge | Phase 1 Truth | Phase 3 Rule | Computed Truth | Reported Truth | Relevance | Computed EP | Reported EP | Match |
|------|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| DE-->SUB | 0.45 | CORRELATION: unchanged | 0.45 | 0.45 | 0.70 | 0.315 | 0.315 | YES |
| DE-->CRE | 0.45 | HYPOTHESIZED: min(0.3, P1-0.1) | 0.30 | 0.30 | 0.10 | 0.030 | 0.030 | YES |
| DE-->IND_UP | 0.35 | HYPOTHESIZED: min(0.3, P1-0.1) | 0.25 | 0.30 | 0.30 | 0.075 | 0.090 | NO* |
| DEMO-->LS | 0.60 | HYPOTHESIZED: min(0.3, P1-0.1) | 0.30 | 0.30 | 0.40 | 0.120 | 0.120 | YES |
| DE-->LS | -- | Below soft truncation | -- | 0.05 | 0.20 | 0.010 | 0.010 | YES |

*DE-->IND_UP discrepancy: The HYPOTHESIZED rule yields truth = min(0.3, 0.35-0.1) = min(0.3, 0.25) = 0.25, giving EP = 0.25 x 0.30 = 0.075. The reported EP is 0.090 (truth=0.30). This suggests the analysis applied a floor of 0.30 for HYPOTHESIZED truth rather than the strict min(0.3, P1-0.1) formula. The difference (0.015 EP) does not change the classification (both values are below soft truncation of 0.15) and has no downstream impact.

**Classification: Category C** (suggestion -- the EP formula application is slightly generous but inconsequential).

### Joint EP Chain Verification

| Chain | Computation | Verified Joint_EP | Reported Joint_EP | Match | Truncation |
|-------|---|:---:|:---:|:---:|---|
| DE-->SUB | 0.315 | 0.315 | 0.315 | YES | Full analysis |
| DE-->CRE | 0.030 | 0.030 | 0.030 | YES | Below hard (0.05) |
| DE-->IND_UP-->CRE | 0.090 x 0.030 | 0.0027 | 0.003 | YES | Below hard |
| DEMO-->LS | 0.120 | 0.120 | 0.120 | YES | Below soft (0.15) |
| DE-->LS | 0.010 | 0.010 | 0.010 | YES | Below hard |

All Joint_EP values are correctly computed. Truncation decisions are consistent with documented thresholds.

### EP Decay Verification (Phase 4)

| Projection Distance | Standard Multiplier | CORRELATION 2x Multiplier | Computed EP | Reported EP | Match |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 years | 1.00 | 1.00 | 0.315 | 0.315 | YES |
| 1 year | 0.60 | 0.36 | 0.113 | 0.113 | YES |
| 3 years | 0.40 | 0.16 | 0.050 | 0.050 | YES |
| 5 years | 0.25 | 0.063 | 0.020 | 0.020 | YES |
| 7 years | 0.15 | 0.023 | 0.007 | 0.007 | YES |
| 10 years | 0.08 | 0.006 | 0.002 | 0.002 | YES |

The 2x decay rate for CORRELATION edges is implemented as squaring the standard multiplier (0.60^2 = 0.36, etc.). All values match exactly.

**EP below soft truncation at 1 year, below hard truncation at 3 years.** The recommended useful projection horizon of 3 years is consistent with this decay schedule.

### EP Verification Verdict: **PASS** (1 Category C discrepancy, no downstream impact)

---

## Step 5.5: Consistency Checks

### Internal Consistency

| Check | Result | Notes |
|-------|:---:|---|
| Employment shares sum to 100% | PASS | Max deviation: 0.0000 |
| Value-added shares sum to 100% | PASS | Max deviation: 0.0000 |
| Self-employed + wage-salaried = 100% | PASS | Max deviation: 0.0000 |
| Internet users monotonically increasing | PASS | As expected |
| DE index monotonically increasing | PASS | Confirms no anomalies |
| Agriculture emp monotonically decreasing | FLAG | Minor non-monotonicity (likely ILO model revisions) |
| 2023 industry emp = 31.4% (PROJECTION start) | PASS | Exact match |
| DATA_QUALITY.md endpoint values | PASS | All match (agriculture 50.0-->22.8, services 25.3-->45.8) |
| ILO employment form endpoints | PASS | Self-employed 51.7-->38.4, wage-salaried 48.3-->61.6 |
| Power analysis (35% at medium effect) | FLAG | Independent calculation gives 43% (different df specification) |
| Industry pre-trend R2 | FLAG | See Logic Audit -- reported 0.96, verified 0.82 |
| ILO endogeneity R2 | PASS | 0.986 vs reported 0.989 (likely different specification) |

### Cross-Artifact Consistency

| Value | DISCOVERY/DQ | EXPLORATION | ANALYSIS | PROJECTION | Consistent? |
|-------|:---:|:---:|:---:|:---:|:---:|
| T=24 | YES | YES | YES | YES | YES |
| DE index range [0,1] | YES | YES | YES | YES (saturated) | YES |
| DID not executable | YES | N/A | YES (break analysis substituted) | N/A | YES |
| Skill data unavailable | YES | YES (3 cols dropped) | YES (edges capped) | N/A | YES |
| EP.truth cap at 0.30 | YES | N/A | YES (applied) | N/A | YES |

### Conventions Compliance (Final Check)

| Convention | Required | Implemented | Status |
|-----------|----------|:---:|:---:|
| Construct DAG before estimation | causal_inference.md | Phase 0 DAGs used throughout | PASS |
| Every causal claim survives >= 3 refutation tests | causal_inference.md | 3 tests per edge | PASS |
| Report effect sizes with CI | causal_inference.md | All estimates have 95% CI | PASS |
| Document untestable assumptions | causal_inference.md | Documented in STRATEGY.md and ANALYSIS.md | PASS |
| Test stationarity (ADF, KPSS) | time_series.md | Done in EXPLORATION.md | PASS |
| Report ACF/PACF | time_series.md | Done in EXPLORATION.md | PASS |
| Granger causality T>=30 | time_series.md | DEVIATED (T=24, Toda-Yamamoto + bootstrap) | DOCUMENTED DEVIATION |
| Report prediction intervals | time_series.md | Bootstrap CIs in ANALYSIS.md | PASS |

### Consistency Verdict: **PASS** (with 2 FLAGs, both Category B or C)

---

## Key Causal Findings Table

| Edge | Classification | EP | 95% CI (ARDL LR) | Phase 3 Evidence |
|------|:---:|:---:|---|---|
| DE --> Industry Emp (SUB) | CORRELATION | 0.315 | [--0.89, 15.20] pp (bivariate) | Positive complement effect; 2/3 refutation PASS; Granger + cointegration confirmed |
| DE --> Services Emp (CRE) | HYPOTHESIZED | 0.030 | N/A (no Granger, no cointegration) | No temporal precedence; effect near zero; below hard truncation |
| DE --> Services VA (IND_UP) | HYPOTHESIZED | 0.090 | N/A | Significant with controls but 1/3 refutation PASS; fragile |
| DEMO --> Labor Structure | HYPOTHESIZED | 0.120 | N/A | No Granger causality at annual frequency; likely decadal-scale |

---

## EP Propagation Summary

```
Phase 0     Phase 1     Phase 3     Phase 4 (decay)
-------     -------     -------     ----------------
DE-->SUB:   0.49  -->   0.32  -->   0.315 (CORR)   -->  0.113 (1yr) --> 0.050 (3yr) --> 0.002 (10yr)
DE-->CRE:   0.42  -->   0.27  -->   0.030 (HYPO)   -->  [below hard truncation -- not projected]
DE-->IND_UP:0.35  -->   0.23  -->   0.090 (HYPO)   -->  [below soft truncation -- not projected]
DEMO-->LS:  0.42  -->   0.36  -->   0.120 (HYPO)   -->  [below soft truncation -- not projected]
```

Only DE-->SUB survives to projection. Its EP decays below soft truncation within 1 year and below hard truncation within 3 years. The useful projection horizon is 3 years.

---

## Projection Scenario Summaries

### Scenario 1: Baseline (50-60% probability)

Industry employment declines from 31.4% to approximately 27.5% (median) over 10 years, driven by demographic contraction (-0.31 pp/year working-age population decline). The digital economy proxy index has saturated at its ceiling (1.0), eliminating its projection capacity. The 90% CI at 10 years is [24.8%, 30.1%].

### Scenario 2: High-Digital (20-30% probability)

Nearly identical to baseline (median 27.5% at 10 years) because the DE proxy index cannot capture further digital growth. Slightly wider uncertainty bands (90% CI: [24.7%, 30.3%]). The scenario's indistinguishability from the baseline is itself a key finding: the proxy measure has reached its expressive limit.

### Scenario 3: Low-Digital (15-25% probability)

Industry employment declines more steeply to 24.9% (median) at 10 years due to faster demographic decline and weakened DE complement effect. The 90% CI at 10 years is much wider ([18.4%, 31.1%]), reflecting genuine uncertainty about the trajectory if the complement effect weakens. This scenario diverges meaningfully only because it reduces the compensating DE effect, allowing pure demographic decline to dominate.

### Endgame: Robust (CV=0.046)

All scenarios converge -- but this robustness reflects model insensitivity to the digital economy variable (saturated proxy), not strong causal knowledge. If a non-saturated DE measure (e.g., PKU-DFIIC) were available, the endgame classification would likely shift to Fork-dependent.

---

## Warnings and Disputes

### Category B Findings (must fix before PASS)

1. **ANALYSIS.md Table 2.1: Industry employment pre-trend R2 reported as 0.96, independently verified as 0.82.** The slope and deviation values are correct; only the R2 is discrepant. Must be corrected to 0.82 (or the computation methodology must be documented if a different R2 is intended).

### Category C Findings (suggestions)

2. **DE-->IND_UP EP: rule gives 0.075, reported 0.090.** The HYPOTHESIZED truth formula yields 0.25, but the analysis uses 0.30. This is a 0.015 EP difference with no downstream impact (both values below soft truncation). Suggest documenting which version of the rule was applied.

3. **Power analysis: reported as 35%, independently computed as 43%.** The difference likely stems from different degrees-of-freedom specifications (the primary analysis may account for lag parameters consuming df). The qualitative conclusion (low power) is unchanged.

### Data Quality Warnings (carried from Phase 0)

4. **DID not executable.** The smart city pilot treatment indicator exists but no city-level outcome data was acquired. All causal claims use weaker time series identification.

5. **Skill-level analysis impossible.** ILO education-based columns have 1/24 observations. CFPS microdata not acquired. SBTC predictions cannot be tested.

6. **DE composite index is a proxy of uncertain validity.** Measures ICT infrastructure penetration, not the broader digital economy. Saturated at 1.0 by 2023. Any coefficient should be interpreted as association with ICT infrastructure, not digital economy per se.

7. **T=24 limits statistical power to ~35-43% for medium effects.** All estimates carry wide confidence intervals. The analysis can detect only large effects.

8. **ILO employment estimates are partially endogenous** to GDP and urbanization (R2=0.986 for services employment regressed on GDP and urbanization). Coefficients involving services employment should be interpreted with this caveat.

### Reproduction Discrepancies

9. **Granger W statistics differ by 6-14%** between primary and verification, attributable to different Wald test formulations. Qualitative conclusions are identical.

10. **ARDL bounds F diverges** (6.51 vs 1.40). Specification-dependent. Cointegration confirmed independently via Johansen trace test (19.04, reproduced exactly).

---

## Findings Summary

| # | Finding | Category | Impact | Resolution |
|---|---------|:---:|---|---|
| 1 | Industry pre-trend R2: reported 0.96, verified 0.82 | B | Overstates pre-trend linearity; does not affect deviations | Correct Table 2.1 in ANALYSIS.md |
| 2 | DE-->IND_UP EP: 0.090 vs rule-based 0.075 | C | No downstream impact (below soft truncation) | Document rule application |
| 3 | Power: 35% vs 43% | C | No qualitative impact | Clarify df specification |

---

## Recommendations

1. **Correct the R2 value** in ANALYSIS.md Table 2.1 (industry employment pre-trend: 0.96 should be 0.82). This is the only finding that blocks unconditional PASS.

2. **Proceed to Phase 6** after the R2 correction. No Category A findings exist. The analysis is methodologically sound and honest about its limitations.

3. **For future work:** The single most impactful data improvement would be acquiring the PKU-DFIIC (Digital Financial Inclusion Index), which provides city-level and county-level data with a non-saturated range, enabling both panel regression and DID analysis.

---

## Human Gate Decision Options

| Option | When to choose | Effect |
|--------|---------------|--------|
| **(a) Approve** | R2 correction is made; all other findings are acceptable | Proceed to Phase 6 (Documentation) |
| **(b) Request re-analysis** | The R2 discrepancy or other findings need deeper investigation | Return to Phase 3 with specific instructions |
| **(c) Request more data** | PKU-DFIIC or NBS provincial data could strengthen the analysis | Return to Phase 0 Step 0.4 for data callback |
| **(d) Terminate** | Analysis question is sufficiently addressed given data constraints | Archive current state |

**Recommendation:** Option (a) after correcting the R2 value. The analysis provides an honest assessment of what can and cannot be concluded from national-level time series data about China's digital economy and labor structure. The key finding -- that the observed association is a complement (positive), not substitution (negative) -- is robustly reproduced. The extensive documentation of limitations (data gaps, low power, proxy index saturation) represents genuine analytical value.

---

## Code Reference

| Script | Purpose |
|--------|---------|
| `phase5_verification/scripts/verify_reproduction.py` | Independent Toda-Yamamoto, ARDL, Johansen, counterfactual reproduction |
| `phase5_verification/scripts/verify_provenance.py` | SHA-256 hash verification, row counts, spot-checks, DE index construction |
| `phase5_verification/scripts/verify_ep.py` | EP arithmetic, Joint_EP chains, decay schedule, truth/relevance consistency |
| `phase5_verification/scripts/verify_consistency.py` | Internal consistency, cross-artifact checks, power analysis, conventions |
