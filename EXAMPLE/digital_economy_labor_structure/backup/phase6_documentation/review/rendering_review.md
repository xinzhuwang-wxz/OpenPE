# Rendering Review

## Summary
- **Document**: REPORT.pdf at `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase6_documentation/exec/REPORT.pdf`
- **Secondary document**: ANALYSIS_NOTE.pdf at `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase6_documentation/exec/ANALYSIS_NOTE.pdf`
- **Date**: 2026-03-30
- **Compilation status**: Success with warnings
- **REPORT.pdf page count**: 23 pages
- **ANALYSIS_NOTE.pdf page count**: 26 pages
- **Category A issues**: 3
- **Category B issues**: 5
- **Category C issues**: 4

## Compilation

- **Command**: `pixi run build-pdf`
- **Exit code**: 0
- **Pandoc-crossref version mismatch**: pandoc-crossref compiled with 3.8.2.1 but run through 3.8.3. This is a known minor incompatibility but can cause silent cross-reference failures.
- **Overfull hbox warnings**: Multiple occurrences, most notably:
  - texput.tex line 342-350: repeated overfull hbox (7-12pt too wide) -- corresponds to the methodology choices table in Section 9.2
  - texput.tex line 849: overfull hbox (32.7pt too wide) in alignment -- corresponds to a table overflowing margins
- **Underfull hbox warnings**: Multiple occurrences at lines 180-190, 256-266, 503-511, 632-640, 1047-1052, 1113-1119. These are cosmetic (loose paragraph spacing).
- **Absolute path warnings**: Tectonic reports accessing system fonts (Palatino.ttc, Menlo.ttc) and temporary figure paths. Non-blocking but builds are not portable.
- **Errors**: None

## Figure Rendering

### REPORT.pdf

| Figure | Page | Renders | Size | Caption | Notes |
|--------|------|---------|------|---------|-------|
| Fig. 1: structural_break_did_baseline.pdf | 8 | OK | Appropriate | Present, descriptive | 4-panel figure, all subplots legible |
| Fig. 2: method_comparison_summary.pdf | 10 | OK | Appropriate | Present, descriptive | 6-panel figure, small axis labels but readable |
| Fig. 3: var_irf_mediation.pdf | 11 | OK | Appropriate | Present, descriptive | 9-panel IRF grid, readable |
| Fig. 4: scenario_comparison.pdf | 14 | OK | Appropriate | Present, descriptive | Clean rendering with confidence bands |
| Fig. 5: sensitivity_tornado.pdf | 15 | OK | Appropriate | Present, descriptive | Color legend readable |
| Fig. 6: ep_decay_chart.pdf | 18 | OK | Appropriate | Present, descriptive | Two-panel figure, truncation lines clear |
| Fig. 7: uncertainty_tornado.pdf | 18 | OK | Appropriate | Present, descriptive | Horizontal bar chart, clear |

### ANALYSIS_NOTE.pdf

| Figure | Page | Renders | Size | Caption | Notes |
|--------|------|---------|------|---------|-------|
| Fig. 1: structural_break_did_baseline.pdf | 8 | OK | Appropriate | Present | Same 4-panel figure as REPORT |
| Fig. 2: method_comparison_summary.pdf | 9 | OK | Appropriate | Present | Same 6-panel figure |
| Fig. 3: var_irf_mediation.pdf | 11 | OK | Appropriate | Present | Same 9-panel IRF |
| Fig. 4: ep_propagation.pdf | 13 | OK | Appropriate | Present | EP propagation across phases |
| Fig. 5: refutation_summary.pdf | 14 | OK | Appropriate | Present | Heatmap, color-coded |
| Fig. 6: sensitivity_break_year.pdf | 16 | OK | Appropriate | Present | Break year sensitivity |
| Fig. 7: uncertainty_tornado.pdf | 17 | OK | Appropriate | Present | Same tornado chart |
| Fig. 8: scenario_comparison.pdf | 20 | OK | Appropriate | Present | Same scenario comparison |
| Fig. 9: sensitivity_tornado.pdf | 21 | OK | Appropriate | Present | Same sensitivity tornado |
| Fig. 10: ep_decay_chart.pdf | 22 | OK | Appropriate | Present | Same EP decay chart |
| Fig. 11: irf_creation_substitution.pdf | 25 | OK | Appropriate | Present | Two-panel IRF comparison |

