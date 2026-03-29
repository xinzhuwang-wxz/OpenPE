"""
Step 5b: EP Updates and Classification.

- Update truth values based on refutation results
- Recalculate all EP values
- Apply post-refutation labels
- Generate EP decay chart

Produces: phase3_analysis/figures/fig_p3_08_*.pdf/png
"""
import json
import logging
import os

import matplotlib.pyplot as plt
import numpy as np
from rich.logging import RichHandler

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

DATA_DIR = "phase3_analysis/data"
FIG_DIR = "phase3_analysis/figures"

os.makedirs(FIG_DIR, exist_ok=True)

# Load results
with open(f"{DATA_DIR}/its_results.json") as f:
    its = json.load(f)
with open(f"{DATA_DIR}/bsts_results.json") as f:
    bsts = json.load(f)
with open(f"{DATA_DIR}/refutation_results.json") as f:
    refutation = json.load(f)
with open(f"{DATA_DIR}/compositional_results.json") as f:
    comp = json.load(f)

# =============================================================================
# EP Update Protocol (per Phase 3 CLAUDE.md Step 3.4)
# =============================================================================

# Phase 1 EP values (from STRATEGY.md Section 3)
phase1_edges = {
    "Policy -> Industry Collapse": {
        "dag": "All", "phase0_ep": 0.6, "phase1_truth": 0.8, "phase1_relevance": 0.7,
        "phase1_ep": 0.6, "confidence": "HIGH",
    },
    "Industry Collapse -> Reduced Tutoring": {
        "dag": "1", "phase0_ep": 0.2, "phase1_truth": 0.5, "phase1_relevance": 0.4,
        "phase1_ep": 0.2, "confidence": "MEDIUM",
    },
    "Reduced Tutoring -> Total Expenditure": {
        "dag": "1", "phase0_ep": 0.2, "phase1_truth": 0.3, "phase1_relevance": 0.4,
        "phase1_ep": 0.1, "confidence": "LOW",
    },
    "Policy -> Underground Market": {
        "dag": "2", "phase0_ep": 0.5, "phase1_truth": 0.3, "phase1_relevance": 0.7,
        "phase1_ep": 0.2, "confidence": "LOW",
    },
    "Underground -> Higher Prices": {
        "dag": "2", "phase0_ep": 0.2, "phase1_truth": 0.3, "phase1_relevance": 0.4,
        "phase1_ep": 0.1, "confidence": "LOW",
    },
    "Competitive Pressure -> Inelastic Demand": {
        "dag": "2", "phase0_ep": 0.5, "phase1_truth": 0.6, "phase1_relevance": 0.7,
        "phase1_ep": 0.4, "confidence": "MEDIUM",
    },
    "Income -> Differential Access": {
        "dag": "2", "phase0_ep": 0.4, "phase1_truth": 0.6, "phase1_relevance": 0.6,
        "phase1_ep": 0.3, "confidence": "MEDIUM",
    },
    "Public Spending -> Crowding-In": {
        "dag": "3", "phase0_ep": 0.3, "phase1_truth": 0.6, "phase1_relevance": 0.4,
        "phase1_ep": 0.2, "confidence": "MEDIUM",
    },
    "Policy -> Aggregate Spending (net)": {
        "dag": "All", "phase0_ep": 0.3, "phase1_truth": 0.5, "phase1_relevance": 0.5,
        "phase1_ep": 0.3, "confidence": "MEDIUM",
        "note": "Primary testable edge via ITS/BSTS",
    },
}

# =============================================================================
# Apply Phase 3 updates based on refutation results
# =============================================================================

# The primary tested edge is "Policy -> Aggregate Spending (net)"
# Refutation classification: CORRELATION for all three series
# COVID placebo FAIL means we cannot distinguish policy from COVID

# Classification-to-truth update rules (from Phase 3 CLAUDE.md):
# DATA_SUPPORTED: truth = max(0.8, phase1_truth + 0.2)
# CORRELATION: truth = phase1_truth (unchanged)
# HYPOTHESIZED: truth = min(0.3, phase1_truth - 0.1)
# DISPUTED: truth = 0.1

# Effect size comparison for relevance update:
# Expected: 5-15% (from strategy)
# Observed ITS: -23.7% national (larger than expected)
# Observed BSTS: -18.8% national
# But: COVID placebo shows similar magnitude, so the "effect" is likely
# confounded. Relevance should decrease because the signal is ambiguous.

log.info("=" * 60)
log.info("EP UPDATE PROTOCOL")
log.info("=" * 60)

# Primary edge update
primary_class = refutation["national"]["classification"]
log.info(f"\nPrimary edge classification: {primary_class}")

# ITS and BSTS agreement check
its_shift = its["national"]["primary"]["level_shift"]
bsts_effect = bsts["national"]["mean_effect"]
agreement_pct = abs(its_shift - bsts_effect) / abs(its_shift) * 100
log.info(f"ITS level shift: {its_shift:.1f}")
log.info(f"BSTS mean effect: {bsts_effect:.1f}")
log.info(f"Method disagreement: {agreement_pct:.1f}%")
methods_agree = agreement_pct < 50  # <50% difference threshold
log.info(f"Methods agree (<50% difference): {methods_agree}")

