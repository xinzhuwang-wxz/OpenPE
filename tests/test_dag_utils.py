"""Tests for causal DAG utilities."""
from src.templates.scripts.dag_utils import CausalDAG, CausalEdge


def test_add_edge():
    dag = CausalDAG()
    dag.add_edge("urbanization", "birth_rate", label="THEORIZED", relevance=0.5)
    assert len(dag.edges) == 1
    assert dag.edges[0].source == "urbanization"


def test_to_mermaid():
    dag = CausalDAG()
    dag.add_edge("A", "B", label="DATA_SUPPORTED", relevance=0.7)
    dag.add_edge("B", "C", label="CORRELATION", relevance=0.3)
    mermaid = dag.to_mermaid()
    assert "graph TD" in mermaid or "graph LR" in mermaid
    assert "A" in mermaid
    assert "B" in mermaid


def test_nodes_extracted():
    dag = CausalDAG()
    dag.add_edge("A", "B")
    dag.add_edge("B", "C")
    assert set(dag.nodes) == {"A", "B", "C"}


def test_serialization_roundtrip():
    dag = CausalDAG()
    dag.add_edge("X", "Y", label="THEORIZED", relevance=0.4, truth=0.6)
    d = dag.to_dict()
    dag2 = CausalDAG.from_dict(d)
    assert len(dag2.edges) == 1
    assert dag2.edges[0].source == "X"
    assert dag2.edges[0].relevance == 0.4


def test_ep_annotation():
    dag = CausalDAG()
    dag.add_edge("A", "B", truth=0.85, relevance=0.55, label="DATA_SUPPORTED")
    ep = dag.edges[0].ep
    assert abs(ep - 0.4675) < 0.001
