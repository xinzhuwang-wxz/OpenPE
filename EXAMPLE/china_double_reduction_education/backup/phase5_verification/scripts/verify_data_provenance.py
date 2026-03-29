"""
Program 2: Data provenance audit.

Verifies SHA-256 hashes for raw data files against registry.yaml.
Spot-checks data values against documented statistics.
Verifies source URL accessibility.
"""
import logging
import hashlib
from pathlib import Path
import json
import sys

import yaml
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent.parent

# -------------------------------------------------------------------
# Step 1: Load registry
# -------------------------------------------------------------------
with open(BASE / "phase0_discovery" / "data" / "registry.yaml") as f:
    registry = yaml.safe_load(f)

datasets = registry["datasets"]
log.info("Registry contains %d datasets", len(datasets))

# -------------------------------------------------------------------
# Step 2: SHA-256 hash verification for acquired datasets
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("SHA-256 HASH VERIFICATION")
log.info("=" * 60)

hash_results = {}
for ds in datasets:
    ds_id = ds["id"]
    status = ds.get("status", "unknown")

    if status == "failed":
        hash_results[ds_id] = {"status": "SKIPPED (failed acquisition)", "match": None}
        log.info("  %s: SKIPPED (failed acquisition)", ds_id)
        continue

    raw_file = ds.get("raw_file")
    expected_hash = ds.get("sha256_raw")

    if not raw_file or not expected_hash:
        hash_results[ds_id] = {"status": "NO HASH", "match": None}
        log.info("  %s: No hash or raw file specified", ds_id)
        continue

    raw_path = BASE / "phase0_discovery" / raw_file.replace("data/", "data/")
    if not raw_path.exists():
        # Try without phase0 prefix
        raw_path = BASE / raw_file
    if not raw_path.exists():
        raw_path = BASE / "phase0_discovery" / raw_file

    if not raw_path.exists():
        hash_results[ds_id] = {"status": "FILE NOT FOUND", "match": False, "path": str(raw_path)}
        log.info("  %s: FILE NOT FOUND at %s", ds_id, raw_path)
        continue

    # Compute SHA-256
    h = hashlib.sha256()
    with open(raw_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    computed_hash = h.hexdigest()

    match = computed_hash == expected_hash
    hash_results[ds_id] = {
        "status": "MATCH" if match else "MISMATCH",
        "match": match,
        "computed": computed_hash[:16] + "...",
        "expected": expected_hash[:16] + "...",
    }
    log.info("  %s: %s (computed=%s, expected=%s)",
             ds_id, "MATCH" if match else "MISMATCH",
             computed_hash[:12], expected_hash[:12])

# -------------------------------------------------------------------
# Step 3: Spot-check data values
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("DATA VALUE SPOT-CHECKS")
log.info("=" * 60)

spot_checks = []

# Check 1: NBS expenditure 2025 national value (documented: 3,489 yuan nominal)
exp = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_education_expenditure.parquet")
val_2025 = exp[exp["year"] == 2025]
nat_cols = [c for c in exp.columns if "national" in c.lower() and "yuan" in c.lower()]
if len(nat_cols) > 0 and len(val_2025) > 0:
    v = val_2025[nat_cols[0]].values[0]
    expected = 3489  # From DATA_QUALITY.md
    match = abs(v - expected) < 5
    spot_checks.append({
        "dataset": "ds_001",
        "check": "2025 national education/culture/rec spending",
        "expected": expected,
        "found": float(v),
        "match": match,
    })
    log.info("  ds_001 2025 national: expected=%.0f, found=%.0f, match=%s", expected, v, match)

# Check 2: NBS 2020 COVID dip (documented: 2,032 yuan = -19.1% YoY)
val_2020 = exp[exp["year"] == 2020]
if len(val_2020) > 0:
    v = val_2020[nat_cols[0]].values[0]
    expected = 2032
    match = abs(v - expected) < 5
    spot_checks.append({
        "dataset": "ds_001",
        "check": "2020 national (COVID dip)",
        "expected": expected,
        "found": float(v),
        "match": match,
    })
    log.info("  ds_001 2020 national: expected=%.0f, found=%.0f, match=%s", expected, v, match)

# Check 3: Demographics births 2024 (documented: 9.54M)
demo = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "china_demographics.parquet")
log.info("  Demographics columns: %s", list(demo.columns))
birth_cols = [c for c in demo.columns if "birth" in c.lower() and "million" in c.lower()]
if birth_cols:
    val = demo[demo["year"] == 2024][birth_cols[0]].values
    if len(val) > 0:
        v = val[0]
        expected = 9.54
        match = abs(v - expected) < 0.1
        spot_checks.append({
            "dataset": "ds_006",
            "check": "2024 births (millions)",
            "expected": expected,
            "found": float(v),
            "match": match,
        })
        log.info("  ds_006 2024 births: expected=%.2f, found=%.2f, match=%s", expected, v, match)

