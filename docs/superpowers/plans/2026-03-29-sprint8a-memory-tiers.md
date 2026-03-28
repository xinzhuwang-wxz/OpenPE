# Sprint 8A: Memory Tier Transitions

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement memory tier transitions (L1→L0 promotion, L2 generation, tier demotion, true forgetting) so the memory system evolves across analyses instead of accumulating flat L1 entries.

**Architecture:** Add `promote_tier()`, `demote_tier()`, `forget()`, and `generate_l2_summary()` to `MemoryStore` and `session_commit.py`. Tier transitions are triggered during `commit_session()` based on corroboration count (promotion), contradiction-driven confidence drop (demotion), and staleness (forgetting). L2 entries are auto-generated as analysis summaries.

**Tech Stack:** Python 3.11+, PyYAML, pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/templates/scripts/memory_store.py` | Modify | Add `promote_tier()`, `demote_tier()`, `forget()` methods |
| `src/templates/scripts/session_commit.py` | Modify | Add L2 generation, trigger tier transitions in `commit_session()` |
| `tests/test_memory_store.py` | Modify | Add tier transition tests |
| `tests/test_session_commit.py` | Modify | Add L2 generation test |

---

### Task 1: Tier Promotion (L1 → L0)

**Files:**
- Modify: `src/templates/scripts/memory_store.py`
- Modify: `tests/test_memory_store.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_memory_store.py`:

```python
def test_promote_tier_l1_to_l0():
    """L1 entry corroborated by 3+ analyses should promote to L0."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="promotable",
        content="World Bank wbgapi works without API key",
        domain="economics",
        memory_type="data_source",
        tier="L1",
        confidence=0.8,
    )
    entry.corroborated_by = ["analysis_1", "analysis_2", "analysis_3"]
    store.add(entry)

    promoted = store.promote_tier("promotable")
    assert promoted is True
    assert store.entries["promotable"].tier == "L0"
    # File should be moved from L1/ to L0/
    assert (TMP / "memory" / "L0" / "promotable.yaml").exists()
    assert not (TMP / "memory" / "L1" / "promotable.yaml").exists()


def test_promote_tier_insufficient_corroboration():
    """L1 entry with < 3 corroborations should not promote."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="not_ready",
        content="Some finding",
        domain="test",
        memory_type="domain",
        tier="L1",
        confidence=0.6,
    )
    entry.corroborated_by = ["analysis_1"]
    store.add(entry)

    promoted = store.promote_tier("not_ready")
    assert promoted is False
    assert store.entries["not_ready"].tier == "L1"


def test_promote_tier_already_l0():
    """L0 entry cannot be promoted further."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="already_l0",
        content="Universal principle",
        domain="general",
        memory_type="principle",
        tier="L0",
        confidence=0.9,
    )
    store.add(entry)

    promoted = store.promote_tier("already_l0")
    assert promoted is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py::test_promote_tier_l1_to_l0 -v`
Expected: FAIL — `promote_tier` not found

- [ ] **Step 3: Implement promote_tier in memory_store.py**

Add to the `MemoryStore` class, after `archive()`:

```python
    # --- Tier transition thresholds ---
    PROMOTION_CORROBORATION_MIN = 3  # L1→L0 requires ≥3 independent corroborations
    DEMOTION_CONFIDENCE_MAX = 0.3    # L0→L1 if confidence drops below this

    def promote_tier(self, memory_id: str) -> bool:
        """Promote L1→L0 if corroboration threshold is met.

        Returns True if promoted, False if conditions not met or already L0.
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/memory_store.py tests/test_memory_store.py
git commit -m "feat(sprint8a): add L1→L0 tier promotion (≥3 corroborations)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Tier Demotion (L0 → L1) and True Forgetting

**Files:**
- Modify: `src/templates/scripts/memory_store.py`
- Modify: `tests/test_memory_store.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_memory_store.py`:

