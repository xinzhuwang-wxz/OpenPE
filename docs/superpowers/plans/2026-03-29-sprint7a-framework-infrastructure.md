# Sprint 7A: Framework Infrastructure Fixes

> **Execution order:** Plans 7A → 7B → 7C → 7D (sequential, not parallel) due to shared file modifications in pixi.toml and root_claude.md.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 6 framework-level bugs that break orchestrator state tracking, pixi task management, experiment logging, pixi availability checking, and method-environment consistency.

**Architecture:** Surgical fixes to scaffolder, templates, and orchestrator protocol. Each task is independent — no ordering dependencies between tasks. All changes are to `src/` (templates + scaffolder) and `tests/`.

**Tech Stack:** Python 3.11+, PyYAML, pixi, pytest

**Issues addressed:** I3 (isolation hook), I4 (pixi check), I5/I19 (STATE.md updates), I6 (experiment log format), I9 (method availability), I13/I20/O5 (pixi `all` task), O7/O10 (review iteration + STATE auto-update)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `.claude/hooks/isolate.sh` | Modify | Whitelist `.claude/` directory for memory access |
| `src/scaffold_analysis.py` | Modify | Add pixi check, STATE.md helper, experiment log template |
| `src/templates/pixi.toml` | Modify | Add default `all` task placeholder |
| `src/templates/root_claude.md` | Modify | Add STATE.md update step + review iteration tracking to orchestrator protocol |
| `src/templates/scripts/state_manager.py` | Create | Helper module for STATE.md read/write/update |
| `src/templates/scripts/experiment_logger.py` | Create | Structured experiment log entry writer |
| `tests/test_state_manager.py` | Create | Tests for state manager |
| `tests/test_experiment_logger.py` | Create | Tests for experiment logger |
| `tests/test_scaffold.py` | Modify | Add pixi check test |

---

### Task 0: Fix Isolation Hook to Allow .claude/ Memory Access

**Files:**
- Modify: `.claude/hooks/isolate.sh`

Fixes: I3

The isolation hook blocks access to `.claude/projects/*/memory/` when running inside an analysis directory. The fix is to add the `.claude/` directory as an always-allowed path in the ALLOWED array, similar to how `/tmp` is always allowed.

- [ ] **Step 1: Modify isolate.sh**

In `.claude/hooks/isolate.sh`, change the ALLOWED array initialization from:

```bash
ALLOWED=("$ANALYSIS_DIR" "/tmp")
```

to:

```bash
ALLOWED=("$ANALYSIS_DIR" "/tmp" "$HOME/.claude")
```

This allows agents running inside analysis directories to read/write Claude memory files (e.g., `.claude/projects/*/memory/`) without being blocked by the isolation hook.

- [ ] **Step 2: Verify the fix**

Run from an analysis directory:
```bash
cd analyses/some_analysis  # or any dir with .analysis_config
echo '{"tool_name":"Read","cwd":"'$(pwd)'","tool_input":{"file_path":"'$HOME'/.claude/projects/test/memory/test.md"}}' | bash ../../.claude/hooks/isolate.sh
```
Expected: exit 0 (allowed), no JSON deny output.

- [ ] **Step 3: Commit**

```bash
git add .claude/hooks/isolate.sh
git commit -m "fix(sprint7a): whitelist .claude/ in isolation hook for memory access

Fixes I3 — agents in analysis directories can now read/write
.claude/projects/*/memory/ files without being blocked."
```

---

### Task 1: STATE.md Manager Module

**Files:**
- Create: `src/templates/scripts/state_manager.py`
- Create: `tests/test_state_manager.py`

Fixes: I5, I19, O7, O10

- [ ] **Step 1: Write failing tests**

