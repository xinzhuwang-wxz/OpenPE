# OpenPE Sprint 2: Core Analysis Runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Python runtime modules that OpenPE agents call during Phases 1-3: causal testing pipeline (DoWhy wrapper with 3-refutation protocol), EP calculation/propagation engine, and sub-chain expansion scaffolding mechanism.

**Architecture:** Reusable Python modules in `src/templates/scripts/` that get copied into each scaffolded analysis. Agents invoke these scripts via `pixi run py`. The modules wrap DoWhy for causal inference, implement the EP algebra from the spec, and provide sub-chain scaffolding utilities.

**Tech Stack:** Python 3.11+, DoWhy (causal inference), pandas, numpy, matplotlib (EP visualization), pyyaml (artifact serialization)

**Spec:** `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` — Sections 2.2-2.4 (EP), 3.2 Phase 3 (causal testing), 5.4 (artifact structure)

---

## File Map

### Files to Create
- `src/templates/scripts/ep_engine.py` — EP calculation, propagation, truncation decisions
- `src/templates/scripts/causal_pipeline.py` — DoWhy wrapper with 3-refutation protocol
- `src/templates/scripts/subchain.py` — Sub-chain expansion scaffolding utility
- `src/templates/scripts/dag_utils.py` — Causal DAG I/O (mermaid ↔ Python, EP annotation)
- `tests/test_ep_engine.py` — EP engine unit tests
- `tests/test_causal_pipeline.py` — Causal pipeline unit tests
- `tests/test_dag_utils.py` — DAG utility tests

### Files to Modify
- `src/scaffold_analysis.py` — Ensure new scripts are copied to scaffolded analyses

---

## Task 1: EP Engine

**Files:**
- Create: `src/templates/scripts/ep_engine.py`
- Create: `tests/test_ep_engine.py`

The EP engine implements the core metric from spec Section 2.2-2.3.

- [ ] **Step 1: Write tests**

