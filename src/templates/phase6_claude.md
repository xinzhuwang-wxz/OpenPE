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
| **ANALYSIS_NOTE.md** | `exec/ANALYSIS_NOTE.md` | Logic-focused technical artifact: quantitative results, EP arithmetic, refutation details, reasoning chain |
| **REPORT.md** | `exec/REPORT.md` | Final stakeholder deliverable: rewritten per Writing Style Guide with "so what" leads, named scenarios, analogies |
| **REPORT.pdf** | `REPORT.pdf` (analysis root) | Rendered PDF compiled from REPORT.md via pandoc |
| **Audit trail** | `audit_trail/` | Per-claim source links, per-step methodology records, `generate_audit.py` script |

**All four must exist for the analysis to be considered complete.**

> **CRITICAL:** REPORT.md is NEVER a symlink or copy of ANALYSIS_NOTE.md.
> They are independently written documents with different prose styles.
> ANALYSIS_NOTE.md emphasizes logic and quantitative rigor.
> REPORT.md transforms this into polished prose following the Writing Style Guide.

---

## Agent profiles

Phase 6 uses two specialized agents. Read the applicable profile before
beginning each step:

| Agent | Profile | Steps |
|-------|---------|-------|
| Report writer | `.claude/agents/report-writer.md` | 6.1, 6.2, 6.3 |
| Plot validator | `.claude/agents/plot-validator.md` | 6.2 (figure validation) |

---

## Step 6.1 — Report Generation (Two Documents)

**Goal:** Produce TWO documents: (1) ANALYSIS_NOTE.md — the logic-focused
technical backbone, and (2) REPORT.md — the polished stakeholder deliverable.

**Workflow:**
1. Write `exec/ANALYSIS_NOTE.md` first. This document emphasizes quantitative
   results, EP arithmetic, refutation test details, and the full reasoning
   chain. It follows `methodology/analysis-note.md` format.
2. Then write `exec/REPORT.md` as an **independent rewrite** of the same
   content, transforming the prose per the Writing Style Guide below. Every
   fact and number comes from ANALYSIS_NOTE.md, but the prose is completely
   different.

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

- **Never hand-number headings.** Write `# First Principles` not
  `# 1. First Principles`. Pandoc's `--number-sections` flag generates all
  section numbers automatically. Hand-numbered headings produce double
  numbering in the PDF (e.g., "2  1. First Principles").
- Every factual claim must cite its data source (dataset ID from registry.yaml)
- Every inferential step must reference the statistical test that supports it
- Uncertainty ranges appear with every quantitative claim — never bare numbers
- The report must be self-contained: a reader should not need to consult
  phase artifacts to understand the analysis
- Use pandoc-compatible markdown throughout

**Output:** `exec/REPORT.md` following the outline above.

## Writing Style Guide

The report's core value is rigorous, transparent reasoning. Every causal
claim, every EP assessment, every refutation test result must be explained
fully. **Do not sacrifice analytical depth for brevity.** A 30-page report
that explains every step is better than a 10-page report that hand-waves.

**The dual requirement:** Rigorous reasoning AND polished prose. These are
not in tension — the best analysis reports are both thorough and well-written.
The reader should feel guided through a careful argument, not buried in a
data dump.

**Structure each section as:** conclusion first, then full reasoning chain,
then caveats and limitations.

**Prose quality checklist (apply before submitting):**

1. **Lead with "so what" — then show your work.** Every section opens with
   one sentence stating the key takeaway. Then walk through the full
   reasoning: what data was used, what method was applied, what the result
   was, what alternative explanations were considered and ruled out.
   Not "We analyzed X using Y" but "X causes Y — here is how we know,
   and here is what could make us wrong."

2. **No LLM-speak.** Avoid: "It is important to note that...",
   "As shown in Figure X...", "We can observe that...",
   "In this section, we will...". Instead, state the fact directly.
   But DO keep detailed technical explanations — just write them well.

3. **Use concrete numbers throughout.** Not "adoption increased significantly"
   but "adoption grew from 12% to 47% in 3 years (a 3.9x increase)."
   Provide both absolute and relative magnitudes where informative.

4. **Bold key numbers.** Use **bold** for the most important quantitative
   findings. One or two bold numbers per paragraph, maximum.

5. **Explain statistical concepts inline.** When using terms like "refutation
   test," "confidence interval," or "Granger causality," add a brief
   parenthetical: "refutation tests (which check whether the result
   holds up under different assumptions — for example, what happens if
   we randomly shuffle the treatment variable)."

6. **Use analogies for scale.** "The broadband divide between rich and
   poor countries is 800x — equivalent to comparing highway networks
   with dirt paths." Analogies complement the numbers, not replace them.

7. **Executive Summary is a standalone document.** Someone who reads ONLY
   the executive summary should know: the question, the answer, the
   confidence level, and the key caveat. 4 paragraphs maximum. But the
   rest of the report MUST contain the full reasoning — the executive
   summary is a preview, not a replacement.

8. **Each scenario gets a name and a narrative.** Not "Scenario 1:
   parameters (L=104, k=0.19)" but "The 'Smartphone Redux' scenario:
   agents follow the same explosive growth that smartphones did, reaching
   80% penetration by 2033." Then explain the full parameter set and
   why these values were chosen.

9. **Show the causal chain, step by step.** When presenting a causal
   argument, walk through each edge: "A causes B (EP=0.77, supported by
   scaling laws literature), B causes C (EP=0.55, theorized based on
   task-technology fit theory), therefore the chain A→B→C has Joint EP
   of 0.42." The reader should be able to follow and challenge each link.

