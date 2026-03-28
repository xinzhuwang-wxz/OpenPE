# Copyright 2026 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Persistent causal knowledge graph for OpenPE.

Stores established causal relationships across analyses with confidence
tracking. Enables knowledge reuse: high-confidence relationships can
skip re-testing, while contradictions trigger review.

Temporal validity fields borrowed from Graphiti EntityEdge pattern:
valid_at/invalid_at track when a relationship was true, expired_at
tracks metadata staleness.

Reference: OpenPE spec — Causal Knowledge Graph (Graphiti Integration)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal


# Reuse policy thresholds
SKIP_RETEST_THRESHOLD = 0.8
LIGHTWEIGHT_VERIFY_THRESHOLD = 0.5


ReusePolicy = Literal["SKIP", "LIGHTWEIGHT_VERIFY", "MUST_RETEST"]


@dataclass
class CausalRelationship:
    """A directed causal or correlational relationship."""

    source: str
    target: str
    relationship_type: str  # "CAUSES" | "CORRELATED_WITH" | "HYPOTHESIZED"
    strength: float = 0.5
    confidence: float = 0.5
    source_analyses: list[str] = field(default_factory=list)
    corroborated_by: list[str] = field(default_factory=list)
    contradicted_by: list[str] = field(default_factory=list)
    # Temporal validity (from Graphiti EntityEdge pattern)
    valid_at: str = ""       # when the relationship became true
    invalid_at: str = ""     # when it stopped being true (empty = still valid)
    expired_at: str = ""     # when the metadata became stale
    episodes: list[str] = field(default_factory=list)  # source analysis references
    created: str = ""
    updated: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created:
            self.created = now
        if not self.updated:
            self.updated = now

    @property
    def edge_id(self) -> str:
        return f"{self.source}→{self.target}"

    @property
    def reuse_policy(self) -> ReusePolicy:
        if self.confidence >= SKIP_RETEST_THRESHOLD:
            return "SKIP"
        elif self.confidence >= LIGHTWEIGHT_VERIFY_THRESHOLD:
            return "LIGHTWEIGHT_VERIFY"
        else:
            return "MUST_RETEST"

    @property
    def is_valid(self) -> bool:
        """Whether the relationship is currently considered valid."""
        return not self.invalid_at

    @property
    def is_expired(self) -> bool:
        """Whether the metadata has become stale."""
        return bool(self.expired_at)

    def invalidate(self, analysis_id: str) -> None:
        """Mark relationship as no longer true (from Graphiti temporal pattern)."""
        self.invalid_at = datetime.now().isoformat()
        if analysis_id not in self.episodes:
            self.episodes.append(analysis_id)
        self.updated = datetime.now().isoformat()

    def corroborate(self, analysis_id: str) -> None:
        if analysis_id not in self.corroborated_by:
            self.corroborated_by.append(analysis_id)
        self.confidence = min(0.95, self.confidence + 0.10)
        self.updated = datetime.now().isoformat()

    def contradict(self, analysis_id: str) -> None:
        if analysis_id not in self.contradicted_by:
            self.contradicted_by.append(analysis_id)
        self.confidence = max(0.05, self.confidence - 0.20)
        self.updated = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
            "strength": round(self.strength, 4),
            "confidence": round(self.confidence, 4),
            "source_analyses": self.source_analyses,
            "corroborated_by": self.corroborated_by,
            "contradicted_by": self.contradicted_by,
            "valid_at": self.valid_at,
            "invalid_at": self.invalid_at,
            "expired_at": self.expired_at,
            "episodes": self.episodes,
            "created": self.created,
            "updated": self.updated,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CausalRelationship:
        return cls(
            source=d["source"],
            target=d["target"],
            relationship_type=d.get("relationship_type", "HYPOTHESIZED"),
            strength=d.get("strength", 0.5),
            confidence=d.get("confidence", 0.5),
            source_analyses=d.get("source_analyses", []),
            corroborated_by=d.get("corroborated_by", []),
            contradicted_by=d.get("contradicted_by", []),
            valid_at=d.get("valid_at", ""),
            invalid_at=d.get("invalid_at", ""),
            expired_at=d.get("expired_at", ""),
            episodes=d.get("episodes", []),
            created=d.get("created", ""),
            updated=d.get("updated", ""),
        )


