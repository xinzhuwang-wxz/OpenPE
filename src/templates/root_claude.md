<!-- Spec developer note: agent prompt templates live in
     src/orchestration/agents.md. Context assembly rules are in
     src/methodology/04-orchestration.md §3a.4.2. -->

# Analysis: {{name}}

Type: {{analysis_type}}

**Sections:** Execution Model · Methodology · Environment · Tool
Requirements · Phase Gates · Review Protocol · Phase Regression · Coding
Rules · Scale-Out · Plotting · Conventions · Analysis Note Format ·
Feasibility · Reference Analyses · Pixi Reference · Git

---

## Execution Model

**You are the orchestrator.** You do NOT write analysis code yourself. You
delegate to subagents. Your context stays small; heavy work happens in
subagent contexts.

**All executor subagents start in plan mode.** When spawning an executor,
instruct it to first produce a plan: what scripts it will write, what figures
it will produce, what the artifact structure will be. The subagent executes
only after the plan is set. This prevents agents from diving into code
without thinking.

**Memory loading at analysis start.** Before Phase 0, copy the global
`memory/` directory (at the spec root) into the analysis-local `memory/`
directory. Pass the memory context string to each phase executor:

```bash
cd analyses/{name}
pixi run py scripts/session_commit.py --load-only --domain {domain}
# outputs memory context to include in phase_context_N.md
```

Each phase agent receives L0 (universal principles, always loaded) and
L1 entries matching the analysis domain in its phase_context_N.md under
a `## Prior Experience` section.

**Memory commit at analysis end.** After Phase 6 completes and is committed,
run the session commit to extract experiences and promote to global memory:

```bash
cd analyses/{name}
pixi run py scripts/session_commit.py --analysis-id {name} --global-memory {spec_root}/memory
```

This writes L1 experiences, an L2 summary, seeds L0 universal principles
(idempotent), and promotes high-confidence entries (≥0.6) to global memory.
Run this once per completed analysis — the commit marker prevents double-decay.

**The orchestrator loop for each phase:**

```
for each phase in [0, 1, 2, 3, 4, 5, 6]:

  1. EXECUTE — spawn a phase executor subagent (start in plan mode) with:
     - The analysis question and context
     - The phase CLAUDE.md (read from disk, pass in prompt)
     - Paths to upstream artifacts (subagent reads from disk)
     - The experiment log path (subagent appends to it)
     - The conventions directory path (for phases that need it)
     - Instruction to write the phase artifact to disk

  2. REVIEW — spawn reviewer subagent(s) with:
     - Path to the phase artifact just written
     - The review criteria for this phase
     - The conventions directory path
     - Instruction to write REVIEW_NOTES.md in the phase directory

  3. CHECK — read the arbiter decision and structured fix instructions.
     If regression trigger: → Phase Regression protocol (see below).
     If ITERATE:
       **First, check routing before spawning anything:**
       - **B-only** (`b_only: true` in REVIEW_NOTES.md, a_count=0) — this
         path applies regardless of iteration count (including 3rd+):
         Apply all B fixes: exact fixes via Edit tool; reasoning fixes inline
         (orchestrator applies them directly without spawning fix agents).
         Write `phase*/review/B_SELF_VERIFY.md` with one line per fix:
           - B{id} [{description}]: APPLIED — {file}:{section}, "{old_snippet}" → "{new_snippet}"
         If ANY fix cannot be written as APPLIED, escalate to full arbiter.
         **Orchestrator spot-check (mandatory before COMMIT):** For every
         `type: exact` fix listed as APPLIED, use the Read tool to read the
         target file section and confirm the `new` text is present and the
         `old` text is absent. If any spot-check fails: do NOT commit —
         escalate to full arbiter with the failing fix id(s) noted.
         If ALL spot-checks pass → proceed directly to COMMIT. No arbiter spawn.
       - **A-present** (a_count > 0):
         a. Apply `exact` fixes (old→new text) directly via Edit tool.
         b. Spawn one fix agent **per** `requires_reasoning` fix, all in parallel.
            Each agent receives: the fix's `file`, `section`, `instruction`, and
            `reason` fields from REVIEW_NOTES.md. Fixes target different
            file+section pairs and are independent — do not serialize them.
            Wait for all parallel fix agents to complete before re-verify.
         c. Re-verify: Continue the original arbiter via SendMessage with
            scoped context: pass (1) the previous REVIEW_NOTES.md, (2) the
            `git diff HEAD` of the artifact file(s) that were edited, and
            (3) a one-line summary: "Fixes applied for: A1, A2, B3. Verify
            these are resolved and check the diff for new issues."
            Do NOT re-pass the full artifact — the arbiter already has it.
            On 3rd+ iteration, spawn a new arbiter instance instead of
            continuing the original via SendMessage; pass the same scoped
            context PLUS all prior REVIEW_NOTES.md files (in chronological
            order) as "prior iteration history."
     If only Category C or no issues: apply all Category C `exact` fixes in
     parallel (multiple Edit tool calls in a single message — they target
     independent file+section pairs). Then proceed.

  4. COMMIT — commit the phase's work.

  4b. STATE_UPDATE — Update STATE.md directly using the Edit tool:
     - Set `current_phase` to N, `phase_{N}_status` to COMPLETE, record the
       artifact path and review verdict (PASS/ITERATE count)
     - STATE.md is the single source of truth for pipeline progress
     - On resumption after interruption, read STATE.md to determine where to restart
     - (`scripts/state_manager.py` is a library for analysis scripts — it has
       no CLI; the orchestrator edits STATE.md directly)

  5. HUMAN GATE (after Phase 5 only):
     Present the verification report, key causal findings, EP propagation
     summary, and projection scenarios to the human. Pause until approved.

  6. ADVANCE — proceed to next phase.
```

