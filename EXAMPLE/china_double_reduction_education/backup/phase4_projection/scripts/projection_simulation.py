"""
Phase 4: Forward Projection -- Monte Carlo Scenario Simulation,
Sensitivity Analysis, and EP Decay Visualization.

Produces:
  - figures/scenario_comparison.pdf
  - figures/sensitivity_tornado.pdf
  - figures/ep_decay_chart.pdf
  - data/projection_results.json

Revision history:
  v2 (2026-03-29): Fix review issues A1-A3, B1-B3, B6, C3-C4.
    - A1: Sensitivity baseline underground_disp corrected from 0.30 to 0.20.
    - A2: Policy double-counting removed. OBS_2025 already embeds the policy
      effect; net_policy now models only *marginal deviation* from the
      embedded state (persistence=1 => no change from 2025, <1 => partial
      reversal, >1 => deepening).
    - A3: Underground displacement now uses Uniform(0, 0.6) as documented,
      not a clipped Normal.
    - B1: Removed unjustified 2%/yr policy deepening term. Policy shift is
      now constant (standard ITS assumption).
    - B2: Removed unjustified 30% demographic dampening. Full pass-through
      applied (factor=1.0).
    - B3: Switched policy_persistence to Beta distribution to avoid
      clipping artifacts. Underground displacement already uses Uniform.
    - B6: Added correlated systematic uncertainty drawn once per MC
      iteration from N(0, SYST_UNC=254), added to all years.
    - C3: Vectorized inner loop over years (numpy broadcasting).
    - C4: Added MC convergence diagnostic (running-mean stability check).
"""
import logging
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats as sp_stats

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# Paths
BASE = Path("phase4_projection")
FIG_DIR = BASE / "figures"
DATA_DIR = BASE / "data"
FIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
SEED = 42
np.random.seed(SEED)
N_ITER = 10_000

# ============================================================
# 1. Load Phase 3 parameters
# ============================================================
with open("phase3_analysis/data/its_results.json") as f:
    its = json.load(f)
with open("phase3_analysis/data/step7_uncertainty_results.json") as f:
    unc = json.load(f)

df = pd.read_parquet("phase3_analysis/data/analysis_dataset.parquet")

# Key empirical parameters (national series -- primary)
LEVEL_SHIFT = its["national"]["primary"]["level_shift"]          # -483 yuan
LEVEL_SHIFT_SE = its["national"]["primary"]["level_shift_se"]    # 159 yuan
PRE_TREND = its["national"]["primary"]["trend"]                  # +183 yuan/yr
PRE_POLICY_MEAN = its["national"]["pre_policy_mean"]             # 2038 yuan
STAT_UNC = unc["final_results"]["national"]["stat_unc"]          # 127
SYST_UNC = unc["final_results"]["national"]["syst_unc"]          # 254
TOTAL_UNC = unc["final_results"]["national"]["total_unc"]        # 284

# Observed values
OBS_2025 = df.loc[df["year"] == 2025, "real_national"].values[0]  # ~2986

# Demographic: births declining ~8%/year from 2020
births = df[["year", "births_millions"]].dropna()
log.info("Births data:\n%s", births.to_string())

# Pre-policy spending per birth was rising -- use last observed
SPB_2024 = df.loc[df["year"] == 2024, "spending_per_birth"].values[0]  # ~288

# ============================================================
# 2. Projection Model  (v2 -- see revision notes)
# ============================================================
# We project real per capita education/culture/recreation spending.
# Base year: 2025 (last observed). Projection horizon: 2026-2035 (10 years).
#
# Model (corrected v2):
#   Y(t) = Y_base * income_factor(t) * demo_factor(t)
#          + Y_base * culture_recovery * t
#          + policy_deviation(t)
#          + systematic_bias
#          + noise(t)
#
# Where:
#   Y_base         = OBS_2025 (already contains the current policy effect)
#   income_factor  = (1 + g * eta)^t   (compound income-driven growth)
#   demo_factor    = (1 + delta)^t      (full pass-through, no dampening)
#   culture_recovery = proxy confound addition per year
#   policy_deviation = LEVEL_SHIFT * (pol_p - 1.0) * (1 - ug_d)
#       pol_p = 1.0 means the current embedded effect persists unchanged
#       pol_p < 1.0 means partial reversal (spending rebounds)
#       pol_p > 1.0 means policy deepens beyond current state
#       ug_d  = underground displacement fraction (offsets policy savings)
#   systematic_bias ~ N(0, SYST_UNC) drawn once per MC iteration
#       (correlated across all years -- represents persistent measurement bias)
#   noise(t) ~ N(0, STAT_UNC * sqrt(t))  (independent statistical noise)
#
# NOTE on policy double-counting (A2 fix):
#   OBS_2025 = 2,986 yuan already reflects whatever policy effect existed
#   by 2025.  The original model added the full LEVEL_SHIFT again, double-
#   counting.  In v2, pol_p is re-parameterized:
#     - Scenario A (pol_p ~ Beta centered ~0.8): the policy effect persists
#       at 80% of what's currently embedded => 20% reversal => spending
#       *rises* slightly from 2025 baseline due to partial relaxation.
#       Wait -- this needs careful thought.  If pol_p=0.8 means 80% of the
#       original LEVEL_SHIFT persists, then the *deviation* from the current
#       baseline is LEVEL_SHIFT * (0.8 - 1.0) = -483 * (-0.2) = +97 yuan.
#       That is, partial reversal adds back ~97 yuan.
#     - Scenario B (pol_p ~ Beta centered ~0.3): large reversal;
#       deviation = -483 * (0.3 - 1.0) = +338 yuan rebound.
#     - Scenario C (pol_p ~ Beta centered ~0.0): near-full reversal;
#       deviation = -483 * (0.0 - 1.0) = +483 yuan full rebound.
#   This correctly models the marginal change from the 2025 observed state.

PROJECTION_YEARS = np.arange(2026, 2036)
N_PROJ = len(PROJECTION_YEARS)
T_VEC = np.arange(1, N_PROJ + 1)  # [1, 2, ..., 10] years from 2025

# ============================================================
# Helper: Beta distribution from (mean, std) on [lo, hi]
# ============================================================
def beta_params_from_mean_std(mean, std, lo=0.0, hi=1.0):
    """Compute scipy Beta(a, b, loc, scale) parameters for a desired mean/std
    on the interval [lo, hi].  Falls back to uniform if std is too large."""
    rng = hi - lo
    mu_01 = (mean - lo) / rng            # mean mapped to [0,1]
    sig_01 = std / rng                    # std mapped to [0,1]
    mu_01 = np.clip(mu_01, 0.01, 0.99)   # keep away from boundaries
    # Beta variance = mu(1-mu)/(a+b+1); solve for concentration
    var_01 = sig_01 ** 2
    max_var = mu_01 * (1 - mu_01)
    if var_01 >= max_var:
        # Requested spread exceeds Beta's maximum -> use uniform
        return 1.0, 1.0, lo, rng
    concentration = mu_01 * (1 - mu_01) / var_01 - 1
    a = mu_01 * concentration
    b = (1 - mu_01) * concentration
    return max(a, 0.01), max(b, 0.01), lo, rng


# ============================================================
# 3. Scenario Definitions  (v2 -- re-parameterized)
# ============================================================
# policy_persistence is now a Beta distribution on [0, 1.5].
# underground_disp is Uniform(lo, hi) -- A3 fix.
SCENARIOS = {
    "A: Policy Succeeds": {
        "description": (
            "Double Reduction policy effect is real and persists near current "
            "levels. Formal tutoring remains suppressed, underground market is "
            "contained. Spending grows slowly from the 2025 base."
        ),
        "conditional_probability": "Unlikely (15-25%)",
        "income_growth": (0.035, 0.01),
        "income_elasticity": (0.9, 0.10),
        "policy_persistence_beta": (0.8, 0.15, 0.0, 1.5),   # (mean, std, lo, hi)
        "demo_decline": (-0.07, 0.02),
        "underground_disp_uniform": (0.0, 0.15),             # Uniform(lo, hi)
        "culture_recovery": (0.01, 0.005),
    },
    "B: Status Quo (Displacement)": {
        "description": (
            "Policy reduced formal tutoring but spending displaced to underground "
            "channels, non-academic enrichment, and in-school costs. Net household "
            "education burden unchanged or slightly lower. Demographic decline is "
            "the dominant trend driver."
        ),
        "conditional_probability": "Likely (45-55%)",
        "income_growth": (0.04, 0.015),
        "income_elasticity": (1.0, 0.15),
        "policy_persistence_beta": (0.3, 0.25, 0.0, 1.5),
        "demo_decline": (-0.06, 0.03),
        "underground_disp_uniform": (0.0, 0.60),             # wide uniform prior
        "culture_recovery": (0.015, 0.01),
    },
    "C: Rebound": {
        "description": (
            "Spending returns to or exceeds pre-policy trajectory. "
            "Underground tutoring expands, enforcement weakens, new enrichment "
            "channels emerge. Competitive pressure reasserts."
        ),
        "conditional_probability": "Plausible (25-35%)",
        "income_growth": (0.045, 0.015),
        "income_elasticity": (1.1, 0.12),
        "policy_persistence_beta": (0.0, 0.15, 0.0, 1.5),
        "demo_decline": (-0.05, 0.02),
        "underground_disp_uniform": (0.0, 0.60),             # wide uniform prior
        "culture_recovery": (0.02, 0.01),
    },
}


