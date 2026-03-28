# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""World Bank data fetcher for OpenPE.

Usage:
    pixi run py phase0_discovery/scripts/fetch_worldbank.py \
        --indicator NY.GDP.PCAP.CD --country CHN --start 1980 --end 2025 \
        --output phase0_discovery/data/raw/

Requires: wbgapi, pandas, pyarrow (in pixi.toml)
"""
import argparse
from pathlib import Path
import pandas as pd
import wbgapi as wb
from registry_utils import register_dataset


def fetch(indicator: str, country: str, start: int, end: int, output_dir: Path) -> Path:
    """Fetch a World Bank indicator and save as Parquet."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df = wb.data.DataFrame(indicator, country, time=range(start, end + 1))
    df = df.T.reset_index()
    df.columns = ["year", "value"]
    filename = f"wb_{indicator}_{country}_{start}_{end}.parquet"
    filepath = output_dir / filename
    df.to_parquet(filepath, index=False)
    registry_path = output_dir.parent / "registry.yaml"
    register_dataset(
        registry_path=registry_path,
        source_id=f"wb_{indicator}_{country}",
        name=f"World Bank: {indicator} for {country}",
        url=f"https://data.worldbank.org/indicator/{indicator}?locations={country}",
        filepath=filepath,
        query_params={"indicator": indicator, "country": country, "start": start, "end": end},
    )
    print(f"Saved {filepath} ({len(df)} rows)")
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch World Bank data")
    parser.add_argument("--indicator", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--start", type=int, default=1960)
    parser.add_argument("--end", type=int, default=2025)
    parser.add_argument("--output", type=Path, default=Path("phase0_discovery/data/raw"))
    args = parser.parse_args()
    fetch(args.indicator, args.country, args.start, args.end, args.output)
