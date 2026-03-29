"""
Step 2: Primary ITS Analysis -- 3-parameter segmented regression.

Model: Y_t = beta_0 + beta_1 * time + beta_2 * post_policy + epsilon_t
- Primary specification: exclude 2020
- Sensitivity: include 2020 with COVID indicator
- Run on national, urban, rural separately
- Permutation-based inference (all possible intervention year assignments)

Produces: phase3_analysis/figures/fig_p3_02_*.pdf/png
"""
import json
import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler
from scipy import stats
import statsmodels.api as sm

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

np.random.seed(42)

DATA_DIR = "phase3_analysis/data"
FIG_DIR = "phase3_analysis/figures"
OUT_DIR = "phase3_analysis/data"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ---- Load ----
df = pd.read_parquet(f"{DATA_DIR}/analysis_dataset.parquet")
log.info(f"Loaded analysis dataset: {df.shape}")


def run_its_model(data, outcome_col, intervention_year, exclude_years=None, covid_indicator=False):
    """
    Run 3-parameter ITS: Y = b0 + b1*time + b2*post_policy + e
    Returns dict with coefficients, CIs, p-values, residuals, predictions.
    """
    d = data.copy()
    if exclude_years:
        d = d[~d["year"].isin(exclude_years)].reset_index(drop=True)

    # Build design matrix
    d["time"] = d["year"] - d["year"].min()
    d["post"] = (d["year"] >= intervention_year).astype(int)

    exog_cols = ["time", "post"]
    if covid_indicator:
        d["covid"] = (d["year"] == 2020).astype(int)
        exog_cols.append("covid")

    X = sm.add_constant(d[exog_cols])
    y = d[outcome_col]

    model = sm.OLS(y, X).fit()

    # Counterfactual: what would have happened without intervention
    d_cf = d.copy()
    d_cf["post"] = 0
    if covid_indicator:
        d_cf["covid"] = 0
    X_cf = sm.add_constant(d_cf[exog_cols])
    counterfactual = model.predict(X_cf)

    return {
        "model": model,
        "data": d,
        "outcome_col": outcome_col,
        "level_shift": model.params["post"],
        "level_shift_se": model.bse["post"],
        "level_shift_pvalue": model.pvalues["post"],
        "level_shift_ci_90": model.conf_int(alpha=0.10).loc["post"].tolist(),
        "level_shift_ci_95": model.conf_int(alpha=0.05).loc["post"].tolist(),
        "trend": model.params["time"],
        "intercept": model.params["const"],
        "r_squared": model.rsquared,
        "df_resid": model.df_resid,
        "fitted": model.fittedvalues.values,
        "counterfactual": counterfactual.values,
        "residuals": model.resid.values,
        "years": d["year"].values,
        "observed": y.values,
        "n_obs": len(d),
        "summary": model.summary().as_text(),
    }


def permutation_test(data, outcome_col, true_intervention_year, exclude_years=None,
                     candidate_years=None):
    """
    Exhaustive permutation test: try all possible intervention years.
    Returns distribution of level-shift coefficients under permutation.
    """
    if candidate_years is None:
        candidate_years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

    results = {}
    for yr in candidate_years:
        try:
            res = run_its_model(data, outcome_col, yr, exclude_years=exclude_years)
            results[yr] = {
                "level_shift": res["level_shift"],
                "level_shift_se": res["level_shift_se"],
                "level_shift_pvalue": res["level_shift_pvalue"],
            }
        except Exception as e:
            log.warning(f"Permutation at year {yr} failed: {e}")
            results[yr] = {"level_shift": np.nan, "level_shift_se": np.nan, "level_shift_pvalue": np.nan}

    return results


# ==== Run primary analysis: national, urban, rural ====
series_configs = [
    ("national", "real_national"),
    ("urban", "real_urban"),
    ("rural", "real_rural"),
]

all_results = {}

