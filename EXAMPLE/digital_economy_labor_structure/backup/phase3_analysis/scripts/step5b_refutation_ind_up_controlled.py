"""
A-1 Fix: Run refutation battery on the CONTROLLED (trivariate) specification
for DE-->IND_UP (DE + demographics -> services_value_added_pct_gdp).

The original step5 only tested the bivariate specification. The controlled
specification (W=15.81, p=0.008) is the one used for inference, so it must
be the one refuted.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.api import VAR
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
# Toda-Yamamoto test (same implementation as step5, supports controls)
# ---------------------------------------------------------------------------
def ty_granger(data_df, cause_col, effect_col, control_cols=None):
    """Toda-Yamamoto test, returns W statistic and p-value.

    Uses p_opt=2, d_max=1 to match the specification from step1 that
    produced the W=15.81 result for the controlled DE-->IND_UP test.
    """
    cols = [cause_col, effect_col]
    if control_cols:
        cols = cols + control_cols

    sub = data_df[cols].dropna()
    T = len(sub)
    n_vars = len(cols)
    d_max = 1
    p_opt = 2  # Match step1 AIC-selected lag order for this specification

    total_lag = p_opt + d_max
    try:
        var_model = VAR(sub.values)
        var_result = var_model.fit(maxlags=total_lag, trend="c")
    except Exception:
        return None, None

    nobs = var_result.nobs
    effect_idx = 1
    cause_idx = 0

    Y = sub.values[total_lag:]
    X_parts = [np.ones((nobs, 1))]
    for lag in range(1, total_lag + 1):
        start = total_lag - lag
        end = start + nobs
        X_parts.append(sub.values[start:end])
    X = np.hstack(X_parts)
    y = Y[:, effect_idx]

    beta_u = np.linalg.lstsq(X, y, rcond=None)[0]
    resid_u = y - X @ beta_u
    SSR_u = np.sum(resid_u**2)

    X_r = X.copy()
    for lag in range(1, p_opt + 1):
        col_idx = 1 + (lag - 1) * n_vars + cause_idx
        X_r[:, col_idx] = 0.0

    beta_r = np.linalg.lstsq(X_r, y, rcond=None)[0]
    resid_r = y - X_r @ beta_r
    SSR_r = np.sum(resid_r**2)

    q = p_opt
    k = X.shape[1]
    F_stat = ((SSR_r - SSR_u) / q) / (SSR_u / (nobs - k))
    W_stat = q * F_stat
    p_val = 1 - stats.chi2.cdf(W_stat, df=q)

    return float(W_stat), float(p_val)


# ---------------------------------------------------------------------------
# Refutation 1: Placebo Treatment (Time Shift)
# ---------------------------------------------------------------------------
def placebo_timing_test(data_df, cause_col, effect_col, control_cols=None):
    """Shift the cause variable by 2-5 years and re-test."""
    log.info(f"  Placebo timing test: {cause_col} -> {effect_col} (controls={control_cols})")
    placebo_results = []

    for shift in range(2, 6):
        df_placebo = data_df.copy()
        df_placebo[f"{cause_col}_placebo"] = df_placebo[cause_col].shift(shift)

        W, p = ty_granger(df_placebo, f"{cause_col}_placebo", effect_col, control_cols)
        if W is not None:
            placebo_results.append({"shift": shift, "W": W, "p": p})
            log.info(f"    Shift={shift}: W={W:.3f}, p={p:.4f}")

    if not placebo_results:
        return {"verdict": "INCONCLUSIVE", "details": "No valid placebo runs"}

    n_sig = sum(1 for r in placebo_results if r["p"] < 0.10)
    n_total = len(placebo_results)

    verdict = "PASS" if n_sig <= 1 else "FAIL"
    log.info(f"    Placebo verdict: {verdict} ({n_sig}/{n_total} significant)")
    return {
        "verdict": verdict,
        "n_significant": n_sig,
        "n_total": n_total,
        "placebo_runs": placebo_results,
    }


# ---------------------------------------------------------------------------
# Refutation 2: Random Common Cause
# ---------------------------------------------------------------------------
def random_common_cause_test(data_df, cause_col, effect_col, control_cols=None,
                             n_random=100):
    """Add a random variable as additional control. If W changes >10%, fragile."""
    log.info(f"  Random common cause test: {cause_col} -> {effect_col} (controls={control_cols})")

    # Original WITH existing controls
    W_orig, p_orig = ty_granger(data_df, cause_col, effect_col, control_cols)
    if W_orig is None:
        return {"verdict": "INCONCLUSIVE", "details": "Original test failed"}

    log.info(f"    Original W={W_orig:.3f}, p={p_orig:.4f}")

    W_with_random = []
    base_controls = control_cols if control_cols else []
    for i in range(n_random):
        df_rcc = data_df.copy()
        df_rcc["random_var"] = np.random.randn(len(df_rcc))
        W, p = ty_granger(df_rcc, cause_col, effect_col,
                          control_cols=base_controls + ["random_var"])
        if W is not None:
            W_with_random.append(W)

    if not W_with_random:
        return {"verdict": "INCONCLUSIVE", "details": "No valid random cause runs"}

    W_mean = np.mean(W_with_random)
    change_pct = abs(W_mean - W_orig) / max(abs(W_orig), 1e-10) * 100

    if change_pct <= 10:
        verdict = "PASS"
    elif change_pct <= 20:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    log.info(f"    Mean W with random={W_mean:.3f}, change={change_pct:.1f}%")
    log.info(f"    Random common cause verdict: {verdict}")

    return {
        "verdict": verdict,
        "W_original": W_orig,
        "W_mean_random": float(W_mean),
        "W_std_random": float(np.std(W_with_random)),
        "change_pct": float(change_pct),
    }


# ---------------------------------------------------------------------------
# Refutation 3: Data Subset Stability
# ---------------------------------------------------------------------------
def data_subset_test(data_df, cause_col, effect_col, control_cols=None,
                     n_subsets=100, drop_frac=0.25):
    """Randomly drop 25% and re-test."""
    log.info(f"  Data subset test: {cause_col} -> {effect_col} (controls={control_cols})")

    W_orig, p_orig = ty_granger(data_df, cause_col, effect_col, control_cols)
    if W_orig is None:
        return {"verdict": "INCONCLUSIVE", "details": "Original test failed"}

    W_subsets = []
    p_subsets = []
    n_drop = max(1, int(len(data_df) * drop_frac))

    for i in range(n_subsets):
        drop_idx = np.random.choice(len(data_df), size=n_drop, replace=False)
        df_sub = data_df.drop(data_df.index[drop_idx]).reset_index(drop=True)

        if len(df_sub) < 15:
            continue

        W, p = ty_granger(df_sub, cause_col, effect_col, control_cols)
        if W is not None:
            W_subsets.append(W)
            p_subsets.append(p)

    if len(W_subsets) < 10:
        return {"verdict": "INCONCLUSIVE", "details": f"Only {len(W_subsets)} valid subset runs"}

    W_mean = np.mean(W_subsets)
    change_pct = abs(W_mean - W_orig) / max(abs(W_orig), 1e-10) * 100

    if p_orig < 0.10:
        frac_sig = np.mean(np.array(p_subsets) < 0.10)
    else:
        frac_sig = np.mean(np.array(p_subsets) >= 0.10)

    if change_pct <= 20 and frac_sig >= 0.5:
        verdict = "PASS"
    elif change_pct <= 30:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    log.info(f"    Original W={W_orig:.3f} (p={p_orig:.4f})")
    log.info(f"    Subset mean W={W_mean:.3f}, change={change_pct:.1f}%")
    log.info(f"    Consistency fraction: {frac_sig:.2f}")
    log.info(f"    Data subset verdict: {verdict}")

    return {
        "verdict": verdict,
        "W_original": float(W_orig),
        "p_original": float(p_orig),
        "W_mean_subset": float(W_mean),
        "W_std_subset": float(np.std(W_subsets)),
        "change_pct": float(change_pct),
        "consistency_fraction": float(frac_sig),
        "n_valid_subsets": len(W_subsets),
    }


# ---------------------------------------------------------------------------
# Run refutation battery on CONTROLLED specification
# ---------------------------------------------------------------------------
log.info("=" * 60)
log.info("REFUTATION: DE -> IND_UP (with demographic control)")
log.info("=" * 60)

cause_col = "digital_economy_index"
effect_col = "services_value_added_pct_gdp"
control_cols = ["population_15_64_pct"]

# Verify original result
W_orig, p_orig = ty_granger(df, cause_col, effect_col, control_cols)
log.info(f"Original controlled result: W={W_orig:.3f}, p={p_orig:.4f}")

# Run three refutation tests
r1 = placebo_timing_test(df, cause_col, effect_col, control_cols)
r2 = random_common_cause_test(df, cause_col, effect_col, control_cols)
r3 = data_subset_test(df, cause_col, effect_col, control_cols)

verdicts = [r1["verdict"], r2["verdict"], r3["verdict"]]
n_pass = sum(1 for v in verdicts if v == "PASS")
n_marginal = sum(1 for v in verdicts if v == "MARGINAL")

if n_pass >= 3:
    classification = "DATA_SUPPORTED"
elif n_pass >= 2:
    classification = "CORRELATION"
elif n_pass >= 1:
    classification = "HYPOTHESIZED"
else:
    classification = "DISPUTED"

log.info(f"\nCLASSIFICATION: {classification}")
log.info(f"Refutation: {n_pass}/3 PASS, {n_marginal}/3 MARGINAL")

result = {
    "label": "DE -> IND_UP (controlled, with demographic)",
    "cause": cause_col,
    "effect": effect_col,
    "controls": control_cols,
    "original_W": float(W_orig) if W_orig else None,
    "original_p": float(p_orig) if p_orig else None,
    "placebo": r1,
    "random_cause": r2,
    "data_subset": r3,
    "n_pass": n_pass,
    "n_marginal": n_marginal,
    "classification": classification,
}

output_path = "phase3_analysis/scripts/refutation_ind_up_controlled.json"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2,
              default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else x)
log.info(f"\nResults saved to {output_path}")
