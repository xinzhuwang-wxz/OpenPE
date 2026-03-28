# OpenPE Sprint 6: Reference Project Integration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance existing Sprint 1-5 modules by integrating proven patterns from reference projects (OpenViking, Graphiti, ACG Protocol, Causica, DoWhy). Fix the DoWhy CI extraction bug. Add new causal structure discovery capability using the PC algorithm.

**Architecture:** Enhancements to existing Python modules in `src/templates/scripts/`. New `causal_discovery.py` module wraps causal-learn's PC algorithm with a correlation-threshold fallback. All borrowed patterns are self-contained (no new external API dependencies beyond causal-learn).

**Tech Stack:** Python 3.11+, causal-learn (PC algorithm), numpy, scipy, pandas, pyyaml

**Spec:** `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` — Sections 3.2 Phase 0 (Discovery), 4.1-4.3 (Memory), 4.4 (Knowledge Graph)

**Reference projects consulted:**
- OpenViking: hotness scoring, memory archival, deduplication
- Graphiti: temporal validity fields on graph edges
- ACG Protocol: inline grounding markers (IGM), source registry (SSR), veracity audit (VAR)
- Causica: graph evaluation metrics (precision/recall/F1)
- DoWhy: `CausalEstimate.get_confidence_intervals()` API

---

## File Map

### Files to Create
- `src/templates/scripts/causal_discovery.py` — PC algorithm wrapper for DAG structure learning
- `tests/test_causal_discovery.py` — Discovery module unit tests
- `tests/test_sprint6_integration.py` — End-to-end integration test

### Files to Modify
- `src/templates/scripts/causal_pipeline.py` — Fix DoWhy CI extraction bug (line ~211)
- `src/templates/scripts/memory_store.py` — Add hotness scoring, archival, deduplication
- `src/templates/scripts/causal_knowledge_graph.py` — Add temporal validity fields
- `src/templates/scripts/audit_trail.py` — Add IGM/SSR/VAR from ACG Protocol
- `src/templates/pixi.toml` — Add `causal-learn` dependency
- `tests/test_causal_pipeline.py` — Skip test when DoWhy unavailable

---

## Task 1: Fix DoWhy CI Extraction + Failing Test

**Files:**
- Modify: `src/templates/scripts/causal_pipeline.py`
- Modify: `tests/test_causal_pipeline.py`

- [ ] **Step 1: Fix causal_pipeline.py CI extraction**

DoWhy's `CausalEstimate` object does NOT have a `.confidence_intervals` attribute. The correct API is `estimate.get_confidence_intervals()` which returns a tuple `(lower, upper)`.

Replace lines ~211-212:
```python
# WRONG (current):
ci_lower=getattr(estimate, 'confidence_intervals', [None, None])[0]
ci_upper=getattr(estimate, 'confidence_intervals', [None, None])[1]

# CORRECT:
# Use the _extract_ci() static method
```

Add static method to `CausalTest` before `_run_fallback()`:
```python
@staticmethod
def _extract_ci(estimate, index: int):
    """Extract confidence interval bound from DoWhy estimate.

    DoWhy's CausalEstimate uses get_confidence_intervals() method,
    not a stored attribute. Reference: dowhy/causal_estimator.py
    """
    try:
        ci = estimate.get_confidence_intervals()
        if ci is not None and len(ci) > index:
            return ci[index]
    except Exception:
        pass
    return None
```

Then update the CausalTestResult construction:
```python
ci_lower=self._extract_ci(estimate, 0),
ci_upper=self._extract_ci(estimate, 1),
```

- [ ] **Step 2: Fix test_causal_pipeline.py**

Add skip marker for DoWhy-dependent test:
```python
import importlib.util
_dowhy_available = importlib.util.find_spec("dowhy") is not None

@pytest.mark.skipif(not _dowhy_available, reason="DoWhy not installed")
def test_causal_test_with_synthetic_data():
    ...
```

