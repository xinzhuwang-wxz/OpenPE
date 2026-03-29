# Phase 0: Discovery

> **Phase 0: Discovery** decomposes the user's question from first principles,
> hypothesizes causal structures, acquires public data, and gates on data
> quality — all before any analysis strategy is formulated.

You are running Phase 0 for a **analysis** analysis named
**china_double_reduction_education**.

**Start in plan mode.** Before searching the web or writing any code,
produce a plan: what domain you expect, what entities and relationships you
will investigate, what data sources you will target, and what your artifact
structure will be. Execute after the plan is set.

---

## Input classification

Read `analysis_config.yaml` and `.analysis_config` to determine the input
mode. The mode governs how Phase 0 begins:

| Mode | Trigger | Behavior |
|------|---------|----------|
| **A — Question only** | No user data or context files provided | Fully autonomous: question decomposition, hypothesis generation, data requirements, acquisition, quality assessment. |
| **B — Question + user data** | `user_data_dir` set in `.analysis_config` | User data is a *starting point*, not a trusted source. Ingest it, then run the same quality assessment as autonomously acquired data. Supplement with additional public data as needed. |
| **C — Question + user hypotheses/context** | `user_context` set in `.analysis_config` | User hypotheses become *one candidate DAG* among agent-generated ones. They receive no trust privilege — all DAGs undergo equal scrutiny. |

**Non-negotiable:** User-provided data and hypotheses receive no trust
privilege. They undergo the same quality assessment and causal testing as
autonomously acquired data.

---

## Output artifacts

Phase 0 produces three artifacts, all written to the `exec/` directory:

| Artifact | Path | Contents |
|----------|------|----------|
| **DISCOVERY.md** | `exec/DISCOVERY.md` | Question decomposition, candidate first principles, causal DAGs (mermaid format), data requirements matrix, initial EP assessment |
| **data/** | `data/raw/`, `data/processed/`, `data/registry.yaml` | Raw downloaded data, processed/aligned datasets, and the provenance registry |
| **DATA_QUALITY.md** | `exec/DATA_QUALITY.md` | Per-dataset quality assessment, overall gate decision, warnings |

All three must exist before Phase 1 can begin. This is a hard gate.

---

## Agent profiles

Phase 0 uses three specialized agents. Read the applicable profile before
beginning each step:

| Agent | Profile | Steps |
|-------|---------|-------|
| Hypothesis agent | `.claude/agents/hypothesis-agent.md` | 0.1, 0.2 |
| Data acquisition agent | `.claude/agents/data-acquisition-agent.md` | 0.3, 0.4 |
| Data quality agent | `.claude/agents/data-quality-agent.md` | 0.5 |

The orchestrator delegates to these agents in sequence. Steps 0.1 and 0.2
run together (hypothesis agent). Steps 0.3 and 0.4 run together (data
acquisition agent). Step 0.5 is the quality gate (data quality agent).

---

## Step 0.1 — Question Decomposition

**Goal:** Parse the user's question into structured components that ground
all subsequent reasoning.

**The agent must:**

1. **Identify the domain.** What field(s) does this question belong to?
   (economics, demography, public health, technology, geopolitics, etc.)
   If the question spans multiple domains, name all and identify the primary.

2. **Extract entities.** List every named or implied entity: countries,
   organizations, populations, markets, technologies, policies, measurable
   quantities. Be exhaustive — missing an entity means missing a causal path.

3. **Map relationships.** For each pair of entities that might be causally
   related, state the hypothesized direction and mechanism. Use natural
   language at this stage; DAGs come in Step 0.2.

4. **Determine timeframe.** What temporal scope does the question cover?
   Historical (analysis of past events), current (present-day snapshot),
   prospective (projection into the future), or mixed? Identify key
   inflection dates if known.

5. **Surface implied concerns.** What is the user actually trying to
   understand or decide? A question like "Why is X declining?" implies
   concern about continuation, potential intervention points, and
   consequences. Make the implicit explicit.

**Output:** A structured decomposition table in DISCOVERY.md:

```markdown
## Question Decomposition

| Component | Value |
|-----------|-------|
| Raw question | [user's original text] |
| Domain(s) | [primary], [secondary if any] |
| Entities | [bulleted list] |
| Relationships | [entity A] -> [entity B]: [mechanism] |
| Timeframe | [start] to [end], type: [historical/current/prospective/mixed] |
| Implied concerns | [bulleted list] |
```

---

## Step 0.2 — First-Principles Hypothesization

**Goal:** Generate candidate causal DAGs grounded in first principles.
Avoid anchoring on the first hypothesis — always produce competing
alternatives.

**The agent must:**

1. **Identify candidate first principles.** For the domain(s) identified in
   Step 0.1, generate at least 3 candidate first principles that could
   govern the phenomena in question. A first principle is a foundational
   causal mechanism — not a surface correlation. Examples: supply/demand
   equilibrium, demographic transition theory, technological S-curves,
   institutional path dependence.

2. **Construct causal DAGs.** For each candidate first principle (or
   combination), construct a directed acyclic graph. Each node is a
   measurable variable or observable event. Each edge is a hypothesized
   causal link. Generate **at least 2 competing DAGs** to avoid anchoring.

3. **Label every edge.** Use the pre-analysis label taxonomy:

   | Label | Meaning | Example |
   |-------|---------|---------|
   | `LITERATURE_SUPPORTED` | Edge has published academic support (cite it) | "Urbanization reduces fertility (cite: Dyson 2011)" |
   | `THEORIZED` | Edge follows from domain theory but lacks direct empirical citation | "Cultural norm shift reduces desired family size" |
   | `SPECULATIVE` | Novel hypothesis without theoretical or empirical basis | "Social media algorithm changes affect birth timing" |

4. **Assess initial EP for each edge.** Before any data is acquired, use
   qualitative mapping to estimate Explanatory Power:

   **EP = truth x relevance**, where:

   - **Truth** (epistemic confidence):
     - `LITERATURE_SUPPORTED` : 0.7 (default; range 0.7-1.0 based on evidence strength)
     - `THEORIZED` : 0.4 (default; range 0.3-0.7 based on theoretical grounding)
     - `SPECULATIVE` : 0.2 (default; range 0.0-0.3)

   - **Relevance** (causal attribution fraction — what share of the target
     event's variance does this edge explain?):
     - Strong theoretical link : 0.7
     - Moderate theoretical link : 0.4
     - Weak theoretical link : 0.2

   EP values at this stage are qualitative estimates. They will be refined
   with actual data in Phase 3. The purpose here is to prioritize data
   acquisition and identify which edges matter most.

5. **Render DAGs in mermaid format.** Each DAG must be renderable. Annotate
   edges with labels and initial EP values:

   ```mermaid
   graph LR
     A[Urbanization] -->|LITERATURE_SUPPORTED<br>EP=0.47| B[Birth Rate Decline]
     C[Housing Cost] -->|CORRELATION<br>EP=0.21| B
   ```

6. **Cross-reference competing DAGs.** Identify where they agree (shared
   edges) and where they diverge (unique edges). Divergence points are
   the high-value targets for data acquisition.

**Output:** DISCOVERY.md sections for first principles, DAGs, and EP
assessment.

---

## Step 0.3 — Data Requirements Derivation

**Goal:** From the causal DAGs, derive exactly what data is needed to test
each edge.

**The agent must:**

1. **Build a data requirements matrix.** For every edge in every DAG,
   identify:
   - The independent variable(s) needed
   - The dependent variable(s) needed
   - Required temporal granularity (annual, quarterly, monthly, daily)
   - Required spatial granularity (global, national, subnational, city)
   - Minimum time span for meaningful analysis
   - Preferred data source(s) if known

2. **Prioritize by EP.** Edges with higher initial EP should have their
   data acquired first. Edges below the soft truncation threshold (Joint_EP
   < 0.15) get lightweight data search only.

3. **Identify overlapping requirements.** Multiple edges may need the same
   dataset. Consolidate to avoid redundant acquisition.

**Output:** Data requirements matrix in DISCOVERY.md:

```markdown
## Data Requirements

| DAG Edge | Variable | Granularity | Time Span | Priority | Source Candidates |
|----------|----------|-------------|-----------|----------|-------------------|
| A -> B | GDP per capita | Annual, national | 1990-2025 | HIGH | World Bank, FRED |
| A -> B | Urbanization rate | Annual, national | 1990-2025 | HIGH | World Bank |
| C -> B | Housing price index | Quarterly, national | 2005-2025 | MEDIUM | OECD, national stats |
```

---

## Step 0.4 — Data Acquisition

**Goal:** Acquire all required data from public sources. Log everything.

**Tools available:**
- `WebSearch` — discover data sources and APIs
- `WebFetch` — download data files and API responses
- `Bash` (within pixi) — run Python scripts for API calls, format conversion

**The agent must:**

1. **Search for each required variable.** Use WebSearch to find public data
   sources. Prefer authoritative sources: World Bank, FRED, OECD, UN
   agencies, national statistical offices, peer-reviewed datasets.

2. **Fetch and store data.** Download to `data/raw/` with immutable
   filenames: `{source_id}_{date}.{ext}`. Never overwrite existing raw
   files.

3. **Register every dataset in `data/registry.yaml`.** Each entry must
   include:

   ```yaml
   datasets:
     - id: "ds_001"
       name: "World Bank - GDP per capita"
       source_url: "https://api.worldbank.org/v2/..."
       retrieval_date: "2026-03-28"
       api_query: "indicator=NY.GDP.PCAP.CD&country=CHN"
       file_hash_sha256: "abc123..."
       raw_path: "data/raw/worldbank_gdp_pcap_20260328.csv"
       processed_path: "data/processed/gdp_per_capita.parquet"
       format: "CSV"
       temporal_coverage: "1960-2024"
       spatial_coverage: "China"
       variables: ["year", "gdp_per_capita_usd"]
       limitations: "2-year reporting lag; PPP-adjusted version also available"
   ```

4. **Process and standardize.** Convert all acquired data to a common
   format in `data/processed/`:
   - Tabular data to Parquet files
   - Time series aligned to a common temporal index
   - Missing values explicitly marked (never zero-filled)
   - Units documented in `registry.yaml`

5. **Handle failures gracefully.** Follow this fallback cascade:

   | Failure | Action |
   |---------|--------|
   | API rate-limited | Retry with exponential backoff (max 3 attempts), then fall back to WebSearch for alternative source |
   | Source unavailable | Log in DATA_QUALITY.md as "Source unavailable: {URL}", reduce affected variable's quality to LOW |
   | No data found for required variable | State explicitly in DISCOVERY.md: "Variable X required but no public data found. Analysis cannot assess causal edge Y->Z." |
   | Authentication required | Skip source, log as "Requires authentication (not accessible)", search for alternative public source |

6. **Caching and reproducibility.** All raw files in `data/raw/` are
   immutable. `registry.yaml` is the single source of truth for
   provenance. Re-running Phase 0 on the same question uses cached data
   by default (override with `force_refresh=true` in analysis_config).

**For Mode B (user data):** Ingest user-provided data into `data/raw/` with
a `user_provided: true` flag in the registry. Run the same quality checks
in Step 0.5 — no trust privilege.

### Data Callback Protocol

Later phases (especially Phase 3) may discover they need additional data
not anticipated during initial acquisition. The orchestrator can invoke a
**data callback** — a re-run of Steps 0.3-0.5 for specific variables.

**Callback triggers (orchestrator decides):**
- A causal edge with EP > 0.30 cannot be tested due to missing data
- Phase 2 EDA reveals a confounding variable not in the original DAGs
- A reviewer flags a data gap as Category A

**Callback guards (prevent infinite loops):**
- Maximum 2 callbacks per analysis (hard cap)
- Each callback must justify: what new data is needed, which DAG edge it
  supports, and why Phase 0 didn't acquire it
- Re-acquired data goes through the same quality gate (Step 0.5)
- Callback data is appended to `registry.yaml`, never overwrites existing

**Multi-strategy search (before declaring "no data found"):**
When a required variable cannot be found through the primary source, the
data acquisition agent MUST try these fallback strategies in order:

1. **Alternative APIs:** World Bank, FRED, OECD, UN, IMF, national stats
2. **Proxy variables:** Find a measurable proxy for the unmeasurable concept
3. **Academic datasets:** Search data repositories (Harvard Dataverse, Zenodo, Kaggle)
4. **Report extraction:** Use `scripts/data_extractor.py` to extract numbers
   from PDF/web reports with confidence labeling
5. **Composite indicators:** Construct from available sub-components

Only after exhausting all 5 strategies may the agent declare "no data found."
Document each failed strategy in the experiment log.

**Output:** Populated `data/` directory and complete `registry.yaml`.

---

## Step 0.5 — Data Quality Assessment (Hard Gate)

**Goal:** Assess the quality of every acquired dataset and make a gate
decision. This step determines whether the analysis can proceed and with
what caveats.

**The agent must:**

1. **Assess each dataset individually.** For every entry in
   `registry.yaml`, evaluate:

   | Dimension | What to check | Scale |
   |-----------|--------------|-------|
   | **Completeness** | Missing values, temporal gaps, spatial coverage holes | 0.0-1.0 |
   | **Consistency** | Internal consistency, cross-source agreement, unit coherence | 0.0-1.0 |
   | **Bias assessment** | Sampling bias, reporting bias, survivorship bias, measurement methodology changes | Free text + severity rating |
   | **Granularity** | Does temporal/spatial resolution match what the DAG edges require? | Adequate / Marginal / Insufficient |

2. **Assign a verdict per dataset:**

   | Verdict | Criteria | Implication |
   |---------|----------|-------------|
   | **HIGH** | Completeness > 0.9, consistency > 0.85, granularity adequate, no severe biases | Full confidence in conclusions drawn from this data |
   | **MEDIUM** | Completeness > 0.7, consistency > 0.7, granularity at least marginal | Conclusions valid but hedge with caveats; widen uncertainty bands |
   | **LOW** | Below MEDIUM thresholds, severe biases, or insufficient granularity | Prominent warnings required; cannot support strong causal claims from this data alone |

3. **Make the overall gate decision.** The gate considers all datasets
   together:

   - If ALL datasets supporting high-EP edges are HIGH or MEDIUM: **PROCEED**
   - If ANY dataset supporting a high-EP edge is LOW: **PROCEED WITH WARNINGS**
     — the analysis continues but must carry prominent data quality warnings
     through every subsequent phase artifact
   - Never fabricate precision from poor data. A LOW-quality dataset
     supporting a critical edge means that edge's EP.truth is capped at 0.3
     regardless of other evidence.

4. **Write DATA_QUALITY.md.** Structure:

   ```markdown
   # Data Quality Assessment

   ## Per-Dataset Assessment

   ### ds_001: World Bank - GDP per capita
   - **Completeness:** 0.95 — annual data 1960-2024, 2 missing years
   - **Consistency:** 0.88 — methodology change in 2015 (PPP revision)
   - **Bias assessment:** Reporting bias possible for early years; post-2000
     data considered reliable
   - **Granularity:** Adequate (annual national, matches DAG requirements)
   - **Verdict:** HIGH

   [... repeat for each dataset ...]

   ## Overall Gate Decision
   - **Overall quality:** MEDIUM
   - **Proceed:** YES
   - **Warnings:**
     - Dataset ds_003 (housing prices) has LOW completeness for pre-2005 period
     - Edge C->B analysis limited to 2005-2025 window
   ```

**Gate rule:** If overall quality is LOW, the analysis proceeds with
prominent warnings. **Never halt an analysis solely on data quality** — an
honest analysis with acknowledged limitations is more valuable than no
analysis. But never fabricate precision from poor data either.

---

## EP Estimation Guidance for Phase 0

All EP values in Phase 0 are pre-analysis estimates. They serve two
purposes: (1) prioritize data acquisition, and (2) set expectations for
Phase 1 strategy.

**Qualitative mapping (use when no quantitative data is yet available):**

| Evidence strength | Default truth value | Range |
|-------------------|-------------------|-------|
| Strong published evidence (LITERATURE_SUPPORTED) | 0.7 | 0.7 - 1.0 |
| Domain theory without direct citation (THEORIZED) | 0.4 | 0.3 - 0.7 |
| Novel or weakly grounded hypothesis (SPECULATIVE) | 0.2 | 0.0 - 0.3 |

| Causal relevance | Default relevance value |
|------------------|----------------------|
| Strong theoretical link (primary mechanism) | 0.7 |
| Moderate theoretical link (contributing factor) | 0.4 |
| Weak theoretical link (indirect or uncertain) | 0.2 |

**EP = truth x relevance.** Example: a LITERATURE_SUPPORTED edge (truth =
0.7) with moderate relevance (0.4) has EP = 0.28.

**Truncation thresholds (applied to Joint_EP along chains):**

| Threshold | Value | Action |
|-----------|-------|--------|
| Hard truncation | 0.05 | Stop exploring this chain. Label "Beyond analytical horizon." |
| Soft truncation | 0.15 | Lightweight assessment only. No sub-chain expansion. |
| Sub-chain expansion minimum | 0.30 | Full sub-analysis justified if expansion expected to change conclusions. |

These thresholds are tunable. If experience suggests different values, note
the recommendation in the experiment log for calibration.

---

## Methodology references

- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (4-bot review)

---

## Non-negotiable rules

1. **Never fabricate data.** If a required dataset cannot be found, say so
   explicitly. An honest "insufficient data for edge X->Y" is infinitely
   better than a hallucinated dataset. Fabricated data is a Category A
   finding that blocks all downstream phases.

2. **Never assume causation without evidence.** Phase 0 produces
   *hypothesized* causal DAGs. Every edge is labeled with its evidence
   basis. No edge is treated as established fact until Phase 3 refutation
   testing.

3. **Always generate competing hypotheses.** A single DAG is an anchored
   analysis. Produce at least 2 competing DAGs with materially different
   causal structures. If you cannot think of alternatives, you have not
   thought hard enough.

4. **User-provided data/hypotheses receive no trust privilege.** Mode B
   user data undergoes the same quality assessment as acquired data. Mode C
   user hypotheses are one candidate among several — not the default.

5. **Data quality gates are hard gates.** LOW quality triggers prominent
   warnings, not pretended precision. Every subsequent artifact must carry
   forward data quality caveats from Phase 0.

6. **Log everything.** Every data source gets a `registry.yaml` entry.
   Every failed search gets logged. Every decision gets an experiment log
   entry. Phase 0 without an experiment log is incomplete.

7. **Cite all sources.** Every data point traces to a URL and retrieval
   date. Every first principle cites its theoretical basis. Every
   LITERATURE_SUPPORTED edge cites at least one publication.

8. **Append to the experiment log.** Document every material decision:
   why you chose one data source over another, why a hypothesis was
   included or excluded, what searches failed and why. The experiment log
   is the audit trail for Phase 0 reasoning.

---

## Review

**4-bot review** — see `methodology/06-review.md` for protocol.

Reviewers evaluate:
- Is the question decomposition complete? Are there missing entities or
  relationships?
- Do the causal DAGs represent genuinely different hypotheses, or are they
  minor variations of the same structure?
- Are edge labels (LITERATURE_SUPPORTED / THEORIZED / SPECULATIVE)
  justified? Are citations provided for LITERATURE_SUPPORTED edges?
- Are EP estimates reasonable given the evidence basis?
- Is the data acquisition thorough? Were obvious public sources missed?
- Is the data quality assessment honest and well-calibrated?
- Is registry.yaml complete with full provenance for every dataset?

Write findings to `review/REVIEW_NOTES.md`.
