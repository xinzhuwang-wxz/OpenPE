# OpenPE Architecture Design

**Date**: 2026-03-28
**Status**: Under Review
**Approach**: Incremental modification of slop-X (Phase Extension)

---

## 1. Project Identity

**Name**: OpenPE (Principle to Endgame)
**Core thesis**: Any real-world event is governed by discoverable first principles. This framework starts from first principles, grows through data-driven analysis to user-specified events, then projects forward to find endgames.

**Relationship to slop-X**: OpenPE is an in-place transformation of the existing slop-X HEP analysis framework. It preserves the phase-based pipeline, multi-agent review mechanism, isolation model, and pixi environment — while generalizing from particle physics to domain-agnostic first-principles reasoning.

**Transformation scope**: This is an in-place modification, not a fork. The `src/` infrastructure (scaffolder, templates, agent profiles, methodology) is modified directly. Existing HEP-specific files are archived to `_archive/` before modification. No backward compatibility with slop-X HEP analyses is maintained — this is a clean transformation.

**Endgame** (formal definition): The projected terminal state or steady-state outcome of the causal chain extending from the user's event of interest. An endgame may be a convergent point (all scenarios agree), a fork (scenarios diverge based on identifiable conditions), an equilibrium (self-sustaining state), or an unstable trajectory (bounded only by external constraints).

---

## 2. Core Concept: Explanatory Chain

### 2.1 The Chain Model

OpenPE's central data structure is the **Explanatory Chain** — a causal reasoning chain from first principles to endgame, passing through the user's event of interest.

```
         ← Abductive direction (Why?)        → Projective direction (What next?)

Principle₁ ──→ E₁ ──→ E₂ ──→ [User Event] ──→ E₃ ──→ E₄ ──→ Endgame
                │              ↑                 │
                ↓              │                 ↓
            sub-chain₁    Principle₂         sub-chain₂
            (EP=0.7)      (independent        (EP=0.3 → truncated)
                           causal path)
```

Each node E on the chain is an **Event Record** — a structured tuple of evidence:

```yaml
event_id: "e_001"
description: "China urbanization rate exceeds 60%"
truth:
  evidence_type: DATA_SUPPORTED  # DATA_SUPPORTED | CORRELATION | HYPOTHESIZED
  confidence: 0.92
  sources: [...]
relevance:
  causal_path_to_target: ["e_001", "e_002", "user_event"]
  effect_size: 0.65
explanatory_power: 0.60         # = truth.confidence × relevance.effect_size
artifacts:
  data: "path/to/dataset.csv"
  analysis: "path/to/script.py"
  table: "path/to/summary.md"
  figure: "path/to/plot.png"
```

### 2.2 Explanatory Power (EP)

**Explanatory Power** is the unified metric that governs chain traversal and truncation. It combines two dimensions:

- **Truth** (epistemic confidence): How certain are we that this event is real? Supported by what quality of data and evidence? Bounded in [0, 1].
- **Relevance** (normalized causal attribution): What fraction of the variance in the target event does this edge explain? Bounded in [0, 1]. This is always a normalized fraction, not a raw effect size.

**Formal definition**:
```
EP = truth × relevance

Where:
  truth ∈ [0, 1]:
    - Based on evidence type: DATA_SUPPORTED → [0.7, 1.0], CORRELATION → [0.3, 0.7], HYPOTHESIZED → [0.0, 0.3]
    - Refined by data quality, sample size, replication

  relevance ∈ [0, 1]:
    - Normalized causal attribution fraction: "what share of the target event's variance does this edge explain?"
    - Pre-analysis (Phase 0): estimated by hypothesis_agent using domain knowledge + literature
      - Use qualitative mapping: Strong theoretical link → 0.7, Moderate → 0.4, Weak → 0.2
    - Post-analysis (Phase 3): refined using actual R² decomposition, partial correlation, or causal effect magnitude normalized to [0,1]

  EP ∈ [0, 1] (guaranteed by construction)
```

**EP thresholds are tunable parameters**, not fixed constants. Initial values:
- Hard truncation: 0.05
- Soft truncation: 0.15
- Sub-chain expansion minimum: 0.30

These should be calibrated through experience and stored in L0 memory.

**Quadrant interpretation**:
```
High truth × High relevance → Strong EP → Continue expanding
High truth × Low relevance  → Weak EP   → Truncate (true but irrelevant)
Low truth  × High relevance → Weak EP   → Mark as hypothesis, cautious expansion
Low truth  × Low relevance  → Minimal EP → Truncate
```