**Agent roster and phase mapping:**

| Phase | Executor agent(s) | Role |
|-------|-------------------|------|
| 0: Discovery | `hypothesis-agent` → `data-acquisition-agent` (parallel by source) → `data-quality-agent` | Question decomposition, DAG construction, parallel data acquisition, quality gate |
| 1: Strategy | `lead-analyst` | Analysis strategy from DAGs and data |
| 2: Exploration | `data-explorer` | Exploratory data analysis, distribution checks |
| 3: Causal Analysis | `analyst` (single or split by edge count — see below) | Causal testing, refutation, statistical modeling |
| 4: Projection | `projector-agent` | Forward projection, scenario analysis |
| 5: Verification | `verifier` | Cross-validation, sensitivity analysis, EP reconciliation |
| 6: Documentation | `report-writer` (ANALYSIS_NOTE first, then REPORT) + `plot-validator` | Final report, sequential AN→REPORT then PDF |

**Dynamic context splitting — Phase 3:** The orchestrator counts primary
causal edges (those marked "full analysis" in STRATEGY.md).

- **0 edges (all lightweight or no full-analysis edges):** Run Phase 3 as a
  single subagent covering only lightweight assessments and sub-chain
  expansion decisions. No refutation battery. Document all edges as
  "lightweight assessment only" with justification.
- **1–2 edges:** Run Phase 3 as a single subagent (Steps 3.1–3.7 together).
- **3–5 edges:** Split by edge: spawn one analyst sub-agent per edge for
  Steps 3.1–3.5 in **parallel**. Each sub-agent receives `phase_context_3.md`
  plus its assigned edge name and the STRATEGY.md entries for that edge only.
  Each sub-agent writes its partial results to `exec/edge_{edge_name}/ANALYSIS_PARTIAL.md`.
  After all parallel edge agents complete, spawn a single verifier sub-agent
  for Steps 3.6–3.7 that globs `exec/edge_*/ANALYSIS_PARTIAL.md`, merges
  all per-edge results, and produces the unified `exec/ANALYSIS.md`.
