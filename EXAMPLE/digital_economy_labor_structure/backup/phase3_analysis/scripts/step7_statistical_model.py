"""
Step 3.6: Statistical Model Fitting.

Fits final VECM/ARDL models with selected specifications, produces
coefficient tables with confidence intervals, runs signal injection tests,
and sensitivity analysis on model specifications.
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import VECM, coint_johansen
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
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
log.info(f"Loaded data: {df.shape[0]} obs, {df.shape[1]} cols")

results = {}

# -----------------------------------------------------------------------
# 1. VECM for Substitution Channel (DE, industry_emp, demo)
# -----------------------------------------------------------------------
log.info("=== VECM: Substitution Channel ===")

# Bivariate VECM
y_sub = df[["digital_economy_index", "employment_industry_pct"]].dropna()
vecm_sub = VECM(y_sub.values, k_ar_diff=1, coint_rank=1, deterministic="ci")
vecm_sub_fit = vecm_sub.fit()

# Extract coefficients and standard errors
alpha_sub = vecm_sub_fit.alpha
beta_sub = vecm_sub_fit.beta
gamma_sub = vecm_sub_fit.gamma  # short-run coefficients

# Residual diagnostics
resid_sub = vecm_sub_fit.resid
log.info(f"VECM substitution alpha: {alpha_sub.flatten()}")
log.info(f"VECM substitution beta: {beta_sub.flatten()}")

# Trivariate VECM with demographic control
y_sub_ctrl = df[["digital_economy_index", "employment_industry_pct",
                  "population_15_64_pct"]].dropna()
vecm_sub_ctrl = VECM(y_sub_ctrl.values, k_ar_diff=1, coint_rank=2,
                      deterministic="ci")
vecm_sub_ctrl_fit = vecm_sub_ctrl.fit()

results["vecm_substitution"] = {
    "bivariate": {
        "alpha": alpha_sub.tolist(),
        "beta": beta_sub.tolist(),
        "gamma": vecm_sub_fit.gamma.tolist() if vecm_sub_fit.gamma is not None else None,
        "sigma_u": vecm_sub_fit.sigma_u.tolist(),
        "llf": float(vecm_sub_fit.llf) if hasattr(vecm_sub_fit, "llf") else None,
        "nobs": int(y_sub.shape[0] - 2),
    },
    "trivariate": {
        "alpha": vecm_sub_ctrl_fit.alpha.tolist(),
        "beta": vecm_sub_ctrl_fit.beta.tolist(),
        "sigma_u": vecm_sub_ctrl_fit.sigma_u.tolist(),
        "llf": float(vecm_sub_ctrl_fit.llf) if hasattr(vecm_sub_ctrl_fit, "llf") else None,
        "nobs": int(y_sub_ctrl.shape[0] - 2),
    },
}

# -----------------------------------------------------------------------
# 2. ARDL for Substitution Channel
# -----------------------------------------------------------------------
log.info("=== ARDL: Substitution Channel ===")

# Manual ARDL(1,1) implementation
dep = df["employment_industry_pct"].values
indep = df["digital_economy_index"].values
demo = df["population_15_64_pct"].values
T = len(dep)

# Construct ARDL variables (lag 1)
y_t = dep[1:]
y_lag = dep[:-1]
x_t = indep[1:]
x_lag = indep[:-1]
d_t = demo[1:]
d_lag = demo[:-1]

# ARDL(1,1) without demo
X_ardl = np.column_stack([y_lag, x_t, x_lag, np.ones(len(y_t))])
ardl_model = OLS(y_t, X_ardl).fit(cov_type="HC1")

# Long-run coefficient: sum of x coefficients / (1 - coeff on y_lag)
lr_coeff = (ardl_model.params[1] + ardl_model.params[2]) / (1 - ardl_model.params[0])

# Delta method SE for long-run coefficient
b0, b1, b2 = ardl_model.params[0], ardl_model.params[1], ardl_model.params[2]
denom = (1 - b0)
# Partial derivatives for delta method
g = np.array([
    (b1 + b2) / denom**2,  # d/d(b0)
    1.0 / denom,            # d/d(b1)
    1.0 / denom,            # d/d(b2)
    0.0,                     # d/d(const)
])
lr_se = np.sqrt(g @ ardl_model.cov_params() @ g)

log.info(f"ARDL substitution LR coeff: {lr_coeff:.4f} (SE={lr_se:.4f})")

# ARDL(1,1,1) with demo control
X_ardl_ctrl = np.column_stack([y_lag, x_t, x_lag, d_t, d_lag, np.ones(len(y_t))])
ardl_ctrl = OLS(y_t, X_ardl_ctrl).fit(cov_type="HC1")

lr_coeff_ctrl = (ardl_ctrl.params[1] + ardl_ctrl.params[2]) / (1 - ardl_ctrl.params[0])
lr_demo = (ardl_ctrl.params[3] + ardl_ctrl.params[4]) / (1 - ardl_ctrl.params[0])

# Delta method for controlled model
b0c = ardl_ctrl.params[0]
denom_c = (1 - b0c)
g_ctrl = np.zeros(6)
g_ctrl[0] = (ardl_ctrl.params[1] + ardl_ctrl.params[2]) / denom_c**2
g_ctrl[1] = 1.0 / denom_c
g_ctrl[2] = 1.0 / denom_c
lr_se_ctrl = np.sqrt(g_ctrl @ ardl_ctrl.cov_params() @ g_ctrl)

results["ardl_substitution"] = {
    "bivariate": {
        "params": ardl_model.params.tolist(),
        "bse": ardl_model.bse.tolist(),
        "pvalues": ardl_model.pvalues.tolist(),
        "rsquared": float(ardl_model.rsquared),
        "lr_coeff": float(lr_coeff),
        "lr_se": float(lr_se),
        "lr_ci95": [float(lr_coeff - 1.96 * lr_se), float(lr_coeff + 1.96 * lr_se)],
        "nobs": int(ardl_model.nobs),
    },
    "with_demo": {
        "params": ardl_ctrl.params.tolist(),
        "bse": ardl_ctrl.bse.tolist(),
        "pvalues": ardl_ctrl.pvalues.tolist(),
        "rsquared": float(ardl_ctrl.rsquared),
        "lr_coeff_de": float(lr_coeff_ctrl),
        "lr_se_de": float(lr_se_ctrl),
        "lr_ci95_de": [float(lr_coeff_ctrl - 1.96 * lr_se_ctrl),
                       float(lr_coeff_ctrl + 1.96 * lr_se_ctrl)],
        "lr_coeff_demo": float(lr_demo),
        "nobs": int(ardl_ctrl.nobs),
    },
}

# -----------------------------------------------------------------------
# 3. First-Difference OLS for both channels (DID-inspired)
# -----------------------------------------------------------------------
log.info("=== First-Difference OLS (DID-inspired) ===")

d_de = np.diff(indep)
d_emp_svc = np.diff(df["employment_services_pct"].values)
d_emp_ind = np.diff(dep)
d_demo = np.diff(demo)
d_sva = np.diff(df["services_value_added_pct_gdp"].values)
years_fd = df["year"].values[1:]

# Break indicator: POST = year >= 2016 (allowing for implementation lag)
post = (years_fd >= 2016).astype(float)

# Substitution: d(ind_emp) ~ d(DE) + POST*d(DE)
X_did_sub = add_constant(np.column_stack([d_de, post * d_de]))
did_sub = OLS(d_emp_ind, X_did_sub).fit(cov_type="HAC", cov_kwds={"maxlags": 2})

# Substitution with demo: d(ind_emp) ~ d(DE) + POST*d(DE) + d(demo) + POST*d(demo)
X_did_sub_ctrl = add_constant(np.column_stack([d_de, post * d_de, d_demo, post * d_demo]))
did_sub_ctrl = OLS(d_emp_ind, X_did_sub_ctrl).fit(cov_type="HAC", cov_kwds={"maxlags": 2})

# Creation: d(svc_emp) ~ d(DE) + POST*d(DE)
X_did_cre = add_constant(np.column_stack([d_de, post * d_de]))
did_cre = OLS(d_emp_svc, X_did_cre).fit(cov_type="HAC", cov_kwds={"maxlags": 2})

# Creation with demo
X_did_cre_ctrl = add_constant(np.column_stack([d_de, post * d_de, d_demo, post * d_demo]))
did_cre_ctrl = OLS(d_emp_svc, X_did_cre_ctrl).fit(cov_type="HAC", cov_kwds={"maxlags": 2})

# Mediation: d(sva) ~ d(DE) + POST*d(DE)
X_did_med = add_constant(np.column_stack([d_de, post * d_de]))
did_med = OLS(d_sva, X_did_med).fit(cov_type="HAC", cov_kwds={"maxlags": 2})

results["did_inspired"] = {}
for name, model, var_names in [
    ("substitution", did_sub, ["const", "d_DE", "POST*d_DE"]),
    ("substitution_ctrl", did_sub_ctrl, ["const", "d_DE", "POST*d_DE", "d_DEMO", "POST*d_DEMO"]),
    ("creation", did_cre, ["const", "d_DE", "POST*d_DE"]),
    ("creation_ctrl", did_cre_ctrl, ["const", "d_DE", "POST*d_DE", "d_DEMO", "POST*d_DEMO"]),
    ("mediation", did_med, ["const", "d_DE", "POST*d_DE"]),
]:
    results["did_inspired"][name] = {
        "params": dict(zip(var_names, model.params.tolist())),
        "bse": dict(zip(var_names, model.bse.tolist())),
        "pvalues": dict(zip(var_names, model.pvalues.tolist())),
        "tvalues": dict(zip(var_names, model.tvalues.tolist())),
        "rsquared": float(model.rsquared),
        "nobs": int(model.nobs),
        "ci95": {v: [float(model.conf_int()[i, 0]), float(model.conf_int()[i, 1])]
                 for i, v in enumerate(var_names)},
    }

# -----------------------------------------------------------------------
# 4. Signal Injection Tests
# -----------------------------------------------------------------------
log.info("=== Signal Injection Tests ===")

def signal_injection_test(y_orig, x_orig, inject_size, n_boot=500):
    """Inject artificial signal into pure noise and check recovery.

    Uses residuals from regressing y on x as the baseline (noise floor),
    then injects inject_size * x to create synthetic data with known signal.
    """
    T = len(y_orig)
    d_y = np.diff(y_orig)
    d_x = np.diff(x_orig)

    # Get residuals (noise) from base regression
    X = add_constant(d_x)
    base_model = OLS(d_y, X).fit()
    residuals = base_model.resid

    # Construct synthetic y = inject_size * d_x + noise
    d_y_injected = inject_size * d_x + residuals

    # Recover via OLS
    model = OLS(d_y_injected, X).fit()
    recovered = model.params[1]
    se = model.bse[1]

    # Bootstrap CI
    boot_coefs = []
    for _ in range(n_boot):
        idx = np.random.choice(len(d_x), size=len(d_x), replace=True)
        m = OLS(d_y_injected[idx], add_constant(d_x[idx])).fit()
        boot_coefs.append(m.params[1])
    boot_se = np.std(boot_coefs)

    within_1sigma = abs(recovered - inject_size) < boot_se
    return {
        "injected": float(inject_size),
        "recovered": float(recovered),
        "se_boot": float(boot_se),
        "within_1sigma": bool(within_1sigma),
        "residual": float(recovered - inject_size),
    }

# Injection on substitution channel
y_inj = df["employment_industry_pct"].values
x_inj = df["digital_economy_index"].values

# Observed effect size from first-diff regression
obs_effect = did_sub.params[1]  # d_DE coefficient

injection_results = []
for mult, label in [(1.0, "observed"), (2.0, "2x_observed"), (0.0, "null")]:
    inject_val = obs_effect * mult
    res = signal_injection_test(y_inj, x_inj, inject_val)
    res["test_label"] = label
    injection_results.append(res)
    log.info(f"Injection [{label}]: injected={inject_val:.3f}, "
             f"recovered={res['recovered']:.3f} +/- {res['se_boot']:.3f}, "
             f"within_1sig={res['within_1sigma']}")

results["signal_injection"] = injection_results

# -----------------------------------------------------------------------
# 5. Sensitivity Analysis: Lag Order
# -----------------------------------------------------------------------
log.info("=== Sensitivity: Lag Order ===")

sensitivity_lag = []
for p in [1, 2, 3]:
    try:
        y_df = df[["digital_economy_index", "employment_industry_pct"]].dropna()
        if p + 1 >= len(y_df) - 5:
            continue
        model_var = VAR(y_df)
        fit_var = model_var.fit(maxlags=p + 1)  # p + d_max=1
        gc = fit_var.test_causality(
            caused="employment_industry_pct",
            causing="digital_economy_index",
            kind="wald")
        sensitivity_lag.append({
            "p": p,
            "W_stat": float(gc.test_statistic),
            "p_value": float(gc.pvalue),
        })
    except Exception as e:
        log.warning(f"Lag {p}: {e}")

results["sensitivity_lag"] = sensitivity_lag

# -----------------------------------------------------------------------
# 6. Sensitivity: Break Year
# -----------------------------------------------------------------------
log.info("=== Sensitivity: Break Year ===")

sensitivity_break = []
for break_year in [2013, 2014, 2015, 2016, 2017]:
    post_by = (years_fd >= break_year).astype(float)
    X_by = add_constant(np.column_stack([d_de, post_by * d_de]))
    m_by = OLS(d_emp_ind, X_by).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    sensitivity_break.append({
        "break_year": break_year,
        "beta_de": float(m_by.params[1]),
        "beta_post_de": float(m_by.params[2]),
        "se_de": float(m_by.bse[1]),
        "se_post_de": float(m_by.bse[2]),
        "p_de": float(m_by.pvalues[1]),
        "p_post_de": float(m_by.pvalues[2]),
    })

results["sensitivity_break_year"] = sensitivity_break

# -----------------------------------------------------------------------
# 7. Sensitivity: Variable Definition
# -----------------------------------------------------------------------
log.info("=== Sensitivity: Variable Definition ===")

# Test with services VA as alternative outcome
sensitivity_var = []
for outcome_name, outcome_col in [
    ("employment_industry_pct", "employment_industry_pct"),
    ("employment_services_pct", "employment_services_pct"),
    ("services_value_added_pct_gdp", "services_value_added_pct_gdp"),
]:
    d_out = np.diff(df[outcome_col].values)
    X_sv = add_constant(d_de)
    m_sv = OLS(d_out, X_sv).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    sensitivity_var.append({
        "outcome": outcome_name,
        "beta": float(m_sv.params[1]),
        "se": float(m_sv.bse[1]),
        "p": float(m_sv.pvalues[1]),
        "rsquared": float(m_sv.rsquared),
    })

results["sensitivity_variable"] = sensitivity_var

# -----------------------------------------------------------------------
# Save results
# -----------------------------------------------------------------------
out_path = "phase3_analysis/scripts/statistical_model_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
log.info(f"Results saved to {out_path}")
