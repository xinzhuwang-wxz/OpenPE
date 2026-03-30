# Logic Review: Phase 6 Documentation

## Review Summary
- **Phase**: Phase 6 (Documentation)
- **Artifacts reviewed**:
  - `phase6_documentation/exec/REPORT.md`
  - `phase6_documentation/exec/ANALYSIS_NOTE.md`
  - `phase6_documentation/audit_trail/` (claims.yaml, methodology.yaml, provenance.yaml, verification.yaml, audit_trail_section.md)
- **Date**: 2026-03-30
- **Verdict**: PASS
- **Category A issues**: 0
- **Category B issues**: 3
- **Category C issues**: 5

---

## Conventions Compliance

### Phase 6 Completion Checklist (Hard Gate)

| Required file | Exists | Status |
|:---|:---:|:---:|
| `exec/ANALYSIS_NOTE.md` | YES | PASS |
| `exec/ANALYSIS_NOTE.pdf` | YES | PASS |
| `exec/REPORT.md` | YES | PASS |
| `exec/REPORT.pdf` | YES | PASS |
| `exec/references.bib` | YES | PASS |
| `exec/figures/` (all referenced figures) | YES | PASS -- 19 PDFs present |
| `audit_trail/claims.yaml` | YES | PASS |
| `audit_trail/methodology.yaml` | YES | PASS |
| `audit_trail/provenance.yaml` | YES | PASS |
| `audit_trail/verification.yaml` | YES | PASS |
| `audit_trail/audit_trail_section.md` | YES | PASS |
| `scripts/generate_audit.py` | YES | PASS |
| `REPORT.pdf` (analysis root) | YES | PASS |

All required Phase 6 deliverables exist.

### Dual-Document Requirement

REPORT.md and ANALYSIS_NOTE.md are distinct documents with different prose styles. REPORT.md uses the Writing Style Guide (analogies, "so what" leads, named scenarios). ANALYSIS_NOTE.md is quantitative and logic-focused. They are not symlinks or copies. PASS.

### Pandoc Compatibility