def run_scenario(params, n_iter=N_ITER):
    """Run vectorized Monte Carlo for one scenario.
    Returns array (n_iter, n_proj_years)."""

    # --- Sample all parameters at once (vectorized) ---
    inc_g = np.random.normal(*params["income_growth"], size=n_iter)
    inc_e = np.random.normal(*params["income_elasticity"], size=n_iter)

    # Policy persistence: Beta distribution on [lo, hi] (B3 fix)
    pp_mean, pp_std, pp_lo, pp_hi = params["policy_persistence_beta"]
    a, b, loc, scale = beta_params_from_mean_std(pp_mean, pp_std, pp_lo, pp_hi)
    pol_p = sp_stats.beta.rvs(a, b, loc=loc, scale=scale, size=n_iter)

    demo_d = np.random.normal(*params["demo_decline"], size=n_iter)

    # Underground displacement: Uniform (A3 fix)
    ug_lo, ug_hi = params["underground_disp_uniform"]
    ug_d = np.random.uniform(ug_lo, ug_hi, size=n_iter)

    cult_r = np.random.normal(*params["culture_recovery"], size=n_iter)

    # Systematic bias: one draw per iteration, persists across all years (B6)
    syst_bias = np.random.normal(0, SYST_UNC, size=n_iter)

    # --- Policy deviation from 2025 baseline (A2 fix) ---
    # pol_p = fraction of original LEVEL_SHIFT that persists
    # Deviation from embedded state = LEVEL_SHIFT * (pol_p - 1.0) * (1 - ug_d)
    # Note: LEVEL_SHIFT is negative (-483). If pol_p < 1, deviation is positive
    # (spending rebounds). If pol_p > 1, deviation is negative (deepening).
    policy_dev = LEVEL_SHIFT * (pol_p - 1.0) * (1 - ug_d)  # shape (n_iter,)

    # --- Vectorized projection over years (C3 fix) ---
    # T_VEC has shape (N_PROJ,); parameter arrays have shape (n_iter,)
    # Use broadcasting: (n_iter, 1) op (1, N_PROJ) -> (n_iter, N_PROJ)

    inc_g_e = (inc_g * inc_e)[:, None]             # (n_iter, 1)
    income_factor = (1.0 + inc_g_e) ** T_VEC[None, :]   # (n_iter, N_PROJ)

    demo_d_col = demo_d[:, None]                   # (n_iter, 1)
    demo_factor = (1.0 + demo_d_col) ** T_VEC[None, :]  # full pass-through (B2)

    culture_add = OBS_2025 * cult_r[:, None] * T_VEC[None, :]

    # Counterfactual from 2025 base (no policy deviation yet)
    counterfactual = OBS_2025 * income_factor * demo_factor + culture_add

    # Policy deviation is constant across years (B1: no deepening term)
    policy_term = policy_dev[:, None] * np.ones((1, N_PROJ))

    # Noise: stat noise scales with sqrt(t), systematic is constant (B6)
    stat_noise = np.random.normal(
        0, 1, size=(n_iter, N_PROJ)
    ) * (STAT_UNC * np.sqrt(T_VEC[None, :]))
    syst_term = syst_bias[:, None] * np.ones((1, N_PROJ))

    results = counterfactual + policy_term + stat_noise + syst_term
    return results


