# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Causal DAG utilities for OpenPE.

Provides CausalEdge and CausalDAG for building, serializing, and
rendering causal directed acyclic graphs. Edges carry EP metadata
(truth × relevance) and can be rendered to Mermaid for documentation.

Reference: OpenPE spec Section 2.2, 5.4
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CausalEdge:
    """A directed edge in a causal DAG with EP metadata."""

    source: str
    target: str
    label: str = "HYPOTHESIZED"
    truth: float = 0.5
    relevance: float = 0.5

    @property
    def ep(self) -> float:
        """Explanatory Power = truth × relevance, bounded in [0, 1]."""
        return max(0.0, min(1.0, self.truth * self.relevance))

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "truth": self.truth,
            "relevance": self.relevance,
            "ep": round(self.ep, 4),
        }

    @classmethod
    def from_dict(cls, d: dict) -> CausalEdge:
        return cls(
            source=d["source"],
            target=d["target"],
            label=d.get("label", "HYPOTHESIZED"),
            truth=d.get("truth", 0.5),
            relevance=d.get("relevance", 0.5),
        )


class CausalDAG:
    """A causal directed acyclic graph with EP-annotated edges."""

    def __init__(self) -> None:
        self.edges: list[CausalEdge] = []

    def add_edge(
        self,
        source: str,
        target: str,
        label: str = "HYPOTHESIZED",
        truth: float = 0.5,
        relevance: float = 0.5,
    ) -> CausalEdge:
        """Add a directed edge and return it."""
        edge = CausalEdge(source=source, target=target, label=label,
                          truth=truth, relevance=relevance)
        self.edges.append(edge)
        return edge

    @property
    def nodes(self) -> set[str]:
        """Return the set of all unique node names."""
        result: set[str] = set()
        for edge in self.edges:
            result.add(edge.source)
            result.add(edge.target)
        return result

    def to_mermaid(self) -> str:
        """Generate a Mermaid graph TD diagram with EP annotations on edges."""
        lines = ["graph TD"]
        for edge in self.edges:
            ep_str = f"{edge.ep:.3f}"
            annotation = f"{edge.label} EP={ep_str}"
            lines.append(f'    {edge.source} -->|"{annotation}"| {edge.target}')
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict) -> CausalDAG:
        dag = cls()
        for ed in d.get("edges", []):
            dag.edges.append(CausalEdge.from_dict(ed))
        return dag
