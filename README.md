<div align="center">

# OpenPE — Principle to Endgame

**LLM-driven first-principles causal analysis framework**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-orange.svg)](https://claude.ai/claude-code)

[English](README.md) · [中文](README_zh.md) · [한국어](README_ko.md)

</div>

---

Every event has a cause. Every cause has a cause. This forms a network — not a line, a network. Each node is the center of its own web of causes and consequences.

But the network doesn't expand forever. The further you trace from the origin, the weaker the explanatory signal becomes — multiplicatively, not linearly. At some point the trail goes cold. That boundary isn't a flaw. It's the natural horizon of what can be understood from a given starting point.

OpenPE works within that horizon. It builds causal graphs from first principles, tests every link against refutation, and projects forward only as far as the evidence can carry — from **principle** to **endgame**.

---

## Quick Start

### Option 1: Manual Setup

```bash
git clone https://github.com/xinzhuwang-wxz/OpenPE.git
cd OpenPE

# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Scaffold your first analysis
python src/scaffold_analysis.py analyses/my_analysis
cd analyses/my_analysis

# Configure
# Edit analysis_config.yaml → set question and domain
pixi install
claude   # starts the orchestrator agent
```

### Option 2: One-Shot with Claude Code

Paste this directly into [Claude Code](https://claude.ai/claude-code):

```
Clone https://github.com/xinzhuwang-wxz/OpenPE and use OpenPE's scaffolding + orchestrator flow to complete this analysis: <your question here>
```

Claude Code will scaffold the analysis, install dependencies, and run all seven phases autonomously — producing a full report with causal DAGs, refutation tests, scenario projections, and an audit trail.

---

## How It Works

```
Question ─→ Phase 0: Discovery ─→ Phase 1: Strategy ─→ Phase 2: Exploration
                │                      │                     │
           Causal DAGs            Method Selection        EDA + Figures
           Data Acquisition       EP Assessment            Distribution Checks
           Quality Gate           Chain Planning
                │                      │                     │
                ▼                      ▼                     ▼
           Phase 3: Analysis ─→ Phase 4: Projection ─→ Phase 5: Verification
                │                      │                     │
           Causal Testing         Monte Carlo Scenarios   Independent Reproduction
           3-Refutation Battery   Sensitivity Tornado     EP Propagation Audit
           EP Propagation         Endgame Classification  Causal Label Audit
                │                      │                     │
                ▼                      ▼                     ▼
                         Phase 6: Documentation
                              │
                         Analysis Note (MD + PDF)
                         Audit Trail (Claims + Sources + Logic)
                         EP Decay Visualization
```

Each phase follows the same loop:

1. **EXECUTE** — Subagent produces artifact (starts in plan mode)
2. **REVIEW** — Independent reviewers classify issues as A (blocking) / B (must fix) / C (suggestion)
3. **CHECK** — Arbiter decides pass/iterate/regress
4. **COMMIT** — State tracked in STATE.md
5. **HUMAN GATE** — After Phase 5, human approves before final report

---

## Three Core Innovations

### 1. Explanatory Power (EP) — Quantified Reasoning Under Uncertainty

Most analysis frameworks treat confidence as a binary: "we believe this" or "we don't." OpenPE introduces **Explanatory Power** — a continuous, multiplicative measure that tracks how much explanatory value survives along a causal chain.

```
EP = truth × relevance

truth:     How confident are we that this causal link is real? (0–1)
relevance: How much of the outcome's variance does this link explain? (0–1)
```

Along a causal chain A → B → C → D, **Joint EP decays multiplicatively**:

```
Joint_EP = EP(A→B) × EP(B→C) × EP(C→D)
```

This has a profound consequence: long causal chains naturally lose explanatory power. A 5-link chain where each edge has EP=0.7 yields Joint_EP = 0.17 — barely above the soft truncation threshold. The framework enforces explicit stopping rules:

| Threshold | Joint EP | Action |
|-----------|----------|--------|
| **Hard truncation** | < 0.05 | Stop exploring. This chain is beyond the analytical horizon. |
| **Soft truncation** | < 0.15 | Lightweight assessment only. No sub-chain expansion. |
| **Sub-chain expansion** | > 0.30 | Worth investigating in detail. Scaffold a sub-analysis. |

EP values evolve across the analysis lifecycle. Pre-analysis labels (`LITERATURE_SUPPORTED` → truth=0.70, `THEORIZED` → 0.40, `SPECULATIVE` → 0.15) are updated by Phase 3 refutation testing to post-analysis classifications (`DATA_SUPPORTED` → 0.85, `CORRELATION` → 0.50, `HYPOTHESIZED` → 0.15, `DISPUTED` → 0.30).

**Why this matters:** EP makes the decay of analytical confidence visible and quantifiable. Rather than burying uncertainty in prose hedging, every causal argument carries a number that the reader can trace and challenge.

### 2. Placebo-Anchored Contradiction Detection (DISPUTED Classification)

Standard causal inference treats refutation results as a scorecard: more tests pass → stronger evidence. OpenPE adds a semantic layer that detects **logical contradictions** in the evidence pattern.

Every causal edge undergoes three refutation tests:
- **Placebo treatment** — Replace treatment with random variable; effect should vanish
- **Random common cause** — Add random confounder; estimate should remain stable
- **Data subset** — Estimate on random 80% subsets; should be consistent

The classification uses **placebo as the causal anchor**:

- If placebo **passes** (effect is treatment-specific / "real"), then subset and common_cause failures are contradictory — a real effect should be stable and robust to confounders
- If placebo **fails** (effect is not treatment-specific), then subset passing is contradictory — a non-real effect cannot be perfectly stable

When these contradictions are detected, the edge is classified as `DISPUTED` — not DATA_SUPPORTED, not CORRELATION, but a flag for human review. The framework refuses to auto-classify contradictory evidence.

```python
# Contradiction detection logic (Scheme C)
if placebo_passed and (not subset_passed or not cc_passed):
    return "DISPUTED"   # Real but unstable/confounded — contradictory
if not placebo_passed and subset_passed:
    return "DISPUTED"   # Not real but perfectly stable — contradictory
```

**Why this matters:** Most frameworks force a classification even when the evidence disagrees with itself. DISPUTED acknowledges that some patterns don't have a clean answer — and routes them to human judgment rather than algorithmic guessing.

### 3. Cross-Analysis Memory with Evidence-Driven Tier Transitions

OpenPE analyses don't start from zero. A tiered memory system accumulates domain knowledge across analyses, with confidence-driven lifecycle management:

| Tier | Scope | Loading | Content |
|------|-------|---------|---------|
| **L0** | Universal | Always loaded | Cross-domain principles validated by ≥3 analyses |
| **L1** | Domain | Loaded for matching domain | Domain-specific experiences (methods, data sources, failures) |
| **L2** | Detail | On-demand | Full analysis summaries (auto-generated) |

Memories aren't static. They evolve:

```
Created (L1, conf=0.50)
  → Corroborated by 2nd analysis (+0.15 → 0.65)
  → Corroborated by 3rd analysis (+0.15 → 0.80) → PROMOTED to L0
  → Contradicted by 4th analysis (-0.25 → 0.55)
  → Contradicted by 5th analysis (-0.25 → 0.30) → DEMOTED back to L1
  → Decays over time (-0.01 per analysis)
  → Eventually: conf < 0.05 AND hotness < 0.01 → FORGOTTEN (deleted)
```

The lifecycle is fully automated in `commit_session()`:
- **Promotion** (L1→L0): ≥2 independent corroborations
- **Demotion** (L0→L1): confidence drops below 0.30
- **Forgetting**: confidence ≤ 0.05 AND hotness < 0.01 → file deleted
- **Archival**: cold L2 entries (hotness < 0.1) moved to `_archive/`
- **Idempotent commit**: marker file prevents double-decay on crash+restart

Global memory lives at the repo root (`memory/`). Each new analysis inherits a snapshot via scaffolding and promotes high-confidence findings back after completion.

**Why this matters:** The 3rd analysis in a domain is better than the 1st — not because the code improved, but because the memory system learned what works and what doesn't.

---

## Adapted Foundations

OpenPE builds on ideas from three notable projects, adapted to fit the first-principles analysis context:

### ACG Protocol → Audit Trail (IGM/SSR/VAR)

The [ACG Protocol](https://github.com/Kos-M/acg_protocol) introduced Inline Grounding Markers and source verification registries for fact-grounded text generation. OpenPE adapts this into a three-layer audit trail:

- **IGM** (Inline Grounding Markers): `[C1:a1b2c3d4e5:phase3/data.csv:row42]` — every claim embeds a hash linking to its source
- **SSR** (Structured Source Registry): SHA-256 hashes, source types, verification status per dataset
- **VAR** (Veracity Audit Registry): tracks inferential logic chains with `verify_logic()` for automated consistency checking

### Graphiti → Temporal Causal Knowledge Graph

[Graphiti](https://github.com/getzep/graphiti)'s temporal EntityEdge model inspired the validity-window pattern in OpenPE's causal knowledge graph. Relationships carry `valid_at`/`invalid_at`/`expired_at` timestamps, enabling the graph to record *when* a causal mechanism was true — not just *whether* it's true. Combined with confidence-driven reuse policies (SKIP / LIGHTWEIGHT_VERIFY / MUST_RETEST), this allows high-confidence relationships to skip re-testing in future analyses.

### OpenViking → Memory Hotness Scoring

[OpenViking](https://github.com/volcengine/OpenViking)'s memory lifecycle system provided the hotness scoring formula: `sigmoid(frequency) × exponential_recency`. OpenPE uses this to distinguish actively-used memories from stale ones, driving the archival and forgetting mechanisms that keep the memory system bounded.

## Input Modes

| Mode | When | Behavior |
|------|------|----------|
| **A** — Question only | No data provided | Fully autonomous: hypothesis, data acquisition, quality gate |
| **B** — Question + data | User provides datasets | User data passes through the same quality gate as acquired data |
| **C** — Question + hypotheses | User provides causal hypotheses | User hypotheses become one candidate DAG — no trust privilege |

---

## Requirements

- **Python** ≥ 3.11
- **[pixi](https://pixi.sh)** — dependency management (installs everything else)
- **[Claude Code](https://claude.ai/claude-code)** — LLM orchestrator
- **pandoc** ≥ 3.0 + xelatex — PDF generation (installed via pixi)

---

## Acknowledgments

OpenPE originated from [slop-X](https://github.com/jfc-mit/slop-X) and generalizes it to any domain.

We also draw inspiration and adapt patterns from these open-source projects:

| Project | What We Borrowed | License |
|---------|-----------------|---------|
| [ACG Protocol](https://github.com/Kos-M/acg_protocol) | UGVP fact grounding (IGM/SSR/VAR audit structures) | — |
| [Graphiti](https://github.com/getzep/graphiti) | Temporal EntityEdge validity model for knowledge graphs | Apache-2.0 |
| [OpenViking](https://github.com/volcengine/OpenViking) | Memory lifecycle hotness scoring (`sigmoid × recency`) | Apache-2.0 |
| [Causica](https://github.com/microsoft/causica) | Graph evaluation metrics patterns | MIT |
| [causal-learn](https://github.com/py-why/causal-learn) | PC algorithm for causal structure discovery | MIT |
| [DoWhy](https://github.com/py-why/dowhy) | Causal inference + refutation testing framework | MIT |
| [DeerFlow](https://github.com/bytedance/deer-flow) | Multi-agent orchestration patterns | MIT |

The development workflow was powered by [Superpowers](https://github.com/cline/superpowers-marketplace) skills for Claude Code — particularly `writing-plans`, `subagent-driven-development`, `test-driven-development`, and `code-reviewer`.

---

## License

[GPL-3.0](LICENSE) — Free to use, modify, and distribute. Derivative works must also be open-source under GPL-3.0.
