# Panel Analysis Conventions

> **When this applies:** Any analysis using cross-sectional data across
> multiple entities (countries, firms, individuals) over time.

## Required Methodology

- Use fixed effects (FE) as the default specification
- Run Hausman test to justify FE vs RE choice
- Cluster standard errors at the entity level
- Check for cross-sectional dependence (Pesaran CD test)

## Data Quality Requirements

- Report the panel balance (% of complete observations)
- Document any entity entry/exit patterns
- Missing values must be explicitly documented, never zero-filled

## Common Pitfalls

- Ignoring heterogeneity across entities
- Using pooled OLS when FE is appropriate
- Drawing causal conclusions from cross-sectional variation alone