**Worked example (economics domain)**:
```
Question: "Why is China's birth rate declining?"

Edge: urbanization → birth_rate_decline
  truth = 0.85  (DATA_SUPPORTED: World Bank data, strong regression)
  relevance = 0.55 (explains ~55% of variance in cross-country models)
  EP = 0.85 × 0.55 = 0.47

Edge: housing_cost → birth_rate_decline
  truth = 0.70  (CORRELATION: observed but causal direction unclear)
  relevance = 0.30 (partial correlation after controlling for urbanization)
  EP = 0.70 × 0.30 = 0.21

Edge: social_media_influence → birth_rate_decline
  truth = 0.30  (HYPOTHESIZED: limited empirical evidence)
  relevance = 0.15 (weak theoretical link)
  EP = 0.30 × 0.15 = 0.045 → Below hard truncation threshold → truncated
```

### 2.3 EP Propagation and Natural Truncation

Joint EP along a chain decays multiplicatively:

```
Joint_EP(chain) = EP₁ × EP₂ × ... × EPₙ

Truncation rules:
  Joint_EP < 0.05  → Hard truncation, label "Beyond analytical horizon"
  Joint_EP < 0.15  → Soft truncation, lightweight assessment only (no sub-chain expansion)
  Joint_EP ≥ 0.15  → Normal expansion
```

This is the mathematical realization of the core insight: **chains are interleaved but convergent, because joint confidence necessarily decays.** The chain length is not artificially limited — it is bounded by the information-theoretic properties of the evidence.

### 2.4 Sub-Chain Expansion Criteria

A main-chain event expands into a sub-analysis when:

```
Expansion condition =
    (event's EP contribution to main chain > 0.3)
    AND (expansion is expected to significantly change main-chain conclusions)
    AND (Joint_EP at expansion point still > 0.15)
```

**Sub-chain execution protocol**:

Sub-chains run a lightweight version of the Phase 0→6 pipeline:
- **Review tier**: All sub-chain phases use 1-bot review (single logic reviewer), not full 4-bot. The parent chain's Phase 5 (Verification) covers the integrated result with full review.
- **Maximum recursion depth**: 2 levels. Sub-chains may NOT trigger their own sub-chains. If a sub-chain identifies a branch needing expansion, it logs the finding for the parent chain's report but does not recurse.
- **Resumption**: The parent chain resumes after the sub-chain completes Phase 3 (Analysis) — this is sufficient to update the parent's EP values. Sub-chain Phases 4-6 run asynchronously and are referenced in the parent's final report.

**Sub-chain interface contract**:
```
Parent provides:
  - Context: relevant Event Record from main chain
  - EP threshold: minimum Joint_EP for the sub-chain to justify its findings
  - Scope constraint: specific causal edge(s) to investigate

Sub-chain returns:
  - Updated EP values for the investigated edges
  - Key findings summary (≤500 words)
  - Causal classification for each edge
  - Path to full sub-analysis directory (for reference in parent report)
```

---

## 3. Phase Structure

### 3.1 Phase Mapping (slop-X → OpenPE)

slop-X has 5 phases (with 4a/4b/4c split). OpenPE extends to 7 phases, preserving the review tier system.

| New Phase | Name | Origin | Maps to slop-X | Review Tier |
|-----------|------|--------|-----------------|-------------|
| **Phase 0** | Discovery | **New** | — | 4-bot |
| **Phase 1** | Strategy | Modified | Phase 1 | 4-bot |
| **Phase 2** | Exploration | Modified | Phase 2 | Self |
| **Phase 3** | Analysis | Modified | Phase 3 + 4a | 4-bot |
| **Phase 4** | Projection | **New** | — | 4-bot |
| **Phase 5** | Verification | Modified | Phase 4b + 4c | 4-bot + Human Gate |
| **Phase 6** | Documentation | Modified | Phase 5 | 5-bot |

### 3.2 Phase Details

#### Phase 0 — Discovery

**Purpose**: Decompose the user's question, hypothesize first principles, acquire data, and gate on data quality.

**Input classification** (first step):
- **Mode A — Question only**: Fully autonomous data acquisition
- **Mode B — Question + user data**: User data as starting point, but undergoes same quality assessment
- **Mode C — Question + user hypotheses/context**: User hypotheses become candidate DAGs alongside agent-generated ones; no trust privilege

**Key principle**: User-provided data and hypotheses receive no trust privilege. They undergo the same quality assessment and causal testing as autonomously acquired data.

**Steps**:
1. **Question decomposition** → domain, entities, relationships, timeframe, implied concerns
2. **First-principles hypothesization** → candidate causal DAGs (≥2 competing hypotheses, avoid anchoring)
3. **Data requirements derivation** → based on DAG edges, determine needed variables
4. **Data acquisition** → Web search + API calls for public data; log every source with URL, retrieval date, methodology notes, limitations
5. **Data quality assessment** (hard gate) → completeness, consistency, bias assessment, granularity, verdict (HIGH/MEDIUM/LOW)

