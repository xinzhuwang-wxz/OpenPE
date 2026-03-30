"""Quick verification of acquired data."""
import pandas as pd
import logging
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])
log = logging.getLogger(__name__)

wb = pd.read_parquet("data/processed/worldbank_china_indicators.parquet")
log.info(f"World Bank: {wb.shape}, years: {wb['year'].min()}-{wb['year'].max()}")
log.info(f"  Columns: {list(wb.columns)}")

ilo = pd.read_parquet("data/processed/ilo_china_employment_structure.parquet")
log.info(f"ILO: {ilo.shape}, years: {ilo['year'].min()}-{ilo['year'].max()}")

pilots = pd.read_parquet("data/processed/smart_city_pilots_list.parquet")
log.info(f"Smart city pilots: {pilots.shape}, batches: {pilots['batch'].value_counts().to_dict()}")

panel = pd.read_parquet("data/processed/smart_city_pilots_panel.parquet")
log.info(f"Pilot panel: {panel.shape}")

de = pd.read_parquet("data/processed/digital_economy_composite_index.parquet")
log.info(f"DE index: {de.shape}, years: {de['year'].min()}-{de['year'].max()}")

merged = pd.read_parquet("data/processed/china_national_panel_merged.parquet")
log.info(f"Merged: {merged.shape}, years: {merged['year'].min()}-{merged['year'].max()}")
log.info(f"  Overall missing: {merged.isna().mean().mean()*100:.1f}%")
log.info(f"  Total columns: {len(merged.columns)}")

# Check for key analysis variables
key_vars = [
    "employment_agriculture_pct", "employment_industry_pct", "employment_services_pct",
    "internet_users_pct", "gdp_per_capita_usd", "urban_population_pct",
    "digital_economy_index", "self_employed_pct", "wage_salaried_workers_pct",
]
log.info("Key variable coverage:")
for v in key_vars:
    if v in merged.columns:
        non_null = merged[v].notna().sum()
        log.info(f"  {v}: {non_null}/{len(merged)} observations")
    else:
        log.warning(f"  {v}: MISSING from merged dataset")
