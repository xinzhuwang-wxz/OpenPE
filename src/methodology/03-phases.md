## 3. Analysis Phases

The analysis proceeds through five phases. Dependencies between phases are
sequential — each phase consumes artifacts from prior phases. Within a phase,
**work should be parallelized where possible** — sub-delegate independent
tasks (MVA training, systematic evaluations, plot generation) to concurrent
sub-agents. Parallelism is not optional overhead; it is the standard
operating mode for compute-heavy phases. See §3a.5 for guidance.

### 3.0 Artifact and Review Gates

**Every phase boundary is a hard gate.** The agent must not begin Phase N+1
until Phase N has produced its required artifact AND the required review has
been performed. This applies regardless of execution mode (orchestrated
multi-agent or single-session).

**The gate protocol:**
1. Phase executor produces the phase artifact (written to disk as markdown)
2. Phase executor updates the experiment log with what was done
3. The required review is performed (see Section 6)
4. Review findings are addressed (Category A items resolved)
5. Only then does the next phase begin

**Artifact existence is a precondition.** If Phase 2 has no `EXPLORATION.md`
on disk, Phase 3 must not start. If Phase 4 has no `INFERENCE_EXPECTED.md`,
Phase 4b must not start. The artifact is both the handoff document and the
proof that the phase was completed with appropriate rigor.

**Why this is a hard rule:** Without artifact gates, agents compress or skip
phases to reach results faster. The result is an analysis with no audit trail,
no intermediate review, and gaps that compound. The artifacts exist to force
the agent to consolidate what it knows before moving on — the act of writing
the artifact surfaces gaps that coding alone does not.

Skipping a phase artifact is never acceptable, even under context pressure.
If context limits are approaching, the agent should write the artifact for the
current phase, commit, and stop — not rush through remaining phases without
artifacts.

**Orchestrator architecture.** See §3a (`03a-orchestration.md`) for the
orchestrator loop, subagent delegation, context management, and health
monitoring. Phase-specific agent instructions are provided by the CLAUDE.md
templates in each phase directory (sourced from `templates/`) — these are
the operational entry points agents read at runtime.

---

### Analysis Types

The spec supports two analysis types. The physics prompt must declare which
type applies; the agent confirms this during Phase 1.

- **Search / limit-setting:** Signal vs. background discrimination, signal
  region / control region structure, blinding protocol (Section 4), expected
  limits or significance as the primary deliverable.
- **Measurement:** Corrected differential or inclusive cross-sections, event
  shape distributions, or extracted physical parameters (e.g., αs). No
  signal/background separation per se — the "signal" is the process being
  measured. Blinding may not apply (the observable is the result). The primary
  deliverable is a corrected spectrum or extracted parameter with full
  uncertainties.

Where phase descriptions below reference search-specific concepts (signal
region, control regions, S/B optimization), measurement analyses substitute
the analogous concepts: fiducial region, sideband/validation regions,
purity optimization. The review criteria adapt accordingly — e.g., "closure
test in VR" becomes "correction validation via cross-checks."

---

### Phase 1: Strategy

**Goal:** Produce a written analysis strategy that a collaboration reviewer
could approve.

**Inputs:** Physics prompt, experiment context (via retrieval).

**The agent must:**
- Query the experiment corpus to understand the detector capabilities, available
  datasets, and any prior work in the same or related channels
- Identify the signal process, production mechanism, and final state
- Enumerate principal backgrounds and classify them (irreducible, reducible,
  instrumental) with expected relative importance
- Propose an event selection approach with justification for the choice
- Define the discriminating variable(s) for the final statistical interpretation
- Specify the blinding variable and signal region boundaries (see Section 4)
- Outline the background estimation strategy per background and identify
  control regions needed
- List anticipated systematic uncertainty categories (experimental, theoretical).
  **Before finalizing the systematic plan,** read the applicable `conventions/`
  document and enumerate every required source. For each source, state whether
  it will be implemented and, if not, why not. This enumeration becomes the
  baseline that Phase 4a reviews against — sources omitted here without
  justification are Category A findings downstream.
- Identify which collision data and simulation samples are needed

**For measurement analyses,** the agent must additionally:
- Define the observable(s) to be measured and their physical interpretation
- Identify the correction/unfolding strategy (bin-by-bin, matrix inversion,
  iterative Bayesian, OmniFold) and what inputs it requires (response matrix,
  MC truth, etc.)
- Survey prior measurements of the same observable — identify published data
  points that will serve as the primary validation target
- Identify what theory predictions or MC generators can be compared to the
  corrected result

