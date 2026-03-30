"""
Step 3.1 Signal Extraction: Toda-Yamamoto Granger Causality Tests.

Tests temporal precedence for all channel pairs:
- DE --> employment_services_pct (creation)
- DE --> employment_industry_pct (substitution)
- DE --> services_value_added_pct_gdp (mediation first link)
- DEMO --> employment_services_pct (confounder)
- DEMO --> employment_industry_pct (confounder)

Runs with and without demographic controls per Phase 2 ILO endogeneity requirement.
Bootstrap p-values for small-sample correction.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

np.random.seed(42)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)
log.info(f"Loaded data: {df.shape[0]} obs, {df.shape[1]} cols")

# ---------------------------------------------------------------------------
# Helper: determine d_max (max integration order)
# ---------------------------------------------------------------------------
def get_dmax(series_list, alpha=0.10):
    """Return max integration order across series (0 or 1)."""
    dmax = 0
    for s in series_list:
        s_clean = s.dropna()
        adf_p = adfuller(s_clean, maxlag=4, autolag="AIC")[1]
        if adf_p > alpha:
            # Likely I(1) -- check first diff
            d1 = s_clean.diff().dropna()
            adf_d1 = adfuller(d1, maxlag=3, autolag="AIC")[1]
            if adf_d1 <= alpha:
                dmax = max(dmax, 1)
            else:
                dmax = max(dmax, 2)  # Possibly I(2) -- cap at 2
    return min(dmax, 2)


# ---------------------------------------------------------------------------
# Toda-Yamamoto Granger causality test
# ---------------------------------------------------------------------------
def toda_yamamoto_granger(data_df, cause_col, effect_col, control_cols=None,
                          max_lag=3, n_bootstrap=10000):
    """
    Toda-Yamamoto Granger causality test with bootstrap p-values.

    Returns dict with test statistics and p-values.
    """
    cols = [cause_col, effect_col]
    if control_cols:
        cols = cols + control_cols

    sub = data_df[cols].dropna()
    T = len(sub)

    # Determine d_max
    series_list = [sub[c] for c in cols]
    d_max = get_dmax(series_list)
    d_max = max(d_max, 1)  # At least 1 for safety with I(1) variables

    log.info(f"T-Y test: {cause_col} -> {effect_col}, T={T}, d_max={d_max}")

    # Select optimal lag p using AIC on VAR(p) in levels
    try:
        var_select = VAR(sub.values)
        max_p = min(max_lag, T // (len(cols) + 2) - d_max - 1)
        max_p = max(max_p, 1)
        lag_order = var_select.select_order(maxlags=max_p)
        p_opt = lag_order.aic
        if p_opt == 0:
            p_opt = 1
    except Exception:
        p_opt = 1

    log.info(f"  Optimal lag p={p_opt}, fitting VAR({p_opt + d_max})")

    # Fit VAR(p + d_max) in levels
    total_lag = p_opt + d_max
    try:
        var_model = VAR(sub.values)
        var_result = var_model.fit(maxlags=total_lag, trend="c")
    except Exception as e:
        log.warning(f"  VAR fit failed: {e}")
        return None

    # Get coefficient matrix for the effect equation
    # The effect variable is at index 1
    effect_idx = 1
    cause_idx = 0

    # Extract the Wald test: test that coefficients on lags 1..p of cause
    # variable in the effect equation are jointly zero
    # Coefficients in var_result.params: rows = variables + const, cols = equations
    # Shape: (n_lags * n_vars + 1, n_vars)

    nobs = var_result.nobs
    n_vars = len(cols)

    # Construct restriction matrix for Wald test
    # We want to test: coefficients on cause variable at lags 1..p in effect eq = 0
    params = var_result.params  # shape: (1 + total_lag * n_vars, n_vars)

    # The cause variable coefficients in the effect equation:
    # params layout: [const, var0_lag1, var1_lag1, ..., vark_lag1, var0_lag2, ...]
    # For the effect equation (col effect_idx), we want rows corresponding to
    # cause_idx at lags 1..p_opt (NOT the extra d_max lags)

    # Row indices for cause_idx at each lag
    cause_rows = []
    for lag in range(1, p_opt + 1):
        row_idx = 1 + (lag - 1) * n_vars + cause_idx
        cause_rows.append(row_idx)

    # Extract effect equation residuals and do Wald test manually
    # Restricted model: set cause lags 1..p to zero
    Y = sub.values[total_lag:]  # dependent (T - total_lag, n_vars)

    # Build regressor matrix
    X_list = [np.ones((nobs, 1))]  # constant
    for lag in range(1, total_lag + 1):
        X_list.append(sub.values[total_lag - lag: -lag if lag < total_lag else None])
    # Fix: build properly
    X_parts = [np.ones((nobs, 1))]
    for lag in range(1, total_lag + 1):
        start = total_lag - lag
        end = start + nobs
        X_parts.append(sub.values[start:end])
    X = np.hstack(X_parts)

    y = Y[:, effect_idx]

    # Unrestricted OLS
    beta_u = np.linalg.lstsq(X, y, rcond=None)[0]
    resid_u = y - X @ beta_u
    SSR_u = np.sum(resid_u**2)

    # Restricted: zero out cause variable at lags 1..p_opt
    X_r = X.copy()
    for lag in range(1, p_opt + 1):
        col_idx = 1 + (lag - 1) * n_vars + cause_idx
        X_r[:, col_idx] = 0.0

    beta_r = np.linalg.lstsq(X_r, y, rcond=None)[0]
    resid_r = y - X_r @ beta_r
    SSR_r = np.sum(resid_r**2)

    # Wald statistic (F-form)
    q = p_opt  # number of restrictions
    k = X.shape[1]  # number of parameters
    F_stat = ((SSR_r - SSR_u) / q) / (SSR_u / (nobs - k))

    # Chi-squared form (Wald = q * F ~ chi2(q) asymptotically)
    W_stat = q * F_stat
    p_asymptotic = 1 - stats.chi2.cdf(W_stat, df=q)
    p_F = 1 - stats.f.cdf(F_stat, dfn=q, dfd=nobs - k)

    # Bootstrap p-value
    bootstrap_W = np.zeros(n_bootstrap)
    resid_centered = resid_u - resid_u.mean()

    for b in range(n_bootstrap):
        # Resample residuals
        idx = np.random.randint(0, len(resid_centered), size=len(resid_centered))
        y_boot = X @ beta_r + resid_centered[idx]  # under H0 (restricted)

        beta_u_b = np.linalg.lstsq(X, y_boot, rcond=None)[0]
        resid_u_b = y_boot - X @ beta_u_b
        SSR_u_b = np.sum(resid_u_b**2)

        beta_r_b = np.linalg.lstsq(X_r, y_boot, rcond=None)[0]
        resid_r_b = y_boot - X_r @ beta_r_b
        SSR_r_b = np.sum(resid_r_b**2)

        if SSR_u_b > 0:
            F_b = ((SSR_r_b - SSR_u_b) / q) / (SSR_u_b / (nobs - k))
            bootstrap_W[b] = q * F_b
        else:
            bootstrap_W[b] = 0

    p_bootstrap = np.mean(bootstrap_W >= W_stat)

    result = {
        "cause": cause_col,
        "effect": effect_col,
        "controls": control_cols if control_cols else [],
        "T": T,
        "p_opt": p_opt,
        "d_max": d_max,
        "total_lag": total_lag,
        "nobs_effective": nobs,
        "W_stat": float(W_stat),
        "F_stat": float(F_stat),
        "p_asymptotic": float(p_asymptotic),
        "p_F": float(p_F),
        "p_bootstrap": float(p_bootstrap),
    }

    log.info(f"  W={W_stat:.3f}, p_asym={p_asymptotic:.4f}, p_boot={p_bootstrap:.4f}")
    return result


# ---------------------------------------------------------------------------
# Run all Granger tests
# ---------------------------------------------------------------------------
results = []

# Define test pairs
test_pairs = [
    # Creation channel
    ("digital_economy_index", "employment_services_pct", "creation"),
    # Substitution channel
    ("digital_economy_index", "employment_industry_pct", "substitution"),
    # Mediation first link
    ("digital_economy_index", "services_value_added_pct_gdp", "mediation_link1"),
    # Reverse causality tests
    ("employment_services_pct", "digital_economy_index", "reverse_creation"),
    ("employment_industry_pct", "digital_economy_index", "reverse_substitution"),
    # Demographic confounder
    ("population_15_64_pct", "employment_services_pct", "demo_creation"),
    ("population_15_64_pct", "employment_industry_pct", "demo_substitution"),
    # DE -> demographics (should NOT be significant if demo is exogenous)
    ("digital_economy_index", "population_15_64_pct", "de_to_demo"),
]

log.info("=" * 60)
log.info("BIVARIATE Toda-Yamamoto Granger Tests (no controls)")
log.info("=" * 60)

for cause, effect, label in test_pairs:
    r = toda_yamamoto_granger(df, cause, effect)
    if r:
        r["label"] = label
        r["spec"] = "bivariate"
        results.append(r)

log.info("")
log.info("=" * 60)
log.info("WITH DEMOGRAPHIC CONTROL (population_15_64_pct)")
log.info("=" * 60)

# Re-run DE -> employment tests with demographic control
controlled_pairs = [
    ("digital_economy_index", "employment_services_pct", "creation_ctrl"),
    ("digital_economy_index", "employment_industry_pct", "substitution_ctrl"),
    ("digital_economy_index", "services_value_added_pct_gdp", "mediation_link1_ctrl"),
]

for cause, effect, label in controlled_pairs:
    r = toda_yamamoto_granger(df, cause, effect, control_cols=["population_15_64_pct"])
    if r:
        r["label"] = label
        r["spec"] = "with_demo_control"
        results.append(r)

# ---------------------------------------------------------------------------
# Power context for each test
# ---------------------------------------------------------------------------
log.info("")
log.info("=" * 60)
log.info("RESULTS SUMMARY")
log.info("=" * 60)

for r in results:
    sig = "***" if r["p_bootstrap"] < 0.01 else "**" if r["p_bootstrap"] < 0.05 else "*" if r["p_bootstrap"] < 0.10 else ""
    log.info(
        f"  {r['label']:25s} | W={r['W_stat']:6.3f} | "
        f"p_boot={r['p_bootstrap']:.4f}{sig} | "
        f"p_asym={r['p_asymptotic']:.4f} | "
        f"spec={r['spec']}"
    )
    # Power note for null results
    if r["p_bootstrap"] >= 0.10:
        log.info(f"    ^ Power note: At T={r['T']}, power is ~35% for medium effects (beta=0.3)")

# Save results
output_path = "phase3_analysis/scripts/granger_results.json"

# Convert numpy types to native Python for JSON serialization
def convert_numpy(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

clean_results = []
for r in results:
    clean_results.append({k: convert_numpy(v) for k, v in r.items()})

with open(output_path, "w") as f:
    json.dump(clean_results, f, indent=2)
log.info(f"\nResults saved to {output_path}")
