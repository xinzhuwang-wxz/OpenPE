# Logic Review: Phase 1 Strategy

## Review Summary
- **Phase**: Phase 1 (Strategy)
- **Artifact reviewed**: `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase1_strategy/exec/STRATEGY.md`
- **Upstream artifact**: `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase0_discovery/exec/DISCOVERY.md`
- **Date**: 2026-03-29
- **Verdict**: ITERATE
- **Category A issues**: 2
- **Category B issues**: 5
- **Category C issues**: 3

---

## Conventions Compliance

| Convention | Source | Compliance | Notes |
|---|---|---|---|
| Construct DAG before estimation | `causal_inference.md` | PASS | DAGs constructed in Phase 0, refined in Phase 1 Section 6 |
| Every causal claim survives >=3 refutation tests | `causal_inference.md` | PASS (planned) | Time series adapted refutation battery described in Section 2.2, conventions table |
| Report effect sizes with CI | `causal_inference.md` | PASS (planned) | Bootstrap 95% CI specified throughout |
| Document untestable assumptions | `causal_inference.md` | PASS | Listed in conventions table row 4 and Section 8 risk assessment |
| Use DoWhy CausalTest pipeline | `causal_inference.md` | N/A (justified) | Time series data incompatible with DoWhy; manual equivalents planned; justification provided |
| Refutation-based classification | `causal_inference.md` | PASS (planned) | DATA_SUPPORTED / CORRELATION / HYPOTHESIZED labels will be assigned post-refutation |
| Test stationarity (ADF, KPSS) | `time_series.md` | PASS (planned) | Joint ADF+KPSS protocol specified in Section 7.2 |
| Report ACF/PACF | `time_series.md` | PASS (planned) | Listed as Phase 2 deliverable |
| ARIMA/cointegration/VAR model selection | `time_series.md` | PASS | Cointegration + VECM for I(1), first-difference VAR as fallback |
| Granger causality requires T>=30 | `time_series.md` | DEVIATE (documented) | T=24; Toda-Yamamoto and bootstrap alternatives specified; deviation explicitly documented |
| Report prediction intervals | `time_series.md` | PASS (planned) | Bootstrap prediction intervals specified |
| Out-of-sample validation | `time_series.md` | PASS with caveat | Train 2000-2019, test 2020-2023; COVID structural break in test period acknowledged |
| Spurious regression warning | `time_series.md` | PASS | Cointegration testing as guard; risk identified as HIGH in Section 8.1 |
| Panel: FE default | `panel_analysis.md` | N/A | Single-entity time series, not panel |
| Panel: Hausman test | `panel_analysis.md` | N/A | Not panel data |
| Panel: Cluster standard errors | `panel_analysis.md` | N/A | HAC (Newey-West) used instead for autocorrelation |
| Panel: Report balance | `panel_analysis.md` | N/A | Not panel data |
| At least 2 methods per primary edge | Phase 1 CLAUDE.md | PASS | Each primary edge has primary + secondary method in Section 2.2 |
| Data quality warnings propagate | Phase 1 CLAUDE.md | PASS | Section 5.4 maps all 7 DATA_QUALITY.md warnings |
| Truncation decisions documented | Phase 1 CLAUDE.md | PASS | Section 4.1 and 4.2 document all classifications |
| Reference analyses (2-3 required) | CLAUDE.md | PASS | Three reference analyses in Section "Reference Analysis Survey" |

**Summary**: No convention violations detected. The T>=30 deviation is properly documented with appropriate mitigations.

---

## EP Propagation Audit

### Chain structure validity

The Phase 1 DAG (Section 6.1) is acyclic. Seven nodes, nine edges, no cycles. The consolidation from three Phase 0 DAGs (36 edges) to a single testable DAG (9 edges) is well-motivated by data constraints.

### EP calculation correctness -- edge-level

Audit of the Phase 1 EP table (Section 3.2):

