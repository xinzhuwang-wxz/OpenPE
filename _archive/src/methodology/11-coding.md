## 11. Version Control and Coding Practices

Analysis code is exploratory by nature, but it must be correct and
reproducible. The engineering bar is **"would this pass review from a physicist
colleague"** — not enterprise software standards.

### 11.1 Git Discipline

All analysis work is tracked in git. This serves as the checkpointing mechanism
within and across phases.

**Conventional commits.** Every commit uses a structured message format:

```
<type>(phase): <description>

Types:
  feat     — new analysis capability (selection, training, fit)
  fix      — bug fix in analysis code
  data     — data exploration, sample inventory
  plot     — figure generation or update
  doc      — artifact writing, note updates
  refactor — restructuring without changing results
  test     — adding or updating tests
  chore    — housekeeping (formatting, dependencies)
```

**Commit frequency:** After every meaningful step — completing a cut study,
producing a set of plots, finishing a closure test, updating the artifact.
Commits within a phase are the checkpoints; if the agent crashes at step 12 of
15, it can resume from the last commit.

**Session boundaries.** When a session is getting long (many iterations,
extensive debugging), commit all work, append findings to the experiment log,
and produce an intermediate artifact with an "Open issues" section listing
what remains. The next session reads the experiment log and intermediate
artifact to continue. Do not attempt to do everything in a single session —
clean handoffs between sessions are better than context-exhausted work.

**Branch strategy:** Each phase works on a branch (`phase1_strategy`,
`phase2_exploration`, etc.). The branch is merged to main when the phase's
review passes. This keeps main clean — it always reflects reviewed work.

### 11.2 Code Quality

**Formatting and linting:** Use `ruff` (or equivalent) with a pre-commit hook.
Every commit is automatically formatted and checked for common errors (undefined
variables, unused imports, shadowed names). This is cheap and catches real bugs.

**Code style:**
- **KISS.** Obvious numpy/awkward operations over clever metaprogramming. A
  physicist reading the code should be able to follow the analysis flow.
- **DRY.** If multiple channels share the same calibration logic, factor it out.
  But do not prematurely abstract for hypothetical future needs.
- **YAGNI.** Do not build CLIs, config systems, or plugin architectures. Write
  scripts. Refactor when (not before) reuse is actually needed.

**Logging, not printing.** All analysis scripts must use Python's `logging`
module with `rich.logging.RichHandler` — never bare `print()` statements.
Standard setup:

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

Ruff's `T201` rule (enabled in `pyproject.toml`) flags `print()` calls as
lint errors. This is enforced at commit time via the pre-commit hook.

**What NOT to do:**
- Do not write unit tests for every function
- Do not create mock data fixtures when real data is available
- Do not add type annotations to exploratory scripts
- Do not write docstrings for functions that run once
- Do not build frameworks when scripts work
- Do not use dependency injection, abstract base classes, or enterprise patterns

### 11.3 Testing

Testing effort should focus on **structural bugs** — errors in the plumbing
that silently propagate through everything downstream. A bug in the final fit
is cheap to fix (re-run the fit). But cutting on the wrong lepton pT branch,
reconstructing a nonsensical 4-lepton mass, or applying a weight meant for
signal to background — these are catastrophic because they require re-running
the entire analysis and are hard to track down (the numbers look plausible
but are wrong).

**Always:** One **smoke test** per phase — does the full pipeline run on ~100
events without crashing? This catches import errors, broken paths, shape
mismatches, and API changes. Fast to run, high value.

**Always:** One **integration test** for the processing chain — does it produce
output files with the expected structure? Not checking physics values — checking
that the machinery works (correct number of bins, files exist, no NaN yields).

**Focus on structural correctness:**
- Test that variable names map to the right physical quantities (is this
  actually lepton pT, not jet pT?)
- Test that cut inversions actually invert (CR selection is complement of SR)
- Test that object definitions produce yields consistent with published
  efficiencies (if the experiment says 99% tracking efficiency and you get 60%,
  something is structurally wrong)
- Test that systematic variations go in the expected direction
- Test that event counts are monotonically decreasing through the cutflow
  (if a cut increases yield, something is wrong)

These structural tests are cheap to write and catch the bugs that are most
expensive to debug later.

**Never:** Full test suites, 100% coverage targets, TDD. The analysis result
is the product, not the code. The physics validation (closure tests, signal
injection, post-fit diagnostics) IS the test suite for correctness.

### 11.4 Reproducibility via Task Graph

The analysis must be reproducible by a human who has never seen the code.
The standard is: clone the repo, `cd` into the analysis directory,
`pixi install`, `pixi run all` — and the full analysis executes from raw
data to final results.