```python
def test_demote_tier_l0_to_l1():
    """L0 entry with confidence < 0.3 should demote to L1."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="demotable",
        content="Previously trusted principle",
        domain="general",
        memory_type="principle",
        tier="L0",
        confidence=0.25,
    )
    store.add(entry)

    demoted = store.demote_tier("demotable")
    assert demoted is True
    assert store.entries["demotable"].tier == "L1"
    assert (TMP / "memory" / "L1" / "demotable.yaml").exists()
    assert not (TMP / "memory" / "L0" / "demotable.yaml").exists()


def test_demote_tier_confidence_ok():
    """L0 entry with sufficient confidence should not demote."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="solid",
        content="Well-established principle",
        domain="general",
        memory_type="principle",
        tier="L0",
        confidence=0.7,
    )
    store.add(entry)

    demoted = store.demote_tier("solid")
    assert demoted is False
    assert store.entries["solid"].tier == "L0"


def test_forget_removes_entry():
    """Entries with conf < 0.05 AND hotness < 0.01 should be deleted."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="forgettable",
        content="Ancient irrelevant finding",
        domain="test",
        memory_type="domain",
        tier="L1",
        confidence=0.04,
        active_count=0,
        updated="2020-01-01T00:00:00",  # very old → hotness ≈ 0
    )
    store.add(entry)
    assert (TMP / "memory" / "L1" / "forgettable.yaml").exists()

    forgotten = store.forget()
    assert "forgettable" in forgotten
    assert "forgettable" not in store.entries
    assert not (TMP / "memory" / "L1" / "forgettable.yaml").exists()


def test_forget_keeps_recent():
    """Recent entries above thresholds should not be forgotten."""
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="keeper",
        content="Recent finding",
        domain="test",
        memory_type="domain",
        tier="L1",
        confidence=0.3,
    )
    store.add(entry)

    forgotten = store.forget()
    assert "keeper" not in forgotten
    assert "keeper" in store.entries
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py::test_demote_tier_l0_to_l1 -v`
Expected: FAIL

- [ ] **Step 3: Implement demote_tier and forget**

Add to `MemoryStore` class, after `promote_tier()`:

```python
    def demote_tier(self, memory_id: str) -> bool:
        """Demote L0→L1 if confidence drops below demotion threshold.

        Returns True if demoted, False if conditions not met or not L0.
        """
        entry = self.entries.get(memory_id)
        if entry is None or entry.tier != "L0":
            return False
        if entry.confidence >= self.DEMOTION_CONFIDENCE_MAX:
            return False

        old_path = self._entry_path(entry)
        entry.tier = "L1"
        entry.updated = datetime.now().isoformat()
        new_path = self._entry_path(entry)

        self._save_entry(entry)
        if old_path.exists() and old_path != new_path:
            old_path.unlink()

        return True

    FORGET_CONFIDENCE = 0.05
    FORGET_HOTNESS = 0.01

    def forget(self) -> list[str]:
        """Delete entries with confidence < 0.05 AND hotness < 0.01.

        True forgetting — removes the file entirely (not archived).
        Returns list of forgotten memory IDs.
        """
        self.load_all()
        forgotten = []
        for entry in list(self.entries.values()):
            if entry.confidence < self.FORGET_CONFIDENCE and entry.hotness < self.FORGET_HOTNESS:
                path = self._entry_path(entry)
                if path.exists():
                    path.unlink()
                del self.entries[entry.memory_id]
                forgotten.append(entry.memory_id)
        return forgotten
```

- [ ] **Step 4: Run tests**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/memory_store.py tests/test_memory_store.py
git commit -m "feat(sprint8a): add L0→L1 demotion + true forgetting

Demotion when conf < 0.3, forgetting when conf < 0.05 AND hotness < 0.01.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: L2 Generation and Tier Transitions in session_commit

**Files:**
- Modify: `src/templates/scripts/session_commit.py`
- Modify: `tests/test_session_commit.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_session_commit.py`:

```python
def test_commit_generates_l2_summary():
    """commit_session should create an L2 entry with analysis summary."""
    analysis_dir = TMP / "analysis"
    _mock_analysis(analysis_dir)

    store = MemoryStore(TMP / "memory")
    graph = CausalKnowledgeGraph(TMP / "memory" / "graph.json")

    entries = commit_session(analysis_dir, store, graph, analysis_id="l2_test")

    # Should have at least one L2 entry
    l2_entries = [e for e in entries if e.tier == "L2"]
    assert len(l2_entries) >= 1
    assert "economics" in l2_entries[0].content.lower() or "analysis" in l2_entries[0].content.lower()
    # L2 file should exist on disk
    assert (TMP / "memory" / "L2" / f"l2_test_summary_0.yaml").exists()


def test_commit_triggers_tier_transitions():
    """commit_session should promote well-corroborated L1 and forget stale entries."""
    analysis_dir = TMP / "analysis"
    _mock_analysis(analysis_dir)

    store = MemoryStore(TMP / "memory")
    graph = CausalKnowledgeGraph(TMP / "memory" / "graph.json")

    # Pre-populate: one highly corroborated L1 and one stale entry
    from src.templates.scripts.memory_store import MemoryEntry
    store.add(MemoryEntry(
        memory_id="well_corroborated",
        content="Reliable cross-analysis finding",
        domain="economics",
        memory_type="domain",
        tier="L1",
        confidence=0.85,
        corroborated_by=["a1", "a2", "a3"],
    ))
    store.add(MemoryEntry(
        memory_id="stale_entry",
        content="Very old forgotten entry",
        domain="economics",
        memory_type="domain",
        tier="L1",
        confidence=0.03,
        active_count=0,
        updated="2020-01-01T00:00:00",
    ))

    commit_session(analysis_dir, store, graph, analysis_id="tier_test")

    store.load_all()
    # Well-corroborated should be promoted to L0
    assert store.entries["well_corroborated"].tier == "L0"
    # Stale entry should be forgotten
    assert "stale_entry" not in store.entries
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_session_commit.py::test_commit_generates_l2_summary -v`
Expected: FAIL

- [ ] **Step 3: Add L2 generation and tier transitions to session_commit.py**

In `session_commit.py`, modify `commit_session()`. After the line that writes the commit marker (`commit_marker.write_text(...)`), add:

```python
    # Generate L2 analysis summary
    l2_entry = _generate_l2_summary(analysis_dir, analysis_id, domain="general")
    if l2_entry:
        memory_store.add(l2_entry)
        new_entries.append(l2_entry)

    # Tier transitions: promote well-corroborated L1→L0, forget stale
    memory_store.load_all()
    for mid in list(memory_store.entries.keys()):
        memory_store.promote_tier(mid)
        memory_store.demote_tier(mid)
    memory_store.forget()
```

Also add the helper function before `commit_session`:

```python
def _generate_l2_summary(
    analysis_dir: Path,
    analysis_id: str,
    domain: str = "general",
) -> MemoryEntry | None:
    """Generate an L2 summary entry from analysis artifacts."""
    analysis_dir = Path(analysis_dir)

    # Read analysis config for domain
    config_path = analysis_dir / "analysis_config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
        domain = config.get("domain", domain)
        question = config.get("question", "")
    else:
        question = ""

    # Build summary from available artifacts
    parts = []
    if question:
        parts.append(f"Question: {question}")

    for artifact_name in ["DISCOVERY.md", "ANALYSIS.md", "VERIFICATION.md"]:
        path = _find_artifact(analysis_dir, artifact_name)
        if path:
            text = path.read_text()
            # Extract first non-empty, non-heading line as summary
            for line in text.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("|") and not line.startswith("-"):
                    parts.append(f"{artifact_name}: {line[:120]}")
                    break

    if not parts:
        return None

    return MemoryEntry(
        memory_id=f"{analysis_id}_summary_0",
        content=" | ".join(parts),
        domain=domain,
        memory_type="domain",
        tier="L2",
        confidence=0.5,
        source_analysis=analysis_id,
    )
```

- [ ] **Step 4: Read `session_commit.py` to find exact domain variable location**

The `commit_session` function needs access to the analysis domain for L2 generation. Read the function to find where to get it from.

- [ ] **Step 5: Run tests**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_session_commit.py -v`
Expected: all pass

- [ ] **Step 6: Run full suite**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v --tb=short`
Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add src/templates/scripts/session_commit.py tests/test_session_commit.py
git commit -m "feat(sprint8a): L2 generation + tier transitions in commit_session

commit_session now: generates L2 analysis summary, promotes
well-corroborated L1→L0, demotes contradicted L0→L1, forgets stale entries.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Verification

```bash
cd /Users/bamboo/Githubs/OpenPE
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py tests/test_session_commit.py -v
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v --tb=short
```
