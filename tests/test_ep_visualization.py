"""Tests for EP visualization module."""
from pathlib import Path
import pytest
from src.templates.scripts.ep_visualization import (
    plot_ep_decay,
    plot_scenario_comparison,
    plot_sensitivity_tornado,
)


OUTPUT_DIR = Path("/tmp/test_ep_viz")


def setup_function():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_ep_decay_chart_created():
    path = plot_ep_decay(
        node_labels=["Urbanization", "Housing Cost", "Birth Rate"],
        ep_values=[0.47, 0.21, 0.045],
        joint_eps=[0.47, 0.47 * 0.21, 0.47 * 0.21 * 0.045],
        output_path=OUTPUT_DIR / "ep_decay.png",
    )
    assert path.exists()
    assert path.stat().st_size > 1000  # non-trivial file


def test_scenario_comparison_created():
    path = plot_scenario_comparison(
        time_points=[2025, 2026, 2027, 2028, 2029],
        scenarios={
            "baseline": [100, 102, 104, 106, 108],
            "optimistic": [100, 105, 110, 118, 125],
            "pessimistic": [100, 98, 95, 90, 85],
        },
        output_path=OUTPUT_DIR / "scenarios.png",
    )
    assert path.exists()
    assert path.stat().st_size > 1000


def test_sensitivity_tornado_created():
    path = plot_sensitivity_tornado(
        param_names=["Interest Rate", "Urbanization", "Education"],
        impacts=[0.45, 0.30, 0.15],
        controllable=[True, False, True],
        output_path=OUTPUT_DIR / "tornado.png",
    )
    assert path.exists()
    assert path.stat().st_size > 1000


def test_ep_decay_with_single_node():
    """Edge case: single node chain."""
    path = plot_ep_decay(
        node_labels=["Single"],
        ep_values=[0.8],
        joint_eps=[0.8],
        output_path=OUTPUT_DIR / "single.png",
    )
    assert path.exists()
