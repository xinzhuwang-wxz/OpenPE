"""
Step 1: Prefiltering -- Load all datasets, CPI-deflate, verify stationarity.

Produces: phase3_analysis/figures/fig_p3_01_*.pdf/png
"""
import logging
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# --- OpenPE default style ---
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

DATA_DIR = "phase0_discovery/data/processed"
FIG_DIR = "phase3_analysis/figures"
OUT_DIR = "phase3_analysis/data"

# ---- Load datasets ----
log.info("Loading datasets...")
edu = pd.read_parquet(f"{DATA_DIR}/nbs_education_expenditure.parquet")
income = pd.read_parquet(f"{DATA_DIR}/nbs_disposable_income.parquet")
cpi = pd.read_parquet(f"{DATA_DIR}/nbs_cpi_deflator.parquet")
consumption = pd.read_parquet(f"{DATA_DIR}/nbs_consumption_categories.parquet")
demographics = pd.read_parquet(f"{DATA_DIR}/china_demographics.parquet")

log.info(f"Education: {edu.shape}, Income: {income.shape}, CPI: {cpi.shape}")
log.info(f"Consumption categories: {consumption.shape}, Demographics: {demographics.shape}")

# ---- CPI deflation ----
log.info("CPI deflating education spending series...")

# Merge CPI into education data
merged = edu.merge(cpi[["year", "deflator_education", "deflator_overall"]], on="year")
merged = merged.merge(income[["year", "national_yuan", "urban_yuan", "rural_yuan"]], on="year",
                      suffixes=("", "_income"))

# Real education spending (2015 yuan)
merged["real_national"] = merged["education_culture_recreation_national_yuan"] * merged["deflator_education"]
merged["real_urban"] = merged["education_culture_recreation_urban_yuan"] * merged["deflator_education"]
merged["real_rural"] = merged["education_culture_recreation_rural_yuan"] * merged["deflator_education"]

# Real income (2015 yuan, using overall CPI)
merged["real_income_national"] = merged["national_yuan"] * merged["deflator_overall"]
merged["real_income_urban"] = merged["urban_yuan"] * merged["deflator_overall"]
merged["real_income_rural"] = merged["rural_yuan"] * merged["deflator_overall"]

# Policy and COVID indicators
merged["post_policy"] = (merged["year"] >= 2021).astype(int)
merged["covid_2020"] = (merged["year"] == 2020).astype(int)
merged["time_index"] = merged["year"] - 2016  # 0..9
merged["time_since_policy"] = np.maximum(merged["year"] - 2021, 0)

# Education share of income
merged["edu_share_income_national"] = (
    merged["education_culture_recreation_national_yuan"] / merged["national_yuan"] * 100
)
merged["edu_share_income_urban"] = (
    merged["education_culture_recreation_urban_yuan"] / merged["urban_yuan"] * 100
)
merged["edu_share_income_rural"] = (
    merged["education_culture_recreation_rural_yuan"] / merged["rural_yuan"] * 100
)

# Merge demographics for per-child normalization
merged = merged.merge(
    demographics[["year", "births_millions", "compulsory_education_enrollment_millions"]],
    on="year", how="left",
)

# Per-birth spending intensity
merged["spending_per_birth"] = merged["real_national"] / merged["births_millions"]

log.info(f"Merged analysis dataset: {merged.shape}")
log.info(f"Columns: {list(merged.columns)}")

# ---- Verify stationarity ----
log.info("\n=== Stationarity Tests ===")

stationarity_results = []

for series_name, col in [
    ("Real national (levels)", "real_national"),
    ("Real urban (levels)", "real_urban"),
    ("Real rural (levels)", "real_rural"),
    ("Real national (1st diff)", None),
]:
    if col is not None:
        data = merged[col].dropna().values
    else:
        data = np.diff(merged["real_national"].dropna().values)

    # ADF test
    try:
        adf_stat, adf_p, adf_lags, nobs, *_ = adfuller(data, maxlag=2)
    except Exception as e:
        log.warning(f"ADF test failed for {series_name}: {e}")
        adf_stat, adf_p = np.nan, np.nan

    # KPSS test
    try:
        kpss_stat, kpss_p, kpss_lags, kpss_cv = kpss(data, regression="c", nlags="auto")
    except Exception as e:
        log.warning(f"KPSS test failed for {series_name}: {e}")
        kpss_stat, kpss_p = np.nan, np.nan

    adf_verdict = "Stationary" if adf_p < 0.05 else "NON-stationary"
    kpss_verdict = "Stationary" if kpss_p > 0.05 else "NON-stationary"

    stationarity_results.append({
        "series": series_name,
        "adf_stat": adf_stat,
        "adf_p": adf_p,
        "adf_verdict": adf_verdict,
        "kpss_stat": kpss_stat,
        "kpss_p": kpss_p,
        "kpss_verdict": kpss_verdict,
    })

    log.info(
        f"{series_name}: ADF={adf_stat:.3f} (p={adf_p:.4f}, {adf_verdict}), "
        f"KPSS={kpss_stat:.3f} (p={kpss_p:.4f}, {kpss_verdict})"
    )

stationarity_df = pd.DataFrame(stationarity_results)

# ---- Save processed dataset ----
import os
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

merged.to_parquet(f"{OUT_DIR}/analysis_dataset.parquet", index=False)
log.info(f"Saved analysis dataset to {OUT_DIR}/analysis_dataset.parquet")

# ---- Filter-flow table ----
log.info("\n=== Prefilter Summary ===")
log.info(f"Total observations: {len(merged)}")
log.info(f"Years: {merged['year'].min()}-{merged['year'].max()}")
log.info(f"Pre-policy (excl 2020): {len(merged[(merged['year'] < 2021) & (merged['year'] != 2020)])}")
log.info(f"Post-policy: {len(merged[merged['year'] >= 2021])}")
log.info(f"Missing values in key columns: "
         f"real_national={merged['real_national'].isna().sum()}, "
         f"real_income_national={merged['real_income_national'].isna().sum()}")

# Validate deflation
log.info("\n=== CPI Deflation Validation ===")
for yr in [2019, 2025]:
    row = merged[merged["year"] == yr].iloc[0]
    log.info(
        f"Year {yr}: Nominal={row['education_culture_recreation_national_yuan']:.0f}, "
        f"Deflator={row['deflator_education']:.4f}, "
        f"Real={row['real_national']:.0f}"
    )

# ---- Figure: CPI-deflated series with policy line ----
fig, ax = plt.subplots(figsize=(8, 6))

years = merged["year"]
ax.plot(years, merged["real_national"], "o-", color="#2196F3", linewidth=2, label="National")
ax.plot(years, merged["real_urban"], "s-", color="#F44336", linewidth=2, label="Urban")
ax.plot(years, merged["real_rural"], "^-", color="#4CAF50", linewidth=2, label="Rural")
ax.axvline(2021, color="gray", linestyle="--", linewidth=1.5, label="Double Reduction (Jul 2021)")
ax.axvspan(2020, 2021, alpha=0.1, color="orange", label="COVID period")

ax.set_xlabel("Year")
ax.set_ylabel("Real per capita spending [2015 yuan]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8,
        va="top", ha="left", color="gray", style="italic")

fig.savefig(f"{FIG_DIR}/fig_p3_01_real_spending_prefilter.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_01_real_spending_prefilter.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"Saved prefilter figure to {FIG_DIR}/fig_p3_01_real_spending_prefilter.pdf")

# ---- Summary statistics ----
log.info("\n=== Summary Statistics ===")
for col_label, col in [("Real national", "real_national"), ("Real urban", "real_urban"),
                        ("Real rural", "real_rural")]:
    vals = merged[col]
    log.info(f"{col_label}: mean={vals.mean():.0f}, std={vals.std():.0f}, "
             f"min={vals.min():.0f}, max={vals.max():.0f}")

log.info("\nStep 1 (Prefilter) complete.")
