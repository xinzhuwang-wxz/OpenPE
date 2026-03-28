# OpenPE Sprint 5: Memory System + Self-Evolution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the cross-analysis memory system that enables OpenPE to learn from experience — L0/L1/L2 tiered memory with confidence decay, session commit for experience extraction, causal knowledge graph for relationship tracking, and domain pack auto-growth.

**Architecture:** Python modules in `src/templates/scripts/` that persist to YAML/JSON on the filesystem. The memory store uses a tiered directory layout (L0/L1/L2). The causal knowledge graph stores as a single `graph.json`. Session commit extracts experiences from completed analysis artifacts and populates both stores.

**Tech Stack:** Python 3.11+, pyyaml (memory serialization), json (graph storage), pathlib (file I/O)

**Spec:** `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` — Sections 4.1-4.3 (Memory System), 4.4 (Causal Knowledge Graph), 4.5 (Session Commit)

---

## File Map

### Files to Create
- `src/templates/scripts/memory_store.py` — L0/L1/L2 tiered memory with confidence evolution
- `src/templates/scripts/causal_knowledge_graph.py` — Persistent causal relationship graph
- `src/templates/scripts/session_commit.py` — Post-analysis experience extraction
- `tests/test_memory_store.py` — Memory store unit tests
- `tests/test_causal_knowledge_graph.py` — Knowledge graph unit tests
- `tests/test_session_commit.py` — Session commit unit tests
- `tests/test_sprint5_integration.py` — End-to-end integration test

---

## Task 1: Memory Store (L0/L1/L2)

**Files:**
- Create: `src/templates/scripts/memory_store.py`
- Create: `tests/test_memory_store.py`

Core memory store with tiered loading and confidence evolution.

- [ ] **Step 1: Write tests**

Create `tests/test_memory_store.py`:

```python
"""Tests for the cross-analysis memory store."""
import pytest
from pathlib import Path
from src.templates.scripts.memory_store import MemoryEntry, MemoryStore


def test_entry_creation():
    entry = MemoryEntry(memory_id="test1", content="X works well",
                        domain="economics", memory_type="method", tier="L1")
    assert entry.confidence == 0.5
    assert entry.created != ""


def test_corroborate():
    entry = MemoryEntry(memory_id="t1", content="A", domain="d", memory_type="domain", tier="L1")
    entry.corroborate("analysis_1")
    assert entry.confidence == pytest.approx(0.65)  # 0.5 + 0.15
    assert "analysis_1" in entry.corroborated_by


def test_contradict():
    entry = MemoryEntry(memory_id="t1", content="A", domain="d", memory_type="domain", tier="L1")
    entry.contradict("analysis_2")
    assert entry.confidence == pytest.approx(0.25)  # 0.5 - 0.25
    assert "analysis_2" in entry.contradicted_by


def test_decay():
    entry = MemoryEntry(memory_id="t1", content="A", domain="d", memory_type="domain", tier="L1")
    entry.decay()
    assert entry.confidence == pytest.approx(0.49)  # 0.5 - 0.01


def test_quarantine_and_warning():
    low = MemoryEntry(memory_id="q", content="Q", domain="d", memory_type="domain",
                      tier="L1", confidence=0.05)
    assert low.is_quarantined
    assert "[QUARANTINED]" in low.loading_prefix

    warn = MemoryEntry(memory_id="w", content="W", domain="d", memory_type="domain",
                       tier="L1", confidence=0.15)
    assert warn.needs_warning
    assert "WARNING" in warn.loading_prefix


def test_store_add_and_load(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    store.add(MemoryEntry(memory_id="e1", content="Test",
                          domain="econ", memory_type="domain", tier="L1"))
    store2 = MemoryStore(tmp_path / "memory")
    store2.load_all()
    assert "e1" in store2.entries


def test_load_for_analysis(tmp_path):
    store = MemoryStore(tmp_path / "memory")
    store.add(MemoryEntry(memory_id="l0", content="Universal",
                          domain="any", memory_type="principle", tier="L0"))
    store.add(MemoryEntry(memory_id="l1_econ", content="Econ insight",
                          domain="economics", memory_type="domain", tier="L1"))
    store.add(MemoryEntry(memory_id="l1_phys", content="Physics insight",
                          domain="physics", memory_type="domain", tier="L1"))
    entries = store.load_for_analysis("economics")
    ids = {e.memory_id for e in entries}
    assert "l0" in ids
    assert "l1_econ" in ids
    assert "l1_phys" not in ids


def test_serialization_roundtrip():
    entry = MemoryEntry(memory_id="rt", content="Roundtrip test",
                        domain="test", memory_type="method", tier="L1",
                        confidence=0.75)
    d = entry.to_dict()
    restored = MemoryEntry.from_dict(d)
    assert restored.memory_id == "rt"
    assert restored.confidence == 0.75


def test_context_string():
    store = MemoryStore(Path("/tmp/mem_ctx_test"))
    e1 = MemoryEntry(memory_id="c1", content="Insight A",
                     domain="d", memory_type="domain", tier="L1", confidence=0.8)
    ctx = store.to_context_string([e1])
    assert "Insight A" in ctx
    assert "conf=0.80" in ctx
```

