# Phase 6: Documentation

> **Phase 6: Documentation** produces a comprehensive, auditable report with
> EP decay visualization, full audit trail, and PDF output.

You are running Phase 6 for a **{{analysis_type}}** analysis named
**{{name}}**.

**Start in plan mode.** Before writing any prose, produce a plan: the report
section structure, which figures go where, which results tables are needed,
and what audit trail entries must be generated. Execute after the plan is set.

---

## Input requirements

Phase 6 depends on human-approved Phase 5. Before beginning, verify:

1. `exec/VERIFICATION.md` exists with overall PASS or FLAG verdict
2. Human gate approval (option a) is documented in the experiment log
3. All prior phase artifacts exist: DISCOVERY.md, STRATEGY.md, ANALYSIS.md,
   PROJECTION.md, VERIFICATION.md
4. All figures from Phases 0–4 exist in `figures/`
5. `data/registry.yaml` is complete

If human gate approval is not documented, halt and request Phase 5 completion.

---

## Output artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| **REPORT.md** | `exec/REPORT.md` | Complete analysis report in pandoc-compatible markdown |
| **REPORT.pdf** | `REPORT.pdf` | Rendered PDF via pandoc |
| **Audit trail** | `audit_trail/` | Per-claim source links, per-step methodology records |

All three must exist for the analysis to be considered complete.

---

## Agent profiles

Phase 6 uses two specialized agents. Read the applicable profile before
beginning each step:

| Agent | Profile | Steps |
|-------|---------|-------|
| Report writer | `.claude/agents/report-writer.md` | 6.1, 6.2, 6.3 |
| Plot validator | `.claude/agents/plot-validator.md` | 6.2 (figure validation) |

---

## Step 6.1 — Report Generation

**Goal:** Produce a structured, comprehensive report that synthesizes all
analysis phases into a coherent narrative.

**The agent must write REPORT.md following this outline:**

```markdown
# [Title derived from the user's original question]

## Executive Summary

[2-4 paragraphs: question, approach, key findings, confidence assessment.
 State the endgame classification. Include the primary EP chain with
 Joint_EP. No jargon — a non-specialist should understand this section.]

## 1. First Principles Identified

[Causal DAG visualization (mermaid format). Literature support for each
 principle. Competing DAGs considered and why the final structure was
 selected. Edge labels and EP values.]

## 2. Data Foundation

[Sources used (table from registry.yaml). Quality assessment summary per
 source. Limitations and caveats. Any data gaps and their impact on
 conclusions.]

## 3. Analysis Findings

[For each causal edge in the final DAG:]
### 3.X [Edge name: A → B]
- **Classification:** DATA_SUPPORTED / CORRELATION / HYPOTHESIZED
- **EP:** [value] (95% CI: [lower, upper])
- **Evidence:** [summary of statistical test, effect size, confounders]
- **Uncertainty range:** [quantified]

[Use these labels consistently:]
| Label | Meaning | Reader interpretation |
|-------|---------|----------------------|
| DATA_SUPPORTED | Survived refutation testing with quantitative evidence | Strong basis for conclusions |
| CORRELATION | Statistical association found, causation not established | Suggestive but not conclusive |
| HYPOTHESIZED | Not yet testable with available data | Speculative; treat with caution |

## 4. Forward Projection

[Scenario descriptions and results. Sensitivity analysis with tornado
 diagram reference. Endgame classification with evidence. EP decay chart
 reference. Fork conditions if applicable.]

## 5. Audit Trail

[Data provenance summary. Methodology choices and alternatives considered.
 Refutation test results. Verification report summary. Human gate decision.]

## Appendix

### A. Raw Code References
[Paths to all analysis scripts with brief descriptions]

### B. Statistical Details
[Full regression tables, test statistics, p-values, confidence intervals]

### C. Data Quality Report
[Full DATA_QUALITY.md content or reference]

### D. Experiment Log
[Complete experiment log or reference]
```

**Writing standards:**

- Every factual claim must cite its data source (dataset ID from registry.yaml)
- Every inferential step must reference the statistical test that supports it
- Uncertainty ranges appear with every quantitative claim — never bare numbers
- The report must be self-contained: a reader should not need to consult
  phase artifacts to understand the analysis
- Use pandoc-compatible markdown throughout

**Output:** `exec/REPORT.md` following the outline above.

---

## Step 6.2 — EP Decay Visualization

**Goal:** The EP decay chart is the core figure of every OpenPE report. It
communicates how confidence degrades from established findings through
forward projection.

**The agent must:**

1. **Finalize the EP decay chart.** Update or regenerate the Phase 4
   EP decay chart with any corrections from Phase 5 verification:
   - X-axis: time from present (or projection distance)
   - Y-axis: EP-weighted confidence in projected target variable
   - Central line: baseline scenario
   - Inner band (68% CI): near-term uncertainty
   - Outer band (95% CI): full scenario uncertainty
   - Vertical lines marking confidence tier transitions
   - Endgame classification annotation

2. **Validate all report figures.** Using the plot validator agent:
   - Every figure referenced in REPORT.md exists in `figures/`
   - Axis labels are present and readable
   - Color schemes are colorblind-accessible
   - Figure captions are descriptive and standalone-interpretable
   - No figure contains fabricated or placeholder data