- **>5 edges:** Same parallel pattern as 3–5 edges. Run agents in waves of 3
  concurrent spawns: spawn the first 3 edge agents, wait for all to complete
  (use Read tool to confirm `exec/edge_{edge_name}/ANALYSIS_PARTIAL.md` exists
  for each agent in the wave before proceeding), spawn the next 3, and so on
  until all edges are processed. The verifier sub-agent runs once after all
  waves complete.

The verifier sub-agent (Steps 3.6–3.7) always runs as a single invocation
after all edge agents complete — it reads `exec/edge_*/ANALYSIS_PARTIAL.md`
from disk and constructs the statistical model and uncertainty quantification
across all edges jointly.

**Pre-generated phase context.** Before spawning ANY subagent for Phase N,
assemble `phase*/context/phase_context_N.md` using the Read tool. Structure:

  ```markdown
  # [Analysis Name] — Phase N Context

  ## Bird's-Eye Framing
  - Physics/research question: [from analysis prompt]
  - Analysis type: [from analysis_config.yaml]
  - Phase N goal: [what this phase must deliver]
  - End goal: publication-quality analysis note

  ## Upstream Artifact Summaries (link to full files for agent reference)
  - DISCOVERY.md summary: [3-5 bullets — key decomposition, data sources, EP priors]
  - STRATEGY.md summary: [3-5 bullets — method selections, EP values for primary edges]
  - EXPLORATION.md summary: [2-3 bullets — data quality findings]  ← Phase 3+ only
  - ANALYSIS.md summary: [2-3 bullets — causal findings, classifications]  ← Phase 4+ only

  ## Methodology Sections for Phase N
  [Paste relevant sections from methodology/ per §3a.4.2 table]

  ## Applicable Conventions Excerpt
  [Paste the required-checks section from conventions/ for this analysis technique]
  ```

Pass this single file to ALL subagents for Phase N (executor, all reviewers,
arbiter). Do NOT ask each subagent to read methodology/ and upstream artifacts
separately. Regenerate `phase_context_N.md` only if upstream methodology files
or artifacts change between phases.

**Phase context pre-assembly (pipeline parallelism).** While Phase N's
executor is running, pre-assemble the static sections of `phase_context_{N+1}.md`:
read and write the "Methodology Sections" and "Applicable Conventions Excerpt"
blocks — these come from fixed methodology/ and conventions/ files that do not
depend on Phase N's output. Leave the "Upstream Artifact Summaries" section
as a placeholder. When Phase N completes, fill in the summaries and the file
is ready immediately. This moves ~70% of context assembly off the critical path.

**Reviewer context scoping.** When spawning reviewers, do NOT pass the full
`phase_context_N.md` + full artifact to every reviewer. Instead, pass each
reviewer a scoped slice containing only what their role requires:

| Reviewer | Artifact sections to pass | Context sections to pass |
|----------|--------------------------|--------------------------|
| Domain reviewer | Domain interpretation, causal findings, results summary, figures list | Bird's-eye framing only |
| Logic reviewer | EP propagation table, causal test results, DAG | Bird's-eye framing + EP methodology |
| Methods reviewer | Statistical model, UQ section, method selection | Bird's-eye framing + methods methodology |
| Plot-validator | Figures directory path, plotting scripts | Plotting appendix excerpt |

Assemble each reviewer's slice from `phase_context_N.md` and the artifact
before spawning. This reduces reviewer input context by 40-60%, speeds up
spawning, and improves focus. The arbiter receives the full artifact + all
reviewer outputs (not a slice) — it needs the complete picture to synthesize.

**Data callbacks.** If Phase 2 or 3 agents report that a high-EP edge
(EP > 0.30) cannot be tested due to missing data, the orchestrator MAY
invoke a data callback:

1. Spawn `data-acquisition-agent` with the specific variable request
2. The agent runs Steps 0.3-0.4 for the requested variable only
3. Spawn `data-quality-agent` for the new data (Step 0.5)
4. **Quality gate decision (mandatory before proceeding):**
   Read the DATA_QUALITY verdict for the new data:
   - **HIGH quality:** proceed normally — append to registry.yaml and resume.
   - **MEDIUM quality:** proceed with caveat — append to registry.yaml,
     resume, and add a data quality warning to the requesting phase's
     artifact for the affected edge. The edge's Classification must note
     "medium-quality callback data" in its caveats. Append the DATA_QUALITY
     verdict summary to `experiment_log.md`.
   - **LOW quality on a high-EP edge (EP > 0.30):** DO NOT resume
     automatically. Present to the human: show the quality verdict, the
     affected edge, and its EP value. Await human approval to either proceed
     or downgrade the edge to lightweight assessment (treat EP as 0.15–0.30
     range). Log the decision AND the DATA_QUALITY verdict summary in
     `experiment_log.md`.
   - **LOW quality on a low-EP edge (EP ≤ 0.30):** downgrade the edge to
     lightweight assessment automatically. Append the DATA_QUALITY verdict
     summary to `experiment_log.md`. Log as a limitation. Resume.
5. Append results to `phase0_discovery/data/registry.yaml`
6. Resume the requesting phase with the new data available (subject to step 4)

**Guards:** Maximum 2 callbacks per analysis. Each callback gets logged
in `experiment_log.md` with justification. If 2 callbacks have already
been used, log the data gap as a limitation instead.

**EP monitoring at sub-chain expansion.** During Phase 3, when an event or
edge triggers sub-chain expansion, the orchestrator checks Joint_EP. If an
event's individual EP > 0.3 and the chain's Joint_EP > 0.15, scaffold a
sub-analysis directory using the scaffolder. If Joint_EP <= 0.15, log it as
"below soft truncation — lightweight assessment only" and do not expand.

**Agent profiles:** Detailed role definitions with domain knowledge, mandatory
checklists, and output formats live in `.claude/agents/*.md`. When spawning an
executor or reviewer, instruct it to read its agent profile first. The profile
contains the deep domain expertise (causal inference methodology, EP
assessment criteria, data quality standards, etc.) that makes the agent
effective. The agent roster and phase-to-agent mapping is in the table above.

**Anti-patterns:**
- Running straight from Phase 1 to Phase 6 with no intermediate artifacts
- The orchestrator writing analysis scripts itself
- Using an LLM for format conversion — use pandoc, not an agent
- Writing a workaround when a maintained tool exists — `pixi add` it instead
- Accepting reviewer PASS too easily — the arbiter should ITERATE liberally
- Spawning subagents without `model: "opus"` — this silently degrades quality
- Subagents reading files with `cat | sed | head` instead of the Read tool
- Skipping plot-validator in review cycles — it catches errors LLMs miss
- Spawning an executor without pointing it to its `.claude/agents/` profile
- Presenting correlation as causation without refutation tests in Phase 3
- Skipping EP assessment for causal edges — every edge must have EP values
- Ignoring data quality gate warnings from Phase 0 in downstream artifacts
- Expanding sub-chains beyond recursion depth 2 without orchestrator approval
- Treating REPORT.md as a symlink or copy of ANALYSIS_NOTE.md — they are distinct documents
- Skipping the audit trail (Step 6.3) — `audit_trail/` with claims.yaml, methodology.yaml, provenance.yaml, verification.yaml is mandatory
- Skipping `generate_audit.py` in `phase6_documentation/scripts/` — the audit trail must be reproducible

**What the orchestrator does NOT do:**
- Read full scripts or data files (subagents do this)
- Debug code (subagents do this)
- Produce figures (subagents do this)
- Write analysis prose (subagents do this)

**What the orchestrator MUST do:**
- **Health monitoring.** Commit before spawning each subagent. Check progress
  every ~5 minutes for long-running subagents. Respawn stalled agents from
  the last commit (if no commit in >10 minutes and no progress, terminate
  and respawn). When background/non-blocking agent spawning is available,
  use it for long-running subagents (Phase 3 causal testing, Phase 4
  projection scenarios, Phase 6 report writing) to enable monitoring and
  respawning.