def compute_percentiles(results):
    """Compute summary statistics from MC results."""
    return {
        "median": np.median(results, axis=0).tolist(),
        "mean": np.mean(results, axis=0).tolist(),
        "ci_50_low": np.percentile(results, 25, axis=0).tolist(),
        "ci_50_high": np.percentile(results, 75, axis=0).tolist(),
        "ci_90_low": np.percentile(results, 5, axis=0).tolist(),
        "ci_90_high": np.percentile(results, 95, axis=0).tolist(),
        "ci_95_low": np.percentile(results, 2.5, axis=0).tolist(),
        "ci_95_high": np.percentile(results, 97.5, axis=0).tolist(),
    }


# ============================================================
# 4. Run Monte Carlo Simulations
# ============================================================
log.info("Running Monte Carlo simulations (%d iterations per scenario)...", N_ITER)

scenario_results = {}
for name, params in SCENARIOS.items():
    log.info("  Scenario: %s", name)
    raw = run_scenario(params)
    scenario_results[name] = {
        "raw": raw,
        "stats": compute_percentiles(raw),
    }
    med = scenario_results[name]["stats"]["median"]
    ci90_lo = scenario_results[name]["stats"]["ci_90_low"]
    ci90_hi = scenario_results[name]["stats"]["ci_90_high"]
    log.info("    2030 median: %.0f [90%% CI: %.0f, %.0f]", med[4], ci90_lo[4], ci90_hi[4])
    log.info("    2035 median: %.0f [90%% CI: %.0f, %.0f]", med[9], ci90_lo[9], ci90_hi[9])


# ============================================================
# 4b. MC Convergence Diagnostic (C4 fix)
# ============================================================
log.info("Running MC convergence diagnostic...")
convergence_info = {}
for name, sdata in scenario_results.items():
    raw = sdata["raw"]
    # Check running mean stability at 2030 (index 4) and 2035 (index 9)
    for yr_idx, yr_label in [(4, "2030"), (9, "2035")]:
        col = raw[:, yr_idx]
        # Running mean over cumulative samples
        cumsum = np.cumsum(col)
        running_mean = cumsum / np.arange(1, len(col) + 1)
        # Stability: max deviation of running mean in last 20% of samples
        # relative to the final mean
        final_mean = running_mean[-1]
        tail_start = int(0.8 * len(running_mean))
        tail_means = running_mean[tail_start:]
        max_dev = np.max(np.abs(tail_means - final_mean))
        rel_dev = max_dev / abs(final_mean) * 100
        converged = rel_dev < 0.5  # < 0.5% deviation in tail = converged
        convergence_info[f"{name}_{yr_label}"] = {
            "final_mean": float(final_mean),
            "max_tail_deviation": float(max_dev),
            "relative_deviation_pct": float(rel_dev),
            "converged": bool(converged),
        }
        status = "CONVERGED" if converged else "NOT CONVERGED"
        log.info("  %s @ %s: mean=%.0f, tail dev=%.1f yuan (%.3f%%) [%s]",
                 name, yr_label, final_mean, max_dev, rel_dev, status)


# ============================================================
# 5. Scenario Comparison Figure
# ============================================================
log.info("Generating scenario comparison figure...")

colors = {"A: Policy Succeeds": "#2166ac", "B: Status Quo (Displacement)": "#4daf4a",
          "C: Rebound": "#d62728"}

fig, ax = plt.subplots(figsize=(10, 10))

# Plot historical data
hist_years = df["year"].values
hist_vals = df["real_national"].values
ax.plot(hist_years, hist_vals, "ko-", markersize=5, label="Observed (CPI-deflated)", zorder=5)

# Policy line
ax.axvline(2021, color="grey", linestyle="--", alpha=0.5, linewidth=1)
ax.text(2021.1, max(hist_vals) * 1.05, "Policy\n(Jul 2021)", fontsize="x-small",
        color="grey", va="bottom")

# ITS counterfactual
its_cf = PRE_POLICY_MEAN + PRE_TREND * (np.arange(2016, 2036) - 2016)
ax.plot(np.arange(2016, 2036), its_cf, "k:", alpha=0.3, linewidth=1, label="ITS counterfactual")

for name, sdata in scenario_results.items():
    stats = sdata["stats"]
    c = colors[name]
    ax.plot(PROJECTION_YEARS, stats["median"], color=c, linewidth=2, label=name)
    ax.fill_between(PROJECTION_YEARS, stats["ci_50_low"], stats["ci_50_high"],
                    color=c, alpha=0.25)
    ax.fill_between(PROJECTION_YEARS, stats["ci_90_low"], stats["ci_90_high"],
                    color=c, alpha=0.10)

