# Phase 3: Analysis

> **Prerequisite:** Phase 2 must be complete. Read `exec/STRATEGY.md` and
> `exec/EXPLORATION.md` before beginning. The method selections, EP
> assessments, cleaned data, and assumption pre-checks are your inputs.

You are implementing the core analysis for a **analysis** analysis
named **china_double_reduction_education**.

**This is the most complex phase.** It contains the causal testing pipeline
(the heart of OpenPE), statistical model construction, and uncertainty
quantification. It is split into two context blocks for subagent delegation:

- **Steps 3.1-3.5** (Signal extraction through sub-chain expansion):
  delegated to the analyst agent
- **Steps 3.6-3.7** (Statistical model and uncertainty quantification):
  delegated to the verifier agent

**Start in plan mode.** Before writing any code, produce a plan: what
scripts you will write, what causal tests you will run, what the artifact
structure will be. Execute after the plan is set.

---

## Output artifact

`exec/ANALYSIS.md` — signal extraction results, baseline estimation,
causal test results with classifications, EP propagation graph, statistical
model specification, and uncertainty quantification.

## Methodology references

- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (4-bot review)
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/08-coding.md`

---

## Agent profiles

Phase 3 uses two specialized agents in sequence:

| Agent | Profile | Steps |
|-------|---------|-------|
| Analyst | `.claude/agents/analyst.md` | 3.1, 3.2, 3.3, 3.4, 3.5 |
| Verifier | `.claude/agents/verifier.md` | 3.6, 3.7 |

The orchestrator delegates Steps 3.1-3.5 to the analyst agent as one
invocation, then delegates Steps 3.6-3.7 to the verifier agent as a
second invocation.

---

## Step 3.1 — Signal Extraction

**Goal:** Identify patterns in the data consistent with the causal
hypotheses from the DAG. This is descriptive, not yet causal.

**The agent must:**

1. **Define "signal" for each causal edge.** Based on the DAG and method
   selection from STRATEGY.md:
   - What observable pattern would constitute evidence for this edge?
   - What is the expected direction and approximate magnitude?
   - What temporal or spatial signature should it produce?

2. **Extract preliminary effect estimates.** For each primary causal edge,
   run the primary method (from STRATEGY.md) in a preliminary form:
   - Point estimate of the causal effect
   - Preliminary standard error
   - Visual presentation (e.g., event study plot for DiD, RD plot for RDD)

3. **Document the signal.** For each edge:

   ```markdown
   ### Signal: Edge A -> B
   - **Expected pattern:** Policy introduction reduces outcome by 10-20%
   - **Observed pattern:** Outcome drops 14.2% post-treatment (SE = 3.1%)
   - **Visual:** See figures/phase3/signal_A_B.png
   - **Preliminary assessment:** Signal present, consistent with hypothesis
   ```

**Output:** Signal extraction section in ANALYSIS.md.

---

## Step 3.2 — Baseline Estimation

**Goal:** Construct the null-hypothesis model — what would have happened
in the absence of the hypothesized causal effect.

**The agent must:**

1. **Construct a baseline for each causal edge.** The baseline depends on
   the method:

   | Method | Baseline construction |
   |--------|---------------------|
   | DiD | Control group trajectory extrapolated to treatment group |
   | Synthetic control | Weighted combination of donor units |
   | IV | Reduced-form relationship without instrument |
   | RDD | Polynomial fit on untreated side of cutoff |
   | ITS | Pre-intervention trend extrapolation |
   | Regression | Predicted outcome with treatment set to zero |
   | Bayesian structural | Counterfactual posterior from structural model |

2. **Validate the baseline.** The baseline must be credible:
   - Does it fit the pre-treatment / pre-intervention data well?
   - Is it stable under reasonable perturbations?
   - Does it produce sensible out-of-sample predictions?

3. **Quantify signal-baseline separation.** For each edge:
   - Difference between observed data and baseline prediction
   - Significance of the separation (t-statistic, p-value, or posterior
     probability as appropriate)
   - Effect size metric (Cohen's d, percentage change, or domain-appropriate)

**Output:** Baseline estimation section in ANALYSIS.md with baseline
vs. observed comparison figures.

---

## Step 3.3 — Causal Testing Pipeline

> **This is the heart of OpenPE.** Every hypothesized causal edge undergoes
> a rigorous testing battery. No edge is accepted as causal without passing
> this pipeline.

**For each causal edge classified as "full analysis" in STRATEGY.md, the
agent must execute the following sequence:**

### 3.3.1 — Formalize the Causal Model

- Write down the DAG for this edge, including all confounders, mediators,
  and instruments identified in Phase 1
- State the causal estimand precisely (ATE, ATT, LATE, CATE, etc.)
- State all identifying assumptions explicitly

### 3.3.2 — Identify the Estimand

- From the DAG, derive the statistical estimand using do-calculus or
  backdoor/frontdoor criteria
- State what must be conditioned on and what must not be
- If the estimand is not identifiable from the DAG, document why and
  state what additional assumptions are needed

### 3.3.3 — Estimate the Causal Effect

- **Primary method:** Run the primary method from STRATEGY.md
- **Secondary method:** Run at least one secondary method
- Both methods must produce: point estimate, confidence interval (or
  credible interval), and p-value (or posterior probability)
- Compare results across methods. If they substantially disagree (>50%
  difference in point estimates or different sign), investigate and
  document the discrepancy.

### 3.3.4 — Run 3 Refutation Tests

Every causal edge must pass a battery of 3 refutation tests. These are
designed to stress-test the causal claim:

| Test | What it does | How to implement |
|------|-------------|-----------------|
| **Placebo treatment** | Apply a fake treatment at a different time/place where no effect should exist | Re-run the estimation with a placebo treatment date (e.g., 2 years before actual treatment) or a placebo treatment group. The estimate should be near zero and not statistically significant. |
| **Random common cause** | Add a randomly generated confounder to the model | Generate a random variable, add it as a control. If the estimate changes substantially (>10%), the original model may be sensitive to unobserved confounding. |
| **Data subset** | Re-estimate on a random subset of the data | Randomly drop 20-30% of observations and re-estimate. The estimate should remain similar in magnitude and significance. Tests sensitivity to influential observations. |

**Each test produces a PASS / FAIL verdict:**
- **PASS:** Result is consistent with causal interpretation (placebo
  estimate near zero; random cause does not change estimate; subset
  estimate is stable)
- **FAIL:** Result is inconsistent with causal interpretation

### 3.3.5 — Classify the Edge

Use the refutation test results to classify each edge:

| Refutation Results | Classification | Meaning |
|-------------------|---------------|---------|
| 3/3 PASS | **DATA_SUPPORTED** | Strong evidence for causal relationship. Report as a finding. |
| 2/3 PASS | **CORRELATION** | Evidence suggestive but not robust. Report with prominent caveats. |
| 1/3 PASS | **HYPOTHESIZED** | Insufficient evidence. Causal claim cannot be sustained from this data. Revert to the prior hypothesis status from Phase 0. |
| 0/3 PASS | **DISPUTED** | Evidence contradicts the hypothesis. The data actively argues against this causal edge. |

**Document every test result:**

```markdown
### Causal Test: Edge A -> B

