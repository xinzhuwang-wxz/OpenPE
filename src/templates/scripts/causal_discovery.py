"""Causal structure discovery for OpenPE.

Discovers causal DAG structure from observational data using the
PC (Peter-Clark) algorithm via causal-learn. Falls back to pairwise
correlation thresholding when causal-learn is unavailable.

Graph evaluation metrics borrowed from Causica evaluation_metrics.py.

Reference: OpenPE spec — Phase 0 causal hypothesis generation
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from dag_utils import CausalDAG

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    """Result of causal structure discovery."""

    adjacency_matrix: np.ndarray
    variable_names: list[str]
    edges: list[tuple[str, str]] = field(default_factory=list)
    skeleton: list[tuple[str, str]] = field(default_factory=list)
    method: str = "PC"
    alpha: float = 0.05

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "alpha": self.alpha,
            "variable_names": self.variable_names,
            "edges": self.edges,
            "skeleton": self.skeleton,
            "adjacency_matrix": self.adjacency_matrix.tolist(),
        }


def discover_dag(
    data: pd.DataFrame,
    alpha: float = 0.05,
    method: str = "pc",
) -> DiscoveryResult:
    """Discover causal DAG from observational data.

    Args:
        data: DataFrame with variables as columns, observations as rows.
        alpha: significance level for independence tests.
        method: discovery algorithm ("pc" or "correlation_fallback").

    Returns:
        DiscoveryResult with adjacency matrix and extracted edges.
    """
    variable_names = list(data.columns)
    n_vars = len(variable_names)

    if method == "pc":
        try:
            return _discover_pc(data, variable_names, alpha)
        except ImportError:
            logger.warning(
                "causal-learn not available — falling back to correlation thresholding"
            )
            return _discover_correlation_fallback(data, variable_names, alpha)
    else:
        return _discover_correlation_fallback(data, variable_names, alpha)


def _discover_pc(
    data: pd.DataFrame,
    variable_names: list[str],
    alpha: float,
) -> DiscoveryResult:
    """PC algorithm via causal-learn."""
    from causallearn.search.ConstraintBased.PC import pc

    result = pc(data.values, alpha=alpha, indep_test="fisherz")
    graph = result.G.graph  # adjacency matrix

    n = len(variable_names)
    adj = np.zeros((n, n), dtype=int)
    edges = []
    skeleton = []

    for i in range(n):
        for j in range(n):
            if graph[i, j] == -1 and graph[j, i] == 1:
                # i --> j (directed edge)
                adj[i, j] = 1
                edges.append((variable_names[i], variable_names[j]))
            elif graph[i, j] == -1 and graph[j, i] == -1:
                # i --- j (undirected, part of skeleton)
                if i < j:
                    skeleton.append((variable_names[i], variable_names[j]))

    return DiscoveryResult(
        adjacency_matrix=adj,
        variable_names=variable_names,
        edges=edges,
        skeleton=skeleton,
        method="PC",
        alpha=alpha,
    )


def _discover_correlation_fallback(
    data: pd.DataFrame,
    variable_names: list[str],
    alpha: float,
) -> DiscoveryResult:
    """Fallback: threshold pairwise correlations to infer skeleton.

    Uses Fisher's z-test for significance. Directed edges are not inferred
    (all edges are undirected skeleton). This is NOT causal discovery —
    it's a best-effort skeleton when causal-learn is unavailable.
    """
    from scipy import stats

    n = len(variable_names)
    n_samples = len(data)
    adj = np.zeros((n, n), dtype=int)
    edges = []
    skeleton = []

    for i in range(n):
        for j in range(i + 1, n):
            corr, p_value = stats.pearsonr(data.iloc[:, i], data.iloc[:, j])
            if p_value < alpha and abs(corr) > 0.1:
                skeleton.append((variable_names[i], variable_names[j]))
                # Heuristic directionality: variable with lower variance is more
                # likely a cause (crude, but better than nothing for fallback)
                var_i = data.iloc[:, i].var()
                var_j = data.iloc[:, j].var()
                if var_i < var_j:
                    adj[i, j] = 1
                    edges.append((variable_names[i], variable_names[j]))
                else:
                    adj[j, i] = 1
                    edges.append((variable_names[j], variable_names[i]))

    return DiscoveryResult(
        adjacency_matrix=adj,
        variable_names=variable_names,
        edges=edges,
        skeleton=skeleton,
        method="correlation_fallback",
        alpha=alpha,
    )


def discovery_to_causal_dag(result: DiscoveryResult) -> CausalDAG:
    """Convert a DiscoveryResult into the OpenPE CausalDAG format.

    All discovered edges start as HYPOTHESIZED with default EP values.
    They must pass through the causal testing pipeline to be upgraded.
    """
    dag = CausalDAG()
    for source, target in result.edges:
        dag.add_edge(
            source=source,
            target=target,
            label="HYPOTHESIZED",
            truth=0.15,  # hypothesized default
            relevance=0.5,
        )
    return dag


def evaluate_discovery(
    discovered: np.ndarray,
    ground_truth: np.ndarray,
) -> dict:
    """Compute edge-level precision, recall, and F1.

    Borrowed from Causica graph/evaluation_metrics.py adjacency metrics.
    Both inputs should be binary adjacency matrices of the same shape.
    """
    d = (discovered > 0).astype(int)
    g = (ground_truth > 0).astype(int)

    # Exclude diagonal
    np.fill_diagonal(d, 0)
    np.fill_diagonal(g, 0)

    tp = int(np.sum(d & g))
    fp = int(np.sum(d & ~g))
    fn = int(np.sum(~d & g))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }
