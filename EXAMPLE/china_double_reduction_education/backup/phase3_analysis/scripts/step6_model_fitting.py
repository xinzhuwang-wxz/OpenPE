"""
Step 6: Statistical Model Fitting -- Formal ITS with bootstrap CIs,
sensitivity analysis, model diagnostics, and signal injection tests.

Produces:
  - phase3_analysis/data/step6_model_results.json
  - phase3_analysis/figures/fig_p3_09_diagnostics.pdf/png
  - phase3_analysis/figures/fig_p3_10_bootstrap.pdf/png
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
from statsmodels.stats.stattools import durbin_watson

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

os.makedirs(FIG_DIR, exist_ok=True)

# ---- Load ----
df = pd.read_parquet(f"{DATA_DIR}/analysis_dataset.parquet")
log.info(f"Loaded analysis dataset: {df.shape}")


# ===========================================================================
# Section 1: Formal ITS model specification
# ===========================================================================

def run_its(data, outcome_col, intervention_year, exclude_years=None):
    """
    3-parameter ITS: Y = b0 + b1*time + b2*post + e
    Returns full model results including residuals.
    """
    d = data.copy()
    if exclude_years:
        d = d[~d["year"].isin(exclude_years)].reset_index(drop=True)

    d["time"] = d["year"] - d["year"].min()
    d["post"] = (d["year"] >= intervention_year).astype(int)

    X = sm.add_constant(d[["time", "post"]])
    y = d[outcome_col]
    model = sm.OLS(y, X).fit()

    d_cf = d.copy()
    d_cf["post"] = 0
    X_cf = sm.add_constant(d_cf[["time", "post"]])
    counterfactual = model.predict(X_cf)

    return {
        "model": model,
        "data": d,
        "X": X,
        "y": y,
        "years": d["year"].values,
        "observed": y.values,
        "fitted": model.fittedvalues.values,
        "residuals": model.resid.values,
        "counterfactual": counterfactual.values,
        "level_shift": float(model.params["post"]),
        "level_shift_se": float(model.bse["post"]),
        "level_shift_pvalue": float(model.pvalues["post"]),
        "trend": float(model.params["time"]),
        "intercept": float(model.params["const"]),
        "r_squared": float(model.rsquared),
        "adj_r_squared": float(model.rsquared_adj),
        "df_resid": int(model.df_resid),
        "n_obs": len(d),
        "aic": float(model.aic),
        "bic": float(model.bic),
    }


# ===========================================================================
# Section 2: Residual Bootstrap (2000 replications)
# ===========================================================================

def residual_bootstrap(data, outcome_col, intervention_year, exclude_years=None,
                       n_boot=2000):
    """
    Residual bootstrap for ITS level-shift coefficient.
    1. Fit the model, get residuals.
    2. Resample residuals with replacement.
    3. Create pseudo-data: fitted + resampled residuals.
    4. Re-estimate model on pseudo-data.
    5. Collect level-shift coefficient from each replication.
    """
    base = run_its(data, outcome_col, intervention_year, exclude_years)
    fitted = base["fitted"]
    resids = base["residuals"]
    n = len(resids)

    boot_shifts = np.empty(n_boot)
    boot_trends = np.empty(n_boot)

    d = base["data"].copy()
    d["time"] = d["year"] - d["year"].min()
    d["post"] = (d["year"] >= intervention_year).astype(int)
    X = sm.add_constant(d[["time", "post"]])

    for b in range(n_boot):
        resampled_resids = np.random.choice(resids, size=n, replace=True)
        y_star = fitted + resampled_resids
        try:
            model_b = sm.OLS(y_star, X).fit()
            boot_shifts[b] = model_b.params["post"]
            boot_trends[b] = model_b.params["time"]
        except Exception:
            boot_shifts[b] = np.nan
            boot_trends[b] = np.nan

    valid = ~np.isnan(boot_shifts)
    shifts_valid = boot_shifts[valid]

    ci_68 = np.percentile(shifts_valid, [16, 84])
    ci_90 = np.percentile(shifts_valid, [5, 95])
    ci_95 = np.percentile(shifts_valid, [2.5, 97.5])

    return {
        "n_boot": n_boot,
        "n_valid": int(valid.sum()),
        "point_estimate": base["level_shift"],
        "boot_mean": float(np.mean(shifts_valid)),
        "boot_se": float(np.std(shifts_valid, ddof=1)),
        "ci_68": [float(ci_68[0]), float(ci_68[1])],
        "ci_90": [float(ci_90[0]), float(ci_90[1])],
        "ci_95": [float(ci_95[0]), float(ci_95[1])],
        "boot_shifts": shifts_valid,
        "boot_trends": boot_trends[valid],
        "base_result": base,
    }


# ===========================================================================
# Section 3: Run primary models + bootstrap for all series
# ===========================================================================

series_configs = [
    ("national", "real_national"),
    ("urban", "real_urban"),
    ("rural", "real_rural"),
]

all_results = {}

for label, col in series_configs:
    log.info(f"\n=== Step 6: {label} ===")

    # Primary model
    primary = run_its(df, col, 2021, exclude_years=[2020])
    log.info(f"Level shift: {primary['level_shift']:.1f} (SE={primary['level_shift_se']:.1f})")
    log.info(f"R-sq: {primary['r_squared']:.4f}, AIC: {primary['aic']:.1f}, BIC: {primary['bic']:.1f}")
    log.info(f"Durbin-Watson: {durbin_watson(primary['residuals']):.3f}")

    # Bootstrap
    log.info(f"Running residual bootstrap (2000 reps) for {label}...")
    boot = residual_bootstrap(df, col, 2021, exclude_years=[2020], n_boot=2000)
    log.info(f"Bootstrap SE: {boot['boot_se']:.1f}")
    log.info(f"Bootstrap 68% CI: [{boot['ci_68'][0]:.1f}, {boot['ci_68'][1]:.1f}]")
    log.info(f"Bootstrap 90% CI: [{boot['ci_90'][0]:.1f}, {boot['ci_90'][1]:.1f}]")
    log.info(f"Bootstrap 95% CI: [{boot['ci_95'][0]:.1f}, {boot['ci_95'][1]:.1f}]")

    all_results[label] = {
        "primary": primary,
        "bootstrap": boot,
    }


# ===========================================================================
# Section 4: Model diagnostics
# ===========================================================================

log.info("\n=== Model Diagnostics ===")

diagnostics = {}
for label, col in series_configs:
    primary = all_results[label]["primary"]
    resids = primary["residuals"]
    n = len(resids)

    dw = durbin_watson(resids)

    # Shapiro-Wilk normality test
    if n >= 3:
        sw_stat, sw_p = stats.shapiro(resids)
    else:
        sw_stat, sw_p = np.nan, np.nan

    # Breusch-Pagan heteroscedasticity (manual)
    resid_sq = resids ** 2
    X = primary["X"]
    try:
        bp_model = sm.OLS(resid_sq, X).fit()
        bp_f = bp_model.fvalue
        bp_p = bp_model.f_pvalue
    except Exception:
        bp_f, bp_p = np.nan, np.nan

    diagnostics[label] = {
        "durbin_watson": float(dw),
        "dw_interpretation": "No autocorrelation" if 1.5 < dw < 2.5 else "Possible autocorrelation",
        "shapiro_stat": float(sw_stat),
        "shapiro_p": float(sw_p),
        "shapiro_interpretation": "Normal" if sw_p > 0.05 else "Non-normal",
        "bp_f": float(bp_f) if not np.isnan(bp_f) else None,
        "bp_p": float(bp_p) if not np.isnan(bp_p) else None,
        "bp_interpretation": "Homoscedastic" if (not np.isnan(bp_p) and bp_p > 0.05) else "Possible heteroscedasticity",
        "residual_mean": float(np.mean(resids)),
        "residual_std": float(np.std(resids, ddof=1)),
        "max_abs_residual": float(np.max(np.abs(resids))),
    }

    log.info(f"{label}: DW={dw:.3f} ({diagnostics[label]['dw_interpretation']}), "
             f"Shapiro p={sw_p:.3f} ({diagnostics[label]['shapiro_interpretation']}), "
             f"BP p={bp_p:.3f} ({diagnostics[label]['bp_interpretation']})")


# ===========================================================================
# Section 5: Sensitivity analysis (intervention date, COVID handling)
# ===========================================================================

log.info("\n=== Sensitivity Analysis ===")

sensitivity = {}
for label, col in series_configs:
    sens = {}

    # Primary: intervention 2021, exclude 2020
    p = run_its(df, col, 2021, exclude_years=[2020])
    sens["primary_2021_excl2020"] = {
        "level_shift": p["level_shift"],
        "level_shift_se": p["level_shift_se"],
        "level_shift_pvalue": p["level_shift_pvalue"],
    }

    # Alternative intervention at 2022 (delayed effect)
    r2022 = run_its(df, col, 2022, exclude_years=[2020])
    sens["intervention_2022"] = {
        "level_shift": r2022["level_shift"],
        "level_shift_se": r2022["level_shift_se"],
        "level_shift_pvalue": r2022["level_shift_pvalue"],
    }

    # Include 2020 (no exclusion)
    r_incl = run_its(df, col, 2021)
    sens["include_2020"] = {
        "level_shift": r_incl["level_shift"],
        "level_shift_se": r_incl["level_shift_se"],
        "level_shift_pvalue": r_incl["level_shift_pvalue"],
    }

    # Include 2020 with COVID indicator (4-param model)
    d_covid = df.copy()
    d_covid = d_covid.copy()
    d_covid["time"] = d_covid["year"] - d_covid["year"].min()
    d_covid["post"] = (d_covid["year"] >= 2021).astype(int)
    d_covid["covid"] = (d_covid["year"] == 2020).astype(int)
    X_cov = sm.add_constant(d_covid[["time", "post", "covid"]])
    y_cov = d_covid[col]
    m_cov = sm.OLS(y_cov, X_cov).fit()
    sens["covid_indicator"] = {
        "level_shift": float(m_cov.params["post"]),
        "level_shift_se": float(m_cov.bse["post"]),
        "level_shift_pvalue": float(m_cov.pvalues["post"]),
    }

    # Pre-period restricted to 2018-2019 only (drop 2016-2017)
    df_short = df[df["year"].isin([2018, 2019, 2021, 2022, 2023, 2024, 2025])]
    try:
        r_short = run_its(df_short, col, 2021)
        sens["short_preperiod_2018_2019"] = {
            "level_shift": r_short["level_shift"],
            "level_shift_se": r_short["level_shift_se"],
            "level_shift_pvalue": r_short["level_shift_pvalue"],
        }
    except Exception as e:
        log.warning(f"Short pre-period failed for {label}: {e}")
        sens["short_preperiod_2018_2019"] = {
            "level_shift": None,
            "level_shift_se": None,
            "level_shift_pvalue": None,
        }

    sensitivity[label] = sens
    log.info(f"{label} sensitivity:")
    for spec_name, spec_res in sens.items():
        shift = spec_res["level_shift"]
        if shift is not None:
            log.info(f"  {spec_name}: shift={shift:.1f}, p={spec_res['level_shift_pvalue']:.4f}")
        else:
            log.info(f"  {spec_name}: FAILED")


# ===========================================================================
# Section 6: Signal injection tests
# ===========================================================================

log.info("\n=== Signal Injection Tests ===")

signal_injection = {}

for label, col in series_configs:
    primary = all_results[label]["primary"]
    observed_shift = primary["level_shift"]

    d = df.copy()
    d = d[~d["year"].isin([2020])].reset_index(drop=True)
    d["time"] = d["year"] - d["year"].min()
    d["post"] = (d["year"] >= 2021).astype(int)

    injections = {}

    for inject_label, inject_value in [
        ("observed_magnitude", observed_shift),
        ("double_magnitude", 2.0 * observed_shift),
        ("null_injection", 0.0),
    ]:
        # Create synthetic data: pre-trend only + injected shift
        y_base = primary["intercept"] + primary["trend"] * d["time"].values
        y_injected = y_base + inject_value * d["post"].values
        # Add noise from the residual distribution
        noise = np.random.normal(0, primary["residuals"].std(), size=len(d))
        y_synthetic = y_injected + noise

        X = sm.add_constant(d[["time", "post"]])
        model_inj = sm.OLS(y_synthetic, X).fit()
        recovered = float(model_inj.params["post"])
        recovered_se = float(model_inj.bse["post"])

        within_1sigma = abs(recovered - inject_value) <= recovered_se
        within_2sigma = abs(recovered - inject_value) <= 2 * recovered_se

        injections[inject_label] = {
            "injected": float(inject_value),
            "recovered": recovered,
            "recovered_se": recovered_se,
            "within_1sigma": bool(within_1sigma),
            "within_2sigma": bool(within_2sigma),
            "deviation_pct": float(abs(recovered - inject_value) / max(abs(inject_value), 1) * 100)
                if inject_value != 0 else float(abs(recovered)),
        }

        log.info(f"  {label}/{inject_label}: injected={inject_value:.1f}, "
                 f"recovered={recovered:.1f}+/-{recovered_se:.1f}, "
                 f"1sig={within_1sigma}, 2sig={within_2sigma}")

    signal_injection[label] = injections


# ===========================================================================
# Section 7: Effect size estimation
# ===========================================================================

log.info("\n=== Effect Size Estimation ===")

effect_sizes = {}

for label, col in series_configs:
    primary = all_results[label]["primary"]
    boot = all_results[label]["bootstrap"]

    pre_mean = float(df[df["year"].isin([2016, 2017, 2018, 2019])][col].mean())
    pre_std = float(df[df["year"].isin([2016, 2017, 2018, 2019])][col].std())
    post_mean = float(df[df["year"] >= 2021][col].mean())

    # Cohen's d using pre-policy variability
    if pre_std > 0:
        cohens_d = abs(primary["level_shift"]) / pre_std
    else:
        cohens_d = np.nan

    # Percentage effect
    pct_effect = primary["level_shift"] / pre_mean * 100

    # Bootstrap-based effect sizes
    boot_pct = boot["boot_shifts"] / pre_mean * 100

    effect_sizes[label] = {
        "level_shift_yuan": primary["level_shift"],
        "level_shift_boot_se": boot["boot_se"],
        "level_shift_boot_ci_68": boot["ci_68"],
        "level_shift_boot_ci_90": boot["ci_90"],
        "level_shift_boot_ci_95": boot["ci_95"],
        "pre_policy_mean": pre_mean,
        "pre_policy_std": pre_std,
        "post_policy_mean": post_mean,
        "pct_effect": float(pct_effect),
        "pct_effect_ci_95": [float(np.percentile(boot_pct, 2.5)),
                             float(np.percentile(boot_pct, 97.5))],
        "cohens_d": float(cohens_d),
    }

    log.info(f"{label}: shift={primary['level_shift']:.0f} yuan "
             f"({pct_effect:.1f}%), Cohen's d={cohens_d:.2f}, "
             f"boot 95% CI [{boot['ci_95'][0]:.0f}, {boot['ci_95'][1]:.0f}]")


# ===========================================================================
# Figure 1: Model diagnostics (residuals, Q-Q, autocorrelation)
# ===========================================================================

fig, axes = plt.subplots(3, 3, figsize=(18, 18))

for i, (label, col) in enumerate(series_configs):
    primary = all_results[label]["primary"]
    resids = primary["residuals"]
    fitted = primary["fitted"]
    years = primary["years"]

    # (a) Residuals vs fitted
    ax = axes[i, 0]
    ax.scatter(fitted, resids, color="#2196F3", s=60, edgecolors="black", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Fitted values [2015 yuan]")
    ax.set_ylabel("Residuals [2015 yuan]")
    subplot_label = chr(ord('a') + i * 3)
    ax.text(0.02, 0.98, f"({subplot_label}) {label.capitalize()} -- Residuals vs Fitted",
            transform=ax.transAxes, fontsize="small", va="top", ha="left", fontweight="bold")

    # (b) Q-Q plot
    ax = axes[i, 1]
    osm, osr = stats.probplot(resids, dist="norm")
    ax.scatter(osm[0], osm[1], color="#2196F3", s=60, edgecolors="black", linewidth=0.5)
    # Fit line
    slope, intercept, r_val, p_val, se = stats.linregress(osm[0], osm[1])
    x_line = np.array([osm[0].min(), osm[0].max()])
    ax.plot(x_line, slope * x_line + intercept, "r--", linewidth=1.5)
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles [yuan]")
    subplot_label = chr(ord('a') + i * 3 + 1)
    ax.text(0.02, 0.98, f"({subplot_label}) {label.capitalize()} -- Q-Q Plot (r={r_val:.3f})",
            transform=ax.transAxes, fontsize="small", va="top", ha="left", fontweight="bold")

    # (c) Residuals over time
    ax = axes[i, 2]
    ax.bar(years, resids, color="#2196F3", edgecolor="black", linewidth=0.5, width=0.6)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Year")
    ax.set_ylabel("Residuals [2015 yuan]")
    dw_val = diagnostics[label]["durbin_watson"]
    subplot_label = chr(ord('a') + i * 3 + 2)
    ax.text(0.02, 0.98, f"({subplot_label}) {label.capitalize()} -- Residuals over time (DW={dw_val:.2f})",
            transform=ax.transAxes, fontsize="small", va="top", ha="left", fontweight="bold")

axes[0, 0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0, 0].transAxes,
                fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_09_diagnostics.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_09_diagnostics.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved diagnostics figure to {FIG_DIR}/fig_p3_09_diagnostics.pdf")


# ===========================================================================
# Figure 2: Bootstrap distributions
# ===========================================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, (label, col) in enumerate(series_configs):
    ax = axes[i]
    boot = all_results[label]["bootstrap"]
    shifts = boot["boot_shifts"]
    point_est = boot["point_estimate"]

    ax.hist(shifts, bins=50, density=True, color="#2196F3", alpha=0.7,
            edgecolor="black", linewidth=0.3)
    ax.axvline(point_est, color="red", linewidth=2, label=f"Point est: {point_est:.0f}")
    ax.axvline(boot["ci_95"][0], color="orange", linewidth=1.5, linestyle="--",
               label=f"95% CI: [{boot['ci_95'][0]:.0f}, {boot['ci_95'][1]:.0f}]")
    ax.axvline(boot["ci_95"][1], color="orange", linewidth=1.5, linestyle="--")
    ax.axvline(0, color="black", linewidth=0.5, linestyle=":")

    ax.set_xlabel("Level shift [2015 yuan]")
    ax.set_ylabel("Density")
    ax.legend(fontsize="x-small")

    subplot_label = chr(ord('a') + i)
    ax.text(0.02, 0.98, f"({subplot_label}) {label.capitalize()} (n={boot['n_boot']} boot reps)",
            transform=ax.transAxes, fontsize="small", va="top", ha="left", fontweight="bold")

axes[0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0].transAxes,
             fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_10_bootstrap.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_10_bootstrap.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved bootstrap figure to {FIG_DIR}/fig_p3_10_bootstrap.pdf")


# ===========================================================================
# Save results
# ===========================================================================

results_json = {}
for label in ["national", "urban", "rural"]:
    primary = all_results[label]["primary"]
    boot = all_results[label]["bootstrap"]

    results_json[label] = {
        "model": {
            "level_shift": primary["level_shift"],
            "level_shift_se": primary["level_shift_se"],
            "level_shift_pvalue": primary["level_shift_pvalue"],
            "trend": primary["trend"],
            "intercept": primary["intercept"],
            "r_squared": primary["r_squared"],
            "adj_r_squared": primary["adj_r_squared"],
            "aic": primary["aic"],
            "bic": primary["bic"],
            "df_resid": primary["df_resid"],
            "n_obs": primary["n_obs"],
        },
        "bootstrap": {
            "n_boot": boot["n_boot"],
            "n_valid": boot["n_valid"],
            "boot_mean": boot["boot_mean"],
            "boot_se": boot["boot_se"],
            "ci_68": boot["ci_68"],
            "ci_90": boot["ci_90"],
            "ci_95": boot["ci_95"],
        },
        "diagnostics": diagnostics[label],
        "sensitivity": sensitivity[label],
        "signal_injection": signal_injection[label],
        "effect_size": effect_sizes[label],
    }

with open(f"{DATA_DIR}/step6_model_results.json", "w") as f:
    json.dump(results_json, f, indent=2)

log.info(f"\nSaved Step 6 results to {DATA_DIR}/step6_model_results.json")
log.info("\nStep 6 (Statistical Model Fitting) complete.")
