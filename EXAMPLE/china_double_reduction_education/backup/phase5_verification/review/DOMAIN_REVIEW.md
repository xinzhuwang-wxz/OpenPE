# Domain Review

## Summary
- **Artifact reviewed**: `phase5_verification/exec/VERIFICATION.md`
- **Cross-referenced**: `phase3_analysis/exec/ANALYSIS.md`, `phase4_projection/exec/PROJECTION.md`
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 2
- **Category B issues**: 4
- **Category C issues**: 3

## First Principles Assessment

The causal DAG is reasonable for this domain. The identification of COVID-19, demographic decline, and underground market displacement as confounders/competing mechanisms reflects the established literature on education policy evaluation in China. The downscoping from chain-level to edge-level assessment is well-justified given the Joint EP values. The analysis correctly identifies that the NBS proxy variable is the binding constraint on causal identification.

One structural concern: the DAG treats "Policy -> Aggregate Spending" as a direct edge alongside the mediated chain (Policy -> Industry -> Tutoring -> Total). The verification does not interrogate whether this direct edge is conceptually coherent or whether it is simply a reduced-form shortcut that absorbs all unmeasured mediation. This matters because the EP of 0.20 on the direct edge carries forward to projection, but the direct edge has no theoretical mechanism -- it is purely empirical.

## Data Source Validity Assessment

The data provenance audit is mechanically sound: 13/13 hash matches, 5 spot-checks pass. However, the verification has a significant blind spot on data validity that goes beyond hash matching.

The entire analysis rests on NBS annual aggregate data with 9 usable observations. The verification confirms the numbers are transcribed correctly but does not interrogate whether NBS methodology changed during the period. NBS revised its consumption survey methodology in 2013 and has made incremental changes since. The back-calculated 2016-2018 data (acknowledged in ANALYSIS.md warning 7) introduces unknown error structure that the verification accepts at face value. The verifier notes the +/-2-3% error but does not test sensitivity to systematic bias in the back-calculated years (e.g., what if all three back-calculated years are biased upward by 3%, inflating the pre-trend).

Source URL verification was skipped entirely. The justification ("NBS URLs point to general press release pages") is factually correct but insufficient -- spot-checking even 2-3 values against the original NBS Statistical Yearbook or press releases would strengthen provenance. This is classified as a FLAG scenario under the Phase 5 protocol, yet the verification reports PASS.

## Methodology Assessment

The independent reproduction using numpy OLS is genuinely independent from the statsmodels-based primary analysis. Exact reproduction (0.00% difference) is expected and confirmed -- this is a deterministic linear algebra operation on identical input data, so exact agreement is a necessary condition, not a sufficient validation of the methodology.

The verification does not attempt to reproduce the result using a genuinely different methodology. For example, a Bayesian structural time series model (which was originally planned but fell back to OLS) would provide meaningful independent corroboration. The ANALYSIS.md itself notes this limitation (the A2 note on method agreement). The verification acknowledges this but does not flag it as a gap.

The signal injection review is incomplete. The verification reports the Phase 3 signal injection results but did not independently re-run them. The stated reason ("would require reimplementing the synthetic data generation and bootstrap") is an explanation, not a justification. Signal injection is one of the most important verification checks for model specification, and accepting reported results without independent confirmation weakens the verification.

## Systematic Uncertainty Assessment

The uncertainty decomposition is arithmetically verified and internally consistent. The dominance of systematic uncertainty (80%) is correctly identified as the binding constraint. The COVID handling specification contributing 61% of variance is the key finding and is well-documented.

However, the verification does not stress-test the uncertainty decomposition itself. The quadrature combination assumes uncorrelated systematics, but COVID handling and intervention date specification are clearly correlated (both relate to the timing of the structural break in 2020-2021). If these two sources are positively correlated (which they are -- moving the intervention date to 2022 partially absorbs COVID dynamics), the total systematic uncertainty could be either larger or smaller than the quadrature estimate. The verification should have checked whether treating COVID handling and intervention date as correlated changes the total uncertainty materially.

The decision to exclude the per-birth normalization result from the quadrature sum is defensible (it questions existence, not magnitude), but the verification does not probe whether this framing is the only reasonable one. An alternative framing would treat demographic decline as a systematic uncertainty on the level shift itself (range: 0 to -483 yuan), which would dramatically increase the total uncertainty and push the significance well below 1 sigma. The verification accepts the ANALYSIS.md framing without testing the alternative.