**Output artifacts**:
- `DISCOVERY.md` — question decomposition + causal DAGs + first-principles hypotheses
- `data/` directory — raw data + metadata
- `DATA_QUALITY.md` — per-dataset quality assessment + gate decision

**Gate rule**: If overall quality is LOW, analysis proceeds with prominent warnings. Never fabricate precision from poor data.

**Agents**: hypothesis_agent, data_acquisition_agent, data_quality_agent

---

#### Phase 1 — Strategy

**Purpose**: Formulate analysis strategy, assess initial EP, plan chain traversal.

**Steps**:
1. **Method selection** → regression, diff-in-diff, synthetic control, etc. (generalized from slop-X "technique selection")
2. **Initial EP assessment** → estimate EP for each causal DAG edge
3. **Chain planning** → determine main chain depth, identify potential sub-chain expansion points
4. **Systematic uncertainty inventory**

**Output artifacts**:
- `STRATEGY.md` — analysis plan with EP assessments
- Causal DAG visualization with EP annotations

**Modification from slop-X**: Generalize "technique selection" to "method selection"; add EP assessment step.

**Agents**: lead_analyst (prompt generalized)

---

#### Phase 2 — Exploration

**Purpose**: Clean data, perform exploratory analysis, preliminary signal-baseline separation.

**Steps**:
1. Data cleaning + feature engineering
2. Exploratory analysis → distributions, trends, preliminary correlations
3. Signal vs. baseline preliminary separation
4. Variable ranking by EP contribution

**Output artifacts**:
- Exploratory figures
- Variable importance ranking
- Data issue discovery log

**Modification from slop-X**: Generalize "sample inventory" to "data exploration".

**Agents**: data_explorer (prompt generalized)

---

#### Phase 3 — Analysis (Core Phase)

**Purpose**: Signal extraction, causal testing, EP propagation, sub-chain expansion decisions.

**Steps**:
1. **Signal extraction** → extract patterns consistent with causal hypotheses
2. **Baseline estimation** → null-hypothesis model (historical trends, counterfactuals, synthetic controls)
3. **Causal testing** → for each hypothesized causal edge:
   - Formalize causal model (DAG)
   - Identify estimand
   - Estimate causal effect using ≥2 methods
   - Run 3 refutation tests:
     - a. Placebo treatment (random variable replacing treatment → effect should vanish)
     - b. Random common cause (adding random confounder → estimate should be stable)
     - c. Data subset (estimate on random subsets → should be consistent)
   - Classify: `DATA_SUPPORTED` / `CORRELATION` / `HYPOTHESIZED`
4. **EP update** → use actual test results to update node EP values
5. **Sub-chain expansion decision** → scaffold sub-analysis for high-EP branches
6. **Statistical model construction** (absorbed from slop-X Phase 4a):
   - Build formal statistical model with nuisance parameters for each systematic uncertainty
   - Construct likelihood function connecting observed data to causal parameters
   - Run expected results: given the model and estimated parameters, what range of outcomes is expected?
   - Signal injection tests: inject known synthetic signal to validate model sensitivity
7. **Uncertainty quantification**:
   - Statistical uncertainties: point estimate + confidence interval via bootstrap/profile likelihood
   - Systematic uncertainties: identify, estimate, and propagate separately from statistical
   - Total uncertainty: combine statistical + systematic (quadrature or profile)
   - Every numerical result must include: central value, statistical uncertainty, systematic uncertainty, total uncertainty

**Output artifacts**:
- `ANALYSIS.md` — causal test results + EP propagation graph + statistical model description
- Causal classification labels for each edge
- Updated DAG with empirical EP values
- Statistical model specification (likelihood, nuisance parameters, constraints)
- Expected results and signal injection validation

**Modification from slop-X**: Merges Phase 3 (selection) and Phase 4a (expected results), including statistical model construction, signal injection, and expected results. Adds causal testing pipeline and EP propagation.

**Causal testing failure modes**:
```
Decision tree for refutation test outcomes:
  All 3 pass           → DATA_SUPPORTED (strong causal evidence)
  2 pass, 1 fail       → CORRELATION (observed relationship, causal claim weakened)
  1 pass, 2 fail       → CORRELATION (weak, note which tests failed)
  All 3 fail           → HYPOTHESIZED (no empirical support; edge remains in DAG but EP.truth → 0.1)
  Insufficient data    → HYPOTHESIZED (label "untestable with available data"; EP.truth → 0.2)
  Contradictory results → DISPUTED (flag for human review; do not auto-classify)
```

