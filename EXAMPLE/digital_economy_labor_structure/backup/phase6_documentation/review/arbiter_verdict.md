# Arbiter Adjudication: Phase 6 Documentation

## Input Reviews
- Logic Review: `phase6_documentation/review/logic_review.md` (0 A, 3 B, 5 C -- PASS)
- Methods Review: `phase6_documentation/review/methods_review.md` (0 A, 4 B, 5 C)
- Domain Review: `phase6_documentation/review/domain_review.md` (0 A, 3 B, 5 C)
- Rendering Review: `phase6_documentation/review/rendering_review.md` (3 A, 5 B, 4 C)

## Issue Adjudication Table

| ID | Finding | Domain | Logic | Methods | Rendering | Adjudicated Category | Rationale |
|----|---------|--------|-------|---------|-----------|---------------------|-----------|
| 1 | ARDL F-stat divergence not flagged in findings sections | B1 | -- | B1 | -- | B | Domain and methods agree this is important. The substitution channel section cites ARDL F=6.51 as confirmatory but the independent replication produced F=1.40. One sentence noting the divergence and reliance on Johansen suffices. |
| 2 | State industrial policy as omitted confounder for complement effect | B1 | -- | -- | -- | B | Domain-only finding but valid. Made in China 2025 and dual circulation strategy are plausible alternative explanations for why industrial employment held up. A paragraph acknowledging this as a confounder is appropriate. No new analysis required. |
| 3 | Controlled ARDL specification may overstate precision (overfitting at T=24) | B3 | -- | -- | -- | C | Downgraded from B to C. The REPORT already presents both bivariate and controlled specifications with full numbers. The uncertainty decomposition captures the 7.78 pp shift from demographic control inclusion. The bivariate estimate is presented first and used as the headline. Adding an explicit overfitting caveat would be ideal but is not required -- the reader can assess both specifications as presented. |
| 4 | DISPUTED label missing from claims.yaml for controlled DE->CRE | -- | B1 | -- | -- | B | The audit trail should be at least as precise as the ANALYSIS_NOTE. Adding a DISPUTED annotation to claim C3 or a separate entry is a small fix that strengthens traceability. |
| 5 | Executive Summary "Joint EP" phrasing implies multi-edge chain | -- | B2 | -- | -- | C | Downgraded from B to C. The Executive Summary context makes clear that DE->SUB is the finding under discussion. "Joint EP" is the framework's standard term. A clarification would be nice but is not misleading enough to require a fix. |
| 6 | methodology.yaml has 5 entries but audit_trail_section.md claims 18 | -- | B3 | B4 | -- | B | Both logic and methods reviewers flagged this. Internal inconsistency in the audit trail -- either populate the YAML or fix the count. This is a clear discrepancy that undermines the audit trail's credibility. |
| 7 | Bootstrap CI missing for ARDL long-run coefficient | -- | -- | B2 | -- | C | Downgraded from B to C. The delta-method CI is standard practice and the REPORT already notes that bootstrap intervals are wider than analytical ones in the controlled specification. Computing a bootstrap CI for the ARDL coefficient at T=24 would be a new computation beyond Phase 6 scope (documentation phase). The limitation is implicitly acknowledged. |
| 8 | DE->IND_UP EP value (0.090 vs 0.075) not flagged in REPORT mediation section | -- | -- | B3 | -- | C | Downgraded from B to C. The discrepancy was classified as Category C in Phase 5, has no downstream impact (both values are below soft truncation), and is documented in VERIFICATION.md. The logic reviewer confirmed it is a known upstream issue carried forward correctly. A footnote would be nice but is not required. |
| 9 | ANALYSIS_NOTE.pdf Table 15 (Final results) unreadable | -- | -- | -- | A1 | C | Downgraded from A to C. This is a PDF rendering artifact in the secondary deliverable. The ANALYSIS_NOTE.md source is correct (pipe tables with valid markdown). The table overflow is caused by pandoc/LaTeX column width allocation failing on a wide table with inline math. REPORT.pdf is the primary deliverable and renders correctly. The markdown source is readable. This is a cosmetic issue in the secondary PDF that does not block the analysis. |
| 10 | ANALYSIS_NOTE.pdf Table 20 (Conventions compliance) unreadable | -- | -- | -- | A2 | C | Downgraded from A to C. Same rationale as ID 9. The conventions compliance table in ANALYSIS_NOTE.pdf has garbled rendering due to math-in-pipe-table parsing issues. The source markdown is correct. The REPORT.pdf conventions table (Table 9) renders with minor overflow but is readable. This is a secondary-deliverable rendering issue. |
| 11 | ANALYSIS_NOTE.pdf Table 12 (Signal injection) corrupted cell | -- | -- | -- | A3 | C | Downgraded from A to C. A single cell shows `${ }$0` instead of a numeric value. The rest of the table is readable and the value is available in the markdown source. This is a minor rendering glitch, not an analytical error. |
| 12 | REPORT.pdf Table 5 (Sensitivity) dollar sign leak | -- | -- | -- | B1 | C | The plus-minus symbol renders correctly with surrounding dollar sign artifacts. Values are interpretable. Minor formatting issue. |
| 13 | REPORT.pdf Table 9 (Methodology) overfull hbox | -- | -- | -- | B2 | C | Content overflows right margin by 32.7pt. Still readable. Minor layout issue. |
| 14 | ANALYSIS_NOTE.pdf Table 1 (Initial EP) column merge | -- | -- | -- | B3 | C | "LITERATURE_SUPPORTED" merges with EP values in some rows. The values are available in the markdown source. Minor rendering issue in secondary deliverable. |
| 15 | ANALYSIS_NOTE.pdf Sections 11.3/11.4 empty stubs | -- | -- | -- | B4 | C | Empty appendix headers. Either remove or populate. Minor structural issue. |
| 16 | ANALYSIS_NOTE.pdf Table 21 math leak | -- | -- | -- | B5 | C | Same category of math-in-pipe-table rendering issue. Minor. |
| 17 | Date mismatch (REPORT 2026-03-30, AN 2026-03-29) | -- | C1 | -- | -- | C | Cosmetic. |
| 18 | provenance.yaml quality scores unexplained | -- | C2 | -- | -- | C | Minor documentation gap. |
| 19 | verification.yaml 8 vs 10 metric count | -- | C3 | -- | -- | C | Minor inconsistency in YAML extract. |
| 20 | Section heading "The 2014 Structural Break" vs text 2013-2015 | -- | C4 | -- | -- | C | Minor. |
| 21 | ANALYSIS_NOTE Phase 0 labels missing from REPORT EP table | -- | C5 | -- | -- | C | Style difference between documents. Acceptable. |
| 22 | "pp" not defined on first use | -- | -- | C1 | -- | C | Minor. |
| 23 | Sensitivity tornado omits sign information | -- | -- | C2 | -- | C | Minor. |
| 24 | DID equation omits demographic control | -- | -- | C3 | -- | C | Minor. |
| 25 | Block bootstrap block size not justified | -- | -- | C4 | -- | C | Minor. Standard cube-root rule gives 3. |
| 26 | Notation inconsistency between documents | -- | -- | C5 | -- | C | Minor. |
| 27 | "Robust" endgame label potentially misleading | C1 | -- | -- | -- | C | Minor. Report explains the label thoroughly. |
| 28 | Complement effect lacks sectoral context | C2 | -- | -- | -- | C | Minor. |
| 29 | Power analysis 35% vs 43% range | C3 | -- | -- | -- | C | Already uses conservative 35%. |
| 30 | Reference analyses need methodological context | C4 | -- | -- | -- | C | Minor. |
| 31 | Automation lag effects not mentioned | C5 | -- | -- | -- | C | Minor. |
| 32 | REPORT.pdf white space issues | -- | -- | -- | C1-C3 | C | LaTeX float placement. Cosmetic. |
| 33 | ANALYSIS_NOTE.pdf Phase 0 warnings `${ }$35%` rendering | -- | -- | -- | C4 | C | Minor rendering glitch. |

