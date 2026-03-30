"""
Independent Reproduction: Phase 5 Verification Program 1
Reproduces key Phase 3 results from scratch without using any Phase 3 code.

Target results to reproduce:
1. Toda-Yamamoto Granger causality: DE-->SUB (W=5.84 bivariate, W=13.33 with DEMO)
2. ARDL(1,1) long-run coefficient: 7.15 pp bivariate
3. Johansen cointegration test: trace=19.04
4. Structural break counterfactual deviation: -4.45 pp for industry emp
"""
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from rich.logging import RichHandler
from scipy import stats as scipy_stats
from statsmodels.tsa.vector_ar.vecm import coint_johansen

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

BASE = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure")
DATA = BASE / "data" / "processed"
OUT = BASE / "phase5_verification"

# ---- Load data independently ----
df = pd.read_parquet(DATA / "china_national_panel_merged.parquet")
log.info(f"Loaded merged panel: {df.shape}")

de = df["digital_economy_index"].values
ind_emp = df["employment_industry_pct"].values
svc_emp = df["employment_services_pct"].values
svc_va = df["services_value_added_pct_gdp"].values
demo = df["population_15_64_pct"].values
years = df["year"].values
T = len(de)
log.info(f"T = {T}, year range: {years[0]}-{years[-1]}")

results = {}


def build_var_regressors(data_mat, total_lags):
    """Build Y (dependent) and X (regressor) matrices for a VAR system."""
    n_obs = len(data_mat) - total_lags
    k = data_mat.shape[1]
    Y_dep = data_mat[total_lags:]
    X_reg = np.ones((n_obs, 1))  # constant
    for lag in range(1, total_lags + 1):
        X_reg = np.hstack([X_reg, data_mat[total_lags - lag : total_lags - lag + n_obs]])
    return Y_dep, X_reg


def toda_yamamoto(y_var, x_vars, p_opt=2, d_max=1):
    """
    Toda-Yamamoto Granger causality test.
    Tests whether x_vars Granger-cause y_var.
    x_vars can be a 1D array (single var) or 2D (multiple vars).
    Returns Wald statistic (chi2) and p-value.
    """
    if x_vars.ndim == 1:
        x_vars = x_vars.reshape(-1, 1)
    k_x = x_vars.shape[1]
    data_mat = np.column_stack([y_var, x_vars])
    k_total = data_mat.shape[1]
    total_lags = p_opt + d_max

    Y_all, X_all = build_var_regressors(data_mat, total_lags)
    n = len(Y_all)

    # Focus on the y equation (column 0)
    y_dep = Y_all[:, 0]

    # Unrestricted OLS for y equation
    ols_u = sm.OLS(y_dep, X_all).fit()

    # Identify columns for x-variable lags 1..p (NOT lags p+1..p+d_max)
    # Column layout in X_all: [const, lag1_var0, lag1_var1, ..., lag1_var_{k-1},
    #                                  lag2_var0, lag2_var1, ..., etc.]
    # At lag j (1-based), variable v is at column: 1 + (j-1)*k_total + v
    # x variables are at indices 1..k_x in the data matrix
    drop_cols = []
    for j in range(1, p_opt + 1):
        for v in range(1, k_x + 1):
            col_idx = 1 + (j - 1) * k_total + v
            drop_cols.append(col_idx)

    keep_cols = [i for i in range(X_all.shape[1]) if i not in drop_cols]
    X_r = X_all[:, keep_cols]
    ols_r = sm.OLS(y_dep, X_r).fit()

    q = len(drop_cols)  # number of restrictions
    SSR_r = ols_r.ssr
    SSR_u = ols_u.ssr
    W = n * (SSR_r - SSR_u) / SSR_r

    p_val = 1 - scipy_stats.chi2.cdf(W, q)
    return W, p_val


# ============================================================
# 1. TODA-YAMAMOTO GRANGER CAUSALITY
# ============================================================
log.info("=" * 60)
log.info("1. Toda-Yamamoto Granger Causality")

# Bivariate: DE --> Industry Emp
W_biv, p_biv = toda_yamamoto(ind_emp, de, p_opt=2, d_max=1)
log.info(f"Bivariate DE-->IND_EMP: W={W_biv:.2f}, p={p_biv:.4f}")
results["granger_biv_W"] = W_biv
results["granger_biv_p"] = p_biv

# Trivariate: DE --> Industry Emp | DEMO
W_tri, p_tri = toda_yamamoto(ind_emp, np.column_stack([de, demo]), p_opt=2, d_max=1)
log.info(f"Trivariate DE-->IND_EMP|DEMO: W={W_tri:.2f}, p={p_tri:.4f}")
results["granger_tri_W"] = W_tri
results["granger_tri_p"] = p_tri

# Note: The primary analysis reports W=13.33 for trivariate. In TY with
# 2 exogenous variables, the test restricts only DE lags (not DEMO lags).
# Let me also test with just DE lags restricted in the presence of DEMO:
data3 = np.column_stack([ind_emp, de, demo])
total_lags_3 = 3  # p=2 + d_max=1
Y3, X3 = build_var_regressors(data3, total_lags_3)
y3 = Y3[:, 0]
ols3_u = sm.OLS(y3, X3).fit()

