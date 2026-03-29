"""Check row count mismatches for ds_002, ds_004, ds_011."""
import pandas as pd
from pathlib import Path

BASE = Path("phase0_discovery/data/processed")

# ds_002: registry says 13 observations, but main file has 3
# The 13 includes sub-files (ciefr_compulsory_education, ciefr_spending_by_income, etc.)
df = pd.read_parquet(BASE / "ciefr_spending_composition.parquet")
print("ds_002 main file rows:", len(df))

# Check sub-files
for f in sorted(BASE.glob("ciefr_*.parquet")):
    d = pd.read_parquet(f)
    print(f"  {f.name}: {len(d)} rows")

print()

# ds_004: registry says 19, main file has 10
df4 = pd.read_parquet(BASE / "tutoring_industry_metrics.parquet")
print("ds_004 main file rows:", len(df4))
for f in sorted(BASE.glob("tutoring_*.parquet")):
    d = pd.read_parquet(f)
    print(f"  {f.name}: {len(d)} rows")

print()

# ds_011: registry says 14, main file has 9
df11 = pd.read_parquet(BASE / "underground_tutoring_prices.parquet")
print("ds_011 main file rows:", len(df11))