```python
# tests/test_state_manager.py
"""Tests for state_manager.py — STATE.md read/write/update."""
import shutil
from pathlib import Path

from state_manager import StateManager

TMP = Path("/tmp/test_state_manager")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_create_initial_state():
    sm = StateManager(TMP / "STATE.md", analysis_name="test_analysis")
    sm.save()
    assert (TMP / "STATE.md").exists()
    content = (TMP / "STATE.md").read_text()
    assert "Current phase**: 0" in content
    assert "initialized" in content


def test_advance_phase():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.advance_phase(0, artifact="DISCOVERY.md", review="4-bot PASS", notes="2 DAGs")
    content = (TMP / "STATE.md").read_text()
    assert "Current phase**: 1" in content
    assert "DISCOVERY.md" in content


def test_record_review_iteration():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.record_review_iteration(phase=0, issues_a=1, issues_b=2)
    sm.record_review_iteration(phase=0, issues_a=0, issues_b=0)
    assert sm.get_iteration_count(0) == 2


def test_iteration_warning_thresholds():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    for i in range(3):
        sm.record_review_iteration(phase=0, issues_a=1, issues_b=0)
    assert sm.should_warn(0) is True
    assert sm.should_hard_stop(0) is False


def test_iteration_hard_stop():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    for i in range(10):
        sm.record_review_iteration(phase=0, issues_a=1, issues_b=0)
    assert sm.should_hard_stop(0) is True


def test_add_blocker():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.add_blocker("Missing GDP data for 2024")
    content = (TMP / "STATE.md").read_text()
    assert "Missing GDP data" in content


def test_load_existing_state():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.advance_phase(0, artifact="DISCOVERY.md")

    sm2 = StateManager(TMP / "STATE.md")
    sm2.load()
    assert sm2.current_phase == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_state_manager.py -v`
Expected: FAIL — `state_manager` module not found

> **Note on test imports:** The run command uses `PYTHONPATH=src/templates/scripts:.` which makes `src/templates/scripts/` a top-level package directory. Therefore test files import directly: `from state_manager import StateManager` (not `from src.templates.scripts.state_manager`).

- [ ] **Step 3: Implement state_manager.py**

```python
# src/templates/scripts/state_manager.py
"""STATE.md manager for OpenPE analysis pipeline.

Reads, writes, and updates the analysis state file that tracks
pipeline progress, review iterations, and blockers.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


# Review iteration thresholds (from orchestrator protocol)
WARN_THRESHOLD = 3
STRONG_WARN_THRESHOLD = 5
HARD_STOP_THRESHOLD = 10


class StateManager:
    """Manages STATE.md for an analysis pipeline."""

    def __init__(self, path: Path, analysis_name: str = "") -> None:
        self.path = Path(path)
        self.analysis_name = analysis_name
        self.current_phase = 0
        self.status = "initialized"
        self.phase_history: list[dict] = []
        self.blockers: list[str] = []
        self.iteration_counts: dict[int, int] = {}

    def save(self) -> None:
        """Write STATE.md to disk."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "# Analysis State\n",
            f"- **Analysis**: {self.analysis_name}",
            f"- **Current phase**: {self.current_phase}",
            f"- **Status**: {self.status}",
            f"- **Last updated**: {now}\n",
            "## Phase History\n",
            "| Phase | Status | Artifact | Review | Iterations | Notes |",
            "|-------|--------|----------|--------|------------|-------|",
        ]
        for ph in self.phase_history:
            iters = self.iteration_counts.get(ph["phase"], 0)
            lines.append(
                f"| {ph['phase']} | {ph.get('status', 'complete')} "
                f"| {ph.get('artifact', '')} | {ph.get('review', '')} "
                f"| {iters} | {ph.get('notes', '')} |"
            )
        lines.append("")
        lines.append("## Blockers")
        if self.blockers:
            for b in self.blockers:
                lines.append(f"- {b}")
        else:
            lines.append("- (none)")
        lines.append("")
        lines.append("## Regression Log")
        lines.append("- (none)")
        lines.append("")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("\n".join(lines))

    def load(self) -> None:
        """Parse existing STATE.md from disk."""
        if not self.path.exists():
            return
        text = self.path.read_text()

        # Parse current phase
        m = re.search(r"\*\*Current phase\*\*:\s*(\d+)", text)
        if m:
            self.current_phase = int(m.group(1))

        # Parse status
        m = re.search(r"\*\*Status\*\*:\s*(.+)", text)
        if m:
            self.status = m.group(1).strip()

        # Parse analysis name
        m = re.search(r"\*\*Analysis\*\*:\s*(.+)", text)
        if m:
            self.analysis_name = m.group(1).strip()

    def advance_phase(
        self,
        completed_phase: int,
        artifact: str = "",
        review: str = "",
        notes: str = "",
    ) -> None:
        """Record completion of a phase and advance to next."""
        self.phase_history.append({
            "phase": completed_phase,
            "status": "complete",
            "artifact": artifact,
            "review": review,
            "notes": notes,
        })
        self.current_phase = completed_phase + 1
        self.status = f"phase {self.current_phase} pending"
        self.save()

    def record_review_iteration(
        self,
        phase: int,
        issues_a: int = 0,
        issues_b: int = 0,
    ) -> None:
        """Increment review iteration counter for a phase."""
        self.iteration_counts[phase] = self.iteration_counts.get(phase, 0) + 1
        self.save()

    def get_iteration_count(self, phase: int) -> int:
        return self.iteration_counts.get(phase, 0)

    def should_warn(self, phase: int) -> bool:
        return self.get_iteration_count(phase) >= WARN_THRESHOLD

    def should_hard_stop(self, phase: int) -> bool:
        return self.get_iteration_count(phase) >= HARD_STOP_THRESHOLD

    def add_blocker(self, description: str) -> None:
        self.blockers.append(description)
        self.save()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_state_manager.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/state_manager.py tests/test_state_manager.py
git commit -m "feat(sprint7a): add STATE.md manager with iteration tracking

Fixes I5, I19, O7, O10 — STATE.md now tracks phase progress,
review iterations, and blockers with warn/hard-stop thresholds."
```