| Edge | Claimed truth | Verified truth | Claimed EP | Verified EP | Status |
|---|---|---|---|---|---|
| DE --> LS | 0.15 | 0.30 - 0.05 - 0.10 = 0.15 | 0.06 | 0.15 x 0.4 = 0.06 | CORRECT |
| DE --> SUB | 0.45 | 0.70 - 0.10 - 0.10 - 0.05 = 0.45 | 0.32 | 0.45 x 0.7 = 0.315 ~= 0.32 | CORRECT (rounding) |
| DE --> CRE | 0.45 | 0.70 - 0.10 - 0.10 - 0.05 = 0.45 | 0.27 | 0.45 x 0.6 = 0.27 | CORRECT |
| DE --> IND_UP | 0.45 | 0.70 - 0.10 - 0.10 - 0.05 = 0.45 | 0.23 | 0.45 x 0.5 = 0.225 ~= 0.23 | CORRECT (rounding) |
| IND_UP --> TERT_EMP | 0.60 | 0.70 - 0.10 = 0.60 | 0.30 | 0.60 x 0.5 = 0.30 | CORRECT |
| TERT_EMP --> LS | 0.60 | 0.70 - 0.10 = 0.60 | 0.30 | 0.60 x 0.5 = 0.30 | CORRECT |
| DEMO --> DE | 0.60 | 0.70 - 0.10 = 0.60 | 0.30 | 0.60 x 0.5 = 0.30 | CORRECT |
| DEMO --> LS | 0.60 | 0.70 - 0.10 = 0.60 | 0.36 | 0.60 x 0.6 = 0.36 | CORRECT |

All edge-level EP calculations are arithmetically correct.

### EP calculation correctness -- Joint_EP chains

| Chain | Claimed computation | Verified | Status |
|---|---|---|---|
| DE --> LS (direct) | 0.06 | Single edge, Joint_EP = EP = 0.06 | CORRECT |
| DE --> SUB | 0.32 | Single edge, Joint_EP = EP = 0.32 | CORRECT |
| DE --> CRE | 0.27 | Single edge, Joint_EP = EP = 0.27 | CORRECT |
| DE --> IND_UP --> TERT_EMP --> LS | 0.23 x 0.30 x 0.30 = 0.021 | 0.23 x 0.30 x 0.30 = 0.0207 | CORRECT |
| DE --> IND_UP | 0.23 | Single edge | CORRECT |
| DEMO --> LS | 0.36 | Single edge | CORRECT |

All Joint_EP calculations verified.

### Truncation logic

| Chain | Joint_EP | Claimed classification | Threshold check | Status |
|---|---|---|---|---|
| DE --> LS | 0.06 | Below soft truncation | 0.05 < 0.06 < 0.15 -- between hard and soft | **SEE ISSUE A1** |
| DE --> SUB | 0.32 | Full analysis | 0.32 >= 0.30 | CORRECT |
| DE --> CRE | 0.27 | Lightweight-to-moderate | 0.15 <= 0.27 < 0.30 | CORRECT |
| DE --> IND_UP --> TERT_EMP --> LS | 0.021 | Below hard truncation | 0.021 < 0.05 | CORRECT |
| DEMO --> LS | 0.36 | Full analysis | 0.36 >= 0.30 | CORRECT |

### Summary statement inconsistency (Issue A1)

The STRATEGY.md Summary (line 5) states: "All mechanism-level Joint_EP values fall below hard truncation (0.05); the direct DE-->LS path (EP=0.12) and the IND_UP mediation chain (Joint_EP=0.043) receive lightweight assessment."

This conflicts with Section 3.3, which shows:
- DE --> SUB has Joint_EP = 0.32 (above sub-chain expansion threshold)
- DE --> CRE has Joint_EP = 0.27 (above soft truncation)

