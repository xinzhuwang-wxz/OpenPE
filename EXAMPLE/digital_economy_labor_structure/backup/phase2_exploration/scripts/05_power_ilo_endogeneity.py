"""Step 2.3: Power analysis (Monte Carlo) and ILO endogeneity check."""

import logging
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from rich.logging import RichHandler
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")

DATA_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/processed")
FIG_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/figures")
OUT_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/scripts")

df = pd.read_parquet(DATA_DIR / "analysis_ready.parquet")

# ===================================================
# POWER ANALYSIS: Monte Carlo simulation for Toda-Yamamoto
# ===================================================
log.info("=== POWER ANALYSIS: Toda-Yamamoto at T=24 ===")

np.random.seed(42)
T = 24
n_sims = 5000
alpha = 0.10  # test at 10% level (liberal, given small T)

# Reference effect sizes from published literature
# Zhu et al. (2023): DID coeff ~0.03-0.05 for smart city on employment
# We translate to VAR coefficient for Granger context
# Small effect: beta = 0.15, Medium: 0.30, Large: 0.50

effect_sizes = [0.0, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
power_results = {}

for effect in effect_sizes:
    rejections = 0
    for sim in range(n_sims):
        # Generate bivariate VAR(1):
        # x_t = 0.7*x_{t-1} + e1_t
        # y_t = effect*x_{t-1} + 0.7*y_{t-1} + e2_t
        x = np.zeros(T + 50)  # burnin
        y = np.zeros(T + 50)
        for t in range(1, T + 50):
            x[t] = 0.7 * x[t-1] + np.random.normal(0, 1)
            y[t] = effect * x[t-1] + 0.7 * y[t-1] + np.random.normal(0, 1)
        
        x = x[50:]  # discard burnin
        y = y[50:]
        
        # Toda-Yamamoto: fit VAR(p+d) in levels, test restriction on lag 1 of x in y equation
        # Simplified: fit y_t = a + b1*x_{t-1} + b2*x_{t-2} + c1*y_{t-1} + c2*y_{t-2} + e
        # (p=1, d=1, so fit 2 lags, test b1=0)
        p, d = 1, 1
        max_lag = p + d
        
        Y = y[max_lag:]
        X_mat = np.column_stack([
            np.ones(T - max_lag),
            x[max_lag-1:-1],   # x_{t-1} (restricted)
            x[max_lag-2:-2],   # x_{t-2} (extra lag, not tested)
            y[max_lag-1:-1],   # y_{t-1}
            y[max_lag-2:-2],   # y_{t-2}
        ])
        
        try:
            # Unrestricted
            beta_u = np.linalg.lstsq(X_mat, Y, rcond=None)[0]
            rss_u = np.sum((Y - X_mat @ beta_u)**2)
            
            # Restricted (drop x_{t-1})
            X_r = np.column_stack([X_mat[:, 0], X_mat[:, 2], X_mat[:, 3], X_mat[:, 4]])
            beta_r = np.linalg.lstsq(X_r, Y, rcond=None)[0]
            rss_r = np.sum((Y - X_r @ beta_r)**2)
            
            # Wald statistic (asymptotically chi2(1) under H0)
            n_eff = len(Y)
            W = (rss_r - rss_u) / (rss_u / (n_eff - X_mat.shape[1]))
            p_val = 1 - stats.chi2.cdf(W, 1)
            
            if p_val < alpha:
                rejections += 1
        except Exception:
            pass
    
    power = rejections / n_sims
    power_results[effect] = power
    log.info(f"  Effect={effect:.2f}: Power={power:.3f} (rejections={rejections}/{n_sims})")

# Save
with open(OUT_DIR / "power_analysis_results.json", "w") as f:
    json.dump({str(k): v for k, v in power_results.items()}, f, indent=2)

# ===================================================
# FIGURE: Power curve
# ===================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
effects = list(power_results.keys())
powers = list(power_results.values())
ax.plot(effects, powers, "o-", color="#2c3e50", linewidth=2, markersize=8)
ax.axhline(0.80, ls="--", color="red", alpha=0.5, label="80% power threshold")
ax.axhline(alpha, ls=":", color="gray", alpha=0.5, label=f"Size = {alpha}")
ax.set_xlabel("True VAR(1) coefficient (effect size)", fontsize="small")
ax.set_ylabel("Power (rejection rate)", fontsize="small")
ax.legend(fontsize="small")
ax.set_ylim(0, 1.05)
ax.tick_params(labelsize="x-small")

# Annotate reference effect sizes
ax.annotate("Small\n(0.15)", xy=(0.15, power_results.get(0.15, 0)), fontsize="x-small",
            textcoords="offset points", xytext=(10, 10), arrowprops=dict(arrowstyle="->", alpha=0.5))
ax.annotate("Medium\n(0.30)", xy=(0.30, power_results.get(0.30, 0)), fontsize="x-small",
            textcoords="offset points", xytext=(10, 10), arrowprops=dict(arrowstyle="->", alpha=0.5))

for ext in ["pdf", "png"]:
    fig.savefig(FIG_DIR / f"power_analysis_toda_yamamoto.{ext}", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved power_analysis_toda_yamamoto")

# ===================================================
# ILO ENDOGENEITY CHECK
# ===================================================
log.info("\n=== ILO ENDOGENEITY CHECK ===")
log.info("ILO modeled employment estimates methodology for China:")
log.info("  - ILO uses econometric models that incorporate GDP, demographic trends,")
log.info("    educational attainment, and labor force surveys as inputs")
log.info("  - For countries like China with infrequent labor force surveys,")
log.info("    the models rely more heavily on GDP and demographic covariates")
log.info("  - This creates potential mechanical correlation between")
log.info("    employment estimates and GDP/urbanization/demographics")
log.info("")

# Test: regress employment on GDP and urbanization
# If R^2 is very high AND residuals show no independent variation, ILO is endogenous
emp_vars = ["employment_services_pct", "employment_industry_pct", "employment_agriculture_pct"]
control_vars = ["gdp_per_capita_usd", "urban_population_pct", "population_15_64_pct"]

log.info("Regression of employment shares on GDP + urbanization + demographics:")
for emp_var in emp_vars:
    valid = df[control_vars + [emp_var]].dropna()
    X = valid[control_vars].values
    X = np.column_stack([np.ones(len(X)), X])
    y = valid[emp_var].values
    
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_hat = X @ beta
    ss_res = np.sum((y - y_hat)**2)
    ss_tot = np.sum((y - y.mean())**2)
    r2 = 1 - ss_res / ss_tot
    
    # Check if residuals have autocorrelation (Durbin-Watson)
    resid = y - y_hat
    dw = np.sum(np.diff(resid)**2) / np.sum(resid**2)
    
    log.info(f"  {emp_var}: R2={r2:.4f}, DW={dw:.3f}")

log.info("\nInterpretation:")
log.info("  If R2 > 0.95, ILO employment shares are largely predicted by")
log.info("  GDP/urbanization/demographics, suggesting mechanical correlation.")
log.info("  Sensitivity test: compare DE coefficient with/without these controls.")

# Sensitivity: correlation of DE index with employment controlling for GDP/urban/demo
log.info("\n=== PARTIAL CORRELATION: DE vs Employment (controlling GDP, Urban, Demo) ===")
from numpy.linalg import lstsq

for emp_var in ["employment_services_pct", "employment_industry_pct"]:
    valid = df[["digital_economy_index"] + control_vars + [emp_var]].dropna()
    
    # Simple correlation
    r_simple = np.corrcoef(valid["digital_economy_index"], valid[emp_var])[0, 1]
    
    # Partial correlation: residualize both on controls
    X_ctrl = np.column_stack([np.ones(len(valid)), valid[control_vars].values])
    
    de_resid = valid["digital_economy_index"].values - X_ctrl @ lstsq(X_ctrl, valid["digital_economy_index"].values, rcond=None)[0]
    emp_resid = valid[emp_var].values - X_ctrl @ lstsq(X_ctrl, valid[emp_var].values, rcond=None)[0]
    
    r_partial = np.corrcoef(de_resid, emp_resid)[0, 1]
    
    log.info(f"  {emp_var}:")
    log.info(f"    Simple r with DE: {r_simple:.3f}")
    log.info(f"    Partial r (ctrl GDP/urban/demo): {r_partial:.3f}")
    log.info(f"    Change: {r_partial - r_simple:+.3f}")

# ===================================================
# FIGURE: ILO endogeneity scatter
# ===================================================
fig, axes = plt.subplots(1, 3, figsize=(30, 10))

for i, emp_var in enumerate(emp_vars):
    ax = axes[i]
    valid = df[control_vars + [emp_var]].dropna()
    X = np.column_stack([np.ones(len(valid)), valid[control_vars].values])
    y = valid[emp_var].values
    beta = lstsq(X, y, rcond=None)[0]
    y_hat = X @ beta
    resid = y - y_hat
    
    ax.scatter(y_hat, resid, color="#3498db", s=40, alpha=0.7)
    ax.axhline(0, ls="--", color="gray", alpha=0.5)
    ax.set_xlabel(f"Predicted {emp_var[:20]}...", fontsize="small")
    ax.set_ylabel("Residual", fontsize="small")
    ax.tick_params(labelsize="x-small")
    
    r2 = 1 - np.sum(resid**2) / np.sum((y - y.mean())**2)
    ax.text(0.05, 0.95, f"R2={r2:.3f}", transform=ax.transAxes, fontsize="small", va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

for ext in ["pdf", "png"]:
    fig.savefig(FIG_DIR / f"ilo_endogeneity_residuals.{ext}", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved ilo_endogeneity_residuals")
