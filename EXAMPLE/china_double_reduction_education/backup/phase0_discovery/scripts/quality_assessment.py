import pandas as pd
import numpy as np
import logging
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

DATA_DIR = Path("phase0_discovery/data/processed")

def assess(name, path):
    log.info(f"\n{'='*60}")
    log.info(f"DATASET: {name}")
    log.info(f"{'='*60}")
    df = pd.read_parquet(path)
    log.info(f"Shape: {df.shape}")
    log.info(f"Columns: {list(df.columns)}")
    log.info(f"Dtypes:\n{df.dtypes}")
    log.info(f"\nMissing values per column:")
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
    for col in df.columns:
        log.info(f"  {col}: {missing[col]} ({missing_pct[col]}%)")
    log.info(f"\nTotal missing rate: {(df.isnull().sum().sum() / df.size * 100):.1f}%")
    
    # Numeric stats
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        log.info(f"\nNumeric summary:")
        log.info(f"{df[num_cols].describe().to_string()}")
    
    # Check for duplicates
    n_dupes = df.duplicated().sum()
    log.info(f"\nDuplicate rows: {n_dupes}")
    
    log.info(f"\nFull data:")
    log.info(f"{df.to_string()}")
    return df

# Dataset 1: NBS Education Expenditure
df1 = assess("NBS Education Expenditure", DATA_DIR / "nbs_education_expenditure.parquet")

# Dataset 2: CIEFR Spending Composition
df2 = assess("CIEFR Spending Composition", DATA_DIR / "ciefr_spending_composition.parquet")

# Dataset 3: World Bank
df3 = assess("World Bank Education Indicators", DATA_DIR / "worldbank_education_indicators.parquet")

# Dataset 4: Tutoring Industry
df4 = assess("Tutoring Industry Metrics", DATA_DIR / "tutoring_industry_metrics.parquet")

# Dataset 5: Policy Timeline
df5 = assess("Policy Timeline", DATA_DIR / "policy_timeline.parquet")

# Dataset 6: Demographics
df6 = assess("Demographics", DATA_DIR / "china_demographics.parquet")

# Dataset 7: Public Education Expenditure
df7 = assess("Public Education Expenditure", DATA_DIR / "public_education_expenditure.parquet")

# Dataset 8: NBS Consumption Categories
df8 = assess("NBS Consumption Categories", DATA_DIR / "nbs_consumption_categories.parquet")

# Dataset 9: NBS Disposable Income
df9 = assess("NBS Disposable Income", DATA_DIR / "nbs_disposable_income.parquet")

# Dataset 10: International Comparison
df10 = assess("International Comparison", DATA_DIR / "international_comparison.parquet")

# Dataset 11: Underground Tutoring Prices
df11 = assess("Underground Tutoring Prices", DATA_DIR / "underground_tutoring_prices.parquet")

# Dataset 12: Crowding-In Evidence
df12 = assess("Crowding-In Evidence", DATA_DIR / "crowding_in_evidence.parquet")

# Additional CIEFR files
for f in sorted(DATA_DIR.glob("ciefr_*.parquet")):
    if f.name not in ["ciefr_spending_composition.parquet"]:
        assess(f"CIEFR sub-file: {f.name}", f)

# Cross-dataset checks
log.info("\n" + "="*60)
log.info("CROSS-DATASET CONSISTENCY CHECKS")
log.info("="*60)

# Check NBS education expenditure vs consumption categories
log.info("\nNBS Education Expenditure vs All Categories (overlap check):")
if "year" in df1.columns and "year" in df8.columns:
    years_1 = set(df1["year"].unique())
    years_8 = set(df8["year"].unique())
    log.info(f"  Education dataset years: {sorted(years_1)}")
    log.info(f"  All categories years: {sorted(years_8)}")
    log.info(f"  Overlap: {sorted(years_1 & years_8)}")

# Check NBS income temporal alignment
log.info("\nNBS Income vs Education (temporal alignment):")
if "year" in df1.columns and "year" in df9.columns:
    years_9 = set(df9["year"].unique())
    log.info(f"  Income years: {sorted(years_9)}")
    log.info(f"  Education years: {sorted(years_1)}")
    log.info(f"  Overlap: {sorted(years_1 & years_9)}")

