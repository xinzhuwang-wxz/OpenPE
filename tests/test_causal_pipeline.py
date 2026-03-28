"""Tests for the causal testing pipeline.

Note: Some tests use synthetic data and are slow.
The pipeline wraps DoWhy — tests verify our wrapper logic,
not DoWhy internals.
"""
import importlib.util
import subprocess
import sys

import pytest
import numpy as np
import pandas as pd


def _ensure_dowhy():
    """Try to import dowhy; if unavailable, attempt pip install."""
    if importlib.util.find_spec("dowhy") is not None:
        return True
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "dowhy", "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
        return importlib.util.find_spec("dowhy") is not None
    except Exception:
        return False


_dowhy_available = _ensure_dowhy()

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


def test_classify_two_pass_placebo_anchored():
    """Placebo pass + cc fail → DISPUTED (scheme C: real but confounded)."""
    results = [
        RefutationResult("placebo", passed=True, p_value=0.85),
        RefutationResult("random_common_cause", passed=False, p_value=0.03),
        RefutationResult("data_subset", passed=True, p_value=0.68),
    ]
    assert classify_refutation_results(results) == "DISPUTED"


def test_classify_correlation_no_placebo():
    """Without placebo, mixed results → CORRELATION (no anchor to contradict)."""
    results = [
        RefutationResult("random_common_cause", passed=True, p_value=0.72),
        RefutationResult("data_subset", passed=False, p_value=0.04),
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


def test_classify_contradictory_placebo_vs_subset():
    """Placebo passes but data_subset fails → DISPUTED."""
    results = [
        RefutationResult("placebo", passed=True, p_value=0.85),
        RefutationResult("random_common_cause", passed=True, p_value=0.72),
        RefutationResult("data_subset", passed=False, p_value=0.03),
    ]
    assert classify_refutation_results(results) == "DISPUTED"


def test_classify_contradictory_reverse():
    """Placebo fails but data_subset passes → DISPUTED."""
    results = [
        RefutationResult("placebo", passed=False, p_value=0.02),
        RefutationResult("random_common_cause", passed=True, p_value=0.65),
        RefutationResult("data_subset", passed=True, p_value=0.70),
    ]
    assert classify_refutation_results(results) == "DISPUTED"


def test_classify_non_contradictory_correlation():
    """Placebo fail + cc fail + subset fail with different p-values → HYPOTHESIZED."""
    results = [
        RefutationResult("placebo", passed=False, p_value=0.03),
        RefutationResult("random_common_cause", passed=False, p_value=0.02),
        RefutationResult("data_subset", passed=False, p_value=0.04),
    ]
    # All fail, no contradiction — just no evidence
    assert classify_refutation_results(results) == "HYPOTHESIZED"


def test_classify_placebo_fail_cc_pass_subset_fail():
    """Placebo fail + subset fail → not contradictory (both say 'not real')."""
    results = [
        RefutationResult("placebo", passed=False, p_value=0.02),
        RefutationResult("random_common_cause", passed=True, p_value=0.70),
        RefutationResult("data_subset", passed=False, p_value=0.04),
    ]
    assert classify_refutation_results(results) == "CORRELATION"


@pytest.mark.skipif(not _dowhy_available, reason="DoWhy not installed")
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