ax.set_xlabel("Year", fontsize="medium")
ax.set_ylabel("Real per capita education/culture/rec spending (2015 yuan)", fontsize="medium")
ax.legend(loc="upper left", fontsize="x-small", framealpha=0.9)
ax.set_xlim(2016, 2035)
ax.tick_params(labelsize="small")

for fmt in ["pdf", "png"]:
    fig.savefig(FIG_DIR / f"scenario_comparison.{fmt}", dpi=200,
                bbox_inches="tight", transparent=True)
plt.close(fig)
log.info("  Saved scenario_comparison.pdf/png")


# ============================================================
# 6. Sensitivity Analysis (Tornado Chart)
# ============================================================
log.info("Running sensitivity analysis...")

# Baseline parameters (scenario B central values)
baseline_params = {
    "income_growth": 0.04,
    "income_elasticity": 1.0,
    "policy_persistence": 0.3,
    "demo_decline": -0.06,
    "underground_disp": 0.20,
    "culture_recovery": 0.015,
}

# Perturbation: +/- 1 sigma or +/- 20% for assumed parameters
perturbations = {
    "Income growth rate": ("income_growth", 0.015),
    "Income elasticity": ("income_elasticity", 0.15),
    "Policy persistence": ("policy_persistence", 0.25),
    "Demographic decline rate": ("demo_decline", 0.03),
    "Underground displacement": ("underground_disp", 0.20),
    "Culture/rec recovery": ("culture_recovery", 0.01),
}

# Classification
var_class = {
    "Income growth rate": "Exogenous",
    "Income elasticity": "Exogenous",
    "Policy persistence": "Controllable",
    "Demographic decline rate": "Exogenous",
    "Underground displacement": "Semi-controllable",
    "Culture/rec recovery": "Exogenous",
}


def run_single_projection(params_dict, n_years=10):
    """Deterministic single-run projection for sensitivity (v2).
    Matches the corrected MC model: no double-counting, no dampening,
    no deepening, full pass-through demographics."""
    base = OBS_2025
    # Policy deviation from embedded 2025 state (A2 fix)
    policy_dev = LEVEL_SHIFT * (params_dict["policy_persistence"] - 1.0) * (
        1 - params_dict["underground_disp"]
    )
    vals = []
    for t in range(1, n_years + 1):
        inc_f = (1 + params_dict["income_growth"] * params_dict["income_elasticity"]) ** t
        demo_f = (1 + params_dict["demo_decline"]) ** t   # full pass-through (B2)
        cult = base * params_dict["culture_recovery"] * t
        proj = base * inc_f * demo_f + cult + policy_dev   # constant shift (B1)
        vals.append(proj)
    return vals


# Baseline projection (at 2030 = index 4)
baseline_proj = run_single_projection(baseline_params)
baseline_2030 = baseline_proj[4]
log.info("  Baseline 2030 projection: %.0f yuan", baseline_2030)

sensitivity = {}
for label, (key, delta) in perturbations.items():
    # Low
    p_low = baseline_params.copy()
    p_low[key] = baseline_params[key] - delta
    val_low = run_single_projection(p_low)[4]

    # High
    p_high = baseline_params.copy()
    p_high[key] = baseline_params[key] + delta
    val_high = run_single_projection(p_high)[4]

    sensitivity[label] = {
        "low_impact": val_low - baseline_2030,
        "high_impact": val_high - baseline_2030,
        "abs_range": abs(val_high - val_low),
        "classification": var_class[label],
    }
    log.info("  %s: low=%.0f, high=%.0f, range=%.0f",
             label, val_low - baseline_2030, val_high - baseline_2030, abs(val_high - val_low))

# Sort by absolute range
sorted_sens = sorted(sensitivity.items(), key=lambda x: x[1]["abs_range"], reverse=True)

# Tornado chart
fig, ax = plt.subplots(figsize=(10, 10))

y_pos = np.arange(len(sorted_sens))
class_colors = {"Controllable": "#d62728", "Semi-controllable": "#ff7f0e", "Exogenous": "#1f77b4"}

for i, (label, vals) in enumerate(sorted_sens):
    color = class_colors[vals["classification"]]
    ax.barh(i, vals["high_impact"], height=0.4, color=color, alpha=0.7,
            label=vals["classification"] if i == 0 or vals["classification"] not in
            [sorted_sens[j][1]["classification"] for j in range(i)] else "")
    ax.barh(i, vals["low_impact"], height=0.4, color=color, alpha=0.7)

