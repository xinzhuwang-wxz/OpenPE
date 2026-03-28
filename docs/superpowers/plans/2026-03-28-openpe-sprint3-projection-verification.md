# OpenPE Sprint 3: Projection + Verification Runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the runtime modules for Phase 4 (Projection) and Phase 5 (Verification): scenario simulation, sensitivity analysis, endgame convergence detection, EP decay visualization, and independent verification utilities.

**Architecture:** Python modules in `src/templates/scripts/` copied into scaffolded analyses. The projector modules wrap numpy/scipy for Monte Carlo simulation and matplotlib for EP decay charts. The verification module provides automated checks that the verifier agent calls.

**Tech Stack:** Python 3.11+, numpy, scipy, matplotlib, pandas, pyyaml

**Spec:** Sections 3.2 Phase 4 (Projection), 3.2 Phase 5 (Verification), 2.2 (EP decay)

---

## Task 1: Scenario Simulation Engine

**Files:**
- Create: `src/templates/scripts/projection.py`
- Create: `tests/test_projection.py`

Monte Carlo scenario simulation from causal parameter distributions.

The module provides:
- `ScenarioParams`: dataclass holding variable name, base value, uncertainty, distribution type
- `simulate_scenarios()`: run Monte Carlo sampling, produce ≥3 scenarios (baseline, optimistic, pessimistic)
- `sensitivity_analysis()`: for each causal lever, compute ±X% impact on outcome
- `detect_endgame()`: classify convergence pattern (Robust/Fork-dependent/Equilibrium/Unstable)

Tests should verify: scenario count ≥3, sensitivity ranking is ordered, endgame classification works for each of the 4 types.

Commit: `git commit -m "feat: implement scenario simulation and endgame detection"`

---

## Task 2: EP Decay Visualization

**Files:**
- Create: `src/templates/scripts/ep_visualization.py`
- Create: `tests/test_ep_visualization.py`

The core visualization of OpenPE — confidence bands widening over chain depth / projection distance.

The module provides:
- `plot_ep_decay()`: generates the EP decay chart showing confidence bands at each chain node
- `plot_scenario_comparison()`: fan chart of scenarios with confidence envelope
- `plot_sensitivity_tornado()`: tornado diagram of sensitivity analysis results
- All plots saved as PNG with consistent OpenPE styling

Tests should verify: files are created, have non-zero size, correct format.

Commit: `git commit -m "feat: implement EP decay and projection visualizations"`

---

## Task 3: Verification Utilities

**Files:**
- Create: `src/templates/scripts/verification.py`
- Create: `tests/test_verification.py`

Automated verification checks that the verifier agent calls during Phase 5.

The module provides:
- `verify_data_provenance()`: spot-check registry.yaml entries (URLs accessible, hashes match)
- `verify_ep_propagation()`: recalculate EP chain from node values, compare to stored joint EP
- `verify_causal_labels()`: check that post-analysis labels match refutation test outcomes
- `generate_verification_report()`: produce VERIFICATION.md summarizing all checks

Tests should verify: provenance check catches mismatched hashes, EP verification catches wrong propagation, label verification catches mismatches.

Commit: `git commit -m "feat: implement verification utilities for Phase 5"`

---

## Task 4: Integration Test

**Files:**
- Create: `tests/test_sprint3_integration.py`

End-to-end test: build a DAG → compute EP → simulate scenarios → generate EP decay chart → verify propagation.

Commit: `git commit -m "test: add Sprint 3 integration tests"`

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Scenario simulation + endgame detection | 2 | 20 min |
| 2 | EP decay visualization | 2 | 15 min |
| 3 | Verification utilities | 2 | 15 min |
| 4 | Integration test | 1 | 10 min |
| **Total** | | **7 files** | **~60 min** |
