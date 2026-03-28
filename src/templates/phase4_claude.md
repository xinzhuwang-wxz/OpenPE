# Phase 4: Projection

> **Phase 4: Projection** forward-projects from Phase 3's established causal
> relationships to endgame, using scenario simulation, sensitivity analysis,
> and convergence detection.

You are running Phase 4 for a **{{analysis_type}}** analysis named
**{{name}}**.

**Start in plan mode.** Before writing any code, produce a plan: what
scenarios you will simulate, what sensitivity ranges you will test, what
convergence criteria you will apply, and what the artifact structure will be.
Execute after the plan is set.

---

## Input requirements

Phase 4 depends on completed Phase 3 artifacts. Before beginning, verify:

1. `exec/ANALYSIS.md` exists with established causal relationships
2. Every causal edge has a post-refutation label:
   - `DATA_SUPPORTED` — survived refutation testing with quantitative evidence
   - `CORRELATION` — statistical association found but causation not established
   - `HYPOTHESIZED` — not yet testable with available data
   - `REFUTED` — failed refutation testing (excluded from projection)
3. EP values are post-analysis (not Phase 0 qualitative estimates)
4. Uncertainty distributions are available for each causal parameter

If any of these are missing, halt and request Phase 3 completion.

---

## Output artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| **PROJECTION.md** | `exec/PROJECTION.md` | Scenario definitions, simulation results, sensitivity rankings, convergence classification, EP decay analysis |
| **Figures** | `figures/` | EP decay chart, scenario comparison, sensitivity tornado diagram |

All three figures and PROJECTION.md must exist before Phase 5 can begin.

---

## Agent profile

Phase 4 uses the projector agent. Read the profile before beginning:

| Agent | Profile | Steps |
|-------|---------|-------|
| Projector agent | `.claude/agents/projector-agent.md` | 4.1 – 4.4 |

---

## Step 4.1 — Scenario Simulation

**Goal:** Monte Carlo sampling from causal parameter uncertainty distributions
to generate forward projections under multiple scenarios.

**The agent must:**

1. **Extract parameter distributions.** For each DATA_SUPPORTED and
   CORRELATION edge from Phase 3, extract the point estimate and uncertainty
   distribution (Gaussian, log-normal, or empirical — use whatever the data
   supports). HYPOTHESIZED edges use wide uniform priors.

2. **Define at least 3 scenarios:**

   | Scenario | Definition | Purpose |
   |----------|------------|---------|
   | **Baseline** | All parameters at central values; exogenous factors follow current trends | Most likely trajectory |
   | **Optimistic** | Controllable levers at favorable extremes; exogenous factors at +1σ favorable | Best plausible outcome |
   | **Pessimistic** | Controllable levers at unfavorable extremes; exogenous factors at -1σ unfavorable | Worst plausible outcome |

   Additional scenarios are encouraged when specific fork conditions exist
   (e.g., "Policy X enacted" vs. "Policy X not enacted").

3. **Run Monte Carlo simulation.** For each scenario:
   - Draw ≥1000 samples from the joint parameter distribution
   - Propagate through the causal DAG to compute the target variable trajectory
   - Record the full distribution of outcomes at each projection timestep
   - Compute mean, median, and 68%/95% confidence intervals

4. **Document assumptions explicitly.** Every scenario must list:
   - Which parameters are varied and their distributions
   - What external conditions are assumed (held constant vs. trending)
   - What interactions between parameters are modeled vs. assumed independent

**Output:** Scenario definition table and simulation results in PROJECTION.md.

---

## Step 4.2 — Sensitivity Analysis

**Goal:** Quantify the impact of each causal lever on the projected outcome
and rank them by importance.

**The agent must:**

1. **One-at-a-time sensitivity.** For each causal parameter:
   - Hold all others at baseline values
   - Vary this parameter by ±1σ (or ±20% if no uncertainty estimate exists)
   - Record the change in the target variable at each projection timestep

2. **Rank parameters by impact magnitude.** At the primary projection
   horizon, sort parameters by absolute impact on the target variable.

3. **Classify each parameter:**

   | Category | Definition | Implication |
   |----------|------------|-------------|
   | **Controllable** | Can be influenced by a decision-maker (policy, investment, strategy) | Actionable lever — highlight in recommendations |
   | **Exogenous** | Outside decision-maker influence (demographics, global markets, natural forces) | Risk factor — monitor but cannot directly influence |
   | **Partially controllable** | Influence possible but limited (market sentiment, cultural trends) | Indirect lever — influence through secondary mechanisms |

4. **Generate tornado diagram.** Horizontal bar chart showing parameter
   impact ranked from largest to smallest. Color-code by controllability.
   Save to `figures/sensitivity_tornado.pdf`.

5. **Interaction check.** For the top 3 parameters by impact, test pairwise
   interactions: vary two simultaneously and compare to sum of individual
   effects. Report any nonlinear interactions exceeding 10% of additive
   expectation.

**Output:** Sensitivity rankings, parameter classifications, and tornado
diagram in PROJECTION.md and figures/.

---

## Step 4.3 — Endgame Convergence Detection

**Goal:** Classify the projection outcome into one of four endgame categories
based on scenario behavior.

**The agent must:**

1. **Compare scenario trajectories.** Analyze the spread of scenario outcomes
   over the projection horizon. Use the coefficient of variation (CV) of
   scenario endpoints as the primary metric.