## EP Adjudication

1. **EP Assessment Reasonableness**: All four reviewers agree that EP values are correctly computed, consistently propagated across all documents and upstream artifacts, and conservatively assessed. The logic reviewer verified every EP calculation against the truth x relevance formula and confirmed exact matches across REPORT.md, ANALYSIS_NOTE.md, and ANALYSIS.md. No EP-related disagreements exist.

2. **Truncation Decision Validity**: The logic reviewer confirmed all truncation decisions are correct. Only DE->SUB (0.315) survives above soft truncation (0.15). All other edges and chains are correctly truncated. No reviewer challenged this.

3. **Label Consistency**: All reviewers confirm DATA_SUPPORTED/CORRELATION/HYPOTHESIZED labels are consistent with refutation test outcomes. DE->SUB at CORRELATION (2/3 PASS) is the correct classification. The logic reviewer noted the DISPUTED classification for controlled DE->CRE is present in ANALYSIS_NOTE.md but missing from claims.yaml (adjudicated as B above).

4. **Confidence Band Appropriateness**: The methods reviewer confirmed that uncertainty decomposition is thorough. The domain reviewer noted the bands are appropriate given data constraints. No reviewer found the bands too narrow or too wide.

5. **Causal DAG Validity**: All reviewers confirm the DAG structure is defensible. The domain reviewer identified state industrial policy as a missing potential confounder (adjudicated as B above) but agreed this does not change the DAG structure -- it is a caveat about interpretation of the DE->SUB edge.

