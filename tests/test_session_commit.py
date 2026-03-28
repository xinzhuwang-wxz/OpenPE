"""Unit tests for session_commit.py."""
import shutil
from pathlib import Path
from src.templates.scripts.memory_store import MemoryStore
from src.templates.scripts.causal_knowledge_graph import CausalKnowledgeGraph
from src.templates.scripts.session_commit import (
    extract_experiences, commit_session, grow_domain_pack, promote_to_global,
)

TMP = Path("/tmp/test_session_commit")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def _mock_analysis(analysis_dir: Path) -> None:
    """Create a mock completed analysis."""
    config = analysis_dir / "analysis_config.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("domain: economics\nquestion: Why is GDP declining?\n")

    artifacts = {
        "phase0_discovery/exec/DISCOVERY.md": "## Discovery\nData sources: World Bank API, FRED",
        "phase0_discovery/exec/DATA_QUALITY.md": "## Data Quality\nGDP dataset: HIGH quality\nEmployment data: LOW quality — missing years",
        "phase1_strategy/exec/STRATEGY.md": "## Strategy\nUsing diff_in_diff and propensity_score methods",
        "phase3_analysis/exec/ANALYSIS.md": (
            "## Analysis\n"
            "interest_rate → GDP_growth: DATA_SUPPORTED\n"
            "unemployment → inflation: CORRELATION\n"
        ),
        "phase5_verification/exec/VERIFICATION.md": "## Verification\nAll checks passed. No FAIL detected.",
    }
    for path, content in artifacts.items():
        full = analysis_dir / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)


def test_extract_experiences():
    analysis_dir = TMP / "analysis"
    _mock_analysis(analysis_dir)
    experiences = extract_experiences(analysis_dir)

    types = {e.experience_type for e in experiences}
    assert "data_source" in types
    assert "failure" in types  # LOW quality data
    assert "method" in types  # diff_in_diff
    assert "domain" in types  # DATA_SUPPORTED findings
    assert all(e.domain == "economics" for e in experiences)


def test_commit_session():
    analysis_dir = TMP / "analysis"
    _mock_analysis(analysis_dir)

    store = MemoryStore(TMP / "memory")
    graph = CausalKnowledgeGraph(TMP / "memory" / "graph.json")

    entries = commit_session(analysis_dir, store, graph, analysis_id="test_001")

    assert len(entries) > 0
    assert all(e.source_analysis == "test_001" for e in entries)

    # Verify causal graph was populated
    rels = graph.query(source="interest_rate")
    assert len(rels) == 1
    assert rels[0].target == "GDP_growth"
    assert rels[0].relationship_type == "CAUSES"


def test_grow_domain_pack():
    store = MemoryStore(TMP / "memory")
    # Populate with some L1 memories
    from src.templates.scripts.memory_store import MemoryEntry
    store.add(MemoryEntry(
        memory_id="m1", content="Bootstrap CI works well",
        domain="economics", memory_type="method", tier="L1", confidence=0.7,
    ))
    store.add(MemoryEntry(
        memory_id="m2", content="FRED is reliable for US macro",
        domain="economics", memory_type="data_source", tier="L1", confidence=0.8,
    ))

    pack_path = grow_domain_pack(store, "economics", TMP / "packs")
    assert pack_path.exists()

    import yaml
    with open(pack_path) as f:
        pack = yaml.safe_load(f)
    assert pack["domain"] == "economics"
    assert "method" in pack["experiences"]
    assert "data_source" in pack["experiences"]


def test_promote_to_global():
    """High-confidence findings should be promoted to global memory."""
    analysis_dir = TMP / "analysis"
    _mock_analysis(analysis_dir)

    # Create local memory with entries at varying confidence
    store = MemoryStore(analysis_dir / "memory")
    from src.templates.scripts.memory_store import MemoryEntry
    store.add(MemoryEntry(
        memory_id="high_conf", content="Reliable finding",
        domain="economics", memory_type="domain", tier="L1", confidence=0.8,
    ))
    store.add(MemoryEntry(
        memory_id="low_conf", content="Weak finding",
        domain="economics", memory_type="domain", tier="L1", confidence=0.3,
    ))

    # Create local causal graph with a high-confidence edge
    graph = CausalKnowledgeGraph(analysis_dir / "memory" / "causal_graph" / "graph.json")
    graph.add_relationship("A", "B", "CAUSES", confidence=0.75, analysis_id="test")
    graph.add_relationship("C", "D", "HYPOTHESIZED", confidence=0.2, analysis_id="test")
    graph.save()

    # Promote to global
    global_mem = TMP / "global_memory"
    stats = promote_to_global(analysis_dir, global_mem, min_confidence=0.6)

    assert stats["memories_promoted"] >= 1
    assert stats["graph_edges_promoted"] >= 1

    # Verify high_conf was promoted but low_conf was not
    promoted = global_mem / "L1" / "high_conf.yaml"
    not_promoted = global_mem / "L1" / "low_conf.yaml"
    assert promoted.exists()
    assert not not_promoted.exists()

    # Verify global graph has A→B but not C→D
    global_graph = CausalKnowledgeGraph(global_mem / "causal_graph" / "graph.json")
    global_graph.load()
    assert "A→B" in global_graph.relationships
    assert "C→D" not in global_graph.relationships
