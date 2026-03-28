# OpenPE Sprint 3: Projection + Verification Runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the runtime modules for Phase 4 (Projection) and Phase 5 (Verification): scenario simulation, sensitivity analysis, endgame convergence detection, EP decay visualization, and independent verification utilities.

**Architecture:** Python modules in `src/templates/scripts/` copied into scaffolded analyses. The projector modules wrap numpy/scipy for Monte Carlo simulation and matplotlib for EP decay charts. The verification module provides automated checks that the verifier agent calls.

**Tech Stack:** Python 3.11+, numpy, scipy, matplotlib, pandas, pyyaml

**Spec:** `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` — Sections 3.2 Phase 4 (Projection), 3.2 Phase 5 (Verification), 2.2 (EP decay)

---

## File Map

### Files to Create
- `src/templates/scripts/projection.py` — Scenario simulation, sensitivity analysis, endgame detection
- `src/templates/scripts/ep_visualization.py` — EP decay chart, scenario comparison, tornado diagram
- `src/templates/scripts/verification.py` — Data provenance, EP propagation, causal label verification
- `tests/test_projection.py` — Projection engine unit tests
- `tests/test_ep_visualization.py` — Visualization output tests
- `tests/test_verification.py` — Verification logic tests
- `tests/test_sprint3_integration.py` — End-to-end integration test

---

## Task 1: Scenario Simulation Engine

**Files:**
- Create: `src/templates/scripts/projection.py`
- Create: `tests/test_projection.py`

Monte Carlo scenario simulation from causal parameter distributions.

- [ ] **Step 1: Write tests**

Create `tests/test_projection.py`:

```python
"""Tests for scenario simulation and endgame detection."""
import pytest
import numpy as np
from src.templates.scripts.projection import (
    ScenarioParam, ScenarioResult, SensitivityResult,
    simulate_scenarios, sensitivity_analysis, detect_endgame,
)


def _make_params():
    return [
        ScenarioParam("growth_rate", 0.03, 0.01, controllable=True),
        ScenarioParam("inflation", 0.02, 0.005, controllable=False),
    ]


def _outcome_fn(p):
    return 100 * (1 + p["growth_rate"]) - 50 * p["inflation"]


def test_simulate_produces_at_least_3_scenarios():
    scenarios = simulate_scenarios(_make_params(), _outcome_fn)
    assert len(scenarios) >= 3
    names = {s.name for s in scenarios}
    assert {"baseline", "optimistic", "pessimistic"}.issubset(names)


def test_baseline_is_deterministic():
    s1 = simulate_scenarios(_make_params(), _outcome_fn, seed=42)
    s2 = simulate_scenarios(_make_params(), _outcome_fn, seed=42)
    b1 = next(s for s in s1 if s.name == "baseline")
    b2 = next(s for s in s2 if s.name == "baseline")
    assert b1.outcome_mean == b2.outcome_mean


def test_optimistic_greater_than_pessimistic():
    scenarios = simulate_scenarios(_make_params(), _outcome_fn)
    opt = next(s for s in scenarios if s.name == "optimistic")
    pess = next(s for s in scenarios if s.name == "pessimistic")
    assert opt.outcome_mean > pess.outcome_mean


def test_sensitivity_ranking():
    results = sensitivity_analysis(_make_params(), _outcome_fn)
    assert len(results) == 2
    assert results[0].impact_magnitude >= results[1].impact_magnitude


def test_endgame_robust():
    """Low variance → ROBUST_ENDGAME."""
    params = [ScenarioParam("x", 1.0, 0.01)]
    scenarios = simulate_scenarios(params, lambda p: p["x"])
    endgame = detect_endgame(scenarios, convergence_threshold=0.10)
    assert endgame["classification"] == "ROBUST_ENDGAME"


def test_endgame_unstable():
    """Extreme variance → UNSTABLE_TRAJECTORY."""
    params = [ScenarioParam("x", 1.0, 10.0)]
    scenarios = simulate_scenarios(params, lambda p: p["x"])
    endgame = detect_endgame(scenarios)
    assert endgame["classification"] in ("UNSTABLE_TRAJECTORY", "FORK_DEPENDENT")


def test_scenario_serialization():
    scenarios = simulate_scenarios(_make_params(), _outcome_fn)
    for s in scenarios:
        d = s.to_dict()
        assert "name" in d
        assert "outcome_mean" in d
```

- [ ] **Step 2: Implement projection.py**

Create `src/templates/scripts/projection.py` with:

**Data structures:**
- `ScenarioParam`: dataclass with `name`, `base_value`, `uncertainty`, `controllable`, `distribution` ("normal" | "uniform" | "lognormal")
- `ScenarioResult`: dataclass with `name`, `outcome_mean`, `outcome_std`, `outcome_samples` (ndarray), `param_values` (dict), `to_dict()`
- `SensitivityResult`: dataclass with `param_name`, `impact_magnitude`, `impact_pct`, `controllable`, `to_dict()`

**Functions:**
- `simulate_scenarios(params, outcome_fn, n_samples=10000, seed=42) -> list[ScenarioResult]`
  - Baseline: all params at base values (deterministic)
  - Monte Carlo: sample n_samples from parameter distributions
  - Optimistic: 90th percentile of MC outcomes
  - Pessimistic: 10th percentile of MC outcomes
  - Supports normal, uniform, lognormal distributions via `rng = np.random.default_rng(seed)`

- `sensitivity_analysis(params, outcome_fn, delta_fraction=0.10) -> list[SensitivityResult]`
  - For each param: compute outcome at base ± delta
  - Impact = |up_outcome - down_outcome| / 2
  - Sort by impact magnitude descending

- `detect_endgame(scenarios, convergence_threshold=0.10) -> dict`
  - CV < threshold → `ROBUST_ENDGAME`
  - Relative spread > 1.0 → `UNSTABLE_TRAJECTORY`
  - Relative spread > 0.5 → `FORK_DEPENDENT`
  - Otherwise → `EQUILIBRIUM`
  - Returns dict with `classification`, `confidence`, `description`

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_projection.py -v
```

Commit: `git commit -m "feat: implement scenario simulation and endgame detection"`

---

## Task 2: EP Decay Visualization

**Files:**
- Create: `src/templates/scripts/ep_visualization.py`
- Create: `tests/test_ep_visualization.py`

The core visualization of OpenPE — confidence bands widening over chain depth / projection distance.

- [ ] **Step 1: Write tests**

Create `tests/test_ep_visualization.py`:

```python
"""Tests for EP visualization outputs."""
import pytest
from pathlib import Path
from src.templates.scripts.ep_visualization import (
    plot_ep_decay, plot_scenario_comparison, plot_sensitivity_tornado,
)

OUTPUT = Path("/tmp/test_ep_viz")


def setup_function():
    OUTPUT.mkdir(parents=True, exist_ok=True)


def teardown_function():
    import shutil
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)


def test_ep_decay_chart_created():
    labels = ["A→B", "B→C", "C→D"]
    ep_values = [0.6, 0.4, 0.3]
    joint_eps = [0.6, 0.24, 0.072]
    path = plot_ep_decay(labels, ep_values, joint_eps, OUTPUT / "decay.png")
    assert path.exists()
    assert path.stat().st_size > 0


def test_scenario_comparison_created():
    t = [0, 1, 2, 3]
    scenarios = {"baseline": [1, 2, 3, 4], "optimistic": [1, 2.5, 4, 6]}
    path = plot_scenario_comparison(t, scenarios, output_path=OUTPUT / "scenarios.png")
    assert path.exists()


def test_sensitivity_tornado_created():
    path = plot_sensitivity_tornado(
        ["param_a", "param_b"], [0.5, 0.3], [True, False],
        output_path=OUTPUT / "tornado.png")
    assert path.exists()


def test_ep_decay_with_single_node():
    path = plot_ep_decay(["A"], [0.8], [0.8], OUTPUT / "single.png")
    assert path.exists()
```

- [ ] **Step 2: Implement ep_visualization.py**

Create `src/templates/scripts/ep_visualization.py` with:

**Configuration:**
- `matplotlib.use("Agg")` — non-interactive backend
- OpenPE color palette: `COLORS = {"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c", "band": "#3498db", "baseline": "#2c3e50"}`

**Functions:**
- `plot_ep_decay(node_labels, ep_values, joint_eps, output_path, title, figsize) -> Path`
  - Two-panel subplot: top = per-node EP bars (color-coded green/orange/red by threshold), bottom = joint EP line with confidence band
  - Horizontal lines at 0.30 (sub-chain threshold), 0.15 (soft truncation), 0.05 (hard truncation)

- `plot_scenario_comparison(time_points, scenarios, confidence_band, output_path, title, xlabel, ylabel, figsize) -> Path`
  - Line chart with scenario-specific styles (solid baseline, dashed optimistic/pessimistic)
  - Optional confidence band fill_between

- `plot_sensitivity_tornado(param_names, impacts, controllable, output_path, title, figsize) -> Path`
  - Horizontal bar chart sorted by impact, color-coded green (controllable) vs orange (exogenous)

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_ep_visualization.py -v
```