ax.set_yticks(y_pos)
ax.set_yticklabels([s[0] for s in sorted_sens], fontsize="small")
ax.set_xlabel("Impact on 2030 projected spending (yuan)", fontsize="small")
ax.axvline(0, color="black", linewidth=0.8)

# Legend for classifications
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=class_colors[c], alpha=0.7, label=c)
                   for c in ["Controllable", "Semi-controllable", "Exogenous"]]
ax.legend(handles=legend_elements, loc="lower right", fontsize="x-small")

ax.tick_params(labelsize="x-small")
fig.tight_layout()

for fmt in ["pdf", "png"]:
    fig.savefig(FIG_DIR / f"sensitivity_tornado.{fmt}", dpi=200,
                bbox_inches="tight", transparent=True)
plt.close(fig)
log.info("  Saved sensitivity_tornado.pdf/png")


# ============================================================
# 7. Interaction Check (top 3 parameters)
# ============================================================
log.info("Running pairwise interaction checks...")

top3_keys = [sorted_sens[i][0] for i in range(min(3, len(sorted_sens)))]
interactions = {}
for i in range(len(top3_keys)):
    for j in range(i+1, len(top3_keys)):
        k1, k2 = top3_keys[i], top3_keys[j]
        key1, delta1 = perturbations[k1]
        key2, delta2 = perturbations[k2]

        # Individual effects
        p1 = baseline_params.copy()
        p1[key1] = baseline_params[key1] + delta1
        eff1 = run_single_projection(p1)[4] - baseline_2030

        p2 = baseline_params.copy()
        p2[key2] = baseline_params[key2] + delta2
        eff2 = run_single_projection(p2)[4] - baseline_2030

        # Joint effect
        p12 = baseline_params.copy()
        p12[key1] = baseline_params[key1] + delta1
        p12[key2] = baseline_params[key2] + delta2
        eff12 = run_single_projection(p12)[4] - baseline_2030

        additive = eff1 + eff2
        interaction_pct = abs(eff12 - additive) / abs(additive) * 100 if additive != 0 else 0

        interactions[f"{k1} x {k2}"] = {
            "individual_sum": float(additive),
            "joint": float(eff12),
            "interaction_pct": float(interaction_pct),
            "nonlinear": bool(interaction_pct > 10),
        }
        log.info("  %s x %s: additive=%.0f, joint=%.0f, interaction=%.1f%%",
                 k1, k2, additive, eff12, interaction_pct)


# ============================================================
# 8. EP Decay Visualization
# ============================================================
log.info("Generating EP decay chart...")

# EP values from Phase 3
ep_phases = {
    "Phase 0\n(Discovery)": 0.30,
    "Phase 1\n(Strategy)": 0.30,
    "Phase 3\n(Analysis)": 0.20,
}

# EP decay schedule for projection
# CORRELATION edges decay at 2x standard rate
# Standard: 1.0, 0.7, 0.4, 0.2
# For CORRELATION: 1.0, 0.49, 0.16, 0.04
BASE_EP = 0.20  # Phase 3 EP for Policy -> Aggregate Spending

decay_schedule = {
    "Phase 3\n(Empirical)": {"ep_mult": 1.0, "ep": BASE_EP},
    "Near-term\n(1-3 yr)": {"ep_mult": 0.49, "ep": BASE_EP * 0.49},   # 0.7^2 for CORRELATION
    "Mid-term\n(3-7 yr)": {"ep_mult": 0.16, "ep": BASE_EP * 0.16},    # 0.4^2
    "Long-term\n(7-10 yr)": {"ep_mult": 0.04, "ep": BASE_EP * 0.04},  # 0.2^2
}

# Detailed projection with EP-weighted CIs
projection_t = np.arange(0, 11)  # 0=2025 (observed), 1=2026, ..., 10=2035
baseline_stats = scenario_results["B: Status Quo (Displacement)"]["stats"]

# Build median and CI arrays including the observed 2025
all_years = np.concatenate([[2025], PROJECTION_YEARS])
median_line = np.concatenate([[OBS_2025], baseline_stats["median"]])
ci50_lo = np.concatenate([[OBS_2025], baseline_stats["ci_50_low"]])
ci50_hi = np.concatenate([[OBS_2025], baseline_stats["ci_50_high"]])
ci90_lo = np.concatenate([[OBS_2025], baseline_stats["ci_90_low"]])
ci90_hi = np.concatenate([[OBS_2025], baseline_stats["ci_90_high"]])
ci95_lo = np.concatenate([[OBS_2025], baseline_stats["ci_95_low"]])
ci95_hi = np.concatenate([[OBS_2025], baseline_stats["ci_95_high"]])

