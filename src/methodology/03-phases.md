## 3. Analysis Phases

The analysis proceeds through seven phases (0–6). Dependencies between
phases are sequential — each phase consumes artifacts from prior phases.
Within a phase, **work should be parallelized where possible** —
sub-delegate independent tasks (data acquisition, statistical tests,
plot generation) to concurrent sub-agents. Parallelism is not optional
overhead; it is the standard operating mode for compute-heavy phases.
See §3a.5 for guidance.

### 3.0 Artifact and Review Gates

**Every phase boundary is a hard gate.** The agent must not begin Phase
N+1 until Phase N has produced its required artifact AND the required
review has been performed. This applies regardless of execution mode
(orchestrated multi-agent or single-session).

**The gate protocol:**
1. Phase executor produces the phase artifact (written to disk as markdown)
2. Phase executor updates the analysis log with what was done
3. The required review is performed (see Section 6)
4. Review findings are addressed (Category A items resolved)
5. Only then does the next phase begin

**Artifact existence is a precondition.** If Phase 1 has no `STRATEGY.md`
on disk, Phase 2 must not start. If Phase 3 has no `ANALYSIS.md`, Phase 4
must not start. The artifact is both the handoff document and the proof
that the phase was completed with appropriate rigor.

**Why this is a hard rule:** Without artifact gates, agents compress or
skip phases to reach results faster. The result is an analysis with no
audit trail, no intermediate review, and gaps that compound. The artifacts
exist to force the agent to consolidate what it knows before moving on —
the act of writing the artifact surfaces gaps that coding alone does not.

Skipping a phase artifact is never acceptable, even under context pressure.
If context limits are approaching, the agent should write the artifact for
the current phase, commit, and stop — not rush through remaining phases
without artifacts.

**Orchestrator architecture.** See §3a (`03a-orchestration.md`) for the
orchestrator loop, subagent delegation, context management, and health
monitoring. Phase-specific agent instructions are provided by the CLAUDE.md
templates in each phase directory (sourced from `templates/`) — these are
the operational entry points agents read at runtime.

**EP propagation across phases.** Every phase produces an epistemic
probability (EP) assessment for its key findings. EP is not a single
number — it is a vector across the analysis's sub-questions. The EP
vector from Phase N is an input to Phase N+1. Findings whose EP drops
below the `speculative` threshold (from `analysis_config.yaml`) are
flagged but not dropped — they continue through the chain with explicit
uncertainty markers. The EP decay chart (Appendix D) visualizes this
propagation across phases.

---

### Analysis Types

OpenPE supports multiple analysis types. The question and domain determine
which type applies; the agent confirms this during Phase 1.

- **Causal inference:** Identifying cause-effect relationships. Requires
  explicit confounder enumeration, identification strategy (IV, DiD, RDD,
  matching), and sensitivity analysis for unobserved confounders. The
  primary deliverable is a causal effect estimate with EP assessment.
- **Descriptive / measurement:** Quantifying a phenomenon without causal
  claims. Estimating distributions, trends, correlations, or summary
  statistics with full uncertainty. The primary deliverable is a
  characterized quantity with confidence intervals and EP assessment.
- **Forecasting / projection:** Predicting future outcomes under specified
  scenarios. Requires explicit assumptions, scenario definitions, and
  sensitivity to assumption violations. The primary deliverable is
  scenario-conditional projections with uncertainty bands and EP
  assessment.
- **Exploratory:** Open-ended investigation where the question is broad
  and the analysis structure emerges from the data. The primary
  deliverable is a set of ranked findings with EP assessments, each
  tagged as hypothesis-generating (not confirmatory).

Where phase descriptions below reference causal-inference-specific
concepts (identification strategy, confounder control), other analysis
types substitute the analogous concepts: measurement analyses substitute
systematic uncertainty evaluation, forecasting analyses substitute
scenario specification, exploratory analyses substitute discovery
criteria. The review criteria adapt accordingly.

---

### Phase 0: Discovery

**Goal:** Decompose the question, acquire and inventory data, and assess
whether the analysis is feasible.

