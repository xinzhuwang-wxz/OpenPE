# Phase 1: Strategy

> **Prerequisite:** Phase 0 must be complete. Read `exec/DISCOVERY.md` and
> `exec/DATA_QUALITY.md` before beginning. The causal DAGs, EP assessments,
> and acquired data from Phase 0 are your starting inputs.

You are developing the analysis strategy for a **{{analysis_type}}** analysis
named **{{name}}**.

**Start in plan mode.** Before writing any code or prose, produce a plan:
what methods you will evaluate, how you will refine EP estimates, what the
artifact structure will be. Execute after the plan is set.

---

## Output artifact

`exec/STRATEGY.md` — analysis strategy with method selection, initial EP
assessment, chain planning, systematic uncertainty inventory, and causal DAG
visualization.

## Methodology references

- Architecture design: `docs/superpowers/specs/2026-03-28-slop-fp-architecture-design.md` (Sections 2-5)
- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (4-bot review)

---

## Agent profile

Phase 1 uses the lead analyst agent. Read the profile before beginning:

| Agent | Profile | Steps |
|-------|---------|-------|
| Lead analyst | `.claude/agents/lead-analyst.md` | All of Phase 1 |

---

## Step 1.1 — Method Selection

**Goal:** Choose the causal inference method(s) best suited to the data
and causal structure identified in Phase 0.

**The agent must:**

1. **Review the causal DAGs from Phase 0.** Re-read `exec/DISCOVERY.md`
   and identify the primary causal edges to test. Note the edge labels
   (LITERATURE_SUPPORTED, THEORIZED, SPECULATIVE) and initial EP values.

2. **Assess data characteristics.** From Phase 0's acquired data and
   `exec/DATA_QUALITY.md`, determine:
   - Observational vs. experimental data
   - Panel data vs. cross-sectional vs. time series
   - Natural experiments or policy discontinuities available
   - Sample size and statistical power constraints
   - Confounding structure implied by the DAGs

3. **Evaluate candidate methods.** For each primary causal edge, consider
   which methods are applicable given the data structure:

   | Method | When applicable | Key requirements |
   |--------|----------------|------------------|
   | **Regression with controls** | Baseline; always applicable | Sufficient controls for confounders identified in DAG |
   | **Difference-in-differences** | Pre/post treatment with control group | Parallel trends assumption testable |
   | **Synthetic control** | Single treated unit, multiple control units | Adequate pre-treatment fit period |
   | **Instrumental variables** | Valid instrument available | Relevance + exclusion restriction defensible |
   | **Regression discontinuity** | Sharp/fuzzy cutoff in treatment assignment | Running variable identified, manipulation testable |
   | **Propensity score matching/weighting** | Selection on observables | Overlap condition, no unobserved confounders |
   | **Interrupted time series** | Intervention at known time point | Sufficient pre/post data, no concurrent shocks |
   | **Granger causality / VAR** | Time series with temporal precedence | Stationarity, sufficient lags |
   | **Mediation analysis** | Decomposing direct vs. indirect effects | Sequential ignorability |
   | **Bayesian structural model** | Complex DAG with prior information | Informative priors from literature |

4. **Select primary and secondary methods.** For each causal edge under
   test, select:
   - A **primary method** — the best-suited given data and assumptions
   - At least one **secondary method** — for robustness (Phase 3 requires
     estimation with at least 2 methods per edge)

   Justify each selection: why this method, why it is credible for this
   edge, what assumptions it requires, and how those assumptions will be
   tested.

5. **Identify method-specific data requirements.** Some methods require
   data transformations not yet performed:
   - IV: instrument variable identification and construction
   - DiD: treatment/control group assignment, pre-treatment period definition
   - Synthetic control: donor pool construction
   - RDD: running variable identification, bandwidth selection approach

   Document these as inputs to Phase 2 data preparation.

**Output:** Method selection table in STRATEGY.md:

```markdown
## Method Selection

| Causal Edge | Primary Method | Secondary Method | Key Assumptions | Data Requirements |
|-------------|---------------|-----------------|-----------------|-------------------|
| A -> B | Diff-in-diff | Synthetic control | Parallel trends | Pre-2015 control group data |
| C -> B | IV (instrument: Z) | Regression + controls | Exclusion restriction | Instrument Z time series |
```

