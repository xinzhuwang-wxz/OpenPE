"""Unit tests for memory_store.py."""
import shutil
from pathlib import Path
from src.templates.scripts.memory_store import MemoryEntry, MemoryStore

TMP = Path("/tmp/test_memory_store")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_entry_creation():
    entry = MemoryEntry(
        memory_id="test_001",
        content="Bootstrap works better than asymptotic CI for small samples",
        domain="economics",
        memory_type="method",
        tier="L1",
    )
    assert entry.confidence == 0.5
    assert not entry.is_quarantined
    assert not entry.needs_warning
    assert entry.loading_prefix == ""


def test_corroborate():
    entry = MemoryEntry(memory_id="e1", content="x", domain="d", memory_type="domain", tier="L1")
    entry.corroborate("analysis_002")
    assert entry.confidence == 0.65
    assert "analysis_002" in entry.corroborated_by
    # Cap at 0.95
    for i in range(10):
        entry.corroborate(f"a_{i}")
    assert entry.confidence <= 0.95


def test_contradict():
    entry = MemoryEntry(memory_id="e1", content="x", domain="d", memory_type="domain", tier="L1")
    entry.contradict("analysis_003")
    assert entry.confidence == 0.25
    entry.contradict("analysis_004")
    assert entry.confidence == 0.05  # floor


def test_decay():
    entry = MemoryEntry(memory_id="e1", content="x", domain="d", memory_type="domain", tier="L1", confidence=0.2)
    entry.decay()
    assert entry.confidence == 0.19


def test_quarantine_and_warning():
    quarantined = MemoryEntry(memory_id="q", content="x", domain="d", memory_type="domain", tier="L1", confidence=0.05)
    assert quarantined.is_quarantined
    assert "[QUARANTINED]" in quarantined.loading_prefix

    warning = MemoryEntry(memory_id="w", content="x", domain="d", memory_type="domain", tier="L1", confidence=0.15)
    assert warning.needs_warning
    assert "[WARNING" in warning.loading_prefix


def test_store_add_and_load():
    store = MemoryStore(TMP / "mem")
    entry = MemoryEntry(memory_id="m1", content="test", domain="econ", memory_type="domain", tier="L1")
    store.add(entry)

    # Reload from disk
    store2 = MemoryStore(TMP / "mem")
    store2.load_all()
    assert "m1" in store2.entries
    assert store2.entries["m1"].content == "test"


def test_load_for_analysis():
    store = MemoryStore(TMP / "mem")
    store.add(MemoryEntry(memory_id="l0_1", content="always", domain="general", memory_type="principle", tier="L0"))
    store.add(MemoryEntry(memory_id="l1_econ", content="econ insight", domain="economics", memory_type="domain", tier="L1"))
    store.add(MemoryEntry(memory_id="l1_health", content="health insight", domain="health", memory_type="domain", tier="L1"))
    store.add(MemoryEntry(memory_id="l2_detail", content="detail", domain="economics", memory_type="domain", tier="L2"))

    loaded = store.load_for_analysis("economics")
    ids = {e.memory_id for e in loaded}
    assert "l0_1" in ids  # L0 always loaded
    assert "l1_econ" in ids  # matching domain
    assert "l1_health" not in ids  # wrong domain
    assert "l2_detail" not in ids  # L2 not auto-loaded


def test_serialization_roundtrip():
    entry = MemoryEntry(
        memory_id="rt1", content="test", domain="d", memory_type="method", tier="L1",
        confidence=0.75, source_analysis="a1",
        corroborated_by=["a2"], contradicted_by=["a3"],
    )
    d = entry.to_dict()
    restored = MemoryEntry.from_dict(d)
    assert restored.memory_id == "rt1"
    assert restored.confidence == 0.75
    assert restored.corroborated_by == ["a2"]


def test_context_string():
    store = MemoryStore(TMP / "mem")
    store.add(MemoryEntry(memory_id="c1", content="Always verify data", domain="general", memory_type="principle", tier="L0", confidence=0.9))
    store.add(MemoryEntry(memory_id="c2", content="Weak finding", domain="general", memory_type="domain", tier="L0", confidence=0.15))

    ctx = store.to_context_string(list(store.entries.values()))
    assert "Always verify data" in ctx
    assert "[WARNING" in ctx


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
    assert (TMP / "memory" / "L0" / "promotable.yaml").exists()
    assert not (TMP / "memory" / "L1" / "promotable.yaml").exists()


def test_promote_tier_insufficient_corroboration():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="not_ready", content="Some finding",
        domain="test", memory_type="domain", tier="L1", confidence=0.6,
    )
    entry.corroborated_by = ["analysis_1"]
    store.add(entry)
    assert store.promote_tier("not_ready") is False
    assert store.entries["not_ready"].tier == "L1"


def test_promote_tier_already_l0():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="already_l0", content="Universal principle",
        domain="general", memory_type="principle", tier="L0", confidence=0.9,
    )
    store.add(entry)
    assert store.promote_tier("already_l0") is False


def test_demote_tier_l0_to_l1():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="demotable", content="Previously trusted principle",
        domain="general", memory_type="principle", tier="L0", confidence=0.25,
    )
    store.add(entry)
    assert store.demote_tier("demotable") is True
    assert store.entries["demotable"].tier == "L1"
    assert (TMP / "memory" / "L1" / "demotable.yaml").exists()
    assert not (TMP / "memory" / "L0" / "demotable.yaml").exists()


def test_demote_tier_confidence_ok():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="solid", content="Well-established principle",
        domain="general", memory_type="principle", tier="L0", confidence=0.7,
    )
    store.add(entry)
    assert store.demote_tier("solid") is False
    assert store.entries["solid"].tier == "L0"


def test_forget_removes_entry():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="forgettable", content="Ancient irrelevant finding",
        domain="test", memory_type="domain", tier="L1",
        confidence=0.04, active_count=0, updated="2020-01-01T00:00:00",
    )
    store.add(entry)
    assert (TMP / "memory" / "L1" / "forgettable.yaml").exists()
    forgotten = store.forget()
    assert "forgettable" in forgotten
    assert "forgettable" not in store.entries
    assert not (TMP / "memory" / "L1" / "forgettable.yaml").exists()


def test_forget_keeps_recent():
    store = MemoryStore(TMP / "memory")
    entry = MemoryEntry(
        memory_id="keeper", content="Recent finding",
        domain="test", memory_type="domain", tier="L1", confidence=0.3,
    )
    store.add(entry)
    forgotten = store.forget()
    assert "keeper" not in forgotten
    assert "keeper" in store.entries
