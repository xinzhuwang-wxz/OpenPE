<!-- Spec developer note: agent prompt templates live in
     src/orchestration/agents.md. Context assembly rules are in
     src/methodology/03a-orchestration.md §3a.4.2. -->

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

**The orchestrator loop for each phase:**

```
for each phase in [1, 2, 3, 4a, 4b, 4c, 5]:

  1. EXECUTE — spawn a phase executor subagent (start in plan mode) with:
     - The physics prompt
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

  3. CHECK — read the review findings (short).
     If regression trigger (physics issue from earlier phase):
       → enter Phase Regression protocol (see below).
     If Category A or B issues: spawn a fix agent to address ALL of them,
       then re-review with a fresh reviewer added to the panel.
     If only Category C or no issues: proceed.

  4. COMMIT — commit the phase's work.

  5. HUMAN GATE (after 4b for both measurements and searches):
     Present the draft AN and 10% results to the human. Pause until approved.

  6. ADVANCE — proceed to next phase.
```

**Phase 4 flow (both measurements and searches):**
All three sub-phases (4a → 4b → 4c) are required for both analysis types.
- **4a:** Statistical analysis — systematics, expected results. No AN draft.
- **4b:** 10% data validation. Compare to expected. Write full AN draft.
  Review + PDF render. Human gate after 4b review passes.
- **4c:** Full data. Compare to **both** 10% and expected. Update AN with full results.

**Context splitting:** Phase 4b and Phase 5 are context-intensive (AN writing
alongside statistical analysis). When context pressure is high, split into
separate subagent invocations: one for statistical analysis, another for AN
writing/rendering. The AN-writing subagent reads the inference artifact from
disk.

**Agent profiles:** Detailed role definitions with domain knowledge, mandatory
checklists, and output formats live in `.claude/agents/*.md`. When spawning an
executor or reviewer, instruct it to read its agent profile first. The profile
contains the deep domain expertise (5-step selection philosophy, 8 mandatory
fit diagnostics, closure test criteria, etc.) that makes the agent effective.
The agent roster and phase-to-agent mapping is in
`methodology/orchestration/agents.md` (or `src/orchestration/agents.md` from
the spec root).

**Anti-patterns:**
- Running straight from Phase 1 to Phase 5 with no intermediate artifacts
- The orchestrator writing analysis scripts itself
- Using an LLM for format conversion — use pandoc, not an agent
- Writing a workaround when a maintained tool exists — `pixi add` it instead
- Accepting reviewer PASS too easily — the arbiter should ITERATE liberally
- Spawning subagents without `model: "opus"` — this silently degrades quality
- Subagents reading files with `cat | sed | head` instead of the Read tool
- Skipping plot-validator in review cycles — it catches errors LLMs miss
- Spawning an executor without pointing it to its `.claude/agents/` profile

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
  use it for long-running subagents (Phase 3 processing, Phase 4 systematic
  evaluation, Phase 5 AN writing) to enable monitoring and respawning.
- Ensure review quality. Do NOT conserve tokens by accepting weak reviews
  or rushing past issues. If a reviewer finds problems, have the work redone
  properly — not minimally patched.
- Trigger phase regression when ANY review finds physics issues traceable
  to an earlier phase.

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
| Orchestration | `methodology/03a-orchestration.md` | Orchestrator planning |
| Blinding | `methodology/04-blinding.md` | Phase 4 |
| Artifacts | `methodology/05-artifacts.md` | Writing phase artifacts |
| Analysis note spec | `methodology/analysis-note.md` | Phase 4b (writing AN), Phase 5 |
| Review protocol | `methodology/06-review.md` | Spawning reviewers |
| Tools & paradigms | `methodology/07-tools.md` | Coding phases |
| Coding practices | `methodology/11-coding.md` | Coding phases |
| Downscoping | `methodology/12-downscoping.md` | Hitting limitations |
| Plotting | `methodology/appendix-plotting.md` | All figure-producing phases |
| Checklist | `methodology/appendix-checklist.md` | Review, Phase 5 |