---

## Step 1.2 — Initial EP Assessment

**Goal:** Refine the Phase 0 EP estimates using the method selection and
data quality information now available.

**The agent must:**

1. **Update truth values.** Incorporate data quality verdicts from Phase 0:
   - HIGH quality data supporting an edge: truth unchanged from Phase 0
   - MEDIUM quality: truth reduced by 0.1 (minimum 0.1)
   - LOW quality: truth capped at 0.3 regardless of Phase 0 estimate

   Also incorporate method credibility:
   - Strong identification strategy (e.g., valid RDD): truth +0.1 (max 1.0)
   - Weak identification (e.g., regression without clear exogeneity): truth -0.1

2. **Update relevance values.** With the actual data now in hand, reassess
   the causal attribution fraction for each edge. Phase 0 used theoretical
   priors; Phase 1 can use preliminary data characteristics (variance
   decomposition, correlation structure) to refine.

3. **Compute updated EP = truth x relevance** for every edge.

4. **Compute Joint_EP along chains.** For chains A -> B -> C, compute
   Joint_EP = EP(A->B) x EP(B->C). Apply truncation thresholds:

   | Threshold | Value | Action |
   |-----------|-------|--------|
   | Hard truncation | 0.05 | Stop exploring. Label "Beyond analytical horizon." |
   | Soft truncation | 0.15 | Lightweight assessment only. No sub-chain expansion. |
   | Sub-chain expansion minimum | 0.30 | Full sub-analysis justified. |

5. **Produce an EP summary table** comparing Phase 0 and Phase 1 values,
   with justification for every change.

**Output:** EP assessment section in STRATEGY.md with comparison table and
updated DAG visualization.

---

## Step 1.3 — Chain Planning

**Goal:** Determine the analytical scope — which causal chains get full
treatment, which get lightweight assessment, and where sub-chain expansion
may be needed.

**The agent must:**

1. **Classify every chain by Joint_EP:**
   - **Full analysis** (Joint_EP >= 0.30): Full causal testing pipeline in
     Phase 3, sub-chain expansion if warranted
   - **Lightweight assessment** (0.15 <= Joint_EP < 0.30): Single method
     estimation, no refutation battery, documented as "assessed but not
     fully tested"
   - **Beyond horizon** (Joint_EP < 0.15): No analysis. Document the chain
     and why it falls below threshold.

2. **Identify sub-chain expansion points.** For full-analysis chains, flag
   edges where:
   - The edge has high EP but low confidence (high relevance, low truth)
   - The edge represents a compound mechanism that could be decomposed
   - Decomposition would materially change the analysis conclusion

   These become candidate sub-analyses to scaffold in Phase 3.

3. **Determine main chain depth.** How many edges deep does the primary
   causal chain go? Deeper chains accumulate Joint_EP losses. A chain of
   depth 4 with EP = 0.5 per edge has Joint_EP = 0.0625 — below soft
   truncation. Plan accordingly.

4. **Map the analysis tree.** Produce a tree diagram showing:
   - Main analysis chains (full treatment)
   - Lightweight branches
   - Truncated branches
   - Potential sub-chain expansion points

**Output:** Chain planning section in STRATEGY.md with analysis tree diagram.

---

## Step 1.4 — Systematic Uncertainty Inventory

**Goal:** Enumerate all sources of uncertainty that must be quantified in
Phase 3. Every result in this framework carries: central value, statistical
uncertainty, systematic uncertainty, and total uncertainty.

**The agent must:**

1. **Statistical uncertainty sources:**
   - Sample size limitations
   - Estimation variance (bootstrap, jackknife, or analytical)
   - Model specification uncertainty (functional form)

2. **Systematic uncertainty sources (method-specific):**

   | Method | Key systematics |
   |--------|----------------|
   | Regression | Omitted variable bias, functional form, multicollinearity |
   | DiD | Parallel trends violation, treatment timing, spillovers |
   | Synthetic control | Donor pool sensitivity, pre-treatment fit quality |
   | IV | Weak instrument, exclusion restriction violation |
   | RDD | Bandwidth sensitivity, functional form near cutoff |
   | Propensity score | Model specification, overlap violation, hidden bias |
   | Time series | Structural breaks, non-stationarity, lag selection |

3. **Data-driven uncertainty sources:**
   - Measurement error in key variables
   - Missing data and imputation sensitivity
   - Temporal or spatial aggregation effects
   - Selection bias in the data source itself (from DATA_QUALITY.md)

4. **For each identified source, specify:**
   - How it will be quantified (analytical, bootstrap, sensitivity analysis)
   - What constitutes a "significant" systematic (threshold for reporting)
   - Whether it affects a single edge or propagates through the chain

5. **Cross-reference with DATA_QUALITY.md.** Every data quality warning
   from Phase 0 must map to at least one systematic uncertainty. Silent
   omissions are Category A findings (must-resolve, blocks advancement).

**Output:** Systematic uncertainty inventory table in STRATEGY.md.

---

## Step 1.5 — Causal DAG Visualization

**Goal:** Produce a refined causal DAG that incorporates all Phase 1
decisions and serves as the blueprint for Phase 3 analysis.

**The agent must:**

1. **Render the final Phase 1 DAG in mermaid format.** Include:
   - Updated EP values on each edge
   - Method assignment annotations
   - Chain classification (full / lightweight / truncated)
   - Sub-chain expansion candidates marked

2. **Produce a comparison view** showing Phase 0 DAG alongside Phase 1 DAG
   to make refinements visible.

3. **Document all DAG modifications** since Phase 0: edges added, removed,
   or re-labeled, with justification for each change.

**Output:** DAG visualization section in STRATEGY.md.

---

## STRATEGY.md structure

The final artifact must follow this structure:

```markdown
# Analysis Strategy: {{name}}

## 1. Phase 0 Summary
[Brief recap of question, domain, key findings from DISCOVERY.md]

## 2. Method Selection
[Step 1.1 output: method table with justifications]

## 3. EP Assessment
[Step 1.2 output: updated EP table, Phase 0 vs Phase 1 comparison]

## 4. Chain Planning
[Step 1.3 output: analysis tree, chain classifications]

## 5. Systematic Uncertainty Inventory
[Step 1.4 output: uncertainty sources table]

## 6. Causal DAG (Phase 1)
[Step 1.5 output: mermaid DAG with annotations]

## 7. Phase 2 Data Preparation Requirements
[Method-specific data transformations needed before analysis]

## 8. Risk Assessment
[What could go wrong: weak instruments, parallel trends violations,
insufficient data for planned methods. Contingency plans.]
```

---

## Non-negotiable rules

1. **Every method choice must be justified.** "We will use DiD" is
   insufficient. State why DiD is appropriate for this edge, what
   assumptions it requires, and how those assumptions will be tested.

2. **EP updates must be traceable.** Every change from Phase 0 EP values
   must have an explicit reason. No silent adjustments.

3. **At least 2 methods per primary edge.** Phase 3 requires estimation
   with at least 2 methods. Plan for this now — do not defer method
   selection to Phase 3.

4. **Data quality warnings propagate.** Every warning from
   `exec/DATA_QUALITY.md` must appear in the systematic uncertainty
   inventory. Ignoring a data quality issue is a Category A finding.

5. **Truncation decisions are documented.** Every chain classified as
   "beyond horizon" must be explicitly listed with its Joint_EP and the
   reason it falls below threshold. Readers must be able to see what was
   excluded and why.

6. **Append to the experiment log.** Document every material decision:
   why one method was chosen over another, why EP values were adjusted,
   what chains were truncated and why. The experiment log is the audit
   trail.

---

## Review

**4-bot review** — see `methodology/06-review.md` for protocol.

Reviewers evaluate:
- Are method selections appropriate for the data structure and causal
  questions? Are assumptions clearly stated?
- Are EP updates from Phase 0 justified and traceable?
- Is the chain planning reasonable? Are truncation decisions defensible?
- Is the systematic uncertainty inventory complete? Does every data quality
  warning map to at least one systematic?
- Is the causal DAG consistent with all decisions made?
- Are at least 2 methods planned for every primary causal edge?

Write findings to `review/REVIEW_NOTES.md`.