# Useful projection horizon: where 90% CI spans > 50% of plausible range
# Plausible range: 1500-5000 yuan (based on historical and projected extremes)
PLAUSIBLE_RANGE = 3500
useful_horizon = None
for i, yr in enumerate(all_years):
    span = ci90_hi[i] - ci90_lo[i]
    if span > 0.5 * PLAUSIBLE_RANGE:
        useful_horizon = yr
        break

log.info("  Useful projection horizon: %s", useful_horizon)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10), gridspec_kw={"width_ratios": [3, 2]})

# Left panel: EP-weighted confidence bands
ax1.plot(hist_years, hist_vals, "ko-", markersize=5, label="Observed", zorder=5)
ax1.plot(all_years, median_line, "b-", linewidth=2, label="Baseline median")
ax1.fill_between(all_years, ci50_lo, ci50_hi, color="blue", alpha=0.25, label="50% CI")
ax1.fill_between(all_years, ci90_lo, ci90_hi, color="blue", alpha=0.12, label="90% CI")
ax1.fill_between(all_years, ci95_lo, ci95_hi, color="blue", alpha=0.06, label="95% CI")

# Mark EP decay tiers
tier_bounds = [2025, 2028, 2032, 2035]
tier_labels_short = ["HIGH\n(emp.)", "MED\n(0.49x)", "LOW\n(0.16x)", "V.LOW\n(0.04x)"]
for k, yr in enumerate(tier_bounds[:-1]):
    ax1.axvline(yr, color="red", linestyle=":", alpha=0.4, linewidth=0.8)
    ax1.text(yr + 0.2, ax1.get_ylim()[1] if k > 0 else max(hist_vals) * 1.1,
             tier_labels_short[k], fontsize="xx-small", color="red", va="top")

if useful_horizon:
    ax1.axvline(useful_horizon, color="red", linestyle="--", linewidth=1.5,
                label=f"Useful horizon ({useful_horizon})")

ax1.set_xlabel("Year", fontsize="medium")
ax1.set_ylabel("Real per capita spending (2015 yuan)", fontsize="medium")
ax1.legend(loc="upper left", fontsize="x-small", framealpha=0.9)
ax1.set_xlim(2016, 2035)
ax1.tick_params(labelsize="small")

# Right panel: EP decay curve
ep_x = [0, 1.5, 5, 8.5]  # midpoints of tiers in years from 2025
ep_y = [BASE_EP, BASE_EP * 0.49, BASE_EP * 0.16, BASE_EP * 0.04]

ax2.plot(ep_x, ep_y, "ro-", markersize=8, linewidth=2)
ax2.fill_between(ep_x, 0, ep_y, color="red", alpha=0.15)
ax2.axhline(0.05, color="grey", linestyle="--", linewidth=1, alpha=0.7)
ax2.text(0.5, 0.055, "Hard truncation (0.05)", fontsize="xx-small", color="grey")
ax2.axhline(0.15, color="grey", linestyle=":", linewidth=1, alpha=0.5)
ax2.text(0.5, 0.155, "Soft truncation (0.15)", fontsize="xx-small", color="grey")

ax2.set_xlabel("Projection distance (years from 2025)", fontsize="medium")
ax2.set_ylabel("Epistemic Probability (EP)", fontsize="medium")
ax2.set_ylim(0, 0.25)
ax2.tick_params(labelsize="small")

# Annotate tiers
for k, (x, y) in enumerate(zip(ep_x, ep_y)):
    ax2.annotate(f"EP={y:.3f}", (x, y), textcoords="offset points",
                 xytext=(10, 10), fontsize="xx-small")

fig.tight_layout()
for fmt in ["pdf", "png"]:
    fig.savefig(FIG_DIR / f"ep_decay_chart.{fmt}", dpi=200,
                bbox_inches="tight", transparent=True)
plt.close(fig)
log.info("  Saved ep_decay_chart.pdf/png")


# ============================================================
# 9. Endgame Convergence Detection
# ============================================================
log.info("Computing endgame convergence metrics...")

