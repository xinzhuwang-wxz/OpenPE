"""
Step 3.7: Uncertainty Quantification.

Bootstrap confidence intervals for all key estimates.
Sensitivity analysis across model specs.
Final EP assessment table.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.api import VAR
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

np.random.seed(42)

# -----------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------
df = pd.read_parquet("data/processed/analysis_ready.parquet")
df = df.sort_values("year").reset_index(drop=True)

dep_ind = df["employment_industry_pct"].values
dep_svc = df["employment_services_pct"].values
de_idx = df["digital_economy_index"].values
demo = df["population_15_64_pct"].values
sva = df["services_value_added_pct_gdp"].values
years = df["year"].values

results = {}

# -----------------------------------------------------------------------
# 1. Bootstrap CIs for First-Difference Regressions
# -----------------------------------------------------------------------
log.info("=== Bootstrap CIs ===")

d_de = np.diff(de_idx)
d_emp_ind = np.diff(dep_ind)
d_emp_svc = np.diff(dep_svc)
d_demo = np.diff(demo)
d_sva = np.diff(sva)
years_fd = years[1:]
post = (years_fd >= 2016).astype(float)
T_fd = len(d_de)

n_boot = 2000

def bootstrap_did(d_y, d_x, post_indicator, d_control=None, n_boot=2000):
    """Bootstrap DID-style regression in first differences."""
    if d_control is not None:
        X = add_constant(np.column_stack([d_x, post_indicator * d_x,
                                           d_control, post_indicator * d_control]))
    else:
        X = add_constant(np.column_stack([d_x, post_indicator * d_x]))

    # Point estimate
    m = OLS(d_y, X).fit()
    point = m.params.copy()
    se_ols = m.bse.copy()

    # Block bootstrap (block size = 3 for annual data)
    block_size = 3
    n = len(d_y)
    n_blocks = n // block_size + 1

    boot_params = []
    for _ in range(n_boot):
        # Block bootstrap
        block_starts = np.random.choice(n - block_size + 1, size=n_blocks, replace=True)
        idx = []
        for bs in block_starts:
            idx.extend(range(bs, min(bs + block_size, n)))
        idx = np.array(idx[:n])
        try:
            m_b = OLS(d_y[idx], X[idx]).fit()
            boot_params.append(m_b.params)
        except Exception:
            pass

    boot_params = np.array(boot_params)
    boot_se = np.std(boot_params, axis=0)
    ci_lo = np.percentile(boot_params, 2.5, axis=0)
    ci_hi = np.percentile(boot_params, 97.5, axis=0)
    ci68_lo = np.percentile(boot_params, 16, axis=0)
    ci68_hi = np.percentile(boot_params, 84, axis=0)

    return {
        "point": point.tolist(),
        "se_ols": se_ols.tolist(),
        "se_boot": boot_se.tolist(),
        "ci95": [ci_lo.tolist(), ci_hi.tolist()],
        "ci68": [ci68_lo.tolist(), ci68_hi.tolist()],
        "n_boot_valid": len(boot_params),
    }

# Substitution channel
boot_sub = bootstrap_did(d_emp_ind, d_de, post, n_boot=n_boot)
boot_sub_ctrl = bootstrap_did(d_emp_ind, d_de, post, d_control=d_demo, n_boot=n_boot)
boot_cre = bootstrap_did(d_emp_svc, d_de, post, n_boot=n_boot)
boot_cre_ctrl = bootstrap_did(d_emp_svc, d_de, post, d_control=d_demo, n_boot=n_boot)
boot_med = bootstrap_did(d_sva, d_de, post, n_boot=n_boot)

results["bootstrap"] = {
    "substitution": boot_sub,
    "substitution_ctrl": boot_sub_ctrl,
    "creation": boot_cre,
    "creation_ctrl": boot_cre_ctrl,
    "mediation": boot_med,
}

# -----------------------------------------------------------------------
# 2. Bootstrap CIs for Granger Causality W-stats
# -----------------------------------------------------------------------
log.info("=== Bootstrap Granger W-stats ===")

def bootstrap_granger_w(cause_col, effect_col, df_in, p=2, d_max=1, n_boot=1000):
    """Bootstrap the Toda-Yamamoto Granger W statistic."""
    cols = [cause_col, effect_col]
    data_df = df_in[cols].dropna()
    data = data_df.values
    T = len(data)
    total_lag = p + d_max

    # Original VAR with named columns
    model = VAR(data_df)
    fit = model.fit(maxlags=total_lag)
    gc = fit.test_causality(caused=effect_col, causing=cause_col, kind="wald")
    W_orig = float(gc.test_statistic)

    # Residual bootstrap
    resid = fit.resid.values if hasattr(fit.resid, 'values') else fit.resid
    fitted_vals = data[total_lag:] - resid
    W_boots = []

    for _ in range(n_boot):
        idx = np.random.choice(len(resid), size=len(resid), replace=True)
        resid_boot = resid[idx]
        data_boot_trimmed = fitted_vals + resid_boot

        # Reconstruct full series with original pre-sample
        data_boot = np.vstack([data[:total_lag], data_boot_trimmed])
        data_boot_df = pd.DataFrame(data_boot, columns=cols)
        try:
            m_b = VAR(data_boot_df)
            f_b = m_b.fit(maxlags=total_lag)
            gc_b = f_b.test_causality(caused=effect_col, causing=cause_col, kind="wald")
            W_boots.append(float(gc_b.test_statistic))
        except Exception:
            pass

    W_boots = np.array(W_boots)
    return {
        "W_original": W_orig,
        "W_boot_mean": float(np.mean(W_boots)),
        "W_boot_se": float(np.std(W_boots)),
        "W_boot_ci95": [float(np.percentile(W_boots, 2.5)),
                         float(np.percentile(W_boots, 97.5))],
        "p_boot": float(np.mean(W_boots >= W_orig)),
        "n_boot_valid": len(W_boots),
    }

boot_granger_sub = bootstrap_granger_w(
    "digital_economy_index", "employment_industry_pct", df, n_boot=1000)
boot_granger_cre = bootstrap_granger_w(
    "digital_economy_index", "employment_services_pct", df, n_boot=1000)

results["bootstrap_granger"] = {
    "substitution": boot_granger_sub,
    "creation": boot_granger_cre,
}

# -----------------------------------------------------------------------
# 3. Systematic Uncertainty Decomposition
# -----------------------------------------------------------------------
log.info("=== Systematic Uncertainty Decomposition ===")

# For the substitution channel (primary result)
# Base estimate
X_base = add_constant(np.column_stack([d_de, post * d_de]))
m_base = OLS(d_emp_ind, X_base).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
base_estimate = m_base.params[1]  # d_DE coefficient

systematics = {}

# 3a. Lag selection: use d_de with lag
d_de_lag1 = d_de[:-1]
d_y_trim = d_emp_ind[1:]
post_trim = post[1:]
X_lag = add_constant(np.column_stack([d_de_lag1, d_de[1:], post_trim * d_de[1:]]))
m_lag = OLS(d_y_trim, X_lag).fit()
systematics["lag_selection"] = {
    "base": float(base_estimate),
    "varied": float(m_lag.params[2]),  # contemporaneous d_DE
    "shift": float(m_lag.params[2] - base_estimate),
}

# 3b. Break year sensitivity
shifts_break = []
for by in [2013, 2014, 2015, 2016, 2017]:
    post_by = (years_fd >= by).astype(float)
    X_by = add_constant(np.column_stack([d_de, post_by * d_de]))
    m_by = OLS(d_emp_ind, X_by).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    shifts_break.append(float(m_by.params[1]))
systematics["break_year"] = {
    "base": float(base_estimate),
    "range": [float(min(shifts_break)), float(max(shifts_break))],
    "shift": float(max(shifts_break) - min(shifts_break)),
}

# 3c. Demographic control
X_ctrl = add_constant(np.column_stack([d_de, post * d_de, d_demo, post * d_demo]))
m_ctrl = OLS(d_emp_ind, X_ctrl).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
systematics["demographic_control"] = {
    "base": float(base_estimate),
    "varied": float(m_ctrl.params[1]),
    "shift": float(m_ctrl.params[1] - base_estimate),
}

# 3d. Functional form (quadratic DE)
d_de_sq = d_de**2
X_quad = add_constant(np.column_stack([d_de, d_de_sq, post * d_de]))
m_quad = OLS(d_emp_ind, X_quad).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
systematics["functional_form"] = {
    "base": float(base_estimate),
    "varied": float(m_quad.params[1]),
    "shift": float(m_quad.params[1] - base_estimate),
}

# 3e. Sample period (exclude COVID years 2020-2021)
mask_no_covid = ~np.isin(years_fd, [2020, 2021])
X_nc = X_base[mask_no_covid]
y_nc = d_emp_ind[mask_no_covid]
m_nc = OLS(y_nc, X_nc).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
systematics["covid_exclusion"] = {
    "base": float(base_estimate),
    "varied": float(m_nc.params[1]),
    "shift": float(m_nc.params[1] - base_estimate),
}

# 3f. ILO endogeneity proxy
# Use services VA as alternative outcome (less affected by ILO modeling)
d_sva_out = np.diff(sva)
X_sva = add_constant(np.column_stack([d_de, post * d_de]))
m_sva = OLS(d_sva_out, X_sva).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
systematics["ilo_endogeneity"] = {
    "note": "Alternative outcome: services VA instead of employment",
    "base_employment": float(base_estimate),
    "alternative_va": float(m_sva.params[1]),
    "shift_interpretation": "Not directly comparable -- different units and scale",
}

# Compute total systematic
shifts = []
for k, v in systematics.items():
    if k == "ilo_endogeneity":
        continue
    if "shift" in v and isinstance(v["shift"], (int, float)):
        shifts.append(abs(v["shift"]))

total_syst = np.sqrt(sum(s**2 for s in shifts))
stat_unc = float(boot_sub["se_boot"][1])  # bootstrap SE for d_DE coeff

results["systematics"] = systematics
results["uncertainty_summary"] = {
    "parameter": "d_DE coefficient (substitution, first-diff)",
    "central_value": float(base_estimate),
    "stat_unc_68": stat_unc,
    "stat_unc_95": 1.96 * stat_unc,
    "syst_unc": total_syst,
    "total_unc_68": float(np.sqrt(stat_unc**2 + total_syst**2)),
    "total_unc_95": float(1.96 * np.sqrt(stat_unc**2 + total_syst**2)),
    "dominant_source": "statistical" if stat_unc > total_syst else "systematic",
    "systematic_breakdown": {k: abs(v.get("shift", 0)) if isinstance(v.get("shift", 0), (int, float)) else 0.0
                             for k, v in systematics.items()},
}

# -----------------------------------------------------------------------
# 4. Creation Channel Uncertainty
# -----------------------------------------------------------------------
log.info("=== Creation Channel Uncertainty ===")

X_cre_base = add_constant(np.column_stack([d_de, post * d_de]))
m_cre_base = OLS(d_emp_svc, X_cre_base).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
cre_estimate = m_cre_base.params[1]
cre_stat = float(boot_cre["se_boot"][1])

# Quick systematic for creation
cre_shifts = []
for by in [2013, 2014, 2015, 2016, 2017]:
    post_by = (years_fd >= by).astype(float)
    X_by_c = add_constant(np.column_stack([d_de, post_by * d_de]))
    m_by_c = OLS(d_emp_svc, X_by_c).fit()
    cre_shifts.append(float(m_by_c.params[1]))
cre_syst = (max(cre_shifts) - min(cre_shifts)) / 2.0

results["creation_uncertainty"] = {
    "central_value": float(cre_estimate),
    "stat_unc_68": cre_stat,
    "syst_unc": cre_syst,
    "total_unc_68": float(np.sqrt(cre_stat**2 + cre_syst**2)),
    "significant": bool(abs(cre_estimate) > 1.96 * np.sqrt(cre_stat**2 + cre_syst**2)),
}

# -----------------------------------------------------------------------
# 5. Mediation First-Link Uncertainty
# -----------------------------------------------------------------------
log.info("=== Mediation First-Link Uncertainty ===")

X_med_base = add_constant(np.column_stack([d_de, post * d_de]))
m_med_base = OLS(d_sva, X_med_base).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
med_estimate = m_med_base.params[1]
med_stat = float(boot_med["se_boot"][1])

results["mediation_uncertainty"] = {
    "central_value": float(med_estimate),
    "stat_unc_68": med_stat,
    "total_unc_68": med_stat,  # simplified
    "significant": bool(abs(med_estimate) > 1.96 * med_stat),
}

# -----------------------------------------------------------------------
# 6. Final Results Table
# -----------------------------------------------------------------------
log.info("=== Compiling Final Results ===")

# Load previous results
with open("phase3_analysis/scripts/granger_results.json") as f:
    granger = json.load(f)

final_results = []

# Substitution
sub_stat = float(boot_sub["se_boot"][1])
sub_syst = total_syst
sub_total = float(np.sqrt(sub_stat**2 + sub_syst**2))
final_results.append({
    "parameter": "DE -> Industry Emp (substitution)",
    "method": "First-diff DID-inspired",
    "central": float(base_estimate),
    "stat_unc": sub_stat,
    "syst_unc": sub_syst,
    "total_unc": sub_total,
    "classification": "CORRELATION",
    "ep": 0.315,
})

# Substitution Granger
for g in granger:
    if g["label"] == "substitution" and g["spec"] == "bivariate":
        final_results.append({
            "parameter": "DE -> Industry Emp (Granger W)",
            "method": "Toda-Yamamoto",
            "central": g["W_stat"],
            "stat_unc": float(boot_granger_sub["W_boot_se"]),
            "syst_unc": 0.0,  # not applicable for test statistic
            "total_unc": float(boot_granger_sub["W_boot_se"]),
            "classification": "CORRELATION",
            "ep": 0.315,
            "p_boot": g["p_bootstrap"],
        })

# Creation
cre_total = float(np.sqrt(cre_stat**2 + cre_syst**2))
final_results.append({
    "parameter": "DE -> Services Emp (creation)",
    "method": "First-diff DID-inspired",
    "central": float(cre_estimate),
    "stat_unc": cre_stat,
    "syst_unc": cre_syst,
    "total_unc": cre_total,
    "classification": "HYPOTHESIZED",
    "ep": 0.120,
})

# Mediation
final_results.append({
    "parameter": "DE -> Services VA (mediation link 1)",
    "method": "First-diff DID-inspired",
    "central": float(med_estimate),
    "stat_unc": med_stat,
    "syst_unc": 0.0,
    "total_unc": med_stat,
    "classification": "HYPOTHESIZED",
    "ep": 0.090,
})

# ARDL long-run
with open("phase3_analysis/scripts/statistical_model_results.json") as f:
    model_results = json.load(f)

ardl_lr = model_results["ardl_substitution"]["bivariate"]
final_results.append({
    "parameter": "DE -> Industry Emp (ARDL long-run)",
    "method": "ARDL bounds",
    "central": ardl_lr["lr_coeff"],
    "stat_unc": ardl_lr["lr_se"],
    "syst_unc": 0.0,
    "total_unc": ardl_lr["lr_se"],
    "classification": "CORRELATION",
    "ep": 0.315,
})

# Counterfactual trend deviations
with open("phase3_analysis/scripts/structural_break_results.json") as f:
    sb_results = json.load(f)

for cf in sb_results["counterfactual"]:
    if cf["variable"] in ["employment_industry_pct", "employment_services_pct"]:
        final_results.append({
            "parameter": f"Post-break deviation: {cf['variable']}",
            "method": "Counterfactual trend",
            "central": cf["mean_deviation"],
            "stat_unc": cf["se_deviation"],
            "syst_unc": 0.0,
            "total_unc": cf["se_deviation"],
            "classification": "DESCRIPTIVE",
            "ep": None,
            "t_stat": cf["t_stat"],
            "p_value": cf["p_value"],
        })

results["final_results"] = final_results

# -----------------------------------------------------------------------
# Save
# -----------------------------------------------------------------------
out_path = "phase3_analysis/scripts/uncertainty_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
log.info(f"Results saved to {out_path}")
