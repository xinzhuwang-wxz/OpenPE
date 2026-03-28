"""Sprint 6 integration: full lifecycle with _ref enhancements."""
import shutil
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

TMP = Path("/tmp/test_s6_integration")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_full_lifecycle():
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
    assert len(dag.edges) >= 1

    # 3. Build EP chain from discovered edges
    chain = EPChain()
    for edge in dag.edges:
        node = EPNode(
            event_id=f"{edge.source}→{edge.target}",
            truth=classify_truth("HYPOTHESIZED"),
            relevance=edge.relevance,
            evidence_type="HYPOTHESIZED",
        )
        chain.add_node(node)
    assert chain.joint_ep > 0

    # 4. Commit to causal knowledge graph with temporal fields
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    for edge in dag.edges:
        graph.add_relationship(
            source=edge.source,
            target=edge.target,
            relationship_type="HYPOTHESIZED",
            confidence=0.3,
            analysis_id="s6_test",
        )
    graph.save()

    # Verify temporal fields
    for rel in graph.relationships.values():
        assert rel.is_valid  # not invalidated
        assert not rel.is_expired

    # Test invalidation
    first_edge = list(graph.relationships.values())[0]
    graph.invalidate_edge(first_edge.source, first_edge.target, "s6_test_v2")
    assert not first_edge.is_valid
    assert first_edge.invalid_at != ""

    # Query with only_valid should exclude invalidated
    valid_rels = graph.query(only_valid=True)
    invalid_rels = graph.query(only_valid=False)
    assert len(valid_rels) < len(invalid_rels)

    # 5. Commit to memory store with hotness tracking
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="s6_m1",
        content="Causal discovery found X→Y relationship",
        domain="test",
        memory_type="domain",
        tier="L1",
        confidence=0.5,
    ))
    store.add(MemoryEntry(
        memory_id="s6_l2_detail",
        content="Detailed analysis record",
        domain="test",
        memory_type="domain",
        tier="L2",
        confidence=0.3,
        active_count=0,
    ))

    # Load for analysis increments active_count
    loaded = store.load_for_analysis("test")
    reloaded_entry = store.get("s6_m1")
    assert reloaded_entry.active_count >= 1

    # Hotness scoring
    score = hotness_score(active_count=5, updated_at=reloaded_entry.updated)
    assert 0.0 < score <= 1.0

    # 6. Build audit trail with ACG Protocol patterns
    trail = AuditTrail(analysis_name="Sprint 6 Integration Test")

    # Add claim with IGM
    source_data = "X,Y,Z\n" + "\n".join(f"{x},{y},{z}" for x, y, z in zip(X[:5], Y[:5], Z[:5]))
    shi = compute_shi(source_data)
    igm = construct_igm("C1", shi, "data.csv:col_X")
    assert igm.startswith("[C1:")
    assert len(igm) > 10

    trail.add_claim(
        claim_id="C1",
        text=f"X causes Y {igm}",
        source_type="analysis",
        source_ref="phase3/causal_test.py",
        evidence_type="HYPOTHESIZED",
        confidence=0.3,
        phase="phase3",
    )
    trail.add_claim(
        claim_id="C2",
        text="Y causes Z",
        source_type="analysis",
        source_ref="phase3/causal_test.py",
        evidence_type="DATA_SUPPORTED",
        confidence=0.7,
        phase="phase3",
    )

    # Add source record (SSR)
    trail.add_source(
        shi=shi,
        source_type="computation",
        uri="phase3/data.csv",
        location="col_X",
        verification_status="VERIFIED",
    )

    # Add veracity record (VAR) with relationship marker
    rm = construct_rm("R1", "CAUSAL_CLAIM", ["C1", "C2"])
    assert rm == "(R1:CAUSAL_CLAIM:C1,C2)"

    trail.add_veracity(
        relation_id="R1",
        relation_type="CAUSAL_CLAIM",
        dependent_claims=["C1", "C2"],
        synthesis_prose="X→Y→Z causal chain established",
    )

    # Verify logic (C1 is HYPOTHESIZED → should fail)
    trail.verify_logic()
    assert trail.veracity[0].audit_status == "INSUFFICIENT_PREMISE"

    # Save and reload
    audit_dir = TMP / "audit"
    trail.save(audit_dir)
    loaded_trail = AuditTrail.load(audit_dir)
    assert len(loaded_trail.claims) == 2
    assert len(loaded_trail.sources) == 1
    assert len(loaded_trail.veracity) == 1
    assert loaded_trail.sources[0].verification_status == "VERIFIED"

    # Markdown output includes SSR and VAR tables
    md = loaded_trail.to_markdown()
    assert "Source Registry" in md
    assert "Veracity Audit" in md


def test_memory_deduplication():
    """Test keyword-based similarity for deduplication."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="dup1",
        content="Bootstrap confidence intervals work well for small samples",
        domain="statistics",
        memory_type="method",
        tier="L1",
    ))
    store.add(MemoryEntry(
        memory_id="dup2",
        content="For small samples, bootstrap methods give good confidence intervals",
        domain="statistics",
        memory_type="method",
        tier="L1",
    ))

    similar = store.find_similar("bootstrap confidence intervals small samples")
    assert len(similar) >= 2
    # Both entries should be found as similar
    ids = {entry.memory_id for entry, _ in similar}
    assert "dup1" in ids
    assert "dup2" in ids


def test_memory_archival():
    """Test cold L2 entry archival."""
    store = MemoryStore(TMP / "memory")

    # Add an L2 entry with 0 active_count (very cold)
    store.add(MemoryEntry(
        memory_id="cold_l2",
        content="Old analysis detail",
        domain="test",
        memory_type="domain",
        tier="L2",
        confidence=0.3,
        active_count=0,
        # Set updated to a very old timestamp to ensure low hotness
        updated="2020-01-01T00:00:00",
    ))

    archived = store.archive(threshold=0.5)
    assert "cold_l2" in archived
    assert "cold_l2" not in store.entries

    # Verify archive file exists
    archive_path = TMP / "memory" / "L2" / "_archive" / "cold_l2.yaml"
    assert archive_path.exists()


def test_graph_prune_stale():
    """Test stale relationship pruning."""
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "HYPOTHESIZED", 0.3, 0.3, "old_analysis")
    # Manually set old timestamp
    rel = graph.relationships["A→B"]
    rel.updated = "2020-01-01T00:00:00"

    expired = graph.prune_stale(max_age_days=30)
    assert "A→B" in expired
    assert rel.is_expired