# Compute CV of scenario endpoints at 2030 and 2035
endpoints_2030 = [scenario_results[s]["stats"]["median"][4] for s in SCENARIOS]
endpoints_2035 = [scenario_results[s]["stats"]["median"][9] for s in SCENARIOS]

cv_2030 = np.std(endpoints_2030) / np.mean(endpoints_2030)
cv_2035 = np.std(endpoints_2035) / np.mean(endpoints_2035)

log.info("  Scenario endpoint medians at 2030: %s", [f"{x:.0f}" for x in endpoints_2030])
log.info("  Scenario endpoint medians at 2035: %s", [f"{x:.0f}" for x in endpoints_2035])
log.info("  CV at 2030: %.3f", cv_2030)
log.info("  CV at 2035: %.3f", cv_2035)

# Check 90% CI overlap between scenarios at 2035
ci90_ranges = {}
for name, sdata in scenario_results.items():
    lo = sdata["stats"]["ci_90_low"][9]
    hi = sdata["stats"]["ci_90_high"][9]
    ci90_ranges[name] = (lo, hi)
    log.info("  %s 2035 90%% CI: [%.0f, %.0f]", name, lo, hi)

# Check overlap between A and C
a_lo, a_hi = ci90_ranges["A: Policy Succeeds"]
c_lo, c_hi = ci90_ranges["C: Rebound"]
overlap = max(0, min(a_hi, c_hi) - max(a_lo, c_lo))
a_span = a_hi - a_lo
c_span = c_hi - c_lo
avg_span = (a_span + c_span) / 2
overlap_pct = overlap / avg_span * 100 if avg_span > 0 else 100
log.info("  A-C overlap at 2035: %.0f yuan (%.1f%% of avg span)", overlap, overlap_pct)


# ============================================================
# 10. Tipping Points Scan
# ============================================================
log.info("Scanning for tipping points...")

# Test: at what policy_persistence does the 2030 projection cross
# above vs below the ITS counterfactual?
counterfactual_2030 = PRE_POLICY_MEAN + PRE_TREND * (2030 - 2016)
log.info("  ITS counterfactual at 2030: %.0f yuan", counterfactual_2030)

pp_range = np.linspace(-0.2, 1.2, 50)
proj_2030_by_pp = []
for pp in pp_range:
    params = baseline_params.copy()
    params["policy_persistence"] = pp
    proj_2030_by_pp.append(run_single_projection(params)[4])

# Find crossing point
proj_arr = np.array(proj_2030_by_pp)
crossing_idx = np.where(np.diff(np.sign(proj_arr - counterfactual_2030)))[0]
if len(crossing_idx) > 0:
    crossing_pp = pp_range[crossing_idx[0]]
    log.info("  Counterfactual crossing at policy_persistence=%.2f", crossing_pp)
else:
    crossing_pp = None
    log.info("  No counterfactual crossing found in range")


# ============================================================
# 11. Save Results
# ============================================================
log.info("Saving results...")

output = {
    "metadata": {
        "n_iterations": N_ITER,
        "seed": SEED,
        "base_year": 2025,
        "base_value": float(OBS_2025),
        "projection_years": PROJECTION_YEARS.tolist(),
    },
    "scenarios": {},
    "sensitivity": {},
    "interactions": interactions,
    "convergence": {
        "cv_2030": float(cv_2030),
        "cv_2035": float(cv_2035),
        "endpoints_2030": {k: float(v) for k, v in zip(SCENARIOS.keys(), endpoints_2030)},
        "endpoints_2035": {k: float(v) for k, v in zip(SCENARIOS.keys(), endpoints_2035)},
        "ci90_ranges_2035": {k: [float(v[0]), float(v[1])] for k, v in ci90_ranges.items()},
        "overlap_pct_A_C": float(overlap_pct),
    },
    "mc_convergence": convergence_info,
    "useful_projection_horizon": int(useful_horizon) if useful_horizon else None,
    "ep_decay": decay_schedule,
    "tipping_points": {
        "counterfactual_2030": float(counterfactual_2030),
        "crossing_policy_persistence": float(crossing_pp) if crossing_pp else None,
    },
}

for name, sdata in scenario_results.items():
    output["scenarios"][name] = sdata["stats"]

for label, vals in sensitivity.items():
    output["sensitivity"][label] = vals

with open(DATA_DIR / "projection_results.json", "w") as f:
    json.dump(output, f, indent=2)

log.info("Done. All outputs saved to %s", BASE)