# Restrict only DE (var index 1) lags 1..2
drop_de_only = []
k3 = 3
for j in range(1, 3):  # lags 1,2
    col_idx = 1 + (j - 1) * k3 + 1  # var index 1 = DE
    drop_de_only.append(col_idx)
keep3 = [i for i in range(X3.shape[1]) if i not in drop_de_only]
X3_r = X3[:, keep3]
ols3_r = sm.OLS(y3, X3_r).fit()
n3 = len(y3)
q3 = 2
W_de_only = n3 * (ols3_r.ssr - ols3_u.ssr) / ols3_r.ssr
p_de_only = 1 - scipy_stats.chi2.cdf(W_de_only, q3)
log.info(f"Trivariate DE-only restriction: W={W_de_only:.2f}, p={p_de_only:.4f}")
results["granger_tri_de_only_W"] = W_de_only
results["granger_tri_de_only_p"] = p_de_only

# ============================================================
# 2. ARDL(1,1) LONG-RUN COEFFICIENT (bivariate)
# ============================================================
log.info("=" * 60)
log.info("2. ARDL(1,1) Long-Run Coefficient")

# y_t = phi * y_{t-1} + theta0 * x_t + theta1 * x_{t-1} + mu + e_t
Y_ardl = ind_emp[1:]
X_ardl = np.column_stack([
    ind_emp[:-1],   # y_{t-1}
    de[1:],         # x_t
    de[:-1],        # x_{t-1}
    np.ones(T - 1)  # constant
])

ols_ardl = sm.OLS(Y_ardl, X_ardl).fit()
phi = ols_ardl.params[0]
theta0 = ols_ardl.params[1]
theta1 = ols_ardl.params[2]
mu = ols_ardl.params[3]

beta_LR = (theta0 + theta1) / (1 - phi)
log.info(f"phi={phi:.4f}, theta0={theta0:.2f}, theta1={theta1:.2f}, mu={mu:.2f}")
log.info(f"Long-run coefficient: beta_LR = {beta_LR:.2f}")

# Delta method SE
cov = ols_ardl.cov_params()
grad = np.array([
    (theta0 + theta1) / (1 - phi)**2,
    1.0 / (1 - phi),
    1.0 / (1 - phi),
    0.0
])
se_LR = np.sqrt(grad @ cov @ grad)
log.info(f"SE (delta method): {se_LR:.2f}")
log.info(f"95% CI: [{beta_LR - 1.96*se_LR:.2f}, {beta_LR + 1.96*se_LR:.2f}]")

results["ardl_phi"] = phi
results["ardl_theta0"] = theta0
results["ardl_theta1"] = theta1
results["ardl_beta_LR"] = beta_LR
results["ardl_se_LR"] = se_LR

# ============================================================
# 3. JOHANSEN COINTEGRATION TEST
# ============================================================
log.info("=" * 60)
log.info("3. Johansen Cointegration Test")

data_coint = np.column_stack([de, ind_emp])
joh = coint_johansen(data_coint, det_order=0, k_ar_diff=1)
log.info(f"Trace stats: {joh.lr1}")
log.info(f"CV 95%: {joh.cvt[:, 1]}")
log.info(f"Trace r=0: {joh.lr1[0]:.2f} vs cv95: {joh.cvt[0, 1]:.2f}")
results["johansen_trace_r0"] = float(joh.lr1[0])
results["johansen_cv95_r0"] = float(joh.cvt[0, 1])

# ============================================================
# 4. STRUCTURAL BREAK COUNTERFACTUAL
# ============================================================
log.info("=" * 60)
log.info("4. Structural Break Counterfactual")

pre_mask = years <= 2012
post_mask = years >= 2016
pre_years = years[pre_mask]
post_years = years[post_mask]

# Industry employment
X_pre = sm.add_constant(pre_years)
trend_ind = sm.OLS(ind_emp[pre_mask], X_pre).fit()
cf_ind = trend_ind.params[0] + trend_ind.params[1] * post_years
dev_ind = ind_emp[post_mask] - cf_ind
mean_dev_ind = np.mean(dev_ind)
se_dev_ind = np.std(dev_ind, ddof=1) / np.sqrt(len(dev_ind))
log.info(f"Industry pre-trend slope: {trend_ind.params[1]:.4f}/yr, R2={trend_ind.rsquared:.4f}")
log.info(f"Industry post-2016 deviation: {mean_dev_ind:.2f} pp (SE={se_dev_ind:.2f})")
results["cf_dev_ind"] = mean_dev_ind
results["cf_slope_ind"] = trend_ind.params[1]
results["cf_r2_ind"] = trend_ind.rsquared

# Services employment
trend_svc = sm.OLS(svc_emp[pre_mask], X_pre).fit()
cf_svc = trend_svc.params[0] + trend_svc.params[1] * post_years
dev_svc = svc_emp[post_mask] - cf_svc
mean_dev_svc = np.mean(dev_svc)
log.info(f"Services pre-trend slope: {trend_svc.params[1]:.4f}/yr, R2={trend_svc.rsquared:.4f}")
log.info(f"Services post-2016 deviation: {mean_dev_svc:.2f} pp")
results["cf_dev_svc"] = mean_dev_svc