| Convention | REPORT.md | ANALYSIS_NOTE.md |
|:---|:---:|:---:|
| No hand-numbered headings | PASS | PASS |
| LaTeX math ($...$, $$...$$) | PASS | PASS |
| Pandoc figure syntax | PASS | PASS |
| No raw HTML | PASS | PASS |
| Pipe tables | PASS | PASS |
| pandoc-crossref labels ({#fig:...}, {#tbl:...}) | PASS | PASS |
| Citations ([@key]) | PASS (present) | N/A (no bib in AN) |

### Classification Labels

Every causal finding in both documents carries its DATA_SUPPORTED/CORRELATION/HYPOTHESIZED label. PASS.

### Writing Style Guide (REPORT.md only)

| Guideline | Status |
|:---|:---:|
| Lead with "so what" | PASS -- each section opens with a takeaway sentence |
| No LLM-speak | PASS -- no "It is important to note..." patterns found |
| Concrete numbers | PASS -- numbers throughout with both absolute and relative magnitudes |
| Bold key numbers | PASS -- primary findings bolded appropriately |
| Explain statistical concepts inline | PASS -- parenthetical explanations for Granger causality, refutation tests, etc. |
| Analogies for scale | PASS -- telescope analogy (power), ruler analogy (DE saturation), staircase analogy (spurious correlation) |
| Executive summary standalone | PASS -- contains question, answer, confidence, key caveat |
| Named scenarios | PASS -- "Trend Continuation", "Digital Acceleration", "Digital Stagnation" |
| Causal chain step-by-step | PASS |
| Completeness over brevity | PASS |

---

## EP Propagation Audit

### Chain Structure Validity

The final DAG has five tested edges: DE->SUB, DE->CRE, DE->IND_UP, DEMO->LS, DE->LS. The DAG is acyclic. All edges are accounted for. PASS.

### EP Calculation Correctness

| Edge | Truth | Relevance | Computed EP | Reported EP (AN) | Reported EP (REPORT) | Match |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| DE->SUB | 0.45 | 0.70 | 0.315 | 0.315 | 0.315 | YES |
| DE->CRE | 0.30 | 0.10 | 0.030 | 0.030 | 0.030 | YES |
| DE->IND_UP | 0.30 | 0.30 | 0.090 | 0.090 | 0.090 | YES |
| DEMO->LS | 0.30 | 0.40 | 0.120 | 0.120 | 0.120 | YES |
| DE->LS | 0.05 | 0.20 | 0.010 | 0.010 | 0.010 | YES |

All EP values are consistent across REPORT.md, ANALYSIS_NOTE.md, and ANALYSIS.md (Phase 3). PASS.

**Note on DE->IND_UP truth value**: Phase 5 verification flagged that strict application of the HYPOTHESIZED rule (truth = min(0.3, 0.35 - 0.1) = 0.25) would yield EP = 0.075, not 0.090. The analysis used truth = 0.30 (a floor). This was classified as Category C in Phase 5 because 0.090 is still below soft truncation and has no downstream impact. Both REPORT.md and ANALYSIS_NOTE.md carry the 0.090 value, which is consistent with Phase 3 ANALYSIS.md. This is not a Phase 6 regression; it is a known upstream Category C issue carried forward correctly.

### Decay Propagation

| Distance | Standard Mult. | CORR 2x Mult. | Computed EP | Reported (AN) | Reported (REPORT) | Match |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 yr | 1.00 | 1.00 | 0.315 | 0.315 | 0.315 | YES |
| 1 yr | 0.60 | 0.36 | 0.113 | 0.113 | 0.113 | YES |
| 3 yr | 0.40 | 0.16 | 0.050 | 0.050 | 0.050 | YES |
| 5 yr | 0.25 | 0.063 | 0.020 | 0.020 | 0.020 | YES |
| 10 yr | 0.08 | 0.006 | 0.002 | 0.002 | 0.002 | YES |

EP decay values are correct and consistent across all documents. The "useful projection horizon" of 3 years is consistent with EP reaching hard truncation (0.05) at that distance. PASS.

### Truncation Logic

| Chain | Joint_EP | Decision | Correct? |
|:---|:---:|:---|:---:|
| DE->SUB | 0.315 | Full analysis + projection | YES |
| DE->CRE | 0.030 | Below hard truncation (0.05) | YES |
| DE->IND_UP->CRE | 0.003 | Below hard truncation | YES |
| DEMO->LS | 0.120 | Below soft truncation (0.15) | YES |
| DE->LS | 0.010 | Below hard truncation | YES |

All truncation decisions are logically consistent. PASS.

### Label Consistency

| Edge | Classification | Refutation Score | Label Correct? |
|:---|:---|:---:|:---:|
| DE->SUB | CORRELATION | 2/3 PASS | YES (2/3 = CORRELATION per protocol) |
| DE->CRE | HYPOTHESIZED | 1/3 PASS (biv) / 0/3 (controlled) | YES -- HYPOTHESIZED for the bivariate spec |
| DE->IND_UP | HYPOTHESIZED | 1/3 PASS | YES |
| DEMO->LS | HYPOTHESIZED | 1/3 PASS | YES |

All labels are consistent with refutation outcomes. PASS.

---

## Causal Claim Consistency

### Refutation Alignment

Every causal edge with a classification above HYPOTHESIZED (only DE->SUB at CORRELATION) has its refutation test results documented in detail in both REPORT.md (Section 3, Table: Refutation battery) and ANALYSIS_NOTE.md (Table refutation-sub). The specific tests, results, and failure explanations are present. PASS.

### Label Downgrade Logic

- DE->CRE: Bivariate scores 1/3 (HYPOTHESIZED). Controlled scores 0/3 (DISPUTED). ANALYSIS_NOTE.md correctly reports both but uses HYPOTHESIZED as the overall classification (the more favorable bivariate specification). REPORT.md describes this as "HYPOTHESIZED" and "below hard truncation." This is acceptable since the bivariate is the specification where at least some signal was present.
- DE->IND_UP: Controlled specification scores 1/3 despite a significant Granger p-value (0.008). The downgrade from "potentially CORRELATION" to HYPOTHESIZED is correctly justified by refutation failure. PASS.

### DAG-Claim Consistency

The claims follow from the DAG structure. The positive DE->SUB direction (complement rather than substitution) is honestly reported as contradicting the original hypothesis. No overclaiming of causation is present; the CORRELATION label is appropriately cautious. PASS.

### Circular Reasoning Check

No circular dependencies found. Demographics are confirmed exogenous (DE does not Granger-cause demographics). The analysis does not use outcome variables to define treatment. PASS.

---

## Reference Analysis Comparison

The analysis identifies three reference analyses: Zhu et al. (2023), Li et al. (2024), and Zhao et al. (2022). A competing group publishing a similar analysis would likely have:

1. **Provincial panel data (N=30+).** Li et al. (2024) uses a 30-province panel; Zhu et al. (2023) uses city-level DID with 280+ cities. This analysis uses only national time series (T=24, no cross-section). The limitation is correctly documented and prominent throughout.

2. **A non-saturated DE index.** PKU-DFIIC (digital financial inclusion) or a broader composite. The analysis correctly flags this as the binding constraint on projection and recommends it for future work.

3. **Individual-level mechanism data.** CFPS microdata for skill-level and task-level analysis. Correctly documented as unavailable.

4. **Proper DID identification.** The analysis correctly documents that DID was planned but infeasible. Structural break analysis is an honest substitute but weaker.

These gaps are all documented as limitations. No undisclosed gap was identified. The reference analysis comparison in the REPORT.md (Section 3, mediation channel discussion) explicitly compares against Li et al. (2024) and explains the discrepancy. PASS with the note that these are genuine limitations, not oversights.

---

## Issues

### Category A (Blocking)

None.

### Category B (Important)

1. **[B1]: ANALYSIS_NOTE.md reports DE->CRE classification as "HYPOTHESIZED (bivariate) / DISPUTED (with controls)" but claims.yaml (C3) lists only HYPOTHESIZED with EP=0.030.**
   - Location: `audit_trail/claims.yaml`, claim C3; `exec/ANALYSIS_NOTE.md` line 159
   - Impact: The DISPUTED classification for the controlled specification is lost in the audit trail. A reader tracing claims through claims.yaml would miss that the creation channel with demographic controls is actively contradicted by the data (0/3 refutation PASS).
   - Suggested fix: Add a separate claim entry for the controlled DE->CRE specification with classification DISPUTED, or amend C3 to include both classifications. The audit trail should be at least as precise as the ANALYSIS_NOTE.

2. **[B2]: REPORT.md Executive Summary states "Joint EP for the best-supported chain: 0.315" but does not explicitly state this is the only edge above soft truncation until Section 3.**
   - Location: `exec/REPORT.md` lines 30-31
   - Impact: The Executive Summary is intended to be standalone (per Writing Style Guide point 7). A reader of the Executive Summary alone may not immediately grasp that only one of five edges has meaningful EP. The phrase "Joint EP" also implies a multi-edge chain, but 0.315 is actually a single-edge EP (DE->SUB is not a chain of multiple edges).
   - Suggested improvement: Clarify in the Executive Summary that 0.315 is a single-edge EP (not a chain product) and that all other tested edges fell below soft or hard truncation. For example: "Only one of five tested causal edges produced EP above soft truncation."

3. **[B3]: audit_trail/methodology.yaml contains only 5 entries (M_auto_1 through M_auto_5), but REPORT.md Table tbl:methodology-audit and ANALYSIS_NOTE.md Table tbl:methodology-choices list the same 5 choices. The audit_trail_section.md references "eighteen non-trivial analytical decisions" in methodology.yaml.**
   - Location: `audit_trail/methodology.yaml`; `audit_trail/audit_trail_section.md` line 15
   - Impact: The audit trail narrative claims 18 methodology decisions are documented in methodology.yaml, but only 5 are present. This is an internal inconsistency within the audit trail. The 13 missing decisions may be less consequential (lag selection, bootstrap block size, etc.) but their absence makes the "eighteen" claim unverifiable.
   - Suggested fix: Either populate methodology.yaml with all 18 decisions referenced in the narrative, or correct the audit_trail_section.md count to match the actual number of entries (5).

### Category C (Minor)

1. **[C1]: REPORT.md date in YAML frontmatter is 2026-03-30; ANALYSIS_NOTE.md date is 2026-03-29.**
   - Location: REPORT.md line 4; ANALYSIS_NOTE.md line 4
   - Suggested fix: Align dates. Both should use the same date (the date of final completion).

2. **[C2]: provenance.yaml uses numeric quality scores (75, 58, 85, etc.) without explanation of the scale.**
   - Location: `audit_trail/provenance.yaml`
   - Suggested fix: Add a comment or header explaining the 0-100 quality scale and its interpretation.

3. **[C3]: verification.yaml reproduction_details lists 8 metrics but the summary says "7/10 metrics within 5%."**
   - Location: `audit_trail/verification.yaml` lines 5, 13-50
   - Impact: The reproduction details section contains 8 metrics, not 10. The "7/10" figure comes from VERIFICATION.md which tested 10 metrics (including counterfactual deviation for services and level correlation). The YAML summary is a simplified extract and does not list all 10.
   - Suggested fix: Either expand the YAML to include all 10 reproduced metrics, or annotate that the list is a subset of the full reproduction battery.

4. **[C4]: REPORT.md Section "The 2014 Structural Break" (heading) says 2014, but the text discusses 2013-2015.**
   - Location: `exec/REPORT.md` Section heading at approximately line 184
   - Suggested fix: Rename to "The 2013-2015 Structural Break" for consistency with the text, or "The Mid-2010s Structural Break."

5. **[C5]: ANALYSIS_NOTE.md Table tbl:ep-phase0 uses the label "LITERATURE_SUPPORTED" for Phase 0 EP classifications, but REPORT.md Table tbl:ep-evolution omits Phase 0 classification labels entirely.**
   - Location: `exec/ANALYSIS_NOTE.md` line 50-57; `exec/REPORT.md` lines 67-75
   - Suggested fix: Minor style difference. If desired, add a Phase 0 label column to the REPORT.md EP evolution table for completeness.

---

## Figure Review

Figures are symlinked into `exec/figures/`. All 19 PDFs referenced in both documents exist. Since this is a logic review (not a rendering review), the check focuses on figure references and captions rather than visual rendering.

| Figure | Referenced in REPORT.md | Referenced in AN | File exists | Caption present | Label present |
|:---|:---:|:---:|:---:|:---:|:---:|
| structural_break_did_baseline.pdf | YES | YES | YES | YES | YES (#fig:structural-break) |
| method_comparison_summary.pdf | YES | YES | YES | YES | YES (#fig:method-comparison) |
| var_irf_mediation.pdf | YES | YES | YES | YES | YES (#fig:var-irf) |
| scenario_comparison.pdf | YES | YES | YES | YES | YES (#fig:scenario-comparison) |
| sensitivity_tornado.pdf | YES | YES | YES | YES | YES (#fig:sensitivity-tornado) |
| ep_decay_chart.pdf | YES | YES | YES | YES | YES (#fig:ep-decay) |
| uncertainty_tornado.pdf | YES | YES | YES | YES | YES (#fig:uncertainty-tornado) |
| ep_propagation.pdf | NO | YES | YES | YES | YES (#fig:ep-propagation) |
| refutation_summary.pdf | NO | YES | YES | YES | YES (#fig:refutation-summary) |
| sensitivity_break_year.pdf | NO | YES | YES | YES | YES (#fig:break-year-sensitivity) |

EP propagation and refutation summary figures are in ANALYSIS_NOTE.md but not REPORT.md. This is acceptable since REPORT.md is the stakeholder document and these are technical details. No figures are referenced but missing.

No `ax.set_title()` calls were checked (logic review, not rendering review). Caption quality is appropriate -- captions describe the content and are standalone-interpretable.

---

## Distribution Sanity Checks

Sanity checks are performed against the numbers reported in the documents, cross-referenced with upstream artifacts.

| Claim | REPORT.md | ANALYSIS_NOTE.md | ANALYSIS.md (Phase 3) | PROJECTION.md (Phase 4) | VERIFICATION.md (Phase 5) | Consistent? |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| ARDL LR coeff (biv) | +7.15 pp | +7.15 pp | +7.15 pp | +7.15 pp | +7.15 pp (0.0% diff) | YES |
| ARDL LR coeff (ctrl) | +12.57 pp | +12.57 pp | +12.57 pp | +12.57 pp | N/A | YES |
| 95% CI (biv) | [-0.89, 15.20] | [-0.89, 15.20] | [-0.89, 15.20] | [-0.89, 15.20] | N/A | YES |
| Granger W (biv) | 5.84 | 5.84 | 5.84 | 5.84 | 6.18 (indep) | YES |
| Granger W (ctrl) | 13.33 | 13.33 | 13.33 | 13.33 | 11.51 (indep) | YES |
| Johansen trace | 19.04 | 19.04 | 19.04 | 19.04 | 19.04 | YES |
| ARDL F-stat | 6.51 | 6.51 | 6.51 | 6.51 | 1.40 (indep; explained) | YES |
| Industry pre-trend R2 | 0.82 | 0.82 | 0.82 | N/A | 0.82 | YES |
| Industry counterfactual deviation | -4.45 pp | -4.45 pp | -4.45 pp | N/A | -4.45 pp | YES |
| Services counterfactual deviation | +1.83 pp | +1.83 pp | +1.83 pp | N/A | +1.83 pp | YES |
| Services VA deviation | +5.89 pp | N/A | +5.89 pp | N/A | N/A | YES |
| Level correlation DE-services | 0.981 | N/A | 0.981 | N/A | 0.981 | YES |
| ILO endogeneity R2 | 0.989 | 0.989 | 0.989 | 0.989 | 0.986 (indep) | YES |
| Baseline 2033 median | 27.5% | 27.5% | N/A | 27.5% | N/A | YES |
| Low-digital 2033 median | 24.9% | 24.9% | N/A | 24.9% | N/A | YES |
| CV (endgame) | 0.046 | 0.046 | N/A | 0.046 | N/A | YES |
| Power | ~35% | ~35% | ~35% | ~35% | 43% (indep; explained) | YES |
| EP DE->SUB | 0.315 | 0.315 | 0.315 | 0.315 | 0.315 | YES |
| EP DE->CRE | 0.030 | 0.030 | 0.030 | N/A | 0.030 | YES |
| EP DE->IND_UP | 0.090 | 0.090 | 0.090 | N/A | 0.090 (0.075 strict) | YES |

All numbers are factually consistent across Phase 6 documents and upstream artifacts. The R2 = 0.82 correction (from the original 0.96 in ANALYSIS.md before the Phase 5 fix) has been properly propagated into both REPORT.md and ANALYSIS_NOTE.md. PASS.

---

## Regression Detection

### R2 Correction Propagation

Phase 5 flagged the industry pre-trend R2 as 0.82 (not 0.96 as originally reported). The human gate approved with instruction to correct. ANALYSIS.md Table 2.1 now shows 0.82. REPORT.md and ANALYSIS_NOTE.md both report 0.82. REPORT.md Section 7 (Verification Summary) explicitly documents this correction. No regression.

### EP Values

All EP values in Phase 6 documents match Phase 3 ANALYSIS.md exactly. No unexplained changes. No regression.

### Scenario Results

All scenario medians and confidence intervals in Phase 6 documents match Phase 4 PROJECTION.md exactly. No regression.

### Filter-Flow Numbers

T=24, 40 columns, 37 usable columns, 286 smart city pilots -- all consistent across phases. No regression.

---

## Audit Trail Completeness

### claims.yaml Coverage

claims.yaml contains 34 claims (C1 through C34) covering:
- Executive Summary claims (C1-C4)
- Data Foundation claims (C5-C9)
- Substitution channel findings (C10-C16)
- Creation channel findings (C17-C19)
- Mediation findings (C20-C21)
- Demographics findings (C22-C23)
- Uncertainty quantification (C24-C25)
- Forward projection (C26-C28)
- Structural break (C29-C30)
- Power analysis (C31)
- ILO endogeneity (C32)
- DID-inspired regression (C33)
- Break year sensitivity (C34)

**Section coverage check against REPORT.md:**

| REPORT.md Section | Claims covering it | Adequate? |
|:---|:---|:---:|
| Executive Summary | C1-C4, C26-C28 | YES |
| First Principles | None directly | Acceptable -- theoretical framing, not factual claims |
| Data Foundation | C5-C9, C31, C32 | YES |
| Substitution Channel | C1, C2, C10-C16 | YES |
| Creation Channel | C3, C17-C19 | YES |
| Mediation Channel | C4, C20-C21 | YES |
| Demographics | C22-C23 | YES |
| Structural Break | C29-C30, C34 | YES |
| Forward Projection | C26-C28 | YES |
| Sensitivity | C34 | Minimal -- see B2 note |
| Uncertainty | C24-C25 | YES |
| Verification | Phase 5 results in verification.yaml | YES |
| Policy Implications | Not directly claimed | Acceptable -- implications derived from findings |

Coverage is adequate. Every major factual claim in the report maps to at least one claim in claims.yaml.

### Methodology Coverage

methodology.yaml has 5 entries. This is the subject of issue B3 above.

### Provenance Coverage

provenance.yaml lists 8 datasets, matching the data registry. PASS.

### Verification Coverage

verification.yaml accurately summarizes Phase 5 results with reproduction details. PASS (subject to C3 above about the 8 vs 10 metric count).

---

## Caveats Carried Forward

All seven Phase 0 data quality warnings are explicitly listed in both documents:

| Warning | In REPORT.md | In ANALYSIS_NOTE.md | In audit_trail_section.md |
|:---|:---:|:---:|:---:|
| 1. DID not executable | YES (Sec 2, 5, 7) | YES (Sec 2, audit) | YES |
| 2. Skill-level analysis impossible | YES (Sec 2) | YES (Sec 2) | YES |
| 3. DE proxy saturated | YES (Sec 2, 4, 5, 7) | YES (Sec 2, 6, audit) | YES |
| 4. T=24 limits complexity | YES (Sec 2, 3, 5, 7) | YES (Sec 2, 3, audit) | YES |
| 5. ILO endogeneity | YES (Sec 2, 7) | YES (Sec 2) | YES |
| 6. No individual-level testing | YES (Sec 2, 7) | YES (Sec 2) | YES |
| 7. No cross-sectional variation | YES (Sec 2, 7) | YES (Sec 2) | YES |

PASS. All warnings are prominently carried forward.

The Phase 5 flags are also carried:
- R2 discrepancy: corrected and documented in REPORT.md Section 7
- ARDL F-stat divergence: documented in REPORT.md Section 7
- Power analysis discrepancy (35% vs 43%): documented in REPORT.md Section 7
- DE->IND_UP EP discrepancy (0.090 vs 0.075): noted in VERIFICATION.md as Category C

The audit_trail_section.md lists 10 warnings carried forward (the 7 from Phase 0 plus 3 additional from downstream phases: structural break confounding, VAR ordering sensitivity, DE index structural break at 2009). This is more thorough than the 7 in REPORT.md but the extra 3 are analysis-internal concerns that do not need stakeholder-facing prominence.

---

## Upstream Feedback

No issues requiring upstream fixes were identified. The R2 correction requested in Phase 5 has been applied in Phase 3 ANALYSIS.md. All EP values and classifications are consistent from Phase 3 through Phase 6.

---

## Overall Assessment

The Phase 6 documentation is thorough, factually consistent, and honest about limitations. The REPORT.md is well-written per the Writing Style Guide, with effective analogies and clear explanations of statistical concepts. The ANALYSIS_NOTE.md provides the complete technical backbone with full EP arithmetic and refutation details. The audit trail covers the major claims, though the methodology.yaml count discrepancy (B3) should be resolved.

The 3 Category B issues are all resolvable without structural changes:
- B1 (DISPUTED label missing from claims.yaml) is a single claim entry addition
- B2 (Executive Summary clarity on single-edge EP) is a minor prose clarification
- B3 (methodology.yaml count mismatch) requires either expanding the YAML or fixing the narrative count

No Category A issues block advancement. The analysis is epistemically honest, the EP propagation is correct, the factual claims are traceable, and the caveats are prominently displayed.

**Verdict: PASS** -- the 3 Category B issues should be addressed before final publication but do not block the Phase 6 gate.
