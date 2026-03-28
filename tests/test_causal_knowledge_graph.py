"""Unit tests for causal_knowledge_graph.py."""
import shutil
from pathlib import Path
from src.templates.scripts.causal_knowledge_graph import CausalRelationship, CausalKnowledgeGraph

TMP = Path("/tmp/test_causal_kg")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_relationship_creation():
    rel = CausalRelationship(
        source="interest_rate", target="credit_expansion",
        relationship_type="CAUSES", strength=0.73, confidence=0.8,
    )
    assert rel.edge_id == "interest_rate→credit_expansion"
    assert rel.reuse_policy == "SKIP"


def test_reuse_policies():
    high = CausalRelationship(source="a", target="b", relationship_type="CAUSES", confidence=0.85)
    assert high.reuse_policy == "SKIP"

    mid = CausalRelationship(source="a", target="b", relationship_type="CAUSES", confidence=0.6)
    assert mid.reuse_policy == "LIGHTWEIGHT_VERIFY"

    low = CausalRelationship(source="a", target="b", relationship_type="HYPOTHESIZED", confidence=0.3)
    assert low.reuse_policy == "MUST_RETEST"


def test_corroborate_and_contradict():
    rel = CausalRelationship(source="a", target="b", relationship_type="CAUSES", confidence=0.5)
    rel.corroborate("a1")
    assert rel.confidence == 0.6
    assert "a1" in rel.corroborated_by

    rel.contradict("a2")
    assert abs(rel.confidence - 0.4) < 0.001
    assert "a2" in rel.contradicted_by


def test_graph_save_load():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.8, "a1")
    graph.add_relationship("Y", "Z", "CORRELATED_WITH", 0.3, 0.4, "a1")
    graph.save()

    graph2 = CausalKnowledgeGraph(TMP / "graph.json")
    graph2.load()
    assert len(graph2.relationships) == 2
    assert "X→Y" in graph2.relationships


def test_add_existing_corroborates():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.5, "a1")
    graph.add_relationship("X", "Y", "CAUSES", 0.8, 0.5, "a2")
    # Should corroborate, not duplicate
    assert len(graph.relationships) == 1
    rel = graph.relationships["X→Y"]
    assert rel.confidence > 0.5  # corroborated


def test_query():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.8, "a1")
    graph.add_relationship("X", "Z", "CORRELATED_WITH", 0.3, 0.3, "a1")
    graph.add_relationship("A", "B", "CAUSES", 0.5, 0.9, "a1")

    from_x = graph.query(source="X")
    assert len(from_x) == 2

    high_conf = graph.query(min_confidence=0.5)
    assert all(r.confidence >= 0.5 for r in high_conf)


def test_detect_contradictions():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.8, "a1")

    # New analysis finds only correlation
    contradiction = graph.detect_contradictions("X", "Y", "CORRELATED_WITH", "a2")
    assert contradiction is True
    assert graph.relationships["X→Y"].confidence < 0.8  # penalized


def test_reuse_policy_lookup():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.85, "a1")

    policy, rel = graph.get_reuse_policy("X", "Y")
    assert policy == "SKIP"
    assert rel is not None

    policy2, rel2 = graph.get_reuse_policy("A", "B")
    assert policy2 == "MUST_RETEST"
    assert rel2 is None


def test_mermaid_output():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("X", "Y", "CAUSES", 0.7, 0.8, "a1")
    mermaid = graph.to_mermaid()
    assert "graph TD" in mermaid
    assert "X" in mermaid
    assert "Y" in mermaid
