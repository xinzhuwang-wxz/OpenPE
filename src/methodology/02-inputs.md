## 2. Inputs

An analysis begins with a structured input that defines the question,
the domain context, and what data the agent has to work with.

### 2.1 Analysis Question

A brief natural-language description of the analytical goal. Examples:

> What is the causal effect of minimum wage increases on youth unemployment
> in OECD countries over the period 2000–2023?

> How sensitive is US county-level life expectancy to healthcare spending
> after controlling for income, education, and urbanization?

> Forecast quarterly GDP growth for the Eurozone under three fiscal policy
> scenarios through 2027.

The question need not specify methodology. It states the analytical target
and any constraints (dataset, time range, geography, outcome variable).

### 2.2 Input Modes

OpenPE supports three input modes. The mode determines what the agent
must acquire versus what it receives.

#### Mode A: Question Only

The user provides only the question. The agent must:
1. Decompose the question into measurable sub-questions
2. Identify required data sources (public APIs, databases, web scraping)
3. Acquire the data programmatically (Phase 0)
4. Document provenance for every acquired dataset

This is the most autonomous mode. The agent bears full responsibility for
data selection and must justify every source choice in the strategy artifact.

#### Mode B: Question + User Data

The user provides the question and one or more datasets. The agent must:
1. Inventory the provided data (schema, completeness, quality)
2. Assess whether the data is sufficient for the question
3. Identify gaps and propose supplementary data sources if needed
4. Document which findings depend on user-provided vs. acquired data

The user places data files in the analysis `data/` directory (or configures
`data_dir` in `.analysis_config` to point to an external location). The
agent discovers the data at runtime — it should expect to learn the schema
by inspection, not from prior knowledge.

#### Mode C: Question + User Hypotheses

The user provides the question, optionally data, and explicit hypotheses
to test. The agent must:
1. Formalize each hypothesis as a testable statistical statement
2. Define the null and alternative for each
3. Identify potential confounders that could invalidate each test
4. Structure the analysis to test hypotheses independently where possible

This mode constrains the analysis scope — the agent tests what the user
asks, rather than exploring freely. The agent should still flag obvious
gaps ("your hypotheses do not address [confounder X], which may bias
results") but does not redirect the analysis without user approval.

### 2.3 Analysis Configuration

Every analysis has an `analysis_config.yaml` in the root directory. This
is the structured interface between the user and the agent.

```yaml
# analysis_config.yaml — structured input for OpenPE analysis

question: |
  What is the causal effect of minimum wage increases on youth
  unemployment in OECD countries (2000–2023)?

domain: labor_economics
input_mode: A  # A = question only, B = question + data, C = question + hypotheses

# Epistemic probability thresholds — governs convergence criteria
ep_thresholds:
  high_confidence: 0.85    # EP above this = high-confidence finding
  reportable: 0.70         # EP above this = reportable finding
  speculative: 0.50        # EP below this = speculative, flagged as such
  convergence: 0.02        # EP change < this across iterations = converged

# Optional: user hypotheses (Mode C)
hypotheses:
  - id: H1
    statement: "A 10% minimum wage increase reduces youth employment by 1–3%"
    direction: negative
  - id: H2
    statement: "The effect is stronger in industries with high minimum-wage worker share"
    direction: negative

# Optional: data sources (Mode B)
data_sources:
  - path: data/oecd_wages.parquet
    description: "OECD minimum wage panel, annual"
  - path: data/youth_unemployment.csv
    description: "ILO youth unemployment rates by country-year"

# Optional: domain-specific constraints
constraints:
  time_range: "2000-2023"
  geography: "OECD member states"
  outcome_variable: "youth_unemployment_rate_15_24"
```

**Required fields:** `question`, `domain`, `input_mode`, `ep_thresholds`.
Everything else is optional and depends on the input mode.

**EP thresholds** are central to OpenPE. They define when a finding is
considered converged, when it is reportable, and when it remains
speculative. The defaults above are sensible for most analyses; the user
may tighten them for high-stakes decisions or loosen them for exploratory
work. See Section 3 (Phases) for how EP propagation uses these thresholds
at every phase gate.

### 2.4 Domain Context (Retrieval-Based, When Available)

The agent **may** have access to retrieval tools (web search, API
endpoints, domain-specific databases) for acquiring context about the
domain. When available, these augment the agent's training knowledge
with current data and domain-specific information.

**When retrieval is available:** The agent queries external sources to
obtain:
- Domain definitions and standard variable operationalizations
- Prior studies addressing the same or related questions
- Known confounders, effect sizes, and methodological debates
- Available datasets and their documented limitations

**When retrieval is not available:** The agent proceeds using its training
knowledge and any documentation provided in the analysis directory (e.g.,
methodology papers, data dictionaries placed in a `docs/` directory by the
user). All domain-specific claims must be marked as "based on training
knowledge — no external verification" and flagged for human review.

The agent must cite the source for any domain-specific information it uses
(variable definitions, prior effect sizes, methodological choices).
"Retrieved from [source]" or "Based on [reference]" is the minimum;
direct quotation with context is preferred.

**Retrieve, then verify.** Information from external sources may be
incomplete, out of context, or wrong. Where the analysis has access to
the underlying data, the agent must verify retrieved claims against the
data itself. If a source says "the average treatment effect is ~2%", the
agent should check whether this is consistent with what the data shows.
The data is the ground truth; external sources provide starting points
and context. Discrepancies must be documented and resolved.

**When retrieval fails.** The source may be unavailable, the query poorly
matched, or the relevant information simply not indexed. The agent should:
1. Log the failed query and what it was looking for in a retrieval log
   (`retrieval_log.md` in the phase directory)
2. Try rephrased queries or broader searches
3. If retrieval remains unhelpful, proceed using the agent's training
   knowledge and clearly mark any claim that is not source-backed as
   "unverified — based on general knowledge, to be confirmed"
4. Flag the gap in the artifact's open issues section

External sources are an aid, not a requirement. The agent should never
block on a failed retrieval — it does its best and documents the
uncertainty.

---
