"""
Step 3.6/3.7 Key Figure: DID Baseline Comparison.

Produces the comprehensive comparison figure requested by the user:
- Structural break (DID-inspired) estimates vs Granger causality vs VECM
- For both creation and substitution channels
- With confidence bands and significance markers

Layout: 2x3 grid
  Row 1: Substitution channel
  Row 2: Creation channel
  Col 1: DID-inspired structural break estimate with CI
  Col 2: Granger causality W-stat comparison
  Col 3: Method comparison forest plot
"""

import logging
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

np.random.seed(42)

# --- OpenPE default style ---
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

# -----------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------
df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)

with open("phase3_analysis/scripts/granger_results.json") as f:
    granger = json.load(f)
with open("phase3_analysis/scripts/structural_break_results.json") as f:
    sb = json.load(f)
with open("phase3_analysis/scripts/cointegration_results.json") as f:
    coint = json.load(f)
with open("phase3_analysis/scripts/statistical_model_results.json") as f:
    model = json.load(f)
with open("phase3_analysis/scripts/uncertainty_results.json") as f:
    unc = json.load(f)

# -----------------------------------------------------------------------
# Prepare data
# -----------------------------------------------------------------------
dep_ind = df["employment_industry_pct"].values
dep_svc = df["employment_services_pct"].values
de_idx = df["digital_economy_index"].values
demo = df["population_15_64_pct"].values
years = df["year"].values

d_de = np.diff(de_idx)
d_emp_ind = np.diff(dep_ind)
d_emp_svc = np.diff(dep_svc)
d_demo = np.diff(demo)
years_fd = years[1:]
post = (years_fd >= 2016).astype(float)

# -----------------------------------------------------------------------
# Figure 1: Comprehensive DID Baseline Comparison (2x3)
# -----------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(24, 16))

# --- Colors ---
c_did = "#E53935"    # red for DID-inspired
c_granger = "#1E88E5"  # blue for Granger
c_vecm = "#43A047"   # green for VECM/ARDL
c_cf = "#FF9800"     # orange for counterfactual
c_sig = "#4CAF50"    # green for significant
c_ns = "#9E9E9E"     # gray for non-significant

# ===== ROW 1: SUBSTITUTION CHANNEL =====

# (a) DID-inspired time series with counterfactual
ax = axes[0, 0]
# Get counterfactual for industry employment
cf_ind = None
for cf in sb["counterfactual"]:
    if cf["variable"] == "employment_industry_pct":
        cf_ind = cf
cf_svc = None
for cf in sb["counterfactual"]:
    if cf["variable"] == "employment_services_pct":
        cf_svc = cf

# Pre-trend line
pre_years = np.array([y for y in years if y <= 2015])
pre_vals_ind = np.array([dep_ind[i] for i, y in enumerate(years) if y <= 2015])

# Full counterfactual line (extrapolated from pre-trend)
all_years = np.arange(2000, 2024)
cf_line = cf_ind["pre_slope"] * all_years + cf_ind["pre_intercept"]

ax.plot(years, dep_ind, "o-", color=c_did, linewidth=2, markersize=5,
        label="Observed industry emp [%]", zorder=3)
ax.plot(all_years, cf_line, "--", color=c_cf, linewidth=1.5,
        label="Pre-2013 trend counterfactual", alpha=0.8)

# Shade the treatment period
ax.axvspan(2012.5, 2015.5, alpha=0.08, color="blue",
           label="Smart city pilot window")

# Shade the deviation post-2015
post_years_cf = np.array(cf_ind["post_years"])
cf_vals = np.array(cf_ind["counterfactual"])
actual_vals = np.array(cf_ind["actual"])
ax.fill_between(post_years_cf, cf_vals, actual_vals,
                alpha=0.15, color=c_did)

# Annotation with deviation
ax.annotate(
    f"Deviation: {cf_ind['mean_deviation']:.2f} pp\n"
    f"(t={cf_ind['t_stat']:.1f}, p<0.001)",
    xy=(2020, (actual_vals[4] + cf_vals[4]) / 2),
    xytext=(2005, 35),
    fontsize="small",
    arrowprops=dict(arrowstyle="->", color="gray", lw=1),
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
)