These are mechanism-level Joint_EP values that are well above hard truncation. The Summary appears to conflate the Phase 0 DISCOVERY.md Joint_EP values (which were computed from multi-link chains through the original DAGs) with the Phase 1 single-edge EP values. Moreover, the Summary cites "EP=0.12" for the direct DE-->LS path, but the Phase 1 EP table gives EP=0.06. The value 0.12 is the Phase 0 data-adjusted EP, not the Phase 1 value. Similarly, the Summary cites "Joint_EP=0.043" for IND_UP mediation, which matches the Phase 0 DISCOVERY.md computation but the Phase 1 computation yields 0.021.

This is a blocking issue because the Summary is the first thing downstream agents read and it provides incorrect EP values and incorrect truncation classifications.

### DE --> LS classification

The direct DE --> LS path has Joint_EP = 0.06. The strategy classifies this as "Below soft truncation (0.15). Lightweight assessment." This is correct procedurally (0.06 < 0.15). However, the chain planning table (Section 4.1) further states this receives "Single method (Granger). Labeled as HYPOTHESIZED regardless of statistical significance." Pre-labeling an edge as HYPOTHESIZED before refutation testing is defensible given the extremely low EP, but it should be noted that this is a prior judgment, not a post-refutation classification. This is not blocking but should be clarified.

### Decay propagation via reduced-form workaround

Section 3.3's "Critical observation" proposes testing the mediation chain as two reduced-form relationships rather than the full three-link chain. This is a reasonable analytical decision. However, the document does not state what label the mediation finding will receive given that the full chain is below hard truncation. If the full chain is "beyond analytical horizon," the individual links being tested as reduced-form should carry a prominent caveat that the full mediation claim remains below hard truncation. This is addressed partially in Section 4.1 where IND_UP mediation is classified as "Lightweight."

---

## Causal Claim Consistency

### Refutation alignment

No causal claims are made yet (Phase 1 is strategy). Planned refutation battery is appropriate: placebo treatment timing, random common cause (permutation), data subset stability (rolling window). These are reasonable time series adaptations of the standard DoWhy refutations.

### Label consistency

Phase 0 labels (LITERATURE_SUPPORTED, THEORIZED, SPECULATIVE) are properly carried forward. Phase 1 adds method credibility adjustments to truth values. The transition from Phase 0 labels to Phase 1 EP values is traceable.

### DAG-claim consistency

The Phase 1 DAG (Section 6.1) is consistent with the chain planning (Section 4.1) and method selection (Section 2.2). Every edge in the Phase 1 DAG has a corresponding entry in the EP table and method assignment.

### Circular reasoning check

No circular dependencies detected. The DE --> IND_UP --> CRE_PROXY path is unidirectional. The DEMO confounder arrows are correctly shown as dashed (non-causal control).

### Evidence sufficiency

The strategy is appropriately conservative. The highest single-edge EP is 0.36 (DEMO --> LS), and the highest mechanism-chain EP is 0.32 (DE --> SUB). The document is honest that T=24 limits statistical power and that the DE index has construct validity concerns.

---

## Reference Analysis Comparison

The strategy identifies three reference analyses. Comparison against what a competing group would have:

1. **Provincial panel data**: All three references use provincial or city-level panels (N=30 provinces or N=280 cities). This analysis has T=24 national time series only. A competing group with NBS provincial data would have 30x13=390 observations and could run two-way FE, the standard in the field. **Gap identified** -- see B3.

2. **Validated digital economy index**: References use PKU-DFIIC or entropy-weighted TOPSIS indices. This analysis uses a 4-component WB proxy. A competing group would use PKU-DFIIC. **Gap acknowledged in document** as construct validity systematic.

3. **Endogeneity handling**: References use system GMM for dynamic panel endogeneity. This analysis cannot use GMM with T=24 national series. **Gap inherent in data constraint, properly documented.**

4. **Nonlinearity testing**: Reference 3 (Zhao & Li 2022) finds an inverted-U relationship. The strategy does not plan for nonlinearity testing. **Gap identified** -- see B4.

5. **Spatial effects**: Reference 2 uses spatial Durbin model. Not applicable to single national series. **N/A.**

---

## Issues

