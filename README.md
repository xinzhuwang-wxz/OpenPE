# OpenPE — Principle to Endgame

Autonomous first-principles analysis framework. An orchestrator agent
delegates work to specialized subagents through seven sequential phases,
producing a comprehensive report from any user question.

## Quick start

```bash
pixi run scaffold analyses/my_analysis
cd analyses/my_analysis
# Edit analysis_config.yaml → set question, domain, input_mode
pixi install
claude   # starts the orchestrator agent
```

## How it works

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                             │
│  Never writes code. Holds: question, summaries, verdicts     │
└─────┬───────────────────────────────────────────────────────┘
      │
      ▼
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Phase 0  │──▶│ Phase 1  │──▶│ Phase 2  │──▶│ Phase 3  │──▶│ Phase 4  │──▶│ Phase 5  │──▶│ Phase 6  │
 │Discovery │   │ Strategy │   │ Explore  │   │ Analysis │   │Projection│   │ Verify   │   │ Document │
 │ (4-bot)  │   │ (4-bot)  │   │ (self)   │   │ (4-bot)  │   │ (4-bot)  │   │(4-bot+HG)│   │ (5-bot)  │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘   └──────────┘
                                                                                  │
                                                                            HUMAN GATE
```

Each phase runs the same loop:

```
  1. EXECUTE ── spawn executor subagent (enters plan mode first)
  2. REVIEW ─── spawn reviewer(s) per review tier
  3. CHECK:
       Regression trigger? → Investigator → fix origin + downstream → resume
       A or B items?       → fix agent + fresh reviewer → re-review (loop)
       Only C items?       → PASS, executor applies Cs before commit
  4. COMMIT
  5. HUMAN GATE (after Phase 5 Verification)
  6. ADVANCE
```

### Phases

| Phase | Review | Key deliverable |
|-------|--------|-----------------|
| **0. Discovery** | 4-bot | Question decomposition, causal DAG, data acquisition, quality gate |
| **1. Strategy** | 4-bot | Method selection, EP assessment, chain planning, systematic inventory |
| **2. Exploration** | Self | Data cleaning, feature engineering, variable ranking by EP |
| **3. Analysis** | 4-bot | Causal testing (3 refutations), EP propagation, sub-chain expansion |
| **4. Projection** | 4-bot | Scenario simulation, sensitivity analysis, endgame convergence |
| **5. Verification** | 4-bot + HG | Independent reproduction, data provenance audit, logic audit, human gate |
| **6. Documentation** | 5-bot | Complete report (pandoc → PDF), EP decay visualization, audit trail |

The human gate is between Phase 5 and Phase 6.

### Core concepts

**Explanatory Power (EP).** Each node in the causal chain carries an EP
score = f(truth, relevance). Joint EP decays along the chain. When Joint EP
falls below 0.05, the chain is truncated — this is the natural analytical
horizon.

**Input modes.** Users can provide:
- Mode A: Question only (agent acquires data autonomously)
- Mode B: Question + user data (data still goes through quality gate)
- Mode C: Question + user hypotheses (hypotheses compete with agent-generated ones)

**Causal testing.** Every causal claim must pass 3 refutation tests (placebo,
random common cause, data subset). Results are labeled:
DATA_SUPPORTED / CORRELATION / HYPOTHESIZED / DISPUTED.

**Self-evolution.** The memory system (L0/L1/L2 tiers + causal knowledge
graph) accumulates experience across analyses. Domain packs grow
automatically.

### Review classification

| Cat | Meaning | Action |
|-----|---------|--------|
| **A** | Would invalidate conclusions | Fix + re-review + fresh reviewer |
| **B** | Weakens the analysis | Same — must be zero before PASS |
| **C** | Style / clarity | Arbiter PASses; executor applies before commit |

### Phase regression

Any review can trigger regression when an issue is traceable to an earlier
phase. The investigator traces impact, writes a REGRESSION_TICKET.md, then
the fix cycle re-runs affected phases.

## Directory structure

```
OpenPE/
  src/                        Spec infrastructure
    methodology/              Methodology spec (human reference)
    orchestration/            Session management (human reference)
    conventions/              Domain knowledge (symlinked into analyses)
    templates/                CLAUDE.md, pixi.toml, and script templates
    scaffold_analysis.py      Scaffolder
  analyses/                   Each is its own git repo
    <name>/
      CLAUDE.md               Self-contained orchestrator instructions
      pixi.toml               Environment + task graph
      analysis_config.yaml    Question, domain, EP thresholds
      .analysis_config        data_dir + allow paths for isolation hook
      conventions/ → src/conventions/
      memory/                 L0/L1/L2/causal_graph (per-analysis memory)
      phase{0..6}_*/          Phase dirs with CLAUDE.md, exec/, scripts/, figures/, review/
```

## How scaffolding works

The scaffolder (`pixi run scaffold`) creates a new analysis directory:

1. **Template files** (`root_claude.md`, `phase*_claude.md`, `pixi.toml`)
   are copied with `{{name}}` and `{{analysis_type}}` placeholders replaced.
2. **Seven phase directories** (`phase0_discovery/` through
   `phase6_documentation/`) are created with standard subdirs.
3. **Helper scripts** (EP engine, causal pipeline, data fetchers, etc.) are
   copied into `phase0_discovery/scripts/`.
4. **Memory structure** (`memory/L0_universal/`, `L1_domain/`, `L2_detailed/`,
   `causal_graph/`) is initialized.
5. **Symlinks** — `conventions/`, `methodology/`, `.claude/` point back to
   the parent project.
6. **Git repo** is initialized in the analysis directory.

## Requirements

- [pixi](https://pixi.sh) for environment management
- [Claude Code](https://claude.ai/claude-code) as the agent runtime