**Output artifact:** `STRATEGY.md` — a document covering the above points,
written at the level of an internal analysis note introduction. Quantitative
estimates (cross-sections, expected yields) should cite sources from the
retrieval corpus; order-of-magnitude estimates are acceptable where precision
is unavailable.

**Review:** See Section 6. Strategy review evaluates physics soundness,
completeness of background enumeration, and adequacy of the blinding plan.

---

### Phase 2: Exploration

**Goal:** Characterize the available data, validate the detector model, and
establish the foundation for event selection.

**Inputs:** Strategy, experiment context (via retrieval), data/MC samples.

**The agent must:**
- Inventory available samples (data and simulation): discover file locations,
  tree/branch structure, number of events, cross-sections, luminosity
- Validate data quality: check for pathologies (empty branches, outliers,
  discontinuities in distributions) and document findings
- Apply standard object definitions (retrieved from the experiment corpus) and
  verify agreement between data and simulation in inclusive distributions
- Survey discriminating variables: produce distributions of kinematic observables
  for signal and principal backgrounds, rank by separation power
- Establish baseline event yields after preselection

**PDF build test (independent task).** At any point during or after Phase 2,
run a stub PDF build (`pixi run build-pdf`) to verify the toolchain. This
is an independent task that can run in parallel with Phase 2 work or be
sub-delegated. Create a minimal `phase5_documentation/exec/ANALYSIS_NOTE.md`
stub with a title, one section heading, and one figure reference. Fix any
toolchain issues (missing packages, broken pandoc flags) now — not in
Phase 5.

**Output artifact:** `EXPLORATION.md` — sample inventory, data quality summary,
variable ranking with distributions, preselection cutflow, and data/MC
comparison observations.

**Review:** See Section 6. Exploration review checks sample inventory
completeness, flags data quality issues, and assesses variable survey
thoroughness.

**Data discovery.** The agent should expect to discover the data format at
runtime — branch naming conventions, tree structures, and storage formats vary
across experiments and analyses. To avoid wasting time and memory:

1. **Metadata first.** Inspect tree names, branch names, and types before
   loading any event data (e.g., `uproot.open(f).keys()`, branch dtypes).
2. **Small slice of scalars.** Load ~1000 events of scalar branches first.
   Do not attempt to load all branches (especially jagged/variable-length)
   until you know the schema.
3. **Identify jagged structure.** Determine which branches are variable-length
   before bulk loading — these require awkward-array handling and consume
   more memory.
4. **Document the schema.** The discovered tree/branch structure, event counts,
   and any format quirks are themselves artifact content.

This discovery process is documented in the artifact.

---

### Phase 3: Processing

**Goal:** Implement the analysis approach defined in the Phase 1 strategy.
For searches: define the selection, design control and validation regions,
estimate backgrounds, and validate the background model. For measurements:
define the selection and build the validated correction chain (response
matrix, unfolding, closure tests). The strategy determines which track
applies and what specific deliverables Phase 3 must produce — Phase 3
executes the plan, it does not redesign it.

**Inputs:** Strategy, exploration report, data/MC samples.

**The agent must:**

*Selection:*
- Implement event selection (preselection + final selection or MVA, as
  determined by the strategy and what the data supports)
- **Default to multivariate techniques** (BDT, neural network) when the
  task involves classification in more than one dimension — flavour tagging,
  signal/background separation, event categorization. Rectangular cuts are
  acceptable only for preselection, single-variable selections with clear
  physical motivation, or when the training sample is too small (< ~1000
  events). A BDT with 5 input features trains in seconds; the complexity
  cost is negligible and the performance gain over hand-tuned cuts is
  typically substantial. Reviewers will flag analyses that use multi-
  dimensional rectangular cuts where a trained classifier would be standard
  practice.
- If using multivariate techniques: train, validate (overtraining checks), and
  optimize the classifier. Document feature importance and working point choice.
  - **Train at least one alternative architecture** (e.g., fully connected NN
    if primary is BDT, or vice versa). This is inexpensive and provides a
    genuine cross-check. Report both performances.
  - **When the physics has >2 classes** (e.g., b vs. c vs. light in flavour
    tagging), try multiclass classification — not just binary. Multiclass
    often outperforms chained binary classifiers.
  - **Check data/MC agreement on the classifier output** — if mismodeling is
    visible, investigate input variable cuts or calibration before accepting
    the MVA systematic as-is.
  - **Sub-delegate MVA training** to a sub-agent. Classifier training is a
    self-contained task (hyperparameter tuning, overtraining checks, feature
    selection) that should not consume the main executor's context. See
    §3a.5.1.
- If cut-based: optimize cut values with a figure of merit and document N-1
  distributions.
