# Phase 2: Exploration

> **Prerequisite:** Phase 1 must be complete. Read `exec/STRATEGY.md` before
> beginning. The method selections, EP assessments, and data preparation
> requirements from Phase 1 are your starting inputs.

You are exploring and preparing the data for a **{{analysis_type}}** analysis
named **{{name}}**.

**Start in plan mode.** Before loading any data, produce a plan: which
datasets to inspect first, what cleaning steps to apply, what features to
engineer, what exploratory analyses to run. Execute after the plan is set.

---

## Output artifact

`exec/EXPLORATION.md` — data cleaning log, feature inventory, exploratory
analysis results, variable ranking by EP contribution, and data readiness
assessment for Phase 3.

## Methodology references

- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/08-coding.md`

---

## Agent profile

Phase 2 uses the data explorer agent. Read the profile before beginning:

| Agent | Profile | Steps |
|-------|---------|-------|
| Data explorer | `.claude/agents/data-explorer.md` | All of Phase 2 |

---

## Step 2.1 — Data Cleaning

**Goal:** Transform Phase 0's acquired data into analysis-ready datasets.
Every cleaning decision must be documented and justified.

**The agent must:**

1. **Inventory all datasets.** Read `data/registry.yaml` and list every
   dataset with its quality verdict from `exec/DATA_QUALITY.md`. For each:
   - Confirm the file exists and is readable
   - Verify row counts match the registry
   - Check column names and types against the registry schema

2. **Handle missing values.** For each variable with missing data:
   - Document the missingness pattern (MCAR, MAR, MNAR if determinable)
   - Choose a strategy: listwise deletion, imputation (specify method),
     or indicator variable for missingness
   - **Never zero-fill missing values.** Zeros and missing are different.
   - Record the fraction of missing data before and after treatment

3. **Handle outliers.** For each numeric variable:
   - Compute summary statistics (mean, median, std, min, max, quantiles)
   - Flag values beyond 3 IQR from median or domain-specific thresholds
   - Decision: winsorize, trim, flag, or retain with justification
   - **Never silently remove outliers.** Every removal is documented.

4. **Validate temporal alignment.** If datasets span different time periods
   or use different temporal granularities:
   - Align to a common temporal index (as specified in STRATEGY.md)
   - Document any interpolation or aggregation applied
   - Flag periods where datasets do not overlap

5. **Validate cross-dataset consistency.** For variables appearing in
   multiple datasets:
   - Compare distributions and summary statistics
   - Investigate discrepancies (different definitions, units, populations)
   - Choose the authoritative source and document why

**Output:** Data cleaning log in EXPLORATION.md:

```markdown
## Data Cleaning Log