- [ ] **Step 3: Verify fix**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_pipeline.py -v
```

Commit: `git commit -m "fix: correct DoWhy CI extraction API and skip test when unavailable"`

---

## Task 2: Enhance memory_store.py with OpenViking Patterns

**Files:**
- Modify: `src/templates/scripts/memory_store.py`

- [ ] **Step 1: Add imports and constants**

Add to imports: `import math`, `import re`, `import shutil`

Add constants:
```python
DEFAULT_HALF_LIFE_DAYS = 30.0
ARCHIVE_HOTNESS_THRESHOLD = 0.1
```

- [ ] **Step 2: Add hotness scoring**

Add module-level function (adapted from OpenViking `memory_lifecycle.py`):
```python
def hotness_score(active_count: int, updated_at: str, half_life_days: float = DEFAULT_HALF_LIFE_DAYS) -> float:
    """Compute hotness score = sigmoid(frequency) × exponential_recency.

    Returns 0.0-1.0. Higher means hotter (more active/recent).
    """
    freq = 1.0 / (1.0 + math.exp(-math.log1p(active_count)))
    try:
        updated_dt = datetime.fromisoformat(updated_at)
        age_days = max((datetime.now() - updated_dt).total_seconds() / 86400.0, 0.0)
    except (ValueError, TypeError):
        age_days = 365.0
    decay_rate = math.log(2) / half_life_days
    recency = math.exp(-decay_rate * age_days)
    return freq * recency
```

Add `_tokenize()` helper:
```python
def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))
```

- [ ] **Step 3: Add fields and property to MemoryEntry**

Add field: `active_count: int = 0`

Add property:
```python
@property
def hotness(self) -> float:
    return hotness_score(self.active_count, self.updated)
```

Update `to_dict()` and `from_dict()` to include `active_count`.

- [ ] **Step 4: Enhance MemoryStore**

Update `load_for_analysis()` to increment `active_count` on each loaded entry and save.

Add `archive(threshold) -> list[str]`:
- Only archives L2 entries with hotness < threshold
- Moves YAML files to `L2/_archive/` subdirectory
- Returns archived memory IDs

Add `find_similar(content, candidates, threshold) -> list[tuple[MemoryEntry, float]]`:
- Jaccard similarity on tokenized word sets
- Returns (entry, score) tuples above threshold, sorted descending

- [ ] **Step 5: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py -v
```

Commit: `git commit -m "feat: add hotness scoring, archival, and deduplication to memory store"`

---

## Task 3: Enhance causal_knowledge_graph.py with Graphiti Temporal Patterns

**Files:**
- Modify: `src/templates/scripts/causal_knowledge_graph.py`

- [ ] **Step 1: Add temporal fields to CausalRelationship**

```python
# Temporal validity (from Graphiti EntityEdge pattern)
valid_at: str = ""       # when the relationship became true
invalid_at: str = ""     # when it stopped being true (empty = still valid)
expired_at: str = ""     # when the metadata became stale
episodes: list[str] = field(default_factory=list)  # source analysis references
```

- [ ] **Step 2: Add properties and methods**

```python
@property
def is_valid(self) -> bool:
    return not self.invalid_at

@property
def is_expired(self) -> bool:
    return bool(self.expired_at)

def invalidate(self, analysis_id: str) -> None:
    self.invalid_at = datetime.now().isoformat()
    if analysis_id not in self.episodes:
        self.episodes.append(analysis_id)
    self.updated = datetime.now().isoformat()
```

Update `to_dict()` and `from_dict()` with all temporal fields.

- [ ] **Step 3: Enhance CausalKnowledgeGraph methods**

Add `only_valid` parameter to `query()` (default True) — filters out invalidated relationships.

Add `invalidate_edge(source, target, analysis_id) -> bool`.

Add `prune_stale(max_age_days=180) -> list[str]` — marks old low-confidence relationships as expired.

Add `only_valid` parameter to `to_mermaid()`.

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_knowledge_graph.py -v
```

Commit: `git commit -m "feat: add temporal validity to causal knowledge graph"`

---

## Task 4: Enhance audit_trail.py with ACG Protocol Patterns

**Files:**
- Modify: `src/templates/scripts/audit_trail.py`

- [ ] **Step 1: Add ACG Protocol data structures**

Add module-level constants and functions:
```python
SHI_PREFIX_LENGTH = 10

def compute_shi(content: str | bytes) -> str:
    """SHA-256 hash of source content."""
    ...