**Inputs:** Analysis question, `analysis_config.yaml`, any user-provided
data.

**The agent must:**

*Question decomposition:*
- Parse the analysis question into atomic sub-questions, each with a
  measurable outcome
- Identify implicit assumptions in the question and make them explicit
- Determine the analysis type (causal, descriptive, forecasting,
  exploratory) and confirm with the configuration
- Map sub-questions to required data variables

*Data acquisition (Mode A) or inventory (Mode B/C):*
- **Mode A:** Identify data sources, acquire programmatically (APIs,
  web scraping, public databases), document provenance for each dataset
- **Mode B/C:** Inventory user-provided data — schema, completeness,
  quality, coverage
- For all modes: assess data sufficiency for each sub-question. If
  critical data is missing, document the gap and its impact on feasibility
- Record data lineage: source URL or API, retrieval date, version,
  license, any transformations applied during acquisition

*Quality gate:*
- Compute basic data quality metrics: missingness per variable, duplicate
  rates, outlier prevalence, temporal coverage
- Assess whether the data supports the question at the required
  granularity (geographic, temporal, cross-sectional)
- Identify potential selection bias in the available data
- **Gate criterion:** The agent must have at least one viable data path
  for each sub-question. If any sub-question has no data path, the agent
  must either acquire additional data, propose a proxy variable (with EP
  penalty), or recommend scoping out that sub-question.

**Output artifact:** `DISCOVERY.md` — question decomposition, data
inventory with quality metrics, feasibility assessment per sub-question,
data lineage documentation, and initial EP assessment (how confident is
the agent that the available data can answer each sub-question?).

**Review:** See Section 6. Discovery review evaluates question
decomposition quality, data sufficiency, and feasibility realism.

---

### Phase 1: Strategy

**Goal:** Produce a written analysis strategy that defines the
methodological approach for each sub-question.

**Inputs:** Discovery report, analysis configuration, domain context.

**The agent must:**
- Select the analytical method for each sub-question with justification
  (e.g., difference-in-differences for causal questions with panel data,
  regression discontinuity where a threshold exists, bootstrap estimation
  for uncertainty quantification)
- For causal analyses: specify the identification strategy, enumerate
  all known confounders, and propose the control approach for each
- For forecasting: define scenarios, specify model assumptions, and
  identify the sensitivity axes
- Enumerate anticipated sources of uncertainty and classify them
  (statistical, systematic, model-form, data-quality). **Before
  finalizing the uncertainty plan,** review relevant domain literature
  and enumerate every required source. For each source, state whether it
  will be addressed and, if not, why not. This enumeration becomes the
  baseline that Phase 5 reviews against — sources omitted here without
  justification are Category A findings downstream.
- Assess the initial EP for each sub-question based on data quality,
  method appropriateness, and confounder coverage
- Plan the analysis chain: which sub-questions feed into others, where
  EP compounds, and what the critical path is
- Identify validation strategy: what cross-checks, robustness tests,
  or out-of-sample validations will be performed

**For causal analyses,** the agent must additionally:
- Specify the causal graph (DAG) or identification argument
- Identify instruments, discontinuities, or natural experiments if
  applicable
- Plan sensitivity analysis for unobserved confounders (e.g., Rosenbaum
  bounds, E-value, coefficient stability)

**For forecasting analyses,** the agent must additionally:
- Define at least three scenarios (baseline, optimistic, pessimistic)
  with explicit parameter ranges
- Identify which assumptions drive the largest forecast divergence
- Plan backtesting on historical data to validate the forecasting
  approach

**Output artifact:** `STRATEGY.md` — a document covering the above points,
written at the level of a methods section in a peer-reviewed paper.
Quantitative estimates (expected effect sizes, sample sizes, power
calculations) should cite sources; order-of-magnitude estimates are
acceptable where precision is unavailable.

**Review:** See Section 6. Strategy review evaluates methodological
soundness, completeness of confounder/uncertainty enumeration, and
adequacy of the validation plan.

---

### Phase 2: Exploration

**Goal:** Characterize the data, validate assumptions, and establish the
foundation for the analytical approach.