- [ ] **Step 2: Implement memory_store.py**

Create `src/templates/scripts/memory_store.py` with:

**Constants:**
- `CORROBORATION_BOOST = 0.15`, `CONTRADICTION_PENALTY = 0.25`, `DECAY_PER_ANALYSIS = 0.01`
- `CONFIDENCE_CAP = 0.95`, `CONFIDENCE_FLOOR = 0.05`
- `NORMAL_THRESHOLD = 0.2`, `WARNING_THRESHOLD = 0.1`

**Data structure — `MemoryEntry`:**
- Fields: `memory_id`, `content`, `domain`, `memory_type` (Literal["domain", "method", "data_source", "failure", "principle"]), `tier` (Literal["L0", "L1", "L2"]), `confidence`, `source_analysis`, `corroborated_by` (list), `contradicted_by` (list), `decay_rate`, `active_count`, `created`, `updated`
- Methods: `corroborate(analysis_id)` (+0.15 capped at 0.95), `contradict(analysis_id)` (-0.25 floored at 0.05), `decay()` (-0.01)
- Properties: `is_quarantined` (conf < 0.1), `needs_warning` (0.1 ≤ conf < 0.2), `loading_prefix`, `hotness`
- Serialization: `to_dict()`, `from_dict()` (classmethod)

**Class — `MemoryStore`:**
- Directory layout: `memory_root/{L0,L1,L2}/*.yaml`
- Methods: `add(entry)`, `get(id)`, `load_all()`, `load_for_analysis(domain)` (L0 + matching L1, increments `active_count`), `load_l2(id)`, `apply_decay()`, `corroborate(id, analysis_id)`, `contradict(id, analysis_id)`, `archive(threshold)`, `find_similar(content, candidates, threshold)`, `to_context_string(entries)`

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py -v
```

Commit: `git commit -m "feat: implement L0/L1/L2 tiered memory store"`

---

## Task 2: Causal Knowledge Graph

**Files:**
- Create: `src/templates/scripts/causal_knowledge_graph.py`
- Create: `tests/test_causal_knowledge_graph.py`

Persistent graph of established causal relationships across analyses.

- [ ] **Step 1: Write tests**

Create `tests/test_causal_knowledge_graph.py`:

```python
"""Tests for the causal knowledge graph."""
import pytest
from pathlib import Path
from src.templates.scripts.causal_knowledge_graph import CausalRelationship, CausalKnowledgeGraph


def test_relationship_creation():
    rel = CausalRelationship(source="A", target="B", relationship_type="CAUSES",
                             strength=0.7, confidence=0.8)
    assert rel.edge_id == "A→B"
    assert rel.reuse_policy == "SKIP"  # conf ≥ 0.8


def test_reuse_policies():
    assert CausalRelationship(source="A", target="B", relationship_type="CAUSES",
                              confidence=0.85).reuse_policy == "SKIP"
    assert CausalRelationship(source="A", target="B", relationship_type="CAUSES",
                              confidence=0.6).reuse_policy == "LIGHTWEIGHT_VERIFY"
    assert CausalRelationship(source="A", target="B", relationship_type="CAUSES",
                              confidence=0.3).reuse_policy == "MUST_RETEST"


def test_corroborate_and_contradict():
    rel = CausalRelationship(source="A", target="B", relationship_type="CAUSES", confidence=0.5)
    rel.corroborate("a1")
    assert rel.confidence == pytest.approx(0.6)
    rel.contradict("a2")
    assert rel.confidence == pytest.approx(0.4)


def test_graph_save_load(tmp_path):
    graph = CausalKnowledgeGraph(tmp_path / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.7, "test")
    graph.save()
    graph2 = CausalKnowledgeGraph(tmp_path / "graph.json")
    graph2.load()
    assert "X→Y" in graph2.relationships


def test_add_existing_corroborates():
    graph = CausalKnowledgeGraph(Path("/tmp/test_ckg.json"))
    graph.add_relationship("X", "Y", "HYPOTHESIZED", 0.5, 0.3, "a1")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.5, "a2")
    rel = graph.relationships["X→Y"]
    assert "a2" in rel.corroborated_by
    assert rel.relationship_type == "CAUSES"  # upgraded


