"""Cross-analysis memory store for OpenPE.

Tiered L0/L1/L2 memory system with confidence scoring and decay.
Memories persist across analyses, enabling learning from experience.

L0: Universal principles (always loaded, ~500 tokens)
L1: Domain-specific experiences (loaded for matching domain, ~2000 tokens)
L2: Detailed past analysis records (loaded on-demand)

Hotness scoring and archival borrowed from OpenViking memory lifecycle.
Deduplication uses keyword overlap similarity.

Reference: OpenPE spec — Memory System Design
"""
from __future__ import annotations

import math
import re
import shutil
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml


# Confidence evolution constants
CORROBORATION_BOOST = 0.15
CONTRADICTION_PENALTY = 0.25
DECAY_PER_ANALYSIS = 0.01
CONFIDENCE_CAP = 0.95
CONFIDENCE_FLOOR = 0.05

# Loading thresholds
NORMAL_THRESHOLD = 0.2
WARNING_THRESHOLD = 0.1

# Hotness scoring (from OpenViking memory_lifecycle.py)
DEFAULT_HALF_LIFE_DAYS = 30.0
ARCHIVE_HOTNESS_THRESHOLD = 0.1


MemoryTier = Literal["L0", "L1", "L2"]
MemoryType = Literal["domain", "method", "data_source", "failure", "principle"]


@dataclass
class MemoryEntry:
    """A single memory entry with confidence tracking."""

    memory_id: str
    content: str
    domain: str
    memory_type: MemoryType
    tier: MemoryTier
    confidence: float = 0.5
    source_analysis: str = ""
    corroborated_by: list[str] = field(default_factory=list)
    contradicted_by: list[str] = field(default_factory=list)
    decay_rate: float = DECAY_PER_ANALYSIS
    active_count: int = 0
    created: str = ""
    updated: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created:
            self.created = now
        if not self.updated:
            self.updated = now

    def corroborate(self, analysis_id: str) -> None:
        """Increase confidence when corroborated by independent analysis."""
        if analysis_id not in self.corroborated_by:
            self.corroborated_by.append(analysis_id)
        self.confidence = min(CONFIDENCE_CAP, self.confidence + CORROBORATION_BOOST)
        self.updated = datetime.now().isoformat()

    def contradict(self, analysis_id: str) -> None:
        """Decrease confidence when contradicted by independent analysis."""
        if analysis_id not in self.contradicted_by:
            self.contradicted_by.append(analysis_id)
        self.confidence = max(CONFIDENCE_FLOOR, self.confidence - CONTRADICTION_PENALTY)
        self.updated = datetime.now().isoformat()

    def decay(self) -> None:
        """Apply per-analysis confidence decay."""
        self.confidence = max(CONFIDENCE_FLOOR, self.confidence - self.decay_rate)
        self.updated = datetime.now().isoformat()

    @property
    def is_quarantined(self) -> bool:
        return self.confidence < WARNING_THRESHOLD

    @property
    def needs_warning(self) -> bool:
        return WARNING_THRESHOLD <= self.confidence < NORMAL_THRESHOLD

    @property
    def loading_prefix(self) -> str:
        if self.is_quarantined:
            return "[QUARANTINED] "
        if self.needs_warning:
            return "[WARNING: low confidence] "
        return ""

    @property
    def hotness(self) -> float:
        """Compute hotness score (frequency × recency).

        Borrowed from OpenViking memory_lifecycle.py hotness_score().
        Returns 0.0-1.0. Higher = hotter (more recently/frequently used).
        """
        return hotness_score(self.active_count, self.updated)

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "domain": self.domain,
            "memory_type": self.memory_type,
            "tier": self.tier,
            "confidence": round(self.confidence, 4),
            "source_analysis": self.source_analysis,
            "corroborated_by": self.corroborated_by,
            "contradicted_by": self.contradicted_by,
            "decay_rate": self.decay_rate,
            "active_count": self.active_count,
            "created": self.created,
            "updated": self.updated,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MemoryEntry:
        return cls(
            memory_id=d["memory_id"],
            content=d["content"],
            domain=d.get("domain", "general"),
            memory_type=d.get("memory_type", "domain"),
            tier=d.get("tier", "L1"),
            confidence=d.get("confidence", 0.5),
            source_analysis=d.get("source_analysis", ""),
            corroborated_by=d.get("corroborated_by", []),
            contradicted_by=d.get("contradicted_by", []),
            decay_rate=d.get("decay_rate", DECAY_PER_ANALYSIS),
            active_count=d.get("active_count", 0),
            created=d.get("created", ""),
            updated=d.get("updated", ""),
        )


