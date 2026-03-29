"""
Program 1b: Independent reproduction of refutation tests.

Reproduces the placebo treatment test and COVID-date placebo test independently.
Uses numpy OLS (not statsmodels) to maintain independence.
"""
import logging
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats as spstats

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent.parent

# Load data
expenditure = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_education_expenditure.parquet")
cpi = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_cpi_deflator.parquet")

merged = expenditure.merge(cpi, on="year", how="inner")

deflator_col = [c for c in merged.columns if "deflator" in c.lower() and "edu" in c.lower()][0]
nat_col = [c for c in merged.columns if "national" in c.lower() and "yuan" in c.lower() and "education" in c.lower()][0]

merged["real_national"] = merged[nat_col] * merged[deflator_col]

# Exclude 2020
df = merged[merged["year"] != 2020].copy().sort_values("year").reset_index(drop=True)

years = df["year"].values
y = df["real_national"].values

def run_its(years_arr, y_arr, intervention_year):
    """Run ITS model with given intervention year, return level shift and stats."""
    t_min = years_arr.min()
    t = (years_arr - t_min).astype(float)
    post = (years_arr >= intervention_year).astype(float)
    X = np.column_stack([np.ones(len(t)), t, post])

    beta = np.linalg.solve(X.T @ X, X.T @ y_arr)
    residuals = y_arr - X @ beta
    n, p = len(y_arr), X.shape[1]
    sigma2 = np.sum(residuals**2) / (n - p)
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X) * sigma2))
    p_val = 2 * spstats.t.sf(np.abs(beta[2] / se[2]), df=n - p)
    return {
        "level_shift": float(beta[2]),
        "se": float(se[2]),
        "p_value": float(p_val),
    }

# --- Placebo treatment tests ---
log.info("=== Placebo Treatment Tests (National) ===")
placebo_results = {}
for placebo_year in [2017, 2018, 2019]:
    res = run_its(years, y, placebo_year)
    placebo_results[str(placebo_year)] = res
    log.info("  Placebo %d: shift=%.2f, SE=%.2f, p=%.4f",
             placebo_year, res["level_shift"], res["se"], res["p_value"])

# True estimate
true_res = run_its(years, y, 2021)
log.info("  True 2021: shift=%.2f, SE=%.2f, p=%.4f",
         true_res["level_shift"], true_res["se"], true_res["p_value"])

any_placebo_significant = any(
    placebo_results[k]["p_value"] < 0.10 for k in placebo_results
)
max_placebo_shift = max(abs(placebo_results[k]["level_shift"]) for k in placebo_results)
true_larger = abs(true_res["level_shift"]) > max_placebo_shift
placebo_pass = not any_placebo_significant and true_larger

log.info("  Any placebo significant at 10%%? %s", any_placebo_significant)
log.info("  True shift larger than all placebos? %s (|true|=%.1f vs max_placebo=%.1f)",
         true_larger, abs(true_res["level_shift"]), max_placebo_shift)
log.info("  Placebo test: %s", "PASS" if placebo_pass else "FAIL")

# --- COVID-date placebo ---
log.info("\n=== COVID-Date Placebo (National) ===")
# Include 2020 for COVID placebo
df_full = merged.copy().sort_values("year").reset_index(drop=True)
years_full = df_full["year"].values
y_full = df_full["real_national"].values

# Run ITS with intervention at 2020
covid_res = run_its(years_full, y_full, 2020)
log.info("  COVID placebo (2020): shift=%.2f, SE=%.2f, p=%.4f",
         covid_res["level_shift"], covid_res["se"], covid_res["p_value"])

covid_significant = covid_res["p_value"] < 0.05
covid_larger = abs(covid_res["level_shift"]) > abs(true_res["level_shift"])
covid_pass = not covid_significant  # FAIL means COVID break is significant

log.info("  COVID break significant? %s", covid_significant)
log.info("  COVID break larger than policy? %s (|covid|=%.1f vs |policy|=%.1f)",
         covid_larger, abs(covid_res["level_shift"]), abs(true_res["level_shift"]))
log.info("  COVID-date placebo: %s", "PASS" if covid_pass else "FAIL")

# --- Compare with primary analysis ---
primary = json.load(open(BASE / "phase3_analysis" / "data" / "refutation_results.json"))
pref = primary["national"]

log.info("\n=== Comparison with Primary Analysis ===")

# Placebo comparison
for yr in ["2017", "2018", "2019"]:
    v = placebo_results[yr]["level_shift"]
    p = pref["placebo"]["details"][yr]["level_shift"]
    diff_pct = abs(v - p) / max(abs(p), 1) * 100
    log.info("  Placebo %s: Verifier=%.2f, Primary=%.2f, Diff=%.2f%%",
             yr, v, p, diff_pct)

# COVID placebo comparison
v_covid = covid_res["level_shift"]
p_covid = pref["covid_placebo"]["shift"]
diff_pct = abs(v_covid - p_covid) / abs(p_covid) * 100
log.info("  COVID placebo: Verifier=%.2f, Primary=%.2f, Diff=%.2f%%",
         v_covid, p_covid, diff_pct)

# Primary says: 3/3 core PASS, COVID FAIL
verifier_core_pass = 3  # placebo PASS + random common cause (not reproduced, accepted) + data subset (not reproduced)
verifier_covid_fail = not covid_pass

log.info("\n  Primary: 3/3 core PASS, COVID FAIL")
log.info("  Verifier: Placebo %s, COVID %s",
         "PASS" if placebo_pass else "FAIL",
         "FAIL" if verifier_covid_fail else "PASS")
log.info("  Refutation outcome agreement: %s",
         "CONSISTENT" if (placebo_pass and verifier_covid_fail) else "INCONSISTENT")

# Save
output = {
    "placebo_results": placebo_results,
    "true_result": true_res,
    "placebo_pass": placebo_pass,
    "covid_placebo": covid_res,
    "covid_pass": covid_pass,
    "agreement_with_primary": placebo_pass and verifier_covid_fail,
}

out_path = BASE / "phase5_verification" / "data"
out_path.mkdir(parents=True, exist_ok=True)
with open(out_path / "refutation_reproduction.json", "w") as f:
    json.dump(output, f, indent=2)

log.info("Results saved.")