class CausalKnowledgeGraph:
    """Persistent graph of established causal relationships.

    Stored as graph.json in the memory root.
    """

    def __init__(self, graph_path: Path) -> None:
        self.path = Path(graph_path)
        self.relationships: dict[str, CausalRelationship] = {}

    def load(self) -> None:
        """Load graph from disk."""
        if not self.path.exists():
            return
        with open(self.path) as f:
            data = json.load(f)
        self.relationships.clear()
        for rd in data.get("relationships", []):
            rel = CausalRelationship.from_dict(rd)
            self.relationships[rel.edge_id] = rel

    def save(self) -> None:
        """Persist graph to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "generated": datetime.now().isoformat(),
            "total_relationships": len(self.relationships),
            "relationships": [r.to_dict() for r in self.relationships.values()],
        }
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str = "HYPOTHESIZED",
        strength: float = 0.5,
        confidence: float = 0.5,
        analysis_id: str = "",
    ) -> CausalRelationship:
        """Add or update a causal relationship."""
        edge_id = f"{source}→{target}"
        if edge_id in self.relationships:
            existing = self.relationships[edge_id]
            existing.corroborate(analysis_id)
            if relationship_type == "CAUSES" and existing.relationship_type != "CAUSES":
                existing.relationship_type = relationship_type
            existing.strength = (existing.strength + strength) / 2
            return existing

        rel = CausalRelationship(
            source=source,
            target=target,
            relationship_type=relationship_type,
            strength=strength,
            confidence=confidence,
            source_analyses=[analysis_id] if analysis_id else [],
        )
        self.relationships[edge_id] = rel
        return rel

    def query(
        self,
        source: str | None = None,
        target: str | None = None,
        min_confidence: float = 0.0,
        only_valid: bool = True,
    ) -> list[CausalRelationship]:
        """Query relationships by source/target node and minimum confidence.

        Args:
            only_valid: if True (default), exclude invalidated relationships.
        """
        results = []
        for rel in self.relationships.values():
            if only_valid and not rel.is_valid:
                continue
            if source and rel.source != source:
                continue
            if target and rel.target != target:
                continue
            if rel.confidence < min_confidence:
                continue
            results.append(rel)
        return sorted(results, key=lambda r: r.confidence, reverse=True)

    def get_reuse_policy(self, source: str, target: str) -> tuple[ReusePolicy, CausalRelationship | None]:
        """Check reuse policy for a specific edge."""
        edge_id = f"{source}→{target}"
        rel = self.relationships.get(edge_id)
        if rel is None:
            return "MUST_RETEST", None
        return rel.reuse_policy, rel

    def detect_contradictions(
        self,
        source: str,
        target: str,
        new_type: str,
        analysis_id: str,
    ) -> bool:
        """Check if a new finding contradicts existing knowledge.

        Returns True if contradiction detected (and updates the graph).
        """
        edge_id = f"{source}→{target}"
        existing = self.relationships.get(edge_id)
        if existing is None:
            return False

        is_contradiction = (
            (existing.relationship_type == "CAUSES" and new_type == "CORRELATED_WITH")
            or (existing.relationship_type == "CAUSES" and new_type == "HYPOTHESIZED")
        )
        if is_contradiction:
            existing.contradict(analysis_id)
            return True
        return False

    def invalidate_edge(self, source: str, target: str, analysis_id: str) -> bool:
        """Mark a relationship as no longer valid (Graphiti temporal pattern).

        Unlike contradict() which lowers confidence, invalidate() marks the
        relationship as temporally ended — it was true before but no longer.
        """
        edge_id = f"{source}→{target}"
        rel = self.relationships.get(edge_id)
        if rel is None:
            return False
        rel.invalidate(analysis_id)
        return True

    def prune_stale(self, max_age_days: int = 180) -> list[str]:
        """Mark old unconfirmed relationships as expired.

        Relationships with confidence < 0.5 that haven't been updated
        in max_age_days are marked expired. Returns expired edge IDs.
        """
        now = datetime.now()
        expired = []
        for rel in self.relationships.values():
            if rel.is_expired or rel.confidence >= LIGHTWEIGHT_VERIFY_THRESHOLD:
                continue
            try:
                updated_dt = datetime.fromisoformat(rel.updated)
                age = (now - updated_dt).days
            except (ValueError, TypeError):
                age = max_age_days + 1

            if age > max_age_days:
                rel.expired_at = now.isoformat()
                rel.updated = now.isoformat()
                expired.append(rel.edge_id)

        return expired

    def to_mermaid(self, min_confidence: float = 0.0, only_valid: bool = True) -> str:
        """Render graph as Mermaid diagram."""
        lines = ["graph TD"]
        for rel in self.relationships.values():
            if rel.confidence < min_confidence:
                continue
            if only_valid and not rel.is_valid:
                continue
            style = {
                "CAUSES": "-->",
                "CORRELATED_WITH": "-.->"
            }.get(rel.relationship_type, "-.->")
            label = f"{rel.relationship_type} c={rel.confidence:.2f}"
            lines.append(f'    {rel.source} {style}|"{label}"| {rel.target}')
        return "\n".join(lines)
