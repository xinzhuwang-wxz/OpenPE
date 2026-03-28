# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Scenario simulation and endgame detection for OpenPE Phase 4.

Provides Monte Carlo scenario simulation from causal parameter
distributions, sensitivity analysis, and endgame convergence detection.

Reference: OpenPE spec Section 3.2 Phase 4
"""
from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from typing import Callable


@dataclass
class ScenarioParam:
    """A causal parameter with uncertainty for simulation."""
    name: str
    base_value: float
    uncertainty: float  # standard deviation
    controllable: bool = False  # can a policymaker influence this?
    distribution: str = "normal"  # "normal" | "uniform" | "lognormal"


@dataclass
class ScenarioResult:
    """Result of a single scenario simulation."""
    name: str  # "baseline", "optimistic", "pessimistic", or custom
    outcome_mean: float
    outcome_std: float
    outcome_samples: np.ndarray
    param_values: dict[str, float]  # parameter name → value used

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "outcome_mean": round(float(self.outcome_mean), 4),
            "outcome_std": round(float(self.outcome_std), 4),
            "param_values": {k: round(float(v), 4) for k, v in self.param_values.items()},
        }


@dataclass
class SensitivityResult:
    """Sensitivity of outcome to a single parameter."""
    param_name: str
    impact_magnitude: float  # absolute change in outcome per ±1 std
    impact_pct: float  # % change relative to baseline
    controllable: bool

    def to_dict(self) -> dict:
        return {
            "param_name": self.param_name,
            "impact_magnitude": round(self.impact_magnitude, 4),
            "impact_pct": round(self.impact_pct, 2),
            "controllable": self.controllable,
        }


def simulate_scenarios(
    params: list[ScenarioParam],
    outcome_fn: Callable[[dict[str, float]], float],
    n_samples: int = 10000,
    seed: int = 42,
) -> list[ScenarioResult]:
    """Run Monte Carlo simulation producing ≥3 scenarios.

    Args:
        params: list of causal parameters with uncertainties
        outcome_fn: function mapping {param_name: value} → outcome
        n_samples: number of Monte Carlo samples
        seed: random seed for reproducibility

    Returns:
        List of ScenarioResult (baseline, optimistic, pessimistic, + full MC)
    """
    rng = np.random.default_rng(seed)
    scenarios = []

    # Baseline: all parameters at base values
    base_values = {p.name: p.base_value for p in params}
    baseline_outcome = outcome_fn(base_values)
    scenarios.append(ScenarioResult(
        name="baseline",
        outcome_mean=baseline_outcome,
        outcome_std=0.0,
        outcome_samples=np.array([baseline_outcome]),
        param_values=base_values,
    ))

    # Monte Carlo: sample from parameter distributions
    mc_outcomes = []
    for _ in range(n_samples):
        sample = {}
        for p in params:
            if p.distribution == "normal":
                sample[p.name] = rng.normal(p.base_value, p.uncertainty)
            elif p.distribution == "uniform":
                sample[p.name] = rng.uniform(
                    p.base_value - p.uncertainty,
                    p.base_value + p.uncertainty,
                )
            elif p.distribution == "lognormal":
                mu = np.log(p.base_value**2 / np.sqrt(p.uncertainty**2 + p.base_value**2))
                sigma = np.sqrt(np.log(1 + (p.uncertainty / p.base_value)**2))
                sample[p.name] = rng.lognormal(mu, sigma)
            else:
                sample[p.name] = p.base_value
        mc_outcomes.append(outcome_fn(sample))

    mc_outcomes = np.array(mc_outcomes)

    # Optimistic: 90th percentile
    opt_idx = np.argmin(np.abs(mc_outcomes - np.percentile(mc_outcomes, 90)))
    scenarios.append(ScenarioResult(
        name="optimistic",
        outcome_mean=float(np.percentile(mc_outcomes, 90)),
        outcome_std=float(np.std(mc_outcomes)),
        outcome_samples=mc_outcomes[mc_outcomes >= np.percentile(mc_outcomes, 75)],
        param_values=base_values,  # simplified
    ))

    # Pessimistic: 10th percentile
    scenarios.append(ScenarioResult(
        name="pessimistic",
        outcome_mean=float(np.percentile(mc_outcomes, 10)),
        outcome_std=float(np.std(mc_outcomes)),
        outcome_samples=mc_outcomes[mc_outcomes <= np.percentile(mc_outcomes, 25)],
        param_values=base_values,
    ))

    # Full MC distribution
    scenarios.append(ScenarioResult(
        name="monte_carlo",
        outcome_mean=float(np.mean(mc_outcomes)),
        outcome_std=float(np.std(mc_outcomes)),
        outcome_samples=mc_outcomes,
        param_values=base_values,
    ))

    return scenarios


def sensitivity_analysis(
    params: list[ScenarioParam],
    outcome_fn: Callable[[dict[str, float]], float],
    delta_fraction: float = 0.10,
) -> list[SensitivityResult]:
    """Compute sensitivity of outcome to each parameter.

    For each param, compute outcome at base ± delta and measure impact.
    Results sorted by impact magnitude (descending).
    """
    base_values = {p.name: p.base_value for p in params}
    baseline = outcome_fn(base_values)
    results = []

    for p in params:
        delta = abs(p.base_value * delta_fraction) if p.base_value != 0 else delta_fraction
        up_values = {**base_values, p.name: p.base_value + delta}
        down_values = {**base_values, p.name: p.base_value - delta}

        up_outcome = outcome_fn(up_values)
        down_outcome = outcome_fn(down_values)

        impact = abs(up_outcome - down_outcome) / 2
        impact_pct = (impact / abs(baseline) * 100) if baseline != 0 else 0.0

        results.append(SensitivityResult(
            param_name=p.name,
            impact_magnitude=impact,
            impact_pct=impact_pct,
            controllable=p.controllable,
        ))

    return sorted(results, key=lambda r: r.impact_magnitude, reverse=True)


def detect_endgame(scenarios: list[ScenarioResult], convergence_threshold: float = 0.10) -> dict:
    """Classify the endgame convergence pattern.

    Categories:
      - "Robust endgame": scenarios converge (std/mean < threshold)
      - "Fork-dependent": scenarios diverge significantly
      - "Equilibrium": mean is stable, low variance
      - "Unstable trajectory": high variance, no convergence

    Returns dict with classification, confidence, and description.
    """
    named = {s.name: s for s in scenarios}
    mc = named.get("monte_carlo")
    baseline = named.get("baseline")

    if mc is None or baseline is None:
        return {"classification": "INSUFFICIENT_DATA", "confidence": 0.0, "description": "Need MC and baseline scenarios"}

    cv = mc.outcome_std / abs(mc.outcome_mean) if mc.outcome_mean != 0 else float('inf')
    opt = named.get("optimistic")
    pess = named.get("pessimistic")

    if opt and pess:
        spread = abs(opt.outcome_mean - pess.outcome_mean)
        relative_spread = spread / abs(baseline.outcome_mean) if baseline.outcome_mean != 0 else float('inf')
    else:
        relative_spread = cv

    if cv < convergence_threshold:
        return {
            "classification": "ROBUST_ENDGAME",
            "confidence": 1.0 - cv,
            "description": f"Scenarios converge. Coefficient of variation = {cv:.3f} < {convergence_threshold}",
        }
    elif relative_spread > 1.0:
        return {
            "classification": "UNSTABLE_TRAJECTORY",
            "confidence": 0.3,
            "description": f"High divergence. Relative spread = {relative_spread:.2f}. Outcome highly sensitive to parameters.",
        }
    elif relative_spread > 0.5:
        return {
            "classification": "FORK_DEPENDENT",
            "confidence": 0.5,
            "description": f"Scenarios diverge based on parameter values. Relative spread = {relative_spread:.2f}.",
        }
    else:
        return {
            "classification": "EQUILIBRIUM",
            "confidence": 0.7,
            "description": f"Moderate variance suggests stable equilibrium with uncertainty. CV = {cv:.3f}.",
        }