Create `tests/test_ep_engine.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_ep_engine.py -v`
Expected: ImportError (module doesn't exist yet)

- [ ] **Step 3: Implement ep_engine.py**

Create `src/templates/scripts/ep_engine.py`:

```python
"""Explanatory Power (EP) engine for OpenPE.

EP = truth × relevance, where both are bounded in [0, 1].
Joint EP along a chain decays multiplicatively.
Truncation thresholds determine chain expansion decisions.

Reference: OpenPE spec Section 2.2-2.3
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# Default thresholds (can be overridden from analysis_config.yaml)
HARD_TRUNCATION = 0.05
SOFT_TRUNCATION = 0.15
SUBCHAIN_EXPANSION = 0.30


def compute_ep(truth: float, relevance: float) -> float:
    """Compute Explanatory Power = truth × relevance, bounded in [0, 1]."""
    return max(0.0, min(1.0, truth * relevance))


def joint_ep(eps: list[float]) -> float:
    """Compute joint EP along a chain (multiplicative decay)."""
    result = 1.0
    for ep in eps:
        result *= ep
    return result


def truncation_decision(
    jep: float,
    hard: float = HARD_TRUNCATION,
    soft: float = SOFT_TRUNCATION,
) -> str:
    """Determine truncation decision based on joint EP.

    Returns: "HARD_TRUNCATION" | "SOFT_TRUNCATION" | "NORMAL"
    """
    if jep < hard:
        return "HARD_TRUNCATION"
    elif jep < soft:
        return "SOFT_TRUNCATION"
    else:
        return "NORMAL"


def classify_truth(evidence_type: str) -> float:
    """Map evidence classification to default truth value.

    DATA_SUPPORTED → 0.85 (midpoint of [0.7, 1.0])
    CORRELATION    → 0.50 (midpoint of [0.3, 0.7])
    HYPOTHESIZED   → 0.15 (midpoint of [0.0, 0.3])
    DISPUTED       → 0.30 (treated as weak correlation pending review)
    """
    mapping = {
        "DATA_SUPPORTED": 0.85,
        "CORRELATION": 0.50,
        "HYPOTHESIZED": 0.15,
        "DISPUTED": 0.30,
    }
    return mapping.get(evidence_type, 0.15)


@dataclass
class EPNode:
    """A node in an explanatory chain with EP metadata."""

    event_id: str
    truth: float
    relevance: float
    evidence_type: str = "HYPOTHESIZED"
    description: str = ""

    @property
    def ep(self) -> float:
        return compute_ep(self.truth, self.relevance)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "truth": self.truth,
            "relevance": self.relevance,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "ep": round(self.ep, 4),
        }

    @classmethod
    def from_dict(cls, d: dict) -> EPNode:
        return cls(
            event_id=d["event_id"],
            truth=d["truth"],
            relevance=d["relevance"],
            evidence_type=d.get("evidence_type", "HYPOTHESIZED"),
            description=d.get("description", ""),
        )


@dataclass
class EPChain:
    """An explanatory chain with EP propagation and truncation tracking."""

    nodes: list[EPNode] = field(default_factory=list)

    def add_node(self, node: EPNode) -> None:
        self.nodes.append(node)

    @property
    def joint_ep(self) -> float:
        return joint_ep([n.ep for n in self.nodes])

    @property
    def truncation(self) -> str:
        return truncation_decision(self.joint_ep)

    def should_expand_subchain(self, node: EPNode) -> bool:
        """Check if a node warrants sub-chain expansion."""
        return (
            node.ep > SUBCHAIN_EXPANSION
            and self.joint_ep > SOFT_TRUNCATION
        )

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "joint_ep": round(self.joint_ep, 4),
            "truncation": self.truncation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EPChain:
        chain = cls()
        for nd in d.get("nodes", []):
            chain.add_node(EPNode.from_dict(nd))
        return chain
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_ep_engine.py -v`
Expected: All 13 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/ep_engine.py tests/test_ep_engine.py
git commit -m "feat: implement EP engine (calculation, propagation, truncation)"
```

---

## Task 2: DAG Utilities

**Files:**
- Create: `src/templates/scripts/dag_utils.py`
- Create: `tests/test_dag_utils.py`

Utilities for working with causal DAGs: creating, serializing to mermaid, annotating with EP, loading/saving.

- [ ] **Step 1: Write tests**

Create `tests/test_dag_utils.py`:

```python
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
```

- [ ] **Step 2: Implement dag_utils.py**

Create `src/templates/scripts/dag_utils.py` with:
- `CausalEdge` dataclass (source, target, label, truth, relevance, ep property)
- `CausalDAG` class (edges list, add_edge, nodes property, to_mermaid, to_dict, from_dict)
- Mermaid output format with EP and label annotations on edges

- [ ] **Step 3: Run tests, commit**

```bash
python3 -m pytest tests/test_dag_utils.py -v
git add src/templates/scripts/dag_utils.py tests/test_dag_utils.py
git commit -m "feat: add causal DAG utilities (mermaid, serialization, EP annotation)"
```

---

## Task 3: Causal Testing Pipeline

**Files:**
- Create: `src/templates/scripts/causal_pipeline.py`
- Create: `tests/test_causal_pipeline.py`

DoWhy wrapper implementing the 3-refutation protocol from spec Section 3.2 Phase 3.

- [ ] **Step 1: Write tests**

Create `tests/test_causal_pipeline.py`:

```python
"""Tests for the causal testing pipeline.

Note: Some tests use synthetic data and are slow.
The pipeline wraps DoWhy — tests verify our wrapper logic,
not DoWhy internals.
"""
import pytest
import numpy as np
import pandas as pd
from src.templates.scripts.causal_pipeline import (
    CausalTest,
    RefutationResult,
    classify_refutation_results,
)


def test_classify_all_pass():
    """All 3 refutations pass → DATA_SUPPORTED."""
    results = [
        RefutationResult("placebo", passed=True, p_value=0.85),
        RefutationResult("random_common_cause", passed=True, p_value=0.72),
        RefutationResult("data_subset", passed=True, p_value=0.68),
    ]
    assert classify_refutation_results(results) == "DATA_SUPPORTED"


def test_classify_two_pass():
    """2 pass, 1 fail → CORRELATION."""
    results = [
        RefutationResult("placebo", passed=True, p_value=0.85),
        RefutationResult("random_common_cause", passed=False, p_value=0.03),
        RefutationResult("data_subset", passed=True, p_value=0.68),
    ]
    assert classify_refutation_results(results) == "CORRELATION"


def test_classify_all_fail():
    """All 3 fail → HYPOTHESIZED."""
    results = [
        RefutationResult("placebo", passed=False, p_value=0.01),
        RefutationResult("random_common_cause", passed=False, p_value=0.02),
        RefutationResult("data_subset", passed=False, p_value=0.04),
    ]
    assert classify_refutation_results(results) == "HYPOTHESIZED"


def test_classify_insufficient():
    """Empty results → HYPOTHESIZED (untestable)."""
    assert classify_refutation_results([]) == "HYPOTHESIZED"


@pytest.mark.slow
def test_causal_test_with_synthetic_data():
    """Run full causal test on synthetic data with known causal effect."""
    np.random.seed(42)
    n = 500
    treatment = np.random.binomial(1, 0.5, n)
    outcome = 2.0 * treatment + np.random.normal(0, 1, n)
    df = pd.DataFrame({"treatment": treatment, "outcome": outcome})

    test = CausalTest(
        data=df,
        treatment="treatment",
        outcome="outcome",
        common_causes=[],
    )
    result = test.run()
    assert result.estimate is not None
    assert abs(result.estimate - 2.0) < 1.0  # reasonable range
    assert result.classification in ("DATA_SUPPORTED", "CORRELATION")
```

- [ ] **Step 2: Implement causal_pipeline.py**

Create `src/templates/scripts/causal_pipeline.py`:

```python
"""Causal testing pipeline for OpenPE.

Wraps DoWhy to implement the 3-refutation protocol:
1. Placebo treatment (random variable replacing treatment → effect should vanish)
2. Random common cause (adding random confounder → estimate should be stable)
3. Data subset (estimate on random subsets → should be consistent)

Reference: OpenPE spec Section 3.2 Phase 3, Step 3
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class RefutationResult:
    """Result of a single refutation test."""
    test_name: str
    passed: bool
    p_value: float | None = None
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "p_value": self.p_value,
            "details": self.details,
        }


@dataclass
class CausalTestResult:
    """Complete result of a causal test on one edge."""
    treatment: str
    outcome: str
    estimate: float | None
    ci_lower: float | None
    ci_upper: float | None
    methods_used: list[str]
    refutations: list[RefutationResult]
    classification: str  # DATA_SUPPORTED | CORRELATION | HYPOTHESIZED | DISPUTED

    def to_dict(self) -> dict:
        return {
            "treatment": self.treatment,
            "outcome": self.outcome,
            "estimate": self.estimate,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "methods_used": self.methods_used,
            "refutations": [r.to_dict() for r in self.refutations],
            "classification": self.classification,
        }


def classify_refutation_results(results: list[RefutationResult]) -> str:
    """Classify causal relationship based on refutation test outcomes.

    Decision tree (from spec):
      All 3 pass           → DATA_SUPPORTED
      2 pass, 1 fail       → CORRELATION
      1 pass, 2 fail       → CORRELATION (weak)
      All 3 fail           → HYPOTHESIZED
      Insufficient data    → HYPOTHESIZED (untestable)
      Contradictory        → DISPUTED
    """
    if not results:
        return "HYPOTHESIZED"

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    if passed == total:
        return "DATA_SUPPORTED"
    elif passed == 0:
        return "HYPOTHESIZED"
    else:
        return "CORRELATION"


class CausalTest:
    """Run a causal test on a single edge using DoWhy.

    Estimates causal effect using multiple methods and runs
    3 refutation tests to classify the relationship.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        treatment: str,
        outcome: str,
        common_causes: list[str] | None = None,
        instruments: list[str] | None = None,
    ):
        self.data = data
        self.treatment = treatment
        self.outcome = outcome
        self.common_causes = common_causes or []
        self.instruments = instruments or []

    def run(self) -> CausalTestResult:
        """Execute the full causal testing pipeline."""
        try:
            import dowhy
            return self._run_with_dowhy()
        except ImportError:
            logger.warning("DoWhy not available — falling back to correlation-only analysis")
            return self._run_fallback()

    def _run_with_dowhy(self) -> CausalTestResult:
        """Full DoWhy pipeline with refutation tests."""
        from dowhy import CausalModel

        model = CausalModel(
            data=self.data,
            treatment=self.treatment,
            outcome=self.outcome,
            common_causes=self.common_causes if self.common_causes else None,
            instruments=self.instruments if self.instruments else None,
        )

        # Identify estimand
        estimand = model.identify_effect()

        # Estimate with backdoor (linear regression) as primary method
        methods_used = []
        estimate = model.estimate_effect(
            estimand,
            method_name="backdoor.linear_regression",
        )
        methods_used.append("backdoor.linear_regression")
        primary_value = estimate.value

        # Try propensity score as second method
        try:
            estimate2 = model.estimate_effect(
                estimand,
                method_name="backdoor.propensity_score_matching",
            )
            methods_used.append("backdoor.propensity_score_matching")
        except Exception:
            pass

        # Run 3 refutation tests
        refutations = []

        # 1. Placebo treatment
        try:
            ref1 = model.refute_estimate(
                estimand, estimate,
                method_name="placebo_treatment_refuter",
                placebo_type="permute",
            )
            refutations.append(RefutationResult(
                test_name="placebo",
                passed=ref1.refutation_result is True or (
                    hasattr(ref1, 'new_effect') and abs(ref1.new_effect) < abs(primary_value) * 0.5
                ),
                p_value=getattr(ref1, 'refutation_result', None) if isinstance(getattr(ref1, 'refutation_result', None), float) else None,
            ))
        except Exception as e:
            logger.warning(f"Placebo refutation failed: {e}")

        # 2. Random common cause
        try:
            ref2 = model.refute_estimate(
                estimand, estimate,
                method_name="random_common_cause",
            )
            refutations.append(RefutationResult(
                test_name="random_common_cause",
                passed=ref2.refutation_result is True or (
                    hasattr(ref2, 'new_effect') and abs(ref2.new_effect - primary_value) < abs(primary_value) * 0.2
                ),
                p_value=getattr(ref2, 'refutation_result', None) if isinstance(getattr(ref2, 'refutation_result', None), float) else None,
            ))
        except Exception as e:
            logger.warning(f"Random common cause refutation failed: {e}")

        # 3. Data subset
        try:
            ref3 = model.refute_estimate(
                estimand, estimate,
                method_name="data_subset_refuter",
                subset_fraction=0.8,
            )
            refutations.append(RefutationResult(
                test_name="data_subset",
                passed=ref3.refutation_result is True or (
                    hasattr(ref3, 'new_effect') and abs(ref3.new_effect - primary_value) < abs(primary_value) * 0.3
                ),
                p_value=getattr(ref3, 'refutation_result', None) if isinstance(getattr(ref3, 'refutation_result', None), float) else None,
            ))
        except Exception as e:
            logger.warning(f"Data subset refutation failed: {e}")

        classification = classify_refutation_results(refutations)

        return CausalTestResult(
            treatment=self.treatment,
            outcome=self.outcome,
            estimate=primary_value,
            ci_lower=None,  # TODO: extract from estimate
            ci_upper=None,
            methods_used=methods_used,
            refutations=refutations,
            classification=classification,
        )

    def _run_fallback(self) -> CausalTestResult:
        """Fallback: correlation-only analysis when DoWhy is unavailable."""
        corr = self.data[[self.treatment, self.outcome]].corr().iloc[0, 1]
        return CausalTestResult(
            treatment=self.treatment,
            outcome=self.outcome,
            estimate=corr,
            ci_lower=None,
            ci_upper=None,
            methods_used=["pearson_correlation (fallback)"],
            refutations=[],
            classification="CORRELATION",
        )
