# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""FRED data fetcher for OpenPE.

Usage:
    pixi run py phase0_discovery/scripts/fetch_fred.py \
        --series GDP --start 1980-01-01 --end 2025-01-01 \
        --output phase0_discovery/data/raw/

Requires FRED_API_KEY environment variable.
Get one free at https://fred.stlouisfed.org/docs/api/api_key.html
"""
import argparse
import os
from pathlib import Path
import pandas as pd
from fredapi import Fred
from registry_utils import register_dataset


def fetch(series_id: str, start: str, end: str, output_dir: Path) -> Path:
    """Fetch a FRED series and save as Parquet."""
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        raise ValueError(
            "Set FRED_API_KEY environment variable. "
            "Get one free at https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    fred = Fred(api_key=api_key)
    data = fred.get_series(series_id, observation_start=start, observation_end=end)
    df = data.reset_index()
    df.columns = ["date", "value"]
    filename = f"fred_{series_id}_{start}_{end}.parquet"
    filepath = output_dir / filename
    df.to_parquet(filepath, index=False)
    registry_path = output_dir.parent / "registry.yaml"
    register_dataset(
        registry_path=registry_path,
        source_id=f"fred_{series_id}",
        name=f"FRED: {series_id}",
        url=f"https://fred.stlouisfed.org/series/{series_id}",
        filepath=filepath,
        query_params={"series_id": series_id, "start": start, "end": end},
    )
    print(f"Saved {filepath} ({len(df)} rows)")
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch FRED data")
    parser.add_argument("--series", required=True)
    parser.add_argument("--start", default="1960-01-01")
    parser.add_argument("--end", default="2025-01-01")
    parser.add_argument("--output", type=Path, default=Path("phase0_discovery/data/raw"))
    args = parser.parse_args()
    fetch(args.series, args.start, args.end, args.output)