def construct_igm(claim_id, source_hash, location) -> str:
    """Inline Grounding Marker: [C1:a1b2c3d4e5:path:selector]"""
    ...

def construct_rm(relation_id, relation_type, dep_claims) -> str:
    """Relationship Marker: (R1:INFERENCE:C1,C2)"""
    ...
```

Add dataclasses:
- `SourceRecord`: `shi`, `source_type`, `uri`, `location`, `chunk_id`, `verification_status`
- `VeracityRecord`: `relation_id`, `relation_type`, `dependent_claims`, `synthesis_prose`, `audit_status`, `timestamp`

- [ ] **Step 2: Extend AuditTrail**

Add fields: `sources: list[SourceRecord]`, `veracity: list[VeracityRecord]`

Add methods:
- `add_source(**kwargs) -> SourceRecord`
- `add_veracity(**kwargs) -> VeracityRecord`
- `verify_logic()` — check if all dependent claims are verified (not HYPOTHESIZED)

Extend `save()` to also write `sources.yaml` and `veracity.yaml`.
Extend `load()` to read them back.
Extend `to_markdown()` with SSR table and VAR table.

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_audit_trail.py -v
```

Commit: `git commit -m "feat: add IGM/SSR/VAR audit protocol to audit trail"`

---

## Task 5: New causal_discovery.py Module

**Files:**
- Create: `src/templates/scripts/causal_discovery.py`
- Create: `tests/test_causal_discovery.py`

Lightweight DAG structure learning using causal-learn's PC algorithm.

- [ ] **Step 1: Write tests**

Create `tests/test_causal_discovery.py`:

```python
"""Tests for causal_discovery.py."""
import numpy as np
import pandas as pd
from src.templates.scripts.causal_discovery import (
    discover_dag, discovery_to_causal_dag, evaluate_discovery, DiscoveryResult,
)


def _make_synthetic_data(n=500, seed=42):
    """Generate data with known causal structure: X→Y→Z, W→Y."""
    rng = np.random.RandomState(seed)
    X = rng.normal(0, 1, n)
    W = rng.normal(0, 1, n)
    Y = 0.8 * X + 0.5 * W + rng.normal(0, 0.5, n)
    Z = 0.6 * Y + rng.normal(0, 0.5, n)
    return pd.DataFrame({"X": X, "W": W, "Y": Y, "Z": Z})


def test_discover_dag_returns_result():
    result = discover_dag(_make_synthetic_data(), alpha=0.05)
    assert isinstance(result, DiscoveryResult)
    assert len(result.variable_names) == 4
    assert result.adjacency_matrix.shape == (4, 4)
    assert len(result.edges) > 0


def test_discover_dag_finds_some_edges():
    result = discover_dag(_make_synthetic_data(), alpha=0.05)
    assert len(result.edges) >= 2


def test_discovery_to_causal_dag():
    result = discover_dag(_make_synthetic_data(), alpha=0.05)
    dag = discovery_to_causal_dag(result)
    assert len(dag.edges) == len(result.edges)
    for edge in dag.edges:
        assert edge.label == "HYPOTHESIZED"
        assert edge.truth == 0.15


def test_evaluate_discovery_perfect():
    gt = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    metrics = evaluate_discovery(gt, gt)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_evaluate_discovery_partial():
    gt = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    discovered = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
    metrics = evaluate_discovery(discovered, gt)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5


def test_evaluate_discovery_empty():
    gt = np.array([[0, 1], [0, 0]])
    discovered = np.zeros((2, 2))
    metrics = evaluate_discovery(discovered, gt)
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0


def test_serialization():
    result = discover_dag(_make_synthetic_data(), alpha=0.05)
    d = result.to_dict()
    assert d["method"] in ("PC", "correlation_fallback")
    assert isinstance(d["adjacency_matrix"], list)
```

- [ ] **Step 2: Implement causal_discovery.py**

Create `src/templates/scripts/causal_discovery.py` with:

**Data structure — `DiscoveryResult`:**
- Fields: `adjacency_matrix` (ndarray), `variable_names`, `edges` (list of directed tuples), `skeleton` (list of undirected tuples), `method`, `alpha`
- Method: `to_dict()`

