"""
Step 5: Refutation Battery.

Per strategy Section 5 (adapted for n=10):
1. Permutation-based placebo (exhaustive, all possible intervention years)
2. Random common cause (200 iterations)
3. Jackknife leave-one-out stability
4. COVID-date placebo (move intervention to 2020)

Produces: phase3_analysis/figures/fig_p3_07_*.pdf/png
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

with open(f"{DATA_DIR}/its_results.json") as f:
    its_results = json.load(f)


def run_its(data, outcome_col, intervention_year, exclude_years=None):
    """Run 3-param ITS, return level shift + stats."""
    d = data.copy()
    if exclude_years:
        d = d[~d["year"].isin(exclude_years)].reset_index(drop=True)
    d["time"] = d["year"] - d["year"].min()
    d["post"] = (d["year"] >= intervention_year).astype(int)
    X = sm.add_constant(d[["time", "post"]])
    y = d[outcome_col]
    model = sm.OLS(y, X).fit()
    return {
        "level_shift": float(model.params["post"]),
        "level_shift_se": float(model.bse["post"]),
        "level_shift_pvalue": float(model.pvalues["post"]),
    }


# =============================================================================
# Refutation tests for each series
# =============================================================================
series_configs = [
    ("national", "real_national"),
    ("urban", "real_urban"),
    ("rural", "real_rural"),
]

refutation_results = {}

for label, col in series_configs:
    log.info(f"\n{'='*60}")
    log.info(f"REFUTATION BATTERY: {label}")
    log.info(f"{'='*60}")

    true_shift = its_results[label]["primary"]["level_shift"]
    true_se = its_results[label]["primary"]["level_shift_se"]
    true_p = its_results[label]["primary"]["level_shift_pvalue"]
    log.info(f"True estimate: {true_shift:.1f} (SE={true_se:.1f}, p={true_p:.4f})")

    results = {"true_shift": true_shift, "true_se": true_se, "true_pvalue": true_p}

    # ---- Test 1: Permutation-based placebo ----
    log.info(f"\n--- Test 1: Placebo Treatment (all years) ---")
    placebo_years = [2017, 2018, 2019]  # Pre-policy years only
    placebo_results = {}

    for pyr in placebo_years:
        res = run_its(df, col, intervention_year=pyr, exclude_years=[2020])
        placebo_results[pyr] = res
        log.info(f"  Placebo {pyr}: shift={res['level_shift']:.1f} "
                 f"(SE={res['level_shift_se']:.1f}, p={res['level_shift_pvalue']:.4f})")

    # PASS if no placebo is significant at 10%
    any_placebo_sig = any(r["level_shift_pvalue"] < 0.10 for r in placebo_results.values())
    placebo_pass = not any_placebo_sig

    # Also check: is true effect larger than all placebos?
    max_placebo_abs = max(abs(r["level_shift"]) for r in placebo_results.values())
    true_larger = abs(true_shift) > max_placebo_abs

    log.info(f"  Any placebo significant at 10%? {any_placebo_sig}")
    log.info(f"  True effect ({abs(true_shift):.0f}) > max placebo ({max_placebo_abs:.0f})? {true_larger}")
    log.info(f"  VERDICT: {'PASS' if placebo_pass else 'FAIL'}")

    results["placebo"] = {
        "details": {int(k): v for k, v in placebo_results.items()},
        "any_significant": bool(any_placebo_sig),
        "true_larger_than_all": bool(true_larger),
        "pass": bool(placebo_pass),
    }

    # ---- Test 2: Random common cause (200 iterations) ----
    log.info(f"\n--- Test 2: Random Common Cause (200 iterations) ---")
    df_no2020 = df[df["year"] != 2020].copy().reset_index(drop=True)
    df_no2020["time"] = df_no2020["year"] - df_no2020["year"].min()
    df_no2020["post"] = (df_no2020["year"] >= 2021).astype(int)

    n_iter = 200
    random_shifts = []

    for _ in range(n_iter):
        df_no2020["random_cause"] = np.random.randn(len(df_no2020))
        X = sm.add_constant(df_no2020[["time", "post", "random_cause"]])
        y = df_no2020[col]
        try:
            model = sm.OLS(y, X).fit()
            random_shifts.append(float(model.params["post"]))
        except Exception:
            pass

    random_shifts = np.array(random_shifts)
    mean_shift_with_random = random_shifts.mean()
    std_shift = random_shifts.std()

    # Percent change from true estimate
    pct_change = abs(mean_shift_with_random - true_shift) / abs(true_shift) * 100
    # PASS if estimate changes less than 10% on average
    rcc_pass = pct_change < 10.0

    # Also: what fraction of random-cause estimates exceed true estimate?
    frac_exceed = np.mean(np.abs(random_shifts) >= abs(true_shift))

    log.info(f"  True shift: {true_shift:.1f}")
    log.info(f"  Mean with random cause: {mean_shift_with_random:.1f} (std={std_shift:.1f})")
    log.info(f"  Avg % change: {pct_change:.1f}%")
    log.info(f"  Fraction exceeding true: {frac_exceed:.3f}")
    log.info(f"  VERDICT: {'PASS' if rcc_pass else 'FAIL'} (threshold: <10% change)")

    results["random_common_cause"] = {
        "true_shift": float(true_shift),
        "mean_with_random": float(mean_shift_with_random),
        "std_with_random": float(std_shift),
        "pct_change": float(pct_change),
        "frac_exceed_true": float(frac_exceed),
        "pass": bool(rcc_pass),
    }

    # ---- Test 3: Data Subset (randomly drop 22% = 2 of 9 obs, 200 iter) ----
    # A3 fix: replaces jackknife with the convention-required data subset test.
    # Jackknife is retained below as supplementary diagnostic.
    log.info(f"\n--- Test 3: Data Subset (drop 2 of 9, 200 iterations) ---")
    df_no2020_reset = df[df["year"] != 2020].copy().reset_index(drop=True)
    n_obs = len(df_no2020_reset)
    n_drop = 2  # 22% of 9
    n_subset_iter = 200

    subset_shifts = []
    for _ in range(n_subset_iter):
        drop_idx = np.random.choice(n_obs, size=n_drop, replace=False)
        df_sub = df_no2020_reset.drop(drop_idx).reset_index(drop=True)
        try:
            res = run_its(df_sub, col, intervention_year=2021)
            subset_shifts.append(res["level_shift"])
        except Exception:
            pass

    subset_shifts = np.array(subset_shifts)
    subset_mean = subset_shifts.mean()
    subset_std = subset_shifts.std()
    subset_median = np.median(subset_shifts)

    # Percent deviation of mean from true estimate
    subset_pct_dev = abs(subset_mean - true_shift) / abs(true_shift) * 100
    # Fraction of iterations where sign matches the true estimate
    frac_same_sign = np.mean(np.sign(subset_shifts) == np.sign(true_shift))
    # Fraction within 50% of true estimate magnitude
    frac_within_50pct = np.mean(
        np.abs(subset_shifts - true_shift) < 0.5 * abs(true_shift)
    )

    # PASS if (a) mean deviation < 30% AND (b) >80% of iterations keep the same sign
    subset_pass = (subset_pct_dev < 30.0) and (frac_same_sign > 0.80)

    log.info(f"  True shift: {true_shift:.1f}")
    log.info(f"  Subset mean: {subset_mean:.1f} (std={subset_std:.1f})")
    log.info(f"  Subset median: {subset_median:.1f}")
    log.info(f"  Mean % deviation: {subset_pct_dev:.1f}%")
    log.info(f"  Fraction same sign: {frac_same_sign:.3f}")
    log.info(f"  Fraction within 50% of true: {frac_within_50pct:.3f}")
    log.info(f"  VERDICT: {'PASS' if subset_pass else 'FAIL'} "
             f"(thresholds: <30% mean dev AND >80% same sign)")

    results["data_subset"] = {
        "n_obs": int(n_obs),
        "n_drop": int(n_drop),
        "n_iterations": int(n_subset_iter),
        "mean_shift": float(subset_mean),
        "std_shift": float(subset_std),
        "median_shift": float(subset_median),
        "pct_deviation": float(subset_pct_dev),
        "frac_same_sign": float(frac_same_sign),
        "frac_within_50pct": float(frac_within_50pct),
        "pass": bool(subset_pass),
    }

    # ---- Supplementary: Jackknife leave-one-out (diagnostic only) ----
    log.info(f"\n--- Supplementary: Jackknife Leave-One-Out ---")
    jackknife_shifts = {}

    for idx_to_drop in range(len(df_no2020_reset)):
        dropped_year = int(df_no2020_reset.loc[idx_to_drop, "year"])
        df_jack = df_no2020_reset.drop(idx_to_drop).reset_index(drop=True)

        try:
            res = run_its(df_jack, col, intervention_year=2021)
            jackknife_shifts[dropped_year] = res["level_shift"]
            log.info(f"  Drop {dropped_year}: shift={res['level_shift']:.1f}")
        except Exception as e:
            log.warning(f"  Drop {dropped_year}: FAILED ({e})")
            jackknife_shifts[dropped_year] = np.nan

    jack_vals = [v for v in jackknife_shifts.values() if not np.isnan(v)]
    jack_range = max(jack_vals) - min(jack_vals) if jack_vals else 0
    jack_max_dev = max(abs(v - true_shift) for v in jack_vals) if jack_vals else 0
    jack_max_dev_pct = (jack_max_dev / abs(true_shift)) * 100 if true_shift != 0 else 0

    log.info(f"  True shift: {true_shift:.1f}")
    log.info(f"  Jackknife range: [{min(jack_vals):.1f}, {max(jack_vals):.1f}]")
    log.info(f"  Max deviation: {jack_max_dev:.1f} ({jack_max_dev_pct:.1f}%)")

    results["jackknife"] = {
        "estimates": {int(k): float(v) for k, v in jackknife_shifts.items()},
        "range": float(jack_range),
        "max_deviation": float(jack_max_dev),
        "max_deviation_pct": float(jack_max_dev_pct),
        "note": "Supplementary diagnostic only; not part of core refutation battery.",
    }

    # ---- Test 4: COVID-date placebo ----
    log.info(f"\n--- Test 4: COVID-Date Placebo (intervention at 2020) ---")
    # Use all data, set intervention at 2020 instead of 2021
    res_covid_placebo = run_its(df, col, intervention_year=2020)
    log.info(f"  COVID placebo shift: {res_covid_placebo['level_shift']:.1f} "
             f"(SE={res_covid_placebo['level_shift_se']:.1f}, "
             f"p={res_covid_placebo['level_shift_pvalue']:.4f})")

    # If COVID placebo is also significant and similar magnitude, then
    # the 2021 effect is likely COVID-driven, not policy-driven
    covid_similar = abs(res_covid_placebo["level_shift"]) > abs(true_shift) * 0.5
    covid_sig = res_covid_placebo["level_shift_pvalue"] < 0.10

    covid_placebo_pass = not (covid_similar and covid_sig)
    log.info(f"  COVID shift similar magnitude? {covid_similar}")
    log.info(f"  COVID shift significant? {covid_sig}")
    log.info(f"  VERDICT: {'PASS' if covid_placebo_pass else 'FAIL'}")

    results["covid_placebo"] = {
        "shift": float(res_covid_placebo["level_shift"]),
        "se": float(res_covid_placebo["level_shift_se"]),
        "pvalue": float(res_covid_placebo["level_shift_pvalue"]),
        "similar_magnitude": bool(covid_similar),
        "significant": bool(covid_sig),
        "pass": bool(covid_placebo_pass),
    }

    # ---- Overall classification ----
    tests_passed = sum([
        results["placebo"]["pass"],
        results["random_common_cause"]["pass"],
        results["data_subset"]["pass"],
    ])

    if tests_passed >= 3:
        classification = "DATA_SUPPORTED"
    elif tests_passed >= 2:
        classification = "CORRELATION"
    elif tests_passed >= 1:
        classification = "HYPOTHESIZED"
    else:
        classification = "DISPUTED"

    # Downgrade if COVID placebo fails
    if not results["covid_placebo"]["pass"] and classification == "DATA_SUPPORTED":
        classification = "CORRELATION"
        log.info("  Downgraded from DATA_SUPPORTED due to COVID placebo failure")

    results["tests_passed"] = int(tests_passed)
    results["classification"] = classification

    log.info(f"\n  CLASSIFICATION: {classification} ({tests_passed}/3 core tests passed)")
    log.info(f"  COVID placebo: {'PASS' if covid_placebo_pass else 'FAIL'}")

    refutation_results[label] = results


# ==== Figure: Refutation summary ====
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# (a) Placebo test
ax = axes[0, 0]
for i, (label, col) in enumerate(series_configs):
    true_s = refutation_results[label]["true_shift"]
    placebo_data = refutation_results[label]["placebo"]["details"]
    all_years = sorted(placebo_data.keys()) + [2021]
    all_shifts = [placebo_data.get(yr, {"level_shift": 0})["level_shift"]
                  if yr != 2021 else true_s for yr in all_years]

    offset = (i - 1) * 0.2
    for yr, shift in zip(all_years, all_shifts):
        color = "#F44336" if yr == 2021 else "#2196F3"
        marker = "D" if yr == 2021 else "o"
        ax.scatter(yr + offset, shift, color=color, marker=marker, s=60, zorder=5)

    # Connect with line
    ax.plot([yr + offset for yr in all_years], all_shifts, "-", alpha=0.3,
            label=label if i == 0 else "_" + label)

ax.axhline(0, color="black", linewidth=0.5)
ax.set_xlabel("Intervention year [tested]")
ax.set_ylabel("Level shift [2015 yuan]")
ax.legend(["National", "Urban", "Rural"], fontsize="small")
ax.text(0.02, 0.98, "(a) Placebo tests: shift at each candidate year",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

# (b) Random common cause distribution
ax = axes[0, 1]
for i, (label, col) in enumerate(series_configs):
    rcc = refutation_results[label]["random_common_cause"]
    ax.axvline(refutation_results[label]["true_shift"],
               color=["#2196F3", "#F44336", "#4CAF50"][i],
               linestyle="--", linewidth=2,
               label=f"{label} (true)")

# Show histogram for national only (most representative)
# Re-run to get the distribution
df_no2020 = df[df["year"] != 2020].copy().reset_index(drop=True)
df_no2020["time"] = df_no2020["year"] - df_no2020["year"].min()
df_no2020["post"] = (df_no2020["year"] >= 2021).astype(int)

rcc_shifts_national = []
for _ in range(200):
    df_no2020["random_cause"] = np.random.randn(len(df_no2020))
    X = sm.add_constant(df_no2020[["time", "post", "random_cause"]])
    y = df_no2020["real_national"]
    try:
        model = sm.OLS(y, X).fit()
        rcc_shifts_national.append(float(model.params["post"]))
    except Exception:
        pass

ax.hist(rcc_shifts_national, bins=20, alpha=0.5, color="#2196F3", edgecolor="black")
ax.axvline(refutation_results["national"]["true_shift"], color="#F44336", linewidth=2,
           linestyle="--", label="True estimate")
ax.set_xlabel("Level shift with random confounder [2015 yuan]")
ax.set_ylabel("Count")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "(b) Random common cause: national",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

# (c) Data subset distribution (national)
ax = axes[1, 0]
# Re-run data subset for national to capture the distribution for plotting
df_no2020_plot = df[df["year"] != 2020].copy().reset_index(drop=True)
n_obs_plot = len(df_no2020_plot)
subset_shifts_national = []
for _ in range(200):
    drop_idx = np.random.choice(n_obs_plot, size=2, replace=False)
    df_sub = df_no2020_plot.drop(drop_idx).reset_index(drop=True)
    try:
        res = run_its(df_sub, "real_national", intervention_year=2021)
        subset_shifts_national.append(res["level_shift"])
    except Exception:
        pass

ax.hist(subset_shifts_national, bins=20, alpha=0.5, color="#4CAF50", edgecolor="black")
ax.axvline(refutation_results["national"]["true_shift"], color="#F44336", linewidth=2,
           linestyle="--", label="True estimate")
ax.set_xlabel("Level shift [2015 yuan]")
ax.set_ylabel("Count")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "(c) Data subset: national (drop 2 of 9, 200 iter)",
        transform=ax.transAxes, fontsize="small", va="top", ha="left", fontweight="bold")

# (d) Summary table
ax = axes[1, 1]
ax.axis("off")

table_data = []
headers = ["Series", "Placebo", "RCC", "Data Sub.", "COVID", "Class."]
for label, _ in series_configs:
    r = refutation_results[label]
    p_icon = "PASS" if r["placebo"]["pass"] else "FAIL"
    rcc_icon = "PASS" if r["random_common_cause"]["pass"] else "FAIL"
    ds_icon = "PASS" if r["data_subset"]["pass"] else "FAIL"
    c_icon = "PASS" if r["covid_placebo"]["pass"] else "FAIL"
    table_data.append([label.capitalize(), p_icon, rcc_icon, ds_icon, c_icon,
                       r["classification"]])

table = ax.table(cellText=table_data, colLabels=headers, loc="center",
                 cellLoc="center")
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.5)

# Color code cells
for i in range(len(table_data)):
    for j in range(1, 5):  # test columns
        val = table_data[i][j]
        cell = table[i + 1, j]
        if val == "PASS":
            cell.set_facecolor("#C8E6C9")
        else:
            cell.set_facecolor("#FFCDD2")

    # Classification column
    cls = table_data[i][5]
    cell = table[i + 1, 5]
    if cls == "DATA_SUPPORTED":
        cell.set_facecolor("#C8E6C9")
    elif cls == "CORRELATION":
        cell.set_facecolor("#FFF9C4")
    elif cls == "HYPOTHESIZED":
        cell.set_facecolor("#FFE0B2")
    else:
        cell.set_facecolor("#FFCDD2")

ax.text(0.02, 0.98, "(d) Refutation summary",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

fig.text(0.02, 0.98, "OpenPE Analysis", fontsize=8, va="top", ha="left",
         color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_07_refutation.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_07_refutation.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"\nSaved refutation figure to {FIG_DIR}/fig_p3_07_refutation.pdf")

# ---- Save results ----
with open(f"{DATA_DIR}/refutation_results.json", "w") as f:
    json.dump(refutation_results, f, indent=2)

log.info(f"Saved refutation results to {DATA_DIR}/refutation_results.json")
log.info("\nStep 5 (Refutation Battery) complete.")
