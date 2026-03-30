"""Data Quality Assessment Script for Phase 0, Step 0.5."""
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

DATA_DIR = Path("data/processed")


def assess_dataset(name, path):
    """Assess a single dataset on all four quality dimensions."""
    log.info(f"\n{'='*80}")
    log.info(f"DATASET: {name}")
    log.info(f"{'='*80}")

    df = pd.read_parquet(path)
    log.info(f"Shape: {df.shape}")
    log.info(f"Columns ({len(df.columns)}): {list(df.columns)}")
    log.info(f"dtypes:\n{df.dtypes.to_string()}")

    # Index info
    if df.index.name:
        log.info(f"Index: {df.index.name}, range: {df.index.min()} to {df.index.max()}")
    else:
        log.info(f"Index: RangeIndex, length={len(df)}")

    # --- COMPLETENESS ---
    log.info(f"\n--- COMPLETENESS ---")
    total_cells = len(df) * len(df.columns)
    total_missing = df.isnull().sum().sum()
    overall_missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
    log.info(f"Total cells: {total_cells}, Total missing: {total_missing}, Missing rate: {overall_missing_pct:.2f}%")

    missing_per_col = df.isnull().sum()
    missing_pct_per_col = (df.isnull().sum() / len(df) * 100).round(2)
    cols_with_missing = missing_per_col[missing_per_col > 0]
    if len(cols_with_missing) > 0:
        log.info("Columns with missing values:")
        for col in cols_with_missing.index:
            log.info(f"  {col}: {missing_per_col[col]}/{len(df)} ({missing_pct_per_col[col]}%)")
    else:
        log.info("No missing values in any column.")

    # Temporal coverage check
    year_cols = [c for c in df.columns if c.lower() == "year"]
    if "year" in df.columns:
        years = sorted(df["year"].unique())
        log.info(f"Year range: {years[0]}-{years[-1]}, unique years: {len(years)}")
        expected_years = list(range(int(years[0]), int(years[-1]) + 1))
        missing_years = set(expected_years) - set([int(y) for y in years])
        if missing_years:
            log.info(f"Missing years: {sorted(missing_years)}")
        else:
            log.info("No gaps in year coverage.")
    elif df.index.name == "year" or (hasattr(df.index, "dtype") and "int" in str(df.index.dtype)):
        years = sorted(df.index.unique())
        log.info(f"Year range (index): {years[0]}-{years[-1]}, unique years: {len(years)}")
        expected_years = list(range(int(years[0]), int(years[-1]) + 1))
        missing_years = set(expected_years) - set([int(y) for y in years])
        if missing_years:
            log.info(f"Missing years: {sorted(missing_years)}")
        else:
            log.info("No gaps in year coverage.")

    # --- CONSISTENCY ---
    log.info(f"\n--- CONSISTENCY ---")
    # Check duplicates
    n_dupes = df.duplicated().sum()
    log.info(f"Duplicate rows: {n_dupes}")

    # Check numeric ranges
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        mn, mx, mean, std = series.min(), series.max(), series.mean(), series.std()
        log.info(f"  {col}: min={mn:.4f}, max={mx:.4f}, mean={mean:.4f}, std={std:.4f}")

        # Flag percentage columns outside [0, 100]
        if "pct" in col.lower() and (mn < -0.01 or mx > 100.01):
            log.info(f"    WARNING: percentage column outside [0,100]")

        # Flag large year-over-year jumps (if time series)
        if len(series) >= 3 and std > 0:
            diffs = series.diff().dropna()
            max_jump = diffs.abs().max()
            jump_ratio = max_jump / std if std > 0 else 0
            if jump_ratio > 3:
                jump_year_idx = diffs.abs().idxmax()
                log.info(f"    ALERT: Large jump at index {jump_year_idx}: {max_jump:.4f} ({jump_ratio:.1f}x std)")

    # --- GRANULARITY ---
    log.info(f"\n--- GRANULARITY ---")
    log.info(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    # Descriptive stats for all numeric columns
    log.info(f"\n--- DESCRIPTIVE STATS ---")
    desc = df.describe()
    log.info(desc.round(4).to_string())

    return df


def main():
    datasets = {
        "worldbank_china_indicators": DATA_DIR / "worldbank_china_indicators.parquet",
        "ilo_china_employment_structure": DATA_DIR / "ilo_china_employment_structure.parquet",
        "smart_city_pilots_list": DATA_DIR / "smart_city_pilots_list.parquet",
        "smart_city_pilots_panel": DATA_DIR / "smart_city_pilots_panel.parquet",
        "digital_economy_composite_index": DATA_DIR / "digital_economy_composite_index.parquet",
        "china_provincial_framework": DATA_DIR / "china_provincial_framework.parquet",
        "china_national_panel_merged": DATA_DIR / "china_national_panel_merged.parquet",
    }

    for name, path in datasets.items():
        if path.exists():
            assess_dataset(name, path)
        else:
            log.info(f"\n{'='*80}")
            log.info(f"DATASET: {name} -- FILE NOT FOUND: {path}")
            log.info(f"{'='*80}")

    # --- CROSS-DATASET CHECKS ---
    log.info(f"\n{'='*80}")
    log.info("CROSS-DATASET CONSISTENCY CHECKS")
    log.info(f"{'='*80}")

    wb = pd.read_parquet(DATA_DIR / "worldbank_china_indicators.parquet")
    ilo = pd.read_parquet(DATA_DIR / "ilo_china_employment_structure.parquet")
    merged = pd.read_parquet(DATA_DIR / "china_national_panel_merged.parquet")

    # Check if WB and ILO share the same year index
    log.info(f"\nWB years: {sorted(wb.index.tolist())}")
    log.info(f"ILO years: {sorted(ilo.index.tolist())}")

    # Cross-check: merged should equal WB + ILO + DE index
    log.info(f"\nMerged panel shape: {merged.shape}")
    log.info(f"Merged missing rate: {(merged.isnull().sum().sum() / (len(merged) * len(merged.columns)) * 100):.2f}%")

    # Check ILO education columns specifically (noted as sparse in experiment log)
    edu_cols = [c for c in ilo.columns if "education" in c.lower() or "advanced" in c.lower() or "basic" in c.lower() or "intermediate" in c.lower()]
    log.info(f"\nILO education-related columns: {edu_cols}")
    for col in edu_cols:
        non_null = ilo[col].notna().sum()
        log.info(f"  {col}: {non_null}/{len(ilo)} non-null values")
        if non_null > 0:
            log.info(f"    Values: {ilo[col].dropna().tolist()}")

    # Smart city panel structure check
    panel = pd.read_parquet(DATA_DIR / "smart_city_pilots_panel.parquet")
    log.info(f"\nSmart city panel: {panel.shape}")
    log.info(f"  Unique cities: {panel['city_name'].nunique()}")
    log.info(f"  Year range: {panel['year'].min()}-{panel['year'].max()}")
    log.info(f"  Treatment distribution: {panel['treated'].value_counts().to_dict()}")
    log.info(f"  Batch distribution: {panel['batch'].value_counts().to_dict()}")

    # Provincial framework check
    prov = pd.read_parquet(DATA_DIR / "china_provincial_framework.parquet")
    log.info(f"\nProvincial framework: {prov.shape}")
    log.info(f"  Columns: {list(prov.columns)}")
    log.info(f"  Unique provinces: {prov['province'].nunique()}")
    # Check if it is truly empty (only province + year)
    data_cols = [c for c in prov.columns if c not in ("province", "year")]
    log.info(f"  Data columns (beyond province/year): {data_cols}")
    if len(data_cols) == 0:
        log.info("  CONFIRMED: Framework is empty -- no actual data variables.")


if __name__ == "__main__":
    main()
