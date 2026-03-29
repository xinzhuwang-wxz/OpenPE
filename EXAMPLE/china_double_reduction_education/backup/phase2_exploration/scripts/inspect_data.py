import pandas as pd
import os
import logging
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

data_dir = "phase0_discovery/data/processed"
files = [
    "nbs_education_expenditure.parquet",
    "nbs_consumption_categories.parquet",
    "nbs_disposable_income.parquet",
    "nbs_cpi_deflator.parquet",
    "china_demographics.parquet",
    "public_education_expenditure.parquet",
    "tutoring_industry_metrics.parquet",
    "ciefr_spending_composition.parquet",
    "ciefr_tutoring_2017_vs_2019.parquet",
    "underground_tutoring_prices.parquet",
    "policy_timeline.parquet",
]

for f in files:
    path = os.path.join(data_dir, f)
    df = pd.read_parquet(path)
    log.info(f"=== {f} ===")
    log.info(f"Shape: {df.shape}")
    log.info(f"Columns: {list(df.columns)}")
    log.info(f"Dtypes:\n{df.dtypes}")
    log.info(f"Head:\n{df.head().to_string()}")
    log.info(f"Describe:\n{df.describe(include='all').to_string()}")
    log.info(f"Nulls:\n{df.isnull().sum()}")
    log.info("")
