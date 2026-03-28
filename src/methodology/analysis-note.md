# Analysis Note Specification

The Analysis Note is the primary deliverable of an OpenPE analysis. It is a
pandoc-compatible markdown document that compiles into a professional PDF.

## Required Sections

### Executive Summary
2-4 paragraphs: question, approach, key findings, confidence assessment.
State the endgame classification. Include the primary EP chain with Joint_EP.
No jargon — a non-specialist should understand this section.

### 1. First Principles Identified
Causal DAG visualization (mermaid format). Literature support for each
principle. Competing DAGs considered and why the final structure was selected.
Edge labels and EP values.

### 2. Data Foundation
Sources used (table from registry.yaml). Quality assessment summary per
source. Limitations and caveats. Any data gaps and their impact on conclusions.

### 3. Analysis Findings
For each causal edge in the final DAG:

#### 3.X [Edge name: A → B]
- **Classification:** DATA_SUPPORTED / CORRELATION / HYPOTHESIZED / DISPUTED
- **EP:** [value] (95% CI: [lower, upper])
- **Evidence:** summary of statistical test, effect size, confounders
- **Uncertainty range:** quantified

Classification labels:

| Label | Meaning | Reader interpretation |
|-------|---------|----------------------|
| DATA_SUPPORTED | Survived refutation testing with quantitative evidence | Strong basis for conclusions |
| CORRELATION | Statistical association found, causation not established | Suggestive but not conclusive |
| HYPOTHESIZED | Not yet testable with available data | Speculative; treat with caution |
| DISPUTED | Contradictory evidence — placebo-anchored tests conflict | Requires human review |

### 4. Forward Projection
Scenario descriptions and results. Sensitivity analysis with tornado diagram.
Endgame classification with evidence. EP decay chart. Fork conditions.

### 5. Audit Trail
Data provenance summary. Methodology choices and alternatives considered.
Refutation test results. Verification report summary. Human gate decision.

### Appendices
- **A. Raw Code References:** Paths to all analysis scripts
- **B. Statistical Details:** Full regression tables, test statistics, CIs
- **C. Data Quality Report:** Full DATA_QUALITY.md content
- **D. Experiment Log:** Complete experiment log

## Format Requirements

- **LaTeX math:** `$...$` inline, `$$...$$` display
- **Figures:** `![Caption](figures/name.pdf){#fig:label}` — pandoc converts
  to `\includegraphics`
- **No raw HTML.** Pandoc markdown only.
- **Tables:** Pipe tables (`| col1 | col2 |`)
- **Cross-references:** pandoc-crossref syntax — `{#fig:label}`, `@fig:label`.
  At sentence start: `Figure @fig:name`. Every figure MUST have a label.
- **Citations:** `[@key]` with a `references.bib` BibTeX file
- **Sections:** `#`, `##`, `###` — pandoc adds numbering

## PDF Generation

```bash
pixi run build-pdf
```

Uses `openpe-metadata.yaml` for professional styling (branded headers,
executive summary box, figure sizing). See `scripts/openpe-metadata.yaml`.