3. **Generate any missing summary figures.** The report requires at minimum:
   - EP decay chart (`figures/ep_decay_chart.pdf`)
   - Scenario comparison (`figures/scenario_comparison.pdf`)
   - Sensitivity tornado (`figures/sensitivity_tornado.pdf`)
   - Causal DAG visualization (`figures/causal_dag.pdf`)

4. **Symlink all figures** into the report build directory:
   ```bash
   mkdir -p exec/figures
   ln -sf ../../figures/*.pdf exec/figures/
   ```

**Output:** Validated figures in `figures/` and symlinked into `exec/figures/`.

---

## Step 6.3 — Audit Trail Construction

**Goal:** Produce a machine-readable audit trail that links every claim in
the report to its evidence basis.

**The agent must:**

1. **Create the audit trail directory:**
   ```
   audit_trail/
     claims.yaml        # Every factual claim → data source mapping
     methodology.yaml   # Every analytical choice → justification
     provenance.yaml    # Copy of registry.yaml with verification status
     verification.yaml  # Summary of Phase 5 results
   ```

2. **Populate claims.yaml.** For every factual claim in the report:
   ```yaml
   claims:
     - id: "claim_001"
       text: "GDP growth averaged 6.2% over 2010-2020"
       source_dataset: "ds_001"
       source_field: "gdp_growth_annual"
       computation: "mean(2010:2020)"
       report_section: "3.1"
       verified: true
     - id: "claim_002"
       text: "Urbanization causally drives fertility decline"
       classification: "DATA_SUPPORTED"
       ep: 0.49
       evidence: "Granger causality test, p < 0.01; IV regression β = -0.34"
       refutation_survived: true
       report_section: "3.2"
   ```

3. **Populate methodology.yaml.** For every non-trivial analytical choice:
   ```yaml
   methodology:
     - id: "meth_001"
       choice: "Used Granger causality over simple regression"
       justification: "Time-series data requires temporal precedence test"
       alternatives_considered: ["OLS regression", "VAR model"]
       phase: "Phase 3"
     - id: "meth_002"
       choice: "3 scenarios (baseline, optimistic, pessimistic)"
       justification: "Standard scenario framework; fork conditions not binary"
       alternatives_considered: ["5 scenarios with policy variants"]
       phase: "Phase 4"
   ```

4. **The audit trail completeness test.** Every section of the report must
   have at least one corresponding entry in claims.yaml. Sections without
   auditable claims indicate either missing evidence or summary prose that
   should cite evidence.

**Output:** Populated `audit_trail/` directory.

---

## Step 6.4 — PDF Generation

**Goal:** Compile REPORT.md into a professional PDF.

**The agent must:**

1. **Run the PDF build task:**
   ```bash
   pixi run build-pdf
   ```
   This invokes pandoc with xelatex, numbered sections, table of contents,
   and properly sized figures.

2. **Verify the PDF:**
   - All figures render correctly (no missing image placeholders)
   - Table of contents is complete
   - Cross-references resolve (no "??" in the output)
   - Page count is reasonable for the analysis scope

3. **If the build fails:**
   - Check pandoc error output for markdown syntax issues
   - Verify all figure paths resolve
   - Ensure no raw LaTeX commands are embedded (pandoc handles conversion)
   - Fix and re-run until clean compilation

4. **Never use an LLM to convert markdown to LaTeX.** Pandoc handles this
   automatically. Manual LaTeX conversion introduces errors and is not
   reproducible.

**Output:** `REPORT.pdf` at the analysis root.

---

## Methodology references

- Architecture design: `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` (Sections 2-5)
- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (5-bot review)

---

## Non-negotiable rules

1. **Every claim must be auditable.** A factual claim without a traceable
   data source is not a finding — it is an assertion. The audit trail exists
   to make this distinction machine-verifiable.

2. **Never fabricate precision.** If the underlying data is LOW quality or
   the EP is below 0.3, the report must say so explicitly. Do not use
   precise-sounding language for imprecise findings. "Approximately 5-8%"
   is honest; "6.2%" from LOW-quality data is dishonest.

3. **The report is self-contained.** A reader should be able to understand
   every finding, its evidence basis, its confidence level, and its
   limitations without consulting any other document. If the report requires
   external reading to understand, it has a gap.

4. **EP decay is the core message.** The EP decay chart communicates the
   fundamental epistemic honesty of the analysis: what we know with
   confidence, what we project with decreasing confidence, and where
   uncertainty dominates. It must be prominent in the report.

5. **Carry forward all caveats.** Every data quality warning, every
   verification flag, every DISPUTED edge — all must appear in the report.
   The Documentation phase does not filter inconvenient findings.

6. **Classification labels are mandatory.** Every causal finding must carry
   its DATA_SUPPORTED / CORRELATION / HYPOTHESIZED label. Readers must be
   able to instantly distinguish established findings from speculative ones.

7. **Append to the experiment log.** Document report structure decisions,
   figure selection rationale, any editorial choices about emphasis or
   framing, and PDF build results.

---

## Review

**5-bot review** (includes rendering reviewer) — see `methodology/06-review.md`
for protocol.

Reviewers evaluate:
- Is the report self-contained and comprehensible to a non-specialist?
- Does the executive summary accurately represent the full findings?
- Are all causal findings labeled with classification and EP?
- Is the EP decay chart prominent and correctly annotated?
- Does the audit trail cover all factual claims?
- Are data quality caveats and verification flags visible?
- Does the PDF render correctly with all figures and cross-references?
- Is the report honest about limitations and uncertainty?

Write findings to `review/REVIEW_NOTES.md`.
