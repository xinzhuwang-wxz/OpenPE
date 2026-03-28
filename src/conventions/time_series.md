# Time Series Conventions

> **When this applies:** Any analysis involving temporal data, forecasting,
> trend analysis, or time-dependent causal claims.

## Required Methodology

- Test for stationarity before modeling (ADF test, KPSS test)
- Report autocorrelation structure (ACF/PACF plots)
- Use appropriate models: ARIMA for stationary, cointegration for
  non-stationary, VAR for multivariate
- Granger causality requires sufficient time series length (>=30 observations)

## Forecasting Requirements

- Always report prediction intervals, not point forecasts
- Use out-of-sample validation (train/test split on temporal boundary)
- S-curve fitting must include bootstrap confidence intervals for parameters

## Common Pitfalls

- Spurious regression between trending series
- Confusing Granger causality with true causality
- Extrapolating S-curves beyond the data support region