### Category A (Blocking)

**[A1]: Summary section contains incorrect EP values and incorrect truncation claims that conflict with the body of the document.**

- Location: `phase1_strategy/exec/STRATEGY.md`, line 5 (Summary paragraph)
- The Summary states "All mechanism-level Joint_EP values fall below hard truncation (0.05)" but Section 3.3 shows DE-->SUB at 0.32 and DE-->CRE at 0.27, both above hard truncation.
- The Summary cites "EP=0.12" for DE-->LS but the Phase 1 EP is 0.06 (Section 3.2).
- The Summary cites "Joint_EP=0.043" for IND_UP mediation but the Phase 1 value is 0.021 (Section 3.3).
- Impact: Downstream agents (Phase 2 executor, Phase 3 analyst) read the Summary first. Incorrect EP values here will propagate wrong truncation decisions and resource allocation throughout the analysis. This is exactly the kind of EP propagation error that compounds downstream.
- Suggested fix: Rewrite the Summary to match Section 3.3 values. State that DE-->SUB (Joint_EP=0.32) receives full analysis, DE-->CRE (0.27) receives moderate treatment, DE-->IND_UP-->TERT_EMP-->LS (0.021) is below hard truncation, and DE-->LS direct (0.06) is below soft truncation. Use Phase 1 EP values, not Phase 0 values.

**[A2]: The DE --> LS edge truth derivation uses an incorrect starting value of 0.30, not the Phase 0 LITERATURE_SUPPORTED default of 0.70.**

- Location: `phase1_strategy/exec/STRATEGY.md`, Section 3.2, first row of the EP table
- The truth computation shows: "truth: 0.30 - 0.05 (method) - 0.10 (construct) = 0.15"
- Starting from 0.30 implies the DE-->LS direct edge was already capped at 0.30 by data quality. However, examining Phase 0 DISCOVERY.md DAG 2 edge table, the DE-->LS (direct) edge is listed as THEORIZED with truth=0.3, relevance=0.4, EP=0.12. So the Phase 0 truth was already 0.3 (THEORIZED level), not the LITERATURE_SUPPORTED 0.7.
- In Section 3.1, the rules state "truth reduction by 0.1 for all edges using this data" (MEDIUM quality), and "-0.10 construct validity penalty." Applying these to a THEORIZED base of 0.3: 0.3 - 0.10 (data) - 0.10 (construct) - 0.05 (method) = 0.05, which would give EP = 0.05 x 0.4 = 0.02, not 0.06.
- Alternatively, if the data quality reduction does not apply because the THEORIZED value of 0.3 is already low, this needs to be stated explicitly. The current presentation applies data and construct penalties to some edges starting from 0.70 (LITERATURE_SUPPORTED) but starts DE-->LS from 0.30 without applying the same data quality reduction. The rules in Section 3.1 say "truth reduction by 0.1 for all edges using this data" -- this should include DE-->LS.
- Impact: The DE-->LS EP could be 0.02 (below hard truncation at 0.05) rather than 0.06. This changes whether it receives even lightweight assessment or is classified as "beyond analytical horizon."
- Suggested fix: Clarify the truth derivation for DE-->LS. If the Phase 0 THEORIZED truth of 0.3 is the starting point, apply the same adjustment rules consistently: 0.3 - 0.10 (data) - 0.10 (construct) - 0.05 (method) = 0.05, EP = 0.02. If a floor is applied to prevent negative/near-zero values, state the floor rule explicitly. Alternatively, argue that the MEDIUM data quality penalty and construct penalty are already reflected in the THEORIZED label's low truth value (0.3 vs. 0.7), and thus double-penalizing is inappropriate -- but this reasoning must be stated.

### Category B (Important)

**[B1]: Pre-labeling DE-->LS as HYPOTHESIZED before refutation testing.**