# Services VA
trend_va = sm.OLS(svc_va[pre_mask], X_pre).fit()
cf_va = trend_va.params[0] + trend_va.params[1] * post_years
dev_va = svc_va[post_mask] - cf_va
mean_dev_va = np.mean(dev_va)
log.info(f"Services VA pre-trend slope: {trend_va.params[1]:.4f}/yr")
log.info(f"Services VA post-2016 deviation: {mean_dev_va:.2f} pp")
results["cf_dev_va"] = mean_dev_va

# ============================================================
# 5. ARDL BOUNDS TEST
# ============================================================
log.info("=" * 60)
log.info("5. ARDL Bounds Test")

dy = np.diff(ind_emp)
dx = np.diff(de)
y_lag = ind_emp[:-1]
x_lag = de[:-1]

# ECM: dy_t = c + pi_y*y_{t-1} + pi_x*x_{t-1} + gamma*dx_t + e
# Using observations from t=1..T-1 (dy has T-1 obs, first usable is index 1)
Y_ecm = dy[1:]
X_ecm_u = np.column_stack([y_lag[1:], x_lag[1:], dx[1:], np.ones(len(dy)-1)])
X_ecm_r = np.column_stack([dx[1:], np.ones(len(dy)-1)])

ecm_u = sm.OLS(Y_ecm, X_ecm_u).fit()
ecm_r = sm.OLS(Y_ecm, X_ecm_r).fit()

n_ecm = len(Y_ecm)
q_ecm = 2
k_ecm = X_ecm_u.shape[1]
F_bounds = ((ecm_r.ssr - ecm_u.ssr) / q_ecm) / (ecm_u.ssr / (n_ecm - k_ecm))
log.info(f"ARDL bounds F = {F_bounds:.2f}")
results["ardl_bounds_F"] = F_bounds

# ============================================================
# 6. ILO ENDOGENEITY CHECK (partial correlation reversal)
# ============================================================
log.info("=" * 60)
log.info("6. ILO Endogeneity Check")

# Level correlation
r_level = np.corrcoef(de, svc_emp)[0, 1]
log.info(f"Level correlation DE vs services emp: r={r_level:.3f}")

# Residual correlation (after removing common trend = year)
X_year = sm.add_constant(years.astype(float))
res_de = sm.OLS(de, X_year).fit().resid
res_svc = sm.OLS(svc_emp, X_year).fit().resid
r_resid = np.corrcoef(res_de, res_svc)[0, 1]
log.info(f"Residual correlation (detrended): r={r_resid:.3f}")
results["r_level_de_svc"] = r_level
results["r_resid_de_svc"] = r_resid

# Also check R-squared for ILO endogeneity concern
# The primary analysis mentions R2=0.989
X_endo = sm.add_constant(np.column_stack([
    df["gdp_per_capita_usd"].values,
    df["urban_population_pct"].values
]))
endo_model = sm.OLS(svc_emp, X_endo).fit()
log.info(f"Services emp ~ GDP + Urban: R2={endo_model.rsquared:.4f}")
results["ilo_endogeneity_r2"] = endo_model.rsquared

# ============================================================
# SUMMARY COMPARISON
# ============================================================
log.info("=" * 70)
log.info("COMPARISON: Verification vs Primary Analysis")
log.info("=" * 70)

comparisons = [
    ("Granger W (bivariate)", 5.84, results["granger_biv_W"]),
    ("Granger W (tri, DE-only)", 13.33, results["granger_tri_de_only_W"]),
    ("ARDL LR coeff (biv)", 7.15, results["ardl_beta_LR"]),
    ("ARDL LR SE", 4.10, results["ardl_se_LR"]),
    ("Johansen trace (r=0)", 19.04, results["johansen_trace_r0"]),
    ("CF deviation (ind)", -4.45, results["cf_dev_ind"]),
    ("CF deviation (svc)", 1.83, results["cf_dev_svc"]),
    ("ARDL bounds F", 6.51, results["ardl_bounds_F"]),
    ("ILO endogeneity R2", 0.989, results["ilo_endogeneity_r2"]),
    ("Level corr DE-svc", 0.981, results["r_level_de_svc"]),
]

log.info(f"{'Metric':<30} {'Primary':>10} {'Verified':>10} {'Diff%':>10} {'Status':>10}")
log.info("-" * 72)
for name, primary, verified in comparisons:
    if abs(primary) > 0.001:
        diff_pct = abs(verified - primary) / abs(primary) * 100
    else:
        diff_pct = 0.0
    status = "PASS" if diff_pct < 5.0 else ("CLOSE" if diff_pct < 15.0 else "DIVERGE")
    log.info(f"{name:<30} {primary:>10.3f} {verified:>10.3f} {diff_pct:>9.1f}% {status:>10}")

with open(OUT / "scripts" / "reproduction_results.json", "w") as f:
    json.dump({k: float(v) for k, v in results.items()}, f, indent=2)
log.info(f"\nResults saved to reproduction_results.json")
