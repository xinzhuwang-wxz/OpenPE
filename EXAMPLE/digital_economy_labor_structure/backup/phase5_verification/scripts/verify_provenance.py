"""
Data Provenance Audit: Phase 5 Verification Program 2
Verifies SHA-256 hashes and spot-checks data values.
"""
import hashlib
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

BASE = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure")

# Load registry
with open(BASE / "data" / "registry.yaml") as f:
    registry = yaml.unsafe_load(f)

datasets = registry["datasets"]
log.info(f"Registry contains {len(datasets)} dataset entries")

results = []

for ds in datasets:
    name = ds["name"]
    status = ds.get("status", "unknown")
    raw_file = ds.get("raw_file", "N/A")
    expected_hash = ds.get("sha256_raw", "N/A")

    log.info(f"\n--- {name} (status: {status}) ---")

    if raw_file in ("NOT_ACQUIRED", "N/A") or status in ("failed", "attempted"):
        log.info(f"  Skipping: {status}")
        results.append({
            "name": name, "status": status, "hash_match": "N/A",
            "file_exists": "N/A", "row_check": "N/A", "verdict": "SKIP"
        })
        continue

    raw_path = BASE / raw_file
    if not raw_path.exists():
        log.info(f"  RAW FILE MISSING: {raw_path}")
        results.append({
            "name": name, "status": status, "hash_match": "MISSING",
            "file_exists": False, "row_check": "N/A", "verdict": "FAIL"
        })
        continue

    # SHA-256 hash check
    sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    hash_match = sha == expected_hash
    log.info(f"  SHA-256: {'MATCH' if hash_match else 'MISMATCH'}")
    if not hash_match:
        log.info(f"    Expected: {expected_hash}")
        log.info(f"    Got:      {sha}")

    # Row count check
    try:
        df_raw = pd.read_csv(raw_path)
        n_rows = len(df_raw)
        expected_obs = ds.get("observations", None)
        row_ok = True
        if expected_obs is not None and isinstance(expected_obs, (int, float)):
            row_ok = n_rows == int(expected_obs)
        log.info(f"  Rows: {n_rows} (expected: {expected_obs}, match: {row_ok})")
    except Exception as e:
        log.info(f"  Could not read CSV: {e}")
        n_rows = -1
        row_ok = False

    # Processed file check
    proc_file = ds.get("processed_file", "N/A")
    proc_path = BASE / proc_file if proc_file != "N/A" else None
    proc_exists = proc_path.exists() if proc_path else False
    proc_hash_expected = ds.get("sha256_processed", "N/A")
    if proc_exists and proc_hash_expected != "N/A":
        proc_sha = hashlib.sha256(proc_path.read_bytes()).hexdigest()
        proc_match = proc_sha == proc_hash_expected
        log.info(f"  Processed SHA-256: {'MATCH' if proc_match else 'MISMATCH'}")
    else:
        proc_match = None

    verdict = "PASS" if hash_match and row_ok else "FLAG"
    results.append({
        "name": name, "status": status,
        "hash_match": hash_match,
        "proc_hash_match": proc_match,
        "file_exists": True,
        "rows": n_rows,
        "row_check": row_ok,
        "verdict": verdict
    })

# ============================================================
# SPOT-CHECK: World Bank data values
# ============================================================
log.info("\n" + "=" * 60)
log.info("SPOT-CHECKS: World Bank Data Values")
log.info("=" * 60)

df_wb = pd.read_parquet(BASE / "data" / "processed" / "worldbank_china_indicators.parquet")
log.info(f"WB shape: {df_wb.shape}")

# Known reference values for China from World Bank
spot_checks = [
    ("internet_users_pct", 2020, 70.4, 3.0, "Internet users % (WB 2020)"),
    ("employment_services_pct", 2023, 48.0, 5.0, "Services employment % ~2023"),
    ("employment_agriculture_pct", 2000, 50.0, 2.0, "Agriculture employment % 2000"),
    ("gdp_per_capita_usd", 2023, 12500, 1000, "GDP per capita ~2023"),
    ("population_15_64_pct", 2023, 68.0, 4.0, "Working age pop % ~2023"),
]

for var, year, expected, tol, desc in spot_checks:
    row = df_wb[df_wb["year"] == year]
    if len(row) == 0:
        log.info(f"  {desc}: year {year} not found")
        continue
    actual = row[var].values[0]
    ok = abs(actual - expected) < tol
    log.info(f"  {desc}: expected~{expected}, got={actual:.1f}, {'OK' if ok else 'DIVERGE'}")

# ============================================================
# Digital economy index construction check
# ============================================================
log.info("\n" + "=" * 60)
log.info("DE INDEX CONSTRUCTION VERIFICATION")
log.info("=" * 60)

df_merged = pd.read_parquet(BASE / "data" / "processed" / "china_national_panel_merged.parquet")

# Verify the DE index is constructed from internet, mobile, broadband, R&D
# Each should be min-max normalized, then averaged
for var in ["internet_users_pct", "mobile_subscriptions_per100", "fixed_broadband_per100", "rd_expenditure_pct_gdp"]:
    raw = df_merged[var].values
    norm = df_merged.get(f"{var}_normalized")
    if norm is not None:
        norm_vals = norm.values
        # Check min-max normalization
        raw_clean = raw[~np.isnan(raw)]
        expected_norm = (raw - np.nanmin(raw)) / (np.nanmax(raw) - np.nanmin(raw))
        diff = np.nanmax(np.abs(norm_vals - expected_norm))
        log.info(f"  {var}: max normalization error = {diff:.6f} ({'OK' if diff < 0.01 else 'ERROR'})")

# Check composite index = mean of normalized components
components = ["internet_users_pct_normalized", "mobile_subscriptions_per100_normalized",
              "fixed_broadband_per100_normalized", "rd_expenditure_pct_gdp_normalized"]
comp_data = df_merged[components].values
expected_de = np.nanmean(comp_data, axis=1)
actual_de = df_merged["digital_economy_index"].values
de_diff = np.nanmax(np.abs(expected_de - actual_de))
log.info(f"  DE index = mean(components): max error = {de_diff:.6f} ({'OK' if de_diff < 0.01 else 'ERROR'})")

# Check saturation
log.info(f"  DE index 2023 value: {actual_de[-1]:.4f} (expected ~1.0)")
log.info(f"  DE index 2000 value: {actual_de[0]:.4f} (expected ~0.0)")

# ============================================================
# SUMMARY
# ============================================================
log.info("\n" + "=" * 60)
log.info("PROVENANCE AUDIT SUMMARY")
log.info("=" * 60)
log.info(f"{'Dataset':<40} {'Hash':>8} {'Rows':>8} {'Verdict':>8}")
log.info("-" * 66)
for r in results:
    log.info(f"{r['name']:<40} {str(r['hash_match']):>8} {str(r['row_check']):>8} {r['verdict']:>8}")