## Verification Assessment

The verification executes 6 of 8 programs. Programs 3, 4, and 5 are marked N/A or PARTIAL. While the justifications are individually reasonable, the cumulative effect is that three categories of verification are either skipped or incomplete:

1. **Baseline validation (Program 3)**: Marked N/A because "no separate control regions exist." This is true for a standard ITS, but the urban-rural comparison could serve as a quasi-control validation. Rural areas had much lower tutoring exposure and could provide a partial baseline check for the urban series.

2. **Auxiliary distributions (Program 4)**: Marked N/A. The justification that Phase 2 exploration "already serves the function" conflates exploration with verification. An independent check of the income-spending correlation stability (pre vs. post), or the CPI deflator sensitivity, would be non-trivial auxiliary verifications.

3. **Signal injection (Program 5)**: Marked PARTIAL. Results reviewed from primary analysis output, not independently reproduced. This is the weakest point of the verification.

## EP and Causal Claim Assessment

EP values are arithmetically verified and internally consistent across phases. The CORRELATION classification for the primary edge is well-justified. The EP decay schedule (squaring the standard multiplier for CORRELATION edges) is correctly applied.

Two concerns:

First, the EP for "Income -> Differential Access" increased from 0.30 (Phase 1) to 0.42 (Phase 3) despite parallel trends being violated. The verification passes this without comment. In standard causal inference, a parallel trends violation for a DiD-like comparison should decrease rather than increase the EP, because it undermines the identification strategy. The ANALYSIS.md justifies the increase based on the urban-rural gap being "consistent with exposure," but consistency with exposure is not the same as causal identification. The verification should have flagged this as at least a Category B concern.

Second, the useful projection horizon was revised from 2032 to 2029 in PROJECTION.md v2, but VERIFICATION.md still references 2032 in the human decision options table (Option c references "Return to Phase 0 Step 0.4" without noting the shortened useful horizon). The verification should explicitly confirm the 2029 horizon.

## Result Plausibility

The results are plausible for the domain. A 23.7% decline in the NBS proxy category is large but falls within the range observed in other post-COVID spending categories in China. The finding that per-birth normalization eliminates the signal is the most important result and is directionally consistent with China's dramatic fertility decline (47% drop in births from 2016 to 2024).

The compositional ceiling argument (24% decline vs. 12% maximum tutoring share) is internally consistent and provides useful independent evidence. The 2025 recovery to 11.8% education share (exceeding pre-policy 11.7%) is a strong empirical signal that the aggregate dip was temporary and not policy-driven.

The projection results are reasonable: the three scenarios produce distinguishable but overlapping trajectories, with demographic decline dominating. The sensitivity ranking (demographics first, income second, policy fourth) is consistent with domain knowledge about the relative magnitudes of these forces.

## Issues by Category

### Category A (Blocking)

1. **[A1]: Source URL verification entirely skipped, reported as PASS instead of FLAG.**
   - Domain impact: The Phase 5 protocol explicitly states that incomplete verification should be flagged, not passed. Reporting PASS for data provenance when URL verification was not performed violates the verification protocol. While the hash matches provide integrity assurance, they do not confirm the data actually originated from the claimed NBS sources.
   - Required action: Either perform spot-check URL verification for at least 3 datasets (checking 2-3 values against published NBS Statistical Yearbooks or press releases), or change the Program 2 status from PASS to FLAG and document it as an incomplete check.

2. **[A2]: Signal injection not independently reproduced, yet verification claims "6/8 programs passed."**
   - Domain impact: Signal injection is the primary check for model mis-specification. Reviewing reported results is not the same as independent verification. The verification summary claims "6/8 programs passed" and "Programs 3, 4, 5 not applicable," but Program 5 is marked PARTIAL, not N/A. The summary is misleading -- it should state "5 passed, 1 partial, 2 N/A" or similar.
   - Required action: Either independently reproduce the signal injection tests (the stated reason for not doing so -- reimplementing bootstrap -- is a tractable task for a verification agent) or accurately characterize the verification as PARTIAL and adjust the overall assessment accordingly.

### Category B (Important)

