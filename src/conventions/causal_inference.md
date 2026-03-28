# Causal Inference Conventions

> **When this applies:** Any analysis using DAG-based causal inference,
> do-calculus, instrumental variables, difference-in-differences, or
> regression discontinuity designs.

## Required Methodology

- Construct a DAG before selecting estimation strategy
- Every causal claim must survive at least 3 refutation tests (placebo,
  random common cause, data subset)
- Report effect sizes with confidence intervals, not just p-values
- Acknowledge and document all untestable assumptions (e.g., no unmeasured
  confounders)

## DoWhy Pipeline Requirements

- Use `CausalTest` from `scripts/causal_pipeline.py` for all causal edges
- Classification follows the refutation-based taxonomy:
  DATA_SUPPORTED, CORRELATION, HYPOTHESIZED, DISPUTED
- EP values must be updated after each refutation battery

## Common Pitfalls

- Treating correlation as causation without refutation testing
- Ignoring collider bias when conditioning on intermediate variables
- Using causal language ("X causes Y") for CORRELATION-classified edges