## Adjudicated Category A Issues

None. The three Category A issues from the rendering reviewer have been downgraded to Category C after adjudication. The rationale:

- **REPORT.pdf is the primary deliverable** and has no Category A rendering issues. All figures render correctly, all cross-references resolve, all citations compile, and the document is readable throughout.
- **ANALYSIS_NOTE.pdf is the secondary deliverable.** Its purpose is as a logic-focused technical artifact. The rendering issues (Tables 15, 20, and 12) are caused by pandoc/LaTeX failing to allocate column widths for wide pipe tables containing inline math. The markdown source for all three tables is correct and readable.
- **The rendering issues are cosmetic, not analytical.** No data is lost, no conclusions are affected, and no reader would be misled about the analysis findings. A reader who needs the exact numbers can consult the markdown source or the corresponding (correctly rendered) tables in REPORT.pdf.
- **Fixing these issues would improve polish but does not block the analysis gate.** The fixes (splitting tables, replacing math notation with text equivalents, adding explicit column widths) are desirable improvements that can be made as Category C items.

## Adjudicated Category B Issues

Three Category B issues remain after adjudication. All are low-effort prose/YAML fixes:

1. **[B-1] ARDL F-stat divergence not flagged in findings sections (ID 1).** The substitution channel section of REPORT.md and ANALYSIS_NOTE.md should note that the ARDL bounds F-statistic was not independently reproduced (78.5% divergence) and that cointegration rests primarily on the Johansen trace test. One sentence in each document suffices. Raised by domain reviewer and methods reviewer.

2. **[B-2] State industrial policy as omitted confounder (ID 2).** Add a paragraph in the substitution channel section acknowledging Made in China 2025 / dual circulation strategy as a potential alternative explanation for the complement effect. No new analysis required -- this is a caveat. Raised by domain reviewer only, but the argument is compelling.

3. **[B-3] methodology.yaml count mismatch (ID 6).** The audit_trail_section.md claims 18 methodology decisions but methodology.yaml contains only 5. Either populate the YAML with the missing entries or correct the narrative count. Raised by both logic and methods reviewers.

## Adjudicated Category C Issues