**Inputs:** Strategy, data (acquired or provided), domain context.

**The agent must:**
- Profile all variables: distributions, correlations, missingness
  patterns, outlier analysis
- Validate key assumptions required by the chosen method (e.g.,
  parallel trends for DiD, continuity for RDD, normality for parametric
  tests)
- Perform data cleaning: handle missing values (document the strategy —
  imputation, listwise deletion, etc.), resolve duplicates, standardize
  units and coding
- Engineer features as specified in the strategy: transformations,
  interactions, lag variables, derived quantities
- Rank variables by relevance to each sub-question: correlation with
  outcome, predictive importance, theoretical relevance
- Produce exploratory visualizations: distributions, scatter plots,
  time series, cross-tabulations
- Establish baseline statistics: summary tables, group comparisons,
  naive estimates without controls

**PDF build test (independent task).** At any point during or after
Phase 2, run a stub PDF build (`pixi run build-pdf`) to verify the
toolchain. This is an independent task that can run in parallel with
Phase 2 work or be sub-delegated. Create a minimal
`phase6_documentation/exec/REPORT.md` stub with a title, one section
heading, and one figure reference. Fix any toolchain issues now — not
in Phase 6.

**Output artifact:** `EXPLORATION.md` — data profile summary, assumption
validation results, cleaning documentation, variable ranking with
visualizations, baseline statistics, and updated EP assessment (has data
exploration changed confidence in any sub-question?).

**Review:** See Section 6. Exploration review checks data quality
handling, assumption validation thoroughness, and variable survey
completeness.

**Data discovery.** The agent should expect to discover the data format
at runtime — column naming conventions, encoding, storage formats vary
across domains and sources. To avoid wasting time and memory:

1. **Metadata first.** Inspect column names, types, and shapes before
   loading full datasets (e.g., `pd.read_parquet(f).columns`,
   `df.dtypes`).
2. **Small slice first.** Load ~1000 rows first. Do not attempt to load
   all columns of a multi-GB file until you know the schema.
3. **Identify nested structure.** Determine which columns contain
   complex types (JSON, arrays, nested objects) before bulk loading —
   these require special handling and consume more memory.
4. **Document the schema.** The discovered structure, row counts, and
   any format quirks are themselves artifact content.

This discovery process is documented in the artifact.

---

### Phase 3: Analysis

**Goal:** Execute the analytical methods defined in the strategy,
propagate epistemic probability through each sub-chain, and produce
the core findings.

**Inputs:** Strategy, exploration report, cleaned data.

**The agent must:**

*Core analysis:*
- Implement the analytical method for each sub-question as specified in
  the strategy
- For causal analyses: implement the identification strategy, run the
  main specification, and produce the primary estimate with standard
  errors
- For descriptive analyses: compute the target quantities with full
  uncertainty propagation
- For forecasting: fit models, generate projections under each scenario
- For exploratory: systematically test candidate relationships, rank by
  effect size and statistical significance

*EP propagation:*
- Assess EP for each finding based on: statistical significance, method
  assumptions satisfied, confounder coverage, data quality of inputs
- Track how EP compounds through sub-question chains: if finding A (EP
  0.80) feeds into analysis B, the ceiling EP for B is 0.80
- Update the EP vector after each major analytical step
- Flag any finding whose EP drops below the `speculative` threshold

*Sub-chain expansion:*
- When a finding opens a new analytical avenue not anticipated in the
  strategy, the agent may expand into it — but must document the
  departure from the strategy and assess whether it changes the EP of
  upstream findings
- Sub-chain results are clearly labeled as "post-hoc" and given
  appropriate EP penalties (they are hypothesis-generating, not
  confirmatory)

*Robustness and sensitivity:*
- Run at least two alternative specifications for each primary finding
  (e.g., different control sets, different functional forms, different
  estimation windows)
- For causal analyses: run the planned sensitivity analysis for
  unobserved confounders
- Document how the primary finding changes across specifications — a
  finding that is fragile across reasonable alternatives gets an EP
  penalty
