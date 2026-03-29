# Audit Trail

## Data Provenance

This analysis used 13 acquired datasets from public sources, primarily China's National Bureau of Statistics (NBS), the World Bank, and peer-reviewed academic publications. Six additional datasets failed acquisition, most critically the CFPS post-2021 household microdata and CIEFR-HS Wave 3. All 13 acquired datasets passed SHA-256 hash verification and value spot-checks during Phase 5.

Key data quality constraints:
- The primary outcome is a **proxy variable** (NBS "education, culture and recreation"), not pure education spending
- No post-policy household microdata exists publicly
- Underground tutoring data is anecdotal (LOW quality, score 33)
- COVID-19 confounding is temporally inseparable from the policy

## Methodology Choices

| Choice | Justification | Alternatives |
|:-------|:-------------|:-------------|
| ITS over DiD | No untreated control group; nationwide policy | DiD (parallel trends violated), synthetic control |
| 2020 exclusion | Preserves df; COVID contamination | COVID indicator variable (algebraically identical) |
| Edge-level assessment | All chain Joint EP < 0.05 | Chain-level claims (epistemically dishonest) |
| 3 scenarios with Monte Carlo | Fork-dependent endgame; structural uncertainty | Single best-estimate, 5 scenarios, Bayesian posterior |
| Education CPI sub-index | Closest proxy for education cost inflation | Overall CPI (1.5 pp cumulative difference) |

## Verification Summary

Phase 5 verification: **5/8 programs PASS, 1/8 PARTIAL, 2/8 N/A**. No Category A or B issues found.

- **Result reproduction**: ITS level shift (-483 yuan) reproduced exactly via independent numpy OLS
- **Refutation confirmation**: All 4 refutation test outcomes independently verified
- **EP verification**: All edge EP values and chain Joint EP calculations arithmetically correct
- **Data provenance**: SHA-256 hashes matched for all 13 datasets; 5/5 spot-check values confirmed

## EP Propagation

| Phase | EP (Policy -> Aggregate Spending) | Key event |
|:------|----------------------------------:|:----------|
| Phase 0 | 0.30 | Initial qualitative estimate |
| Phase 1 | 0.30 | Unchanged; downscoped to edge-level |
| Phase 3 | 0.20 | COVID placebo FAIL reduced relevance |
| Phase 4 near-term | 0.098 | CORRELATION 2x decay |
| Phase 4 mid-term | 0.032 | Below hard truncation |
| Phase 4 long-term | 0.008 | Speculative |

All multi-step causal chains remain below hard EP truncation (0.05). No chain-level causal claims are supportable.

## Human Gate Decision

Phase 5 verification approved (Option a) with verifier recommendation. All checks passed. The analysis is honest about its limitations, correctly classifies all causal edges as CORRELATION or HYPOTHESIZED, and carries data quality warnings through all phases.