# Update each edge
phase3_edges = {}

for edge_name, edge_data in phase1_edges.items():
    p1_truth = edge_data["phase1_truth"]
    p1_rel = edge_data["phase1_relevance"]
    p1_ep = edge_data["phase1_ep"]

    # Default: no change
    p3_truth = p1_truth
    p3_rel = p1_rel
    classification = "NOT_TESTED"
    change_reason = "Not directly tested in Phase 3"

    # Primary tested edge
    if edge_name == "Policy -> Aggregate Spending (net)":
        classification = primary_class  # CORRELATION

        # CORRELATION: truth unchanged
        p3_truth = p1_truth

        # Relevance update: effect is larger than expected but COVID-confounded
        # COVID confounding reduces effective relevance of the policy-specific signal
        p3_rel = max(0.1, p1_rel - 0.1)  # Decrease because COVID confounding

        change_reason = (
            f"CORRELATION: 2/3 core refutation tests passed, jackknife FAIL "
            f"(max dev 51.9%), COVID placebo FAIL. ITS & BSTS agree in direction "
            f"(-23.7% vs -18.8%) but COVID confounding is severe. "
            f"Relevance decreased due to COVID confounding."
        )

    elif edge_name == "Policy -> Industry Collapse":
        # A1 fix: Cannot be DATA_SUPPORTED without refutation battery.
        # Carried forward from literature synthesis -- not tested with
        # refutation battery in this analysis.  Highest achievable
        # classification without refutation is CORRELATION.
        classification = "CORRELATION"
        p3_truth = p1_truth  # CORRELATION: truth unchanged from Phase 1 (0.8)
        p3_rel = p1_rel      # unchanged -- well-documented
        change_reason = (
            "CORRELATION (highest achievable without refutation battery). "
            "Industry collapse is well-documented (92-96% closures) but was "
            "not tested with the analysis's own refutation battery. "
            "Carried forward from literature synthesis."
        )

    elif edge_name == "Industry Collapse -> Reduced Tutoring":
        # Compositional analysis: education share dropped 0.7pp, z-score -1.05
        # Not uniquely different from other categories
        classification = "CORRELATION"
        p3_truth = p1_truth  # unchanged
        p3_rel = max(0.1, p1_rel - 0.1)
        change_reason = (
            "Compositional analysis shows education share dropped 0.7pp but z-score "
            "is only -1.05 (not unique among categories). Direction is consistent "
            "but effect is not distinguishable from general shifts."
        )

    elif edge_name == "Reduced Tutoring -> Total Expenditure":
        # Per-birth normalization eliminates the level shift (p=0.48)
        classification = "HYPOTHESIZED"
        p3_truth = min(0.3, p1_truth - 0.1)
        p3_rel = 0.1  # Near-zero relevance after normalization
        change_reason = (
            "Per-birth normalization eliminates the apparent level shift (p=0.48). "
            "Any aggregate decline is attributable to demographic decline, not "
            "per-child spending reduction."
        )

    elif edge_name in ["Policy -> Underground Market", "Underground -> Higher Prices"]:
        classification = "HYPOTHESIZED"
        # B4 fix: HYPOTHESIZED mechanical truth formula:
        # truth = min(0.3, phase1_truth - 0.1)
        p3_truth = min(0.3, p1_truth - 0.1)  # 0.3 -> 0.2 for both
        p3_rel = p1_rel
        change_reason = (
            "HYPOTHESIZED: mechanical truth update applied "
            f"(min(0.3, {p1_truth} - 0.1) = {p3_truth:.1f}). "
            "Beyond analytical horizon: no systematic data to test."
        )

    elif edge_name == "Competitive Pressure -> Inelastic Demand":
        classification = "CORRELATION"
        p3_truth = p1_truth
        p3_rel = p1_rel
        change_reason = "Not directly tested. CIEFR-HS evidence is pre-policy only."

    elif edge_name == "Income -> Differential Access":
        # Urban shift larger than rural (ITS: -711 urban vs -191 rural)
        classification = "CORRELATION"
        p3_truth = p1_truth
        urban_shift = its["urban"]["primary"]["level_shift"]
        rural_shift = its["rural"]["primary"]["level_shift"]
        p3_rel = min(0.9, p1_rel + 0.1) if abs(urban_shift) > 2 * abs(rural_shift) else p1_rel
        change_reason = (
            f"Urban ITS shift ({urban_shift:.0f}) is {abs(urban_shift/rural_shift):.1f}x larger than "
            f"rural ({rural_shift:.0f}), consistent with higher urban exposure. "
            f"But parallel trends are violated, so this is descriptive only."
        )

    elif edge_name == "Public Spending -> Crowding-In":
        classification = "HYPOTHESIZED"
        # B4 fix: HYPOTHESIZED mechanical truth formula:
        # truth = min(0.3, phase1_truth - 0.1)
        p3_truth = min(0.3, p1_truth - 0.1)  # 0.6 -> 0.3 (capped)
        p3_rel = p1_rel
        change_reason = (
            "HYPOTHESIZED: mechanical truth update applied "
            f"(min(0.3, {p1_truth} - 0.1) = {p3_truth:.1f}). "
            "Lightweight assessment only. Public spending maintained above "
            "4% GDP but no causal test possible."
        )

    # Compute Phase 3 EP
    p3_ep = round(p3_truth * p3_rel, 2)

    phase3_edges[edge_name] = {
        "dag": edge_data["dag"],
        "phase0_ep": edge_data["phase0_ep"],
        "phase1_ep": p1_ep,
        "phase3_truth": round(p3_truth, 2),
        "phase3_relevance": round(p3_rel, 2),
        "phase3_ep": p3_ep,
        "classification": classification,
        "change_reason": change_reason,
    }

    log.info(f"\n{edge_name}:")
    log.info(f"  Phase 1 EP: {p1_ep:.2f} -> Phase 3 EP: {p3_ep:.2f}")
    log.info(f"  Classification: {classification}")
    log.info(f"  Reason: {change_reason[:100]}...")


