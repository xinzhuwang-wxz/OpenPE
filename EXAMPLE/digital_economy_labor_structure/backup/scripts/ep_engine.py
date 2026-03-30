# Copyright 2026 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Explanatory Power (EP) engine for OpenPE.

EP = truth × relevance, where both are bounded in [0, 1].
Joint EP along a chain decays multiplicatively.
Truncation thresholds determine chain expansion decisions.

Reference: OpenPE spec Section 2.2-2.3
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# Default thresholds (can be overridden from analysis_config.yaml)
HARD_TRUNCATION = 0.05
SOFT_TRUNCATION = 0.15
SUBCHAIN_EXPANSION = 0.30


def compute_ep(truth: float, relevance: float) -> float:
    """Compute Explanatory Power = truth × relevance, bounded in [0, 1]."""
    return max(0.0, min(1.0, truth * relevance))


def joint_ep(eps: list[float]) -> float:
    """Compute joint EP along a chain (multiplicative decay)."""
    result = 1.0
    for ep in eps:
        result *= ep
    return result


def truncation_decision(
    jep: float,
    hard: float = HARD_TRUNCATION,
    soft: float = SOFT_TRUNCATION,
) -> str:
    """Determine truncation decision based on joint EP.

    Returns: "HARD_TRUNCATION" | "SOFT_TRUNCATION" | "NORMAL"
    """
    if jep < hard:
        return "HARD_TRUNCATION"
    elif jep < soft:
        return "SOFT_TRUNCATION"
    else:
        return "NORMAL"


def classify_truth(evidence_type: str) -> float:
    """Map evidence classification to default truth value.

    Post-analysis labels (Phase 3, after refutation testing):
        DATA_SUPPORTED → 0.85 (midpoint of [0.7, 1.0])
        CORRELATION    → 0.50 (midpoint of [0.3, 0.7])
        HYPOTHESIZED   → 0.15 (midpoint of [0.0, 0.3])
        DISPUTED       → 0.30 (treated as weak correlation pending review)

    Pre-analysis labels (Phase 0, hypothesis_agent):
        LITERATURE_SUPPORTED → 0.70 (published academic support)
        THEORIZED            → 0.40 (domain theory, no direct empirical citation)
        SPECULATIVE          → 0.15 (novel hypothesis, no basis)
    """
    mapping = {
        # Post-analysis labels
        "DATA_SUPPORTED": 0.85,
        "CORRELATION": 0.50,
        "HYPOTHESIZED": 0.15,
        "DISPUTED": 0.30,
        # Pre-analysis labels (spec Section 4.2)
        "LITERATURE_SUPPORTED": 0.70,
        "THEORIZED": 0.40,
        "SPECULATIVE": 0.15,
    }
    return mapping.get(evidence_type, 0.15)


@dataclass
class EPNode:
    """A node in an explanatory chain with EP metadata."""

    event_id: str
    truth: float
    relevance: float
    evidence_type: str = "HYPOTHESIZED"
    description: str = ""

    @property
    def ep(self) -> float:
        return compute_ep(self.truth, self.relevance)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "truth": self.truth,
            "relevance": self.relevance,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "ep": round(self.ep, 4),
        }

    @classmethod
    def from_dict(cls, d: dict) -> EPNode:
        return cls(
            event_id=d["event_id"],
            truth=d["truth"],
            relevance=d["relevance"],
            evidence_type=d.get("evidence_type", "HYPOTHESIZED"),
            description=d.get("description", ""),
        )


@dataclass
class EPChain:
    """An explanatory chain with EP propagation and truncation tracking."""

    nodes: list[EPNode] = field(default_factory=list)

    def add_node(self, node: EPNode) -> None:
        self.nodes.append(node)

    @property
    def joint_ep(self) -> float:
        return joint_ep([n.ep for n in self.nodes])

    @property
    def truncation(self) -> str:
        return truncation_decision(self.joint_ep)

    def should_expand_subchain(self, node: EPNode) -> bool:
        """Check if a node warrants sub-chain expansion."""
        return (
            node.ep > SUBCHAIN_EXPANSION
            and self.joint_ep > SOFT_TRUNCATION
        )

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "joint_ep": round(self.joint_ep, 4),
            "truncation": self.truncation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EPChain:
        chain = cls()
        for nd in d.get("nodes", []):
            chain.add_node(EPNode.from_dict(nd))
        return chain