**Context splitting**: Phase 3 is the most complex phase, absorbing responsibilities from 4 slop-X agents. Steps 1–5 (causal testing + EP propagation) and Steps 6–7 (statistical model + uncertainty quantification) should be split into separate subagent invocations to manage context pressure. The orchestrator may invoke the analyst agent twice: first for causal analysis, then for statistical modeling.

**Agents**: analyst (generalized from signal_lead + background_estimator), verifier (generalized from cross_checker)

---

#### Phase 4 — Projection

**Purpose**: Forward simulation from established causal relationships to endgame.

**Steps**:
1. **Scenario simulation** → Monte Carlo sampling from causal parameter uncertainty distributions; ≥3 scenarios (baseline, optimistic, pessimistic)
2. **Sensitivity analysis** → for each causal lever, test ±X% impact; rank by magnitude; classify controllable vs. exogenous
3. **Endgame convergence detection**:
   - Scenarios converge → "Robust endgame"
   - Scenarios diverge → "Fork-dependent outcome" (identify fork conditions)
   - Steady state exists → "Equilibrium endgame"
   - Runaway behavior → "Unstable trajectory" (identify bounding constraints)
4. **EP decay visualization** → confidence bands widening over projection distance

**Output artifacts**:
- `PROJECTION.md` — scenarios + sensitivity + endgame classification
- EP decay chart (core visualization)
- Controllable vs. exogenous variable classification

**Agents**: projector_agent (new)

---

#### Phase 5 — Verification

**Purpose**: Independent verification of all findings before documentation.

**Steps**:
1. **Independent reproduction** → verifier agent independently re-derives key results
2. **Data provenance audit** → spot-check source URLs and values
3. **Logic audit** → causal claims match refutation test results
4. **EP verification** → propagation chain calculations are correct

**Gate**: Must pass verification before proceeding to documentation.

**Human gate protocol**: After automated verification passes, the following is presented to the human for approval:
- Verification report summary (pass/fail per check)
- Key causal findings table (edge, classification, EP, confidence interval)
- EP propagation summary (main chain with Joint_EP at each node)
- Projection scenario summaries (≤3 paragraphs each)
- Any DISPUTED edges or data quality warnings

Human may: (a) approve and proceed to Phase 6, (b) request re-analysis of specific edges, (c) request additional data acquisition, (d) terminate the analysis with findings to date.

**Modification from slop-X**: Generalizes "unblinding" to "independent verification". The human gate moves from "10% data validation" to "full verification review".

**Agents**: verifier (generalized from cross_checker)

---

#### Phase 6 — Documentation

**Purpose**: Generate comprehensive, auditable report.

**Steps**:
1. **Report generation** → structured report (Executive Summary → Principles → Data → Analysis → Projection → Audit)
2. **EP decay visualization** → core report chart showing confidence bands
3. **Audit trail** → every factual claim linked to data source, every inferential step auditable

**Output**: Complete analysis report (Markdown → PDF via pandoc)

**Report structure**:
```markdown
# [Title derived from user's question]

## Executive Summary
## 1. First Principles Identified
## 2. Data Foundation
## 3. Analysis Findings (with CAUSAL/CORRELATION/HYPOTHESIZED labels)
## 4. Forward Projection (with EP decay chart)
## 5. Audit Trail
## Appendix
```

**Modification from slop-X**: Extends "analysis note" to "comprehensive report with EP decay visualization".

**Agents**: report_writer (generalized from note_writer), plot_validator

---

### 3.3 Review Mechanism

slop-X's multi-tier review mechanism is preserved with role generalization:

| slop-X Reviewer | OpenPE Reviewer | Responsibility Change |
|-----------------|------------------|----------------------|
| Physics Reviewer | Domain Reviewer | "Physics correctness" → "Domain reasonableness" |
| Critical Reviewer | Logic Reviewer | Preserved + EP propagation logic audit |
| Constructive Reviewer | Methods Reviewer | "Suggestions" → "Method appropriateness" |
| Arbiter | Arbiter | Preserved + EP-related adjudication |
| Rendering Reviewer | Rendering Reviewer | Preserved |

Review tiers:
- **4-bot**: Domain + Logic + Methods (parallel) → Arbiter
- **1-bot**: Single logic reviewer
- **5-bot**: Domain + Logic + Methods + Rendering (parallel) → Arbiter
- **Self**: Integrated within executor agent

Blocking findings (Category A) require iteration before proceeding.
Non-blocking findings (Category B) are noted in the report.

---

## 4. Agent Architecture

### 4.1 Agent Transformation Summary

**Retained and generalized (7)**:

| Original | New Name | Transformation |
|----------|----------|---------------|
| lead_analyst | lead_analyst | Remove HEP terminology, add EP assessment responsibility |
| data_explorer | data_explorer | "Sample inventory" → "Data exploration" + data quality pre-screening |
| signal_lead | analyst | "Event selection" → "Signal extraction + causal testing" |
| cross_checker | verifier | "Cross-check" → "Independent verification + data provenance" |
| note_writer | report_writer | "Analysis note" → "Complete report + EP decay visualization" |
| plot_validator | plot_validator | Preserved, add EP decay chart template |
| ml_specialist | ml_specialist | Preserved, generalize terminology |

**Retained with role redefinition (5)**:

| Original | New Role | Change |
|----------|----------|--------|
| physics_reviewer | domain_reviewer | "Physics reasonableness" → "Domain reasonableness" |
| critical_reviewer | logic_reviewer | Preserved core + EP propagation logic audit |
| constructive_reviewer | methods_reviewer | "Suggestions" → "Method appropriateness assessment" |
| arbiter | arbiter | Preserved + EP-related adjudication criteria |
| rendering_reviewer | rendering_reviewer | Preserved |

**New agents (4)**:

| Agent | Phase | Responsibility |
|-------|-------|---------------|
| hypothesis_agent | Phase 0 | Question decomposition, first-principles hypothesization, causal DAG construction |
| data_acquisition_agent | Phase 0 | Data requirements derivation, web search, API calls, data download |
| data_quality_agent | Phase 0 | Data quality assessment, gate decision |
| projector_agent | Phase 4 | Scenario simulation, sensitivity analysis, endgame convergence detection |

**Retired (6 — absorbed or HEP-specific)**:

| Original | Disposition |
|----------|------------|
| detector_specialist | HEP-specific (detector calibration); no generalized equivalent |
| theory_scout | Responsibilities absorbed by hypothesis_agent + data_acquisition_agent |
| systematic_source_evaluator | Absorbed into analyst |
| background_estimator | Absorbed into analyst (as "baseline estimation") |
| systematics_fitter | Absorbed into analyst (as "uncertainty quantification") |
| investigator | Absorbed into verifier (regression investigation → verification) |

Retired agent prompt files are preserved in `_archive/agents/` for reference.

**Note on regression mechanism**: slop-X's regression protocol (re-running earlier phases when reviews find fundamental issues) is preserved in OpenPE. When a Phase N review identifies a Category A issue originating from Phase M (M < N), the orchestrator rolls back to Phase M and re-executes. The investigator's role (root cause analysis for regressions) is absorbed into the verifier agent.

### 4.2 DAG Label Taxonomy

Two label sets are used at different stages. They are intentionally different — one is pre-analysis (before data), the other is post-analysis (after testing):

**Pre-analysis labels** (Phase 0, hypothesis_agent):
- `LITERATURE_SUPPORTED` — Edge has published academic support
- `THEORIZED` — Edge follows from domain theory but lacks direct empirical citation
- `SPECULATIVE` — Edge is a novel hypothesis without theoretical or empirical basis

**Post-analysis labels** (Phase 3, after refutation testing):
- `DATA_SUPPORTED` — Edge passed all 3 refutation tests (strong causal evidence)
- `CORRELATION` — Edge shows statistical relationship but failed ≥1 refutation test
- `HYPOTHESIZED` — Edge untestable with available data or failed all tests
- `DISPUTED` — Contradictory refutation results (flagged for human review)

### 4.3 New Agent Specification Template

All new agents follow slop-X's comprehensive agent definition standard. Example for hypothesis_agent:

```markdown
# Hypothesis Agent

## Role
First-principles identification and causal DAG construction.

## When Invoked
Phase 0, Steps 0.1–0.2

## Inputs
- User question/scenario (raw text)
- Domain pack (if available from memory system)
- Prior causal knowledge (from causal knowledge graph)

## Mandatory Checklist
1. Parse question into: domain, entities, relationships, timeframe, concerns
2. Generate ≥3 candidate first principles for the identified domain
3. For each principle, construct a falsifiable causal DAG
4. Each DAG edge must be labeled: LITERATURE_SUPPORTED | THEORIZED | SPECULATIVE
5. Assess initial EP for each edge
6. Identify data variables required to test each edge
7. Cross-reference memory system for prior domain experiences
8. Generate ≥2 competing DAGs (avoid anchoring on first hypothesis)

## Output Format
DISCOVERY.md containing:
- Question decomposition table
- Candidate first principles with literature support
- Causal DAG (mermaid format for rendering)
- Data requirements matrix (variable × source × priority)
- Initial EP assessment for each DAG edge

## Constraints
- Never assume causation without evidence
- Always generate competing hypotheses
- Flag when domain falls outside known domain packs
- User-provided hypotheses receive no trust privilege
```

### 4.4 Memory Integration (All Agents)

Every agent receives two memory interfaces at invocation:

**Read (at phase start)**:
- L0: Universal analysis principles (always loaded, ~500 tokens)
- L1: Domain experiences (loaded when domain matches, ~2000 tokens)
- L2: On-demand (agent explicitly requests specific past analysis details)

**Write (at phase completion)**:
- Session commit → extract experiences from current phase
- New memories start at confidence 0.5
- Subsequent analyses can corroborate (+0.15, capped at 0.95) or contradict (-0.25, floored at 0.05)

---

## 5. Data Flow and Input Handling

### 5.1 Input Mode Classification

Phase 0 begins with input classification:

- **Mode A — Question only**: Fully autonomous hypothesis generation → data requirements → acquisition → quality assessment
- **Mode B — Question + user data**: User data as starting point → quality assessment (equally rigorous!) → supplement with acquired data → merged quality report
- **Mode C — Question + user context/hypotheses**: User hypotheses become one candidate DAG among agent-generated ones → all undergo equal testing → user hypotheses receive no trust privilege

### 5.2 Data Acquisition Layer

```
DataAcquisitionLayer
├── WebSearchProvider        # General: WebSearch → discover sources → WebFetch to download
├── FREDProvider             # Wrapped: FRED API (economic data)
├── WorldBankProvider        # Wrapped: World Bank API (global development data)
├── UserDataProvider         # User-supplied data (Mode B)
└── DataRegistry             # Unified registry: source, retrieval time, format, provenance
```

Each provider implements a unified interface:
```python
class DataProvider:
    def search(query: str) -> list[DataSource]
    def fetch(source: DataSource) -> RawDataset
    def metadata(source: DataSource) -> Provenance
```

### 5.2.1 Data Acquisition Tooling (detailed specification)

**Tool access**: The data_acquisition_agent uses Claude Code's built-in tools:
- `WebSearch` — discover data sources and APIs
- `WebFetch` — download data files and API responses
- `Bash` (within pixi) — run Python scripts for API calls, data format conversion