1. **[B1]: Correlation between COVID handling and intervention date systematics not tested.**
   - Domain impact: These two sources contribute 61% + 11% = 72% of the total variance. If they are positively correlated (likely), the quadrature combination may understate or overstate total uncertainty. The verification verifies the arithmetic of the quadrature but not its validity.
   - Suggested action: Compute the total systematic uncertainty under the assumption that COVID handling and intervention date are 50% correlated. Report whether this changes the total uncertainty by more than 10%.

2. **[B2]: EP increase for "Income -> Differential Access" (0.30 to 0.42) not scrutinized despite parallel trends violation.**
   - Domain impact: In causal inference, parallel trends violation should weaken, not strengthen, a differential exposure argument. The verification logic audit passes this edge without comment, despite the ANALYSIS.md itself caveating that "the urban-rural differential may reflect pre-existing divergence rather than differential policy exposure."
   - Suggested action: Flag this EP increase as requiring explicit justification. The edge should either remain at 0.30 (Phase 1 value) or the justification for the increase should explicitly address why the parallel trends violation does not undermine the relevance assessment.

3. **[B3]: Urban-rural comparison not used for baseline validation.**
   - Domain impact: The verification marks baseline validation as N/A, missing an opportunity to use the rural series (with much lower tutoring exposure) as a partial control for the urban series. If the urban-rural gap is consistent with differential policy exposure, then the rural trajectory provides partial baseline validation for the urban counterfactual. If it is not (which is the case -- parallel trends are violated), that itself is informative.
   - Suggested action: Add a brief baseline validation check comparing rural trajectory to the urban counterfactual, even if the conclusion is that parallel trends violation prevents meaningful comparison.

4. **[B4]: Verification does not test the alternative framing of demographic decline as a systematic uncertainty.**
   - Domain impact: The ANALYSIS.md frames per-birth normalization as a separate interpretation rather than a systematic uncertainty source. This is a defensible choice, but the verification should test both framings. If demographic decline is treated as a systematic (range 0 to -483 yuan on the level shift), the effect significance drops well below 1 sigma, and the classification could shift from CORRELATION toward HYPOTHESIZED.
   - Suggested action: Compute the total uncertainty under the alternative framing (demographic decline as a systematic) and report whether the CORRELATION classification remains justified.

### Category C (Minor)

1. **[C1]: PROJECTION.md useful horizon (2029) vs. VERIFICATION.md reference to 2032.**
   - The projection was revised from 2032 to 2029, but the verification does not explicitly confirm or validate the revised horizon. The verification should state which horizon it considers valid.
   - Suggested action: Add a sentence in Program 8 confirming the 2029 useful horizon from PROJECTION.md v2.

2. **[C2]: "Programs executed: 6/8" count is confusing.**
   - Programs 3 and 4 are N/A, Program 5 is PARTIAL. The header says "6/8 executed" but then says "Programs 3, 4, 5 not applicable." Program 5 is not "not applicable" -- it was partially executed. The counting is inconsistent.
   - Suggested action: Revise to "5/8 fully executed, 1/8 partial, 2/8 not applicable" or similar.

3. **[C3]: Row count discrepancies in registry.yaml.**
   - Already noted in VERIFICATION.md. Agree this is minor bookkeeping.
   - Suggested action: As recommended in VERIFICATION.md.

## Acceptance Readiness

The APPROVE recommendation is **premature** given the two Category A issues. The verification is thorough in what it covers but has structural blind spots that undermine its claim of comprehensive validation:

1. The data provenance audit is incomplete (no URL verification) yet reported as PASS.
2. Signal injection is not independently reproduced yet counted as a passed program.
3. The uncertainty framework is arithmetically verified but not stress-tested for correlation between dominant systematics or alternative framings of demographic decline.

The underlying analysis (Phase 3) and projection (Phase 4) are of high quality -- the honesty about limitations, the correct CORRELATION classification, and the extensive sensitivity analysis are commendable. The problem is that the verification does not sufficiently challenge these artifacts. A verification that confirms everything and finds zero Category A or B issues for an analysis this limited in data should itself be scrutinized.

I would accept this analysis after: (a) resolving the two Category A issues (URL spot-checks or honest FLAG status; signal injection reproduction or accurate PARTIAL characterization), and (b) addressing the EP increase for Income -> Differential Access [B2], which is the most substantive domain concern.
