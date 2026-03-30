"""Quick data check for Phase 3 analysis."""
import pandas as pd

df = pd.read_parquet("data/processed/analysis_ready.parquet")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print()
cols = [
    "year",
    "digital_economy_index",
    "employment_services_pct",
    "employment_industry_pct",
    "employment_agriculture_pct",
    "services_value_added_pct_gdp",
    "population_15_64_pct",
    "population_65plus_pct",
]
print(df[cols].to_string())
