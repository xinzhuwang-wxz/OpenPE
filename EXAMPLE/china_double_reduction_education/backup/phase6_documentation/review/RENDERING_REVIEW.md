# Rendering Review

## Summary
- **Document**: `/Users/bamboo/Githubs/OpenPE/analyses/china_double_reduction_education/phase6_documentation/exec/ANALYSIS_NOTE.md`
- **PDF**: `/Users/bamboo/Githubs/OpenPE/analyses/china_double_reduction_education/phase6_documentation/exec/ANALYSIS_NOTE.pdf`
- **Date**: 2026-03-29
- **Compilation status**: Success with warnings
- **Page count**: 20 pages
- **Category A issues**: 1
- **Category B issues**: 2
- **Category C issues**: 3

## Compilation
- **Command**: `pixi run build-pdf`
- **Exit code**: 0
- **Warnings**:
  - pandoc-crossref version mismatch (compiled with 3.8.2.1, running through 3.8.3)
  - Multiple overfull `\hbox` warnings (lines 334, 402, 624--630, 994--1007)
  - Multiple underfull `\hbox` (line 570)
  - Absolute path warnings for all 10 included figures (cosmetic; build succeeds)
- **Errors**: None

## Figure Rendering
- **Figure 1** (fig01_real_education_expenditure_timeseries.pdf, p6): Renders correctly. Clear color distinction (blue/red/green). Vertical policy line and COVID band visible. Appropriate size at 90% width.
- **Figure 2** (fig08_ciefr_spending_decomposition.pdf, p7): Renders correctly. Horizontal bar chart with percentage labels. 70% width appropriate.
- **Figure 3** (fig07_tutoring_industry_collapse.pdf, p8): Renders correctly. Two-panel layout. Panel (b) x-axis tick labels are rotated and small but legible.
- **Figure 4** (fig06_per_child_spending.pdf, p8): Renders correctly. Two-panel layout. Legend text in panel (a) partially overlaps data but remains readable.
- **Figure 5** (fig_p3_02_its_primary.pdf, p9): Renders correctly. Three-panel ITS results. Subplot text is small but legible.
- **Figure 6** (fig_p3_07_refutation.pdf, p12): Renders correctly. Four-panel layout. Panel (d) contains an embedded summary table which is readable.
- **Figure 7** (fig10_urban_rural_divergence.pdf, p13): Renders correctly. Two-panel layout.
- **Figure 8** (scenario_comparison.pdf, p14): Renders correctly. Confidence bands clearly distinguished.
- **Figure 9** (sensitivity_tornado.pdf, p15): Renders correctly. Color coding visible.
- **Figure 10** (ep_decay_chart.pdf, p16): Renders correctly. Two-panel layout with EP threshold annotations.

All 10 figures render without corruption or missing-image placeholders.

## Math Compilation
- All inline math (`$...$`) renders correctly throughout. Greek letters, subscripts, superscripts, operators all display properly.
- Display equation (Eq. 1, p7) renders correctly with equation number.
- Indicator function `\mathbb{1}` renders correctly.
- `\pm`, `\sigma`, `\to`, `\times`, `\ge`, `\varepsilon` all render correctly.
- No raw LaTeX visible in the output.

## Layout
- **Page breaks**: Generally acceptable. Figure 6 (refutation, p12) has substantial whitespace above it due to float placement, but this is standard LaTeX float behavior.
- **Table 1** (EP summary, p4): Spans the full page. First column ("Edge") wraps heavily due to narrow column width, creating multi-line rows (e.g., "Policy -> Industry Collapse" wraps to 3 lines). Readable but not ideal.
- **Table 5** (uncertainty, p10--11): Splits across pages 10 and 11. The "CPI deflator choice" row appears alone at the top of page 11 as an orphaned table fragment.
- **Margins**: Content stays within margins on all pages except where overfull hbox warnings indicate minor protrusions (up to 18.58pt on the ITS results table rows, p9).
- **Headers/footers**: Consistent page numbering throughout.
- **Section numbering**: Correct and sequential (1--7 + unnumbered References).

## Cross-References

**Total figure references**: 14 uses of `@fig:` in source; 10 figure labels defined.
**Total table references**: 6 uses of `@tbl:` in source; 11 table labels defined.
**Total equation references**: 0 uses of `@eq:` (equation is defined but never cross-referenced).
**Total section references**: 0 uses of `@sec:` in running text (section labels defined but unused).

- **Resolved**: All `@fig:` and `@tbl:` references resolve to numbered targets. No `??` or unresolved references appear in the PDF.
- **Rendering format issue**: pandoc-crossref renders references in lowercase abbreviated form ("fig. 1", "tbl. 3"). When the source writes `Figure @fig:name`, the PDF shows "Figure fig. 5" -- a redundant "Figure fig." pattern. This occurs on pages 3, 6, 7, 8, 9, 11, 12, 13, 15, 16. This is a **Category A** issue because it looks like a formatting error to readers.

## Citations

