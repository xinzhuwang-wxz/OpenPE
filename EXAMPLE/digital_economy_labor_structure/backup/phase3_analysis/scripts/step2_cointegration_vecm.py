"""
Step 3.2 Baseline Estimation: Johansen Cointegration + VECM + ARDL bounds.

Tests long-run equilibrium for:
- DE <-> employment_services_pct (creation)
- DE <-> employment_industry_pct (substitution)
- DE <-> services_value_added_pct_gdp (mediation)

If cointegrated: estimate VECM with error correction speed and long-run coefficients.
If not cointegrated: ARDL bounds test as secondary.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
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

df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)

# ---------------------------------------------------------------------------
# Johansen cointegration tests
# ---------------------------------------------------------------------------
def run_johansen(data_df, cols, det_order=0, k_ar_diff=1):
    """Run Johansen cointegration test."""
    sub = data_df[cols].dropna()
    log.info(f"Johansen test: {cols}, T={len(sub)}, k_ar_diff={k_ar_diff}")

    try:
        result = coint_johansen(sub.values, det_order=det_order, k_ar_diff=k_ar_diff)
    except Exception as e:
        log.warning(f"  Johansen failed: {e}")
        return None

    # Trace test
    trace_stats = result.lr1
    trace_cv_90 = result.cvt[:, 0]
    trace_cv_95 = result.cvt[:, 1]
    trace_cv_99 = result.cvt[:, 2]

    # Max eigenvalue test
    max_stats = result.lr2
    max_cv_90 = result.cvm[:, 0]
    max_cv_95 = result.cvm[:, 1]
    max_cv_99 = result.cvm[:, 2]

    log.info("  Trace test:")
    for i in range(len(cols)):
        sig = "***" if trace_stats[i] > trace_cv_99[i] else "**" if trace_stats[i] > trace_cv_95[i] else "*" if trace_stats[i] > trace_cv_90[i] else ""
        log.info(f"    r<={i}: stat={trace_stats[i]:.3f}, cv90={trace_cv_90[i]:.3f}, cv95={trace_cv_95[i]:.3f} {sig}")

    log.info("  Max-eigenvalue test:")
    for i in range(len(cols)):
        sig = "***" if max_stats[i] > max_cv_99[i] else "**" if max_stats[i] > max_cv_95[i] else "*" if max_stats[i] > max_cv_90[i] else ""
        log.info(f"    r<={i}: stat={max_stats[i]:.3f}, cv90={max_cv_90[i]:.3f}, cv95={max_cv_95[i]:.3f} {sig}")

    # Determine cointegration rank
    rank_trace = 0
    for i in range(len(cols)):
        if trace_stats[i] > trace_cv_95[i]:
            rank_trace = len(cols) - i
            break

    rank_max = 0
    for i in range(len(cols)):
        if max_stats[i] > max_cv_95[i]:
            rank_max = len(cols) - i
            break

    log.info(f"  Rank (trace): {rank_trace}, Rank (max-eigen): {rank_max}")

    return {
        "variables": cols,
        "T": len(sub),
        "k_ar_diff": k_ar_diff,
        "trace_stats": trace_stats.tolist(),
        "trace_cv95": trace_cv_95.tolist(),
        "max_stats": max_stats.tolist(),
        "max_cv95": max_cv_95.tolist(),
        "rank_trace": int(rank_trace),
        "rank_max": int(rank_max),
        "eigenvectors": result.evec.tolist(),
    }


# ---------------------------------------------------------------------------
# VECM estimation
# ---------------------------------------------------------------------------
def run_vecm(data_df, cols, coint_rank=1, k_ar_diff=1):
    """Estimate VECM if cointegrated."""
    sub = data_df[cols].dropna()
    log.info(f"VECM estimation: {cols}, rank={coint_rank}, k_ar_diff={k_ar_diff}")

    try:
        model = VECM(sub.values, k_ar_diff=k_ar_diff, coint_rank=coint_rank,
                      deterministic="ci")
        result = model.fit()
    except Exception as e:
        log.warning(f"  VECM fit failed: {e}")
        return None

    # Cointegrating vector (alpha * beta')
    log.info(f"  Cointegrating vector (beta): {result.beta.flatten()}")
    log.info(f"  Adjustment coefficients (alpha): {result.alpha.flatten()}")

    # Long-run relationship: beta normalized on first variable
    beta = result.beta.flatten()
    if abs(beta[0]) > 1e-10:
        beta_norm = beta / beta[0]
    else:
        beta_norm = beta

    log.info(f"  Normalized cointegrating vector: {beta_norm}")

    # Error correction speeds
    alpha = result.alpha.flatten()
    for i, col in enumerate(cols):
        log.info(f"  Alpha[{col}] = {alpha[i]:.4f} (speed of adjustment)")

    return {
        "variables": cols,
        "coint_rank": coint_rank,
        "beta": result.beta.tolist(),
        "beta_normalized": beta_norm.tolist(),
        "alpha": alpha.tolist(),
        "k_ar_diff": k_ar_diff,
        "col_names": cols,
    }


# ---------------------------------------------------------------------------
# ARDL bounds test (Pesaran et al. 2001 -- simplified F-test version)
# ---------------------------------------------------------------------------
def ardl_bounds_test(data_df, dep_col, indep_cols, max_lag=2):
    """
    ARDL bounds test for cointegration.
    Tests H0: no long-run relationship.

    Uses the F-test on lagged levels in an error-correction form:
    dy_t = c + sum(phi_i * dy_{t-i}) + sum(theta_j * dx_{t-j}) + pi_y * y_{t-1} + pi_x * x_{t-1} + e_t

    F-test on pi_y = pi_x = 0.
    """
    all_cols = [dep_col] + indep_cols
    sub = data_df[all_cols].dropna()
    T = len(sub)

    log.info(f"ARDL bounds test: {dep_col} ~ {indep_cols}, T={T}")

    # First differences
    dsub = sub.diff().dropna()

    # Build regressor matrix
    # Dependent: d(dep_col)
    y = dsub[dep_col].values[max_lag:]
    nobs = len(y)

    X_parts = [np.ones((nobs, 1))]  # constant

    # Lagged first differences
    for lag in range(1, max_lag + 1):
        for col in all_cols:
            vals = dsub[col].values[max_lag - lag: max_lag - lag + nobs]
            X_parts.append(vals.reshape(-1, 1))

    # Lagged levels (the terms we test)
    level_parts = []
    for col in all_cols:
        vals = sub[col].values[max_lag: max_lag + nobs]
        level_parts.append(vals.reshape(-1, 1))

    X_unrestricted = np.hstack(X_parts + level_parts)
    X_restricted = np.hstack(X_parts)  # without lagged levels

    # OLS both
    beta_u = np.linalg.lstsq(X_unrestricted, y, rcond=None)[0]
    resid_u = y - X_unrestricted @ beta_u
    SSR_u = np.sum(resid_u**2)

    beta_r = np.linalg.lstsq(X_restricted, y, rcond=None)[0]
    resid_r = y - X_restricted @ beta_r
    SSR_r = np.sum(resid_r**2)

    q = len(all_cols)  # number of restricted params (lagged levels)
    k_u = X_unrestricted.shape[1]

    F_stat = ((SSR_r - SSR_u) / q) / (SSR_u / (nobs - k_u))

    # Pesaran bounds critical values (approximate for k=1 regressor, case III)
    # These are from Pesaran et al. (2001) Table CI(iii)
    k = len(indep_cols)
    if k == 1:
        # 10%: I(0)=4.04, I(1)=4.78; 5%: I(0)=4.94, I(1)=5.73
        bounds = {"10_I0": 4.04, "10_I1": 4.78, "5_I0": 4.94, "5_I1": 5.73}
    elif k == 2:
        bounds = {"10_I0": 3.17, "10_I1": 4.14, "5_I0": 3.79, "5_I1": 4.85}
    else:
        bounds = {"10_I0": 2.72, "10_I1": 3.77, "5_I0": 3.23, "5_I1": 4.35}

    if F_stat > bounds["5_I1"]:
        conclusion = "COINTEGRATED (F > upper bound at 5%)"
    elif F_stat > bounds["10_I1"]:
        conclusion = "COINTEGRATED (F > upper bound at 10%)"
    elif F_stat < bounds["10_I0"]:
        conclusion = "NO COINTEGRATION (F < lower bound at 10%)"
    elif F_stat < bounds["5_I0"]:
        conclusion = "INCONCLUSIVE (between bounds at 5%)"
    else:
        conclusion = "INCONCLUSIVE"

    log.info(f"  F-stat = {F_stat:.3f}, bounds(5%): [{bounds['5_I0']:.2f}, {bounds['5_I1']:.2f}]")
    log.info(f"  Conclusion: {conclusion}")

    return {
        "dep": dep_col,
        "indep": indep_cols,
        "T": T,
        "nobs": nobs,
        "F_stat": float(F_stat),
        "bounds_5pct": [bounds["5_I0"], bounds["5_I1"]],
        "bounds_10pct": [bounds["10_I0"], bounds["10_I1"]],
        "conclusion": conclusion,
    }


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------
all_results = {"johansen": [], "vecm": [], "ardl": []}

test_systems = [
    {
        "label": "creation",
        "cols": ["digital_economy_index", "employment_services_pct"],
        "dep": "employment_services_pct",
        "indep": ["digital_economy_index"],
    },
    {
        "label": "substitution",
        "cols": ["digital_economy_index", "employment_industry_pct"],
        "dep": "employment_industry_pct",
        "indep": ["digital_economy_index"],
    },
    {
        "label": "mediation_link1",
        "cols": ["digital_economy_index", "services_value_added_pct_gdp"],
        "dep": "services_value_added_pct_gdp",
        "indep": ["digital_economy_index"],
    },
    {
        "label": "creation_with_demo",
        "cols": ["digital_economy_index", "employment_services_pct", "population_15_64_pct"],
        "dep": "employment_services_pct",
        "indep": ["digital_economy_index", "population_15_64_pct"],
    },
    {
        "label": "substitution_with_demo",
        "cols": ["digital_economy_index", "employment_industry_pct", "population_15_64_pct"],
        "dep": "employment_industry_pct",
        "indep": ["digital_economy_index", "population_15_64_pct"],
    },
]

for system in test_systems:
    log.info(f"\n{'='*60}")
    log.info(f"System: {system['label']}")
    log.info(f"{'='*60}")

    # Johansen
    joh = run_johansen(df, system["cols"], det_order=0, k_ar_diff=1)
    if joh:
        joh["label"] = system["label"]
        all_results["johansen"].append(joh)

        # If cointegrated, run VECM
        rank = max(joh["rank_trace"], joh["rank_max"])
        if rank > 0:
            vecm = run_vecm(df, system["cols"], coint_rank=min(rank, len(system["cols"]) - 1), k_ar_diff=1)
            if vecm:
                vecm["label"] = system["label"]
                all_results["vecm"].append(vecm)

    # ARDL
    ardl = ardl_bounds_test(df, system["dep"], system["indep"], max_lag=2)
    if ardl:
        ardl["label"] = system["label"]
        all_results["ardl"].append(ardl)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
log.info(f"\n{'='*60}")
log.info("COINTEGRATION SUMMARY")
log.info(f"{'='*60}")

for joh in all_results["johansen"]:
    log.info(f"  {joh['label']:30s} | trace_rank={joh['rank_trace']}, max_rank={joh['rank_max']}")

log.info("")
for ardl in all_results["ardl"]:
    log.info(f"  {ardl['label']:30s} | F={ardl['F_stat']:.3f} | {ardl['conclusion']}")

# Save
output_path = "phase3_analysis/scripts/cointegration_results.json"
with open(output_path, "w") as f:
    json.dump(all_results, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else x)
log.info(f"\nResults saved to {output_path}")
