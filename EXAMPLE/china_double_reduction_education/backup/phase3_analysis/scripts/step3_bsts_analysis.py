"""
Step 3: BSTS Counterfactual Analysis.

Using statsmodels UnobservedComponents (local linear trend + regression on income).
Pre-treatment: 2016-2019 (excluding 2020).
Post-treatment: 2021-2025.
Feasibility gate: if pre-treatment fit is poor, downgrade to sensitivity.

Produces: phase3_analysis/figures/fig_p3_05_*.pdf/png
"""
import json
import logging
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.statespace.structural import UnobservedComponents

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": "medium",
    "axes.titlesize": "medium",
    "xtick.labelsize": "small",
    "ytick.labelsize": "small",
    "legend.fontsize": "small",
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

np.random.seed(42)

DATA_DIR = "phase3_analysis/data"
FIG_DIR = "phase3_analysis/figures"

os.makedirs(FIG_DIR, exist_ok=True)

# ---- Load ----
df = pd.read_parquet(f"{DATA_DIR}/analysis_dataset.parquet")

# Exclude 2020
df_no_covid = df[df["year"] != 2020].copy().reset_index(drop=True)
log.info(f"Dataset (excl 2020): {df_no_covid.shape}")

series_configs = [
    ("national", "real_national", "real_income_national"),
    ("urban", "real_urban", "real_income_urban"),
    ("rural", "real_rural", "real_income_rural"),
]

bsts_results = {}


def run_bsts_counterfactual(data, outcome_col, covariate_col, intervention_year):
    """
    Run a local linear trend model with exogenous regressor.
    Pre-period: years < intervention_year.
    Post-period: years >= intervention_year.
    Counterfactual = model predictions in post-period using pre-period parameters.
    """
    pre = data[data["year"] < intervention_year].copy()
    post = data[data["year"] >= intervention_year].copy()
    full = data.copy()

    n_pre = len(pre)
    n_post = len(post)
    log.info(f"  Pre-treatment: {n_pre} obs, Post-treatment: {n_post} obs")

    if n_pre < 3:
        log.warning("  Insufficient pre-treatment observations for BSTS")
        return None

    # Fit structural time series on pre-period
    y_pre = pre[outcome_col].values
    x_pre = pre[covariate_col].values.reshape(-1, 1)

    y_full = full[outcome_col].values
    x_full = full[covariate_col].values.reshape(-1, 1)

    # Method 1: Simple approach -- fit linear model on pre-period, predict post
    # Using OLS with income as predictor for simplicity given n=4
    X_pre = sm.add_constant(x_pre)
    X_full = sm.add_constant(x_full)

    ols_model = sm.OLS(y_pre, X_pre).fit()
    log.info(f"  Pre-period OLS R-squared: {ols_model.rsquared:.4f}")

    # Counterfactual for all years
    counterfactual_all = ols_model.predict(X_full)

    # Prediction intervals (using prediction SE)
    pred_se = np.sqrt(ols_model.mse_resid * (1 + np.diag(X_full @ np.linalg.inv(X_pre.T @ X_pre) @ X_full.T)))

    # Post-period effect
    post_idx = full["year"] >= intervention_year
    observed_post = y_full[post_idx]
    cf_post = counterfactual_all[post_idx]
    effect_post = observed_post - cf_post

    mean_effect = effect_post.mean()
    cumulative_effect = effect_post.sum()

    # Pre-period fit quality (MAPE)
    pre_fitted = ols_model.fittedvalues
    pre_actual = y_pre
    mape = np.mean(np.abs((pre_actual - pre_fitted) / pre_actual)) * 100
    log.info(f"  Pre-period MAPE: {mape:.2f}%")

    # Method 2: try unobserved components if enough data
    uc_result = None
    try:
        # Local level model with regression
        mod = UnobservedComponents(
            y_pre,
            level="local level",
            exog=x_pre,
        )
        res = mod.fit(disp=False)

        # Forecast post-period
        x_post = post[covariate_col].values.reshape(-1, 1)
        forecast = res.get_forecast(steps=n_post, exog=x_post)
        fc_mean = forecast.predicted_mean
        fc_ci = forecast.conf_int(alpha=0.10)

        uc_effect = post[outcome_col].values - fc_mean
        uc_result = {
            "forecast_mean": fc_mean.tolist(),
            "forecast_ci_lo": fc_ci.iloc[:, 0].tolist(),
            "forecast_ci_hi": fc_ci.iloc[:, 1].tolist(),
            "effect": uc_effect.tolist(),
            "mean_effect": float(np.mean(uc_effect)),
        }
        log.info(f"  UC model mean post-period effect: {np.mean(uc_effect):.1f}")
    except Exception as e:
        log.warning(f"  Unobserved Components model failed: {e}")

    # Feasibility gate
    feasible = mape < 10.0  # Less than 10% MAPE in pre-period
    log.info(f"  Feasibility: {'PASS' if feasible else 'FAIL (poor pre-period fit)'}")

    # Bootstrap uncertainty for OLS counterfactual
    n_boot = 1000
    boot_effects = []
    for _ in range(n_boot):
        idx = np.random.choice(n_pre, n_pre, replace=True)
        try:
            b_model = sm.OLS(y_pre[idx], X_pre[idx]).fit()
            b_cf = b_model.predict(X_full[post_idx])
            b_effect = (observed_post - b_cf).mean()
            boot_effects.append(b_effect)
        except Exception:
            pass

    boot_effects = np.array(boot_effects)
    boot_ci_90 = [float(np.percentile(boot_effects, 5)), float(np.percentile(boot_effects, 95))]
    boot_se = float(np.std(boot_effects))

    return {
        "feasible": feasible,
        "pre_mape": float(mape),
        "pre_r_squared": float(ols_model.rsquared),
        "mean_effect": float(mean_effect),
        "cumulative_effect": float(cumulative_effect),
        "post_effects": effect_post.tolist(),
        "counterfactual": counterfactual_all.tolist(),
        "observed": y_full.tolist(),
        "years": full["year"].tolist(),
        "pred_se": pred_se.tolist(),
        "boot_se": boot_se,
        "boot_ci_90": boot_ci_90,
        "n_pre": n_pre,
        "n_post": n_post,
        "uc_result": uc_result,
        "pre_policy_mean": float(np.mean(y_pre)),
        "effect_pct": float(mean_effect / np.mean(y_pre) * 100),
    }


