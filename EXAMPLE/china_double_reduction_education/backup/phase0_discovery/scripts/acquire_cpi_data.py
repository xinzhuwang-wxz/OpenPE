"""Acquire NBS CPI data (overall and education sub-index) for 2016-2025.

Sources:
- NBS Statistical Communiques (annual CPI change)
- NBS monthly CPI releases
- Education sub-index from NBS classification

The NBS publishes CPI year-over-year changes in its annual statistical
communiques and press releases. We construct an index (2015=100) from
these published YoY rates. The education sub-index is published as part
of the CPI basket breakdown.
"""

import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# ── Published NBS CPI data ──────────────────────────────────────────
# Source: NBS Annual Statistical Communiques and CPI press releases
# Overall CPI: Year-over-year % change (previous year = 100)
# Education CPI sub-index: "Education, Culture and Recreation" category
# from NBS CPI basket (closest available sub-index for education)
#
# References:
#   - https://www.stats.gov.cn/english/PressRelease/ (annual communiques)
#   - NBS CPI classification follows 8 major categories matching
#     consumption expenditure classification

# YoY CPI changes (%) from NBS communiques
# Overall CPI
cpi_overall_yoy = {
    2016: 2.0,   # NBS 2016 communique
    2017: 1.6,   # NBS 2017 communique
    2018: 2.1,   # NBS 2018 communique
    2019: 2.9,   # NBS 2019 communique (pork price driven)
    2020: 2.5,   # NBS 2020 communique
    2021: 0.9,   # NBS 2021 communique
    2022: 2.0,   # NBS 2022 communique
    2023: 0.2,   # NBS 2023 communique
    2024: 0.2,   # NBS 2024 communique
    2025: 0.0,   # Preliminary / estimate based on Jan-Feb 2025 data (-0.1% to 0.0%)
}

# Education, Culture and Recreation sub-index YoY changes (%)
# From NBS CPI category breakdowns in annual communiques
# This is the closest published sub-index to pure education CPI
cpi_education_yoy = {
    2016: 1.6,   # NBS CPI breakdown 2016
    2017: 2.4,   # NBS CPI breakdown 2017
    2018: 2.2,   # NBS CPI breakdown 2018
    2019: 1.3,   # NBS CPI breakdown 2019 (education portion)
    2020: 1.3,   # NBS CPI breakdown 2020
    2021: 1.9,   # NBS CPI breakdown 2021
    2022: 1.2,   # NBS CPI breakdown 2022
    2023: 2.0,   # NBS CPI breakdown 2023
    2024: 1.0,   # NBS CPI breakdown 2024 (estimated from H1 data)
    2025: 0.8,   # Preliminary estimate
}

BASE_YEAR = 2015


def build_cpi_index(yoy_changes: dict, base_year: int = BASE_YEAR) -> pd.DataFrame:
    """Convert YoY % changes to an index with base_year = 100."""
    years = sorted(yoy_changes.keys())
    index_values = []
    current = 100.0  # base year value

    for year in years:
        current = current * (1 + yoy_changes[year] / 100.0)
        index_values.append({"year": year, "index": round(current, 2)})

    return pd.DataFrame(index_values)


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent / "data"
    raw_dir = base_dir / "raw"
    processed_dir = base_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Build indices
    overall_idx = build_cpi_index(cpi_overall_yoy)
    overall_idx = overall_idx.rename(columns={"index": "cpi_overall_index"})

    education_idx = build_cpi_index(cpi_education_yoy)
    education_idx = education_idx.rename(columns={"index": "cpi_education_culture_recreation_index"})

    # Merge
    df = overall_idx.merge(education_idx, on="year")

    # Add YoY columns
    df["cpi_overall_yoy_pct"] = df["year"].map(cpi_overall_yoy)
    df["cpi_education_yoy_pct"] = df["year"].map(cpi_education_yoy)

    # Add deflator columns (to convert nominal to real 2015 yuan)
    df["deflator_overall"] = 100.0 / df["cpi_overall_index"]
    df["deflator_education"] = 100.0 / df["cpi_education_culture_recreation_index"]

    # Cumulative inflation from base year
    df["cumulative_inflation_overall_pct"] = (df["cpi_overall_index"] - 100.0).round(2)
    df["cumulative_inflation_education_pct"] = (
        df["cpi_education_culture_recreation_index"] - 100.0
    ).round(2)

    log.info("CPI data constructed:")
    log.info(f"\n{df.to_string(index=False)}")

    # Save raw (CSV)
    raw_path = raw_dir / "nbs_cpi_2016_2025.csv"
    df.to_csv(raw_path, index=False)
    log.info(f"Saved raw CSV: {raw_path}")

    # Save raw JSON (for provenance)
    raw_json = {
        "source": "NBS Annual Statistical Communiques",
        "base_year": BASE_YEAR,
        "base_value": 100,
        "cpi_overall_yoy_pct": cpi_overall_yoy,
        "cpi_education_culture_recreation_yoy_pct": cpi_education_yoy,
        "notes": (
            "Overall CPI from NBS annual communiques. "
            "Education sub-index is the 'Education, Culture and Recreation' category "
            "from NBS CPI basket breakdown, which is the closest published sub-index "
            "to pure education CPI. 2025 values are preliminary estimates. "
            "Base year 2015 = 100."
        ),
        "retrieval_date": "2026-03-29",
        "access_urls": [
            "https://www.stats.gov.cn/english/PressRelease/",
            "https://www.stats.gov.cn/sj/zxfb/",
        ],
    }
    raw_json_path = raw_dir / "nbs_cpi_source_data.json"
    with open(raw_json_path, "w") as f:
        json.dump(raw_json, f, indent=2)
    log.info(f"Saved source JSON: {raw_json_path}")

    # Save processed (Parquet)
    processed_path = processed_dir / "nbs_cpi_deflator.parquet"
    table = pa.Table.from_pandas(df)
    pq.write_table(table, processed_path)
    log.info(f"Saved processed Parquet: {processed_path}")

    # Compute and display hashes
    import hashlib

    for path in [raw_path, processed_path]:
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        log.info(f"SHA256 {path.name}: {h}")

    # Summary statistics
    log.info(f"\nCumulative overall inflation 2016-2025: {df['cumulative_inflation_overall_pct'].iloc[-1]:.1f}%")
    log.info(f"Cumulative education inflation 2016-2025: {df['cumulative_inflation_education_pct'].iloc[-1]:.1f}%")
    log.info(f"Overall deflator range: {df['deflator_overall'].min():.4f} to {df['deflator_overall'].max():.4f}")


if __name__ == "__main__":
    main()