**Functions:**
- `discover_dag(data, alpha=0.05, method="pc") -> DiscoveryResult`
  - Tries causal-learn PC algorithm, falls back to correlation thresholding
  - PC: uses `fisherz` independence test, parses `result.G.graph` adjacency matrix
  - Fallback: pairwise Pearson correlation with significance test, heuristic directionality (lower variance → more likely cause)

- `_discover_pc(data, variable_names, alpha) -> DiscoveryResult` — PC algorithm via causal-learn

- `_discover_correlation_fallback(data, variable_names, alpha) -> DiscoveryResult` — fallback when causal-learn unavailable

- `discovery_to_causal_dag(result) -> CausalDAG` — convert to OpenPE DAG format (all edges start as HYPOTHESIZED, truth=0.15)

- `evaluate_discovery(discovered, ground_truth) -> dict` — edge-level precision, recall, F1 (adapted from Causica evaluation_metrics.py)

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_discovery.py -v
```

Commit: `git commit -m "feat: implement causal structure discovery with PC algorithm"`

---

## Task 6: Update pixi.toml

**Files:**
- Modify: `src/templates/pixi.toml`

- [ ] **Step 1: Add causal-learn dependency**

```toml
# --- Causal inference ---
dowhy = ">=0.11"
causal-learn = ">=0.1"   # PC algorithm for causal structure discovery
```

Commit: `git commit -m "deps: add causal-learn for structure discovery"`

---

## Task 7: Integration Test

**Files:**
- Create: `tests/test_sprint6_integration.py`

- [ ] **Step 1: Write integration test**

Full lifecycle: data → discover DAG → EP → memory with hotness → audit with IGM/SSR/VAR → temporal graph.

```python
"""Sprint 6 integration: full lifecycle with reference project enhancements."""
from pathlib import Path
import numpy as np
import pandas as pd
from src.templates.scripts.causal_discovery import discover_dag, discovery_to_causal_dag
from src.templates.scripts.ep_engine import EPNode, EPChain, classify_truth
from src.templates.scripts.memory_store import MemoryStore, MemoryEntry, hotness_score
from src.templates.scripts.causal_knowledge_graph import CausalKnowledgeGraph
from src.templates.scripts.audit_trail import (
    AuditTrail, SourceRecord, VeracityRecord,
    compute_shi, construct_igm, construct_rm,
)


def test_full_lifecycle(tmp_path):
    """Data → discover DAG → EP → memory → audit with IGM/SSR/VAR."""
    # 1. Generate synthetic data with known structure: X→Y→Z
    rng = np.random.RandomState(42)
    n = 300
    X = rng.normal(0, 1, n)
    Y = 0.7 * X + rng.normal(0, 0.5, n)
    Z = 0.5 * Y + rng.normal(0, 0.5, n)
    data = pd.DataFrame({"X": X, "Y": Y, "Z": Z})

    # 2. Discover causal structure
    result = discover_dag(data, alpha=0.05)
    assert len(result.edges) >= 1
    dag = discovery_to_causal_dag(result)

    # 3. Build EP chain
    chain = EPChain()
    for edge in dag.edges:
        chain.add_node(EPNode(event_id=f"{edge.source}→{edge.target}",
                              truth=classify_truth("HYPOTHESIZED"),
                              relevance=edge.relevance, evidence_type="HYPOTHESIZED"))
    assert chain.joint_ep > 0

    # 4. Commit to causal knowledge graph (temporal fields)
    graph = CausalKnowledgeGraph(tmp_path / "graph.json")
    for edge in dag.edges:
        graph.add_relationship(source=edge.source, target=edge.target,
                               relationship_type="HYPOTHESIZED", confidence=0.3,
                               analysis_id="s6_test")
    graph.save()
    for rel in graph.relationships.values():
        assert rel.is_valid
    # Test invalidation
    first = list(graph.relationships.values())[0]
    graph.invalidate_edge(first.source, first.target, "s6_v2")
    assert not first.is_valid
    assert len(graph.query(only_valid=True)) < len(graph.query(only_valid=False))

    # 5. Memory with hotness tracking
    store = MemoryStore(tmp_path / "memory")
    store.add(MemoryEntry(memory_id="s6_m1", content="Discovery found relationship",
                          domain="test", memory_type="domain", tier="L1"))
    store.load_for_analysis("test")
    assert store.get("s6_m1").active_count >= 1
    assert 0.0 < hotness_score(5, store.get("s6_m1").updated) <= 1.0

    # 6. Audit with ACG Protocol
    trail = AuditTrail(analysis_name="Sprint 6 Test")
    shi = compute_shi("test data")
    igm = construct_igm("C1", shi, "data.csv:col_X")
    assert igm.startswith("[C1:")
    trail.add_claim(claim_id="C1", text=f"X causes Y {igm}",
                    source_type="analysis", source_ref="test.py",
                    evidence_type="HYPOTHESIZED", confidence=0.3, phase="phase3")
    trail.add_claim(claim_id="C2", text="Y causes Z",
                    source_type="analysis", source_ref="test.py",
                    evidence_type="DATA_SUPPORTED", confidence=0.7, phase="phase3")
    trail.add_source(shi=shi, source_type="computation", uri="data.csv",
                     verification_status="VERIFIED")
    rm = construct_rm("R1", "CAUSAL_CLAIM", ["C1", "C2"])
    assert rm == "(R1:CAUSAL_CLAIM:C1,C2)"
    trail.add_veracity(relation_id="R1", relation_type="CAUSAL_CLAIM",
                       dependent_claims=["C1", "C2"])
    trail.verify_logic()
    assert trail.veracity[0].audit_status == "INSUFFICIENT_PREMISE"
    trail.save(tmp_path / "audit")
    loaded = AuditTrail.load(tmp_path / "audit")
    assert len(loaded.sources) == 1
    assert "Source Registry" in loaded.to_markdown()