- **Every analytical choice must be motivated.** The artifact must
  include, for each key decision (variable inclusion, functional form,
  sample restriction), the reasoning and evidence supporting it. A
  choice without justification is an unjustified choice.

*Validation:*
- Run cross-validation, out-of-sample tests, or placebo tests as
  specified in the strategy
- For forecasting: run backtests on historical data
- Compare results to prior literature where available — agreement
  increases EP, disagreement requires investigation and documentation

**Workflow pattern.** Phase 3 is iteration-heavy. Follow this progression:

1. **Setup & prototype.** Build the analysis pipeline on a small slice
   (~1000 rows or a single sub-question). Verify it runs end-to-end and
   produces sensible estimates. Register each script as a pixi task.
2. **Full execution.** Run on the full dataset. Produce estimates,
   diagnostics, and visualizations for every sub-question.
3. **Inspect & validate.** Systematically review all produced results —
   diagnostic plots, residual patterns, sensitivity outcomes. This is
   where modeling issues must be caught before they propagate to Phase 4.

**Output artifact:** `ANALYSIS.md` — primary findings with EP assessment,
robustness results across specifications, sensitivity analysis outcomes,
validation test results, updated EP vector, and all supporting
visualizations.

**Convergence assessment.** After the initial analysis, the agent evaluates
whether findings have converged. The agent maintains a **convergence log**
(`convergence_log.md`) tracking each specification tried, the EP achieved,
and the limiting factor (statistical power, confounder coverage, data
quality, model sensitivity).

The assessment should progress through qualitatively different approaches,
not just parameter tuning within one specification:

1. *Optimize the current specification* — refine controls, functional form
2. *Try an alternative method* — different estimator, different
   identification strategy
3. *Try different data subsets* — time periods, geographies, subgroups
4. *Try different outcome definitions* — alternative operationalizations
   of the target variable
5. *Revisit assumptions* — relax or strengthen key assumptions and
   observe the effect

The agent should stop iterating when:
- The EP meets the `high_confidence` threshold, **or**
- At least 3 materially different specifications have been tried, **and**
- The most recent EP change was below the `convergence` threshold, **and**
- The remaining ideas are increasingly speculative

The convergence log is included in the artifact and provides evidence to
reviewers that reasonable alternatives were explored.

**Review:** See Section 6. Analysis review focuses on methodological
correctness, EP assessment quality, and robustness evidence.

---

### Phase 4: Projection

**Goal:** Extend findings into scenarios, assess sensitivity to key
assumptions, and establish the endgame convergence of the analysis.

**Inputs:** Analysis report, EP vector, full data.

**The agent must:**

*Scenario analysis:*
- Construct scenario projections where the analysis type supports them
  (forecasting analyses do this natively; causal and descriptive analyses
  project "what if" counterfactuals)
- For each scenario: define the assumptions explicitly, compute the
  projected outcome, and propagate EP through the projection
- Scenarios should span the plausible range — not just optimistic and
  pessimistic, but also "assumption X fails" stress tests

*Sensitivity analysis:*
- Identify the top-N assumptions or parameters that drive the largest
  variation in findings (tornado chart inputs)
- Vary each systematically and document the effect on primary findings
- For causal analyses: complete the formal sensitivity analysis for
  unobserved confounders (E-value, Rosenbaum bounds, coefficient
  stability tests)
- Rank sensitivities by impact on EP

*Endgame convergence:*
- Compare the EP vector from Phase 3 to the post-sensitivity EP vector
- Identify any findings whose EP changed materially due to sensitivity
  analysis — these require documentation of what assumption drives the
  change
- Produce the draft EP decay chart showing EP evolution from Phase 0
  through Phase 4
- Assess whether the analysis has reached its convergence criterion
  (EP change < `convergence` threshold across specifications)

*Uncertainty budget:*
- Produce the full uncertainty budget: statistical, systematic (each
  source separately), model-form, and data-quality components
- Provide the uncertainty breakdown in both the artifact (as tables and
  figures) and as machine-readable files (CSV, JSON, or NumPy `.npy`)
