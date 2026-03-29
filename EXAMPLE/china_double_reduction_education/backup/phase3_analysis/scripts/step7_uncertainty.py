"""
Step 7: Uncertainty Quantification -- Consolidate all uncertainty sources,
produce tornado chart and final results table.

Produces:
  - phase3_analysis/data/step7_uncertainty_results.json
  - phase3_analysis/figures/fig_p3_11_tornado.pdf/png
  - phase3_analysis/figures/fig_p3_12_uncertainty_summary.pdf/png
"""
import json
import logging
import os

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

# ---- Load all upstream results ----
with open(f"{DATA_DIR}/step6_model_results.json") as f:
    step6 = json.load(f)

with open(f"{DATA_DIR}/its_results.json") as f:
    its_results = json.load(f)

with open(f"{DATA_DIR}/bsts_results.json") as f:
    bsts_results = json.load(f)

with open(f"{DATA_DIR}/compositional_results.json") as f:
    comp_results = json.load(f)

with open(f"{DATA_DIR}/refutation_results.json") as f:
    refutation = json.load(f)

with open(f"{DATA_DIR}/ep_update_results.json") as f:
    ep_results = json.load(f)

df = pd.read_parquet(f"{DATA_DIR}/analysis_dataset.parquet")

log.info("Loaded all upstream data.")


# ===========================================================================
# Section 1: Uncertainty sources inventory
# ===========================================================================

log.info("\n=== Uncertainty Source Inventory ===")

# For national series (primary result)
baseline = step6["national"]["model"]["level_shift"]
boot_se = step6["national"]["bootstrap"]["boot_se"]

# --- Source 1: Statistical (bootstrap SE) ---
stat_unc = boot_se
log.info(f"1. Statistical (bootstrap): +/-{stat_unc:.1f} yuan")

# --- Source 2: Method disagreement (ITS vs BSTS) ---
its_shift = its_results["national"]["primary"]["level_shift"]
bsts_shift = bsts_results["national"]["mean_effect"]
method_unc = abs(its_shift - bsts_shift) / 2.0  # half-range as uncertainty
log.info(f"2. Method disagreement (ITS vs BSTS): +/-{method_unc:.1f} yuan "
         f"(ITS={its_shift:.0f}, BSTS={bsts_shift:.0f})")

# --- Source 3: COVID confounding ---
# Range between primary (excl 2020) and include-2020 specifications
sens = step6["national"]["sensitivity"]
primary_shift = sens["primary_2021_excl2020"]["level_shift"]
incl2020_shift = sens["include_2020"]["level_shift"]
covid_indicator_shift = sens["covid_indicator"]["level_shift"]
# Use range across all COVID specifications
covid_specs = [primary_shift, incl2020_shift, covid_indicator_shift]
covid_unc = (max(covid_specs) - min(covid_specs)) / 2.0
log.info(f"3. COVID handling: +/-{covid_unc:.1f} yuan "
         f"(range: [{min(covid_specs):.0f}, {max(covid_specs):.0f}])")

# --- Source 4: Intervention date ---
primary_2021 = sens["primary_2021_excl2020"]["level_shift"]
int_2022 = sens["intervention_2022"]["level_shift"]
date_unc = abs(primary_2021 - int_2022) / 2.0
log.info(f"4. Intervention date (2021 vs 2022): +/-{date_unc:.1f} yuan "
         f"(2021={primary_2021:.0f}, 2022={int_2022:.0f})")

# --- Source 5: Pre-period window ---
short_pre = sens.get("short_preperiod_2018_2019", {}).get("level_shift")
if short_pre is not None:
    preperiod_unc = abs(primary_2021 - short_pre) / 2.0
else:
    preperiod_unc = 0.0
log.info(f"5. Pre-period window: +/-{preperiod_unc:.1f} yuan "
         f"(full={primary_2021:.0f}, short={short_pre})")

# --- Source 6: Demographic normalization ---
# Per-child ITS eliminates signal (p=0.48), so the entire effect size
# is the range of uncertainty from demographic confounding
perbirth_shift = comp_results["perbirth_its"]["level_shift"]
# The difference between aggregate and per-birth result represents
# the demographic component
demo_unc = abs(primary_2021)  # worst case: entire effect is demographic
# More conservative: half the difference
demo_unc_conservative = abs(primary_2021 - 0) / 2.0  # 0 is the per-birth result
log.info(f"6. Demographic normalization: +/-{demo_unc_conservative:.1f} yuan "
         f"(per-capita shift={primary_2021:.0f}, per-birth shift={perbirth_shift:.1f} [p=0.48])")

