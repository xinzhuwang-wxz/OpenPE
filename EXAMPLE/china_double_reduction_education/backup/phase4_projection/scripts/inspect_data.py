"""Inspect the analysis dataset for Phase 4 projection planning."""
import pandas as pd
import json

# Read the analysis dataset
df = pd.read_parquet("phase3_analysis/data/analysis_dataset.parquet")
print("Columns:", df.columns.tolist())
print()
print(df.to_string())
print()

# Read key JSON results
with open("phase3_analysis/data/its_results.json") as f:
    its = json.load(f)

print("\n=== ITS Key Parameters ===")
for series in ["national", "urban", "rural"]:
    d = its[series]
    print(f"{series}: shift={d['primary']['level_shift']:.1f}, "
          f"trend={d['primary']['trend']:.1f}, "
          f"pre_mean={d['pre_policy_mean']:.1f}")