2. **Classify into exactly one category:**

   | Category | Detection criteria | Interpretation |
   |----------|-------------------|----------------|
   | **Robust endgame** | Scenarios converge: CV < 0.15 at projection horizon; confidence bands narrow over time | Outcome is largely independent of assumptions; high confidence in direction |
   | **Fork-dependent outcome** | Scenarios diverge: CV > 0.5; identifiable binary conditions separate trajectories | Outcome depends on specific future events; identify and name the fork conditions |
   | **Equilibrium endgame** | Steady state exists: rate of change approaches zero; scenarios oscillate around a common attractor | System reaches natural balance; identify the equilibrium value and basin of attraction |
   | **Unstable trajectory** | Runaway behavior: monotonically accelerating divergence; no bounding mechanism detected | System lacks natural constraints; identify any theoretical or physical bounds that limit runaway |

3. **For fork-dependent outcomes:** Explicitly name each fork condition,
   estimate its probability, and describe the divergent trajectories.

4. **For unstable trajectories:** Search for bounding constraints — physical
   limits, resource constraints, regulatory ceilings — that would eventually
   halt runaway behavior. If bounds exist, estimate when they bind.

5. **Document the classification with evidence.** Quote specific numerical
   results from the Monte Carlo simulation that support the classification.

**Output:** Endgame classification with supporting evidence in PROJECTION.md.

---

## Step 4.4 — EP Decay Visualization

**Goal:** Produce the core projection figure showing how Explanatory Power
confidence decays with projection distance.

**The agent must:**

1. **Define EP decay bands.** Map projection distance to confidence:

   | Projection distance | Confidence level | EP multiplier | Rationale |
   |--------------------|--------------------|---------------|-----------|
   | Phase 3 findings (historical) | HIGH | 1.0 | Empirically tested against data |
   | Near-term (1–3 years) | MEDIUM | 0.7 | Parameter stability assumption holds |
   | Mid-term (3–10 years) | LOW-MEDIUM | 0.4 | Structural changes possible |
   | Long-term (10+ years) | LOW (scenario-dependent) | 0.2 | Multiple regime changes likely |

   These multipliers are defaults. Adjust based on domain volatility — fast-
   moving domains (technology, markets) decay faster; slow-moving domains
   (demographics, geology) decay slower. Document any adjustments.

2. **Generate EP decay chart.** Fan chart showing:
   - X-axis: time from present
   - Y-axis: EP-weighted confidence in the projected target variable
   - Central line: baseline scenario projection
   - Inner band (68% CI): near-term uncertainty
   - Outer band (95% CI): full uncertainty including scenario divergence
   - Vertical dashed lines marking confidence tier boundaries
   - Save to `figures/ep_decay_chart.pdf`

3. **Generate scenario comparison figure.** Line chart showing:
   - Each scenario trajectory as a separate line
   - Shaded uncertainty bands per scenario
   - Key fork points annotated
   - Save to `figures/scenario_comparison.pdf`

4. **Annotate the EP decay chart** with the endgame classification from
   Step 4.3 and any fork conditions or bounding constraints.

**Output:** Figures in figures/; EP decay analysis in PROJECTION.md.

---

## EP Projection Guidance

EP values from Phase 3 are the anchor. Forward projection degrades EP
according to the decay schedule above. The key principle:

**Never project with more confidence than the underlying data supports.**

- If a causal edge is CORRELATION (not DATA_SUPPORTED), its projection
  contribution decays at 2x the standard rate.
- If a causal edge is HYPOTHESIZED, it contributes only to scenario spread,
  not to the central projection.
- Joint_EP along projection chains uses the same multiplicative rule as
  analysis chains: Joint_EP = EP_1 × EP_2 × ... × EP_n × decay_multiplier.
- Apply the same truncation thresholds from Phase 0:
  - Hard truncation at Joint_EP < 0.05
  - Soft truncation at Joint_EP < 0.15

---

## Methodology references

- Architecture design: `docs/superpowers/specs/2026-03-28-slop-fp-architecture-design.md` (Sections 2-5)
- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (4-bot review)

---

## Non-negotiable rules

1. **Never project beyond the data.** Projections are scenario-conditional
   extrapolations, not predictions. Every projection artifact must state this
   explicitly. The EP decay chart is the visual embodiment of this principle.

2. **Never present a single scenario as "the answer."** Always present the
   full scenario range. The baseline is the most likely, not the only outcome.

3. **Always classify controllable vs. exogenous.** The value of projection
   is actionability. If the user cannot distinguish what they can influence
   from what they must accept, the projection has failed.

4. **Document all assumptions.** Every parameter held constant, every trend
   extrapolated, every distribution assumed — all must be explicit in
   PROJECTION.md. Hidden assumptions are Category A findings in review.

5. **Carry forward data quality caveats.** Phase 0 data quality warnings
   propagate through projection. LOW-quality data sources widen uncertainty
   bands; they do not get laundered into precise projections.

6. **Append to the experiment log.** Document scenario design choices,
   sensitivity analysis decisions, convergence classification rationale,
   and any EP decay adjustments.

---

## Review

**4-bot review** — see `methodology/06-review.md` for protocol.

Reviewers evaluate:
- Are scenarios genuinely different, or minor parameter variations?
- Is the sensitivity analysis complete — are all material causal levers tested?
- Is the endgame classification supported by the Monte Carlo evidence?
- Does the EP decay chart accurately represent confidence degradation?
- Are all assumptions documented and reasonable?
- Do data quality caveats from Phase 0 properly widen uncertainty bands?
- Are controllable vs. exogenous levers correctly classified?

Write findings to `review/REVIEW_NOTES.md`.