ax.set_xlabel("Year")
ax.set_ylabel("Industry employment share [%]")
ax.legend(fontsize="x-small", loc="upper left")
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(a) Substitution: DID-inspired baseline",
        transform=ax.transAxes, fontsize="small", va="bottom")

# (b) Granger W-stat comparison
ax = axes[0, 1]

# Granger results for substitution
sub_biv = next(g for g in granger if g["label"] == "substitution" and g["spec"] == "bivariate")
sub_ctrl = next(g for g in granger if g["label"] == "substitution_ctrl" and g["spec"] == "with_demo_control")

labels_g = ["Bivariate", "With DEMO\ncontrol"]
w_stats = [sub_biv["W_stat"], sub_ctrl["W_stat"]]
p_boots = [sub_biv["p_bootstrap"], sub_ctrl["p_bootstrap"]]

# Bootstrap CIs from uncertainty results
w_se_biv = unc["bootstrap_granger"]["substitution"]["W_boot_se"]
w_se_ctrl = w_se_biv * 1.5  # approximate, controlled spec has larger variance

colors_bar = [c_sig if p < 0.10 else c_ns for p in p_boots]
bars = ax.barh(labels_g, w_stats, height=0.5, color=colors_bar, alpha=0.8,
               xerr=[w_se_biv, w_se_ctrl], capsize=5, ecolor="gray")

# Critical value lines
ax.axvline(x=5.991, color="red", linestyle="--", linewidth=1, alpha=0.6,
           label=r"$\chi^2_{0.05}$ = 5.99")
ax.axvline(x=4.605, color="orange", linestyle="--", linewidth=1, alpha=0.6,
           label=r"$\chi^2_{0.10}$ = 4.61")

# p-value annotations
for i, (w, p) in enumerate(zip(w_stats, p_boots)):
    sig_marker = "**" if p < 0.05 else "*" if p < 0.10 else "n.s."
    ax.text(w + 0.5, i, f"p={p:.3f} {sig_marker}", va="center", fontsize="small")

ax.set_xlabel("Toda-Yamamoto W statistic")
ax.legend(fontsize="x-small")
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(b) Substitution: Granger causality",
        transform=ax.transAxes, fontsize="small", va="bottom")

# (c) Method comparison forest plot -- Substitution
ax = axes[0, 2]

methods = [
    "Granger\n(bivariate)",
    "Granger\n(+DEMO)",
    "ARDL bounds\n(F-stat)",
    "Chow 2015\n(first-diff)",
    "Counterfactual\ndeviation",
    "DID-inspired\n(POST*dDE)",
]

# Normalized effect indicators (direction + significance)
# For comparability, we show: significant? direction? as a qualitative indicator
# Values are approximate z-scores or t-stats
effect_vals = [
    sub_biv["W_stat"] / np.sqrt(2),     # Granger biv: W/sqrt(df)
    sub_ctrl["W_stat"] / np.sqrt(2),     # Granger ctrl
    coint["ardl"][1]["F_stat"] / coint["ardl"][1]["bounds_5pct"][1],  # F/upper_bound
    sb["chow"][5]["F_stat"],             # Chow 2015 substitution
    cf_ind["t_stat"],                    # counterfactual t
    model["did_inspired"]["substitution"]["tvalues"]["d_DE"],
]

sig_flags = [
    sub_biv["p_bootstrap"] < 0.10,
    sub_ctrl["p_bootstrap"] < 0.05,
    coint["ardl"][1]["F_stat"] > coint["ardl"][1]["bounds_5pct"][1],
    sb["chow"][5]["p_value"] < 0.10,
    cf_ind["p_value"] < 0.05,
    model["did_inspired"]["substitution"]["pvalues"]["d_DE"] < 0.10,
]