- Produce the final signal region definition and cutflow with efficiencies.
  **Cutflow counts must be monotonically non-increasing** — if any cut
  increases the event count, something is structurally wrong (e.g., a cut
  applied to the wrong mask, a weight applied incorrectly). This is
  Category A if violated.
- **Every cut must be motivated by a plot.** The artifact must include, for
  each selection cut, the distribution of the cut variable showing signal and
  background. The plot should make visually clear why this cut value was chosen
  — typically one of: "signal only exists above/below this threshold," "data
  quality degrades beyond this point," "this value maximizes purity while
  retaining sufficient statistics," or "this removes a specific background
  while preserving signal efficiency." A cut without a motivating plot is an
  unjustified cut.

*Regions (search analyses):*
- Define control regions enriched in each major background. Document purity and
  the kinematic relationship to the signal region.
- Define validation regions kinematically between control and signal regions for
  closure testing. These must be statistically independent of both CR and SR.

*Background estimation (search analyses):*
- Estimate background yields in SR using the chosen method per background
  (simulation-scaled-from-CR, data-driven, or pure simulation with justification)
- Perform closure tests in validation regions: compare predicted yields
  (extrapolated from CRs, not pure MC) to observation. Document agreement
  quantitatively. A closure test passes when agreement is consistent with
  statistical fluctuations (p-value > 0.05 under the relevant test statistic,
  typically chi2). A test that fails at p < 0.05 is Category A — investigate
  and iterate on the region design or estimation method before proceeding.

*Correction infrastructure (measurement analyses):*

For measurements, Phase 3 builds the correction chain rather than a
background model. The primary deliverable is a working, validated correction
pipeline — not yet the final measurement (systematic evaluation is Phase 4a).

- Produce data/MC comparisons for **all** kinematic variables entering the
  observable, resolved by reconstructed object category. Observable-level
  agreement can mask compensating category-level mismodeling. These plots are
  required evidence that the MC response model is adequate — missing
  category-level validation is Category A for unfolded measurements.
- Construct the response matrix from MC (matched reco/gen events). Report
  matrix properties: dimensions, diagonal fraction, condition number,
  efficiency as a function of the particle-level observable.
- Implement the correction/unfolding chain end-to-end on MC. Run closure
  tests: unfold MC truth through the response and verify recovery within
  statistical precision. Run stress tests: unfold a reweighted truth through
  the nominal response and verify recovery of the reweighted shape.
- Closure test failure (chi2 p-value < 0.05) is Category A — the correction
  chain must close before proceeding.
- Prototype the full chain on data to verify it runs without errors. The
  corrected spectrum at this stage is a working result, not the final
  measurement.
- **Binning must be justified.** Every binning choice (for histograms,
  response matrices, fit templates) must be motivated by one or more of:
  detector resolution (bin width ≥ resolution), statistical precision
  (sufficient events per bin), physics features (bin boundaries at physical
  thresholds). "Default numpy bins" or arbitrary round numbers are not
  justifications. Document the reasoning in the artifact.
- Prepare inputs for Phase 4a systematic evaluation: nominal response matrix,
  selection machinery that can be re-run with varied cuts, alternative MC
  samples if available.

If backgrounds are present (e.g., non-hadronic contamination in an event
shape measurement), Phase 3 builds the background estimation infrastructure
— the inputs, methods, and validation that feed into the Phase 4 statistical
analysis. The flow across phases is: Phase 1 defines how backgrounds will
be estimated, Phase 2 validates whether the approach is feasible with the
available data/MC, Phase 3 implements the estimation machinery and prepares
inputs for inference. The primary Phase 3 deliverable for measurements is
the validated correction chain plus background estimation inputs, not a
final background model. Control regions and validation regions (as described
for searches above) are typically not needed for inclusive measurements
where the signal is the process being measured.

**Workflow pattern.** Phase 3 is iteration-heavy. Follow this progression:

1. **Setup & prototype.** Build the processing pipeline on a small slice
   (~1 file or ~1000 events). Verify it runs end-to-end and produces
   sensible distributions. Register each script as a pixi task.
2. **Full processing.** Run on the full dataset. Produce data/MC comparisons
   for every variable entering the observable or selection. For measurements:
   build the response matrix and correction machinery at this stage.
3. **Inspect & validate.** Systematically review all produced plots — data/MC
   agreement per variable, cutflow yields, closure tests. This is where
   modeling issues must be caught before they propagate to Phase 4.

**Output artifact:** `SELECTION.md` — selection definition, cutflow, MVA
details if applicable, region definitions with purity, background estimates with
uncertainties, closure test results, data/MC comparisons in all regions.