All figures render correctly in both documents. No missing images, no placeholder boxes, no corrupted renders. Vector PDF figures are clean. Colors are distinguishable.

## Math Compilation

### REPORT.pdf
- **Inline math**: All `$...$` expressions render correctly throughout. Greek letters ($\alpha$, $\beta$), subscripts ($p_{\text{boot}}$, $\beta_{\text{DE}}$), comparison operators ($\geq$), and confidence intervals render as formatted math.
- **Display math**: No display math equations in REPORT.md (by design -- the report is a stakeholder document).
- **Symbol consistency**: Consistent use of $\to$ for causal arrows (DE$\to$SUB), $\pm$ for uncertainty ranges.
- **No raw LaTeX visible**: All LaTeX commands compile.

### ANALYSIS_NOTE.pdf
- **Inline math**: Renders correctly throughout.
- **Display math**: Equations (1) and (2) on pages 13-14 render as centered display equations with correct numbering.
- **Equation numbering**: Correct and sequential (Eq. 1, Eq. 2).
- **No raw LaTeX visible in main text**.
- **ISSUE**: In Table 15 (page 16-17, "Final results"), the "Total" column shows garbled rendering: "$\pm$4.10|CORRELATION||DE$\to$Ind." runs together with the Classification column text. This is a table overflow/column-merging issue (see Category A below).
- **ISSUE**: In Table 20 (page 23, "Conventions compliance"), some rows render with garbled math and text running together. The row containing "Granger causality T$\geq$30" and "DOCUMENTED DEVIATION" renders as a single unreadable line mixing math symbols and text.

## Layout

### REPORT.pdf
- **Page breaks**: Generally clean. The table of contents spans pages 1-2, which is appropriate for a 23-page document.
- **Orphaned text**: No egregious orphans observed.
- **Margins**: Content generally within margins except for tables flagged below.
- **Headers/footers**: Consistent throughout -- "OpenPE Analysis Report" on the left, section name on the right, page number centered at bottom. Header rule present.
- **Section numbering**: Correct and sequential (1-9 plus unnumbered References).
- **Page numbering**: Correct (1-23).
- **White space**: Page 4 has significant white space below section 2.4 ("How Explanatory Power Evolved") -- the table (Table 1) was pushed to page 5, leaving roughly half of page 4 empty. Similar issue on page 8 where Figure 1 is placed mid-page with large white space above it. Page 14 has significant white space below Figure 4. Page 21 has the Code References section header with an empty table body below and then white space for the rest of the page.

### ANALYSIS_NOTE.pdf
- **Page breaks**: Generally clean.
- **Headers/footers**: No custom headers (unlike REPORT.pdf). Page numbers only.
- **Section numbering**: Correct (1-13).
- **Page numbering**: Correct (1-26).
- **White space**: Page 14 has large white space above Figure 5 (refutation heatmap). Page 24 has sections 11.3 and 11.4 as headers with no content below them -- these appear as empty appendix stubs.

## Cross-References

### REPORT.pdf
- **Total figure references in source**: 7 (`@fig:structural-break`, `@fig:method-comparison`, `@fig:var-irf`, `@fig:scenario-comparison`, `@fig:sensitivity-tornado`, `@fig:ep-decay`, `@fig:uncertainty-tornado`)
- **Total table references in source**: 4 (`@tbl:ep-evolution`, `@tbl:data-overview`, `@tbl:scenarios-main`, `@tbl:sensitivity-main` -- note: not all tables are explicitly referenced via `@tbl:`)
- **Total section references in source**: 0 (sections are labeled with `{#sec:}` but never referenced via `@sec:`)
- **Resolved**: All figure and table references resolve correctly. Verified in PDF: "fig. 1" through "fig. 7", "tbl. 1" through "tbl. 10" appear with correct numbers.
- **Unresolved**: None. No "??" or raw `@fig:` text visible in the PDF output.
- **Spot-check**: "fig. 1" on page 7 correctly refers to the structural break figure on page 8. "tbl. 4" on page 13 correctly refers to the scenarios table on page 13. References verified correct.