for label, col in series_configs:
    log.info(f"\n=== ITS Analysis: {label} ===")

    # Primary: exclude 2020
    res_primary = run_its_model(df, col, intervention_year=2021, exclude_years=[2020])
    log.info(f"[Primary, excl 2020] Level shift: {res_primary['level_shift']:.1f} "
             f"(SE={res_primary['level_shift_se']:.1f}, p={res_primary['level_shift_pvalue']:.4f})")
    log.info(f"  90% CI: [{res_primary['level_shift_ci_90'][0]:.1f}, {res_primary['level_shift_ci_90'][1]:.1f}]")
    log.info(f"  Pre-policy trend: {res_primary['trend']:.1f} yuan/year")
    log.info(f"  R-squared: {res_primary['r_squared']:.4f}")
    log.info(f"  df_resid: {res_primary['df_resid']}")

    # Sensitivity: include 2020 with COVID indicator
    res_covid = run_its_model(df, col, intervention_year=2021, covid_indicator=True)
    log.info(f"[Sensitivity, COVID indicator] Level shift: {res_covid['level_shift']:.1f} "
             f"(SE={res_covid['level_shift_se']:.1f}, p={res_covid['level_shift_pvalue']:.4f})")
    log.info(f"  90% CI: [{res_covid['level_shift_ci_90'][0]:.1f}, {res_covid['level_shift_ci_90'][1]:.1f}]")

    # Permutation test
    log.info(f"Running permutation test for {label}...")
    perm = permutation_test(df, col, true_intervention_year=2021,
                            exclude_years=[2020],
                            candidate_years=[2017, 2018, 2019, 2021, 2022, 2023, 2024])

    # Calculate permutation p-value
    true_shift = res_primary["level_shift"]
    perm_shifts = [v["level_shift"] for v in perm.values() if not np.isnan(v["level_shift"])]
    perm_pvalue = np.mean([abs(s) >= abs(true_shift) for s in perm_shifts])
    log.info(f"Permutation p-value (all years): {perm_pvalue:.3f}")

    # Effect size relative to pre-policy mean
    pre_policy_mean = df[df["year"].isin([2016, 2017, 2018, 2019])][col].mean()
    effect_pct = (true_shift / pre_policy_mean) * 100
    log.info(f"Effect size: {effect_pct:.1f}% of pre-policy mean ({pre_policy_mean:.0f})")

    all_results[label] = {
        "primary": res_primary,
        "covid_sensitivity": res_covid,
        "permutation": perm,
        "perm_pvalue": perm_pvalue,
        "pre_policy_mean": pre_policy_mean,
        "effect_pct": effect_pct,
    }