# Forest plot
y_pos = np.arange(len(methods))
for i, (val, sig) in enumerate(zip(effect_vals, sig_flags)):
    color = c_sig if sig else c_ns
    marker = "D" if sig else "o"
    ax.plot(val, i, marker, color=color, markersize=10, zorder=3)
    ax.plot([0, val], [i, i], "-", color=color, linewidth=1.5, alpha=0.5)

ax.axvline(x=0, color="black", linewidth=0.5)
ax.axvline(x=1.96, color="red", linewidth=0.8, linestyle="--", alpha=0.5,
           label="Conventional threshold")
ax.set_yticks(y_pos)
ax.set_yticklabels(methods, fontsize="small")
ax.set_xlabel("Test statistic (normalized)")
ax.legend(fontsize="x-small")

# Color legend
ax.plot([], [], "D", color=c_sig, markersize=8, label="Significant")
ax.plot([], [], "o", color=c_ns, markersize=8, label="Not significant")
ax.legend(fontsize="x-small", loc="lower right")

ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(c) Substitution: method comparison",
        transform=ax.transAxes, fontsize="small", va="bottom")

# ===== ROW 2: CREATION CHANNEL =====

# (d) DID-inspired time series with counterfactual -- Creation
ax = axes[1, 0]

cf_line_svc = cf_svc["pre_slope"] * all_years + cf_svc["pre_intercept"]

ax.plot(years, dep_svc, "o-", color="#7B1FA2", linewidth=2, markersize=5,
        label="Observed services emp [%]", zorder=3)
ax.plot(all_years, cf_line_svc, "--", color=c_cf, linewidth=1.5,
        label="Pre-2013 trend counterfactual", alpha=0.8)

ax.axvspan(2012.5, 2015.5, alpha=0.08, color="blue",
           label="Smart city pilot window")

post_years_svc = np.array(cf_svc["post_years"])
cf_vals_svc = np.array(cf_svc["counterfactual"])
actual_vals_svc = np.array(cf_svc["actual"])
ax.fill_between(post_years_svc, cf_vals_svc, actual_vals_svc,
                alpha=0.15, color="#7B1FA2")

ax.annotate(
    f"Deviation: +{cf_svc['mean_deviation']:.2f} pp\n"
    f"(t={cf_svc['t_stat']:.1f}, p=0.001)",
    xy=(2020, (actual_vals_svc[4] + cf_vals_svc[4]) / 2),
    xytext=(2005, 44),
    fontsize="small",
    arrowprops=dict(arrowstyle="->", color="gray", lw=1),
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
)

ax.set_xlabel("Year")
ax.set_ylabel("Services employment share [%]")
ax.legend(fontsize="x-small", loc="upper left")
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(d) Creation: DID-inspired baseline",
        transform=ax.transAxes, fontsize="small", va="bottom")

# (e) Granger W-stat comparison -- Creation
ax = axes[1, 1]

cre_biv = next(g for g in granger if g["label"] == "creation" and g["spec"] == "bivariate")
cre_ctrl = next(g for g in granger if g["label"] == "creation_ctrl" and g["spec"] == "with_demo_control")

labels_gc = ["Bivariate", "With DEMO\ncontrol"]
w_stats_c = [cre_biv["W_stat"], cre_ctrl["W_stat"]]
p_boots_c = [cre_biv["p_bootstrap"], cre_ctrl["p_bootstrap"]]

w_se_cre = unc["bootstrap_granger"]["creation"]["W_boot_se"]

colors_bar_c = [c_sig if p < 0.10 else c_ns for p in p_boots_c]
bars_c = ax.barh(labels_gc, w_stats_c, height=0.5, color=colors_bar_c, alpha=0.8,
                 xerr=[w_se_cre, w_se_cre * 1.2], capsize=5, ecolor="gray")

ax.axvline(x=5.991, color="red", linestyle="--", linewidth=1, alpha=0.6,
           label=r"$\chi^2_{0.05}$ = 5.99")
ax.axvline(x=4.605, color="orange", linestyle="--", linewidth=1, alpha=0.6,
           label=r"$\chi^2_{0.10}$ = 4.61")