# =============================================================================
# Chain-level Joint EP recomputation
# =============================================================================
log.info("\n\n" + "=" * 60)
log.info("CHAIN-LEVEL JOINT EP")
log.info("=" * 60)

chains = {
    "DAG 1: Policy -> Industry -> Tutoring -> Total": [
        "Policy -> Industry Collapse",
        "Industry Collapse -> Reduced Tutoring",
        "Reduced Tutoring -> Total Expenditure",
    ],
    "DAG 2: Policy -> Underground -> Prices": [
        "Policy -> Underground Market",
        "Underground -> Higher Prices",
    ],
    "DAG 3: Public -> Crowding-In": [
        "Public Spending -> Crowding-In",
    ],
}

for chain_name, edges in chains.items():
    eps = [phase3_edges[e]["phase3_ep"] for e in edges]
    joint = 1.0
    for ep in eps:
        joint *= ep
    joint = round(joint, 4)

    status = "HARD TRUNCATION" if joint < 0.05 else ("SOFT TRUNCATION" if joint < 0.15 else "ACTIVE")
    log.info(f"\n{chain_name}:")
    log.info(f"  Edge EPs: {' x '.join(f'{ep:.2f}' for ep in eps)} = Joint EP {joint:.4f}")
    log.info(f"  Status: {status}")


# =============================================================================
# EP Decay Chart
# =============================================================================
log.info("\nGenerating EP decay chart...")

key_edges = [
    "Policy -> Industry Collapse",
    "Policy -> Aggregate Spending (net)",
    "Industry Collapse -> Reduced Tutoring",
    "Reduced Tutoring -> Total Expenditure",
    "Income -> Differential Access",
    "Competitive Pressure -> Inelastic Demand",
]

phases = ["P0\nDiscovery", "P1\nStrategy", "P3\nAnalysis"]
x = np.arange(len(phases))

fig, ax = plt.subplots(figsize=(10, 6))

# Threshold bands
ax.axhspan(0.30, 1.0, alpha=0.06, color="green")
ax.axhspan(0.15, 0.30, alpha=0.06, color="blue")
ax.axhspan(0.05, 0.15, alpha=0.06, color="orange")
ax.axhspan(0, 0.05, alpha=0.06, color="red")

# Threshold lines
for thresh, label in [(0.30, "Full analysis"), (0.15, "Soft truncation"), (0.05, "Hard truncation")]:
    ax.axhline(thresh, color="gray", linestyle=":", linewidth=0.8, alpha=0.5)
    ax.text(len(phases) - 0.5, thresh + 0.01, label, fontsize=7, color="gray")

colors = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0", "#607D8B"]

for i, edge in enumerate(key_edges):
    e = phase3_edges[edge]
    ep_values = [e["phase0_ep"], e["phase1_ep"], e["phase3_ep"]]
    ax.plot(x, ep_values, "o-", color=colors[i], linewidth=2, markersize=6,
            label=f"{edge} [{e['classification']}]")

ax.set_xticks(x)
ax.set_xticklabels(phases)
ax.set_ylabel("Epistemic Probability (EP)")
ax.set_ylim(-0.02, 0.75)
ax.legend(fontsize="x-small", loc="upper right")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8,
        va="top", ha="left", color="gray", style="italic")

fig.savefig(f"{FIG_DIR}/fig_p3_08_ep_decay.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_08_ep_decay.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved EP decay chart to {FIG_DIR}/fig_p3_08_ep_decay.pdf")

# Save EP results
with open(f"{DATA_DIR}/ep_update_results.json", "w") as f:
    json.dump(phase3_edges, f, indent=2)

log.info(f"Saved EP results to {DATA_DIR}/ep_update_results.json")
log.info("\nStep 5b (EP Update) complete.")