for label, outcome_col, covariate_col in series_configs:
    log.info(f"\n=== BSTS Counterfactual: {label} ===")
    res = run_bsts_counterfactual(df_no_covid, outcome_col, covariate_col, intervention_year=2021)
    bsts_results[label] = res

    if res:
        log.info(f"Mean post-period effect: {res['mean_effect']:.1f} yuan ({res['effect_pct']:.1f}%)")
        log.info(f"Bootstrap 90% CI: [{res['boot_ci_90'][0]:.1f}, {res['boot_ci_90'][1]:.1f}]")


# ==== Figure: BSTS counterfactual ====
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, (label, outcome_col, _) in enumerate(series_configs):
    ax = axes[i]
    res = bsts_results[label]
    if res is None:
        ax.text(0.5, 0.5, "BSTS infeasible", transform=ax.transAxes, ha="center", va="center")
        continue

    years = res["years"]
    observed = res["observed"]
    counterfactual = res["counterfactual"]
    pred_se = res["pred_se"]

    ax.plot(years, observed, "ko-", linewidth=2, markersize=6, label="Observed")
    ax.plot(years, counterfactual, "r--", linewidth=2, label="Income-predicted\ncounterfactual")

    cf_lo = [c - 1.645 * s for c, s in zip(counterfactual, pred_se)]
    cf_hi = [c + 1.645 * s for c, s in zip(counterfactual, pred_se)]
    ax.fill_between(years, cf_lo, cf_hi, alpha=0.15, color="red", label="90% PI")

    ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.5)

    # Shade effect in post-period
    post_mask = [y >= 2021 for y in years]
    post_years = [y for y, m in zip(years, post_mask) if m]
    post_obs = [o for o, m in zip(observed, post_mask) if m]
    post_cf = [c for c, m in zip(counterfactual, post_mask) if m]
    ax.fill_between(post_years, post_obs, post_cf, alpha=0.2, color="blue")

    ax.set_xlabel("Year")
    ax.set_ylabel("Real spending [2015 yuan]")
    ax.legend(fontsize="x-small", loc="upper left")

    feasible_str = "Feasible" if res["feasible"] else "INFEASIBLE"
    ax.text(0.98, 0.02,
            f"Mean effect: {res['mean_effect']:+.0f}\n"
            f"({res['effect_pct']:+.1f}%)\n"
            f"90% CI: [{res['boot_ci_90'][0]:.0f}, {res['boot_ci_90'][1]:.0f}]\n"
            f"Pre-fit: {feasible_str}",
            transform=ax.transAxes, fontsize=8, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    subtitle_map = {"national": "(a) National", "urban": "(b) Urban", "rural": "(c) Rural"}
    ax.text(0.02, 0.98, subtitle_map[label], transform=ax.transAxes, fontsize=10,
            va="top", ha="left", fontweight="bold")

axes[0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0].transAxes, fontsize=8,
             va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_05_bsts_counterfactual.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_05_bsts_counterfactual.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved BSTS figure to {FIG_DIR}/fig_p3_05_bsts_counterfactual.pdf")

# Save results
bsts_json = {}
for label in ["national", "urban", "rural"]:
    r = bsts_results[label]
    if r:
        bsts_json[label] = {
            "feasible": bool(r["feasible"]),
            "pre_mape": float(r["pre_mape"]),
            "pre_r_squared": float(r["pre_r_squared"]),
            "mean_effect": float(r["mean_effect"]),
            "effect_pct": float(r["effect_pct"]),
            "boot_se": float(r["boot_se"]),
            "boot_ci_90": [float(x) for x in r["boot_ci_90"]],
            "cumulative_effect": float(r["cumulative_effect"]),
            "n_pre": int(r["n_pre"]),
            "n_post": int(r["n_post"]),
        }

with open(f"{DATA_DIR}/bsts_results.json", "w") as f:
    json.dump(bsts_json, f, indent=2)

log.info(f"Saved BSTS results to {DATA_DIR}/bsts_results.json")
log.info("\nStep 3 (BSTS Analysis) complete.")