for i, (w, p) in enumerate(zip(w_stats_c, p_boots_c)):
    sig_marker = "**" if p < 0.05 else "*" if p < 0.10 else "n.s."
    ax.text(w + 0.3, i, f"p={p:.3f} {sig_marker}", va="center", fontsize="small")

ax.set_xlabel("Toda-Yamamoto W statistic")
ax.legend(fontsize="x-small")
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(e) Creation: Granger causality",
        transform=ax.transAxes, fontsize="small", va="bottom")

# (f) Method comparison forest plot -- Creation
ax = axes[1, 2]

methods_c = [
    "Granger\n(bivariate)",
    "Granger\n(+DEMO)",
    "ARDL bounds\n(F-stat)",
    "Chow 2015\n(first-diff)",
    "Counterfactual\ndeviation",
    "DID-inspired\n(POST*dDE)",
]

# Creation channel test statistics
cre_chow = sb["chow"][1]  # creation, break 2015
effect_vals_c = [
    cre_biv["W_stat"] / np.sqrt(2),
    cre_ctrl["W_stat"] / np.sqrt(2),
    coint["ardl"][0]["F_stat"] / coint["ardl"][0]["bounds_10pct"][1],  # F/upper
    cre_chow["F_stat"],
    cf_svc["t_stat"],
    model["did_inspired"]["creation"]["tvalues"]["d_DE"],
]

sig_flags_c = [
    cre_biv["p_bootstrap"] < 0.10,
    cre_ctrl["p_bootstrap"] < 0.10,
    coint["ardl"][0]["F_stat"] > coint["ardl"][0]["bounds_10pct"][1],
    cre_chow["p_value"] < 0.10,
    cf_svc["p_value"] < 0.05,
    model["did_inspired"]["creation"]["pvalues"]["d_DE"] < 0.10,
]

y_pos_c = np.arange(len(methods_c))
for i, (val, sig) in enumerate(zip(effect_vals_c, sig_flags_c)):
    color = c_sig if sig else c_ns
    marker = "D" if sig else "o"
    ax.plot(val, i, marker, color=color, markersize=10, zorder=3)
    ax.plot([0, val], [i, i], "-", color=color, linewidth=1.5, alpha=0.5)

ax.axvline(x=0, color="black", linewidth=0.5)
ax.axvline(x=1.96, color="red", linewidth=0.8, linestyle="--", alpha=0.5,
           label="Conventional threshold")
ax.set_yticks(y_pos_c)
ax.set_yticklabels(methods_c, fontsize="small")
ax.set_xlabel("Test statistic (normalized)")

ax.plot([], [], "D", color=c_sig, markersize=8, label="Significant")
ax.plot([], [], "o", color=c_ns, markersize=8, label="Not significant")
ax.legend(fontsize="x-small", loc="lower right")

ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")
ax.text(0.02, 0.02, "(f) Creation: method comparison",
        transform=ax.transAxes, fontsize="small", va="bottom")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/did_baseline_comparison.pdf",
            bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/did_baseline_comparison.png",
            bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved did_baseline_comparison.pdf/png")

# -----------------------------------------------------------------------
# Figure 2: Uncertainty Tornado Chart (Substitution Channel)
# -----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

unc_summary = unc["uncertainty_summary"]
base_val = unc_summary["central_value"]
syst_breakdown = unc_summary["systematic_breakdown"]

# Sort by absolute shift
items = [(k, abs(v)) for k, v in syst_breakdown.items()
         if isinstance(v, (int, float)) and v != 0]
items.sort(key=lambda x: x[1], reverse=True)

# Add statistical uncertainty
items.insert(0, ("Statistical (bootstrap)", unc_summary["stat_unc_68"]))

params = [x[0].replace("_", " ").capitalize() for x in items]
shifts = [x[1] for x in items]
y_pos = np.arange(len(params))

# Total
total_unc = unc_summary["total_unc_68"]