- Ensure review quality. Do NOT conserve tokens by accepting weak reviews
  or rushing past issues. If a reviewer finds problems, have the work redone
  properly — not minimally patched.
- Trigger phase regression when ANY review finds logic or methodology issues
  traceable to an earlier phase.
- **EP propagation tracking.** After Phase 3, maintain a running summary of
  Joint_EP values for all causal chains. Pass this summary to Phase 4 and
  Phase 5 agents so they can prioritize high-EP findings.

**Subagent model selection:** All subagents — executors, reviewers, arbiters,
fix agents — must be spawned with `model: "opus"`. Never use Sonnet or Haiku
for any analysis subagent. This is non-negotiable.

**Subagent file reading:** Instruct all subagents to use the Read tool to
read files in full (no line limits). Never use `cat`, `sed`, `head`, or
`tail` to read files in chunks — the Read tool handles files of any size
and gives the subagent the complete content.

---

## Methodology

Read relevant sections from `methodology/` as needed:

| Topic | File | When |
|-------|------|------|
| Phase definitions | `methodology/03-phases.md` | Before each phase |
| Orchestration | `methodology/04-orchestration.md` | Orchestrator planning |
| Artifacts | `methodology/05-artifacts.md` | Writing phase artifacts |
| Analysis note spec | `methodology/analysis-note.md` | Phase 6 (writing report), Phase 5 |
| Review protocol | `methodology/06-review.md` | Spawning reviewers |
| Tools & paradigms | `methodology/07-tools.md` | Coding phases |
| Coding practices | `methodology/08-coding.md` | Coding phases |
| Downscoping | `methodology/09-downscoping.md` | Hitting limitations |
| Plotting | `methodology/appendix-plotting.md` | All figure-producing phases |
| Checklist | `methodology/appendix-checklist.md` | Review, Phase 5 |

---

## Environment

This analysis has its own pixi environment defined in `pixi.toml`.
All scripts must run through pixi:

```bash
pixi run py path/to/script.py          # run a script
pixi run py -c "import pandas; ..."    # quick check
pixi shell                              # interactive shell with all deps
```

**Never use bare `python`, `pip install`, or `conda`.** If you need a
package, add it to `pixi.toml` and run `pixi install`. Never use system
calls to install packages.

---

## Tool Requirements

Non-negotiable. Use these — not alternatives.

| Task | Use | NOT |
|------|-----|-----|
| Tabular data | `pandas` | manual CSV parsing, raw dicts |
| Causal inference | `dowhy` | ad-hoc regression-only approaches |
| World Bank data | `wbgapi` | manual URL construction to World Bank API |
| FRED data | `fredapi` | manual URL construction to FRED API |
| Array operations | `numpy`, `scipy` | manual loops for numerical work |
| Statistical modeling | `statsmodels`, `scikit-learn` | custom likelihood code (unless justified) |
| Plotting | `matplotlib` | plotly (for static reports) |
| Logging | `logging` + `rich` | `print()` — never use bare print |
| Document prep | `pandoc` (>=3.0) + pdflatex | LLM-based markdown-to-LaTeX conversion |
| Dependency mgmt | `pixi` | pip, conda |
| Data serialization | `pyarrow` / parquet | CSV for intermediate artifacts |

**Optional:** `networkx` for DAG manipulation and visualization when graph
operations go beyond simple rendering. `seaborn` for statistical
visualization when distribution plots or pair plots are needed.

---

## Phase Gates

Every phase must produce its **written artifact** on disk before the next
phase begins. No exceptions.

