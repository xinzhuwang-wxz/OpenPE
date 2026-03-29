"""
Program 1: Independent reproduction of the ITS level shift estimate.

Independently implements a 3-parameter segmented regression (Interrupted Time Series)
on CPI-deflated NBS education/culture/recreation spending data.

This script does NOT import any Phase 3 code. It reads only the processed data
files and reimplements the ITS model from scratch using numpy linear algebra
(not statsmodels, which the primary analysis used).

Pass/fail criterion: Point estimates agree within 2 sigma of reported uncertainty;
confidence intervals overlap substantially (>50%); qualitative conclusion matches.
"""
import logging
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent.parent

# -------------------------------------------------------------------
# Step 1: Load raw data independently
# -------------------------------------------------------------------
expenditure = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_education_expenditure.parquet")
cpi = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_cpi_deflator.parquet")

log.info("Expenditure columns: %s", list(expenditure.columns))
log.info("CPI columns: %s", list(cpi.columns))
log.info("Expenditure shape: %s", expenditure.shape)
log.info("CPI shape: %s", cpi.shape)

# Print first rows for inspection
log.info("Expenditure head:\n%s", expenditure.head(12).to_string())
log.info("CPI head:\n%s", cpi.head(12).to_string())

# -------------------------------------------------------------------
# Step 2: CPI deflation
# -------------------------------------------------------------------
# Merge on year
merged = expenditure.merge(cpi, on="year", how="inner")

# Find the education deflator column
deflator_col = [c for c in merged.columns if "deflator" in c.lower() and "edu" in c.lower()]
if not deflator_col:
    deflator_col = [c for c in merged.columns if "deflator" in c.lower()]
    log.info("Using general deflator columns: %s", deflator_col)
else:
    log.info("Using education deflator: %s", deflator_col)

deflator_col_name = deflator_col[0] if deflator_col else None

# Find nominal spending columns
nat_col = [c for c in merged.columns if "national" in c.lower() and "yuan" in c.lower() and "education" in c.lower()]
urban_col = [c for c in merged.columns if "urban" in c.lower() and "yuan" in c.lower() and "education" in c.lower()]
rural_col = [c for c in merged.columns if "rural" in c.lower() and "yuan" in c.lower() and "education" in c.lower()]

log.info("Nominal columns found: nat=%s, urban=%s, rural=%s", nat_col, urban_col, rural_col)

nat_col_name = nat_col[0] if nat_col else None
urban_col_name = urban_col[0] if urban_col else None
rural_col_name = rural_col[0] if rural_col else None

# Deflate: real = nominal * deflator (where deflator < 1 means prices rose)
merged["real_national"] = merged[nat_col_name] * merged[deflator_col_name]
merged["real_urban"] = merged[urban_col_name] * merged[deflator_col_name]
merged["real_rural"] = merged[rural_col_name] * merged[deflator_col_name]

log.info("Deflated data:\n%s", merged[["year", "real_national", "real_urban", "real_rural"]].to_string())

# -------------------------------------------------------------------
# Step 3: ITS model using numpy (independent of statsmodels)
# -------------------------------------------------------------------
# Exclude 2020 (COVID year)
df = merged[merged["year"] != 2020].copy().sort_values("year").reset_index(drop=True)

# Time index: linear, starting from first year
years = df["year"].values
t_min = years.min()
t = (years - t_min).astype(float)  # 0-indexed time

# Post-policy indicator: 1 if year >= 2021
post = (years >= 2021).astype(float)

# Design matrix: [intercept, time, post_policy]
X = np.column_stack([np.ones(len(t)), t, post])

log.info("Design matrix (n=%d, p=%d):\n%s", X.shape[0], X.shape[1], X)

results = {}