10. **Don't fear length — fear incompleteness.** Every DAG edge that was
    tested deserves its own subsection with method, data, result,
    refutation outcome, and EP update. Every untestable edge deserves
    an explanation of WHY it's untestable and what data WOULD be needed.

**Tone:** Authoritative but honest. Confident where evidence supports it,
explicitly uncertain where it doesn't. Never hedge everything — that
reads as lack of conviction. Never assert without evidence — that reads
as overconfidence. The goal is the tone of a senior analyst briefing a
board: precise, thorough, and clear about what is known vs unknown.

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

5. **Reuse upstream figures.** Figures generated in Phases 0–5 that help
   illustrate findings MUST be included in the report with proper captions.
   Do not let upstream figures go to waste — review all files in `figures/`
   and incorporate every figure that supports a finding or adds context.

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

5. **Create `audit_trail/audit_trail_section.md`.** A human-readable
   narrative summarizing the audit trail: how many claims are audited,
   how many data sources are verified, and any gaps or flags. This is
   included verbatim in the final report's Audit appendix.

6. **Create `scripts/generate_audit.py`.** This script must be able to
   regenerate the audit trail from upstream artifacts (registry.yaml,
   ANALYSIS_NOTE.md, VERIFICATION.md). It is the reproducibility guarantee
   for the audit trail.

**Output:** Populated `audit_trail/` directory (including `audit_trail_section.md`) AND `scripts/generate_audit.py`.

> **WARNING:** Skipping Step 6.3 is a Category A violation. The audit trail
> is not optional — it is a core deliverable that makes every claim in
> the report machine-verifiable. Phase 6 is NOT complete without it.

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

5. **Produce REPORT_ZH.pdf (Chinese-language report).** After the English
   REPORT.pdf is verified, produce `exec/REPORT_ZH.md` by **translating
   `exec/REPORT.md` into Chinese** — preserving every section, paragraph,
   figure reference, table, and citation from the English version. The
   Chinese version must match the English version in structure, detail, and
   length; it is a faithful translation, NOT an independent rewrite or
   condensed summary. Figures may remain in English (no need to re-render).
   Compile to `REPORT_ZH.pdf` at both `exec/` and the analysis root using
   the same pandoc build pipeline as the English report.

**Output:** `REPORT.pdf` and `REPORT_ZH.pdf` at the analysis root (compiled
from `exec/REPORT.md` and `exec/REPORT_ZH.md` respectively).
Also generate `exec/REPORT.pdf`, `exec/REPORT_ZH.pdf`, and
`exec/ANALYSIS_NOTE.pdf` for archival.

---

## Methodology references

- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (3-bot review)

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

## Completion Checklist (Hard Gate)

Before declaring Phase 6 complete, verify ALL of these exist:

```
phase6_documentation/
  exec/
    ANALYSIS_NOTE.md          # Logic-focused technical document
    ANALYSIS_NOTE.pdf         # Compiled PDF of ANALYSIS_NOTE
    REPORT.md                 # Polished stakeholder deliverable (NOT a symlink)
    REPORT.pdf                # Compiled PDF of REPORT
    REPORT_ZH.md              # Chinese-language stakeholder deliverable
    REPORT_ZH.pdf             # Compiled PDF of REPORT_ZH
    references.bib            # Bibliography
    figures/                  # All referenced figures
  audit_trail/
    claims.yaml               # Every factual claim → data source
    methodology.yaml          # Every analytical choice → justification
    provenance.yaml           # Data provenance with verification status
    verification.yaml         # Phase 5 results summary
    audit_trail_section.md    # Human-readable audit narrative
  scripts/
    generate_audit.py         # Reproducible audit trail generation
REPORT.pdf                    # At analysis root (copy of exec/REPORT.pdf)
REPORT_ZH.pdf                 # At analysis root (copy of exec/REPORT_ZH.pdf)
```

**Missing any of these files is a Category A finding that blocks PASS.**

---

## Review

**3-bot two-stage review** — see `methodology/06-review.md` for protocol.

Phase 6 review is split into two stages to avoid wasting PDF compilation
cycles on content that needs revision:

### Stage 1: MD Content Review (before PDF compilation)

After Steps 6.1–6.3 (markdown documents + audit trail written), spawn the
**domain reviewer** and **plot-validator** in parallel. They evaluate the
markdown source only — no PDFs exist yet.

Domain reviewer evaluates:
- Is the report self-contained and comprehensible to a non-specialist?
- Does the executive summary accurately represent the full findings?
- Are all causal findings labeled with classification and EP?
- Is the EP decay chart prominent and correctly annotated?
- Does the audit trail cover all factual claims?
- Are data quality caveats and verification flags visible?
- Is the report honest about limitations and uncertainty?

If Stage 1 issues require ITERATE: fix the markdown, re-review Stage 1.
Do NOT compile PDFs until Stage 1 passes.

### Stage 2: PDF Rendering Review (after PDF compilation)

After Stage 1 passes and Step 6.4 compiles all PDFs, spawn the
**rendering reviewer**. It evaluates compiled PDFs only:
- Do all figures render correctly (no missing image placeholders)?
- Are there unresolved cross-references ("??" in output)?
- Is the table of contents complete?
- Do tables render properly?
- Is LaTeX math rendering correctly?
- Are section numbers correct (no double-numbering)?
- Is the Chinese PDF rendering CJK characters correctly?

### Arbiter Synthesis

After both stages complete, the **arbiter** synthesizes all findings
(domain + plot-validator from Stage 1, rendering from Stage 2) and issues
the final verdict. The arbiter receives all reviewer outputs but does NOT
re-review the PDFs or markdown itself.

Write findings to `review/REVIEW_NOTES.md`.