- Location: Section 4.1, chain classification table, row "DE --> LS (direct, aggregate)"
- The strategy states this edge is "Labeled as HYPOTHESIZED regardless of statistical significance."
- Per causal inference conventions, the DATA_SUPPORTED / CORRELATION / HYPOTHESIZED classification should follow from refutation test outcomes, not be pre-assigned. Pre-labeling bypasses the refutation protocol.
- Impact: If by some chance the Granger test is highly significant with consistent refutation results, the pre-label would force a classification not supported by the evidence.
- Suggested improvement: Replace with "Expected to be classified as HYPOTHESIZED given low EP; actual classification determined by Phase 3 refutation battery results."

**[B2]: Missing explicit power analysis commitment.**

- Location: Section 8.1, risk table, "Low power" row
- The strategy acknowledges 50% probability of low power but does not commit to computing formal power analysis before running the tests. It mentions "power analysis alongside null results" but this should be done ex ante (Phase 2 or early Phase 3), not ex post.
- Impact: Without ex ante power analysis, null results cannot be properly interpreted. A null result with 40% power is uninformative, but this cannot be assessed after the fact without suspicion of post-hoc rationalization.
- Suggested improvement: Add a Phase 2 deliverable: "Compute statistical power for Toda-Yamamoto Granger test at T=24, for effect sizes calibrated from Reference 1 (coefficient ~0.03-0.05). Report minimum detectable effect size at 80% power."

**[B3]: No data callback strategy for NBS provincial data.**

- Location: Section 11 (Open Issues, item 1) mentions the callback but Section 2 (Method Selection) and Section 4 (Chain Planning) do not integrate it into the decision tree.
- The strategy identifies that provincial panel data (N=31, T=13) would resolve the T=24 limitation, and that 1 of 2 allowed callbacks remains. However, the trigger for this callback is vague: "if Phase 2/3 results are ambiguous."
- Impact: Without a concrete trigger criterion, the callback may never be invoked even when it should be, or may be invoked too late.
- Suggested improvement: Define a specific trigger: "If Milestone M2 (Granger causality) fails for all sectors, invoke data callback for NBS provincial data before proceeding to M3." Integrate into Section 12 milestone table.

**[B4]: No planned nonlinearity test despite Reference 3 finding an inverted-U shape.**

- Location: Section 2 (Method Selection) and Reference Analysis Survey
- Reference 3 (Zhao & Li 2022) documents an inverted-U relationship between digital economy and employment at the industry level. The strategy does not plan any nonlinearity test (threshold regression, quadratic term, or structural break in the slope).
- Impact: If the true relationship is nonlinear, linear Granger/VECM specifications will underestimate or mischaracterize the effect. A competing analysis would test for this.
- Suggested improvement: Add a robustness check in Phase 3: include a quadratic DE term in the VECM or test for threshold effects using a sup-Wald test at the median DE value.

**[B5]: Collider bias in mediation analysis acknowledged but mitigation is insufficient.**

- Location: Section 11 (Open Issues, item 4)
- The document correctly flags that conditioning on IND_UP may open a collider path. The proposed mitigation is "generalized impulse responses (Pesaran & Shin 1998) as robustness check." However, generalized impulse responses address ordering sensitivity, not collider bias. Collider bias arises from DAG structure, not from Cholesky ordering.
- Impact: If a collider path exists (e.g., GOV --> IND_UP <-- DE, with GOV also affecting LS), the mediation estimate will be biased regardless of impulse response method. The mediation share could be inflated or deflated.
- Suggested improvement: (1) Explicitly draw the potential collider path in the DAG and assess whether it is plausible. (2) If plausible, consider the sensitivity analysis approach of VanderWeele (2015) for mediation under potential collider bias, or simply note that the mediation share should be interpreted with caution and label the mediation finding as CORRELATION at best.

### Category C (Minor)

**[C1]: Inconsistent section numbering between the Summary's reference to "Phase 0 Summary" as Section 1 and the conventions compliance section being unnumbered.**