# --- Source 7: Proxy variable (education share assumption) ---
# CIEFR-HS: education = 73% of the proxy category
# If we assume education is 73% of the NBS proxy, the education-only shift
# would be 73% * total shift. The uncertainty is the range from 60% to 85%.
edu_share_low = 0.60
edu_share_mid = 0.73
edu_share_high = 0.85
proxy_range = [primary_2021 * edu_share_low, primary_2021 * edu_share_high]
proxy_unc = abs(proxy_range[1] - proxy_range[0]) / 2.0
log.info(f"7. Proxy variable (education share 60-85%): +/-{proxy_unc:.1f} yuan "
         f"(range: [{proxy_range[0]:.0f}, {proxy_range[1]:.0f}])")

# --- Source 8: CPI deflator choice ---
# From strategy: 1.5pp cumulative difference between education CPI and overall CPI
cpi_unc = abs(primary_2021) * 0.015  # 1.5% effect
log.info(f"8. CPI deflator choice: +/-{cpi_unc:.1f} yuan (1.5% of effect)")


# ===========================================================================
# Section 2: Combine uncertainties
# ===========================================================================

log.info("\n=== Uncertainty Combination ===")

# Systematic sources (combined in quadrature)
syst_sources = {
    "Method disagreement (ITS vs BSTS)": method_unc,
    "COVID handling specification": covid_unc,
    "Intervention date (2021 vs 2022)": date_unc,
    "Pre-period window definition": preperiod_unc,
    "Proxy variable (education share)": proxy_unc,
    "CPI deflator choice": cpi_unc,
}

total_syst = np.sqrt(sum(v**2 for v in syst_sources.values()))
total_unc = np.sqrt(stat_unc**2 + total_syst**2)

log.info(f"Statistical uncertainty: +/-{stat_unc:.1f} yuan")
log.info(f"Systematic uncertainty: +/-{total_syst:.1f} yuan")
log.info(f"Total uncertainty: +/-{total_unc:.1f} yuan")
log.info(f"Effect/total_unc ratio: {abs(baseline)/total_unc:.2f}")

# Dominant source identification
all_sources_sorted = sorted(
    [("Statistical (bootstrap)", stat_unc)] + list(syst_sources.items()),
    key=lambda x: x[1], reverse=True,
)
total_var = sum(v**2 for _, v in all_sources_sorted)

log.info("\nUncertainty ranking:")
for name, val in all_sources_sorted:
    frac = val**2 / total_var * 100
    log.info(f"  {name}: +/-{val:.1f} yuan ({frac:.1f}% of variance)")


# ===========================================================================
# Section 3: Build comprehensive uncertainty table for all series
# ===========================================================================

series_labels = ["national", "urban", "rural"]
final_results = {}

for label in series_labels:
    s6 = step6[label]
    bsts = bsts_results[label]

    primary_shift = s6["model"]["level_shift"]
    primary_se = s6["model"]["level_shift_se"]
    boot_se_val = s6["bootstrap"]["boot_se"]

    pre_mean = s6["effect_size"]["pre_policy_mean"]

    # Statistical
    stat = boot_se_val

    # Method disagreement
    its_val = s6["model"]["level_shift"]
    bsts_val = bsts["mean_effect"]
    meth = abs(its_val - bsts_val) / 2.0

    # COVID handling
    sens_label = s6["sensitivity"]
    covid_specs_label = [
        sens_label["primary_2021_excl2020"]["level_shift"],
        sens_label["include_2020"]["level_shift"],
        sens_label["covid_indicator"]["level_shift"],
    ]
    covid = (max(covid_specs_label) - min(covid_specs_label)) / 2.0

    # Intervention date
    int_date = abs(
        sens_label["primary_2021_excl2020"]["level_shift"]
        - sens_label["intervention_2022"]["level_shift"]
    ) / 2.0

    # Proxy
    proxy = abs(sens_label["primary_2021_excl2020"]["level_shift"]) * (0.85 - 0.60) / 2.0

    # CPI
    cpi_val = abs(sens_label["primary_2021_excl2020"]["level_shift"]) * 0.015

    syst_total = np.sqrt(meth**2 + covid**2 + int_date**2 + proxy**2 + cpi_val**2)
    total = np.sqrt(stat**2 + syst_total**2)

    final_results[label] = {
        "central_value": primary_shift,
        "stat_unc": stat,
        "syst_unc": syst_total,
        "total_unc": total,
        "pct_effect": primary_shift / pre_mean * 100,
        "pct_total_unc": total / pre_mean * 100,
        "significance": abs(primary_shift) / total,
        "classification": "CORRELATION",
        "breakdown": {
            "Statistical (bootstrap)": stat,
            "Method disagreement": meth,
            "COVID handling": covid,
            "Intervention date": int_date,
            "Proxy variable": proxy,
            "CPI deflator": cpi_val,
        },
        "demographic_caveat": "Per-birth normalization eliminates signal (p=0.48). "
                              "Demographic decline is an additional confound not included "
                              "in quadrature sum because it is not an additive systematic "
                              "-- it questions the existence of the effect itself.",
        "boot_ci_95": s6["bootstrap"]["ci_95"],
        "boot_ci_90": s6["bootstrap"]["ci_90"],
        "boot_ci_68": s6["bootstrap"]["ci_68"],
    }

    log.info(f"\n{label}: {primary_shift:.0f} +/- {stat:.0f} (stat) +/- {syst_total:.0f} (syst) "
             f"= +/- {total:.0f} (total) [{primary_shift/pre_mean*100:.1f}%]")
    log.info(f"  Significance: {abs(primary_shift)/total:.2f} sigma")


