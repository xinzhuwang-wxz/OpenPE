"""
Step 3.3: Refutation Tests for All Causal Edges.

Three refutation tests per edge:
1. Placebo treatment (shift timing)
2. Random common cause
3. Data subset stability

Applies to full-analysis edges (DE->SUB, DEMO->LS) and moderate edges (DE->CRE).
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

df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Helper: Toda-Yamamoto test (reuse from step1 but simplified)
# ---------------------------------------------------------------------------
def ty_granger(data_df, cause_col, effect_col, control_cols=None):
    """Quick Toda-Yamamoto test, returns W statistic and p-value."""
    cols = [cause_col, effect_col]
    if control_cols:
        cols = cols + control_cols

    sub = data_df[cols].dropna()
    T = len(sub)
    n_vars = len(cols)
    d_max = 1
    p_opt = 1  # Fixed for consistency in refutation

    total_lag = p_opt + d_max
    try:
        var_model = VAR(sub.values)
        var_result = var_model.fit(maxlags=total_lag, trend="c")
    except Exception:
        return None, None

    nobs = var_result.nobs
    effect_idx = 1
    cause_idx = 0

    # Build X manually for Wald test
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
def placebo_timing_test(data_df, cause_col, effect_col, control_cols=None,
                        original_W=None, n_placebos=50):
    """
    Shift the cause variable by various lags (2-5 years back) and re-test.
    Under H0 (no real causation), placebo should produce similar statistics.
    """
    log.info(f"  Placebo timing test: {cause_col} -> {effect_col}")
    placebo_results = []

    for shift in range(2, 6):
        df_placebo = data_df.copy()
        # Shift cause variable forward (use lagged values as "placebo treatment")
        df_placebo[f"{cause_col}_placebo"] = df_placebo[cause_col].shift(shift)

        W, p = ty_granger(df_placebo, f"{cause_col}_placebo", effect_col, control_cols)
        if W is not None:
            placebo_results.append({"shift": shift, "W": W, "p": p})
            log.info(f"    Shift={shift}: W={W:.3f}, p={p:.4f}")

    if not placebo_results:
        return {"verdict": "INCONCLUSIVE", "details": "No valid placebo runs"}

    # PASS if most placebos are non-significant (p > 0.10)
    n_sig = sum(1 for r in placebo_results if r["p"] < 0.10)
    n_total = len(placebo_results)

    if n_sig <= 1:
        verdict = "PASS"
    else:
        verdict = "FAIL"

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
def random_common_cause_test(data_df, cause_col, effect_col, original_W=None,
                             n_random=100):
    """
    Add a random variable as control. If estimate changes >10%, model is fragile.
    """
    log.info(f"  Random common cause test: {cause_col} -> {effect_col}")

    # Original without random
    W_orig, p_orig = ty_granger(data_df, cause_col, effect_col)
    if W_orig is None:
        return {"verdict": "INCONCLUSIVE", "details": "Original test failed"}

    W_with_random = []
    for i in range(n_random):
        df_rcc = data_df.copy()
        df_rcc["random_var"] = np.random.randn(len(df_rcc))
        W, p = ty_granger(df_rcc, cause_col, effect_col, control_cols=["random_var"])
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

    log.info(f"    Original W={W_orig:.3f}, Mean W with random={W_mean:.3f}, change={change_pct:.1f}%")
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
    """
    Randomly drop 25% of observations and re-test. Result should be stable.
    """
    log.info(f"  Data subset test: {cause_col} -> {effect_col} (drop {drop_frac*100:.0f}%)")

    W_orig, p_orig = ty_granger(data_df, cause_col, effect_col, control_cols)
    if W_orig is None:
        return {"verdict": "INCONCLUSIVE", "details": "Original test failed"}

    W_subsets = []
    p_subsets = []

    n_drop = max(1, int(len(data_df) * drop_frac))

    for i in range(n_subsets):
        # Random drop (maintain time ordering -- drop random years)
        drop_idx = np.random.choice(len(data_df), size=n_drop, replace=False)
        df_sub = data_df.drop(data_df.index[drop_idx]).reset_index(drop=True)

        if len(df_sub) < 15:  # Need minimum obs
            continue

        W, p = ty_granger(df_sub, cause_col, effect_col, control_cols)
        if W is not None:
            W_subsets.append(W)
            p_subsets.append(p)

    if len(W_subsets) < 10:
        return {"verdict": "INCONCLUSIVE", "details": f"Only {len(W_subsets)} valid subset runs"}

    W_mean = np.mean(W_subsets)
    change_pct = abs(W_mean - W_orig) / max(abs(W_orig), 1e-10) * 100

    # Also check: if original was significant, what fraction of subsets remain significant?
    if p_orig < 0.10:
        frac_sig = np.mean(np.array(p_subsets) < 0.10)
    else:
        frac_sig = np.mean(np.array(p_subsets) >= 0.10)  # fraction consistent with null

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
# Run refutation battery for each edge
# ---------------------------------------------------------------------------
edges = [
    {
        "label": "DE -> substitution (industry emp)",
        "cause": "digital_economy_index",
        "effect": "employment_industry_pct",
        "controls": None,
        "level": "full",
    },
    {
        "label": "DE -> creation (services emp)",
        "cause": "digital_economy_index",
        "effect": "employment_services_pct",
        "controls": None,
        "level": "moderate",
    },
    {
        "label": "DE -> mediation (services VA)",
        "cause": "digital_economy_index",
        "effect": "services_value_added_pct_gdp",
        "controls": None,
        "level": "lightweight",
    },
    {
        "label": "DEMO -> services emp (confounder)",
        "cause": "population_15_64_pct",
        "effect": "employment_services_pct",
        "controls": None,
        "level": "full",
    },
    {
        "label": "DEMO -> industry emp (confounder)",
        "cause": "population_15_64_pct",
        "effect": "employment_industry_pct",
        "controls": None,
        "level": "full",
    },
    # WITH controls
    {
        "label": "DE -> substitution (with demo ctrl)",
        "cause": "digital_economy_index",
        "effect": "employment_industry_pct",
        "controls": ["population_15_64_pct"],
        "level": "full",
    },
    {
        "label": "DE -> creation (with demo ctrl)",
        "cause": "digital_economy_index",
        "effect": "employment_services_pct",
        "controls": ["population_15_64_pct"],
        "level": "moderate",
    },
]

all_refutation_results = []

for edge in edges:
    log.info(f"\n{'='*60}")
    log.info(f"REFUTATION BATTERY: {edge['label']}")
    log.info(f"{'='*60}")

    # Get original test statistic
    W_orig, p_orig = ty_granger(df, edge["cause"], edge["effect"], edge.get("controls"))
    log.info(f"  Original: W={W_orig:.3f}, p={p_orig:.4f}" if W_orig else "  Original: FAILED")

    # Run three refutation tests
    r1 = placebo_timing_test(df, edge["cause"], edge["effect"], edge.get("controls"),
                             original_W=W_orig)
    r2 = random_common_cause_test(df, edge["cause"], edge["effect"], original_W=W_orig)
    r3 = data_subset_test(df, edge["cause"], edge["effect"], edge.get("controls"))

    # Count passes
    verdicts = [r1["verdict"], r2["verdict"], r3["verdict"]]
    n_pass = sum(1 for v in verdicts if v == "PASS")
    n_marginal = sum(1 for v in verdicts if v == "MARGINAL")

    # Classification
    if n_pass >= 3:
        classification = "DATA_SUPPORTED"
    elif n_pass >= 2:
        classification = "CORRELATION"
    elif n_pass >= 1:
        classification = "HYPOTHESIZED"
    else:
        classification = "DISPUTED"

    # Special case: if original test was non-significant, cap at CORRELATION
    if W_orig is not None and p_orig >= 0.10:
        if classification == "DATA_SUPPORTED":
            classification = "CORRELATION"
            log.info("  Note: Downgraded from DATA_SUPPORTED because original test non-significant (p>=0.10)")

    log.info(f"\n  CLASSIFICATION: {classification}")
    log.info(f"  Refutation: {n_pass}/3 PASS, {n_marginal}/3 MARGINAL")
    log.info(f"  Original test: W={W_orig}, p={p_orig}")

    edge_result = {
        "label": edge["label"],
        "cause": edge["cause"],
        "effect": edge["effect"],
        "controls": edge.get("controls"),
        "level": edge["level"],
        "original_W": float(W_orig) if W_orig else None,
        "original_p": float(p_orig) if p_orig else None,
        "placebo": r1,
        "random_cause": r2,
        "data_subset": r3,
        "n_pass": n_pass,
        "classification": classification,
    }
    all_refutation_results.append(edge_result)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
log.info(f"\n{'='*60}")
log.info("REFUTATION SUMMARY")
log.info(f"{'='*60}")

for r in all_refutation_results:
    log.info(f"  {r['label']:40s} | {r['classification']:18s} | "
             f"Placebo={r['placebo']['verdict']} | "
             f"RCC={r['random_cause']['verdict']} | "
             f"Subset={r['data_subset']['verdict']}")

# Save
output_path = "phase3_analysis/scripts/refutation_results.json"
with open(output_path, "w") as f:
    json.dump(all_refutation_results, f, indent=2,
              default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else x)
log.info(f"\nResults saved to {output_path}")