def test_memory_deduplication(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    store.add(MemoryEntry(memory_id="d1", content="Bootstrap confidence intervals small samples",
                          domain="stats", memory_type="method", tier="L1"))
    store.add(MemoryEntry(memory_id="d2", content="Small samples bootstrap methods confidence intervals",
                          domain="stats", memory_type="method", tier="L1"))
    similar = store.find_similar("bootstrap confidence intervals small samples")
    assert len(similar) >= 2


def test_memory_archival(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    store.add(MemoryEntry(memory_id="cold", content="Old", domain="test",
                          memory_type="domain", tier="L2", active_count=0,
                          updated="2020-01-01T00:00:00"))
    archived = store.archive(threshold=0.5)
    assert "cold" in archived
    assert (tmp_path / "memory" / "L2" / "_archive" / "cold.yaml").exists()


def test_graph_prune_stale(tmp_path):
    graph = CausalKnowledgeGraph(tmp_path / "graph.json")
    graph.add_relationship("A", "B", "HYPOTHESIZED", 0.3, 0.3, "old")
    graph.relationships["A→B"].updated = "2020-01-01T00:00:00"
    expired = graph.prune_stale(max_age_days=30)
    assert "A→B" in expired
```

- [ ] **Step 2: Run all Sprint 6 tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_discovery.py tests/test_sprint6_integration.py -v
```

Commit: `git commit -m "test: add Sprint 6 integration tests"`

---

## Verification

```bash
# Sprint 6 tests
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_discovery.py tests/test_sprint6_integration.py -v

# Verify DoWhy test skips cleanly
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_pipeline.py -v

# Full regression (all sprints)
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

Expected: 104 passed, 1 skipped (DoWhy test), 0 failures.

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Fix DoWhy CI extraction | `causal_pipeline.py`, `test_causal_pipeline.py` | 5 min |
| 2 | Memory hotness + archival | `memory_store.py` | 15 min |
| 3 | Temporal graph validity | `causal_knowledge_graph.py` | 15 min |
| 4 | ACG audit protocol (IGM/SSR/VAR) | `audit_trail.py` | 15 min |
| 5 | Causal discovery module | `causal_discovery.py` + `test_causal_discovery.py` | 20 min |
| 6 | Update pixi.toml | `pixi.toml` | 2 min |
| 7 | Integration test | `test_sprint6_integration.py` | 15 min |
| **Total** | | **10 files modified/created** | **~87 min** |