def test_query():
    graph = CausalKnowledgeGraph(Path("/tmp/test_ckg_q.json"))
    graph.add_relationship("A", "B", "CAUSES", 0.8, 0.7, "t1")
    graph.add_relationship("A", "C", "CORRELATED_WITH", 0.3, 0.3, "t1")
    results = graph.query(source="A", min_confidence=0.5)
    assert len(results) == 1
    assert results[0].target == "B"


def test_detect_contradictions():
    graph = CausalKnowledgeGraph(Path("/tmp/test_ckg_c.json"))
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.7, "a1")
    contradiction = graph.detect_contradictions("X", "Y", "CORRELATED_WITH", "a2")
    assert contradiction is True
    assert graph.relationships["X→Y"].confidence < 0.7


def test_reuse_policy_lookup():
    graph = CausalKnowledgeGraph(Path("/tmp/test_ckg_r.json"))
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.85, "test")
    policy, rel = graph.get_reuse_policy("X", "Y")
    assert policy == "SKIP"
    policy2, _ = graph.get_reuse_policy("A", "B")
    assert policy2 == "MUST_RETEST"


def test_mermaid_output():
    graph = CausalKnowledgeGraph(Path("/tmp/test_ckg_m.json"))
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.7, "t1")
    mermaid = graph.to_mermaid()
    assert "graph TD" in mermaid
    assert "X" in mermaid
    assert "Y" in mermaid
```

- [ ] **Step 2: Implement causal_knowledge_graph.py**

Create `src/templates/scripts/causal_knowledge_graph.py` with:

**Constants:** `SKIP_RETEST_THRESHOLD = 0.8`, `LIGHTWEIGHT_VERIFY_THRESHOLD = 0.5`

**Data structure — `CausalRelationship`:**
- Fields: `source`, `target`, `relationship_type` ("CAUSES" | "CORRELATED_WITH" | "HYPOTHESIZED"), `strength`, `confidence`, `source_analyses`, `corroborated_by`, `contradicted_by`, temporal fields (`valid_at`, `invalid_at`, `expired_at`, `episodes`), `created`, `updated`
- Methods: `corroborate(id)` (+0.10), `contradict(id)` (-0.20), `invalidate(id)` (sets `invalid_at`)
- Properties: `edge_id` ("A→B"), `reuse_policy`, `is_valid`, `is_expired`
- Serialization: `to_dict()`, `from_dict()`

**Class — `CausalKnowledgeGraph`:**
- Storage: single `graph.json` file
- Methods: `load()`, `save()`, `add_relationship(...)` (adds or corroborates existing), `query(source, target, min_confidence, only_valid)`, `get_reuse_policy(source, target)`, `detect_contradictions(source, target, new_type, analysis_id)`, `invalidate_edge(source, target, analysis_id)`, `prune_stale(max_age_days)`, `to_mermaid(min_confidence, only_valid)`

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_knowledge_graph.py -v
```

Commit: `git commit -m "feat: implement persistent causal knowledge graph"`

---

## Task 3: Session Commit

**Files:**
- Create: `src/templates/scripts/session_commit.py`
- Create: `tests/test_session_commit.py`

Post-analysis experience extraction from phase artifacts.

- [ ] **Step 1: Write tests**

Create `tests/test_session_commit.py`:

```python
"""Tests for session commit and experience extraction."""
import pytest
from pathlib import Path
from src.templates.scripts.session_commit import extract_experiences, commit_session, grow_domain_pack
from src.templates.scripts.memory_store import MemoryStore
from src.templates.scripts.causal_knowledge_graph import CausalKnowledgeGraph


def _create_mock_analysis(tmp_path, domain="economics"):
    """Create mock analysis directory with artifacts."""
    (tmp_path / "analysis_config.yaml").write_text(f"domain: {domain}\n")
    disc = tmp_path / "phase0_discovery" / "exec"
    disc.mkdir(parents=True)
    (disc / "DISCOVERY.md").write_text("Data sources from World Bank API")
    strat = tmp_path / "phase1_strategy" / "exec"
    strat.mkdir(parents=True)
    (strat / "STRATEGY.md").write_text("Use propensity_score method for estimation.")
    analysis = tmp_path / "phase3_analysis" / "exec"
    analysis.mkdir(parents=True)
    (analysis / "ANALYSIS.md").write_text(
        "urbanization → birth_rate: DATA_SUPPORTED\n"
        "Found DATA_SUPPORTED causal link."
    )


def test_extract_experiences(tmp_path):
    _create_mock_analysis(tmp_path)
    exps = extract_experiences(tmp_path)
    assert len(exps) >= 2
    types = {e.experience_type for e in exps}
    assert "data_source" in types or "method" in types


def test_commit_session(tmp_path):
    _create_mock_analysis(tmp_path)
    store = MemoryStore(tmp_path / "memory")
    graph = CausalKnowledgeGraph(tmp_path / "memory" / "graph.json")
    entries = commit_session(tmp_path, store, graph, analysis_id="test_001")
    assert len(entries) >= 1
    assert (tmp_path / "memory" / "graph.json").exists()


def test_grow_domain_pack(tmp_path):
    _create_mock_analysis(tmp_path)
    store = MemoryStore(tmp_path / "memory")
    graph = CausalKnowledgeGraph(tmp_path / "memory" / "graph.json")
    commit_session(tmp_path, store, graph, analysis_id="test_002")
    pack_path = grow_domain_pack(store, "economics", tmp_path / "packs")
    assert pack_path.exists()
    import yaml
    with open(pack_path) as f:
        pack = yaml.safe_load(f)
    assert pack["domain"] == "economics"
```