| Dataset | Original Rows | Final Rows | Missing Treatment | Outlier Treatment | Notes |
|---------|--------------|------------|-------------------|-------------------|-------|
| ds_001 | 1,245 | 1,198 | 47 rows imputed (median) | 0 removed | 3.8% missing in variable X |
| ds_002 | 850 | 842 | 8 rows dropped (MNAR) | 0 removed | Missing correlated with treatment |
```

---

## Step 2.2 — Feature Engineering

**Goal:** Construct the variables needed for the methods selected in
Phase 1. Raw data rarely matches what causal inference methods require.

**The agent must:**

1. **Construct method-specific variables.** Based on STRATEGY.md:
   - DiD: treatment indicator, post-treatment indicator, interaction term
   - IV: instrument variable (if derived from raw data)
   - Synthetic control: donor pool feature matrix
   - RDD: running variable, treatment assignment variable
   - Propensity score: treatment and covariate matrices
   - Time series: lag variables, differenced series, trend components

2. **Construct derived features.** Variables not directly measured but
   computable from acquired data:
   - Ratios, per-capita measures, growth rates
   - Categorical encodings, binning of continuous variables
   - Interaction terms for hypothesized moderating effects
   - Rolling averages, cumulative sums for temporal patterns

3. **Document every engineered feature:**

   ```markdown
   ## Feature Engineering

   | Feature | Formula / Logic | Source Variables | Purpose |
   |---------|----------------|-----------------|---------|
   | gdp_growth | (GDP_t - GDP_{t-1}) / GDP_{t-1} | ds_001.gdp | DiD outcome variable |
   | treated | 1 if country in treatment group, 0 otherwise | Manual assignment | DiD treatment indicator |
   | post_2015 | 1 if year >= 2015, 0 otherwise | ds_001.year | DiD post-period indicator |
   ```

4. **Validate engineered features.** For each:
   - Check for NaN/Inf values introduced by computation (division by zero, log of negative)
   - Verify the distribution is sensible (no impossible values)
   - Confirm the feature has sufficient variation (not near-constant)

**Output:** Feature inventory table in EXPLORATION.md.

---

## Step 2.3 — Exploratory Analysis

**Goal:** Understand the data before formal analysis. Discover patterns,
validate assumptions, and identify potential problems.

**The agent must:**

1. **Univariate distributions.** For every key variable (outcome, treatment,
   instruments, controls):
   - Histogram or density plot
   - Summary statistics table
   - Normality assessment (if methods assume it)
   - Stationarity assessment (for time series variables)

2. **Bivariate relationships.** For every hypothesized causal edge in the
   Phase 1 DAG:
   - Scatter plot or time series overlay of cause and effect variables
   - Correlation coefficient (and partial correlations controlling for
     obvious confounders)
   - Note: correlation is not causation — these are exploratory, not
     confirmatory

3. **Trend analysis.** For time-varying data:
   - Plot time series of all key variables
   - Identify structural breaks, trend changes, seasonality
   - Flag any concurrent events that could confound causal inference
   - For DiD: preliminary parallel trends visual inspection

4. **Preliminary signal vs. baseline separation.** Based on the causal
   hypotheses from Phase 0:
   - Can you visually distinguish treated vs. control groups?
   - Are pre-treatment trends similar (for DiD)?
   - Is there a visible discontinuity (for RDD)?
   - Do instrument and treatment correlate (for IV)?
   - This is a sanity check, not a formal test.

5. **Assumption pre-checks.** For each method selected in STRATEGY.md,
   run preliminary diagnostic checks:

   | Method | Pre-check |
   |--------|-----------|
   | DiD | Visual parallel trends, pre-treatment outcome comparison |
   | IV | First-stage F-statistic (rule of thumb: F > 10) |
   | RDD | McCrary density test for running variable manipulation |
   | Synthetic control | Pre-treatment MSPE for candidate donors |
   | Regression | Variance inflation factors, residual patterns |
   | Time series | ADF/KPSS stationarity tests, ACF/PACF plots |

**Output:** Exploratory analysis section in EXPLORATION.md with all figures
saved to `figures/phase2/`.

---

## Step 2.4 — Variable Ranking by EP Contribution

**Goal:** Rank all variables by their expected contribution to explaining
the target outcome, guided by the causal DAG.

**The agent must:**

1. **Rank variables by causal role.** Using the DAG from STRATEGY.md:
   - **Primary causal variables** (direct edges to outcome): highest priority
   - **Mediators** (on causal pathways): include but note mediation role
   - **Confounders** (common causes): must control for these
   - **Instruments** (for IV): relevance strength
   - **Colliders** (common effects): do NOT control for these

2. **Empirical ranking.** Complement DAG-based ranking with data-driven
   measures:
   - Univariate association strength (correlation, mutual information)
   - Conditional association after controlling for key confounders
   - For classification tasks: feature importance from a preliminary model

3. **Identify red flags:**
   - Variables with near-zero variation (uninformative)
   - Variables with suspiciously perfect correlation (multicollinearity
     or data error)
   - Variables that change ranking dramatically with/without controls
     (potential confounding or mediation)

4. **Produce a ranked variable table:**

   ```markdown
   ## Variable Ranking

   | Rank | Variable | DAG Role | Association | EP Edge | Include? | Notes |
   |------|----------|----------|-------------|---------|----------|-------|
   | 1 | policy_change | Treatment | 0.45 | A->B (0.47) | Yes | Primary treatment |
   | 2 | gdp_growth | Confounder | 0.38 | confounds A->B | Yes | Must control |
   | 3 | population | Mediator | 0.22 | A->C->B | Conditional | Only if testing mediation |
   ```

**Output:** Variable ranking section in EXPLORATION.md.

---

## Step 2.5 — Data Readiness Assessment

**Goal:** Confirm the data is ready for Phase 3 analysis. This is a soft
gate — it does not block Phase 3 but flags risks.

**The agent must:**

1. **Check method prerequisites.** For each method from STRATEGY.md:
   - Are all required variables available and clean?
   - Do assumption pre-checks pass (from Step 2.3)?
   - Is sample size adequate for the planned method?

2. **Summarize readiness per causal edge:**

   | Edge | Method | Data Ready? | Assumptions OK? | Risk Level |
   |------|--------|------------|-----------------|------------|
   | A->B | DiD | Yes | Parallel trends: marginal | MEDIUM |
   | C->B | IV | Yes | F-stat = 14.2 (adequate) | LOW |

3. **Flag method pivots.** If exploratory analysis reveals that a planned
   method's assumptions are violated:
   - State which assumption fails and the evidence
   - Recommend an alternative method
   - Note: this does not require re-doing Phase 1. Document the pivot
     in the experiment log and proceed.

4. **Carry forward data quality warnings.** Every warning from
   `exec/DATA_QUALITY.md` that affects Phase 3 must be restated here.

**Output:** Data readiness assessment section in EXPLORATION.md.

---

## EXPLORATION.md structure

The final artifact must follow this structure:

```markdown
# Data Exploration: {{name}}

## 1. Data Cleaning Log
[Step 2.1 output]

## 2. Feature Engineering
[Step 2.2 output: feature inventory table]

## 3. Exploratory Analysis
[Step 2.3 output: distributions, trends, preliminary checks]

## 4. Variable Ranking
[Step 2.4 output: ranked variable table]

## 5. Data Readiness Assessment
[Step 2.5 output: readiness per edge, method pivots if any]

## 6. Figures Index
[List of all figures in figures/phase2/ with descriptions]
```

---

## Rules

- **Prototype on subsets first.** For large datasets, run initial
  exploration on a random sample (~1000 rows). Scale to full data only
  after validating the approach.
- **Save all figures.** Every plot goes to `figures/phase2/` with a
  descriptive filename. Inline references in EXPLORATION.md.
- **Append to the experiment log.** Document every material decision:
  why a cleaning strategy was chosen, what unexpected patterns were found,
  what assumption checks revealed.
- **Never modify raw data.** All transformations produce new files in
  `data/processed/`. Raw data in `data/raw/` is immutable.
- **Use pixi for all code execution.** `pixi run py script.py` — never
  bare `python`.

---

## Review

**Self-review.** Phase 2 uses self-review only (no external review for
exploration). Explicitly check:

- [ ] Data cleaning log is complete for every dataset?
- [ ] All engineered features are documented with formula and source?
- [ ] Exploratory plots cover all key variables and causal edges?
- [ ] Assumption pre-checks run for every planned method?
- [ ] Variable ranking reflects DAG structure?
- [ ] Data readiness assessment covers every Phase 3 causal edge?
- [ ] Experiment log updated with all material decisions?
- [ ] No raw data files were modified?

Write findings to `review/REVIEW_NOTES.md`.