| Phase | Required artifact | Review type |
|-------|-------------------|-------------|
| 0 | `phase0_discovery/exec/DISCOVERY.md` + `phase0_discovery/exec/DATA_QUALITY.md` + `data/registry.yaml` | 2-bot (logic + arbiter) |
| 1 | `phase1_strategy/exec/STRATEGY.md` | 2-bot (logic + arbiter) |
| 2 | `phase2_exploration/exec/EXPLORATION.md` | Self |
| 3 | `phase3_analysis/exec/ANALYSIS.md` | 4-bot |
| 4 | `phase4_projection/exec/PROJECTION.md` | 4-bot |
| 5 | `phase5_verification/exec/VERIFICATION.md` | 4-bot + Human Gate |
| 6 | `phase6_documentation/exec/ANALYSIS_NOTE.md` + `phase6_documentation/exec/REPORT.md` + `phase6_documentation/audit_trail/` + `REPORT.pdf` | 3-bot two-stage (domain + plot-validator → compile → rendering + arbiter) |

**Review before advancing.** After each artifact, spawn a reviewer subagent.
Self-review is only acceptable for Phase 2 (exploration). All other phases
require independent reviewer agents. Write findings to
`phase*/review/REVIEW_NOTES.md`.

**Experiment log.** Append to `experiment_log.md` throughout. An empty
experiment log at the end of a phase is a process failure.

**`all` task.** `pixi.toml` must have an `all` task that runs the full
analysis chain. Update it whenever scripts are added.

---

## Review Protocol

See `methodology/06-review.md` for the full protocol. Key rules:

**Classification:** **(A) Must resolve** — blocks advancement. **(B) Must fix before PASS** — weakens the analysis. **(C) Suggestion** — applied before commit, no re-review.

The arbiter must not PASS with unresolved A or B items.

**Reviewer agents:**

| Role | Agent | Purpose |
|------|-------|---------|
| Domain reviewer | `domain-reviewer` | Domain expertise, factual accuracy, literature grounding |
| Logic reviewer | `logic-reviewer` | Causal reasoning validity, DAG consistency, EP arithmetic |
| Methods reviewer | `methods-reviewer` | Statistical methodology, test selection, uncertainty quantification |
| Arbiter | `arbiter` | Synthesizes all reviews, makes PASS/FAIL decision |
| Rendering reviewer | `rendering-reviewer` | Document formatting, figure quality, pandoc compatibility |

**Review tiers by phase:**

| Phase | Review type |
|-------|-------------|
| 0: Discovery | 2-bot (logic → arbiter) |
| 1: Strategy | 2-bot (logic → arbiter) |
| 2: Exploration | Self-review |
| 3: Causal Analysis | 4-bot (domain + logic + methods → arbiter) |
| 4: Projection | 4-bot (domain + logic + methods → arbiter) |
| 5: Verification | 4-bot (domain + logic + methods → arbiter) + Human Gate |
| 6: Documentation | 3-bot two-stage (domain + plot-validator → compile → rendering → arbiter) |

**Plot-validator** runs alongside all other reviewers in parallel. It performs
programmatic (not visual) checks on plotting code and output data. Red flags
from the plot-validator are automatic Category A — the arbiter must not
downgrade them. See `.claude/agents/plot-validator.md` and
`methodology/06-review.md` §6.4.3 for the complete protocol.

**Iteration limits:** 2/3/4-bot: warn at 3, strong warn at 5, hard cap at 10. 1-bot: warn at 2, escalate after 3. All subagents use `model: "opus"`.

**Review iteration tracking:** Record iteration counts in STATE.md directly (Edit tool):
- After each review cycle, increment `phase_{N}_review_iterations` in STATE.md
- Warn at 3 iterations (add a note in the commit message and experiment log)
- Hard cap at 10 iterations — present current state to human for guidance
- (`scripts/state_manager.py` thresholds: warn=3, hard_stop=10; it is a library,
  not callable from the orchestrator directly)

---

## Phase Regression

When a reviewer at Phase N finds a **logic or methodology issue** traceable
to Phase M < N, this triggers regression. See `methodology/06-review.md` §6.8
for the full protocol.

**Regression trigger:** Spawn an Investigator to trace impact →
`REGRESSION_TICKET.md` → fix origin phase → re-run affected downstream →
resume review.

**Not regression (local fix):** Axis labels, captions, current-phase code bugs
→ normal Category A fix-and-re-review cycle.

---

## Coding Rules

- **Tabular analysis.** DataFrames and array operations, not row-by-row loops.
  Selections are boolean masks or query expressions.
- **Prototype on a slice.** Small sample first, full data only for production.
- **No bare `print()`.** Use `logging` + `rich`. Ruff T201 enforces this.
- **Conventional commits.** `<type>(phase): <description>`.
- **Scripts as pixi tasks.** Every script gets a named task in `pixi.toml`.
  The `all` task runs the full chain.
- **KISS / YAGNI.** No CLIs, config systems, or plugin architectures. Write scripts.

Standard logging setup:
```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)
```

See `methodology/08-coding.md` for full coding practices.

---

## Scale-Out Rules

**Always estimate before running at full scale.** Check input size, time a
small slice, extrapolate.

| Estimated time | Action |
|---|---|
| < 2 min | Single-core local — just run it |
| 2–15 min | `ProcessPoolExecutor` or equivalent multicore |
| > 15 min | Consider chunking, caching intermediate results, or parallelizing across datasets |

---

## Plotting Rules

See `methodology/appendix-plotting.md` for full plotting standards. Essentials:

- **Style:** Use a clean, consistent matplotlib style. Set a project-wide
  style at the top of plotting scripts (e.g., `plt.style.use('seaborn-v0_8-whitegrid')` or a custom stylesheet).
- **Figure size:** `figsize=(10, 10)`. Subplots: `figsize=(10*ncols, 10*nrows)`.
- **No titles.** Never `ax.set_title()`. Captions go in the analysis note.
- **No absolute font sizes.** Use relative sizes (`'x-small'`, `'small'`).
- **Save as PDF + PNG.** `bbox_inches="tight"`, `dpi=200`, `transparent=True`. Close after saving.
- **Figures in artifacts:** `![Detailed caption](figures/name.pdf)`.

---

## Conventions

Read applicable files in `conventions/` at three mandatory checkpoints:

1. **Phase 1 (Strategy):** Read all applicable conventions before writing
   the analysis plan. Enumerate every required methodology with "Will implement"
   or "Not applicable because [reason]."
2. **Phase 3 (Causal Analysis):** Re-read conventions before finalizing
   causal tests and statistical models. Produce a completeness table comparing
   methods against conventions AND reference analyses.
3. **Phase 5 (Verification):** Final conventions check — verify everything
   required is present in the verification report.

If a convention requires something you plan to omit, justify explicitly.

**Which conventions apply:**

| Analysis technique | Read these files |
|--------------------|-----------------|
| Causal inference (DAG-based, do-calculus, IV, DiD) | `conventions/causal_inference.md` |
| Time series / forecasting | `conventions/time_series.md` |
| Cross-sectional / panel analysis | `conventions/panel_analysis.md` |

If unsure, the methodology selection in Phase 1 determines which file applies.
Read the "When this applies" section of each candidate file to confirm.
Ignore `conventions/TEMPLATE.md` — it is a skeleton for spec developers
creating new conventions files.

---

## Phase 6 Dual-Document Requirement

Phase 6 produces TWO distinct documents in `phase6_documentation/exec/`:

| Document | Purpose | Style |
|----------|---------|-------|
| **ANALYSIS_NOTE.md** | Logic-focused technical artifact | Quantitative, reasoning chain, EP arithmetic, refutation details |
| **REPORT.md** | Final stakeholder deliverable | Writing Style Guide: "so what" leads, named scenarios, analogies, no LLM-speak |

**ANALYSIS_NOTE.md is written first** (the analytical backbone). **REPORT.md
is then written independently** — rewriting the prose per the Writing Style
Guide while preserving all facts and numbers from the ANALYSIS_NOTE. REPORT.md
is NEVER a symlink or copy of ANALYSIS_NOTE.md.

