# CLAUDE.md — Project Instruction Prompt

## Project Identity

**Name**: slop-FP (First Principles)
**Origin**: Extension of [slop-X / JFC framework](https://github.com/jfc-mit/slop-X) (MIT/CERN, arxiv 2603.20179)
**Core Thesis**: Any real-world event is governed by discoverable first principles, and those principles manifest in data. This framework starts from first principles, grows through data-driven analysis to user-specified events, then projects forward to find endgames.

---

## What This Project IS

A **generalized autonomous analysis framework** that retains the slop/JFC pipeline architecture but replaces HEP-specific content with domain-agnostic first-principles reasoning. The workflow:

```
User question/scenario (no data provided)
        │
        ▼
Phase 1: Identify governing first principles + acquire relevant data
        │
        ▼
Phase 2: Data-driven event analysis (slop-X core, generalized)
        │
        ▼
Phase 3: Forward projection to endgame
        │
        ▼
Output: Comprehensive and detailed Auditable report with table, plot, confidence bands
```

**Critical**: The user provides only a question or scenario — NOT data. The agent must autonomously identify what data is needed, find/acquire it from public sources, assess its quality, and then analyze it.

---

## Directory Layout

```
.
├── CLAUDE.md                  ← You are here
├── README.md
├── src/
│   ├── orchestrator/          ← Main pipeline controller (from slop-X, generalized)
│   ├── agents/
│   │   ├── hypothesis/        ← Phase 1: first-principles identification
│   │   ├── data_acquisition/  ← Phase 1: find + fetch relevant public data
│   │   ├── data_quality/      ← Phase 1→2 gate: assess what data can support
│   │   ├── analyst/           ← Phase 2: signal extraction, baseline, inference
│   │   ├── verifier/          ← Phase 2: independent data + logic verification
│   │   ├── projector/         ← Phase 3: scenario simulation + endgame
│   │   └── reporter/          ← Phase 3: report generation with audit trail
│   ├── review/                ← Multi-agent review panel (from slop-X)
│   ├── retrieval/             ← DomainTreeRAG (generalized SciTreeRAG)
│   ├── memory/                ← OpenViking integration for living agent memory
│   ├── knowledge_graph/       ← Graphiti integration for causal KG
│   ├── causal/                ← DoWhy + Causica wrappers
│   └── verification/          ← ACG protocol + OpenFactCheck integration
├── prompts/
│   ├── templates/             ← Domain-agnostic analysis prompt templates
│   └── domain_packs/          ← Per-domain terminology + knowledge (injected via OpenViking)
├── config/
├── tests/
├── outputs/                   ← Generated reports land here
└── _ref/                      ← Reference repositories (read-only reference, not imported)
    ├── OpenViking/            ← volcengine/OpenViking
    ├── deer-flow/             ← bytedance/deer-flow
    ├── dowhy/                 ← py-why/dowhy
    ├── causica/               ← microsoft/causica
    ├── graphiti/              ← getzep/graphiti
    ├── acg_protocol/          ← Kos-M/acg_protocol
    └── OpenFactCheck/         ← yuxiaw/OpenFactCheck
```

---

## The Three Phases — Detailed Specifications

### Phase 1: First Principles Identification + Data Acquisition

**This phase is NEW — slop-X does not have it.** It replaces the HEP "analysis plan" with autonomous causal hypothesis discovery.

**Step 1.1 — Decompose the user's question**
- Parse the user's question/scenario into: domain, entities, relationships, timeframe, implied concerns.
- Example: "Why is China's birth rate declining and what happens next?" → domain: demography + economics; entities: birth rate, economic variables, policy; timeframe: 1980–2030+; concern: trajectory.

**Step 1.2 — Hypothesize first principles**
- For the identified domain, generate candidate first principles (fundamental causal drivers).
- Use DomainTreeRAG to retrieve relevant academic literature and established theoretical frameworks.
- Output: a set of hypothesized causal DAGs (directed acyclic graphs) describing how first principles connect to the user's event of interest.
- **Each hypothesis must be falsifiable and data-testable.**

**Step 1.3 — Data acquisition**
- Based on the causal DAGs, determine what data variables are needed.
- Search for and acquire data from public sources: World Bank, FRED, WHO, government statistical agencies, academic datasets, APIs.
- **Log every data source with URL, retrieval date, original methodology notes, known limitations.**
- If critical data is unavailable, explicitly state what analysis CANNOT be done and why.

**Step 1.4 — Data quality assessment (GATE)**
This is a hard gate. Before proceeding to Phase 2, the data_quality agent must produce a Data Quality Report:

```
For each acquired dataset:
  - Completeness: % missing values, temporal coverage gaps
  - Consistency: cross-source agreement where overlapping
  - Bias assessment: sampling bias, survivorship bias, measurement methodology changes
  - Granularity: spatial/temporal resolution vs. what analysis requires
  - Overall verdict: HIGH / MEDIUM / LOW confidence
  - What level of conclusions this data can support
```

**If overall data quality is LOW, the analysis must proceed with explicit hedging and the report must prominently warn about data limitations. Do NOT fabricate precision from poor data.**

### Phase 2: Data-Driven Event Analysis (slop-X Core, Generalized)

This phase retains the slop-X pipeline architecture. The mapping from HEP concepts to general concepts:

| slop-X (HEP-specific)          | slop-FP (generalized)                        |
|---------------------------------|-----------------------------------------------|
| Event selection (physics cuts)  | Signal extraction (pattern filtering)         |
| Background estimation           | Baseline estimation (null-hypothesis model)   |
| Efficiency correction            | Measurement bias correction                   |
| Unfolding                        | Deconvolution / debiasing                     |
| Uncertainty quantification       | Uncertainty quantification (kept as-is)       |
| Statistical inference            | Statistical inference (kept as-is)            |
| Toy-based closure tests          | Synthetic validation / bootstrap tests        |
| Systematic error breakdown       | Systematic error breakdown (kept as-is)       |

**Step 2.1 — Signal extraction**
- From the acquired data, extract patterns that are consistent with the hypothesized causal relationships.
- Separate signal (patterns explained by first principles) from noise (random variation).

**Step 2.2 — Baseline estimation**
- Construct a null-hypothesis baseline: "what would the data look like if the hypothesized first principle had NO effect?"
- Methods: historical baselines, control groups, counterfactual estimation, synthetic controls.

**Step 2.3 — Causal testing (CRITICAL)**
Use DoWhy + Causica for rigorous causal inference:

```python
# Pseudocode for the required causal testing pipeline
for each_hypothesized_causal_edge:
    1. Specify the causal model (DAG) formally
    2. Identify the estimand (what causal effect to estimate)
    3. Estimate the causal effect using ≥2 methods (e.g., propensity score, IV, diff-in-diff)
    4. Run ALL THREE refutation tests:
       a. Placebo treatment (random variable replacing treatment → effect should vanish)
       b. Random common cause (adding random confounder → estimate should be stable)
       c. Data subset (estimate on random subsets → should be consistent)
    5. Classify result:
       - PASSES all 3 refutations → label as "DATA-SUPPORTED CAUSAL RELATIONSHIP"
       - FAILS any refutation → label as "OBSERVED CORRELATION (causal claim not supported)"
       - Insufficient data for testing → label as "HYPOTHESIZED (untestable with available data)"
```

**This classification MUST appear in the final report. Never present a correlation as a causal finding.**

**Step 2.4 — Uncertainty quantification**
- For every numerical estimate: report point estimate + confidence interval.
- Use bootstrap/Monte Carlo methods from slop-X to propagate uncertainties.
- Systematic errors: identify and quantify separately from statistical errors.

**Step 2.5 — Independent verification (Verifier Agent)**
A separate verifier agent, with no shared context with the analyst agent, must:
1. Verify that data sources are real and accessible (spot-check URLs and values).
2. Re-derive at least one key statistical result independently.
3. Check that causal claims match the refutation test results.
4. Flag any logical gaps between data and conclusions.

Following the ACG protocol pattern:
- Every factual claim → linked to specific data source (UGVP-style grounding)
- Every inferential step → logic chain auditable (RSVP-style verification)

### Phase 3: Forward Projection to Endgame

**This phase EXPANDS slop-X's "paper drafting" into full scenario projection.**

**Step 3.1 — Scenario simulation**
- Based on the causal relationships established in Phase 2, simulate forward trajectories.
- Use Monte Carlo methods: sample from the uncertainty distributions of causal parameters.
- Generate ≥3 scenarios: baseline continuation, optimistic (favorable parameter shift), pessimistic (unfavorable shift).
- If applicable, identify tipping points or phase transitions where qualitative behavior changes.

**Step 3.2 — Sensitivity analysis**
- For each causal lever identified in Phase 2, test: "if this variable changes by ±X%, how does the outcome shift?"
- Rank variables by impact magnitude.
- Identify which variables the user/policymaker can actually influence vs. which are exogenous.

**Step 3.3 — Convergence detection (endgame identification)**
- Do the scenarios converge to a common endpoint? → "Robust endgame"
- Do they diverge? → "Fork-dependent outcome" — identify the fork conditions.
- Is there a steady state? → "Equilibrium endgame" — characterize it.
- Is there runaway behavior? → "Unstable trajectory" — identify constraints that might bound it.

**Step 3.4 — Confidence decay visualization**
```
The report MUST include a confidence band that widens over time:

    Phase 2 findings (present/past):  ████████████  HIGH confidence
    Near-term projection (1-3 years):  ██████████░░  MEDIUM confidence  
    Mid-term projection (3-10 years):  ██████░░░░░░  LOW-MEDIUM confidence
    Long-term projection (10+ years):  ███░░░░░░░░░  LOW confidence (scenario-dependent)

Never present long-term projections with the same certainty as empirical findings.
```

**Step 3.5 — Report generation**
Final output structure:

```markdown
# [Title derived from user's question]

## Executive Summary
- One-paragraph answer to the user's question
- Confidence level of the answer
- Key caveats

## 1. First Principles Identified
- What fundamental drivers govern this domain
- Causal DAG visualization
- Literature support

## 2. Data Foundation
- Sources acquired, with full provenance
- Data quality assessment summary
- What the data CAN and CANNOT tell us

## 3. Analysis Findings
- Signal vs. baseline results
- Causal relationships (with explicit CAUSAL vs CORRELATION vs HYPOTHESIZED labels)
- Uncertainty ranges on all estimates
- Verification results

## 4. Forward Projection
- Scenarios with confidence bands
- Sensitivity analysis: what matters most
- Endgame identification
- Confidence decay chart

## 5. Audit Trail
- Full data provenance table
- Methodology choices and alternatives considered
- Refutation test results
- Verifier agent report

## Appendix
- Raw analysis code
- Statistical details
- Data quality report
```

---

## Architectural Principles (from slop-X, enforced here)

### Context Isolation
Following JFC's design: **no agent retains memory between invocations within a single analysis run.** All state is externally serialized. This ensures:
- Complete audit trails
- Reproducibility
- No cross-contamination between analysis steps

**Exception**: The OpenViking memory system stores **cross-analysis** experiences (not within-analysis state). These are curated, confidence-scored lessons learned that improve future analyses.

### Multi-Agent Review
Retain slop-X's multi-agent review panel. At each phase boundary, a review panel (≥3 agents) must pass the work:

```
Review panel composition:
  1. Domain reviewer    — "Is this analysis sensible for this domain?"
  2. Methods reviewer   — "Are the statistical methods appropriate?"
  3. Logic reviewer     — "Does the conclusion follow from the evidence?"
  4. Code validator     — "Does the code actually do what the text claims?"
  
Blocking findings (Category A) require iteration before proceeding.
Non-blocking findings (Category B) are noted in the report.
```

### Serialized State
All intermediate artifacts (data, code, figures, intermediate conclusions) are saved to disk at each step. If the pipeline fails at step N, it can resume from step N-1 without re-running earlier phases.

---

## Memory System Design (OpenViking Integration)

### What Gets Memorized (cross-analysis, NOT within-analysis)
After each completed analysis, trigger OpenViking session commit to extract:

```
viking://memories/agent/{agent_name}/
├── domain_experiences/      ← "In financial data, leading indicators typically precede by 2-4 quarters"
├── method_experiences/      ← "Bootstrap works better than asymptotic CI for small samples in this domain"  
├── data_source_experiences/ ← "World Bank data for country X has a known gap in 2015-2017"
└── failure_experiences/     ← "Granger causality alone is insufficient for policy causal claims"
```

### Confidence-Scored Memory
Every memory entry MUST have:
```json
{
  "content": "...",
  "confidence": 0.85,
  "source_analysis_id": "analysis_20260328_001",
  "corroborated_by": ["analysis_20260401_003"],
  "contradicted_by": [],
  "last_updated": "2026-04-01",
  "decay_rate": 0.01
}
```

Rules:
- New memories start at confidence 0.5
- Corroboration by independent analysis: confidence += 0.15 (capped at 0.95)
- Contradiction by independent analysis: confidence -= 0.25 (floored at 0.05)
- Memories with confidence < 0.2 are loaded with WARNING prefix
- Memories with confidence < 0.1 are quarantined (not loaded by default)

### Loading Tiers (OpenViking L0/L1/L2)
```
L0 (always loaded, ~500 tokens):
  - Universal analysis principles
  - "Always check data quality before analysis"
  - "Correlation ≠ causation — test with refutation"

L1 (loaded for matching domain, ~2000 tokens):
  - Domain-specific experiences
  - Known data source qualities
  - Effective methods for this domain

L2 (loaded on-demand, variable):
  - Specific past analysis details
  - Detailed failure post-mortems
  - Only loaded when agent explicitly requests
```

---

## Causal Knowledge Graph (Graphiti Integration)

Separate from OpenViking's text memory. Graphiti stores **structural causal knowledge**:

```
Every established causal relationship from Phase 2 is written to Graphiti:

Node: "interest_rate" 
  ├── CAUSES → "credit_expansion" (strength: 0.73, confidence: HIGH, analysis: #001)
  ├── CAUSES → "currency_value" (strength: 0.45, confidence: MEDIUM, analysis: #001)
  └── CORRELATED_WITH → "stock_market" (confidence: HIGH, but NOT causal per refutation)

This enables:
  - Cross-analysis knowledge accumulation  
  - "We already know X causes Y from a previous analysis" → skip re-testing, cite prior work
  - Contradiction detection: "New analysis finds X does NOT cause Y → flag for review"
```

---

## Domain Pack System (Prompt Engineering)

slop-X's prompts are HEP-specific. We replace with domain-agnostic templates + injectable domain packs.

### Template (domain-agnostic, lives in prompts/templates/)
```
You are analyzing {domain} data to test the hypothesis that {first_principle} 
drives {observed_event}. 

Your task: identify signal patterns that are statistically distinct from baseline,
quantify the statistical significance of any deviation, and assess whether the 
relationship is causal or merely correlational.

Use the following domain-specific terminology and conventions:
{domain_pack_content}
```

### Domain Pack (lives in prompts/domain_packs/ or viking://resources/)
```yaml
# domain_packs/economics.yaml
domain: economics
terminology:
  signal: "statistically significant deviation from trend"
  baseline: "counterfactual scenario / historical trend"
  background: "confounding economic variables"
  event_selection: "filtering for relevant economic indicators"
  systematic_errors:
    - measurement_revision: "Government statistics are frequently revised; use latest vintage"
    - seasonal_adjustment: "Most economic data requires seasonal adjustment"
    - purchasing_power: "Cross-country comparisons need PPP adjustment"
common_data_sources:
  - name: "FRED (Federal Reserve Economic Data)"
    url: "https://fred.stlouisfed.org/"
    api: true
    quality: HIGH
  - name: "World Bank Open Data"
    url: "https://data.worldbank.org/"
    api: true
    quality: HIGH
  - name: "IMF Data"
    url: "https://data.imf.org/"
    quality: HIGH
known_pitfalls:
  - "Goodhart's Law: when a measure becomes a target, it ceases to be a good measure"
  - "Lucas critique: historical relationships may not hold under policy changes"
  - "Simpson's paradox is common in aggregated economic data"
```

**To add a new domain**: create a new YAML pack. The framework itself does NOT change.

---

## Reference Repos — What to Borrow, What to Skip

### _ref/OpenViking/
**Borrow**: File-system paradigm for context management, L0/L1/L2 tiered loading, session-commit memory extraction, the `viking://` URI scheme.
**Skip**: Volcengine-specific cloud deployment, the bot/console features. We only need the core memory engine.

### _ref/deer-flow/
**Borrow**: Docker sandbox architecture for isolated code execution, sub-agent spawning with scoped contexts, the skill-as-markdown-file pattern.
**Skip**: The LangGraph/LangChain dependency (we use Claude Code directly, as slop-X does), the web UI, messaging integrations.

### _ref/dowhy/
**Borrow**: The complete causal inference pipeline — model specification, identification, estimation, refutation. This is the mathematical backbone of Phase 2's causal testing.
**Integrate as**: A Python library called within analyst agent's code execution. The agent writes DoWhy code, runs it in sandbox, interprets results.

### _ref/causica/
**Borrow**: DECI model for causal discovery from observational data when the causal DAG is unknown.
**Integrate as**: Called when Phase 1's hypothesis agent cannot determine causal structure from literature alone. Feed raw data to Causica → get candidate DAG → validate with DoWhy.

### _ref/graphiti/
**Borrow**: Dynamic knowledge graph with hybrid retrieval (semantic + keyword + graph traversal). The real-time update capability.
**Skip**: Neo4j dependency if too heavy — evaluate FalkorDB or Kuzu as lighter alternatives.

### _ref/acg_protocol/
**Borrow**: The dual-layer audit concept — UGVP for fact grounding + RSVP for logic verification. Adapt the marking scheme for our reports.
**Skip**: The full verifier agent architecture (we build our own simpler version).

### _ref/OpenFactCheck/
**Borrow**: The factuality evaluation pipeline — claim decomposition, evidence retrieval, claim verification. Use as a post-hoc check on Phase 3 report claims.
**Skip**: The LLM evaluation benchmarking parts.

---

## Implementation Priority (Build in This Order)

```
Sprint 1 (Foundation):
  ├── Generalize slop-X orchestrator: strip HEP terms, inject template system
  ├── Build data_acquisition agent: can search + fetch public data
  ├── Build data_quality agent: produces quality assessment
  └── End-to-end test: one simple question → data acquired → quality assessed

Sprint 2 (Core Analysis):
  ├── Build analyst agent with generalized Phase 2 pipeline
  ├── Integrate DoWhy for causal testing with 3-refutation protocol
  ├── Build verifier agent
  └── End-to-end test: question → data → causal analysis → verified findings

Sprint 3 (Forward Projection):
  ├── Build projector agent (scenario sim + sensitivity + convergence)
  ├── Build reporter agent with confidence decay visualization
  ├── Integrate multi-agent review at phase boundaries
  └── End-to-end test: full pipeline producing complete report

Sprint 4 (Memory + Learning):
  ├── Integrate OpenViking for cross-analysis memory
  ├── Implement confidence-scored memory with decay
  ├── Build domain pack system
  └── Test: run 3+ analyses, verify agent improves

Sprint 5 (Knowledge Graph + Polish):
  ├── Integrate Graphiti for causal KG accumulation
  ├── Integrate ACG-style audit trail in reports
  ├── Cross-domain validation (test on economics, public health, technology)
  └── Documentation + release
```

---

## Non-Negotiable Rules

1. **Never fabricate data.** If data cannot be found, say so. An honest "insufficient data" is infinitely better than a hallucinated dataset.

2. **Never present correlation as causation.** Every causal claim must pass 3 refutation tests. Label everything explicitly: CAUSAL / CORRELATION / HYPOTHESIZED.

3. **Always show uncertainty.** Every number has an error bar. Every projection has a confidence band. No false precision.

4. **Always cite sources.** Every data point traces back to a URL + retrieval date. Every analytical method cites its theoretical basis.

5. **Confidence decays with projection distance.** Near-term findings from data are HIGH confidence. Far-future projections are LOW confidence. The report must make this visually obvious.

6. **Data quality gates are hard gates.** If the data quality assessment says LOW, the analysis proceeds with prominent warnings — it does NOT pretend the data is better than it is.

7. **The verifier agent must be independent.** It receives ONLY the analyst's outputs and the raw data. It does NOT see the analyst's intermediate reasoning. This prevents confirmation bias.

8. **Memory pollution is a critical risk.** Wrong conclusions that enter the memory system will poison future analyses. Memory confidence scoring and decay are mandatory, not optional.