# ===========================================================================
# Section 4: Final EP summary table
# ===========================================================================

log.info("\n=== Final EP Summary ===")

ep_summary = {}
for edge_name, edge_data in ep_results.items():
    ep_summary[edge_name] = {
        "phase0_ep": edge_data["phase0_ep"],
        "phase1_ep": edge_data["phase1_ep"],
        "phase3_ep": edge_data["phase3_ep"],
        "classification": edge_data["classification"],
        "change_reason": edge_data["change_reason"],
    }
    log.info(f"  {edge_name}: EP={edge_data['phase3_ep']:.2f} [{edge_data['classification']}]")


# ===========================================================================
# Section 5: Sanity checks
# ===========================================================================

log.info("\n=== Sanity Checks ===")

sanity_checks = {}

for label in series_labels:
    r = final_results[label]
    checks = {
        "total_unc_smaller_than_effect": abs(r["central_value"]) > r["total_unc"],
        "effect_over_total_unc": abs(r["central_value"]) / r["total_unc"],
        "syst_dominant": r["syst_unc"] > r["stat_unc"],
        "stat_frac": r["stat_unc"]**2 / (r["stat_unc"]**2 + r["syst_unc"]**2) * 100,
        "syst_frac": r["syst_unc"]**2 / (r["stat_unc"]**2 + r["syst_unc"]**2) * 100,
    }

    sanity_checks[label] = checks

    if checks["total_unc_smaller_than_effect"]:
        log.info(f"{label}: Effect ({r['central_value']:.0f}) > total unc ({r['total_unc']:.0f}) "
                 f"-- effect is formally significant at {checks['effect_over_total_unc']:.1f} sigma")
    else:
        log.info(f"{label}: Effect ({r['central_value']:.0f}) < total unc ({r['total_unc']:.0f}) "
                 f"-- NOT SIGNIFICANT including systematics")

    if checks["syst_dominant"]:
        log.info(f"  WARNING: Systematic uncertainty dominates ({checks['syst_frac']:.0f}%). "
                 f"More data will not help -- better methods or data quality needed.")
    else:
        log.info(f"  Statistical uncertainty dominates ({checks['stat_frac']:.0f}%).")


# ===========================================================================
# Figure: Tornado chart (national series)
# ===========================================================================

log.info("\n=== Generating tornado chart ===")

# Build sensitivity data for national
nat = final_results["national"]
baseline_val = nat["central_value"]

sensitivities = []
for source_name, unc_val in nat["breakdown"].items():
    sensitivities.append({
        "parameter": source_name,
        "low": baseline_val - unc_val,
        "high": baseline_val + unc_val,
        "baseline": baseline_val,
        "unc": unc_val,
    })

# Add demographic caveat as special entry
sensitivities.append({
    "parameter": "Demographic normalization\n(eliminates signal)",
    "low": 0.0,  # per-birth shows no effect
    "high": baseline_val,
    "baseline": baseline_val,
    "unc": abs(baseline_val) / 2.0,
})

# Sort by range (largest first)
sensitivities.sort(key=lambda s: abs(s["high"] - s["low"]), reverse=True)

fig, ax = plt.subplots(figsize=(10, max(4, len(sensitivities) * 0.6 + 1)))

params = [s["parameter"] for s in sensitivities]
y_pos = np.arange(len(params))