### ANALYSIS_NOTE.pdf
- **Figure references**: All resolve. "fig. 1" through "fig. 11" present.
- **Table references**: All resolve. "tbl. 1" through "tbl. 25" present.
- **Section references**: `@sec:ep-propagation` on page 4 resolves correctly to "sec. 5" (EP Propagation).
- **Unresolved**: None detected.

## Citations

### REPORT.pdf
- **Total citations in source**: 13 citation instances using 10 unique keys
- **Citation keys used**: `acemoglu2011skills` (x2), `herrendorf2014growth`, `toda1995statistical` (x2), `pesaran2001bounds` (x2), `cai2010demographic`, `acemoglu2022demographics`, `zhu2023smart` (x3), `li2024digital` (x2), `zhao2022digital`, `blanchard1989dynamic`, `hacker2006bootstrap`
- **All resolved**: Every citation renders as "(Author Year)" format in the PDF. No `[?]` or raw citation keys visible.
- **Bibliography**: Present on pages 22-23. Contains 10 entries.
- **Bibliography completeness**: All 10 cited works appear in the bibliography.
- **Bibliography format**: Consistent author-year format with hanging indentation.
- **Uncited bibliography entries**: None. Every bibliography entry is cited at least once.

### ANALYSIS_NOTE.pdf
- **Note**: ANALYSIS_NOTE.md does not use `--citeproc` or a bibliography file. Citations appear inline as "(Author Year)" text rather than formal pandoc citations. This is acceptable for the logic-focused technical artifact but differs from REPORT.md's approach.
- **No unresolved citations visible**.

## Table Formatting

### REPORT.pdf

| Table | Page | Readable | Overflow | Booktabs | Caption | Issues |
|-------|------|----------|----------|----------|---------|--------|
| Table 1: EP evolution | 5 | Yes | No | Yes | Present | "Reason for Change" column is narrow, causing multi-line wrapping in some cells; still readable |
| Table 2: Data overview | 5-6 | Yes | No | Yes | Present | Spans page break; content continues on page 6 |
| Table 3: Refutation battery | 9 | Yes | No | Yes | Present | Clean |
| Table 4: Scenarios | 13 | Yes | No | Yes | Present | Clean |
| **Table 5: Sensitivity** | **15** | **Partially** | **Yes** | **Yes** | **Present** | **"Impact" column shows `$\pm\$0.79 pp` -- the dollar signs from LaTeX `$\pm$` leak into the rendered output. The plus-minus symbol renders but is surrounded by literal dollar signs.** |
| Table 6: EP decay | 16 | Yes | No | Yes | Present | Clean |
| Table 7: Uncertainty | 16-17 | Yes | No | Yes | Present | Split across page; readable |
| Table 8: Verification | 20 | Yes | No | Yes | Present | Clean |
| **Table 9: Methodology** | **21** | **Partially** | **Yes** | **Yes** | **Present** | **Overfull hbox (32.7pt). The "Justification" column text is compressed and wraps awkwardly. "T\$\geq\$30" renders correctly but the overall column widths cause content to overflow right margin.** |
| Table 10: Code refs | 22 | Yes | No | Yes | Present | Clean |

### ANALYSIS_NOTE.pdf