| Test | Result | Details |
|------|--------|---------|
| Placebo treatment | PASS | Placebo estimate: 0.02 (SE 0.04), p=0.61 |
| Random common cause | PASS | Estimate changed from 0.142 to 0.138 (2.8% change) |
| Data subset | PASS | Subset estimate: 0.131 (SE 0.039), original: 0.142 (SE 0.031) |

**Classification: DATA_SUPPORTED**
**Primary estimate:** 0.142 (95% CI: 0.081 to 0.203)
**Secondary estimate:** 0.128 (95% CI: 0.065 to 0.191)
```

**For "lightweight assessment" edges** (0.15 <= Joint_EP < 0.30): Run only
the primary method. No refutation battery. Classify as CORRELATION at best.
Document as "assessed but not fully tested."

**Output:** Complete causal test results for every edge in ANALYSIS.md.

---

## Step 3.4 — EP Update

**Goal:** Use the causal test results to update EP values for every node
and edge in the DAG.

**The agent must:**

1. **Update truth values based on classification:**

   | Classification | Truth update |
   |---------------|-------------|
   | DATA_SUPPORTED | truth = max(0.8, Phase 1 truth + 0.2) |
   | CORRELATION | truth = Phase 1 truth (unchanged) |
   | HYPOTHESIZED | truth = min(0.3, Phase 1 truth - 0.1) |
   | DISPUTED | truth = 0.1 |

2. **Update relevance values.** If the estimated effect size differs
   substantially from Phase 1 expectations, adjust relevance:
   - Effect larger than expected: increase relevance (cap at 0.9)
   - Effect smaller than expected: decrease relevance (floor at 0.1)
   - Effect near zero: relevance drops to 0.1

3. **Recompute EP = truth x relevance** for every edge.

4. **Recompute Joint_EP along all chains.** Apply truncation thresholds:
   - Hard truncation (Joint_EP < 0.05): mark chain as resolved
   - Soft truncation (0.05 <= Joint_EP < 0.15): no further analysis

5. **Produce an EP propagation table:**

   ```markdown
   ## EP Propagation

   | Edge | Phase 0 EP | Phase 1 EP | Phase 3 EP | Classification | Change Reason |
   |------|-----------|-----------|-----------|---------------|---------------|
   | A->B | 0.47 | 0.42 | 0.62 | DATA_SUPPORTED | Refutation tests passed; effect confirmed |
   | C->B | 0.21 | 0.18 | 0.09 | DISPUTED | Placebo test failed; likely confounded |
   ```

6. **Render the final Phase 3 DAG** in mermaid format with updated EP
   values and classification labels on each edge.

**Output:** EP propagation section in ANALYSIS.md with comparison table
and updated DAG.

---

## Step 3.5 — Sub-Chain Expansion Decision

**Goal:** Determine whether any causal edges warrant deeper investigation
through a sub-analysis.

**The agent must:**

1. **Evaluate expansion criteria.** A sub-chain expansion is justified when
   ALL of the following hold:
   - Edge EP > 0.3 after Phase 3 update
   - Chain Joint_EP > 0.15
   - The edge represents a compound mechanism that could be decomposed
     into finer-grained causal steps
   - Decomposition would materially change the analysis conclusion or
     provide actionable detail

2. **For each expansion candidate:**
   - Define the sub-DAG (decomposition of the compound edge)
   - Estimate the additional data requirements
   - Estimate whether existing data is sufficient or new acquisition needed
   - Assess whether the expansion is worth the analytical cost

3. **Decision for each candidate:**
   - **EXPAND:** Scaffold a sub-analysis (create a sub-directory with its
     own Phase 0-3 cycle). Document the handoff in ANALYSIS.md.
   - **DEFER:** Note as "recommended for future work" with justification.
   - **SKIP:** Expansion not warranted. State why.

4. **If expanding:** The sub-analysis inherits data from the parent but
   runs its own Phase 0-3 cycle focused on the decomposed edge. The
   parent analysis continues independently — it does not wait for
   sub-analysis completion.

**Output:** Sub-chain expansion decision section in ANALYSIS.md.

---

## Context Split: Steps 3.6-3.7 (Verifier Agent)

> **The orchestrator now delegates to the verifier agent.** Steps 3.6 and
> 3.7 run as a separate subagent invocation. The verifier reads the
> analyst's output from Steps 3.1-3.5 and constructs the statistical model
> and uncertainty quantification.

---

## Step 3.6 — Statistical Model Construction

**Goal:** Build a formal statistical model that encapsulates the causal
findings and enables rigorous inference.

**The verifier agent must:**

1. **Specify the likelihood function.** Based on the causal test results
   and method outputs:
   - Define the probability model for the observed data
   - Include all causal effect parameters (one per tested edge)
   - Include nuisance parameters for systematic uncertainties
   - Specify priors (for Bayesian) or constraint terms (for frequentist)

2. **Parameterize systematic uncertainties.** For each systematic source
   identified in STRATEGY.md:
   - Define a nuisance parameter
   - Specify its constraint (Gaussian, log-normal, uniform, or data-driven)
   - Specify how it affects the likelihood (additive, multiplicative,
     shape variation)

3. **Compute expected results.** Before finalizing:
   - What is the expected sensitivity given the data?
   - What precision is achievable?
   - Are the constraints on nuisance parameters reasonable?

4. **Run signal injection tests.** Inject a known artificial signal and
   verify that the model recovers it:
   - Inject at the observed effect size: does the model recover it within
     1 sigma?
   - Inject at 2x the observed effect size: does the model respond
     proportionally?
   - Inject at zero (null): does the model correctly return a null result?

   Signal injection failures indicate model mis-specification and must be
   resolved before proceeding.

5. **Document the model:**

   ```markdown
   ## Statistical Model

   ### Likelihood
   L(data | θ, ν) = [specification]

   ### Parameters of Interest
   | Parameter | Description | Estimate | 95% CI |
   |-----------|------------|----------|--------|
   | θ_AB | Causal effect A->B | 0.142 | [0.081, 0.203] |

   ### Nuisance Parameters
   | Parameter | Systematic Source | Constraint | Impact |
   |-----------|-----------------|------------|--------|
   | ν_1 | Measurement error in X | Gaussian(0, 0.05) | ±3% on θ_AB |

   ### Signal Injection Tests
   | Injected | Recovered | Within 1σ? |
   |----------|-----------|------------|
   | 0.142 | 0.139 ± 0.033 | Yes |
   | 0.284 | 0.271 ± 0.041 | Yes |
   | 0.000 | 0.003 ± 0.029 | Yes |
   ```

**Output:** Statistical model section in ANALYSIS.md.

---

## Step 3.7 — Uncertainty Quantification

**Goal:** Produce final results with complete uncertainty breakdown. Every
result in OpenPE carries four numbers: central value, statistical
uncertainty, systematic uncertainty, and total uncertainty.

**The verifier agent must:**

1. **Statistical uncertainty.** From the likelihood or estimation procedure:
   - Frequentist: standard errors, confidence intervals
   - Bayesian: posterior standard deviation, credible intervals
   - Bootstrap: bootstrap standard error and percentile intervals
   - Report at 68% (1 sigma) and 95% (2 sigma) levels

2. **Systematic uncertainty.** For each nuisance parameter:
   - Vary by ±1 sigma (or use profile likelihood)
   - Record the shift in the parameter of interest
   - Combine systematics in quadrature (or via the full covariance matrix
     if correlations are significant)

3. **Total uncertainty.** Combine statistical and systematic:
   - Total = sqrt(statistical^2 + systematic^2) for uncorrelated sources
   - Use the full covariance matrix if correlations exist
   - Report the dominant uncertainty source

4. **Produce the final results table:**

   ```markdown
   ## Final Results

   | Parameter | Central Value | Stat. Unc. | Syst. Unc. | Total Unc. | Classification |
   |-----------|--------------|-----------|-----------|-----------|---------------|
   | Effect A->B | 0.142 | ±0.031 | ±0.018 | ±0.036 | DATA_SUPPORTED |
   | Effect C->B | -0.008 | ±0.025 | ±0.012 | ±0.028 | DISPUTED |
   ```

5. **Produce an uncertainty breakdown table** for the primary result:

   ```markdown
   ### Uncertainty Breakdown: Effect A->B

   | Source | Type | ±Shift | Fraction of Total |
   |--------|------|--------|-------------------|
   | Sample size | Statistical | 0.031 | 74% |
   | Measurement error in X | Systematic | 0.012 | 11% |
   | Model specification | Systematic | 0.009 | 6% |
   | Missing data treatment | Systematic | 0.008 | 5% |
   | Temporal aggregation | Systematic | 0.005 | 2% |
   | Other | Systematic | 0.004 | 2% |
   ```

6. **Sanity checks:**
   - Is total uncertainty smaller than the effect size? (If not, the
     result is not significant.)
   - Is systematic uncertainty dominant? (If so, more data will not help —
     better methods or data quality is needed.)
   - Are any single systematics dominant? (If so, flag for future work.)

**Output:** Uncertainty quantification section in ANALYSIS.md.

---

## ANALYSIS.md structure

The final artifact must follow this structure:

```markdown
# Analysis: china_double_reduction_education

