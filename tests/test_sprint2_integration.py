"""Integration test: EP engine + DAG + causal pipeline work together."""
import pytest
from src.templates.scripts.ep_engine import EPNode, EPChain, classify_truth
from src.templates.scripts.dag_utils import CausalDAG
from src.templates.scripts.causal_pipeline import classify_refutation_results, RefutationResult
from src.templates.scripts.subchain import should_expand


def test_dag_to_ep_chain():
    """Build a DAG, convert edges to EP chain, check truncation."""
    dag = CausalDAG()
    dag.add_edge("urbanization", "birth_rate", label="DATA_SUPPORTED", truth=0.85, relevance=0.55)
    dag.add_edge("birth_rate", "labor_force", label="CORRELATION", truth=0.50, relevance=0.40)
    dag.add_edge("labor_force", "gdp_growth", label="THEORIZED", truth=0.30, relevance=0.30)

    chain = EPChain()
    for edge in dag.edges:
        chain.add_node(EPNode(
            event_id=f"{edge.source}_to_{edge.target}",
            truth=edge.truth,
            relevance=edge.relevance,
            evidence_type=edge.label,
        ))

    # EP values: 0.4675, 0.20, 0.09
    # Joint: 0.4675 * 0.20 * 0.09 ≈ 0.00842
    assert chain.joint_ep < 0.05  # HARD_TRUNCATION
    assert chain.truncation == "HARD_TRUNCATION"


def test_refutation_updates_ep():
    """Refutation results update truth → EP changes."""
    # Start with THEORIZED edge
    node = EPNode("e1", truth=0.30, relevance=0.60, evidence_type="THEORIZED")
    assert node.ep == pytest.approx(0.18)

    # After refutation: all 3 pass → DATA_SUPPORTED
    results = [
        RefutationResult("placebo", passed=True),
        RefutationResult("random_common_cause", passed=True),
        RefutationResult("data_subset", passed=True),
    ]
    new_type = classify_refutation_results(results)
    assert new_type == "DATA_SUPPORTED"

    # Update node with new truth
    new_truth = classify_truth(new_type)
    updated = EPNode("e1", truth=new_truth, relevance=0.60, evidence_type=new_type)
    assert updated.ep == pytest.approx(0.85 * 0.60)  # = 0.51
    assert updated.ep > node.ep  # EP increased


def test_subchain_expansion_decision():
    """Sub-chain expansion integrates EP chain with expansion check."""
    chain = EPChain()
    node1 = EPNode("e1", truth=0.85, relevance=0.55, evidence_type="DATA_SUPPORTED")
    chain.add_node(node1)

    # node1 EP = 0.4675 > 0.30, joint EP = 0.4675 > 0.15 → should expand
    assert should_expand(node1.ep, chain.joint_ep) is True

    # Add weak node
    node2 = EPNode("e2", truth=0.20, relevance=0.10, evidence_type="HYPOTHESIZED")
    chain.add_node(node2)

    # node2 EP = 0.02 < 0.30 → should NOT expand
    assert should_expand(node2.ep, chain.joint_ep) is False


def test_full_chain_serialization_roundtrip():
    """DAG → EPChain → dict → EPChain roundtrip preserves data."""
    dag = CausalDAG()
    dag.add_edge("A", "B", truth=0.9, relevance=0.7, label="DATA_SUPPORTED")
    dag.add_edge("B", "C", truth=0.6, relevance=0.4, label="CORRELATION")

    chain = EPChain()
    for edge in dag.edges:
        chain.add_node(EPNode(
            event_id=f"{edge.source}_{edge.target}",
            truth=edge.truth,
            relevance=edge.relevance,
            evidence_type=edge.label,
        ))

    d = chain.to_dict()
    chain2 = EPChain.from_dict(d)
    assert chain2.joint_ep == pytest.approx(chain.joint_ep)
    assert len(chain2.nodes) == 2

    # DAG also roundtrips
    dag_d = dag.to_dict()
    dag2 = CausalDAG.from_dict(dag_d)
    assert len(dag2.edges) == 2