| Table | Page | Readable | Issues |
|-------|------|----------|--------|
| Table 1: Initial EP | 4 | Partially | "Label" column shows "LITERATURE_SUPPORTED" with "D" characters appended to Phase 0 EP values (e.g., "LITERATURE_SUPPORTEDD.49"). This is a column alignment / overflow issue where the label text merges with the next column. |
| Table 2: Data registry | 5 | Yes | "Constructed" in Source column runs into Temporal coverage column for DE composite index row |
| Table 3: Engineered features | 6 | Yes | Clean |
| Tables 4-7: Refutation | 7-10 | Yes | Clean |
| Table 8: EP update rules | 12 | Yes | Clean |
| Table 9: EP propagation | 12 | Partially | Narrow columns cause wrapping; "Change reason" column text compressed |
| Table 10: Joint_EP | 13 | Yes | Clean |
| Table 11: DID regression | 15 | Yes | Clean |
| Table 12: Signal injection | 15 | Partially | "Recovered" column shows `${ }$0` for the null injection row -- literal curly braces and dollar signs leak through |
| Table 13: Bootstrap CI | 16 | Yes | Clean |
| Table 14: Uncertainty decomp | 16 | Yes | Clean |
| **Table 15: Final results** | **16-17** | **No** | **CATEGORY A: The table overflows badly. Text from the "Total" and "Classification" columns merges into an unreadable string: "$\pm$4.10|CORRELATION||DE$\to$\$Ind." The Classification column text runs into the Parameter column of the next row. This table is unreadable in its current form.** |
| Table 16: Scenarios | 17 | Yes | Clean |
| Table 17: Sensitivity | 18 | Yes | Clean |
| Table 18: EP decay | 18-19 | Yes | Clean |
| Table 19: Verification | 19 | Yes | Clean |
| **Table 20: Conventions** | **23** | **No** | **CATEGORY A: The table row containing "Granger causality T$\geq$30" and "DOCUMENTED DEVIATION" renders as a garbled single line: `$3refutationtests|PASS||Reporteffectsizeswith CI|PASS|T$24uTodaYamotobstraplPASS||Stationarity`. Multiple rows merge into one unreadable line. Pipe characters from markdown appear as literal text.** |
| Table 21: Methodology | 23 | Partially | "T$30convention; TY valid for T" leaks math notation into prose |
| Table 22-24: Statistical appendix | 24-25 | Yes | Clean |
| Table 25: Code references | 26 | Yes | Clean |

## Page Count Assessment

- **REPORT.pdf**: 23 pages -- appropriate for the analysis scope (single-channel finding with extensive methodology discussion).
- **ANALYSIS_NOTE.pdf**: 26 pages -- appropriate for the technical artifact with statistical appendix.
- **Assessment**: Both documents are within the acceptable range (30-100 pages guideline is for full multi-channel analyses; this analysis has significant data limitations that constrain scope). Acceptable.

## Issues

### Category A (Blocking)

1. **ANALYSIS_NOTE.pdf Table 15 (Final results, page 16-17)**: Table overflows margins and columns merge into unreadable text. The table has too many columns (Parameter, Central, Stat., Syst., Total, Classification) with inline math in most cells, causing pandoc/LaTeX to fail at column width allocation. The Classification column text merges with adjacent columns. This table is unreadable and must be fixed before the document is rendering-ready.

2. **ANALYSIS_NOTE.pdf Table 20 (Conventions compliance, page 23)**: Multiple rows render as a single garbled line with pipe characters visible as literal text and math/text intermixed. The source markdown has `$\geq$3` in a table cell which appears to cause pandoc to misparse the pipe-delimited table structure. This table is unreadable.

3. **ANALYSIS_NOTE.pdf Table 12 (Signal injection, page 15)**: The "Recovered" column for the null injection row shows `${ }$0` -- literal curly braces and dollar signs leak through instead of rendering as "0". While the rest of the table is readable, this specific cell contains corrupted rendering of what should be a simple numeric value.

### Category B (Important)

1. **REPORT.pdf Table 5 (Sensitivity, page 15)**: The "Impact" column renders `$\pm$` with surrounding dollar signs partially visible, showing as "$\pm\$0.79 pp". The LaTeX math mode delimiters leak into the rendered output. The values are still interpretable but the formatting is incorrect.

2. **REPORT.pdf Table 9 (Methodology choices, page 21)**: Overfull hbox by 32.7pt. The three-column table exceeds the right margin. The "Justification" column contains long text with embedded LaTeX (`T$\geq$30`) that contributes to the overflow. Content is readable but extends past the margin.