**The audit trail (`audit_trail/`) is mandatory.** It must contain:
- `claims.yaml` — every factual claim mapped to its data source
- `methodology.yaml` — every analytical choice with justification
- `provenance.yaml` — registry.yaml with verification status
- `verification.yaml` — Phase 5 results summary
- `audit_trail_section.md` — human-readable audit narrative

**`phase6_documentation/scripts/generate_audit.py`** must exist and be capable of regenerating
the audit trail from upstream artifacts.

**`REPORT.pdf`** is compiled from REPORT.md and placed at the analysis root.

**Reuse upstream figures.** Figures generated in Phases 0–5 that help
illustrate findings MUST be included in the Phase 6 report with proper
captions. Do not let upstream figures go to waste — if a figure was worth
generating, it is worth referencing in the final deliverable.

**`REPORT_ZH.pdf`** is a mandatory deliverable. After producing the English
REPORT.pdf, produce `exec/REPORT_ZH.md` by **translating `exec/REPORT.md`
into Chinese** — preserving every section, paragraph, figure, table, and
citation. The Chinese version must match the English in structure, detail,
and length; it is a faithful translation, NOT an independent rewrite or
condensed summary. Figures may remain in English. Compile to `REPORT_ZH.pdf`
at both `exec/` and the analysis root.

---

## Analysis Note Format

The analysis note (`ANALYSIS_NOTE.md`) must be **pandoc-compatible markdown**:

- **LaTeX math:** `$...$` inline, `$$...$$` display. Write `$\alpha$`, not `alpha`.
- **Figures:** `![Caption text](figures/name.pdf)` — pandoc converts to `\includegraphics`.
- **No raw HTML.** Pandoc markdown only.
- **Tables:** Pipe tables (`| col1 | col2 |`).
- **Cross-references:** pandoc-crossref syntax — `{#fig:label}`, `@fig:label`.
  At sentence start: `Figure @fig:name`. Every figure MUST have a label.
  Never use `[-@fig:...]`.
- **Citations:** `[@key]` with a `references.bib` BibTeX file. `build-pdf` uses `--citeproc`.
- **Sections:** `#`, `##`, `###` — pandoc adds numbering with `--number-sections`.
  **Never hand-number headings** (write `# First Principles` not
  `# 1. First Principles`). Hand-numbering causes double numbering in PDF.

Required AN sections — see `methodology/03-phases.md` → Phase 6 for the full list.

---

## Feasibility Evaluation

When the analysis encounters a limitation, do not silently downscope.
See `methodology/09-downscoping.md` for the full evaluation protocol.

---

## Reference Analyses

To be filled during Phase 1. The strategy must identify 2-3 published
reference analyses (peer-reviewed papers, institutional reports, or
established methodological benchmarks) and tabulate their approaches. This
table is a binding input to Phase 3 and Phase 5 reviews.

---

## Pixi Reference

Common patterns and pitfalls for `pixi.toml`:

```toml
# === Structure ===
[workspace]
name = "my-analysis"
channels = ["conda-forge"]
platforms = ["linux-64"]

# Conda packages (compiled, from conda-forge)
[dependencies]
python = ">=3.11"
pandoc = ">=3.0"

# Python packages (from PyPI)
[pypi-dependencies]
pandas = ">=2.0"
numpy = ">=1.24"
dowhy = ">=0.11"

# Named tasks
[tasks]
py = "python"
acquire = "python phase0_discovery/scripts/acquire_data.py"
all = "python phase0_discovery/scripts/acquire_data.py && ..."
```

**Common pitfalls:**
- PyPI packages go in `[pypi-dependencies]`, NOT `[dependencies]`.
- After editing `pixi.toml`, run `pixi install` to update the environment.
- Task values are shell command strings. Chain with `&&` for sequential.
- The `py` task (`py = "python"`) lets you run arbitrary scripts.

---

## Git

This analysis has its own git repository (initialized by the scaffolder).
Commit work within this directory. Do not modify files outside this
directory — the spec repository is separate.