Commit: `git commit -m "feat: implement EP decay and projection visualizations"`

---

## Task 3: Verification Utilities

**Files:**
- Create: `src/templates/scripts/verification.py`
- Create: `tests/test_verification.py`

Automated verification checks that the verifier agent calls during Phase 5.

- [ ] **Step 1: Write tests**

Create `tests/test_verification.py`:

```python
"""Tests for verification utilities."""
import pytest
from pathlib import Path
from src.templates.scripts.verification import (
    verify_data_provenance, verify_ep_propagation,
    verify_causal_labels, generate_verification_report,
    VerificationCheck, VerificationReport,
)


def test_provenance_missing_registry(tmp_path):
    checks = verify_data_provenance(tmp_path / "nonexistent.yaml")
    assert not checks[0].passed


def test_provenance_valid_registry(tmp_path):
    # ... creates registry.yaml with valid entry, checks pass


def test_provenance_hash_mismatch(tmp_path):
    # ... creates file with wrong hash, catches mismatch


def test_ep_propagation_correct():
    chain = {"nodes": [{"event_id": "e1", "truth": 0.9, "relevance": 0.6, "ep": 0.54}],
             "joint_ep": 0.54}
    checks = verify_ep_propagation(chain)
    assert all(c.passed for c in checks)


def test_ep_propagation_wrong_joint():
    chain = {"nodes": [{"event_id": "e1", "truth": 0.9, "relevance": 0.6, "ep": 0.54}],
             "joint_ep": 0.99}  # wrong!
    checks = verify_ep_propagation(chain)
    assert not all(c.passed for c in checks)


def test_causal_labels_correct():
    results = [{"treatment": "X", "outcome": "Y", "classification": "DATA_SUPPORTED",
                "refutations": [{"passed": True}, {"passed": True}, {"passed": True}]}]
    checks = verify_causal_labels(results)
    assert all(c.passed for c in checks)


def test_causal_labels_mismatch():
    results = [{"treatment": "X", "outcome": "Y", "classification": "DATA_SUPPORTED",
                "refutations": [{"passed": True}, {"passed": False}, {"passed": True}]}]
    checks = verify_causal_labels(results)
    assert not all(c.passed for c in checks)


def test_full_report():
    report = generate_verification_report(
        chain_dict={"nodes": [{"event_id": "e1", "truth": 0.9, "relevance": 0.6, "ep": 0.54}],
                     "joint_ep": 0.54})
    assert report.all_passed
    md = report.to_markdown()
    assert "Verification Report" in md
```

- [ ] **Step 2: Implement verification.py**

Create `src/templates/scripts/verification.py` with:

**Data structures:**
- `VerificationCheck`: dataclass with `name`, `passed`, `details`, `severity` ("error" | "warning")
- `VerificationReport`: dataclass with `checks` list, properties `all_passed`, `pass_count`, `fail_count`, methods `to_dict()`, `to_markdown()`

**Functions:**
- `verify_data_provenance(registry_path) -> list[VerificationCheck]`
  - Check registry YAML exists and is valid
  - Spot-check first and last entries for required fields (source_id, url, sha256, file)
  - Verify file exists and SHA-256 hash matches

- `verify_ep_propagation(chain_dict) -> list[VerificationCheck]`
  - Recalculate EP for each node: truth × relevance
  - Compare to stored ep value (tolerance 0.001)
  - Recalculate joint EP multiplicatively, compare to stored joint_ep

- `verify_causal_labels(analysis_results) -> list[VerificationCheck]`
  - For each edge result, count passed refutations
  - All 3 pass → DATA_SUPPORTED, 0 pass → HYPOTHESIZED, else → CORRELATION
  - Compare expected label to stored classification

- `generate_verification_report(registry_path, chain_dict, analysis_results) -> VerificationReport`
  - Runs all applicable checks, returns unified report

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_verification.py -v
```

Commit: `git commit -m "feat: implement verification utilities for Phase 5"`

---

## Task 4: Integration Test

**Files:**
- Create: `tests/test_sprint3_integration.py`

- [ ] **Step 1: Write integration test**

End-to-end: build a DAG → compute EP → simulate scenarios → generate EP decay chart → verify propagation.

```python
"""Sprint 3 integration test: DAG → EP → Projection → Visualization → Verification."""
import pytest
import numpy as np
from pathlib import Path
from src.templates.scripts.ep_engine import EPNode, EPChain
from src.templates.scripts.dag_utils import CausalDAG
from src.templates.scripts.projection import ScenarioParam, simulate_scenarios, sensitivity_analysis, detect_endgame
from src.templates.scripts.ep_visualization import plot_ep_decay
from src.templates.scripts.verification import verify_ep_propagation, verify_causal_labels, generate_verification_report