- Compare findings to prior literature or benchmarks where available.
  Compute a quantitative agreement measure (e.g., z-score relative to
  prior estimates). If no prior exists, justify why and note the
  finding is novel.

**Output artifact:** `PROJECTION.md` — scenario projections with EP
assessment, sensitivity tornado chart data, EP decay through phases,
uncertainty budget, and comparison to prior work.

**Review:** 4-bot review (Section 6.2). This gates the verification
phase. The cycle repeats until the arbiter issues PASS.

---

### Phase 5: Verification

**Goal:** Independently verify the analysis through reproduction,
robustness confirmation, and human review.

**Inputs:** All prior phase artifacts, analysis code, data.

**The agent must:**

*Independent reproduction:*
- Re-run the complete analysis chain from cleaned data to final findings
  using the committed code and pixi tasks
- Verify that all numerical results reproduce exactly (deterministic
  code with pinned seeds) or within expected stochastic variation
  (document the tolerance)
- Confirm that all figures regenerate correctly

*Cross-validation of key findings:*
- For each primary finding: implement at least one genuinely independent
  check (different method, different data subset, different outcome
  operationalization)
- Compare the independent check to the primary finding — agreement
  increases EP, disagreement requires investigation
- Document the independent checks and their outcomes

*Assumption stress testing:*
- For each key assumption identified in the sensitivity analysis: test
  what happens when the assumption is maximally violated
- Document which findings survive assumption violation and which do not
- Update EP accordingly — findings that are fragile to assumption
  violation get explicit EP penalties

*Draft report:*
- Produce `REPORT_DRAFT.md` — the full analysis report following the
  report specification (see `methodology/analysis-note.md`). **The
  report is a single evolving document across Phases 5 and 6.** Phase 5
  creates the complete report with preliminary results. Phase 6 polishes
  prose, adds final comparisons, and renders the PDF. The structure,
  methodology descriptions, cross-checks, and appendices are all written
  in Phase 5.
- A non-blocking subagent should compile the draft to PDF in parallel
  with the review cycle, so the human gate receives a rendered document.

**Output artifact:** `VERIFICATION.md` — reproduction confirmation,
cross-validation results, assumption stress test outcomes, updated EP
vector.

**Review:** 4-bot review (Section 6.2) on the draft report. The
methodology, critical, and constructive reviewers evaluate the report as
peer reviewers would. The arbiter must PASS before the report goes to
a human.

**Human gate:** After the arbiter passes, the draft report and all phase
artifacts are presented for human review. The analysis pauses until the
human approves proceeding to final documentation.

---

### Phase 6: Documentation

**Goal:** Produce the final analysis report and all deliverables.

**Inputs:** All prior phase artifacts, including verification results.
The draft report from Phase 5 — Phase 6 updates results, not structure.

**Report specification:** See `methodology/analysis-note.md` for the full
report specification: required sections, depth calibration, completeness
test, bibliography requirements, and PDF compilation. The report is a
single evolving document — Phase 5 writes it, Phase 6 polishes and
finalizes.

**The agent must:**
- Finalize the report with all results, visualizations, and EP
  assessments
- Produce the final EP decay chart showing EP evolution across all phases
- Generate machine-readable results in the `results/` directory:
  - `findings.yaml` — primary findings with EP, confidence intervals,
    and metadata
  - `uncertainty_budget.csv` — full uncertainty breakdown by source
  - `ep_trajectory.csv` — EP values at each phase boundary for each
    sub-question
  - `registry.yaml` — complete artifact registry mapping every artifact
    to its phase, commit hash, and review status
- Compile the report to PDF via pandoc
- Perform a final completeness check: every sub-question from Phase 0
  has a finding (even if the finding is "insufficient data, EP below
  threshold"), every finding has an EP, every EP has a justification

**Output artifact:** `REPORT.md` (+ compiled PDF) plus `results/`
directory containing machine-readable deliverables.

**Review:** See Section 6. Documentation review reads the report as a
peer reviewer would. Reviewers must check completeness — are all
cross-checks documented? Are all uncertainties described in sufficient
detail? Could a reader reproduce the analysis? Is the EP decay chart
consistent with the narrative?

---
