"""Step 2.3: Stationarity tests (ADF + KPSS) for all key variables."""

import logging
import json
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from rich.logging import RichHandler
from statsmodels.tsa.stattools import adfuller, kpss

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

DATA_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/processed")
OUT_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/scripts")

df = pd.read_parquet(DATA_DIR / "analysis_ready.parquet")

key_vars = [
    "digital_economy_index",
    "employment_services_pct",
    "employment_industry_pct",
    "employment_agriculture_pct",
    "services_value_added_pct_gdp",
    "population_15_64_pct",
    "population_65plus_pct",
    "urban_population_pct",
    "log_gdp_pc",
    "internet_users_pct",
    "mobile_subscriptions_per100",
    "fixed_broadband_per100",
]

results = []

for var in key_vars:
    if var not in df.columns:
        log.info(f"SKIP: {var} not in dataset")
        continue
    
    series = df[var].dropna()
    if len(series) < 10:
        log.info(f"SKIP: {var} too few observations ({len(series)})")
        continue
    
    # === LEVELS ===
    try:
        adf_stat, adf_p, adf_lags, adf_nobs, adf_cv, adf_ic = adfuller(series, autolag="AIC")
    except Exception as e:
        log.info(f"ADF failed for {var}: {e}")
        adf_stat, adf_p, adf_lags = np.nan, np.nan, np.nan
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kpss_stat, kpss_p, kpss_lags, kpss_cv = kpss(series, regression="ct", nlags="auto")
    except Exception as e:
        log.info(f"KPSS failed for {var}: {e}")
        kpss_stat, kpss_p, kpss_lags = np.nan, np.nan, np.nan
    
    # === FIRST DIFFERENCES ===
    d_series = series.diff().dropna()
    try:
        d_adf_stat, d_adf_p, d_adf_lags, _, _, _ = adfuller(d_series, autolag="AIC")
    except Exception:
        d_adf_stat, d_adf_p = np.nan, np.nan
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d_kpss_stat, d_kpss_p, _, _ = kpss(d_series, regression="c", nlags="auto")
    except Exception:
        d_kpss_stat, d_kpss_p = np.nan, np.nan
    
    # Joint classification
    level_stationary_adf = adf_p < 0.05 if not np.isnan(adf_p) else None
    level_stationary_kpss = kpss_p > 0.05 if not np.isnan(kpss_p) else None
    
    diff_stationary_adf = d_adf_p < 0.05 if not np.isnan(d_adf_p) else None
    diff_stationary_kpss = d_kpss_p > 0.05 if not np.isnan(d_kpss_p) else None
    
    if level_stationary_adf and level_stationary_kpss:
        level_verdict = "I(0) - Stationary"
    elif (not level_stationary_adf) and (not level_stationary_kpss):
        level_verdict = "Non-stationary (both agree)"
    else:
        level_verdict = "Ambiguous (ADF/KPSS disagree)"
    
    if diff_stationary_adf and diff_stationary_kpss:
        diff_verdict = "I(1) confirmed"
    elif diff_stationary_adf or diff_stationary_kpss:
        diff_verdict = "Likely I(1)"
    else:
        diff_verdict = "Possibly I(2) or ambiguous"
    
    if "I(0)" in level_verdict:
        integration_order = 0
    elif "I(1) confirmed" in diff_verdict or "Likely I(1)" in diff_verdict:
        integration_order = 1
    else:
        integration_order = "ambiguous"
    
    row = {
        "variable": var,
        "adf_stat_level": round(float(adf_stat), 3) if not np.isnan(adf_stat) else None,
        "adf_p_level": round(float(adf_p), 4) if not np.isnan(adf_p) else None,
        "kpss_stat_level": round(float(kpss_stat), 3) if not np.isnan(kpss_stat) else None,
        "kpss_p_level": round(float(kpss_p), 4) if not np.isnan(kpss_p) else None,
        "level_verdict": level_verdict,
        "adf_p_diff": round(float(d_adf_p), 4) if not np.isnan(d_adf_p) else None,
        "kpss_p_diff": round(float(d_kpss_p), 4) if not np.isnan(d_kpss_p) else None,
        "diff_verdict": diff_verdict,
        "integration_order": integration_order,
    }
    results.append(row)
    log.info(f"{var}: levels={level_verdict}, diff={diff_verdict}, I({integration_order})")

results_df = pd.DataFrame(results)
log.info(f"\n=== STATIONARITY SUMMARY ===\n{results_df.to_string()}")

results_df.to_csv(OUT_DIR / "stationarity_results.csv", index=False)
with open(OUT_DIR / "stationarity_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
log.info("Stationarity results saved.")