def test_full_pipeline_dag_to_verification():
    """End-to-end: build DAG → compute EP → simulate → visualize → verify."""
    # 1. Build causal DAG with 2 edges
    dag = CausalDAG()
    dag.add_edge("urbanization", "birth_rate", label="DATA_SUPPORTED", truth=0.85, relevance=0.55)
    dag.add_edge("housing_cost", "birth_rate", label="CORRELATION", truth=0.70, relevance=0.30)

    # 2. Build EP chain from DAG edges
    chain = EPChain()
    for edge in dag.edges:
        chain.add_node(EPNode(event_id=f"{edge.source}_to_{edge.target}",
                              truth=edge.truth, relevance=edge.relevance,
                              evidence_type=edge.label))
    assert chain.joint_ep == pytest.approx(0.4675 * 0.21, abs=0.001)

    # 3. Simulate scenarios
    params = [ScenarioParam("urbanization_rate", 0.65, 0.05, controllable=False),
              ScenarioParam("housing_policy", 0.50, 0.20, controllable=True)]
    scenarios = simulate_scenarios(params, lambda p: -2.0 * p["urbanization_rate"] + 1.5 * p["housing_policy"],
                                   n_samples=1000)
    assert len(scenarios) >= 3
    endgame = detect_endgame(scenarios)
    assert endgame["classification"] in ("ROBUST_ENDGAME", "FORK_DEPENDENT", "EQUILIBRIUM", "UNSTABLE_TRAJECTORY")

    # 4. Visualize EP decay
    path = plot_ep_decay([n.event_id for n in chain.nodes],
                         [n.ep for n in chain.nodes],
                         [running := 1.0] and [running := running * n.ep for n in chain.nodes][-1:],
                         Path("/tmp/test_s3_integration/ep_decay.png"))
    assert path.exists()

    # 5. Verify EP propagation
    chain_dict = chain.to_dict()
    assert all(c.passed for c in verify_ep_propagation(chain_dict))

    # 6. Verify causal labels
    analysis_results = [{"treatment": "urbanization", "outcome": "birth_rate",
                         "classification": "DATA_SUPPORTED",
                         "refutations": [{"passed": True}, {"passed": True}, {"passed": True}]}]
    assert all(c.passed for c in verify_causal_labels(analysis_results))


def test_sensitivity_drives_controllability():
    """Sensitivity analysis correctly identifies controllable vs exogenous."""
    params = [ScenarioParam("policy_lever", 1.0, 0.3, controllable=True),
              ScenarioParam("external_shock", 0.5, 0.1, controllable=False)]
    results = sensitivity_analysis(params, lambda p: 3 * p["policy_lever"] + p["external_shock"])
    assert results[0].param_name == "policy_lever"
    assert results[0].controllable is True


def test_verification_report_integration():
    """Full verification report with all check types."""
    chain = {"nodes": [{"event_id": "e1", "truth": 0.9, "relevance": 0.6, "ep": 0.54}], "joint_ep": 0.54}
    analysis = [{"treatment": "X", "outcome": "Y", "classification": "CORRELATION",
                 "refutations": [{"passed": True}, {"passed": False}, {"passed": True}]}]
    report = generate_verification_report(chain_dict=chain, analysis_results=analysis)
    assert report.all_passed
    assert "PASSED" in report.to_markdown()
```

- [ ] **Step 2: Run all Sprint 3 tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_projection.py tests/test_ep_visualization.py tests/test_verification.py tests/test_sprint3_integration.py -v
```

Commit: `git commit -m "test: add Sprint 3 integration tests"`

---

## Verification

```bash
# Run all Sprint 3 tests
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_projection.py tests/test_ep_visualization.py tests/test_verification.py tests/test_sprint3_integration.py -v

# Verify all prior tests still pass
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Scenario simulation + endgame detection | `projection.py` + `test_projection.py` | 20 min |
| 2 | EP decay visualization | `ep_visualization.py` + `test_ep_visualization.py` | 15 min |
| 3 | Verification utilities | `verification.py` + `test_verification.py` | 15 min |
| 4 | Integration test | `test_sprint3_integration.py` | 10 min |
| **Total** | | **7 files** | **~60 min** |
