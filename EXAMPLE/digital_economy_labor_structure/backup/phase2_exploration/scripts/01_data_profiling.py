"""Step 2.1 & 2.2: Data profiling, cleaning log, and feature engineering."""

import logging
import json
import numpy as np
import pandas as pd
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

DATA_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/processed")
OUT_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/scripts")

df = pd.read_parquet(DATA_DIR / "china_national_panel_merged.parquet")
log.info(f"Loaded merged panel: {df.shape}")
log.info(f"Columns: {sorted(df.columns.tolist())}")
log.info(f"Year range: {df['year'].min()} - {df['year'].max()}")

# --- Basic profiling ---
log.info("\n=== DTYPES ===")
log.info(f"\n{df.dtypes.to_string()}")

log.info("\n=== MISSING VALUES ===")
missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
missing_df = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
missing_df = missing_df[missing_df["missing_count"] > 0].sort_values("missing_pct", ascending=False)
log.info(f"\n{missing_df.to_string()}")

log.info("\n=== DESCRIBE (numeric) ===")
desc = df.describe().T
desc_str = desc[["count", "mean", "std", "min", "max"]].round(3).to_string()
log.info(f"\n{desc_str}")

# --- Identify unusable columns ---
unusable = missing_df[missing_df["missing_pct"] > 90].index.tolist()
log.info(f"\nUnusable columns (>90% missing): {unusable}")

cols_to_drop = ["labor_force_advanced_education_pct", "labor_force_basic_education_pct", "labor_force_intermediate_education_pct"]
cols_to_drop = [c for c in cols_to_drop if c in df.columns]
log.info(f"Columns to drop (education-based skill, unusable): {cols_to_drop}")

# --- Usable variable set ---
usable_cols = [c for c in df.columns if c not in cols_to_drop]
df_clean = df[usable_cols].copy()
log.info(f"\nUsable dataset shape: {df_clean.shape}")
log.info(f"Usable missing rate: {df_clean.isnull().sum().sum() / df_clean.size * 100:.2f}%")

# --- Outlier detection (3 sigma) ---
log.info("\n=== OUTLIER CHECK (3 sigma from mean) ===")
numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [c for c in numeric_cols if c != "year"]
outlier_found = False
for col in numeric_cols:
    s = df_clean[col].dropna()
    if len(s) < 5:
        continue
    mean, std = s.mean(), s.std()
    if std == 0:
        continue
    outliers = s[(s < mean - 3*std) | (s > mean + 3*std)]
    if len(outliers) > 0:
        outlier_found = True
        log.info(f"  {col}: {len(outliers)} outlier(s) at years {df_clean.loc[outliers.index, 'year'].tolist()}")
if not outlier_found:
    log.info("  No 3-sigma outliers detected in any variable.")

# --- Duplicate check ---
dupes = df.duplicated().sum()
log.info(f"\nDuplicate rows: {dupes}")

# --- Temporal continuity ---
years = sorted(df["year"].unique())
expected_years = list(range(int(years[0]), int(years[-1])+1))
missing_years = set(expected_years) - set([int(y) for y in years])
log.info(f"Year coverage: {years[0]}-{years[-1]} ({len(years)} obs)")
log.info(f"Missing years: {missing_years if missing_years else 'None'}")

# --- Save profiling results as JSON ---
profile = {
    "shape": list(df.shape),
    "usable_shape": list(df_clean.shape),
    "year_range": [int(years[0]), int(years[-1])],
    "missing_years": sorted(list(missing_years)),
    "duplicate_rows": int(dupes),
    "unusable_columns": unusable,
    "dropped_columns": cols_to_drop,
    "missing_by_column": {k: {"count": int(v), "pct": float(missing_pct[k])} for k, v in missing.items() if v > 0},
    "usable_missing_rate_pct": round(df_clean.isnull().sum().sum() / df_clean.size * 100, 2),
    "columns": list(df_clean.columns),
}
with open(OUT_DIR / "profile_results.json", "w") as f:
    json.dump(profile, f, indent=2)
log.info(f"\nProfile saved to {OUT_DIR / 'profile_results.json'}")

# --- Feature engineering ---
log.info("\n=== FEATURE ENGINEERING ===")

# Log GDP per capita
df_clean["log_gdp_pc"] = np.log(df_clean["gdp_per_capita_usd"])

# Post-pilot indicator
df_clean["post_pilot"] = (df_clean["year"] >= 2016).astype(int)
df_clean["transition_window"] = df_clean["year"].isin([2013, 2014, 2015]).astype(int)

# First differences for key variables
key_vars = ["digital_economy_index", "employment_services_pct", "employment_industry_pct",
            "employment_agriculture_pct", "services_value_added_pct_gdp", "population_15_64_pct",
            "population_65plus_pct", "urban_population_pct", "log_gdp_pc"]
for var in key_vars:
    if var in df_clean.columns:
        df_clean[f"d_{var}"] = df_clean[var].diff()

# Growth rates
for var in ["gdp_per_capita_usd", "labor_force_total"]:
    if var in df_clean.columns:
        df_clean[f"g_{var}"] = df_clean[var].pct_change() * 100

eng_features = [c for c in df_clean.columns if c.startswith("d_") or c.startswith("g_") or c in ["log_gdp_pc", "post_pilot", "transition_window"]]
log.info(f"Engineered features: {eng_features}")
log.info(f"Final dataset shape: {df_clean.shape}")

# Check engineered features for NaN/Inf
for col in [c for c in df_clean.columns if c.startswith("d_") or c.startswith("g_") or c == "log_gdp_pc"]:
    ninf = np.isinf(df_clean[col]).sum()
    nnan = df_clean[col].isnull().sum()
    if ninf > 0:
        log.info(f"  WARNING: {col} has {ninf} Inf values")

# Save cleaned + engineered dataset
out_path = DATA_DIR / "analysis_ready.parquet"
df_clean.to_parquet(out_path, index=False)
log.info(f"\nAnalysis-ready dataset saved to {out_path}")