- **Total unique citations in source**: 9 (`zhang2020shadow`, `park2016shadow`, `liu2025crowdingin`, `sixthtone2022crackdown`, `wei2024household`, `nbs2025communique`, `worldbank2024wdi`, `huang2025biting`, `chen2025bans`)
- **Resolved**: 9/9. All render as author-year format in the PDF.
- **Unresolved**: None.
- **Bibliography entries rendered**: 8 (citeproc correctly omits uncited entries)
- **Bibliography entries in .bib file**: 16
- **Uncited .bib entries**: 7 (`liu2022regulating`, `larbi2025doublereduction`, `sun2024doublereduction`, `wang2023shadowgovernance`, `voxchina2024education`, `voa2024easing`, `eric2024doublereduction`, `mordor2024tutoring`). Not a rendering issue; these are available for future use.
- **Bibliography format**: Consistent author-year style. Entries are well-formatted with DOI links rendered as clickable URLs.

## Table Formatting

- **Table 1** (EP summary, p4): Readable but narrow "Edge" column causes excessive line wrapping. 4 columns; alignment correct.
- **Table 2** (data sources, p5): Clean rendering. 5 columns, all readable.
- **Table 3** (ITS results, p9): 7 columns. **Overflows right margin** per tectonic warning (overfull hbox 18.58pt on 3 data rows). Content is still readable but extends slightly past the margin.
- **Table 4** (refutation, p9--10): 3 columns. Clean rendering, spans page break acceptably.
- **Table 5** (uncertainty, p10--11): 4 columns. Orphaned row on p11 (see Layout above).
- **Table 6** (scenarios, p13): 4 columns. Clean rendering.
- **Table 7** (EP decay, p16): 5 columns. Clean rendering. First column wraps slightly.
- **Table 8** (EP trajectory, p17): 3 columns. Clean rendering.
- **Table 9** (chain EP, p17): 4 columns. Clean rendering.
- **Table 10** (methodology, p17--18): 3 columns. Spans pages; readable.
- **Table 11** (reference comparison, p18): 5 columns. **Overflows right margin** per tectonic warning (overfull hbox 13.77pt). Content readable but extends past margin.

All tables have captions. All use pipe format in source, rendering as proper LaTeX tables.

## Page Count Assessment
- **Total pages**: 20
- **Assessment**: Appropriate for a focused analysis note. The document covers all required sections (executive summary, principles, data, analysis, projection, audit, limitations, references).

## Issues

### Category A (Must Resolve)
1. **Redundant "Figure fig." cross-reference pattern** (pages 3, 6, 7, 8, 9, 11, 12, 13, 15, 16). The source writes `Figure @fig:name` but pandoc-crossref renders `@fig:name` as "fig. N", producing "Figure fig. 5" throughout. **Fix**: Either capitalize the pandoc-crossref output using YAML metadata (`figPrefix: "Figure"`) and drop the manual "Figure" prefix, or use `[-@fig:name]` to suppress the prefix and keep the manual "Figure" word. Alternatively, add crossref metadata to the YAML header: `figPrefix: ["Figure", "Figures"]` and remove the leading "Figure" from prose.

### Category B (Must Fix)
1. **Table 3 (ITS results) overflows right margin** (p9). The 7-column table extends 18.58pt past the right margin. **Fix**: Reduce column count by merging "Stat. unc." and "Syst. unc." into a single column, or use a smaller font for the table, or abbreviate column headers.
2. **Table 11 (reference comparison) overflows right margin** (p18). The 5-column table extends 13.77pt past the margin. **Fix**: Use a `\small` font wrapper or reduce column widths. Consider using a longtable or reducing text in cells.

### Category C (Minor)
1. **Table 5 orphaned row** (p11). The last row ("CPI deflator choice") appears alone at the top of page 11. Consider adding `\needspace` or restructuring to keep the table together.
2. **pandoc-crossref version mismatch warning**. Compiled with 3.8.2.1 but running through 3.8.3. No visible issues resulted, but updating pandoc-crossref would eliminate the warning.
3. **7 uncited bibliography entries** in `references.bib`. Not a rendering issue, but cleaning unused entries would improve maintainability.

## Recommendations

**Before the document is rendering-ready, fix the Category A issue:**

1. Add pandoc-crossref configuration to the YAML front matter to fix the "Figure fig." redundancy. The recommended fix is to add to the YAML header:
   ```yaml
   figPrefix:
     - "Figure"
     - "Figures"
   tblPrefix:
     - "Table"
     - "Tables"
   eqnPrefix:
     - "Equation"
     - "Equations"
   ```
   Then change all instances of `Figure @fig:name` in the prose to just `@fig:name` (pandoc-crossref will prepend the capitalized prefix automatically). At sentence start, use `@Fig:name` for automatic capitalization.

**Category B fixes (table overflow) can be addressed by:**
- Adding `-V 'geometry:margin=0.85in'` to the pandoc command, or
- Wrapping wide tables in `\small` using a pandoc filter, or
- Reducing column count in Table 3 (ITS results).
