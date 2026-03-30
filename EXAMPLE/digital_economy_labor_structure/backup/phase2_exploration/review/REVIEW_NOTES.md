# Phase 2 Self-Review

**Reviewer:** Data Explorer (self-review per Phase 2 protocol)
**Date:** 2026-03-29
**Artifact:** `phase2_exploration/exec/EXPLORATION.md`

## Checklist

- [x] Data cleaning log is complete for every dataset?
  - Single primary dataset (merged national panel). Cleaning documented: 3 columns dropped (95.83% missing), missing values enumerated, outliers assessed, temporal integrity verified.

- [x] All engineered features are documented with formula and source?
  - 14 engineered features documented in Table (Section 2.1): log transform, binary indicators, first differences, growth rates. All validated for NaN/Inf.

- [x] Exploratory plots cover all key variables and causal edges?
  - 12 figure pairs (PDF+PNG) covering: time series, ACF/PACF, correlations (levels + diffs), distributions, scatter plots, demographic transition, structural breaks, power analysis, ILO endogeneity. All DAG edges from STRATEGY.md are covered.

- [x] Assumption pre-checks run for every planned method?
  - Stationarity (ADF+KPSS) for all 12 key variables: done.
  - Structural break (Chow + sup-Wald) at known dates: done.
  - Normality (Shapiro-Wilk): done.
  - ACF/PACF for lag structure: done.
  - Power analysis (Monte Carlo): done.
  - ILO endogeneity check: done.
  - Zivot-Andrews: attempted, failed due to T=24 numerical instability.

- [x] Variable ranking reflects DAG structure?
  - 15 variables ranked by DAG role, EP, quality, and association strength. Exclusions justified.

- [x] Data readiness assessment covers every Phase 3 causal edge?
  - 7 edges assessed in readiness table (Section 5.1). Method pivots discussed. Warnings carried forward.

- [x] Experiment log updated with all material decisions?
  - Will be updated after self-review.

- [x] No raw data files were modified?
  - Confirmed. Only `data/processed/analysis_ready.parquet` was created (new derived file). All raw files untouched.

## Key Findings for Phase 3

1. **ILO endogeneity is the dominant concern.** R-squared of 0.989 for services employment predicted by GDP/urbanization/demographics means the DE coefficient is highly sensitive to control specification. This is more consequential than the small-T power limitation.

2. **First-difference correlation reversal.** DE vs services employment goes from +0.98 (levels) to -0.40 (partial, controlling GDP/urban/demo). Phase 3 must present both level and first-difference results side by side with honest interpretation.

3. **Services employment break at 2014 is promising.** The sup-Wald identifying 2014 as the maximum break point (within the smart city pilot window) is the strongest preliminary evidence. But the DE index itself breaks at 2009, not at pilot dates, which complicates the causal narrative.

4. **Power is low.** 35% power at medium effect size means most null results are underpowered, not evidence of absence. Phase 3 must report power alongside all test results.

5. **ARDL should be elevated to co-primary method** given ambiguous stationarity of DE index and demographic variables.

## Issues

No Category A or B issues identified. The exploration is complete per protocol requirements.

## Verdict

**PASS** (self-review)