---

### Task 2: Structured Experiment Logger

**Files:**
- Create: `src/templates/scripts/experiment_logger.py`
- Create: `tests/test_experiment_logger.py`

Fixes: I6

- [ ] **Step 1: Write failing tests**

```python
# tests/test_experiment_logger.py
"""Tests for experiment_logger.py — structured experiment log entries."""
import shutil
from pathlib import Path

from experiment_logger import ExperimentLogger

TMP = Path("/tmp/test_experiment_logger")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_append_entry():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(
        phase=0,
        agent="hypothesis_agent",
        decision="Generated 2 competing DAGs",
        rationale="Rogers diffusion theory vs trust-gated adoption",
    )
    content = log_path.read_text()
    assert "## [Phase 0]" in content
    assert "hypothesis_agent" in content
    assert "2 competing DAGs" in content


def test_multiple_entries_chronological():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(phase=0, agent="hypothesis_agent", decision="D1")
    logger.log(phase=1, agent="lead_analyst", decision="D2")
    content = log_path.read_text()
    assert content.index("Phase 0") < content.index("Phase 1")


def test_log_with_data_fields():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(
        phase=3,
        agent="analyst",
        decision="Used DoWhy for digital divide",
        rationale="Panel data supports causal identification",
        data={"method": "panel_FE", "n_observations": 710},
    )
    content = log_path.read_text()
    assert "panel_FE" in content
    assert "710" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_experiment_logger.py -v`
Expected: FAIL

- [ ] **Step 3: Implement experiment_logger.py**

