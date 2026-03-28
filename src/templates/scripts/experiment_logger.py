# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Max en Wong, 2026

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