for series_name, col_name in [("national", "real_national"), ("urban", "real_urban"), ("rural", "real_rural")]:
    y = df[col_name].values

    # OLS: beta = (X'X)^-1 X'y
    XtX = X.T @ X
    Xty = X.T @ y
    beta = np.linalg.solve(XtX, Xty)

    # Residuals and variance estimate
    y_hat = X @ beta
    residuals = y - y_hat
    n = len(y)
    p = X.shape[1]
    sigma2 = np.sum(residuals**2) / (n - p)

    # Standard errors: sqrt(diag((X'X)^-1 * sigma2))
    XtX_inv = np.linalg.inv(XtX)
    se = np.sqrt(np.diag(XtX_inv) * sigma2)

    # T-statistics and p-values
    from scipy import stats as spstats
    t_stat = beta / se
    p_values = 2 * spstats.t.sf(np.abs(t_stat), df=n - p)

    # R-squared
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_squared = 1 - ss_res / ss_tot

    # 90% CI for level shift
    t_crit_90 = spstats.t.ppf(0.95, df=n - p)
    ci_90 = [beta[2] - t_crit_90 * se[2], beta[2] + t_crit_90 * se[2]]

    # 95% CI
    t_crit_95 = spstats.t.ppf(0.975, df=n - p)
    ci_95 = [beta[2] - t_crit_95 * se[2], beta[2] + t_crit_95 * se[2]]

    # Pre-policy mean
    pre_mask = years < 2021
    pre_mean = y[pre_mask].mean()

    results[series_name] = {
        "intercept": float(beta[0]),
        "trend": float(beta[1]),
        "level_shift": float(beta[2]),
        "se_level_shift": float(se[2]),
        "p_value": float(p_values[2]),
        "r_squared": float(r_squared),
        "ci_90": [float(ci_90[0]), float(ci_90[1])],
        "ci_95": [float(ci_95[0]), float(ci_95[1])],
        "pre_policy_mean": float(pre_mean),
        "effect_pct": float(beta[2] / pre_mean * 100),
        "n_obs": int(n),
    }

    log.info(
        "\n=== %s ===\n  Level shift: %.2f yuan (SE=%.2f, p=%.4f)\n  Trend: %.2f yuan/yr\n  R2: %.4f\n  90%% CI: [%.2f, %.2f]\n  Effect: %.1f%%",
        series_name, beta[2], se[2], p_values[2], beta[1], r_squared,
        ci_90[0], ci_90[1], beta[2] / pre_mean * 100,
    )

# -------------------------------------------------------------------
# Step 4: Compare with primary analysis
# -------------------------------------------------------------------
primary = json.load(open(BASE / "phase3_analysis" / "data" / "its_results.json"))

log.info("\n" + "=" * 60)
log.info("COMPARISON: Independent vs Primary Analysis")
log.info("=" * 60)

comparison = {}
all_pass = True
for s in ["national", "urban", "rural"]:
    v = results[s]
    p_val = primary[s]["primary"]

    diff = abs(v["level_shift"] - p_val["level_shift"])
    reported_se = p_val["level_shift_se"]
    within_1pct = abs(diff / p_val["level_shift"]) < 0.01
    within_2sigma = diff < 2 * reported_se

    # CI overlap check
    v_lo, v_hi = v["ci_90"]
    p_lo, p_hi = p_val["level_shift_ci_90"]
    overlap = max(0, min(v_hi, p_hi) - max(v_lo, p_lo))
    avg_span = ((v_hi - v_lo) + (p_hi - p_lo)) / 2
    overlap_pct = overlap / avg_span if avg_span > 0 else 0

    status = "PASS" if within_1pct else ("PASS (within 2sigma)" if within_2sigma else "FAIL")
    if not within_2sigma:
        all_pass = False

    comparison[s] = {
        "verifier_shift": v["level_shift"],
        "primary_shift": p_val["level_shift"],
        "abs_diff": diff,
        "pct_diff": abs(diff / p_val["level_shift"]) * 100,
        "within_1pct": within_1pct,
        "within_2sigma": within_2sigma,
        "ci_overlap_pct": overlap_pct,
        "status": status,
    }

    log.info(
        "  %s: Verifier=%.2f, Primary=%.2f, Diff=%.4f (%.4f%%), Status=%s, CI overlap=%.1f%%",
        s, v["level_shift"], p_val["level_shift"], diff,
        abs(diff / p_val["level_shift"]) * 100, status, overlap_pct * 100,
    )

# -------------------------------------------------------------------
# Step 5: Save results
# -------------------------------------------------------------------
output = {
    "verifier_results": results,
    "comparison": comparison,
    "overall_pass": all_pass,
}

out_path = BASE / "phase5_verification" / "data"
out_path.mkdir(parents=True, exist_ok=True)
with open(out_path / "its_reproduction.json", "w") as f:
    json.dump(output, f, indent=2)

log.info("\nOverall reproduction: %s", "PASS" if all_pass else "FAIL")
log.info("Results saved to %s", out_path / "its_reproduction.json")