**Sensitivity optimization.** If the expected sensitivity after the initial
selection is insufficient for the physics goal, the agent must systematically
explore alternative approaches before concluding. The agent maintains a
**sensitivity log** (`sensitivity_log.md`) tracking each approach tried, the
figure of merit achieved, and the limiting factor (statistical, systematic,
background modeling).

The exploration should progress through qualitatively different strategies,
not just parameter tuning within one approach:

1. *Optimize the current approach* — tune cuts for S/√B or equivalent
2. *Try a more powerful discriminant* — move from cut-based to BDT, or from
   BDT to a more expressive model (GNN for high-dimensional inputs, etc.)
3. *Try different extraction strategies* — shape fit vs counting experiment,
   mass fit vs classifier score fit, different discriminant variables
4. *Try different signal extraction techniques* — rebinned histograms,
   classifier output reshaping (e.g., flat signal transform), categorization
   by S/B ratio
5. *Revisit region design* — tighter signal region, different background
   decomposition, additional categories

The agent should stop optimizing when:
- The sensitivity meets the physics goal, **or**
- At least 3 materially different approaches have been tried, **and**
- The most recent improvement was marginal (<10% relative to the best
  achieved so far), **and**
- The remaining ideas are increasingly speculative

The sensitivity log is included in the artifact and provides evidence to
reviewers that reasonable alternatives were explored. "We tried X, Y, and Z;
Y performed best because [reason]; further improvements are limited by
[factor]" is a valid and professional conclusion.

**Review:** See Section 6. For searches, selection review focuses on
background modeling fidelity. For measurements, it focuses on correction
chain closure and data/MC validation. Closure test failures are always
Category A.

---

### Phase 4: Statistical Analysis

This is the longest phase, with three distinct sub-phases separated by
gates. Each sub-phase produces its own artifact. **Both measurements and
searches follow the same 4a → 4b → 4c structure.**

#### Phase 4a: Expected Results

**Goal:** Evaluate systematic uncertainties, construct the statistical model,
and compute expected results using Asimov data only.

**Inputs:** Selection report, background estimates, data/MC samples.

**The agent must:**

*Systematics:*
- Evaluate experimental systematic uncertainties as rate and/or shape variations.
  The relevant sources depend on the experiment and analysis — the agent
  determines these from the experiment corpus and the analysis design.
- Evaluate theory systematic uncertainties as rate and/or shape variations
- Quantify the impact of each source on signal and background yields
- Prune negligible sources and document the pruning criterion

*Statistical model:*
- Construct a binned likelihood model with all signal and background samples,
  Asimov data, and systematic uncertainty terms
- Validate the model: verify nuisance parameter pulls are small, the fit
  converges, and the expected results are physically sensible
- Perform signal injection tests: inject signal at known strengths and verify
  the fit recovers them

*Goodness-of-fit:*
- Report **both** chi2/ndf for quick assessment **and** toy-based p-value
  using the saturated model GoF statistic where binned results are involved.
  chi2/ndf ~ 1 is good; >>1 indicates mismodeling; <<1 indicates
  overestimated uncertainties or overfitting.
- For measurements with binned results: use the saturated model as the
  reference for GoF. Generate toys under the null hypothesis and compute
  the p-value. Report the toy distribution alongside the observed test
  statistic.

*Expected results:*
- Compute expected results (limits, significance, or measurement precision)
- Produce pre-unblinding fit diagnostics

**For measurements:** "Expected results" means the result extracted from
MC pseudo-data — not from real data. For extraction measurements (counting,
ratios), see `conventions/extraction.md` for the pseudo-data generation
protocol and required validation checks. Running the extraction on real
data counts in Phase 4a defeats the purpose of the 4a → 4b → 4c staged
validation — it makes 4a and 4c identical.

**Output artifact:** `INFERENCE_EXPECTED.md` — systematic uncertainty table with
impacts, statistical model description, expected results, fit diagnostics, and
signal injection test outcomes.

**For measurement analyses:** the artifact must additionally include:
- The full bin-to-bin covariance matrix (statistical + each systematic source
  separately + total). This is essential for any downstream use of the result
  (theory fits, combinations, reinterpretation). Provide the matrices in both
  the artifact (as tables or heatmap figures) and as machine-readable files
  (NumPy `.npy`, JSON, or CSV).
- Comparison of the corrected result to at least one theory prediction or MC
  generator (e.g., Pythia, Herwig, Sherpa at particle level, or fixed-order
  pQCD where available). Compute a chi2 or p-value using the full covariance
  matrix. If no theory prediction is available, justify why and compare to
  published measurements instead.