- [ ] **Step 2: Implement session_commit.py**

Create `src/templates/scripts/session_commit.py` with:

**Data structure — `Experience`:**
- Fields: `experience_type` ("domain" | "method" | "data_source" | "failure"), `content`, `domain`, `source_phase`, `confidence`

**Functions:**
- `extract_experiences(analysis_dir) -> list[Experience]`
  - Read `analysis_config.yaml` for domain
  - Scan phase artifacts: DISCOVERY.md (data sources), DATA_QUALITY.md (quality issues), STRATEGY.md (method keywords like propensity_score, instrumental_variable), ANALYSIS.md (DATA_SUPPORTED findings), VERIFICATION.md (failures)
  - Each extractor uses simple keyword matching

- `commit_session(analysis_dir, memory_store, causal_graph, analysis_id) -> list[MemoryEntry]`
  - Apply decay to existing memories
  - Extract experiences
  - Create MemoryEntry for each (tier L0 for principles, L1 for everything else)
  - Parse causal findings from ANALYSIS.md using regex (`source → target: CLASSIFICATION`)
  - Check for contradictions, add to graph, save graph

- `grow_domain_pack(memory_store, domain, output_dir) -> Path`
  - Load L1 entries for domain
  - Group by memory_type
  - Write YAML domain pack file

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_session_commit.py -v
```

Commit: `git commit -m "feat: implement session commit and domain pack growth"`

---

## Task 4: Integration Test

**Files:**
- Create: `tests/test_sprint5_integration.py`

- [ ] **Step 1: Write integration test**

Full lifecycle: commit session → memories stored → contradiction detection → reuse policy → domain pack growth.

```python
"""Sprint 5 integration: memory lifecycle, contradiction detection, reuse policies."""
import pytest
from pathlib import Path
from src.templates.scripts.memory_store import MemoryStore, MemoryEntry
from src.templates.scripts.causal_knowledge_graph import CausalKnowledgeGraph
from src.templates.scripts.session_commit import commit_session, grow_domain_pack


def test_full_memory_lifecycle(tmp_path):
    """Commit analysis → create memories → load in subsequent analysis → verify."""
    # Create first analysis artifacts
    # ... commit session, create entries, verify loading ...


def test_contradiction_detection(tmp_path):
    """When new analysis contradicts existing edge, confidence drops."""
    graph = CausalKnowledgeGraph(tmp_path / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.7, "a1")
    graph.detect_contradictions("X", "Y", "CORRELATED_WITH", "a2")
    assert graph.relationships["X→Y"].confidence < 0.7


def test_reuse_policy_guides_analysis(tmp_path):
    """High-confidence relationships get SKIP policy."""
    graph = CausalKnowledgeGraph(tmp_path / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.85, "test")
    policy, rel = graph.get_reuse_policy("X", "Y")
    assert policy == "SKIP"
    # Unknown edges require full testing
    policy2, _ = graph.get_reuse_policy("A", "B")
    assert policy2 == "MUST_RETEST"
```

- [ ] **Step 2: Run all Sprint 5 tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py tests/test_causal_knowledge_graph.py tests/test_session_commit.py tests/test_sprint5_integration.py -v
```

Commit: `git commit -m "test: add Sprint 5 integration tests"`

---

## Verification

```bash
# Run all Sprint 5 tests
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py tests/test_causal_knowledge_graph.py tests/test_session_commit.py tests/test_sprint5_integration.py -v

# Full regression
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Memory Store (L0/L1/L2) | `memory_store.py` + `test_memory_store.py` | 25 min |
| 2 | Causal Knowledge Graph | `causal_knowledge_graph.py` + `test_causal_knowledge_graph.py` | 20 min |
| 3 | Session Commit | `session_commit.py` + `test_session_commit.py` | 20 min |
| 4 | Integration test | `test_sprint5_integration.py` | 10 min |
| **Total** | | **7 files** | **~75 min** |
