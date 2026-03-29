# Phase 2 Self-Review Notes

**Reviewer:** data-explorer (self-review)
**Date:** 2026-03-29

## Checklist

- [x] Data cleaning log is complete for every dataset?
  - All 12 acquired datasets documented. No cleaning transformations needed beyond CPI deflation.
- [x] All engineered features are documented with formula and source?
  - 11 features documented in feature engineering table with formulas and source dataset IDs.
- [x] Exploratory plots cover all key variables and causal edges?
  - 14 figures covering all required EDA components from the strategy.
- [x] Assumption pre-checks run for every planned method?
  - ADF/KPSS stationarity tests: I(1) confirmed for all spending series.
  - Parallel trends check: VIOLATED for urban-rural comparison.
  - BSTS feasibility: flagged as marginal (4-5 pre-treatment obs).
- [x] Variable ranking reflects DAG structure?
  - 13 variables ranked by DAG role, quality, and EP relevance.
- [x] Data readiness assessment covers every Phase 3 causal edge?
  - 6 edges assessed with readiness, assumption status, and risk level.
- [x] Experiment log updated with all material decisions?
  - 6 decisions and 6 key findings documented.
- [x] No raw data files were modified?
  - Confirmed: all raw files in data/raw/ and processed files in data/processed/ unchanged.

## Issues Identified

### Category C (Suggestions)

1. **Fiscal year misalignment in tutoring financials.** New Oriental and TAL report on fiscal years (ending May/February respectively), not calendar years. The x-axis label "Fiscal year" in fig07 is correct but the reader may conflate FY2022 with calendar 2022. A note in the caption would help.

2. **Per-child figure y-axis units.** The "spending per birth" metric has units of "2015 yuan / million" which is confusing. It would be clearer to show "2015 yuan * 1000 / child" or similar. Not blocking.

3. **Summary statistics table could include pre/post-policy means.** Currently shows full-sample statistics. A split at 2021 would be informative for Phase 3 planning.

## No Category A or B Issues Found

The EDA is complete and consistent with the Phase 1 strategy. All data quality warnings from Phase 0 are carried forward. The parallel trends violation is the most important new finding and is properly handled (method pivot documented).