for i, s in enumerate(sensitivities):
    low_delta = s["low"] - baseline_val
    high_delta = s["high"] - baseline_val

    # Special color for demographic (it questions existence of signal)
    if "Demographic" in s["parameter"]:
        color_lo = "#FF9800"
        color_hi = "#FF9800"
    else:
        color_lo = "#F44336"
        color_hi = "#2196F3"

    ax.barh(i, high_delta, left=baseline_val, height=0.6, color=color_hi, alpha=0.7)
    ax.barh(i, low_delta, left=baseline_val, height=0.6, color=color_lo, alpha=0.7)

ax.axvline(baseline_val, color="black", linewidth=1.5, linestyle="--",
           label=f"Central: {baseline_val:.0f} yuan")
ax.axvline(0, color="gray", linewidth=0.5, linestyle=":")
ax.set_yticks(y_pos)
ax.set_yticklabels(params, fontsize="small")
ax.set_xlabel("Level shift [2015 yuan]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes,
        fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_11_tornado.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_11_tornado.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved tornado chart to {FIG_DIR}/fig_p3_11_tornado.pdf")


# ===========================================================================
# Figure: Uncertainty summary -- forest plot of all series
# ===========================================================================

fig, ax = plt.subplots(figsize=(10, 5))

y_positions = []
y_labels = []
idx = 0

for label in ["national", "urban", "rural"]:
    r = final_results[label]

    # ITS with total uncertainty
    ax.errorbar(r["central_value"], idx, xerr=r["total_unc"],
                fmt="o", color="#2196F3", capsize=6, markersize=8,
                linewidth=2, label="ITS total unc." if idx == 0 else None)
    y_positions.append(idx)
    y_labels.append(f"{label.capitalize()} (ITS)")

    # BSTS estimate
    bsts_val = bsts_results[label]["mean_effect"]
    bsts_se = bsts_results[label]["boot_se"]
    ax.errorbar(bsts_val, idx - 0.3, xerr=1.645 * bsts_se,
                fmt="s", color="#F44336", capsize=6, markersize=7,
                linewidth=1.5, label="BSTS 90% CI" if idx == 0 else None)
    y_positions.append(idx - 0.3)
    y_labels.append(f"{label.capitalize()} (BSTS)")

    idx += 1.2

ax.axvline(0, color="black", linewidth=1, linestyle="--")
ax.set_yticks([p for p in y_positions])
ax.set_yticklabels(y_labels, fontsize="small")
ax.set_xlabel("Level shift [2015 yuan]")
ax.legend(fontsize="small", loc="lower left")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes,
        fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_12_uncertainty_summary.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_12_uncertainty_summary.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved uncertainty summary to {FIG_DIR}/fig_p3_12_uncertainty_summary.pdf")


# ===========================================================================
# Save all results
# ===========================================================================

output = {
    "final_results": {},
    "uncertainty_breakdown_national": {},
    "ep_summary": ep_summary,
    "sanity_checks": sanity_checks,
    "demographic_caveat": (
        "Per-birth normalization eliminates the ITS level shift (p=0.48). "
        "This means the aggregate spending decline is at least partially "
        "attributable to demographic decline (47% fewer births 2016-2024). "
        "The demographic confound is not included in the quadrature sum "
        "because it questions the existence of the effect itself, rather than "
        "shifting its magnitude. If the effect does not exist, the uncertainty "
        "envelope is irrelevant."
    ),
}

for label in series_labels:
    r = final_results[label]
    output["final_results"][label] = {
        "central_value": r["central_value"],
        "stat_unc": r["stat_unc"],
        "syst_unc": r["syst_unc"],
        "total_unc": r["total_unc"],
        "pct_effect": r["pct_effect"],
        "pct_total_unc": r["pct_total_unc"],
        "significance_sigma": r["significance"],
        "classification": r["classification"],
        "boot_ci_95": r["boot_ci_95"],
        "boot_ci_90": r["boot_ci_90"],
        "boot_ci_68": r["boot_ci_68"],
    }

# National breakdown
for source, val in nat["breakdown"].items():
    frac = val**2 / (nat["stat_unc"]**2 + nat["syst_unc"]**2) * 100
    output["uncertainty_breakdown_national"][source] = {
        "shift": val,
        "frac_of_total_var_pct": frac,
    }

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.bool_,)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

with open(f"{DATA_DIR}/step7_uncertainty_results.json", "w") as f:
    json.dump(output, f, indent=2, cls=NumpyEncoder)

log.info(f"\nSaved Step 7 results to {DATA_DIR}/step7_uncertainty_results.json")
log.info("\nStep 7 (Uncertainty Quantification) complete.")
