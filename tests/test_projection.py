"""Tests for projection engine."""
import numpy as np
import pytest
from src.templates.scripts.projection import (
    ScenarioParam,
    simulate_scenarios,
    sensitivity_analysis,
    detect_endgame,
)


def linear_outcome(params: dict[str, float]) -> float:
    """Simple linear outcome for testing: y = 2*a + 3*b."""
    return 2 * params.get("a", 0) + 3 * params.get("b", 0)


def test_simulate_produces_at_least_3_scenarios():
    params = [
        ScenarioParam("a", base_value=1.0, uncertainty=0.2),
        ScenarioParam("b", base_value=2.0, uncertainty=0.5),
    ]
    results = simulate_scenarios(params, linear_outcome, n_samples=1000)
    assert len(results) >= 3
    names = {r.name for r in results}
    assert "baseline" in names
    assert "optimistic" in names
    assert "pessimistic" in names


def test_baseline_is_deterministic():
    params = [ScenarioParam("a", 1.0, 0.1), ScenarioParam("b", 2.0, 0.1)]
    results = simulate_scenarios(params, linear_outcome)
    baseline = [r for r in results if r.name == "baseline"][0]
    assert baseline.outcome_mean == pytest.approx(8.0)  # 2*1 + 3*2
    assert baseline.outcome_std == 0.0


def test_optimistic_greater_than_pessimistic():
    params = [ScenarioParam("a", 1.0, 0.5), ScenarioParam("b", 2.0, 0.5)]
    results = simulate_scenarios(params, linear_outcome)
    opt = [r for r in results if r.name == "optimistic"][0]
    pess = [r for r in results if r.name == "pessimistic"][0]
    assert opt.outcome_mean > pess.outcome_mean


def test_sensitivity_ranking():
    params = [
        ScenarioParam("a", 1.0, 0.1),  # coefficient 2
        ScenarioParam("b", 2.0, 0.1, controllable=True),  # coefficient 3
    ]
    results = sensitivity_analysis(params, linear_outcome)
    assert results[0].param_name == "b"  # b has larger coefficient
    assert results[0].controllable is True


def test_endgame_robust():
    """Low-variance scenarios → Robust endgame."""
    from src.templates.scripts.projection import ScenarioResult
    scenarios = [
        ScenarioResult("baseline", 100.0, 0.0, np.array([100.0]), {}),
        ScenarioResult("optimistic", 102.0, 2.0, np.array([102.0]), {}),
        ScenarioResult("pessimistic", 98.0, 2.0, np.array([98.0]), {}),
        ScenarioResult("monte_carlo", 100.0, 3.0, np.random.normal(100, 3, 1000), {}),
    ]
    result = detect_endgame(scenarios)
    assert result["classification"] == "ROBUST_ENDGAME"


def test_endgame_unstable():
    """High-variance scenarios → Unstable trajectory."""
    from src.templates.scripts.projection import ScenarioResult
    scenarios = [
        ScenarioResult("baseline", 100.0, 0.0, np.array([100.0]), {}),
        ScenarioResult("optimistic", 300.0, 50.0, np.array([300.0]), {}),
        ScenarioResult("pessimistic", -50.0, 50.0, np.array([-50.0]), {}),
        ScenarioResult("monte_carlo", 100.0, 150.0, np.random.normal(100, 150, 1000), {}),
    ]
    result = detect_endgame(scenarios)
    assert result["classification"] in ("UNSTABLE_TRAJECTORY", "FORK_DEPENDENT")


def test_scenario_serialization():
    params = [ScenarioParam("a", 1.0, 0.1)]
    results = simulate_scenarios(params, lambda p: p["a"] * 2, n_samples=100)
    for r in results:
        d = r.to_dict()
        assert "name" in d
        assert "outcome_mean" in d