**Every script gets a pixi task.** When you write a script, register it as a
named task in the analysis's `pixi.toml`. When one script depends on the
output of another, express that with `depends-on`. The task graph *is* the
analysis workflow.

```toml
[tasks]
py = "python"
# Each task is independently runnable
select = "python phase3_selection/scripts/apply_selection.py"
response = "python phase4_inference/scripts/build_response.py"
unfold = "python phase4_inference/scripts/unfold.py"
systematics = "python phase4_inference/scripts/run_systematics.py"
summary = "python phase4_inference/scripts/build_summary.py"
plots = "python phase5_documentation/scripts/make_plots.py"
# Full chain — the reproducibility contract
all = "python phase3_selection/scripts/apply_selection.py && python phase4_inference/scripts/build_response.py && python phase4_inference/scripts/unfold.py && python phase4_inference/scripts/run_systematics.py && python phase4_inference/scripts/build_summary.py && python phase5_documentation/scripts/make_plots.py"
```

**Every task runs independently.** An agent fixing the unfolding script runs
`pixi run unfold` without triggering the full chain. The execution order is
documented by the `all` task and by a comment block in `pixi.toml`, but
individual tasks do not enforce upstream dependencies — they read whatever
intermediate files are on disk.

**`pixi run all` is the reproducibility contract.** It runs the full chain
in order. The Phase 5 review checks that `pixi run all` works from a clean
state (no pre-existing intermediate files). If it runs clean, the analysis
reproduces.

**Why this matters:**
- A reviewer inspects the task list to understand the analysis flow without
  reading Python.
- The execution order is explicit — no hidden assumptions buried in a README.
- Adding a new systematic branch means adding a task, not editing a shell
  script.
- Agents iterate on individual steps without paying the cost of the full
  chain.

**Script decomposition.** If a script's estimated runtime (extrapolated from
a Phase 2 timing slice) exceeds ~5 minutes, split it into stages with
intermediate outputs saved to disk. Each stage gets its own pixi task.
Example: separate `build_response` (construct the response matrix) from
`unfold` (run IBU) from `bootstrap` (500 replicas for stat uncertainties).
This makes debugging faster, enables partial re-runs, and keeps individual
tasks within the scale-out thresholds.

**Rules:**
- Update `pixi.toml` tasks whenever you add, rename, or remove a script.
- Task names should be human-readable (`unfold`, not `step4b`).
- Scripts should be idempotent — running them twice produces the same output.
  Use deterministic seeds and write outputs to fixed paths.
- Scripts read inputs from agreed paths and write outputs to agreed paths.
  The interface between scripts is the filesystem, not function calls.

This replaces the need for Makefiles, shell scripts, or workflow managers.
pixi tasks are declared in the same file as the dependencies, so the
environment and workflow are a single artifact.

### 11.5 Code Reuse Across Analyses

Analysis code written for one analysis is a valuable resource for subsequent
analyses — not as a framework to import, but as working examples to consult.

**Within an analysis:** Reusable patterns emerge naturally (data loading,
standard plots, workspace building). When a pattern is used 3+ times, factor
it into a shared utility in the analysis's `scripts/common/` directory. Do not
anticipate reuse — wait until it happens.

**Across analyses:** A **snippets library** (`snippets/`) provides tested,
documented code patterns for common HEP operations. These are not a framework
— they are copy-and-adapt starting points. The agent consults the snippets
library when beginning a task and adapts relevant patterns to the current
analysis. Prior analysis directories are also a resource: "consult
`../prior_analysis/` for patterns that worked in a similar context."

The snippets library grows organically. After completing an analysis, useful
patterns are extracted and added. This is YAGNI in practice — code is
generalized only after it has proven useful in a real analysis, not before.

### 11.6 Debug and Scratch Code

Debug scripts and throwaway experiments are a normal part of analysis
development, but they must not contaminate the production pipeline:

- **Prefix debug scripts with `debug_`** (e.g., `debug_check_weights.py`,
  `debug_plot_comparison.py`). This makes them visually distinct and
  greppable.
- **Or place them in a `scratch/` directory** within the phase directory.
  The `scratch/` directory is for experiments that may or may not be kept.
- **Never include debug scripts in the `all` task.** The `all` task is the
  reproducibility contract — it must run only production scripts. Debug
  scripts may have their own pixi tasks (e.g., `debug-weights`) but these
  must not appear in the `all` chain.
- **Clean up before review.** Before submitting for review, either delete
  debug scripts that are no longer needed or move them to `scratch/` with
  a note in the experiment log about what they tested.

### 11.7 Pre-commit Configuration

A minimal `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix, --extend-select, T201]
      - id: ruff-format
```

This is installed once and runs automatically on every commit. The `T201`
rule flags any bare `print()` calls as lint errors (see Section 11.2). No
agent attention required after setup.

---