---

## Environment

This analysis has its own pixi environment defined in `pixi.toml`.
All scripts must run through pixi:

```bash
pixi run py path/to/script.py          # run a script
pixi run py -c "import uproot; ..."     # quick check
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
| ROOT file I/O | `uproot` | PyROOT, ROOT C++ macros |
| Array operations | `awkward-array`, `numpy` | pandas (for HEP event data) |
| Histogramming | `hist`, `boost-histogram` | ROOT TH1, numpy.histogram (for filling) |
| Plotting | `matplotlib` + `mplhep` | ROOT TCanvas, plotly |
| Statistical model | `pyhf` (binned), `zfit` (unbinned) | RooFit, RooStats, custom likelihood code |
| Jet clustering | `fastjet` (Python) | manual clustering |
| Logging | `logging` + `rich` | `print()` — never use bare print |
| Document prep | `pandoc` (>=3.0) + pdflatex | LLM-based markdown→LaTeX conversion |
| Dependency mgmt | `pixi` | pip, conda |

**Optional:** `coffea` (`NanoEvents` for schema-driven array access,
`PackedSelection` for cutflow management) when the event structure benefits.

---

## Phase Gates

Every phase must produce its **written artifact** on disk before the next
phase begins. No exceptions.

| Phase | Required artifact | Review type |
|-------|-------------------|-------------|
| 1 | `phase1_strategy/exec/STRATEGY.md` | 4-bot |
| 2 | `phase2_exploration/exec/EXPLORATION.md` | Self |
| 3 | `phase3_selection/exec/SELECTION.md` | 1-bot |
| 4a | `phase4_inference/exec/INFERENCE_EXPECTED.md` | 4-bot |
| 4b | `phase4_inference/exec/INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md` | 4-bot → human gate |
| 4c | `phase4_inference/exec/INFERENCE_OBSERVED.md` | 1-bot |
| 5 | `phase5_documentation/exec/ANALYSIS_NOTE.md` | 5-bot (4 + rendering) |

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

| Phase | Review type |
|-------|-------------|
| 1: Strategy | 4-bot + plot-validator (physics + critical + constructive + arbiter) |
| 2: Exploration | Self-review |
| 3: Processing | 1-bot + plot-validator (critical + plot-validator) |
| 4a: Expected | 4-bot + plot-validator |
| 4b: 10% validation | 4-bot + plot-validator → human gate |
| 4c: Full data | 1-bot + plot-validator |
| 5: Documentation | 5-bot + plot-validator (4-bot + rendering + plot-validator) |

**Plot-validator** runs alongside all other reviewers in parallel. It performs
programmatic (not visual) checks on plotting code and output data. Red flags
from the plot-validator are automatic Category A — the arbiter must not
downgrade them. See `.claude/agents/plot-validator.md` and
`methodology/06-review.md` §6.4.3 for the complete protocol.

**Iteration limits:** 4/5-bot: warn at 3, strong warn at 5, hard cap at 10. 1-bot: warn at 2, escalate after 3. All subagents use `model: "opus"`.

---

## Phase Regression

When a reviewer at Phase N finds a **physics issue** traceable to Phase M < N,
this triggers regression. See `methodology/06-review.md` §6.8 for the full protocol.

**Regression trigger:** Spawn an Investigator to trace impact →
`REGRESSION_TICKET.md` → fix origin phase → re-run affected downstream →
resume review.

**Not regression (local fix):** Axis labels, captions, current-phase code bugs
→ normal Category A fix-and-re-review cycle.

---

## Coding Rules

- **Columnar analysis.** Arrays, not event loops. Selections are boolean masks.
- **Prototype on a slice.** ~1000 events first, full data only for production.
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

See `methodology/11-coding.md` for full coding practices.

---

## Scale-Out Rules

**Always estimate before running at full scale.** Check input size, time a
1000-event slice, extrapolate.

| Estimated time | Action |
|---|---|
| < 2 min | Single-core local — just run it |
| 2–15 min | `ProcessPoolExecutor` or equivalent multicore |
| > 15 min | SLURM: `sbatch --wait` (single) or `--array` (per-file) |

---

## Plotting Rules

See `methodology/appendix-plotting.md` for full plotting standards. Essentials:

- **Style:** `import mplhep as mh; mh.style.use("CMS")` (CMS style is the default mplhep preset — clean, widely used)
- **Figure size:** `figsize=(10, 10)`. Subplots: `figsize=(10*ncols, 10*nrows)`.
- **No titles.** Never `ax.set_title()`. Captions go in the analysis note.
- **No absolute font sizes.** The CMS stylesheet sets sizes. Use `'x-small'` for legends.
- **Save as PDF + PNG.** `bbox_inches="tight"`, `dpi=200`, `transparent=True`. Close after saving.
- **Figures in artifacts:** `![Detailed caption](figures/name.pdf)`.

---

## Conventions

Read applicable files in `conventions/` at three mandatory checkpoints:

1. **Phase 1 (Strategy):** Read all applicable conventions before writing
   the systematic plan. Enumerate every required source with "Will implement"
   or "Not applicable because [reason]."
2. **Phase 4a (Inference):** Re-read conventions before finalizing
   systematics. Produce a completeness table comparing sources against
   conventions AND reference analyses.
3. **Phase 5 (Documentation):** Final conventions check — verify everything
   required is present in the analysis note.

If a convention requires something you plan to omit, justify explicitly.

**Which conventions apply:**

| Analysis technique | Read these files |
|--------------------|-----------------|
| Unfolded measurement (IBU, SVD, TUnfold, OmniFold, bin-by-bin) | `conventions/unfolding.md` |
| Extraction measurement (double-tag, ratio, branching fraction, counting) | `conventions/extraction.md` |
| Search / limit-setting | `conventions/search.md` |

If unsure, the technique selection in Phase 1 determines which file applies.
Read the "When this applies" section of each candidate file to confirm.
Ignore `conventions/TEMPLATE.md` — it is a skeleton for spec developers
creating new conventions files.

---

## Analysis Note Format

The analysis note (`ANALYSIS_NOTE.md`) must be **pandoc-compatible markdown**:

- **LaTeX math:** `$...$` inline, `$$...$$` display. Write `$\alpha_s$`, not `alpha_s`.
- **Figures:** `![Caption text](figures/name.pdf)` — pandoc converts to `\includegraphics`.
- **No raw HTML.** Pandoc markdown only.
- **Tables:** Pipe tables (`| col1 | col2 |`).
- **Cross-references:** pandoc-crossref syntax — `{#fig:label}`, `@fig:label`.
  At sentence start: `Figure @fig:name`. Every figure MUST have a label.
  Never use `[-@fig:...]`.
- **Citations:** `[@key]` with a `references.bib` BibTeX file. `build-pdf` uses `--citeproc`.
- **Sections:** `#`, `##`, `###` — pandoc adds numbering with `--number-sections`.

Required AN sections — see `methodology/03-phases.md` → Phase 5 for the full list.

---

## Feasibility Evaluation

When the analysis encounters a limitation, do not silently downscope.
See `methodology/12-downscoping.md` for the full evaluation protocol.

---

## Reference Analyses

To be filled during Phase 1. The strategy must identify 2-3 published
reference analyses and tabulate their systematic programs. This table is
a binding input to Phase 4 and Phase 5 reviews.

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
uproot = ">=5.0"
numpy = ">=1.24"

# Named tasks
[tasks]
py = "python"
select = "python phase3_selection/scripts/apply_selection.py"
all = "python phase3_selection/scripts/apply_selection.py && ..."
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