```python
# src/templates/scripts/experiment_logger.py
"""Structured experiment log writer for OpenPE.

Appends timestamped, phase-tagged entries to experiment_log.md
with consistent format for programmatic parsing.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ExperimentLogger:
    """Appends structured entries to experiment_log.md."""

    def __init__(self, log_path: Path) -> None:
        self.path = Path(log_path)

    def log(
        self,
        phase: int,
        agent: str,
        decision: str,
        rationale: str = "",
        data: dict | None = None,
    ) -> None:
        """Append a structured entry to the experiment log."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"\n## [Phase {phase}] {agent} — {now}\n",
            f"**Decision:** {decision}\n",
        ]
        if rationale:
            lines.append(f"**Rationale:** {rationale}\n")
        if data:
            lines.append("**Data:**\n")
            for k, v in data.items():
                lines.append(f"- `{k}`: {v}")
            lines.append("")

        with open(self.path, "a") as f:
            f.write("\n".join(lines) + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_experiment_logger.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/experiment_logger.py tests/test_experiment_logger.py
git commit -m "feat(sprint7a): add structured experiment logger

Fixes I6 — experiment log entries now have consistent format:
[Phase N] agent — timestamp, Decision, Rationale, Data fields."
```

---

### Task 3: Pixi Availability Check in Scaffolder

**Files:**
- Modify: `src/scaffold_analysis.py` (add check at top of `scaffold()`)
- Modify: `tests/test_scaffold.py` (add test)

Fixes: I4

- [ ] **Step 1: Write failing test**

Add to `tests/test_scaffold.py`:

```python
def test_scaffold_warns_if_pixi_missing(monkeypatch):
    """Scaffolder should warn (not crash) if pixi is not on PATH."""
    import src.scaffold_analysis as sa
    # Patch shutil.which to return None for pixi
    monkeypatch.setattr("shutil.which", lambda cmd: None if cmd == "pixi" else "/usr/bin/" + cmd)
    # scaffold should still work (pixi is needed later, not during scaffold)
    sa.scaffold(TEST_DIR, "analysis")
    assert (TEST_DIR / "pixi.toml").exists()
    # But a warning file should exist
    assert (TEST_DIR / "SETUP_NOTES.md").exists()
    content = (TEST_DIR / "SETUP_NOTES.md").read_text()
    assert "pixi" in content.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_scaffold.py::test_scaffold_warns_if_pixi_missing -v`
Expected: FAIL

- [ ] **Step 3: Add pixi check to scaffold_analysis.py**

At the top of the `scaffold()` function (after `analysis_dir.mkdir`), add:

```python
    # Check pixi availability and warn if missing
    if shutil.which("pixi") is None:
        setup_notes = analysis_dir / "SETUP_NOTES.md"
        setup_notes.write_text(
            "# Setup Notes\n\n"
            "**Warning:** `pixi` was not found on your PATH.\n\n"
            "Install pixi before running this analysis:\n"
            "```bash\n"
            "curl -fsSL https://pixi.sh/install.sh | bash\n"
            "```\n\n"
            "Then: `cd " + str(analysis_dir) + " && pixi install`\n"
        )
        print(f"  WARNING: pixi not found — wrote {setup_notes}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_scaffold.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add src/scaffold_analysis.py tests/test_scaffold.py
git commit -m "feat(sprint7a): scaffolder warns if pixi not installed

Fixes I4 — writes SETUP_NOTES.md with install instructions
when pixi is not found on PATH."
```

---

### Task 4: Default `all` Task in pixi.toml Template

**Files:**
- Modify: `src/templates/pixi.toml`

Fixes: I13, I20, O5

- [ ] **Step 1: Update pixi.toml template**

Replace the commented example section with an actual default:

```toml
[tasks]
py = "python"
build-pdf = "cd phase6_documentation/exec && pandoc REPORT.md -o REPORT.pdf --pdf-engine=xelatex -V geometry:margin=1in -V documentclass:article -V fontsize:11pt --number-sections --toc --filter pandoc-crossref --citeproc -V header-includes='\\usepackage{graphicx}\\setkeys{Gin}{width=0.45\\linewidth,keepaspectratio}'"
# --- Analysis tasks: uncomment and update as you write scripts ---
# acquire = "python phase0_discovery/scripts/acquire_data.py"
# analyze = "python phase3_analysis/scripts/run_analysis.py"
# project = "python phase4_projection/scripts/run_projection.py"
# verify  = "python phase5_verification/scripts/verify_all.py"
# all = { depends-on = ["acquire", "analyze", "project", "verify", "build-pdf"] }
```

- [ ] **Step 2: Verify template renders correctly**

Run: `cd /Users/bamboo/Githubs/OpenPE && python -c "print(open('src/templates/pixi.toml').read())"`
Expected: clean toml with commented task chain

- [ ] **Step 3: Commit**

```bash
git add src/templates/pixi.toml
git commit -m "feat(sprint7a): add default all task template to pixi.toml

Fixes I13, I20, O5 — pixi.toml now has commented task chain
template showing how to wire up the full analysis pipeline."
```

---

### Task 5: Update Orchestrator Protocol for STATE.md + Review Tracking

**Files:**
- Modify: `src/templates/root_claude.md`

Fixes: I5, I19, O7, O10 (protocol-level)

- [ ] **Step 1: Add STATE_UPDATE step to orchestrator loop**

In `src/templates/root_claude.md`, find the orchestrator loop (the numbered list: 1. EXECUTE, 2. REVIEW, 3. CHECK, 4. COMMIT, 5. HUMAN GATE, 6. ADVANCE) and insert after COMMIT:

```markdown
  4b. STATE_UPDATE — Update STATE.md using `scripts/state_manager.py`:
     - Call `state_manager.advance_phase(N, artifact=..., review=...)`
     - This records the phase completion, review result, and iteration count
     - STATE.md is the single source of truth for pipeline progress
     - On resumption after interruption, read STATE.md to determine where to restart
```

- [ ] **Step 2: Add review iteration tracking instructions**

In the Review Protocol section, after the iteration limits paragraph, add:

```markdown
**Review iteration tracking:** Use `scripts/state_manager.py` to track iterations:
- Call `state_manager.record_review_iteration(phase, issues_a, issues_b)` after each review cycle
- `state_manager.should_warn(phase)` returns True at 3 iterations
- `state_manager.should_hard_stop(phase)` returns True at 10 iterations
- If hard stop triggered, present current state to human for guidance
```

- [ ] **Step 3: Commit**

```bash
git add src/templates/root_claude.md
git commit -m "docs(sprint7a): add STATE.md update + review iteration tracking to orchestrator protocol

Fixes I5, I19, O7, O10 at protocol level — orchestrator now
has explicit instructions to update STATE.md after each phase
and track review iterations with warn/hard-stop thresholds."
```

---

### Task 6: Copy New Scripts to Scaffolder Distribution

**Files:**
- Modify: `src/scaffold_analysis.py` (scripts are auto-copied from templates/scripts/)

No code change needed — the scaffolder already copies all `*.py` from `src/templates/scripts/` to `analysis/scripts/`. The new `state_manager.py` and `experiment_logger.py` will be auto-distributed.

- [ ] **Step 1: Verify auto-distribution works**

Run:
```bash
cd /Users/bamboo/Githubs/OpenPE
rm -rf /tmp/test_s7_scaffold
python src/scaffold_analysis.py /tmp/test_s7_scaffold
ls /tmp/test_s7_scaffold/scripts/ | grep -E "state_manager|experiment_logger"
```
Expected: both files present

- [ ] **Step 2: Run full test suite**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v`
Expected: all tests pass (113+ including new ones)

- [ ] **Step 3: Final commit**

```bash
git commit --allow-empty -m "chore(sprint7a): verify scaffolder distributes new modules

state_manager.py and experiment_logger.py auto-distribute via
the existing scripts/ copy loop in scaffold_analysis.py."
```

---

## Verification

After all tasks complete:

```bash
cd /Users/bamboo/Githubs/OpenPE
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

Expected: all tests pass, including:
- `test_state_manager.py` (8 tests)
- `test_experiment_logger.py` (3 tests)
- `test_scaffold.py::test_scaffold_warns_if_pixi_missing`
- All existing tests unchanged
