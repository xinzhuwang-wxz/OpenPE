"""
Step 3.1/3.2 continued: VAR Impulse Response and Mediation Decomposition.

Three-variable VAR: DE -> services_VA -> employment_services
Cholesky ordering reflects causal DAG.
Impulse response functions + FEVD for mechanism decomposition.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.api import VAR
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

df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)

results = {}

# ---------------------------------------------------------------------------
# Trivariate VAR for mediation: DE -> Services VA -> Services Employment
# ---------------------------------------------------------------------------
log.info("=" * 60)
log.info("VAR IMPULSE RESPONSE: Mediation Decomposition")
log.info("=" * 60)

# Use first differences (all are I(1))
cols_mediation = ["d_digital_economy_index", "d_services_value_added_pct_gdp", "d_employment_services_pct"]
col_labels = ["d(DE)", "d(Serv VA)", "d(Serv Emp)"]

sub = df[cols_mediation].dropna()
T = len(sub)
log.info(f"Mediation VAR: T={T} (first differences)")

# Lag selection
var_model = VAR(sub.values)
max_lags = min(3, T // (len(cols_mediation) + 2) - 1)
max_lags = max(max_lags, 1)
lag_order = var_model.select_order(maxlags=max_lags)
p_opt = lag_order.aic
if p_opt == 0:
    p_opt = 1
log.info(f"  Optimal lag: p={p_opt} (AIC)")

# Fit VAR
var_result = var_model.fit(maxlags=p_opt, trend="c")
log.info(f"  AIC={var_result.aic:.3f}, BIC={var_result.bic:.3f}")

# Impulse response (Cholesky decomposition -- ordering matters)
# Ordering: DE -> Serv VA -> Serv Emp (matches causal DAG)
irf = var_result.irf(periods=10)
# The orthogonalized IRF is stored in .irfs (Cholesky decomposition)
irf_orth = irf.irfs  # shape: (periods+1, n_vars, n_vars)

# Bootstrap confidence intervals
n_boot = 1000
irf_boot = np.zeros((n_boot, 11, len(cols_mediation), len(cols_mediation)))

for b in range(n_boot):
    resids = var_result.resid
    idx = np.random.randint(0, len(resids), size=len(resids))
    resid_boot = resids[idx]

    # Reconstruct data under bootstrap
    fitted = var_result.fittedvalues
    y_boot_vals = fitted + resid_boot
    y_boot_df = pd.DataFrame(y_boot_vals, columns=cols_mediation)

    try:
        var_boot = VAR(y_boot_df.values)
        vr_boot = var_boot.fit(maxlags=p_opt, trend="c")
        irf_boot_obj = vr_boot.irf(periods=10)
        irf_boot[b] = irf_boot_obj.irfs
    except Exception:
        irf_boot[b] = np.nan

# Confidence intervals
irf_lo = np.nanpercentile(irf_boot, 5, axis=0)
irf_hi = np.nanpercentile(irf_boot, 95, axis=0)

# ---------------------------------------------------------------------------
# Plot: Impulse responses (3x3 grid - response of each to shock in each)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(3, 3, figsize=(18, 18))
periods = np.arange(11)

for i in range(3):
    for j in range(3):
        ax = axes[i, j]
        ax.plot(periods, irf.irfs[:, i, j], "o-", color="#2196F3", linewidth=2, markersize=4)
        ax.fill_between(periods, irf_lo[:, i, j], irf_hi[:, i, j], alpha=0.2, color="#2196F3")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_xlabel("Periods [years]")
        ax.set_ylabel(f"Response of {col_labels[i]}")
        ax.legend([f"Shock to {col_labels[j]}"], fontsize="small")
        if i == 0 and j == 0:
            ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes,
                    fontsize=8, va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig("phase3_analysis/figures/var_irf_mediation.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/var_irf_mediation.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Figure saved: var_irf_mediation.pdf/png")

# ---------------------------------------------------------------------------
# FEVD: Forecast Error Variance Decomposition
# ---------------------------------------------------------------------------
fevd = var_result.fevd(periods=10)
log.info("\nForecast Error Variance Decomposition:")

fevd_data = {}
for i, col in enumerate(col_labels):
    log.info(f"\n  {col}:")
    decomp = fevd.decomp[i]  # shape: (periods, n_vars)
    for h in [0, 1, 2, 4, 9]:
        if h < len(decomp):
            log.info(f"    h={h+1}: " + " | ".join(f"{col_labels[j]}={decomp[h,j]*100:.1f}%" for j in range(3)))
    fevd_data[col] = decomp.tolist()

# ---------------------------------------------------------------------------
# Mediation share estimation
# ---------------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("MEDIATION SHARE ESTIMATION")
log.info("=" * 60)

# Total effect: cumulative response of employment to DE shock (direct + indirect)
total_effect_cum = np.cumsum(irf.irfs[:, 2, 0])  # response of emp to DE shock

# Direct effect: from bivariate VAR (DE, emp) only -- no mediator
cols_direct = ["d_digital_economy_index", "d_employment_services_pct"]
sub_direct = df[cols_direct].dropna()
var_direct = VAR(sub_direct.values)
vr_direct = var_direct.fit(maxlags=p_opt, trend="c")
irf_direct = vr_direct.irf(periods=10)
direct_effect_cum = np.cumsum(irf_direct.irfs[:, 1, 0])

# Indirect (mediated) effect = total - direct
indirect_effect = total_effect_cum - direct_effect_cum

# Mediation share at different horizons
log.info("\n  Mediation share (indirect / total):")
for h in [2, 4, 6, 9]:
    if abs(total_effect_cum[h]) > 1e-10:
        med_share = indirect_effect[h] / total_effect_cum[h] * 100
        log.info(f"    h={h+1}: total={total_effect_cum[h]:.4f}, direct={direct_effect_cum[h]:.4f}, "
                 f"indirect={indirect_effect[h]:.4f}, mediation={med_share:.1f}%")
    else:
        log.info(f"    h={h+1}: total effect near zero -- mediation share undefined")

results["mediation"] = {
    "total_effect_cum": total_effect_cum.tolist(),
    "direct_effect_cum": direct_effect_cum.tolist(),
    "indirect_effect": indirect_effect.tolist(),
}

# ---------------------------------------------------------------------------
# Creation vs Substitution: Bivariate IRFs
# ---------------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("CREATION vs SUBSTITUTION: Impulse Responses")
log.info("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, (emp_col, label, color) in enumerate([
    ("d_employment_services_pct", "Services (creation)", "#4CAF50"),
    ("d_employment_industry_pct", "Industry (substitution)", "#F44336"),
]):
    cols_bi = ["d_digital_economy_index", emp_col]
    sub_bi = df[cols_bi].dropna()
    var_bi = VAR(sub_bi.values)
    vr_bi = var_bi.fit(maxlags=1, trend="c")
    irf_bi = vr_bi.irf(periods=10)

    # Bootstrap CI
    boot_irf = np.zeros((500, 11))
    for b in range(500):
        resids_b = vr_bi.resid
        idx_b = np.random.randint(0, len(resids_b), size=len(resids_b))
        y_b = vr_bi.fittedvalues + resids_b[idx_b]
        try:
            vr_b = VAR(y_b).fit(maxlags=1, trend="c")
            boot_irf[b] = vr_b.irf(periods=10).orth_ma_rep[:, 1, 0]
        except Exception:
            boot_irf[b] = np.nan

    lo = np.nanpercentile(boot_irf, 5, axis=0)
    hi = np.nanpercentile(boot_irf, 95, axis=0)

    ax = axes[idx]
    ax.plot(periods, irf_bi.irfs[:, 1, 0], "o-", color=color, linewidth=2, markersize=5)
    ax.fill_between(periods, lo, hi, alpha=0.2, color=color)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Periods [years]")
    ax.set_ylabel(f"Response of {label} [pp]")
    ax.legend([f"DE shock -> {label}", "90% CI"], fontsize="small")

    # Record peak response
    peak = irf_bi.irfs[:, 1, 0]
    log.info(f"  {label}: peak response = {peak[1]:.4f} at h=1, cumulative(10) = {np.sum(peak):.4f}")

    results[f"irf_{label.split()[0].lower()}"] = {
        "response": peak.tolist(),
        "ci_lo": lo.tolist(),
        "ci_hi": hi.tolist(),
    }

axes[0].text(0.02, 0.98, "OpenPE Analysis", transform=axes[0].transAxes,
             fontsize=8, va="top", ha="left", color="gray", style="italic")
fig.tight_layout()
fig.savefig("phase3_analysis/figures/irf_creation_substitution.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("phase3_analysis/figures/irf_creation_substitution.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Figure saved: irf_creation_substitution.pdf/png")

# Save results
output_path = "phase3_analysis/scripts/var_mediation_results.json"
with open(output_path, "w") as f:
    json.dump(results, f, indent=2,
              default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else x)
log.info(f"\nResults saved to {output_path}")