## 1. Signal Extraction
[Step 3.1 output: signal definition and preliminary estimates per edge]

## 2. Baseline Estimation
[Step 3.2 output: baseline construction and signal-baseline separation]

## 3. Causal Testing Pipeline
[Step 3.3 output: for each edge — DAG, estimand, estimates, refutation
tests, classification]

## 4. EP Propagation
[Step 3.4 output: EP update table, Phase 3 DAG with classifications]

## 5. Sub-Chain Expansion Decisions
[Step 3.5 output: expansion candidates and decisions]

## 6. Statistical Model
[Step 3.6 output: likelihood, parameters, signal injection tests]

## 7. Uncertainty Quantification
[Step 3.7 output: final results table, uncertainty breakdown]

## 8. Summary of Findings
[One-paragraph summary: what causal claims are supported, what is
disputed, what remains hypothesized, what are the dominant uncertainties]
```

---

## Non-negotiable rules

1. **Every causal claim must survive the refutation battery.** An edge
   classified as DATA_SUPPORTED without all 3 refutation tests passing is
   a Category A finding. No exceptions.

2. **At least 2 estimation methods per primary edge.** If methods
   substantially disagree, the edge cannot be classified higher than
   CORRELATION regardless of refutation results.

3. **Every result carries 4 numbers.** Central value, statistical
   uncertainty, systematic uncertainty, total uncertainty. A result without
   uncertainty quantification is not a result — it is a guess.

4. **EP updates must be mechanical.** Use the classification-to-truth
   mapping table in Step 3.4. Do not subjectively override EP values.

5. **Never fabricate significance.** If the effect is not significant, say
   so. An honest null result (DISPUTED or HYPOTHESIZED classification) is a
   valid and valuable finding. Do not p-hack, do not selectively report
   refutation tests, do not cherry-pick subsets.

6. **Signal injection must pass.** If the statistical model fails signal
   injection tests, the model is wrong. Fix it before reporting results.

7. **Sub-chain expansion has strict criteria.** EP > 0.3 AND Joint_EP >
   0.15 AND decomposition materially changes conclusions. Do not expand
   every interesting edge — this creates unbounded recursion.

8. **Carry forward all warnings.** Data quality warnings from Phase 0,
   assumption concerns from Phase 2, and method caveats from Phase 1 must
   all appear in the final ANALYSIS.md. Nothing is silently dropped.

9. **Append to the experiment log.** Document every material decision:
   why a refutation test passed or failed, why an edge was classified a
   certain way, what signal injection revealed, what sub-chain expansions
   were considered and why.

---

## Review

**4-bot review** — see `methodology/06-review.md` for protocol.

Reviewers evaluate:
- Is every primary causal edge tested with the full refutation battery?
- Are at least 2 estimation methods used per primary edge? Do they agree?
- Are refutation test implementations correct? (Placebo treatment at
  sensible time/place? Random cause truly random? Subset truly random?)
- Are edge classifications consistent with the refutation results and
  the decision tree?
- Are EP updates mechanical and traceable?
- Is the statistical model well-specified? Do signal injection tests pass?
- Does every result carry complete uncertainty quantification (4 numbers)?
- Are all prior-phase warnings carried forward?
- Is the experiment log complete?

Write findings to `review/REVIEW_NOTES.md`.
