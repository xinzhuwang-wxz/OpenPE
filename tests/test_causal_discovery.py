"""Tests for causal_discovery.py."""
import numpy as np
import pandas as pd
from src.templates.scripts.causal_discovery import (
    discover_dag,
    discovery_to_causal_dag,
    evaluate_discovery,
    DiscoveryResult,
)


def _make_synthetic_data(n=500, seed=42):
    """Generate data with known causal structure: X→Y→Z, W→Y."""
    rng = np.random.RandomState(seed)
    X = rng.normal(0, 1, n)
    W = rng.normal(0, 1, n)
    Y = 0.8 * X + 0.5 * W + rng.normal(0, 0.5, n)
    Z = 0.6 * Y + rng.normal(0, 0.5, n)
    return pd.DataFrame({"X": X, "W": W, "Y": Y, "Z": Z})


def test_discover_dag_returns_result():
    data = _make_synthetic_data()
    result = discover_dag(data, alpha=0.05)
    assert isinstance(result, DiscoveryResult)
    assert len(result.variable_names) == 4
    assert result.adjacency_matrix.shape == (4, 4)
    assert len(result.edges) > 0


def test_discover_dag_finds_some_edges():
    data = _make_synthetic_data()
    result = discover_dag(data, alpha=0.05)
    edge_set = set(result.edges)
    # At minimum, discovery should find significant associations
    # The exact edges depend on the algorithm, but there should be some
    assert len(edge_set) >= 2


def test_discovery_to_causal_dag():
    data = _make_synthetic_data()
    result = discover_dag(data, alpha=0.05)
    dag = discovery_to_causal_dag(result)
    assert len(dag.edges) == len(result.edges)
    for edge in dag.edges:
        assert edge.label == "HYPOTHESIZED"
        assert edge.truth == 0.15


def test_evaluate_discovery_perfect():
    gt = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    metrics = evaluate_discovery(gt, gt)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_evaluate_discovery_partial():
    gt = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    discovered = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])  # found 1 of 2
    metrics = evaluate_discovery(discovered, gt)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5
    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 1


def test_evaluate_discovery_empty():
    gt = np.array([[0, 1], [0, 0]])
    discovered = np.zeros((2, 2))
    metrics = evaluate_discovery(discovered, gt)
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0


def test_serialization():
    data = _make_synthetic_data()
    result = discover_dag(data, alpha=0.05)
    d = result.to_dict()
    assert d["method"] in ("PC", "correlation_fallback")
    assert isinstance(d["adjacency_matrix"], list)
    assert isinstance(d["edges"], list)
