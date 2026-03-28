"""Tests for the EP (Explanatory Power) engine."""
import pytest
from src.templates.scripts.ep_engine import (
    compute_ep,
    joint_ep,
    truncation_decision,
    classify_truth,
    EPNode,
    EPChain,
)


def test_ep_bounded():
    """EP is always in [0, 1]."""
    assert 0 <= compute_ep(truth=1.0, relevance=1.0) <= 1
    assert 0 <= compute_ep(truth=0.0, relevance=0.0) <= 1
    assert compute_ep(truth=0.85, relevance=0.55) == pytest.approx(0.4675)


def test_ep_multiplicative():
    """EP = truth × relevance."""
    assert compute_ep(0.8, 0.5) == pytest.approx(0.4)


def test_joint_ep_decays():
    """Joint EP along a chain decays multiplicatively."""
    eps = [0.5, 0.4, 0.3]
    assert joint_ep(eps) == pytest.approx(0.06)


def test_joint_ep_empty():
    """Joint EP of empty chain is 1.0 (neutral element)."""
    assert joint_ep([]) == 1.0


def test_truncation_hard():
    """Joint EP < 0.05 → hard truncation."""
    decision = truncation_decision(0.04)
    assert decision == "HARD_TRUNCATION"


def test_truncation_soft():
    """0.05 <= Joint EP < 0.15 → soft truncation."""
    decision = truncation_decision(0.10)
    assert decision == "SOFT_TRUNCATION"


def test_truncation_normal():
    """Joint EP >= 0.15 → normal expansion."""
    decision = truncation_decision(0.20)
    assert decision == "NORMAL"


def test_classify_truth_data_supported():
    """DATA_SUPPORTED → truth in [0.7, 1.0]."""
    assert 0.7 <= classify_truth("DATA_SUPPORTED") <= 1.0


def test_classify_truth_correlation():
    """CORRELATION → truth in [0.3, 0.7]."""
    t = classify_truth("CORRELATION")
    assert 0.3 <= t <= 0.7


def test_classify_truth_hypothesized():
    """HYPOTHESIZED → truth in [0.0, 0.3]."""
    t = classify_truth("HYPOTHESIZED")
    assert 0.0 <= t <= 0.3


def test_ep_node():
    """EPNode stores truth, relevance, and computes EP."""
    node = EPNode(event_id="e1", truth=0.85, relevance=0.55, evidence_type="DATA_SUPPORTED")
    assert node.ep == pytest.approx(0.4675)


def test_ep_chain():
    """EPChain tracks nodes and computes joint EP with truncation."""
    chain = EPChain()
    chain.add_node(EPNode("e1", truth=0.85, relevance=0.55, evidence_type="DATA_SUPPORTED"))
    chain.add_node(EPNode("e2", truth=0.70, relevance=0.30, evidence_type="CORRELATION"))
    assert chain.joint_ep == pytest.approx(0.4675 * 0.21)
    assert chain.truncation == "SOFT_TRUNCATION"  # ~0.098


def test_ep_chain_serialization():
    """EPChain can serialize to and from dict (for YAML output)."""
    chain = EPChain()
    chain.add_node(EPNode("e1", truth=0.85, relevance=0.55, evidence_type="DATA_SUPPORTED"))
    d = chain.to_dict()
    assert "nodes" in d
    assert "joint_ep" in d
    chain2 = EPChain.from_dict(d)
    assert chain2.joint_ep == pytest.approx(chain.joint_ep)
