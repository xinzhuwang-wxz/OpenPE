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

    Decision tree (from spec Section 3.2 / 4.2):
      All 3 pass           → DATA_SUPPORTED
      2 pass, 1 fail       → CORRELATION
      1 pass, 2 fail       → CORRELATION (weak)
      All 3 fail           → HYPOTHESIZED
      Insufficient data    → HYPOTHESIZED (untestable)
      Contradictory        → DISPUTED (flag for human review)
    """
    if not results:
        return "HYPOTHESIZED"

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    # Detect contradictory results: placebo passes (effect vanishes under
    # random treatment — good) but data_subset fails (effect not stable
    # across subsets — bad), or vice versa. This indicates internal
    # inconsistency in the evidence, not merely weak causation.
    if total >= 2 and _is_contradictory(results):
        return "DISPUTED"

    if passed == total:
        return "DATA_SUPPORTED"
    elif passed == 0:
        return "HYPOTHESIZED"
    else:
        return "CORRELATION"


def _is_contradictory(results: list[RefutationResult]) -> bool:
    """Detect contradictory refutation patterns.

    Contradictions arise when tests that should agree give opposite signals:
    - placebo passes (effect is treatment-specific) but data_subset fails
      (effect not stable) — the treatment matters but inconsistently
    - data_subset passes (stable effect) but placebo fails (random
      treatment also produces effect) — stable but not treatment-specific

    Returns True if the pattern is logically contradictory rather than
    merely inconclusive.
    """
    by_name = {r.test_name: r.passed for r in results}

    placebo = by_name.get("placebo")
    subset = by_name.get("data_subset")
    common_cause = by_name.get("random_common_cause")

    # Placebo and subset are the strongest contradiction pair:
    # - Placebo passes → effect is treatment-specific (real)
    # - Subset fails → effect is not stable across data splits (unreliable)
    # These directly contradict: the effect is "real" but "unreliable".
    #
    # The reverse is also contradictory:
    # - Placebo fails → random treatment also produces effect (not real)
    # - Subset passes → effect is perfectly stable (reliable)
    # A "not real" but "reliable" effect is contradictory.
    if placebo is not None and subset is not None:
        if placebo != subset:
            return True

    return False


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
            ci_lower=self._extract_ci(estimate, 0),
            ci_upper=self._extract_ci(estimate, 1),
            methods_used=methods_used,
            refutations=refutations,
            classification=classification,
        )

    @staticmethod
    def _extract_ci(estimate, index: int):
        """Extract confidence interval bound from DoWhy estimate.

        DoWhy's CausalEstimate uses get_confidence_intervals() method,
        not a stored attribute. Reference: dowhy/causal_estimator.py
        """
        try:
            ci = estimate.get_confidence_intervals()
            if ci is not None and len(ci) > index:
                return ci[index]
        except Exception:
            pass
        return None

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
