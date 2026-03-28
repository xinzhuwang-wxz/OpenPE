"""Sprint 5 integration: full memory lifecycle across analyses."""
import shutil
from pathlib import Path
from src.templates.scripts.memory_store import MemoryEntry, MemoryStore
from src.templates.scripts.causal_knowledge_graph import CausalKnowledgeGraph
from src.templates.scripts.session_commit import commit_session, grow_domain_pack

TMP = Path("/tmp/test_s5_integration")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def _mock_analysis(analysis_dir: Path, domain: str, analysis_content: str) -> None:
    config = analysis_dir / "analysis_config.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(f"domain: {domain}\n")

    artifacts = {
        "phase0_discovery/exec/DISCOVERY.md": "## Discovery\nData sources: World Bank API",
        "phase0_discovery/exec/DATA_QUALITY.md": "## Data Quality\nOverall: MEDIUM",
        "phase1_strategy/exec/STRATEGY.md": "## Strategy\nUsing propensity_score method",
        "phase3_analysis/exec/ANALYSIS.md": analysis_content,
        "phase5_verification/exec/VERIFICATION.md": "## Verification\nAll checks passed.",
    }
    for path, content in artifacts.items():
        full = analysis_dir / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)


def test_full_memory_lifecycle():
    """Simulate two analyses: commit → store → load → corroborate → domain pack."""
    memory_root = TMP / "memory"
    store = MemoryStore(memory_root)
    graph = CausalKnowledgeGraph(memory_root / "graph.json")

    # --- Analysis 1: discover interest_rate → GDP_growth ---
    a1_dir = TMP / "analysis_001"
    _mock_analysis(a1_dir, "economics",
        "## Analysis\ninterest_rate → GDP_growth: DATA_SUPPORTED\n")

    entries1 = commit_session(a1_dir, store, graph, analysis_id="a001")
    assert len(entries1) > 0

    # Verify causal graph
    rels = graph.query(source="interest_rate")
    assert len(rels) == 1
    assert rels[0].relationship_type == "CAUSES"
    initial_confidence = rels[0].confidence

    # --- Analysis 2: corroborate same finding ---
    a2_dir = TMP / "analysis_002"
    _mock_analysis(a2_dir, "economics",
        "## Analysis\ninterest_rate → GDP_growth: DATA_SUPPORTED\n")

    entries2 = commit_session(a2_dir, store, graph, analysis_id="a002")

    # Causal relationship should be corroborated
    rels2 = graph.query(source="interest_rate")
    assert len(rels2) == 1
    assert rels2[0].confidence > initial_confidence

    # --- Load memories for new analysis ---
    new_store = MemoryStore(memory_root)
    loaded = new_store.load_for_analysis("economics")
    assert len(loaded) > 0
    # All loaded should be non-quarantined
    assert all(not e.is_quarantined for e in loaded)

    # --- Grow domain pack ---
    pack_path = grow_domain_pack(new_store, "economics", TMP / "domain_packs")
    assert pack_path.exists()
    assert pack_path.name == "economics.yaml"

    import yaml
    with open(pack_path) as f:
        pack = yaml.safe_load(f)
    assert pack["domain"] == "economics"
    assert pack["source_memories"] > 0


def test_contradiction_detection():
    """Analysis 1 finds CAUSES, analysis 2 finds only CORRELATION."""
    memory_root = TMP / "memory_contra"
    store = MemoryStore(memory_root)
    graph = CausalKnowledgeGraph(memory_root / "graph.json")

    # Analysis 1: X causes Y
    a1_dir = TMP / "contra_001"
    _mock_analysis(a1_dir, "economics", "## Analysis\nX → Y: DATA_SUPPORTED\n")
    commit_session(a1_dir, store, graph, analysis_id="c001")

    initial = graph.relationships["X→Y"].confidence

    # Analysis 2: X only correlates with Y
    a2_dir = TMP / "contra_002"
    _mock_analysis(a2_dir, "economics", "## Analysis\nX → Y: CORRELATION\n")
    commit_session(a2_dir, store, graph, analysis_id="c002")

    # Confidence should have decreased due to contradiction
    assert graph.relationships["X→Y"].confidence < initial


def test_reuse_policy_guides_analysis():
    """High-confidence relationships should suggest skipping re-test."""
    memory_root = TMP / "memory_reuse"
    graph = CausalKnowledgeGraph(memory_root / "graph.json")

    graph.add_relationship("A", "B", "CAUSES", 0.8, 0.85, "prior")
    graph.add_relationship("C", "D", "HYPOTHESIZED", 0.3, 0.3, "prior")

    policy_ab, _ = graph.get_reuse_policy("A", "B")
    assert policy_ab == "SKIP"

    policy_cd, _ = graph.get_reuse_policy("C", "D")
    assert policy_cd == "MUST_RETEST"

    policy_new, _ = graph.get_reuse_policy("X", "Y")
    assert policy_new == "MUST_RETEST"