3. **ANALYSIS_NOTE.pdf Table 1 (Initial EP, page 4)**: The "Label" column text "LITERATURE_SUPPORTED" merges with the Phase 0 EP values, rendering as "LITERATURE_SUPPORTEDD.49" for some rows. Column boundaries are lost.

4. **ANALYSIS_NOTE.pdf Sections 11.3 and 11.4 (pages 24)**: These appendix sections ("Impulse Response Functions" and "DID-Inspired Estimates (Creation Channel)") appear as headers with no content below them. They appear to be empty stubs -- either the content is missing or was not included. If intentionally empty, they should be removed; if content was intended, it is missing.

5. **ANALYSIS_NOTE.pdf Table 21 (Methodology choices, page 23)**: The "Justification" column for Toda-Yamamoto row renders as "T$30convention; TY valid for T{T}$20)" -- math mode leaks into the text. The `$` delimiters around `\geq` break the table cell parsing.

### Category C (Minor)

1. **REPORT.pdf page 4**: Significant white space (approximately half the page) below section 2.4 before Table 1 appears on page 5. LaTeX float placement pushes the table to the next page.

2. **REPORT.pdf page 8**: Large white space above Figure 1. The figure float is placed below center, leaving the top third of the page empty after the preceding text.

3. **REPORT.pdf page 21**: Section 9.4 (Code References) shows the table header but the table is squeezed near the page bottom. Pages 21-22 have suboptimal page break placement around this table.

4. **ANALYSIS_NOTE.pdf page 24**: Item 4 in the Phase 0 Warnings list shows "power ${ }$35%" -- literal curly braces appear in the rendered text instead of the tilde/approximately symbol.

## Recommendations

### Must fix before rendering-ready (Category A)

1. **ANALYSIS_NOTE.md Table 15 (Final results)**: Reduce the number of columns or use `longtable` with explicit column widths. Consider splitting into two tables (one for the substitution channel, one for descriptive findings) or removing the Classification column to a separate line below each row.

2. **ANALYSIS_NOTE.md Table 20 (Conventions compliance)**: The `$\geq$3` inside a pipe-table cell is causing pandoc to misparse the table. Replace `$\geq$3` with a text equivalent (e.g., ">=3" or spell out "at least 3 refutation tests"). Alternatively, move the detailed convention text outside the table.

3. **ANALYSIS_NOTE.md Table 12 (Signal injection)**: Fix the null injection "Recovered" cell. The source likely contains `${\sim}$0` or similar; replace with a simpler expression like `$\approx 0$` or plain `~0`.

### Should fix (Category B)

4. **REPORT.md Table 5 (Sensitivity)**: The `$\pm$0.79 pp` notation should be changed to `$\pm 0.79$ pp` to ensure the math mode properly wraps only the symbol and number.

5. **REPORT.md Table 9 (Methodology choices)**: Add `\usepackage{tabularx}` or use a `longtable` environment with explicit column widths to prevent the 32.7pt overflow. Alternatively, shorten the "Justification" column text.

6. **ANALYSIS_NOTE.md Table 1 (Initial EP)**: Widen the Label column or abbreviate "LITERATURE_SUPPORTED" to "LIT_SUPPORTED" to prevent column overflow.

7. **ANALYSIS_NOTE.md Sections 11.3 and 11.4**: Either add the intended content (IRF details and DID creation channel details) or remove these empty section headers.

8. **ANALYSIS_NOTE.md Table 21**: Replace `T$\geq$30` with `T>=30` or `T $\geq$ 30` (with spaces) to prevent math-mode parsing issues in the pipe table.

### Nice to fix (Category C)

9. Fix the `${ }$35%` rendering in ANALYSIS_NOTE.md Phase 0 warnings list -- replace `${\sim}35\%$` with `$\sim$35%` or `approximately 35%`.

10. Consider adding `\usepackage{float}` and `[H]` placement to reduce excessive white space on REPORT.pdf pages 4, 8, and 14.