**Isolation policy for Phase 0**:
- The isolation hook is relaxed for Phase 0 agents: they may write to `phase0_discovery/data/` and `/tmp/`
- Web access is unrestricted for data acquisition (this is the agent's primary function)
- Downloaded files are logged in `phase0_discovery/data/registry.yaml` with full provenance

**Caching and reproducibility**:
- All downloaded data is cached in `phase0_discovery/data/raw/` with immutable filenames: `{source_id}_{date}.{ext}`
- `registry.yaml` records: URL, retrieval date, HTTP headers, file hash (SHA-256), API query parameters
- Re-running Phase 0 on the same question uses cached data by default (override with `force_refresh=true`)

**Fallback behavior**:
- API rate-limited → retry with exponential backoff (max 3 attempts), then fall back to WebSearch for alternative source
- Source unavailable → log in DATA_QUALITY.md as "Source unavailable: {URL}", reduce affected variable's quality to LOW
- No data found for a required variable → explicitly state in DISCOVERY.md: "Variable X required but no public data found. Analysis cannot assess causal edge Y→Z."
- Authentication required → skip source, log as "Requires authentication (not accessible)", search for alternative public source

**Required pixi dependencies for data acquisition**:
```toml
[dependencies]
pandas = ">=2.0"
requests = ">=2.31"
wbgapi = ">=1.0"       # World Bank API client
fredapi = ">=0.5"      # FRED API client
openpyxl = ">=3.1"     # Excel file reading
pyarrow = ">=14.0"     # Parquet support
```

**Data format standardization**:
All acquired datasets are converted to a common format before Phase 1:
- Tabular data → Parquet files in `phase0_discovery/data/processed/`
- Time series aligned to common temporal index
- Missing values explicitly marked (not zero-filled)
- Units documented in `registry.yaml`

### 5.3 Data Quality Gate

```yaml
# DATA_QUALITY.md structure
datasets:
  - id: "ds_001"
    name: "World Bank - China GDP per capita"
    source: "api://worldbank/NY.GDP.PCAP.CD"
    retrieved: "2026-03-28"
    quality:
      completeness: 0.95
      consistency: 0.88
      bias_assessment: "description of potential biases"
      granularity: "Annual, national level"
      verdict: HIGH  # HIGH / MEDIUM / LOW
      supports: "What level of conclusions this data can support"
    user_provided: false

gate_decision:
  overall: MEDIUM
  proceed: true
  warnings: [...]
```

### 5.4 Artifact Directory Structure

**Directory naming convention**: Follow slop-X's semantic suffix pattern: `phase{N}_{name}/`. This ensures every template path reference, orchestrator loop, and CLAUDE.md remains consistent with the existing convention.

```
analyses/my_analysis/
├── .analysis_config          # Input mode + data path + input_mode (A/B/C)
├── STATE.md                  # Progress tracking (reused from slop-X)
├── analysis_config.yaml      # Analysis metadata (reused from slop-X)
├── memory/                   # Analysis-local memory snapshot (copied from global at start)
├── phase0_discovery/
│   ├── CLAUDE.md             # Phase 0 instructions for agents
│   ├── exec/
│   ├── DISCOVERY.md
│   ├── DATA_QUALITY.md
│   ├── data/                 # Acquired raw data + metadata
│   │   ├── raw/              # Original downloaded files
│   │   ├── processed/        # Cleaned/aligned data
│   │   └── registry.yaml     # Data provenance registry
│   └── review/
├── phase1_strategy/
│   ├── CLAUDE.md
│   ├── exec/
│   ├── STRATEGY.md
│   ├── figures/
│   └── review/
├── phase2_exploration/
│   ├── CLAUDE.md
│   ├── exec/
│   ├── scripts/
│   ├── figures/
│   └── review/               # Self-review only
├── phase3_analysis/
│   ├── CLAUDE.md
│   ├── exec/
│   ├── ANALYSIS.md
│   ├── scripts/
│   ├── figures/
│   ├── sub_analyses/         # Sub-chain expansions (if any)
│   └── review/
├── phase4_projection/
│   ├── CLAUDE.md
│   ├── exec/
│   ├── PROJECTION.md
│   ├── figures/
│   └── review/
├── phase5_verification/
│   ├── CLAUDE.md
│   ├── exec/
│   ├── VERIFICATION.md
│   └── review/
└── phase6_documentation/
    ├── CLAUDE.md
    ├── exec/
    ├── REPORT.md
    ├── REPORT.pdf
    └── audit_trail/
```

**Input mode classification**: The `input_mode` field in `.analysis_config` is set by the orchestrator at analysis start based on what the user provides:
- `input_mode=A` — question only (default)
- `input_mode=B` — question + user data (user data path in `user_data_dir`)
- `input_mode=C` — question + user context/hypotheses (context file path in `user_context`)

---

## 6. Memory System and Self-Evolution

### 6.1 Memory Architecture

```
memory/
├── L0_universal/              # Always loaded (~500 tokens)
│   └── principles.yaml        # Universal analysis principles
│
├── L1_domain/                 # Loaded per matching domain (~2000 tokens/domain)
│   ├── economics.yaml
│   ├── demography.yaml
│   └── ...                    # Grows automatically with analyses
│
├── L2_detailed/               # On-demand (agent explicitly requests)
│   ├── analysis_YYYYMMDD_NNN/
│   └── ...
│
└── causal_graph/              # Cross-analysis causal knowledge graph
    └── graph.json             # Nodes=variables, Edges=causal relationships+strength+confidence
```

### 6.2 Memory Lifecycle

```
Analysis completion
   │
   ▼
Session Commit (auto-triggered)
   │
   ├── Extract experience entries
   │   Each entry:
   │   {
   │     content: "description of learned experience",
   │     domain: "domain_name",
   │     type: "domain_experience | method_experience | data_source_experience | failure_experience",
   │     confidence: 0.5,          # New memories start here
   │     source_analysis: "analysis_id",
   │     corroborated_by: [],
   │     contradicted_by: [],
   │     decay_rate: 0.01
   │   }
   │
   ├── Update causal graph
   │   Write established causal relationships with strength + confidence
   │   If relationship already exists: corroborate or contradict
   │
   └── Contradiction detection
       If new analysis contradicts stored knowledge → lower stored confidence, flag for review
```

### 6.3 Confidence Evolution Rules

```
Initial value:                    0.50
Corroborated by independent analysis: +0.15 (capped at 0.95)
Contradicted by independent analysis: -0.25 (floored at 0.05)
Unreferenced decay:               -0.01 per analysis (slow forgetting)

Loading rules:
  confidence ≥ 0.2   → Normal loading
  0.1 ≤ conf < 0.2   → Loaded with ⚠️ WARNING prefix
  confidence < 0.1    → Quarantined (not loaded by default, manual request only)
```

### 6.4 Causal Knowledge Graph Reuse

When a new analysis involves previously established causal relationships:

```
confidence ≥ 0.8 → Cite prior finding, skip re-testing (time saving)
0.5 ≤ conf < 0.8 → Cite but still run lightweight verification
confidence < 0.5  → Do not trust, must re-test from scratch
```

### 6.5 Domain Pack Auto-Growth

First analysis in a domain → no domain pack → agent starts from scratch.

After analysis completion → session commit extracts domain knowledge → writes to `L1_domain/{domain}.yaml`:

```yaml
domain: demography
learned_terminology:
  signal: "significant deviation from historical trend"
  baseline: "pre-intervention historical trend extrapolation"
known_data_sources:
  - name: "UN Population Division"
    quality: HIGH
    notes: "2-year revision cycle"
known_pitfalls:
  - "Different countries use inconsistent fertility metrics (TFR vs CBR)"
effective_methods:
  - "Difference-in-differences works well for policy change analysis"
```

Subsequent analyses in the same domain automatically receive this as L1 context.

---

## 7. Non-Negotiable Rules

1. **Never fabricate data.** If data cannot be found, say so. An honest "insufficient data" is infinitely better than a hallucinated dataset.
2. **Never present correlation as causation.** Every causal claim must pass 3 refutation tests. Label everything: `DATA_SUPPORTED` / `CORRELATION` / `HYPOTHESIZED`.
3. **Always show uncertainty.** Every number has an error bar. Every projection has a confidence band. No false precision.
4. **Always cite sources.** Every data point traces to URL + retrieval date. Every method cites its theoretical basis.
5. **EP decays with chain length.** Near-term findings are high EP. Far projections are low EP. The report must make this visually obvious.
6. **Data quality gates are hard gates.** LOW quality → prominent warnings, not pretended precision.
7. **The verifier must be independent.** It receives ONLY outputs and raw data, NOT intermediate reasoning.
8. **Memory pollution is a critical risk.** Confidence scoring and decay are mandatory.
9. **User-provided data/hypotheses receive no trust privilege.** Same quality assessment and causal testing as autonomously acquired data.

---

## 8. Implementation Priority

### Sprint 1 — Foundation (Phase 0 + scaffolding changes)
- Modify `src/scaffold_analysis.py` to create `phase0_discovery/` through `phase6_documentation/` directories
- Create new `src/templates/root_claude.md` with updated orchestrator loop (phase sequence `[0, 1, 2, 3, 4, 5, 6]`)
- Create new `src/templates/phase0_claude.md` for Phase 0 instructions
- Update all existing phase CLAUDE.md templates (`phase1` through `phase5` → renumbered)
- Build hypothesis_agent, data_acquisition_agent, data_quality_agent profiles in `.claude/agents/`
- Implement DataAcquisitionLayer (WebSearch + FRED + WorldBank providers)
- Implement Data Quality Gate
- Update `pixi.toml` template with OpenPE dependencies (pandas, dowhy, wbgapi, fredapi, etc.)
- Archive existing HEP-specific agent profiles to `_archive/agents/`
- Update `.analysis_config` schema to include `input_mode` field
- End-to-end test: question → data acquired → quality assessed

### Sprint 2 — Core Analysis (Phase 1–3)
- Generalize lead_analyst, data_explorer, analyst agents
- Implement causal testing pipeline (3-refutation protocol)
- Implement EP calculation and propagation
- Build sub-chain expansion mechanism
- End-to-end test: question → data → causal analysis → EP propagation

### Sprint 3 — Projection + Verification (Phase 4–5)
- Build projector_agent (scenario simulation, sensitivity, convergence)
- Build/generalize verifier agent
- Implement EP decay visualization
- Implement human gate for Phase 5
- End-to-end test: full pipeline through Phase 5

### Sprint 4 — Documentation + Review (Phase 6 + review system)
- Generalize report_writer agent
- Generalize reviewer agents (domain/logic/methods/arbiter)
- Implement full report structure with audit trail
- End-to-end test: complete pipeline producing report

### Sprint 5 — Memory + Self-Evolution
- Implement memory system (L0/L1/L2 tiers)
- Implement session commit and experience extraction
- Implement causal knowledge graph
- Implement confidence scoring with decay
- Implement domain pack auto-growth
- Test: run 3+ analyses, verify system improves across runs

### Sprint 6 — Polish + Validation
- Cross-domain validation (economics, public health, technology)
- Stress-test EP truncation mechanism
- Stress-test memory pollution resistance
- Documentation and release

---

## 9. Key Architectural Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Modification approach | Phase Extension (not Overlay) | Direct modification maximizes reuse; EP must penetrate agent decisions |
| Core metric | Explanatory Power (EP) | Unifies truth and relevance; provides natural truncation |
| EP computation | truth.confidence × relevance.effect_size | Multiplicative ensures both dimensions contribute; joint EP decays naturally |
| Truncation | Hard at 0.05, soft at 0.15 | Prevents infinite chains while preserving meaningful exploration |
| Sub-chain execution | Hybrid: linear main + on-demand expansion | Pragmatic balance between thoroughness and resource use |
| Data acquisition | Web search primary + key API wrappers | Quick to implement; reliable for high-value sources |
| User data handling | No trust privilege | Prevents bias; user data undergoes same quality assessment |
| Memory integration | Early (Sprint 5, not deferred) | Self-evolution is core capability, not enhancement |
| Retired agents | Moved to _archive/, not deleted | Preserves reference material for future use |