**Review:** 4-bot review (Section 6.2). This gates the 10% data validation
(Phase 4b).
The cycle repeats until the arbiter issues PASS.

#### Phase 4b: 10% Data Validation

**Goal:** Reality-check the analysis with a small data subsample and produce
the draft analysis note.

**Inputs:** Phase 4a artifact, statistical model, 10% data subsample.

**The agent must:**
- Select 10% of data using a fixed random seed
- Run the full analysis chain (fit, correction, or extraction) on this subsample
- Evaluate goodness-of-fit, nuisance parameter pulls, impact ranking
- Compare observed and expected results (should be compatible within the large
  statistical uncertainties). **Explicit comparison to Phase 4a** is required:
  overlay 10% observed vs. expected, report pull or chi2, interpret agreement.
- Document any discrepancies and their explanations
- If problems are found, fix them and re-run (without seeing additional data)

**For searches:** This is a partial unblinding — 10% of the signal region data.
**For measurements:** This is a consistency validation — compare the 10% result
to the expected result from Phase 4a. Agreement validates the correction chain
and systematic evaluation on real data before committing to the full dataset.

**For extraction measurements:** The 10% test must include diagnostics
genuinely sensitive to data/MC differences — not just the final extracted
quantity (which is dominated by correlated systematics and insensitive to
the subsample). See `conventions/extraction.md` → "Required validation
checks" → item 5 for the specific diagnostics required.

**Output artifact:** `INFERENCE_PARTIAL.md` — 10% observed results, post-fit
diagnostics, comparison to expected, and assessment of analysis health.

**Draft analysis note:** The agent produces `ANALYSIS_NOTE_DRAFT.md` — the
full analysis note following the AN specification (see
`methodology/analysis-note.md`). **The AN is a single evolving document
across Phases 4b, 4c, and 5.** Phase 4b creates the complete AN with 10%
results as placeholders. Phase 4c updates the numbers to full-data results.
Phase 5 polishes prose, adds final comparisons, and renders the PDF. The
structure, systematic descriptions, cross-checks, and appendices are all
written in 4b — Phases 4c and 5 update results, not structure.

A non-blocking subagent should compile the draft to LaTeX/PDF in parallel
with the review cycle, so the human gate receives a rendered document.

**Review:** 4-bot review (Section 6.2) on the draft analysis note. The
physics, critical, and constructive reviewers evaluate the note as
collaboration reviewers would. The arbiter must PASS before the note goes to
a human. The point: the human should receive a polished product, not a rough
draft.

**Human gate:** After the arbiter passes, the draft note and all phase
artifacts are presented for human review (Section 4.3 for searches, or
equivalent for measurements). The analysis pauses until the human approves
proceeding to full data.

#### Phase 4c: Full Data

**Goal:** Compute final results on the full dataset.

**Inputs:** Phase 4a+4b artifacts, statistical model, full data, human
approval.

**The agent must:**
- Run the full analysis chain on the complete dataset
- Produce post-fit diagnostics: nuisance parameter pulls, impact ranking,
  correlation matrix, goodness-of-fit
- Compare to **both** 10% results (Phase 4b) and expected results (Phase 4a).
  Report consistency quantitatively: pull distributions, chi2, or ratio plots
  for each comparison. Flag any result that disagrees with expected at >2σ or
  disagrees with 10% beyond statistical scaling.
- If results show anomalies (large NP pulls, poor GoF, unexpected signal),
  investigate and document whether these indicate a modeling problem or a
  genuine feature of the data

**Output artifact:** `INFERENCE_OBSERVED.md` — full observed results, post-fit
diagnostics, interpretation, and comparison to partial and expected results.

**Review:** 1-bot review (Section 6.2). Methodology already human-approved.

---

### Phase 5: Documentation

**Goal:** Produce the final analysis note (AN).

**Inputs:** All prior phase artifacts, including observed results. The
draft AN from Phase 4b — Phase 5 updates results, not structure.

**AN specification:** See `methodology/analysis-note.md` for the full AN
specification: required sections, depth calibration, completeness test,
bibliography requirements, and LaTeX compilation. The AN is a single
evolving document — Phase 4b writes it, Phase 4c updates numbers, Phase 5
polishes and finalizes.

**Output artifact:** `ANALYSIS_NOTE.md` (+ compiled PDF) plus `results/`
directory containing machine-readable data tables.

**Review:** See Section 6. Documentation review reads the note as a
collaboration editorial board reviewer would. Reviewers must check
completeness — are all cross-checks documented? Are all systematics
described in sufficient detail? Could a reader reproduce the analysis?

---
