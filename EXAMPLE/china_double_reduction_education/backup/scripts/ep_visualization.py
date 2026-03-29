# Copyright 2026 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""EP decay and projection visualizations for OpenPE.

The EP decay chart is the core visualization of OpenPE — it shows
confidence bands widening as the explanatory chain extends from
empirical findings to projections.

Reference: OpenPE spec Section 3.2 Phase 4, Step 4
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


# OpenPE color palette
COLORS = {
    "high": "#2ecc71",      # green — high confidence
    "medium": "#f39c12",    # orange — medium
    "low": "#e74c3c",       # red — low confidence
    "band": "#3498db",      # blue — confidence band
    "baseline": "#2c3e50",  # dark — baseline
}


def plot_ep_decay(
    node_labels: list[str],
    ep_values: list[float],
    joint_eps: list[float],
    output_path: Path,
    title: str = "Explanatory Power Decay Along Chain",
    figsize: tuple = (12, 5),
) -> Path:
    """Generate the EP decay chart — core OpenPE visualization.

    Shows per-node EP (bars) and joint EP (line) along the chain,
    with confidence band coloring.

    Args:
        node_labels: names for each chain node
        ep_values: EP value per node
        joint_eps: cumulative joint EP at each position
        output_path: where to save the figure
        title: figure title
        figsize: figure dimensions
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[2, 1],
                                     sharex=True, gridspec_kw={"hspace": 0.05})

    x = np.arange(len(node_labels))

    # Top: per-node EP as bars
    bar_colors = []
    for ep in ep_values:
        if ep >= 0.5:
            bar_colors.append(COLORS["high"])
        elif ep >= 0.2:
            bar_colors.append(COLORS["medium"])
        else:
            bar_colors.append(COLORS["low"])

    ax1.bar(x, ep_values, color=bar_colors, alpha=0.8, edgecolor="white", linewidth=0.5)
    ax1.set_ylabel("Node EP", fontsize=11)
    ax1.set_ylim(0, 1.05)
    ax1.axhline(y=0.30, color="gray", linestyle="--", alpha=0.5, label="Sub-chain threshold (0.30)")
    ax1.legend(fontsize=9, loc="upper right")
    ax1.set_title(title, fontsize=13, fontweight="bold")

    # Bottom: joint EP as line with confidence coloring
    ax2.plot(x, joint_eps, "o-", color=COLORS["baseline"], linewidth=2, markersize=6)
    ax2.fill_between(x, 0, joint_eps, alpha=0.15, color=COLORS["band"])
    ax2.axhline(y=0.15, color=COLORS["medium"], linestyle="--", alpha=0.7, label="Soft truncation (0.15)")
    ax2.axhline(y=0.05, color=COLORS["low"], linestyle="--", alpha=0.7, label="Hard truncation (0.05)")
    ax2.set_ylabel("Joint EP", fontsize=11)
    ax2.set_ylim(0, max(joint_eps) * 1.2 if joint_eps else 1.0)
    ax2.set_xticks(x)
    ax2.set_xticklabels(node_labels, rotation=30, ha="right", fontsize=9)
    ax2.legend(fontsize=9, loc="upper right")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_scenario_comparison(
    time_points: list[float],
    scenarios: dict[str, list[float]],
    confidence_band: tuple[list[float], list[float]] | None = None,
    output_path: Path = Path("scenario_comparison.png"),
    title: str = "Scenario Projections",
    xlabel: str = "Time",
    ylabel: str = "Outcome",
    figsize: tuple = (10, 6),
) -> Path:
    """Plot scenario comparison with optional confidence envelope.

    Args:
        time_points: x-axis values
        scenarios: dict mapping scenario name → outcome values
        confidence_band: (lower, upper) bounds for shading
        output_path: where to save
    """
    fig, ax = plt.subplots(figsize=figsize)

    scenario_styles = {
        "baseline": {"color": COLORS["baseline"], "linewidth": 2.5, "linestyle": "-"},
        "optimistic": {"color": COLORS["high"], "linewidth": 1.5, "linestyle": "--"},
        "pessimistic": {"color": COLORS["low"], "linewidth": 1.5, "linestyle": "--"},
    }

    for name, values in scenarios.items():
        style = scenario_styles.get(name, {"color": "gray", "linewidth": 1, "linestyle": ":"})
        ax.plot(time_points[:len(values)], values, label=name, **style)

    if confidence_band:
        lower, upper = confidence_band
        ax.fill_between(
            time_points[:len(lower)], lower, upper,
            alpha=0.15, color=COLORS["band"], label="95% confidence band",
        )

    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_sensitivity_tornado(
    param_names: list[str],
    impacts: list[float],
    controllable: list[bool],
    output_path: Path = Path("sensitivity_tornado.png"),
    title: str = "Sensitivity Analysis",
    figsize: tuple = (10, 6),
) -> Path:
    """Tornado diagram showing parameter sensitivity ranking.

    Args:
        param_names: parameter names (y-axis labels)
        impacts: impact magnitudes (bar lengths)
        controllable: whether each param is controllable
    """
    fig, ax = plt.subplots(figsize=figsize)

    y = np.arange(len(param_names))
    colors = [COLORS["high"] if c else COLORS["medium"] for c in controllable]

    ax.barh(y, impacts, color=colors, alpha=0.8, edgecolor="white")
    ax.set_yticks(y)
    ax.set_yticklabels(param_names, fontsize=10)
    ax.set_xlabel("Impact on Outcome", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.invert_yaxis()

    # Legend for controllable vs exogenous
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["high"], alpha=0.8, label="Controllable"),
        Patch(facecolor=COLORS["medium"], alpha=0.8, label="Exogenous"),
    ]
    ax.legend(handles=legend_elements, fontsize=9, loc="lower right")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
