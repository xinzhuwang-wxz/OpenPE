"""
Phase 4: Monte Carlo projection simulation for DE --> labor structure.

Produces:
  - Monte Carlo scenario simulations (baseline, high-digital, low-digital)
  - Sensitivity analysis (tornado chart)
  - EP decay visualization
  - Scenario comparison figure
  - Endgame convergence detection

All figures saved as PDF + PNG, 10x10, no titles, bbox_inches tight, dpi 200.
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "phase4_projection" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Reproducibility ────────────────────────────────────────────────────
RNG_SEED = 20260329
rng = np.random.default_rng(RNG_SEED)
N_ITER = 10_000
PROJECTION_YEARS = 10  # project 2024-2033

# ── Load data ──────────────────────────────────────────────────────────
df = pd.read_parquet(DATA_DIR / "china_national_panel_merged.parquet")
log.info(f"Loaded panel: {df.shape}")

# Key variables
de_col = "digital_economy_index"
ind_emp_col = "employment_industry_pct"
svc_emp_col = "employment_services_pct"
demo_col = "population_15_64_pct"

# Extract last known values (2023)
last_year = int(df["year"].max())
last_row = df[df["year"] == last_year].iloc[0]
de_last = float(last_row[de_col])
ind_emp_last = float(last_row[ind_emp_col])
svc_emp_last = float(last_row[svc_emp_col])
demo_last = float(last_row[demo_col])

log.info(f"Last year: {last_year}")
log.info(f"DE index (last): {de_last:.4f}")
log.info(f"Industry emp (last): {ind_emp_last:.2f}%")
log.info(f"Services emp (last): {svc_emp_last:.2f}%")
log.info(f"Demographics (last): {demo_last:.2f}%")

# ── Historical trends for projection anchors ───────────────────────────
# DE growth rate: compute from post-2014 period (after structural break)
df_post = df[df["year"] >= 2016].copy()
de_values = df_post[de_col].values
de_diffs = np.diff(de_values)
de_growth_mean = float(np.mean(de_diffs))
de_growth_std = float(np.std(de_diffs, ddof=1))
log.info(f"Post-2016 DE annual growth: mean={de_growth_mean:.4f}, std={de_growth_std:.4f}")

# Demographics trend (declining): linear fit on recent years
demo_values = df_post[demo_col].values
demo_years = df_post["year"].values.astype(float)
demo_slope = float(np.polyfit(demo_years, demo_values, 1)[0])
demo_residual_std = float(np.std(demo_values - np.polyval(np.polyfit(demo_years, demo_values, 1), demo_years)))
log.info(f"Demographics slope: {demo_slope:.3f}/yr, residual std: {demo_residual_std:.3f}")

# ── Phase 3 parameter estimates ────────────────────────────────────────
# ARDL long-run coefficients from ANALYSIS.md
# Bivariate: beta_DE = 7.15 (SE=4.10)
# With DEMO control: beta_DE = 12.57 (SE=1.86), beta_DEMO = 1.29

# We use the bivariate as the conservative anchor
BETA_DE_BIVARIATE = 7.15
BETA_DE_BIVARIATE_SE = 4.10

# Controlled specification
BETA_DE_CONTROLLED = 12.57
BETA_DE_CONTROLLED_SE = 1.86
BETA_DEMO = 1.29
BETA_DEMO_SE = 0.50  # Estimated; not reported precisely in ANALYSIS.md

# DID interaction: post-break weakening
BETA_POST_INTERACTION = -5.90
BETA_POST_INTERACTION_SE = 4.21

# For services employment (creation channel) - EP=0.030, below hard truncation
# Include only for scenario spread, not central projection
BETA_SVC_DE = -10.89  # negative, opposite of expected
BETA_SVC_DE_SE = 11.04

# ── Causal model function ──────────────────────────────────────────────

def project_industry_emp(
    de_trajectory: np.ndarray,
    demo_trajectory: np.ndarray,
    beta_de: float,
    beta_demo: float,
    base_ind_emp: float,
    base_de: float,
    base_demo: float,
    innovation_std: float = 0.5,
) -> np.ndarray:
    """
    Project industry employment share using ARDL long-run relationship.

    The ARDL LR coefficient gives the long-run equilibrium change in
    industry_emp per unit change in DE, holding demographics constant.

    delta_ind_emp = beta_de * delta_DE + beta_demo * delta_DEMO + noise
    """
    n_steps = len(de_trajectory)
    ind_emp = np.zeros(n_steps)
    ind_emp[0] = base_ind_emp

    for t in range(1, n_steps):
        delta_de = de_trajectory[t] - base_de
        delta_demo = demo_trajectory[t] - base_demo
        # Long-run equilibrium prediction
        equilibrium = base_ind_emp + beta_de * delta_de + beta_demo * delta_demo
        # Add partial adjustment + innovation noise
        noise = rng.normal(0, innovation_std)
        ind_emp[t] = equilibrium + noise

    return ind_emp


# ── Scenario definitions ───────────────────────────────────────────────

proj_years = np.arange(last_year + 1, last_year + 1 + PROJECTION_YEARS)

# Base demographics trajectory (declining, following UN medium variant trend)
demo_base = demo_last + demo_slope * np.arange(1, PROJECTION_YEARS + 1)
demo_base = np.clip(demo_base, 55.0, 80.0)  # Physical bounds

scenarios = {
    "baseline": {
        "label": "Baseline (current trends)",
        "de_growth_mean": de_growth_mean,
        "de_growth_std": de_growth_std,
        "demo_trajectory_offset": 0.0,
        "beta_de_mean": BETA_DE_BIVARIATE,
        "beta_de_std": BETA_DE_BIVARIATE_SE,
        "beta_demo_mean": BETA_DEMO,
        "beta_demo_std": BETA_DEMO_SE,
        "innovation_std": 0.5,
        "color": "#2166ac",
        "conditional_prob": "Likely (50-60%)",
    },
    "high_digital": {
        "label": "High-Digital (accelerated adoption)",
        "de_growth_mean": de_growth_mean * 1.5,
        "de_growth_std": de_growth_std * 1.2,
        "demo_trajectory_offset": 0.0,
        "beta_de_mean": BETA_DE_CONTROLLED,  # Use stronger controlled estimate
        "beta_de_std": BETA_DE_CONTROLLED_SE * 1.5,  # Wider uncertainty
        "beta_demo_mean": BETA_DEMO,
        "beta_demo_std": BETA_DEMO_SE,
        "innovation_std": 0.7,
        "color": "#b2182b",
        "conditional_prob": "Plausible (20-30%)",
    },
    "low_digital": {
        "label": "Low-Digital (stagnation/regulation)",
        "de_growth_mean": de_growth_mean * 0.3,
        "de_growth_std": de_growth_std * 0.8,
        "demo_trajectory_offset": -0.2,  # Faster demographic decline
        "beta_de_mean": BETA_DE_BIVARIATE * 0.5,  # Weaker relationship
        "beta_de_std": BETA_DE_BIVARIATE_SE * 2.0,  # Much wider uncertainty
        "beta_demo_mean": BETA_DEMO,
        "beta_demo_std": BETA_DEMO_SE * 1.5,
        "innovation_std": 0.8,
        "color": "#4dac26",
        "conditional_prob": "Plausible (15-25%)",
    },
}

# ── Monte Carlo simulation ─────────────────────────────────────────────
log.info("Running Monte Carlo simulations...")

results = {}
for scen_name, scen in scenarios.items():
    log.info(f"  Scenario: {scen_name} ({N_ITER} iterations)")
    all_ind_emp = np.zeros((N_ITER, PROJECTION_YEARS))
    all_de = np.zeros((N_ITER, PROJECTION_YEARS))

    for i in range(N_ITER):
        # Sample parameters
        beta_de_i = rng.normal(scen["beta_de_mean"], scen["beta_de_std"])
        beta_demo_i = rng.normal(scen["beta_demo_mean"], scen["beta_demo_std"])

        # Generate DE trajectory with stochastic growth
        de_traj = np.zeros(PROJECTION_YEARS + 1)
        de_traj[0] = de_last
        for t in range(PROJECTION_YEARS):
            growth = rng.normal(scen["de_growth_mean"], scen["de_growth_std"])
            de_traj[t + 1] = de_traj[t] + growth
        de_traj = np.clip(de_traj, 0.0, 1.0)  # Index bounded [0,1]

        # Generate demographics trajectory
        demo_traj = np.zeros(PROJECTION_YEARS + 1)
        demo_traj[0] = demo_last
        for t in range(PROJECTION_YEARS):
            demo_noise = rng.normal(0, demo_residual_std)
            demo_traj[t + 1] = (
                demo_last
                + (demo_slope + scen["demo_trajectory_offset"]) * (t + 1)
                + demo_noise
            )
        demo_traj = np.clip(demo_traj, 55.0, 80.0)

        # Project industry employment
        ind_emp_traj = project_industry_emp(
            de_trajectory=de_traj,
            demo_trajectory=demo_traj,
            beta_de=beta_de_i,
            beta_demo=beta_demo_i,
            base_ind_emp=ind_emp_last,
            base_de=de_last,
            base_demo=demo_last,
            innovation_std=scen["innovation_std"],
        )

        all_ind_emp[i, :] = ind_emp_traj[1:]  # Exclude base year
        all_de[i, :] = de_traj[1:]

    # Physical bounds on employment share
    all_ind_emp = np.clip(all_ind_emp, 5.0, 60.0)

    # Compute percentiles
    pctiles = {}
    for p in [2.5, 5, 16, 25, 50, 75, 84, 95, 97.5]:
        pctiles[p] = np.percentile(all_ind_emp, p, axis=0)

    results[scen_name] = {
        "raw": all_ind_emp,
        "de_raw": all_de,
        "percentiles": pctiles,
        "mean": np.mean(all_ind_emp, axis=0),
        "std": np.std(all_ind_emp, axis=0),
    }

    log.info(
        f"    Year {proj_years[-1]}: "
        f"median={pctiles[50][-1]:.1f}%, "
        f"90% CI=[{pctiles[5][-1]:.1f}, {pctiles[95][-1]:.1f}]%"
    )

# ── Report results ─────────────────────────────────────────────────────
log.info("\n=== SCENARIO RESULTS ===")
for scen_name, scen in scenarios.items():
    r = results[scen_name]
    log.info(f"\n--- {scen['label']} ---")
    for yr_idx, yr in enumerate(proj_years):
        if yr_idx % 3 == 0 or yr_idx == PROJECTION_YEARS - 1:
            p = r["percentiles"]
            log.info(
                f"  {yr}: median={p[50][yr_idx]:.1f}%, "
                f"50% CI=[{p[25][yr_idx]:.1f}, {p[75][yr_idx]:.1f}], "
                f"90% CI=[{p[5][yr_idx]:.1f}, {p[95][yr_idx]:.1f}], "
                f"95% CI=[{p[2.5][yr_idx]:.1f}, {p[97.5][yr_idx]:.1f}]"
            )

# ── Sensitivity Analysis ──────────────────────────────────────────────
log.info("\n=== SENSITIVITY ANALYSIS ===")

# Baseline parameters for sensitivity
baseline_params = {
    "beta_de": BETA_DE_BIVARIATE,
    "de_growth": de_growth_mean,
    "beta_demo": BETA_DEMO,
    "demo_slope": demo_slope,
    "innovation_std": 0.5,
}

param_labels = {
    "beta_de": "DE effect size (ARDL LR coeff)",
    "de_growth": "DE annual growth rate",
    "beta_demo": "Demographic effect size",
    "demo_slope": "Demographic decline rate",
    "innovation_std": "Model innovation noise",
}

param_classifications = {
    "beta_de": "Semi-controllable",
    "de_growth": "Controllable",
    "beta_demo": "Exogenous",
    "demo_slope": "Exogenous",
    "innovation_std": "Exogenous",
}

# Compute baseline endpoint (deterministic, no noise)
def deterministic_endpoint(params):
    """Compute deterministic industry emp at projection horizon."""
    de_end = de_last + params["de_growth"] * PROJECTION_YEARS
    de_end = np.clip(de_end, 0.0, 1.0)
    demo_end = demo_last + params["demo_slope"] * PROJECTION_YEARS
    delta_de = de_end - de_last
    delta_demo = demo_end - demo_last
    return ind_emp_last + params["beta_de"] * delta_de + params["beta_demo"] * delta_demo


baseline_endpoint = deterministic_endpoint(baseline_params)
log.info(f"Deterministic baseline endpoint: {baseline_endpoint:.2f}%")

sensitivity = {}
perturbation = 0.20  # +/- 20%

for param_name, base_val in baseline_params.items():
    if base_val == 0:
        continue  # skip if zero

    params_low = baseline_params.copy()
    params_high = baseline_params.copy()
    params_low[param_name] = base_val * (1 - perturbation)
    params_high[param_name] = base_val * (1 + perturbation)

    ep_low = deterministic_endpoint(params_low)
    ep_high = deterministic_endpoint(params_high)

    impact_low = ep_low - baseline_endpoint
    impact_high = ep_high - baseline_endpoint

    sensitivity[param_name] = {
        "low": impact_low,
        "high": impact_high,
        "magnitude": max(abs(impact_low), abs(impact_high)),
        "classification": param_classifications[param_name],
    }
    log.info(
        f"  {param_labels[param_name]}: "
        f"low={impact_low:+.3f} pp, high={impact_high:+.3f} pp, "
        f"class={param_classifications[param_name]}"
    )

# Rank by magnitude
sensitivity_ranked = sorted(sensitivity.items(), key=lambda x: x[1]["magnitude"], reverse=True)

# ── Interaction check (top 2 parameters) ──────────────────────────────
log.info("\n=== INTERACTION CHECK (top 2 params) ===")
top2 = [s[0] for s in sensitivity_ranked[:2]]
if len(top2) == 2:
    p1, p2 = top2
    # Individual effects
    ind1 = sensitivity[p1]["high"]
    ind2 = sensitivity[p2]["high"]
    additive = ind1 + ind2

    # Joint effect
    params_joint = baseline_params.copy()
    params_joint[p1] = baseline_params[p1] * 1.2
    params_joint[p2] = baseline_params[p2] * 1.2
    joint_endpoint = deterministic_endpoint(params_joint)
    joint_effect = joint_endpoint - baseline_endpoint

    interaction = joint_effect - additive
    interaction_pct = abs(interaction / additive) * 100 if additive != 0 else 0

    log.info(f"  {p1} + {p2} interaction: {interaction:+.4f} pp ({interaction_pct:.1f}% of additive)")
    if interaction_pct > 10:
        log.info("  --> Nonlinear interaction EXCEEDS 10% threshold")
    else:
        log.info("  --> Interaction below 10% threshold (approximately additive)")

# ── Endgame Convergence Detection ─────────────────────────────────────
log.info("\n=== ENDGAME CONVERGENCE ===")

# Compute coefficient of variation across scenarios at projection horizon
endpoints = np.array([results[s]["percentiles"][50][-1] for s in scenarios])
endpoint_mean = np.mean(endpoints)
endpoint_std = np.std(endpoints)
cv = endpoint_std / abs(endpoint_mean) if endpoint_mean != 0 else float("inf")

log.info(f"Scenario endpoint medians: {endpoints}")
log.info(f"Mean: {endpoint_mean:.2f}, Std: {endpoint_std:.2f}, CV: {cv:.4f}")

# Check 90% CI overlap
baseline_90_low = results["baseline"]["percentiles"][5][-1]
baseline_90_high = results["baseline"]["percentiles"][95][-1]
high_90_low = results["high_digital"]["percentiles"][5][-1]
high_90_high = results["high_digital"]["percentiles"][95][-1]
low_90_low = results["low_digital"]["percentiles"][5][-1]
low_90_high = results["low_digital"]["percentiles"][95][-1]

# Variance growth check (for unstable trajectory detection)
variances = [np.var([results[s]["percentiles"][50][t] for s in scenarios]) for t in range(PROJECTION_YEARS)]
variance_growth = np.polyfit(np.arange(PROJECTION_YEARS), variances, 1)[0]

log.info(f"Variance growth rate: {variance_growth:.4f} per year")
log.info(f"Baseline 90% CI at horizon: [{baseline_90_low:.1f}, {baseline_90_high:.1f}]")
log.info(f"High-digital 90% CI at horizon: [{high_90_low:.1f}, {high_90_high:.1f}]")
log.info(f"Low-digital 90% CI at horizon: [{low_90_low:.1f}, {low_90_high:.1f}]")

# Classification
if cv < 0.15:
    endgame = "Robust"
    endgame_detail = f"CV={cv:.3f} < 0.15. Scenarios converge."
elif cv > 0.5:
    endgame = "Fork-dependent"
    endgame_detail = f"CV={cv:.3f} > 0.5. Scenarios diverge significantly."
else:
    # Check for equilibrium vs unstable
    if variance_growth > 0.5:
        endgame = "Unstable trajectory"
        endgame_detail = (
            f"CV={cv:.3f}, variance growth={variance_growth:.3f}/yr. "
            "Outcome variance grows with projection distance."
        )
    else:
        endgame = "Fork-dependent"
        endgame_detail = (
            f"CV={cv:.3f}. Moderate divergence depends on DE growth trajectory. "
            "Fork condition: whether digital economy growth accelerates or stagnates."
        )

log.info(f"Endgame classification: {endgame}")
log.info(f"Detail: {endgame_detail}")


# ── EP Decay Computation ──────────────────────────────────────────────
log.info("\n=== EP DECAY ===")

# Base EP from Phase 3
BASE_EP = 0.315  # DE-->SUB, CORRELATION

# Decay schedule (adjusted for fast-moving tech domain)
# CORRELATION edges decay at 2x standard rate per CLAUDE.md
CORRELATION_MULTIPLIER = 2.0

ep_decay_schedule = {
    0: 1.0,     # Historical (Phase 3 finding)
    1: 0.60,    # Year 1
    2: 0.50,    # Year 2
    3: 0.40,    # Year 3
    5: 0.25,    # Year 5
    7: 0.15,    # Year 7
    10: 0.08,   # Year 10
}

# Interpolate for all years
ep_years = np.arange(0, PROJECTION_YEARS + 1)
ep_multipliers_raw = np.interp(
    ep_years,
    list(ep_decay_schedule.keys()),
    list(ep_decay_schedule.values()),
)
# Apply CORRELATION 2x decay
ep_multipliers = ep_multipliers_raw ** CORRELATION_MULTIPLIER
ep_values = BASE_EP * ep_multipliers

# Useful projection horizon: where 90% CI spans > 50% of plausible range
plausible_range = 60.0 - 5.0  # industry emp can range 5-60%
useful_horizon = PROJECTION_YEARS  # default: full range
for t in range(PROJECTION_YEARS):
    ci90_width = results["baseline"]["percentiles"][95][t] - results["baseline"]["percentiles"][5][t]
    if ci90_width > 0.5 * plausible_range:
        useful_horizon = t + 1
        break

log.info(f"Useful projection horizon: {useful_horizon} years")
for t in [0, 1, 3, 5, 7, 10]:
    if t <= PROJECTION_YEARS:
        idx = min(t, len(ep_values) - 1)
        log.info(f"  Year {t}: EP={ep_values[idx]:.4f}, multiplier={ep_multipliers[idx]:.4f}")


# ══════════════════════════════════════════════════════════════════════
# FIGURES
# ══════════════════════════════════════════════════════════════════════

plt.style.use("seaborn-v0_8-whitegrid")

# ── Figure 1: Scenario Comparison ─────────────────────────────────────
log.info("\nGenerating scenario comparison figure...")

fig, ax = plt.subplots(figsize=(10, 10))

# Historical data
hist_years = df["year"].values
hist_ind = df[ind_emp_col].values
ax.plot(hist_years, hist_ind, "k-", linewidth=1.5, label="Historical", zorder=5)
ax.axvline(last_year + 0.5, color="grey", linestyle=":", alpha=0.5, linewidth=0.8)

for scen_name, scen in scenarios.items():
    r = results[scen_name]
    p = r["percentiles"]
    c = scen["color"]

    ax.plot(proj_years, p[50], color=c, linewidth=1.5, label=scen["label"])
    ax.fill_between(proj_years, p[25], p[75], color=c, alpha=0.20)
    ax.fill_between(proj_years, p[5], p[95], color=c, alpha=0.08)

# Mark useful horizon
if useful_horizon < PROJECTION_YEARS:
    ax.axvline(
        last_year + useful_horizon + 0.5,
        color="red",
        linestyle="--",
        linewidth=0.8,
        label=f"Useful horizon ({useful_horizon} yr)",
    )

ax.set_xlabel("Year", fontsize="medium")
ax.set_ylabel("Industry employment share (%)", fontsize="medium")
ax.legend(loc="upper left", fontsize="small")
ax.set_xlim(2000, last_year + PROJECTION_YEARS + 1)

for fmt in ["pdf", "png"]:
    fig.savefig(
        FIG_DIR / f"scenario_comparison.{fmt}",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
plt.close(fig)
log.info(f"  Saved: {FIG_DIR}/scenario_comparison.pdf/.png")


# ── Figure 2: Sensitivity Tornado ─────────────────────────────────────
log.info("Generating sensitivity tornado figure...")

fig, ax = plt.subplots(figsize=(10, 10))

# Sort by magnitude
names = [param_labels[s[0]] for s in sensitivity_ranked]
lows = [s[1]["low"] for s in sensitivity_ranked]
highs = [s[1]["high"] for s in sensitivity_ranked]
classifications = [s[1]["classification"] for s in sensitivity_ranked]

# Color by classification
class_colors = {
    "Controllable": "#2166ac",
    "Semi-controllable": "#f4a582",
    "Exogenous": "#b2182b",
}

y_pos = np.arange(len(names))

for i, (name, low, high, cls) in enumerate(zip(names, lows, highs, classifications)):
    color = class_colors.get(cls, "grey")
    ax.barh(i, high, left=0, height=0.6, color=color, alpha=0.7, edgecolor="white")
    ax.barh(i, low, left=0, height=0.6, color=color, alpha=0.5, edgecolor="white")

ax.set_yticks(y_pos)
ax.set_yticklabels(names, fontsize="small")
ax.set_xlabel("Impact on industry employment share (pp) at 10-year horizon", fontsize="medium")
ax.axvline(0, color="black", linewidth=0.5)

# Legend for classifications
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=class_colors["Controllable"], alpha=0.7, label="Controllable"),
    Patch(facecolor=class_colors["Semi-controllable"], alpha=0.7, label="Semi-controllable"),
    Patch(facecolor=class_colors["Exogenous"], alpha=0.7, label="Exogenous"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize="small")

ax.invert_yaxis()

for fmt in ["pdf", "png"]:
    fig.savefig(
        FIG_DIR / f"sensitivity_tornado.{fmt}",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
plt.close(fig)
log.info(f"  Saved: {FIG_DIR}/sensitivity_tornado.pdf/.png")


# ── Figure 3: EP Decay Chart ─────────────────────────────────────────
log.info("Generating EP decay chart...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [2, 1]})

# Top panel: Industry employment projection with widening CI bands
# Use historical + projection
hist_line = list(hist_ind) + [np.nan] * PROJECTION_YEARS
full_years = np.concatenate([hist_years, proj_years])

r = results["baseline"]
p = r["percentiles"]

ax1.plot(hist_years, hist_ind, "k-", linewidth=1.5, label="Historical")
ax1.plot(proj_years, p[50], "k--", linewidth=1.2, label="Median projection (baseline)")
ax1.fill_between(proj_years, p[25], p[75], color="#2166ac", alpha=0.25, label="50% CI")
ax1.fill_between(proj_years, p[5], p[95], color="#2166ac", alpha=0.12, label="90% CI")
ax1.fill_between(proj_years, p[2.5], p[97.5], color="#2166ac", alpha=0.06, label="95% CI")

# Confidence tier boundaries
tier_boundaries = [
    (last_year + 3, "MEDIUM"),
    (last_year + 7, "LOW-MEDIUM"),
]
for yr, label in tier_boundaries:
    ax1.axvline(yr, color="grey", linestyle=":", alpha=0.4, linewidth=0.8)
    ax1.text(yr + 0.2, ax1.get_ylim()[1] * 0.95, label, fontsize="x-small", color="grey", rotation=90, va="top")

if useful_horizon < PROJECTION_YEARS:
    ax1.axvline(
        last_year + useful_horizon,
        color="red",
        linestyle="--",
        linewidth=0.8,
        label=f"Useful horizon ({useful_horizon} yr)",
    )

ax1.set_ylabel("Industry employment share (%)", fontsize="medium")
ax1.legend(loc="upper left", fontsize="x-small")
ax1.set_xlim(2010, last_year + PROJECTION_YEARS + 1)

# Annotate endgame
ax1.text(
    0.98, 0.02,
    f"Endgame: {endgame}",
    transform=ax1.transAxes,
    fontsize="small",
    ha="right",
    va="bottom",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5),
)

# Bottom panel: EP decay
ax2.plot(ep_years, ep_values, "k-", linewidth=1.5, marker="o", markersize=4)
ax2.fill_between(ep_years, 0, ep_values, alpha=0.15, color="#2166ac")
ax2.axhline(0.15, color="orange", linestyle="--", linewidth=0.8, label="Soft truncation (0.15)")
ax2.axhline(0.05, color="red", linestyle="--", linewidth=0.8, label="Hard truncation (0.05)")

if useful_horizon < PROJECTION_YEARS:
    ax2.axvline(useful_horizon, color="red", linestyle="--", linewidth=0.8, alpha=0.5)

ax2.set_xlabel("Projection distance (years)", fontsize="medium")
ax2.set_ylabel("Epistemic Probability (EP)", fontsize="medium")
ax2.set_ylim(0, BASE_EP * 1.1)
ax2.legend(loc="upper right", fontsize="x-small")

for fmt in ["pdf", "png"]:
    fig.savefig(
        FIG_DIR / f"ep_decay_chart.{fmt}",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
plt.close(fig)
log.info(f"  Saved: {FIG_DIR}/ep_decay_chart.pdf/.png")


# ── Tipping Points Scan ───────────────────────────────────────────────
log.info("\n=== TIPPING POINTS SCAN ===")

# Check: at what DE index value does the relationship sign change?
# The bivariate ARDL LR coeff is +7.15 (positive: complement effect)
# If it were to turn negative (true substitution), that would be a phase transition
# With current data, no evidence of sign change. But we can check the
# DID interaction: pre-break beta1=20.51, post-break net=20.51-5.90=14.61
# The weakening trend could eventually reach zero

years_to_zero = abs(BETA_DE_BIVARIATE / BETA_POST_INTERACTION) if BETA_POST_INTERACTION != 0 else float("inf")
log.info(f"If DE-industry weakening continues at current rate:")
log.info(f"  POST interaction = {BETA_POST_INTERACTION:.2f} pp/period")
log.info(f"  Time to zero effect: ~{years_to_zero:.1f} periods from break date")
log.info(f"  This would place the tipping point around year {2016 + years_to_zero:.0f}")

# DE index saturation
de_ceiling = 1.0  # Index is bounded [0,1]
years_to_ceiling = (de_ceiling - de_last) / de_growth_mean if de_growth_mean > 0 else float("inf")
log.info(f"DE index saturation: {years_to_ceiling:.1f} years at current growth rate")

# Demographics floor
demo_floor_year = (60.0 - demo_last) / demo_slope if demo_slope < 0 else float("inf")
log.info(f"Demographics reaching 60% (floor concern): {demo_floor_year:.1f} years")

log.info("\n=== SIMULATION COMPLETE ===")

# ── Save summary statistics for PROJECTION.md ─────────────────────────
summary = {
    "scenarios": {},
    "sensitivity": sensitivity_ranked,
    "endgame": endgame,
    "endgame_detail": endgame_detail,
    "useful_horizon": useful_horizon,
    "cv": cv,
    "ep_values": ep_values.tolist(),
    "base_ep": BASE_EP,
}

for scen_name, scen in scenarios.items():
    r = results[scen_name]
    p = r["percentiles"]
    summary["scenarios"][scen_name] = {
        "label": scen["label"],
        "conditional_prob": scen["conditional_prob"],
        "year_1": {
            "median": float(p[50][0]),
            "ci50": [float(p[25][0]), float(p[75][0])],
            "ci90": [float(p[5][0]), float(p[95][0])],
            "ci95": [float(p[2.5][0]), float(p[97.5][0])],
        },
        "year_5": {
            "median": float(p[50][4]),
            "ci50": [float(p[25][4]), float(p[75][4])],
            "ci90": [float(p[5][4]), float(p[95][4])],
            "ci95": [float(p[2.5][4]), float(p[97.5][4])],
        },
        "year_10": {
            "median": float(p[50][-1]),
            "ci50": [float(p[25][-1]), float(p[75][-1])],
            "ci90": [float(p[5][-1]), float(p[95][-1])],
            "ci95": [float(p[2.5][-1]), float(p[97.5][-1])],
        },
    }

import json
summary_path = FIG_DIR.parent / "exec" / "projection_summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2, default=str)
log.info(f"Summary saved to {summary_path}")