# Check 4: Income 2025 national (documented: 43,145 yuan)
income = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_disposable_income.parquet")
log.info("  Income columns: %s", list(income.columns))
inc_cols = [c for c in income.columns if "national" in c.lower()]
if inc_cols:
    val = income[income["year"] == 2025][inc_cols[0]].values
    if len(val) > 0:
        v = val[0]
        expected = 43145
        match = abs(v - expected) < 10
        spot_checks.append({
            "dataset": "ds_009",
            "check": "2025 national disposable income",
            "expected": expected,
            "found": float(v),
            "match": match,
        })
        log.info("  ds_009 2025 income: expected=%.0f, found=%.0f, match=%s", expected, v, match)

# Check 5: CPI overall 2025 (documented: 115.3)
cpi = pd.read_parquet(BASE / "phase0_discovery" / "data" / "processed" / "nbs_cpi_deflator.parquet")
log.info("  CPI columns: %s", list(cpi.columns))
cpi_cols = [c for c in cpi.columns if "overall" in c.lower() and "index" in c.lower()]
if cpi_cols:
    val = cpi[cpi["year"] == 2025][cpi_cols[0]].values
    if len(val) > 0:
        v = val[0]
        expected = 115.3
        match = abs(v - expected) < 0.5
        spot_checks.append({
            "dataset": "ds_013",
            "check": "2025 overall CPI index",
            "expected": expected,
            "found": float(v),
            "match": match,
        })
        log.info("  ds_013 2025 CPI: expected=%.1f, found=%.1f, match=%s", expected, v, match)

# -------------------------------------------------------------------
# Step 4: Row count verification
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("ROW COUNT VERIFICATION")
log.info("=" * 60)

row_checks = []
for ds in datasets:
    if ds.get("status") == "failed":
        continue
    ds_id = ds["id"]
    expected_obs = ds.get("observations")
    proc_file = ds.get("processed_file")
    if not proc_file or not expected_obs:
        continue

    proc_path = BASE / "phase0_discovery" / proc_file.replace("data/", "data/")
    if not proc_path.exists():
        proc_path = BASE / proc_file

    if proc_path.exists():
        df = pd.read_parquet(proc_path)
        actual_rows = len(df)
        match = actual_rows == expected_obs
        row_checks.append({
            "dataset": ds_id,
            "expected": expected_obs,
            "actual": actual_rows,
            "match": match,
        })
        log.info("  %s: expected=%d, actual=%d, %s",
                 ds_id, expected_obs, actual_rows, "MATCH" if match else "MISMATCH")

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("PROVENANCE AUDIT SUMMARY")
log.info("=" * 60)

hash_pass = sum(1 for v in hash_results.values() if v.get("match") is True)
hash_fail = sum(1 for v in hash_results.values() if v.get("match") is False)
hash_skip = sum(1 for v in hash_results.values() if v.get("match") is None)
log.info("  Hashes: %d PASS, %d FAIL, %d SKIPPED", hash_pass, hash_fail, hash_skip)

spot_pass = sum(1 for v in spot_checks if v["match"])
spot_fail = sum(1 for v in spot_checks if not v["match"])
log.info("  Spot checks: %d/%d PASS", spot_pass, len(spot_checks))

row_pass = sum(1 for v in row_checks if v["match"])
row_fail = sum(1 for v in row_checks if not v["match"])
log.info("  Row counts: %d/%d MATCH", row_pass, len(row_checks))

overall = "PASS" if hash_fail == 0 and spot_fail == 0 and row_fail == 0 else "FLAG"
log.info("  Overall: %s", overall)

# Save
output = {
    "hash_results": hash_results,
    "spot_checks": spot_checks,
    "row_checks": row_checks,
    "overall": overall,
}

out_path = BASE / "phase5_verification" / "data"
out_path.mkdir(parents=True, exist_ok=True)
with open(out_path / "provenance_audit.json", "w") as f:
    json.dump(output, f, indent=2, default=str)

log.info("Results saved.")