class MemoryStore:
    """Tiered memory store with file-system persistence.

    Directory layout:
        memory_root/
            L0/         universal principles
            L1/         domain-specific experiences
            L2/         detailed analysis records
    """

    def __init__(self, memory_root: Path) -> None:
        self.root = Path(memory_root)
        self.entries: dict[str, MemoryEntry] = {}
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for tier in ("L0", "L1", "L2"):
            (self.root / tier).mkdir(parents=True, exist_ok=True)

    def _entry_path(self, entry: MemoryEntry) -> Path:
        return self.root / entry.tier / f"{entry.memory_id}.yaml"

    def add(self, entry: MemoryEntry) -> None:
        """Add or overwrite a memory entry."""
        self.entries[entry.memory_id] = entry
        self._save_entry(entry)

    def get(self, memory_id: str) -> MemoryEntry | None:
        return self.entries.get(memory_id)

    def _save_entry(self, entry: MemoryEntry) -> None:
        path = self._entry_path(entry)
        with open(path, "w") as f:
            yaml.dump(entry.to_dict(), f, default_flow_style=False, sort_keys=False)

    def load_all(self) -> None:
        """Load all entries from disk."""
        self.entries.clear()
        for tier in ("L0", "L1", "L2"):
            tier_dir = self.root / tier
            if not tier_dir.exists():
                continue
            for path in tier_dir.glob("*.yaml"):
                with open(path) as f:
                    data = yaml.safe_load(f)
                if data:
                    entry = MemoryEntry.from_dict(data)
                    self.entries[entry.memory_id] = entry

    def load_for_analysis(self, domain: str) -> list[MemoryEntry]:
        """Load memories relevant to a domain analysis.

        Returns L0 (all) + L1 (matching domain) entries.
        Quarantined entries (conf < 0.1) are excluded by default.
        Increments active_count for each loaded entry.
        """
        self.load_all()
        result = []
        for entry in self.entries.values():
            if entry.is_quarantined:
                continue
            if entry.tier == "L0":
                entry.active_count += 1
                self._save_entry(entry)
                result.append(entry)
            elif entry.tier == "L1" and entry.domain == domain:
                entry.active_count += 1
                self._save_entry(entry)
                result.append(entry)
        return sorted(result, key=lambda e: e.confidence, reverse=True)

    def load_l2(self, memory_id: str) -> MemoryEntry | None:
        """Load a specific L2 entry on demand."""
        path = self.root / "L2" / f"{memory_id}.yaml"
        if not path.exists():
            return None
        with open(path) as f:
            data = yaml.safe_load(f)
        if data:
            entry = MemoryEntry.from_dict(data)
            self.entries[entry.memory_id] = entry
            return entry
        return None

    def apply_decay(self) -> None:
        """Apply per-analysis decay to all entries and persist."""
        self.load_all()
        for entry in self.entries.values():
            entry.decay()
            self._save_entry(entry)

    def corroborate(self, memory_id: str, analysis_id: str) -> bool:
        """Corroborate an existing memory. Returns False if not found."""
        entry = self.entries.get(memory_id)
        if entry is None:
            return False
        entry.corroborate(analysis_id)
        self._save_entry(entry)
        return True

    def contradict(self, memory_id: str, analysis_id: str) -> bool:
        """Contradict an existing memory. Returns False if not found."""
        entry = self.entries.get(memory_id)
        if entry is None:
            return False
        entry.contradict(analysis_id)
        self._save_entry(entry)
        return True

    def archive(self, threshold: float = ARCHIVE_HOTNESS_THRESHOLD) -> list[str]:
        """Move cold L2 entries to _archive/ subdirectory.

        Borrowed from OpenViking memory_archiver.py scan/archive pattern.
        Only archives L2 entries (never L0/L1). Returns archived memory IDs.
        """
        self.load_all()
        archived = []
        archive_dir = self.root / "L2" / "_archive"

        for entry in list(self.entries.values()):
            if entry.tier != "L2":
                continue
            if entry.hotness < threshold:
                archive_dir.mkdir(parents=True, exist_ok=True)
                src = self._entry_path(entry)
                dst = archive_dir / f"{entry.memory_id}.yaml"
                if src.exists():
                    shutil.move(str(src), str(dst))
                    archived.append(entry.memory_id)
                    del self.entries[entry.memory_id]

        return archived

    PROMOTION_CORROBORATION_MIN = 3
    DEMOTION_CONFIDENCE_MAX = 0.3

    def promote_tier(self, memory_id: str) -> bool:
        """Promote L1→L0 if corroboration threshold is met.
        Moves the YAML file from L1/ to L0/ on disk.
        """
        entry = self.entries.get(memory_id)
        if entry is None or entry.tier != "L1":
            return False
        if len(entry.corroborated_by) < self.PROMOTION_CORROBORATION_MIN:
            return False

        old_path = self._entry_path(entry)
        entry.tier = "L0"
        entry.updated = datetime.now().isoformat()
        new_path = self._entry_path(entry)

        self._save_entry(entry)
        if old_path.exists() and old_path != new_path:
            old_path.unlink()

        return True

    def find_similar(
        self,
        content: str,
        candidates: list[MemoryEntry] | None = None,
        threshold: float = 0.3,
    ) -> list[tuple[MemoryEntry, float]]:
        """Find similar memories using keyword overlap (Jaccard similarity).

        No embeddings required — uses simple word-level overlap.
        Returns list of (entry, similarity_score) sorted by score descending.
        """
        if candidates is None:
            candidates = list(self.entries.values())

        query_words = _tokenize(content)
        if not query_words:
            return []

        results = []
        for entry in candidates:
            entry_words = _tokenize(entry.content)
            if not entry_words:
                continue
            intersection = query_words & entry_words
            union = query_words | entry_words
            similarity = len(intersection) / len(union) if union else 0.0
            if similarity >= threshold:
                results.append((entry, similarity))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def to_context_string(self, entries: list[MemoryEntry] | None = None) -> str:
        """Format entries for injection into agent context."""
        if entries is None:
            entries = list(self.entries.values())
        lines = []
        for entry in entries:
            prefix = entry.loading_prefix
            lines.append(f"- {prefix}{entry.content} (conf={entry.confidence:.2f})")
        return "\n".join(lines)


# --- Module-level utility functions ---

def hotness_score(
    active_count: int,
    updated_at: str,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
) -> float:
    """Compute hotness score = sigmoid(frequency) × exponential_recency.

    Borrowed from OpenViking memory_lifecycle.py.
    Returns 0.0-1.0. Higher means hotter (more active/recent).

    Args:
        active_count: number of times this memory has been loaded.
        updated_at: ISO timestamp of last update.
        half_life_days: time for recency to decay by half.
    """
    # Frequency component: sigmoid of log(1 + count)
    freq = 1.0 / (1.0 + math.exp(-math.log1p(active_count)))

    # Recency component: exponential decay from last update
    try:
        updated_dt = datetime.fromisoformat(updated_at)
        age_days = max((datetime.now() - updated_dt).total_seconds() / 86400.0, 0.0)
    except (ValueError, TypeError):
        age_days = 365.0  # unknown → treat as old

    decay_rate = math.log(2) / half_life_days
    recency = math.exp(-decay_rate * age_days)

    return freq * recency


def _tokenize(text: str) -> set[str]:
    """Extract lowercase word tokens from text for similarity comparison."""
    return set(re.findall(r"\w+", text.lower()))
