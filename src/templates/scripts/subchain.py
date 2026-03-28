# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Sub-chain expansion utility for OpenPE.

When a main-chain event has EP > 0.3 and Joint_EP > 0.15,
the orchestrator can scaffold a sub-analysis to investigate
specific causal edges in depth.

Reference: OpenPE spec Section 2.4
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from dataclasses import dataclass

import yaml


@dataclass
class SubChainRequest:
    """Request to expand a sub-chain for deeper investigation."""
    parent_analysis: Path
    event_id: str
    edges_to_investigate: list[str]
    ep_threshold: float
    context_summary: str

    def to_dict(self) -> dict:
        return {
            "parent_analysis": str(self.parent_analysis),
            "event_id": self.event_id,
            "edges_to_investigate": self.edges_to_investigate,
            "ep_threshold": self.ep_threshold,
            "context_summary": self.context_summary,
        }


@dataclass
class SubChainResult:
    """Result returned from a sub-chain analysis."""
    sub_analysis_path: Path
    updated_eps: dict[str, float]  # edge_id → new EP
    classifications: dict[str, str]  # edge_id → DATA_SUPPORTED|CORRELATION|etc
    findings_summary: str  # ≤500 words

    def to_dict(self) -> dict:
        return {
            "sub_analysis_path": str(self.sub_analysis_path),
            "updated_eps": self.updated_eps,
            "classifications": self.classifications,
            "findings_summary": self.findings_summary,
        }


def should_expand(node_ep: float, chain_joint_ep: float,
                   min_ep: float = 0.30, min_joint: float = 0.15) -> bool:
    """Check if a node warrants sub-chain expansion.

    Expansion condition (from spec):
      node EP > 0.30 AND Joint_EP at expansion point > 0.15
    """
    return node_ep > min_ep and chain_joint_ep > min_joint


def scaffold_subanalysis(
    parent_dir: Path,
    event_id: str,
    scaffolder_path: Path | None = None,
) -> Path:
    """Scaffold a sub-analysis directory within the parent analysis.

    Creates: phase3_analysis/sub_analyses/{event_id}/
    with the standard OpenPE phase structure (lightweight).
    """
    sub_dir = parent_dir / "phase3_analysis" / "sub_analyses" / event_id

    if sub_dir.exists():
        return sub_dir

    sub_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal sub-analysis structure
    for phase in ["phase0_discovery", "phase1_strategy", "phase2_exploration",
                   "phase3_analysis", "phase4_projection", "phase5_verification"]:
        (sub_dir / phase).mkdir(exist_ok=True)
        (sub_dir / phase / "exec").mkdir(exist_ok=True)

    # Write sub-analysis config
    config = {
        "parent_analysis": str(parent_dir),
        "event_id": event_id,
        "is_subchain": True,
        "max_recursion_depth": 0,  # Sub-chains cannot expand further
        "review_tier": "1-bot",  # Lightweight review for sub-chains
    }
    with open(sub_dir / "subchain_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    return sub_dir
