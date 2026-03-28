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
        self.data_callbacks_used: int = 0

    def save(self) -> None:
        """Write STATE.md to disk."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "# Analysis State\n",
            f"- **Analysis**: {self.analysis_name}",
            f"- **Current phase**: {self.current_phase}",
            f"- **Status**: {self.status}",
            f"- **Last updated**: {now}",
            f"- **Data callbacks used**: {self.data_callbacks_used}/{self.MAX_DATA_CALLBACKS}\n",
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

        m = re.search(r"\*\*Current phase\*\*:\s*(\d+)", text)
        if m:
            self.current_phase = int(m.group(1))

        m = re.search(r"\*\*Status\*\*:\s*(.+)", text)
        if m:
            self.status = m.group(1).strip()

        m = re.search(r"\*\*Analysis\*\*:\s*(.+)", text)
        if m:
            self.analysis_name = m.group(1).strip()

        m = re.search(r"\*\*Data callbacks used\*\*:\s*(\d+)", text)
        if m:
            self.data_callbacks_used = int(m.group(1))

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

    # --- Data callback tracking ---

    MAX_DATA_CALLBACKS = 2

    def record_data_callback(self, reason: str) -> bool:
        """Record a data callback invocation.

        Returns True if the callback is allowed (under cap), False if denied.
        The orchestrator must check this BEFORE spawning the data agent.
        """
        if self.data_callbacks_used >= self.MAX_DATA_CALLBACKS:
            return False
        self.data_callbacks_used += 1
        self.save()
        return True

    def can_data_callback(self) -> bool:
        """Check if a data callback is still allowed."""
        return self.data_callbacks_used < self.MAX_DATA_CALLBACKS

    def add_blocker(self, description: str) -> None:
        self.blockers.append(description)
        self.save()
