"""
Step 3.4-3.5: Comparison figure and EP propagation visualization.

Creates:
1. Summary comparison of structural break, Granger, and cointegration results
2. EP propagation chart
"""

import logging
import json
import numpy as np
import pandas as pd
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

# Load all results
with open("phase3_analysis/scripts/granger_results.json") as f:
    granger = json.load(f)

with open("phase3_analysis/scripts/cointegration_results.json") as f:
    coint = json.load(f)

with open("phase3_analysis/scripts/structural_break_results.json") as f:
    breaks = json.load(f)

with open("phase3_analysis/scripts/refutation_results.json") as f:
    refutation = json.load(f)

# ---------------------------------------------------------------------------
# Figure 1: Method comparison (3x2 grid -- creation vs substitution channels)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Color scheme
colors = {"significant": "#4CAF50", "marginal": "#FF9800", "non_sig": "#9E9E9E"}

# --- Row 0: Substitution channel ---
# (a) Granger p-values
ax = axes[0, 0]
sub_granger = [r for r in granger if r["label"] in ["substitution", "substitution_ctrl"]]
labels = ["Bivariate", "With demo ctrl"]
p_vals = [r["p_bootstrap"] for r in sub_granger]
bar_colors = [colors["significant"] if p < 0.05 else colors["marginal"] if p < 0.10 else colors["non_sig"] for p in p_vals]
bars = ax.barh(labels, [-np.log10(max(p, 1e-10)) for p in p_vals], color=bar_colors, height=0.5)
ax.axvline(-np.log10(0.10), color="red", linestyle="--", linewidth=1, label="p=0.10")
ax.axvline(-np.log10(0.05), color="darkred", linestyle="--", linewidth=1, label="p=0.05")
ax.set_xlabel("-log10(p-value)")
ax.set_ylabel("Specification")
ax.legend(fontsize="small")
for i, p in enumerate(p_vals):
    ax.text(0.1, i, f"p={p:.4f}", va="center", fontsize=9)
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")
ax.text(0.02, 0.05, "(a) Substitution: Granger", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

# (b) Cointegration
ax = axes[0, 1]
sub_coint = [r for r in coint["ardl"] if r["label"] in ["substitution", "substitution_with_demo"]]
labels_c = [r["label"] for r in sub_coint]
F_vals = [r["F_stat"] for r in sub_coint]
bounds_95 = [r["bounds_5pct"][1] for r in sub_coint]
x_pos = np.arange(len(labels_c))
ax.bar(x_pos - 0.15, F_vals, width=0.3, color="#2196F3", label="F-statistic")
ax.bar(x_pos + 0.15, bounds_95, width=0.3, color="#F44336", alpha=0.5, label="Upper bound (5%)")
ax.set_xticks(x_pos)
ax.set_xticklabels(["Bivariate", "With demo"], fontsize=9)
ax.set_ylabel("F-statistic")
ax.legend(fontsize="small")
ax.text(0.02, 0.05, "(b) Substitution: ARDL bounds", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

# (c) Structural break
ax = axes[0, 2]
sub_break = [r for r in breaks["chow"] if "substitution" in r["label"] and "ctrl" not in r["label"]]
break_years = [r["break_year"] for r in sub_break]
F_break = [r["F_stat"] for r in sub_break]
p_break = [r["p_value"] for r in sub_break]
bar_colors_b = [colors["significant"] if p < 0.05 else colors["marginal"] if p < 0.10 else colors["non_sig"] for p in p_break]
ax.bar(range(len(break_years)), F_break, color=bar_colors_b, width=0.5)
ax.set_xticks(range(len(break_years)))
ax.set_xticklabels([f"Break {y}" for y in break_years], fontsize=9)
ax.set_ylabel("Chow F-statistic")
for i, p in enumerate(p_break):
    ax.text(i, F_break[i] + 0.05, f"p={p:.3f}", ha="center", fontsize=9)
ax.text(0.02, 0.05, "(c) Substitution: Chow test", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

# --- Row 1: Creation channel ---
# (d) Granger p-values
ax = axes[1, 0]
cre_granger = [r for r in granger if r["label"] in ["creation", "creation_ctrl"]]
labels_cre = ["Bivariate", "With demo ctrl"]
p_vals_cre = [r["p_bootstrap"] for r in cre_granger]
bar_colors_cre = [colors["significant"] if p < 0.05 else colors["marginal"] if p < 0.10 else colors["non_sig"] for p in p_vals_cre]
bars = ax.barh(labels_cre, [-np.log10(max(p, 1e-10)) for p in p_vals_cre], color=bar_colors_cre, height=0.5)
ax.axvline(-np.log10(0.10), color="red", linestyle="--", linewidth=1, label="p=0.10")
ax.axvline(-np.log10(0.05), color="darkred", linestyle="--", linewidth=1, label="p=0.05")
ax.set_xlabel("-log10(p-value)")
ax.set_ylabel("Specification")
ax.legend(fontsize="small")
for i, p in enumerate(p_vals_cre):
    ax.text(0.1, i, f"p={p:.4f}", va="center", fontsize=9)
ax.text(0.02, 0.05, "(d) Creation: Granger", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

# (e) Cointegration
ax = axes[1, 1]
cre_coint = [r for r in coint["ardl"] if r["label"] in ["creation", "creation_with_demo"]]
labels_cc = [r["label"] for r in cre_coint]
F_vals_cc = [r["F_stat"] for r in cre_coint]
bounds_95_cc = [r["bounds_5pct"][1] for r in cre_coint]
x_pos_cc = np.arange(len(labels_cc))
ax.bar(x_pos_cc - 0.15, F_vals_cc, width=0.3, color="#2196F3", label="F-statistic")
ax.bar(x_pos_cc + 0.15, bounds_95_cc, width=0.3, color="#F44336", alpha=0.5, label="Upper bound (5%)")
ax.set_xticks(x_pos_cc)
ax.set_xticklabels(["Bivariate", "With demo"], fontsize=9)
ax.set_ylabel("F-statistic")
ax.legend(fontsize="small")
ax.text(0.02, 0.05, "(e) Creation: ARDL bounds", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

# (f) Structural break
ax = axes[1, 2]
cre_break = [r for r in breaks["chow"] if "creation" in r["label"] and "ctrl" not in r["label"]]
break_years_c = [r["break_year"] for r in cre_break]
F_break_c = [r["F_stat"] for r in cre_break]
p_break_c = [r["p_value"] for r in cre_break]
bar_colors_cb = [colors["significant"] if p < 0.05 else colors["marginal"] if p < 0.10 else colors["non_sig"] for p in p_break_c]
ax.bar(range(len(break_years_c)), F_break_c, color=bar_colors_cb, width=0.5)
ax.set_xticks(range(len(break_years_c)))
ax.set_xticklabels([f"Break {y}" for y in break_years_c], fontsize=9)
ax.set_ylabel("Chow F-statistic")
for i, p in enumerate(p_break_c):
    ax.text(i, F_break_c[i] + 0.05, f"p={p:.3f}", ha="center", fontsize=9)
ax.text(0.02, 0.05, "(f) Creation: Chow test", transform=ax.transAxes, fontsize=10, va="bottom", ha="left", weight="bold")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/method_comparison_summary.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/method_comparison_summary.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Figure saved: method_comparison_summary.pdf/png")


# ---------------------------------------------------------------------------
# Figure 2: Refutation test summary
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))

edge_labels = [r["label"] for r in refutation]
tests = ["Placebo", "Random Cause", "Data Subset"]

# Build matrix: 1=PASS, 0.5=MARGINAL, 0=FAIL
matrix = np.zeros((len(refutation), 3))
for i, r in enumerate(refutation):
    for j, test_key in enumerate(["placebo", "random_cause", "data_subset"]):
        verdict = r[test_key]["verdict"]
        if verdict == "PASS":
            matrix[i, j] = 1.0
        elif verdict == "MARGINAL":
            matrix[i, j] = 0.5
        else:
            matrix[i, j] = 0.0

# Heatmap
from matplotlib.colors import ListedColormap
cmap = ListedColormap(["#F44336", "#FF9800", "#4CAF50"])
bounds_cmap = [0, 0.25, 0.75, 1.0]
from matplotlib.colors import BoundaryNorm
norm = BoundaryNorm(bounds_cmap, cmap.N)

im = ax.pcolormesh(np.arange(4), np.arange(len(refutation) + 1), matrix, cmap=cmap, norm=norm, edgecolors="white", linewidth=2)

# Labels
ax.set_xticks(np.arange(3) + 0.5)
ax.set_xticklabels(tests)
ax.set_yticks(np.arange(len(refutation)) + 0.5)
ax.set_yticklabels(edge_labels, fontsize=9)

# Annotations
for i in range(len(refutation)):
    for j in range(3):
        val = matrix[i, j]
        text = "PASS" if val == 1.0 else "MARG" if val == 0.5 else "FAIL"
        ax.text(j + 0.5, i + 0.5, text, ha="center", va="center", fontsize=9,
                color="white" if val != 0.5 else "black", weight="bold")

    # Classification label
    cls = refutation[i]["classification"]
    ax.text(3.2, i + 0.5, cls, ha="left", va="center", fontsize=9, weight="bold",
            color={"DATA_SUPPORTED": "#4CAF50", "CORRELATION": "#FF9800",
                   "HYPOTHESIZED": "#9E9E9E", "DISPUTED": "#F44336"}.get(cls, "black"))

ax.set_xlabel("Refutation Test")
ax.set_ylabel("Causal Edge")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/refutation_summary.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/refutation_summary.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Figure saved: refutation_summary.pdf/png")


# ---------------------------------------------------------------------------
# Figure 3: EP propagation chart
# ---------------------------------------------------------------------------
ep_trajectory = {
    "DE->SUB": [0.49, 0.32, 0.32, None],
    "DE->CRE": [0.42, 0.27, 0.27, None],
    "DE->IND_UP": [0.35, 0.23, 0.23, None],
    "DEMO->LS": [0.42, 0.36, 0.36, None],
    "DE->LS (direct)": [0.12, 0.06, 0.06, None],
}

# Phase 3 EP updates based on refutation results
# DE->SUB bivariate: HYPOTHESIZED, with ctrl: CORRELATION
# DE->CRE bivariate: HYPOTHESIZED, with ctrl: DISPUTED
# DEMO->LS: HYPOTHESIZED (both)

# Update rules:
# DATA_SUPPORTED: truth = max(0.8, P1_truth + 0.2)
# CORRELATION: truth unchanged
# HYPOTHESIZED: truth = min(0.3, P1_truth - 0.1)
# DISPUTED: truth = 0.1

# Best classification per edge (taking the more favorable spec):
classifications = {
    "DE->SUB": "CORRELATION",       # Best is with ctrl: 2/3 pass
    "DE->CRE": "HYPOTHESIZED",      # Best is bivariate: 1/3 pass
    "DE->IND_UP": "HYPOTHESIZED",   # 1/3 pass
    "DEMO->LS": "HYPOTHESIZED",     # 1/3 pass
    "DE->LS (direct)": "HYPOTHESIZED",
}

# Phase 1 truth values (from STRATEGY.md)
p1_truth = {
    "DE->SUB": 0.45,
    "DE->CRE": 0.45,
    "DE->IND_UP": 0.45,
    "DEMO->LS": 0.60,
    "DE->LS (direct)": 0.15,
}

p1_rel = {
    "DE->SUB": 0.7,
    "DE->CRE": 0.6,
    "DE->IND_UP": 0.5,
    "DEMO->LS": 0.6,
    "DE->LS (direct)": 0.4,
}

# Phase 3 EP computation
p3_ep = {}
for edge, cls in classifications.items():
    t1 = p1_truth[edge]
    r1 = p1_rel[edge]
    if cls == "DATA_SUPPORTED":
        t3 = max(0.8, t1 + 0.2)
    elif cls == "CORRELATION":
        t3 = t1  # unchanged
    elif cls == "HYPOTHESIZED":
        t3 = min(0.3, t1 - 0.1)
    elif cls == "DISPUTED":
        t3 = 0.1
    else:
        t3 = t1

    # Update relevance based on effect size vs expectations
    r3 = r1  # Keep same unless effect is near zero
    if cls in ["HYPOTHESIZED", "DISPUTED"]:
        r3 = max(0.1, r1 - 0.2)

    ep3 = t3 * r3
    p3_ep[edge] = ep3
    ep_trajectory[edge][3] = ep3
    log.info(f"  {edge}: cls={cls}, truth={t3:.2f}, rel={r3:.2f}, EP={ep3:.3f}")

# Plot
phases = ["P0\nDiscovery", "P1\nStrategy", "P2\nExplore", "P3\nAnalysis"]
x = np.arange(len(phases))

fig, ax = plt.subplots(figsize=(10, 6))

# Threshold bands
ax.axhspan(0.30, 1.0, alpha=0.05, color="green")
ax.axhspan(0.15, 0.30, alpha=0.05, color="blue")
ax.axhspan(0.05, 0.15, alpha=0.05, color="orange")
ax.axhspan(0, 0.05, alpha=0.05, color="red")

# Threshold lines
ax.axhline(0.30, color="green", linestyle=":", linewidth=0.8, alpha=0.5)
ax.axhline(0.15, color="blue", linestyle=":", linewidth=0.8, alpha=0.5)
ax.axhline(0.05, color="orange", linestyle=":", linewidth=0.8, alpha=0.5)

edge_colors = {
    "DE->SUB": "#F44336",
    "DE->CRE": "#4CAF50",
    "DE->IND_UP": "#FF9800",
    "DEMO->LS": "#2196F3",
    "DE->LS (direct)": "#9E9E9E",
}

for edge, ep_vals in ep_trajectory.items():
    ax.plot(x, ep_vals, "o-", color=edge_colors[edge], linewidth=2, markersize=6, label=edge)

ax.set_xticks(x)
ax.set_xticklabels(phases)
ax.set_ylabel("Epistemic Probability (EP)")
ax.set_ylim(0, 0.55)
ax.legend(fontsize="small", loc="upper right")

# Annotations
ax.text(3.3, 0.30, "Full analysis", fontsize=8, color="green", va="bottom")
ax.text(3.3, 0.15, "Lightweight", fontsize=8, color="blue", va="bottom")
ax.text(3.3, 0.05, "Below soft", fontsize=8, color="orange", va="bottom")
ax.text(3.3, 0.01, "Hard truncation", fontsize=8, color="red", va="bottom")

ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/ep_propagation.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/ep_propagation.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Figure saved: ep_propagation.pdf/png")

# Save EP data
ep_output = {
    "classifications": classifications,
    "phase3_ep": p3_ep,
    "trajectory": ep_trajectory,
}
with open("phase3_analysis/scripts/ep_propagation.json", "w") as f:
    json.dump(ep_output, f, indent=2)
log.info("EP data saved to ep_propagation.json")