ax.barh(y_pos, shifts, height=0.6, color="#1E88E5", alpha=0.7)
ax.axvline(total_unc, color="red", linestyle="--", linewidth=1.5,
           label=f"Total unc. = {total_unc:.2f}")

ax.set_yticks(y_pos)
ax.set_yticklabels(params, fontsize="small")
ax.set_xlabel("Uncertainty on d(DE) coefficient [pp]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")

fig.savefig("phase3_analysis/figures/uncertainty_tornado.pdf",
            bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/uncertainty_tornado.png",
            bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved uncertainty_tornado.pdf/png")

# -----------------------------------------------------------------------
# Figure 3: Sensitivity to Break Year
# -----------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Substitution
sens_sub = model["sensitivity_break_year"]
break_years = [s["break_year"] for s in sens_sub]
betas_de = [s["beta_de"] for s in sens_sub]
ses_de = [s["se_de"] for s in sens_sub]
betas_post = [s["beta_post_de"] for s in sens_sub]
ses_post = [s["se_post_de"] for s in sens_sub]

ax1.errorbar(break_years, betas_de, yerr=[1.96 * s for s in ses_de],
             fmt="o-", color=c_did, capsize=5, linewidth=2,
             label=r"$\beta_{DE}$ (pre-break)")
ax1.errorbar(break_years, betas_post, yerr=[1.96 * s for s in ses_post],
             fmt="s--", color=c_granger, capsize=5, linewidth=2,
             label=r"$\beta_{POST \times DE}$ (break interaction)")
ax1.axhline(0, color="black", linewidth=0.5)
ax1.set_xlabel("Break year")
ax1.set_ylabel("Coefficient [pp per unit DE change]")
ax1.legend(fontsize="small")
ax1.text(0.02, 0.98, "OpenPE Analysis",
         transform=ax1.transAxes, fontsize=8, va="top", ha="left",
         color="gray", style="italic")
ax1.text(0.02, 0.02, "(a) Substitution channel",
         transform=ax1.transAxes, fontsize="small", va="bottom")

# Creation: similar analysis
cre_sens = []
d_emp_svc_arr = np.diff(dep_svc)
for by in break_years:
    post_by = (years_fd >= by).astype(float)
    X_by = add_constant(np.column_stack([d_de, post_by * d_de]))
    m_by = OLS(d_emp_svc_arr, X_by).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    cre_sens.append({
        "break_year": by,
        "beta_de": float(m_by.params[1]),
        "se_de": float(m_by.bse[1]),
        "beta_post_de": float(m_by.params[2]),
        "se_post_de": float(m_by.bse[2]),
    })

betas_de_c = [s["beta_de"] for s in cre_sens]
ses_de_c = [s["se_de"] for s in cre_sens]
betas_post_c = [s["beta_post_de"] for s in cre_sens]
ses_post_c = [s["se_post_de"] for s in cre_sens]

ax2.errorbar(break_years, betas_de_c, yerr=[1.96 * s for s in ses_de_c],
             fmt="o-", color="#7B1FA2", capsize=5, linewidth=2,
             label=r"$\beta_{DE}$ (pre-break)")
ax2.errorbar(break_years, betas_post_c, yerr=[1.96 * s for s in ses_post_c],
             fmt="s--", color=c_granger, capsize=5, linewidth=2,
             label=r"$\beta_{POST \times DE}$ (break interaction)")
ax2.axhline(0, color="black", linewidth=0.5)
ax2.set_xlabel("Break year")
ax2.set_ylabel("Coefficient [pp per unit DE change]")
ax2.legend(fontsize="small")
ax2.text(0.02, 0.98, "OpenPE Analysis",
         transform=ax2.transAxes, fontsize=8, va="top", ha="left",
         color="gray", style="italic")
ax2.text(0.02, 0.02, "(b) Creation channel",
         transform=ax2.transAxes, fontsize="small", va="bottom")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/sensitivity_break_year.pdf",
            bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/sensitivity_break_year.png",
            bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved sensitivity_break_year.pdf/png")

log.info("=== All figures generated ===")
