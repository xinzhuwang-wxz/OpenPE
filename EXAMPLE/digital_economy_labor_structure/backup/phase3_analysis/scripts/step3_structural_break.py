"""
Step 3.2 continued: Structural Break Analysis (the 'DID baseline').

Pre/post comparison around smart city pilot dates (2013-2015).
Chow tests in first differences.
Counterfactual trend extrapolation.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

np.random.seed(42)

# OpenPE plotting style
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

df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)

# ---------------------------------------------------------------------------
# Define periods
# ---------------------------------------------------------------------------
PRE_END = 2012
POST_START = 2016

pre = df[df["year"] <= PRE_END].copy()
post = df[df["year"] >= POST_START].copy()
transition = df[(df["year"] >= 2013) & (df["year"] <= 2015)].copy()

log.info(f"Pre-period: {pre['year'].min()}-{pre['year'].max()} (T={len(pre)})")
log.info(f"Post-period: {post['year'].min()}-{post['year'].max()} (T={len(post)})")
log.info(f"Transition: {transition['year'].min()}-{transition['year'].max()} (T={len(transition)})")


# ---------------------------------------------------------------------------
# Chow test in first differences
# ---------------------------------------------------------------------------
def chow_test_first_diff(data_df, dep_col, indep_cols, break_year):
    """
    Chow test for structural break at break_year, using first-differenced data.
    """
    all_cols = [dep_col] + indep_cols
    sub = data_df[all_cols + ["year"]].dropna()

    # First differences (drop year column for diff, keep year for splitting)
    dsub = sub[all_cols].diff()
    dsub["year"] = sub["year"].values
    dsub = dsub.dropna()

    pre_d = dsub[dsub["year"] <= break_year]
    post_d = dsub[dsub["year"] > break_year]

    n1 = len(pre_d)
    n2 = len(post_d)
    k = len(indep_cols) + 1  # including constant

    if n1 < k + 1 or n2 < k + 1:
        log.warning(f"  Insufficient obs for Chow test at {break_year}: n1={n1}, n2={n2}, k={k}")
        return None

    # OLS on pooled
    y_all = dsub[dep_col].values
    X_all = np.column_stack([np.ones(len(dsub))] + [dsub[c].values for c in indep_cols])

    beta_all = np.linalg.lstsq(X_all, y_all, rcond=None)[0]
    SSR_all = np.sum((y_all - X_all @ beta_all) ** 2)

    # OLS on pre
    y1 = pre_d[dep_col].values
    X1 = np.column_stack([np.ones(n1)] + [pre_d[c].values for c in indep_cols])
    beta1 = np.linalg.lstsq(X1, y1, rcond=None)[0]
    SSR1 = np.sum((y1 - X1 @ beta1) ** 2)

    # OLS on post
    y2 = post_d[dep_col].values
    X2 = np.column_stack([np.ones(n2)] + [post_d[c].values for c in indep_cols])
    beta2 = np.linalg.lstsq(X2, y2, rcond=None)[0]
    SSR2 = np.sum((y2 - X2 @ beta2) ** 2)

    # Chow F-statistic
    F_stat = ((SSR_all - SSR1 - SSR2) / k) / ((SSR1 + SSR2) / (n1 + n2 - 2 * k))
    p_value = 1 - stats.f.cdf(F_stat, dfn=k, dfd=n1 + n2 - 2 * k)

    log.info(f"  Chow test at {break_year}: F={F_stat:.3f}, p={p_value:.4f}")
    log.info(f"    Pre coeffs: {beta1.round(4)}")
    log.info(f"    Post coeffs: {beta2.round(4)}")

    return {
        "break_year": break_year,
        "F_stat": float(F_stat),
        "p_value": float(p_value),
        "n_pre": n1,
        "n_post": n2,
        "k": k,
        "beta_pre": beta1.tolist(),
        "beta_post": beta2.tolist(),
    }


# ---------------------------------------------------------------------------
# First-difference regression with break interaction
# ---------------------------------------------------------------------------
def break_interaction_regression(data_df, dep_col, indep_cols, break_year):
    """
    Delta_LS_t = a + b1*Delta_DE_t + b2*(POST_t * Delta_DE_t) + g*Delta_DEMO_t + e_t
    """
    all_cols = [dep_col] + indep_cols
    sub = data_df[all_cols + ["year"]].dropna()

    dsub = sub[all_cols].diff()
    dsub["year"] = sub["year"].values
    dsub = dsub.dropna()

    # Exclude transition window
    dsub = dsub[(dsub["year"] <= PRE_END) | (dsub["year"] >= POST_START)]

    y = dsub[dep_col].values
    post_indicator = (dsub["year"] >= POST_START).astype(float).values

    # Build X: constant, Delta_indep, POST * Delta_indep
    X_parts = [np.ones(len(dsub))]
    col_names = ["const"]
    for c in indep_cols:
        X_parts.append(dsub[c].values)
        col_names.append(f"d_{c}")
        X_parts.append(post_indicator * dsub[c].values)
        col_names.append(f"POST*d_{c}")

    X = np.column_stack(X_parts)
    n = len(y)
    k = X.shape[1]

    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    sigma2 = np.sum(resid**2) / (n - k)

    # Standard errors (OLS)
    try:
        var_beta = sigma2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diag(var_beta))
    except np.linalg.LinAlgError:
        se = np.full(k, np.nan)

    t_stats = beta / se
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n - k))

    log.info(f"\nBreak interaction regression: d({dep_col}) ~ d({indep_cols}) + POST interactions")
    log.info(f"  N={n}, k={k}, R2={1 - np.sum(resid**2)/np.sum((y - y.mean())**2):.4f}")
    for i, name in enumerate(col_names):
        sig = "***" if p_values[i] < 0.01 else "**" if p_values[i] < 0.05 else "*" if p_values[i] < 0.10 else ""
        log.info(f"    {name:25s}: {beta[i]:8.4f} (SE={se[i]:.4f}, t={t_stats[i]:.3f}, p={p_values[i]:.4f}){sig}")

    return {
        "dep": dep_col,
        "indep": indep_cols,
        "break_year": break_year,
        "n": n,
        "k": k,
        "R2": float(1 - np.sum(resid**2) / np.sum((y - y.mean())**2)),
        "coefficients": {name: {"beta": float(b), "se": float(s), "t": float(t), "p": float(p)}
                         for name, b, s, t, p in zip(col_names, beta, se, t_stats, p_values)},
    }


# ---------------------------------------------------------------------------
# Counterfactual trend extrapolation
# ---------------------------------------------------------------------------
def counterfactual_trend(data_df, col, pre_end=PRE_END, post_start=POST_START):
    """Extrapolate pre-period trend to post-period."""
    pre_data = data_df[data_df["year"] <= pre_end][[col, "year"]].dropna()
    post_data = data_df[data_df["year"] >= post_start][[col, "year"]].dropna()

    # Fit linear trend on pre-period
    x_pre = pre_data["year"].values
    y_pre = pre_data[col].values
    slope, intercept, r_val, p_val, se = stats.linregress(x_pre, y_pre)

    # Predict for post-period
    x_post = post_data["year"].values
    y_counterfactual = intercept + slope * x_post
    y_actual = post_data[col].values

    # Difference
    diff = y_actual - y_counterfactual
    mean_diff = np.mean(diff)
    se_diff = np.std(diff) / np.sqrt(len(diff))

    log.info(f"\nCounterfactual for {col}:")
    log.info(f"  Pre-trend: slope={slope:.4f}/yr, intercept={intercept:.2f}")
    log.info(f"  Mean post-period deviation: {mean_diff:.3f} (SE={se_diff:.3f})")
    log.info(f"  t-stat = {mean_diff/se_diff:.3f}, p = {2*(1-stats.t.cdf(abs(mean_diff/se_diff), df=len(diff)-1)):.4f}")

    return {
        "variable": col,
        "pre_slope": float(slope),
        "pre_intercept": float(intercept),
        "pre_r2": float(r_val**2),
        "post_years": x_post.tolist(),
        "counterfactual": y_counterfactual.tolist(),
        "actual": y_actual.tolist(),
        "mean_deviation": float(mean_diff),
        "se_deviation": float(se_diff),
        "t_stat": float(mean_diff / se_diff),
        "p_value": float(2 * (1 - stats.t.cdf(abs(mean_diff / se_diff), df=len(diff) - 1))),
    }


# ---------------------------------------------------------------------------
# Run analyses
# ---------------------------------------------------------------------------
break_results = {"chow": [], "interaction": [], "counterfactual": []}

log.info("=" * 60)
log.info("CHOW TESTS (first differences)")
log.info("=" * 60)

for dep, label in [
    ("employment_services_pct", "creation"),
    ("employment_industry_pct", "substitution"),
    ("services_value_added_pct_gdp", "mediation"),
]:
    for break_yr in [2013, 2015]:
        r = chow_test_first_diff(df, dep, ["digital_economy_index"], break_yr)
        if r:
            r["label"] = label
            r["dep"] = dep
            break_results["chow"].append(r)

    # With demographic control
    for break_yr in [2013, 2015]:
        r = chow_test_first_diff(df, dep, ["digital_economy_index", "population_15_64_pct"], break_yr)
        if r:
            r["label"] = f"{label}_ctrl"
            r["dep"] = dep
            break_results["chow"].append(r)

log.info("")
log.info("=" * 60)
log.info("BREAK INTERACTION REGRESSIONS")
log.info("=" * 60)

for dep, label in [
    ("employment_services_pct", "creation"),
    ("employment_industry_pct", "substitution"),
]:
    # Without control
    r = break_interaction_regression(df, dep, ["digital_economy_index"], POST_START)
    if r:
        r["label"] = label
        break_results["interaction"].append(r)

    # With demographic control
    r = break_interaction_regression(df, dep, ["digital_economy_index", "population_15_64_pct"], POST_START)
    if r:
        r["label"] = f"{label}_ctrl"
        break_results["interaction"].append(r)

log.info("")
log.info("=" * 60)
log.info("COUNTERFACTUAL TREND EXTRAPOLATION")
log.info("=" * 60)

for col in ["employment_services_pct", "employment_industry_pct",
            "employment_agriculture_pct", "services_value_added_pct_gdp",
            "digital_economy_index"]:
    r = counterfactual_trend(df, col)
    break_results["counterfactual"].append(r)


# ---------------------------------------------------------------------------
# Plot: 4-panel structural break figure (the "DID baseline" figure)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# Panel (a): DE index time series with break window
ax = axes[0, 0]
ax.plot(df["year"], df["digital_economy_index"], "o-", color="#2196F3", linewidth=2, markersize=4)
ax.axvspan(2013, 2015, alpha=0.15, color="orange", label="Pilot window")
ax.axvline(2012.5, color="gray", linestyle="--", linewidth=0.8)
ax.axvline(2015.5, color="gray", linestyle="--", linewidth=0.8)
ax.set_xlabel("Year")
ax.set_ylabel("DE Index [0-1]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")
ax.text(0.02, 0.05, "(a)", transform=ax.transAxes, fontsize=12, va="bottom", ha="left", weight="bold")

# Panel (b): Employment structure with break window
ax = axes[0, 1]
for col, label, color in [
    ("employment_services_pct", "Services", "#4CAF50"),
    ("employment_industry_pct", "Industry", "#F44336"),
    ("employment_agriculture_pct", "Agriculture", "#FF9800"),
]:
    ax.plot(df["year"], df[col], "o-", color=color, linewidth=2, markersize=4, label=label)
ax.axvspan(2013, 2015, alpha=0.15, color="orange")
ax.axvline(2012.5, color="gray", linestyle="--", linewidth=0.8)
ax.axvline(2015.5, color="gray", linestyle="--", linewidth=0.8)
ax.set_xlabel("Year")
ax.set_ylabel("Employment share [%]")
ax.legend(fontsize="small")
ax.text(0.02, 0.05, "(b)", transform=ax.transAxes, fontsize=12, va="bottom", ha="left", weight="bold")

# Panel (c): First-diff scatter, pre vs post
ax = axes[1, 0]
d_de = df["digital_economy_index"].diff()
d_serv = df["employment_services_pct"].diff()
years = df["year"].values

pre_mask = (years <= PRE_END) & (~np.isnan(d_de)) & (~np.isnan(d_serv))
post_mask = (years >= POST_START) & (~np.isnan(d_de)) & (~np.isnan(d_serv))

# Filter out first year (NaN from diff)
pre_mask[0] = False
post_mask[0] = False

ax.scatter(d_de[pre_mask], d_serv[pre_mask], c="#2196F3", s=60, label="Pre (2001-2012)", zorder=5)
ax.scatter(d_de[post_mask], d_serv[post_mask], c="#F44336", s=60, label="Post (2016-2023)", zorder=5)

# Regression lines
for mask, color in [(pre_mask, "#2196F3"), (post_mask, "#F44336")]:
    x_vals = d_de[mask].values
    y_vals = d_serv[mask].values
    if len(x_vals) > 1:
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 50)
        ax.plot(x_line, intercept + slope * x_line, color=color, linewidth=1.5, linestyle="--")

ax.set_xlabel("Delta DE Index")
ax.set_ylabel("Delta Services Employment [pp]")
ax.legend(fontsize="small")
ax.text(0.02, 0.05, "(c)", transform=ax.transAxes, fontsize=12, va="bottom", ha="left", weight="bold")

# Panel (d): Counterfactual vs actual for services employment
ax = axes[1, 1]
cf_serv = [r for r in break_results["counterfactual"] if r["variable"] == "employment_services_pct"][0]
ax.plot(df["year"], df["employment_services_pct"], "o-", color="#4CAF50", linewidth=2, markersize=4, label="Observed")

# Pre-trend extrapolation line (full range for visual)
all_years = np.arange(2000, 2024)
cf_line = cf_serv["pre_intercept"] + cf_serv["pre_slope"] * all_years
ax.plot(all_years, cf_line, "--", color="gray", linewidth=1.5, label="Pre-trend extrapolation")

# Shade post-period difference
post_yrs = np.array(cf_serv["post_years"])
cf_vals = np.array(cf_serv["counterfactual"])
actual_vals = np.array(cf_serv["actual"])
ax.fill_between(post_yrs, cf_vals, actual_vals, alpha=0.2, color="#F44336",
                label=f"Deviation: {cf_serv['mean_deviation']:+.2f}pp (p={cf_serv['p_value']:.3f})")

ax.axvspan(2013, 2015, alpha=0.10, color="orange")
ax.set_xlabel("Year")
ax.set_ylabel("Services employment [%]")
ax.legend(fontsize="small", loc="upper left")
ax.text(0.02, 0.05, "(d)", transform=ax.transAxes, fontsize=12, va="bottom", ha="left", weight="bold")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/structural_break_did_baseline.pdf",
            bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/structural_break_did_baseline.png",
            bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("\nFigure saved: structural_break_did_baseline.pdf/png")

# Save results
output_path = "phase3_analysis/scripts/structural_break_results.json"
with open(output_path, "w") as f:
    json.dump(break_results, f, indent=2,
              default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else x)
log.info(f"Results saved to {output_path}")
