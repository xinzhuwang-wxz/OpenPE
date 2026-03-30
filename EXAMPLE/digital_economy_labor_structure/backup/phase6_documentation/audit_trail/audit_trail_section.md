# Audit Trail

This audit trail documents the complete provenance chain for the analysis "Does the Digital Economy Drive Labor Force Structural Change in China?" Every factual claim, analytical choice, data source, and verification result is traceable to its origin. Machine-readable records are in `claims.yaml`, `methodology.yaml`, `provenance.yaml`, and `verification.yaml`.

## Data Provenance

All raw data resides in `phase0_discovery/data/raw/` with SHA-256 hashes recorded at acquisition time. Seven datasets were successfully acquired; four acquisition attempts failed.

The primary analysis dataset is a merged national panel (24 rows by 40 columns, 2000--2023), combining World Bank development indicators, ILO modeled employment estimates, and a constructed digital economy composite index. All seven acquired datasets passed Phase 5 integrity verification: SHA-256 hashes match, row counts match, and spot-checked values fall within expected tolerances.

Three critical data gaps constrain the analysis. First, no city-level outcome data was acquired (EPS requires commercial subscription; PKU-DFIIC requires academic registration), making the planned DID analysis impossible. Second, ILO skill-composition columns are 96% missing (1 of 24 years), eliminating skill-level analysis. Third, the digital economy composite index is a 4-component proxy (internet users, mobile subscriptions, broadband, R&D expenditure) that saturated at its ceiling of 1.0 by 2023, limiting its construct validity and projection capacity.

## Methodology Choices

Eighteen non-trivial analytical decisions are documented in `methodology.yaml`. The five most consequential are:

**Toda-Yamamoto over standard Granger (M4).** The T=24 sample violates the conventions minimum of T>=30 for standard Granger causality. The Toda-Yamamoto (1995) procedure fits a VAR(p+d_max) in levels and is valid for T~20 per original simulations. Bootstrap critical values (Hacker and Hatemi-J 2006) provide additional small-sample correction.

**Structural break analysis over DID (M6).** Without city-level outcome data, the planned DID design could not be executed. The structural break analysis uses smart city pilot announcement dates (2013--2015) as known break points in the national time series. This is a pre/post comparison without a control group -- weaker identification than DID but the strongest available given data constraints.

**VAR mediation over Baron-Kenny (M7).** Baron-Kenny mediation requires i.i.d. observations, which time series data violates. VAR-based impulse response decomposition is the standard macro-labor equivalent, though at T=24 with 3 endogenous variables, the estimates are fragile.

**National time series after DID proved infeasible (M2).** The analysis was downscoped from the requested city-level DID to national time series when EPS, PKU-DFIIC, and NBS provincial data all proved inaccessible. This is the single largest constraint on the analysis and is carried as a prominent warning through all phases.

**Digital economy proxy index (M3).** The PKU-DFIIC (the standard measure in Chinese digital economy research) was unavailable. The constructed proxy uses four World Bank indicators with min-max normalization and equal weighting. Phase 5 verified the construction is arithmetically correct, but the construct validity concern remains: the index measures ICT infrastructure penetration, not the broader digital economy.

## Causal Claims and Classifications

Thirty-four factual claims are registered in `claims.yaml`, each mapped to its data source and verification status. The five causal edges tested in Phase 3 received the following classifications:

| Edge | Classification | EP | Refutation | Key finding |
|:-----|:---------------|:--:|:-----------|:------------|
| DE to Industry Emp (SUB) | CORRELATION | 0.315 | 2/3 PASS | Positive (complement) sign contradicts substitution hypothesis |
| DE to Services Emp (CRE) | HYPOTHESIZED | 0.030 | 1/3 PASS | No Granger signal; no cointegration; effect near zero |
| DE to Services VA (IND_UP) | HYPOTHESIZED | 0.090 | 1/3 PASS | Significant with controls but fragile under refutation |
| DEMO to Labor Structure | HYPOTHESIZED | 0.120 | 1/3 PASS | Demographics operate at decadal frequency; annual test underpowered |
| DE to LS (direct) | HYPOTHESIZED | 0.010 | N/A | Below soft truncation; lightweight assessment only |

Only DE to SUB (EP=0.315) survives above soft truncation. All other mechanism channels fall below the thresholds at which the framework assigns meaningful explanatory power.

## Verification Results

Phase 5 verification produced an overall FLAG verdict (no Category A findings, 1 Category B, 2 Category C).

**Independent reproduction (PASS).** The primary finding (ARDL long-run coefficient of +7.15 pp, Johansen trace statistic of 19.04, counterfactual deviation of -4.45 pp) was reproduced exactly by independently written code. Two Granger W-statistics showed 6--14% differences attributable to Wald test formulation choices. The ARDL bounds F-statistic diverged (6.51 vs. 1.40) due to specification differences, but cointegration was independently confirmed by Johansen.

**Data provenance (PASS).** All seven acquired datasets have matching SHA-256 hashes. Spot-checked values fall within expected tolerances. Source URLs could not be re-verified without re-running acquisition (flagged as PARTIAL for URL verification).

**Logic audit (FLAG).** All five edge classifications are mechanically correct per the refutation-based decision tree. The final DAG is valid (acyclic, all edges accounted for). One Category B finding: the industry employment pre-trend R2 was reported as 0.96 but independently verified as 0.82. The slope and deviation values are unaffected.

**EP verification (PASS).** Four of five edges have exactly matching EP values. One Category C discrepancy: DE to IND_UP reported EP=0.090 (truth=0.30) where strict rule application yields 0.075 (truth=0.25). The difference has no downstream impact as both values fall below soft truncation.

**Conventions compliance.** All applicable conventions from `causal_inference.md` and `time_series.md` are implemented. One documented deviation: T=24 violates the T>=30 Granger convention, mitigated by Toda-Yamamoto procedure and bootstrap critical values.

## Warnings Carried Forward

Ten warnings from upstream phases are carried into the final documentation:

1. DID not executable (no city-level outcome data).
2. Skill-level analysis impossible (ILO education columns 96% missing).
3. DE composite index is a proxy of uncertain validity (saturated at 1.0 by 2023).
4. T=24 limits statistical power to approximately 35--43% for medium effects.
5. ILO employment estimates are partially endogenous to GDP and urbanization.
6. No individual-level mechanism testing without CFPS microdata.
7. No cross-sectional variation in national time series.
8. Structural break confounding from concurrent events (leadership transition, supply-side reform, anti-corruption).
9. VAR ordering sensitivity for mediation decomposition.
10. DE index structural break at 2009, not at smart city pilot dates.

## Human Gate Decision

Phase 5 verification was presented to the human decision-maker. Decision: Approve (option a) with instruction to correct the R2 value in ANALYSIS.md Table 2.1. The analysis proceeded to Phase 6 documentation.

## Reproducibility

The audit trail can be regenerated from upstream artifacts using `phase6_documentation/scripts/generate_audit.py`. This script reads `ANALYSIS_NOTE.md`, `VERIFICATION.md`, and `registry.yaml` to produce the four YAML files in `audit_trail/`.