- Location: Sections following the Summary
- The document has "## 1. Phase 0 Summary" but "## Conventions Compliance" and "## Reference Analysis Survey" without numbers, then resumes numbering at "## 2. Method Selection."
- Suggested fix: Number all sections consistently or remove all manual numbering (per the CLAUDE.md instruction that pandoc adds numbering with `--number-sections` and hand-numbering causes double numbering).

**[C2]: The term "lightweight-to-moderate" is used for chain classification but is not defined in the methodology.**

- Location: Section 4.1, chain classification table
- The methodology defines three tiers: full analysis (>=0.30), lightweight (0.15-0.30), beyond horizon (<0.15). "Lightweight-to-moderate" is not a defined tier.
- Suggested fix: Use "lightweight" for 0.15-0.30 chains, consistent with methodology. If a middle tier is desired, define it explicitly.

**[C3]: The mermaid DAG in Section 6.1 uses `style` directives for coloring that may not render in all markdown viewers.**

- Location: Section 6.1, lines 440-447
- Mermaid `style` directives are not universally supported. The colors add visual clarity but may break in some renderers.
- Suggested fix: Verify rendering in the target output format. If pandoc is used for PDF generation, confirm mermaid filter supports style directives.

---

## Figure Review

No figures are produced in Phase 1. The proxy DID figure is specified (Section 2.5) with four panels. The specification is clear and well-structured. No figure review issues.

---

## Distribution Sanity Checks

No distributions or plots to check in Phase 1. The variable quality summary (Domain Context section) provides plausible ranges:
- Employment agriculture: 50.0% to 22.8% (expected declining trend)
- Employment services: 25.3% to 45.8% (expected rising trend)
- Internet users: 1.8% to 90.6% (S-curve adoption, plausible)

These are consistent with known Chinese economic data.

---

## Regression Detection

### Phase 0 to Phase 1 EP changes

All EP values decreased from Phase 0 to Phase 1, which is expected when applying data quality, method credibility, and construct validity penalties. The changes are documented in Section 3.4 with justifications. No unexpected increases detected.

### Structural consistency

- Phase 0 identified 3 competing DAGs; Phase 1 consolidated to 1 testable DAG. This is a planned downscoping, not a regression.
- Phase 0 identified T=24 as a conventions violation; Phase 1 provides mitigations (Toda-Yamamoto, bootstrap). Consistent.
- Phase 0 identified demographic transition as mandatory confounder; Phase 1 includes it in all specifications. Consistent.
- Phase 0 DISCOVERY.md Summary section identifies the mediation chain Joint_EP as 0.043; the Phase 1 Summary cites 0.043 but the Phase 1 EP table yields 0.021. This is the regression caught in A1 -- the Summary was not updated to reflect Phase 1 EP revisions.

---

## Upstream Feedback

**To Phase 0 (DISCOVERY.md):**

No issues originating in Phase 0 that were not already addressed by the Phase 0 review cycle. The Phase 0 data quality warnings are properly propagated. The DISCOVERY.md Joint_EP values (0.043 for mediation chain, 0.12 for DE-->LS) are Phase 0 values computed before Phase 1 adjustments; Phase 1 should not cite these as current values (this is the root cause of A1).

No upstream fix is required. The current phase work should not pause.

---

## Overall Assessment

The STRATEGY.md is a thorough, well-structured document that honestly grapples with severe data constraints. The method selection is appropriate for T=24 national time series, the EP framework is applied rigorously at the edge level, the reference analysis survey is substantive, and the risk assessment is realistic. The conventions compliance is complete with every applicable convention addressed.

The two blocking issues (A1, A2) are both EP propagation errors -- exactly the type of mistake that compounds if not caught now. A1 is a Summary that quotes stale Phase 0 values instead of updated Phase 1 values. A2 is an inconsistency in truth derivation rules where the DE-->LS edge escapes the data quality and construct validity penalties applied to all other DE-originating edges.

Once A1 and A2 are resolved, and the B-category improvements are incorporated, this strategy provides a solid foundation for Phase 2 exploration and Phase 3 analysis.