# ==== Figure: ITS fit with counterfactual ====
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, (label, col) in enumerate(series_configs):
    ax = axes[i]
    res = all_results[label]["primary"]

    # Full dataset for reference
    ax.scatter(df["year"], df[col], color="black", s=60, zorder=5, label="Observed")

    # Mark excluded 2020
    mask_2020 = df["year"] == 2020
    ax.scatter(df.loc[mask_2020, "year"], df.loc[mask_2020, col],
               color="orange", s=60, zorder=6, marker="x", linewidths=2,
               label="Excluded (2020)")

    # Fitted values
    ax.plot(res["years"], res["fitted"], "b-", linewidth=2, label="ITS fit")

    # Counterfactual
    post_mask = res["years"] >= 2021
    cf_years = res["years"][post_mask]
    cf_vals = res["counterfactual"][post_mask]
    ax.plot(cf_years, cf_vals, "r--", linewidth=2, label="Counterfactual (no policy)")

    # Shade the gap
    obs_post = res["observed"][post_mask]
    ax.fill_between(cf_years, obs_post, cf_vals, alpha=0.15, color="blue")

    ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Real spending [2015 yuan]")
    ax.legend(fontsize="x-small", loc="upper left")

    shift = res["level_shift"]
    p = res["level_shift_pvalue"]
    ax.text(0.98, 0.02, f"Level shift: {shift:+.0f} yuan\n(p={p:.3f})",
            transform=ax.transAxes, fontsize=9, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    subtitle_map = {"national": "(a) National", "urban": "(b) Urban", "rural": "(c) Rural"}
    ax.text(0.02, 0.98, subtitle_map[label], transform=ax.transAxes, fontsize=10,
            va="top", ha="left", fontweight="bold")

axes[0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0].transAxes, fontsize=8,
             va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_02_its_primary.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_02_its_primary.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved ITS figure to {FIG_DIR}/fig_p3_02_its_primary.pdf")


# ==== Figure: Permutation test distribution ====
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, (label, col) in enumerate(series_configs):
    ax = axes[i]
    perm = all_results[label]["permutation"]
    true_shift = all_results[label]["primary"]["level_shift"]

    years_sorted = sorted(perm.keys())
    shifts = [perm[yr]["level_shift"] for yr in years_sorted]

    colors = ["#F44336" if yr == 2021 else "#2196F3" for yr in years_sorted]
    bars = ax.bar(years_sorted, shifts, color=colors, edgecolor="black", linewidth=0.5)

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Intervention year [tested]")
    ax.set_ylabel("Level shift [2015 yuan]")

    subtitle_map = {"national": "(a) National", "urban": "(b) Urban", "rural": "(c) Rural"}
    ax.text(0.02, 0.98, subtitle_map[label], transform=ax.transAxes, fontsize=10,
            va="top", ha="left", fontweight="bold")

    perm_p = all_results[label]["perm_pvalue"]
    ax.text(0.98, 0.02, f"Perm. p={perm_p:.2f}",
            transform=ax.transAxes, fontsize=9, va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

axes[0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0].transAxes, fontsize=8,
             va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_03_permutation_test.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_03_permutation_test.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved permutation test figure to {FIG_DIR}/fig_p3_03_permutation_test.pdf")


# ==== Figure: ITS primary vs sensitivity comparison ====
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for i, (label, col) in enumerate(series_configs):
    ax = axes[i]
    r1 = all_results[label]["primary"]
    r2 = all_results[label]["covid_sensitivity"]

    shifts = [r1["level_shift"], r2["level_shift"]]
    ci_lo = [r1["level_shift_ci_90"][0], r2["level_shift_ci_90"][0]]
    ci_hi = [r1["level_shift_ci_90"][1], r2["level_shift_ci_90"][1]]
    errs = [[s - lo for s, lo in zip(shifts, ci_lo)],
            [hi - s for s, hi in zip(shifts, ci_hi)]]

    x_pos = [0, 1]
    labels_spec = ["Excl. 2020\n(primary)", "COVID ind.\n(sensitivity)"]
    ax.errorbar(x_pos, shifts, yerr=errs, fmt="o", capsize=6, markersize=8,
                color="#2196F3", ecolor="black", linewidth=2)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels_spec)
    ax.set_ylabel("Level shift [2015 yuan]")

    subtitle_map = {"national": "(a) National", "urban": "(b) Urban", "rural": "(c) Rural"}
    ax.text(0.02, 0.98, subtitle_map[label], transform=ax.transAxes, fontsize=10,
            va="top", ha="left", fontweight="bold")

axes[0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0].transAxes, fontsize=8,
             va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_04_its_comparison.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_04_its_comparison.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)

# ==== Save results as JSON ====
results_json = {}
for label in ["national", "urban", "rural"]:
    r = all_results[label]
    results_json[label] = {
        "primary": {
            "level_shift": float(r["primary"]["level_shift"]),
            "level_shift_se": float(r["primary"]["level_shift_se"]),
            "level_shift_pvalue": float(r["primary"]["level_shift_pvalue"]),
            "level_shift_ci_90": [float(x) for x in r["primary"]["level_shift_ci_90"]],
            "level_shift_ci_95": [float(x) for x in r["primary"]["level_shift_ci_95"]],
            "trend": float(r["primary"]["trend"]),
            "r_squared": float(r["primary"]["r_squared"]),
            "df_resid": int(r["primary"]["df_resid"]),
            "n_obs": int(r["primary"]["n_obs"]),
        },
        "covid_sensitivity": {
            "level_shift": float(r["covid_sensitivity"]["level_shift"]),
            "level_shift_se": float(r["covid_sensitivity"]["level_shift_se"]),
            "level_shift_pvalue": float(r["covid_sensitivity"]["level_shift_pvalue"]),
            "level_shift_ci_90": [float(x) for x in r["covid_sensitivity"]["level_shift_ci_90"]],
        },
        "permutation_pvalue": float(r["perm_pvalue"]),
        "pre_policy_mean": float(r["pre_policy_mean"]),
        "effect_pct": float(r["effect_pct"]),
    }

with open(f"{OUT_DIR}/its_results.json", "w") as f:
    json.dump(results_json, f, indent=2)

log.info(f"\nSaved ITS results to {OUT_DIR}/its_results.json")
log.info("\nStep 2 (ITS Analysis) complete.")