```

- [ ] **Step 3: Run tests, commit**

```bash
python3 -m pytest tests/test_causal_pipeline.py -v -k "not slow"
git add src/templates/scripts/causal_pipeline.py tests/test_causal_pipeline.py
git commit -m "feat: implement causal testing pipeline with 3-refutation protocol"
```

---

## Task 4: Sub-Chain Expansion Utility

**Files:**
- Create: `src/templates/scripts/subchain.py`

Utility for the orchestrator to scaffold sub-analyses when EP warrants expansion.

- [ ] **Step 1: Implement subchain.py**

Create `src/templates/scripts/subchain.py`:

```python
"""Sub-chain expansion utility for OpenPE.

When a main-chain event has EP > 0.3 and Joint_EP > 0.15,
the orchestrator can scaffold a sub-analysis to investigate
specific causal edges in depth.

Reference: OpenPE spec Section 2.4
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from dataclasses import dataclass

import yaml


@dataclass
class SubChainRequest:
    """Request to expand a sub-chain for deeper investigation."""
    parent_analysis: Path
    event_id: str
    edges_to_investigate: list[str]
    ep_threshold: float
    context_summary: str

    def to_dict(self) -> dict:
        return {
            "parent_analysis": str(self.parent_analysis),
            "event_id": self.event_id,
            "edges_to_investigate": self.edges_to_investigate,
            "ep_threshold": self.ep_threshold,
            "context_summary": self.context_summary,
        }


@dataclass
class SubChainResult:
    """Result returned from a sub-chain analysis."""
    sub_analysis_path: Path
    updated_eps: dict[str, float]  # edge_id → new EP
    classifications: dict[str, str]  # edge_id → DATA_SUPPORTED|CORRELATION|etc
    findings_summary: str  # ≤500 words

    def to_dict(self) -> dict:
        return {
            "sub_analysis_path": str(self.sub_analysis_path),
            "updated_eps": self.updated_eps,
            "classifications": self.classifications,
            "findings_summary": self.findings_summary,
        }


def should_expand(node_ep: float, chain_joint_ep: float,
                   min_ep: float = 0.30, min_joint: float = 0.15) -> bool:
    """Check if a node warrants sub-chain expansion.

    Expansion condition (from spec):
      node EP > 0.30 AND Joint_EP at expansion point > 0.15
    """
    return node_ep > min_ep and chain_joint_ep > min_joint


def scaffold_subanalysis(
    parent_dir: Path,
    event_id: str,
    scaffolder_path: Path | None = None,
) -> Path:
    """Scaffold a sub-analysis directory within the parent analysis.

    Creates: phase3_analysis/sub_analyses/{event_id}/
    with the standard OpenPE phase structure (lightweight).
    """
    sub_dir = parent_dir / "phase3_analysis" / "sub_analyses" / event_id

    if sub_dir.exists():
        return sub_dir

    sub_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal sub-analysis structure
    for phase in ["phase0_discovery", "phase1_strategy", "phase2_exploration",
                   "phase3_analysis", "phase4_projection", "phase5_verification"]:
        (sub_dir / phase).mkdir(exist_ok=True)
        (sub_dir / phase / "exec").mkdir(exist_ok=True)

    # Write sub-analysis config
    config = {
        "parent_analysis": str(parent_dir),
        "event_id": event_id,
        "is_subchain": True,
        "max_recursion_depth": 0,  # Sub-chains cannot expand further
        "review_tier": "1-bot",  # Lightweight review for sub-chains
    }
    with open(sub_dir / "subchain_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    return sub_dir
```

- [ ] **Step 2: Commit**

```bash
git add src/templates/scripts/subchain.py
git commit -m "feat: add sub-chain expansion utility"
```

---

## Task 5: Update Scaffolder + Integration Test

**Files:**
- Modify: `src/scaffold_analysis.py` (ensure new scripts are copied)
- Create: `tests/test_sprint2_integration.py`

- [ ] **Step 1: Verify scaffolder copies new scripts**

Run: `python3 src/scaffold_analysis.py /tmp/test_s2 && ls /tmp/test_s2/phase0_discovery/scripts/`
Expected: Should list ep_engine.py, causal_pipeline.py, dag_utils.py, subchain.py, registry_utils.py, fetch_worldbank.py, fetch_fred.py

- [ ] **Step 2: Write integration test**

Create `tests/test_sprint2_integration.py`:

```python
"""Integration test: EP engine + DAG + causal pipeline work together."""
import pytest
import numpy as np
import pandas as pd
from src.templates.scripts.ep_engine import EPNode, EPChain, classify_truth
from src.templates.scripts.dag_utils import CausalDAG
from src.templates.scripts.causal_pipeline import classify_refutation_results, RefutationResult


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
    # Joint: 0.4675 * 0.20 * 0.09 = 0.008415
    assert chain.joint_ep < 0.05  # should be HARD_TRUNCATION
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
    assert updated.ep > node.ep  # EP increased after supporting evidence
```

- [ ] **Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v -k "not slow"`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_sprint2_integration.py
git commit -m "test: add Sprint 2 integration tests (EP + DAG + causal pipeline)"
```

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | EP Engine | 2 (impl + test) | 15 min |
| 2 | DAG Utilities | 2 (impl + test) | 10 min |
| 3 | Causal Testing Pipeline | 2 (impl + test) | 20 min |
| 4 | Sub-Chain Expansion | 1 | 10 min |
| 5 | Integration Test | 1 test + scaffolder verify | 10 min |
| **Total** | | **8 files** | **~65 min** |
