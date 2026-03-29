"""Inspect key data files for Phase 3 analysis."""
import pandas as pd

DATA_DIR = "phase0_discovery/data/processed"

for f in [
    "nbs_education_expenditure",
    "nbs_disposable_income",
    "nbs_cpi_deflator",
    "nbs_consumption_categories",
    "china_demographics",
]:
    df = pd.read_parquet(f"{DATA_DIR}/{f}.parquet")
    print(f"\n=== {f} ===")
    print(f"Shape: {df.shape}")
    print(f"Cols: {list(df.columns)}")
    print(df.to_string())