Twenty-seven Category C items (IDs 3, 5, 7-33). These are suggestions for improvement. Notable clusters:

- **Rendering polish** (IDs 9-16, 32-33): Table overflow and math-in-pipe-table issues in ANALYSIS_NOTE.pdf, minor formatting in REPORT.pdf. Desirable to fix but not blocking.
- **Prose clarifications** (IDs 3, 5, 7, 8, 22, 27-31): Additional caveats, definitions, and context that would strengthen the documents.
- **Audit trail minor gaps** (IDs 17-21): Date alignment, quality score explanation, metric count, section heading, label columns.
- **Notation/style** (IDs 23-26): Minor consistency improvements.

## Regression Assessment

No regressions detected. All four reviewers confirmed:
- R-squared correction (0.96 to 0.82) from Phase 5 has been properly propagated into both Phase 6 documents and upstream ANALYSIS.md.
- All EP values match Phase 3 ANALYSIS.md exactly.
- All scenario results match Phase 4 PROJECTION.md exactly.
- All verification findings from Phase 5 are accurately represented.
- Filter-flow numbers (T=24, 40 columns, 37 usable, 286 smart city pilots) are consistent across all phases.

## Verdict Rationale

**No Category A issues remain after adjudication.** The rendering reviewer's three Category A findings are all in ANALYSIS_NOTE.pdf (the secondary deliverable) and are pandoc/LaTeX rendering artifacts, not analytical errors. The markdown source is correct. REPORT.pdf, the primary deliverable, has no Category A issues.

**Three Category B issues remain, all low-effort fixes:**
- B-1: Add one sentence about ARDL F-stat divergence in findings sections (both documents)
- B-2: Add one paragraph about industrial policy as confounder (both documents)
- B-3: Fix methodology.yaml entry count or narrative count

These are prose and YAML additions that can be resolved in a single iteration without structural changes to either document. They do not require new computations, new data, or changes to the analysis strategy.

**All four content reviewers (domain, logic, methods, rendering) found zero Category A analytical issues.** The analysis is epistemically honest, the EP propagation is correct and consistent across all documents and upstream artifacts, the factual claims are traceable, the caveats are prominently displayed, and the Writing Style Guide requirements are met.

**The three Category B items collectively represent a minor gap, not a significant one.** However, per the arbiter protocol, unresolved B items should be addressed before PASS. The choice is between PASS (with B items as accepted post-gate fixes) and ITERATE (requiring a fix cycle).

Given that:
- The B items are all prose/YAML additions requiring no re-analysis
- The logic reviewer already issued a PASS verdict
- No reviewer raised concerns about the analytical conclusions
- The documents are otherwise thorough and well-crafted

I issue ITERATE with a narrowly scoped fix requirement. The three B items must be addressed, after which the phase can pass without full re-review -- a spot-check of the three specific changes is sufficient.

### Items That MUST Be Fixed

1. Add one sentence in the substitution channel section of both REPORT.md and ANALYSIS_NOTE.md noting the ARDL bounds F-statistic was not independently reproduced and that cointegration confirmation rests on the Johansen trace test.
2. Add one paragraph in the substitution channel section of both REPORT.md and ANALYSIS_NOTE.md acknowledging state industrial policy (Made in China 2025, dual circulation) as a potential confounder for the complement effect.
3. Either populate methodology.yaml with the additional entries referenced in audit_trail_section.md, or correct the "eighteen" count in audit_trail_section.md to match the actual number of entries (5).

### Items That Are Suggestions Only

All 27 Category C items. Of particular value if time permits:
- Fix ANALYSIS_NOTE.md pipe tables that cause rendering issues in PDF (IDs 9-11): replace inline math with text equivalents or split wide tables.
- Define "pp" on first use in REPORT.md (ID 22).
- Remove empty appendix stubs in ANALYSIS_NOTE.md sections 11.3/11.4 (ID 15).

DECISION: ITERATE
