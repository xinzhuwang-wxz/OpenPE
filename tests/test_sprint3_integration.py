"""Sprint 3 integration test: DAG → EP → Projection → Visualization → Verification."""
import pytest
import numpy as np
from pathlib import Path

from src.templates.scripts.ep_engine import EPNode, EPChain
from src.templates.scripts.dag_utils import CausalDAG
from src.templates.scripts.projection import (
    ScenarioParam, simulate_scenarios, sensitivity_analysis, detect_endgame,
)
from src.templates.scripts.ep_visualization import plot_ep_decay
from src.templates.scripts.verification import (
    verify_ep_propagation, verify_causal_labels, generate_verification_report,
)

OUTPUT_DIR = Path("/tmp/test_s3_integration")


def setup_function():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def teardown_function():
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)


def test_full_pipeline_dag_to_verification():
    """End-to-end: build DAG → compute EP → simulate → visualize → verify."""
    # 1. Build causal DAG
    dag = CausalDAG()
    dag.add_edge("urbanization", "birth_rate", label="DATA_SUPPORTED", truth=0.85, relevance=0.55)
    dag.add_edge("housing_cost", "birth_rate", label="CORRELATION", truth=0.70, relevance=0.30)

    # 2. Build EP chain
    chain = EPChain()
    for edge in dag.edges:
        chain.add_node(EPNode(
            event_id=f"{edge.source}_to_{edge.target}",
            truth=edge.truth,
            relevance=edge.relevance,
            evidence_type=edge.label,
        ))

    assert chain.joint_ep == pytest.approx(0.4675 * 0.21, abs=0.001)

    # 3. Simulate scenarios
    params = [
        ScenarioParam("urbanization_rate", 0.65, 0.05, controllable=False),
        ScenarioParam("housing_policy", 0.50, 0.20, controllable=True),
    ]
    outcome_fn = lambda p: -2.0 * p["urbanization_rate"] + 1.5 * p["housing_policy"]
    scenarios = simulate_scenarios(params, outcome_fn, n_samples=1000)
    assert len(scenarios) >= 3

    # 4. Detect endgame
    endgame = detect_endgame(scenarios)
    assert endgame["classification"] in (
        "ROBUST_ENDGAME", "FORK_DEPENDENT", "EQUILIBRIUM", "UNSTABLE_TRAJECTORY"
    )

    # 5. Visualize EP decay
    labels = [n.event_id for n in chain.nodes]
    eps = [n.ep for n in chain.nodes]
    joint_eps = []
    running = 1.0
    for ep in eps:
        running *= ep
        joint_eps.append(running)

    path = plot_ep_decay(labels, eps, joint_eps, OUTPUT_DIR / "ep_decay.png")
    assert path.exists()

    # 6. Verify EP propagation
    chain_dict = chain.to_dict()
    ep_checks = verify_ep_propagation(chain_dict)
    assert all(c.passed for c in ep_checks)

    # 7. Verify causal labels
    analysis_results = [{
        "treatment": "urbanization",
        "outcome": "birth_rate",
        "classification": "DATA_SUPPORTED",
        "refutations": [
            {"test_name": "placebo", "passed": True},
            {"test_name": "random_common_cause", "passed": True},
            {"test_name": "data_subset", "passed": True},
        ],
    }]
    label_checks = verify_causal_labels(analysis_results)
    assert all(c.passed for c in label_checks)


def test_sensitivity_drives_controllability():
    """Sensitivity analysis correctly identifies controllable vs exogenous."""
    params = [
        ScenarioParam("policy_lever", 1.0, 0.3, controllable=True),
        ScenarioParam("external_shock", 0.5, 0.1, controllable=False),
    ]
    results = sensitivity_analysis(
        params, lambda p: 3 * p["policy_lever"] + p["external_shock"]
    )
    # policy_lever has coefficient 3 → highest impact
    assert results[0].param_name == "policy_lever"
    assert results[0].controllable is True


def test_verification_report_integration():
    """Full verification report with all check types."""
    chain = {
        "nodes": [
            {"event_id": "e1", "truth": 0.9, "relevance": 0.6, "ep": 0.54},
        ],
        "joint_ep": 0.54,
    }
    analysis = [{
        "treatment": "X", "outcome": "Y",
        "classification": "CORRELATION",
        "refutations": [
            {"test_name": "placebo", "passed": True},
            {"test_name": "random_common_cause", "passed": False},
            {"test_name": "data_subset", "passed": True},
        ],
    }]
    report = generate_verification_report(chain_dict=chain, analysis_results=analysis)
    assert report.all_passed
    md = report.to_markdown()
    assert "PASSED" in md
    assert "Verification Report" in md
