"""
Supplementary data acquisition: underground tutoring indicators,
post-policy spending proxies, and crowding-in evidence.

Usage: pixi run py phase0_discovery/scripts/acquire_supplementary.py
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
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

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "data" / "raw"
PROC_DIR = BASE / "data" / "processed"
REGISTRY_PATH = BASE / "data" / "registry.yaml"


def sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f) or {"datasets": []}


def _convert_numpy(obj):
    """Recursively convert numpy types to Python native types for YAML."""
    if isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(v) for v in obj]
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    return obj


def save_registry(reg: dict) -> None:
    reg = _convert_numpy(reg)
    with open(REGISTRY_PATH, "w") as f:
        yaml.dump(reg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def acquire_underground_tutoring():
    """Underground tutoring price and activity data from media reports."""
    log.info("Assembling underground tutoring indicators...")

    price_data = [
        # Pre-ban prices
        {"period": "pre_ban_2021", "metric": "group_class_10_students_per_2hr",
         "value_yuan": 200, "source": "SCMP 2022"},
        {"period": "pre_ban_2021", "metric": "one_on_one_per_hour",
         "value_yuan": 300, "source": "The Star 2024"},
        {"period": "pre_ban_2021", "metric": "group_class_per_hour",
         "value_yuan": 350, "source": "The Star 2024"},
        # Post-ban prices
        {"period": "post_ban_2022", "metric": "one_on_one_secret_per_session",
         "value_yuan": 400, "source": "SCMP 2022 (more than double)"},
        {"period": "post_ban_2023", "metric": "one_on_one_per_hour",
         "value_yuan": 450, "source": "The Star 2024"},
        {"period": "post_ban_2023", "metric": "group_class_10_students_per_hour",
         "value_yuan": 500, "source": "The Star 2024"},
        {"period": "post_ban_2023", "metric": "one_on_one_premium_per_hour",
         "value_yuan": 3000, "source": "RFA 2021 (high-end market)"},
        {"period": "post_ban_2022", "metric": "teacher_earning_per_secret_course",
         "value_yuan": 800, "source": "SCMP 2022"},
        {"period": "pre_ban_2021", "metric": "teacher_earning_institutional_class",
         "value_yuan": 300, "source": "SCMP 2022"},
    ]

    industry_closure = [
        {"date": "2021-07-01", "metric": "offline_tutoring_centers", "value": 124000, "source": "SCMP/The Star"},
        {"date": "2022-02-28", "metric": "offline_tutoring_centers", "value": 9728, "source": "SCMP 2022",
         "note": "92% decline"},
        {"date": "2022-12-31", "metric": "offline_tutoring_centers", "value": 4932, "source": "The Star 2024",
         "note": "96% decline from pre-ban"},
        {"date": "2022-06-30", "metric": "illegal_operations_detected", "value": 3000, "source": "MoE via Sixth Tone"},
        {"date": "2021-07-01", "metric": "industry_size_billion_usd", "value": 120, "source": "The Star 2024"},
    ]

    parent_reports = [
        {"finding": "Policy increased financial burden for some parents",
         "source": "SCMP 2022", "mechanism": "One-on-one sessions replace cheaper group classes"},
        {"finding": "83.5% of students report not taking subject-based tutoring",
         "source": "Beijing Normal University survey", "mechanism": "Self-reported compliance"},
        {"finding": "Tutoring prices doubled on average for those continuing",
         "source": "Multiple media reports 2022-2023", "mechanism": "Scarcity premium + risk premium"},
        {"finding": "Well-performing classmates are all taking private classes",
         "source": "SCMP 2022 parent interview", "mechanism": "Selection into underground market by performance/income"},
        {"finding": "Price increase approximately 43-50% for standard one-on-one",
         "source": "The Star 2024, SCMP 2022", "mechanism": "300->450 yuan/hr confirmed by multiple sources"},
    ]

    raw_data = {
        "price_data": price_data,
        "industry_closure": industry_closure,
        "parent_reports": parent_reports,
    }

    raw_path = RAW_DIR / "underground_tutoring_indicators.json"
    with open(raw_path, "w") as f:
        json.dump(raw_data, f, indent=2, default=str)

    df_prices = pd.DataFrame(price_data)
    proc_path = PROC_DIR / "underground_tutoring_prices.parquet"
    df_prices.to_parquet(proc_path, index=False)

    df_closure = pd.DataFrame(industry_closure)
    proc_path2 = PROC_DIR / "tutoring_center_closures.parquet"
    df_closure.to_parquet(proc_path2, index=False)

    log.info("Underground tutoring: %d price points, %d closure data points",
             len(df_prices), len(df_closure))

    return {
        "name": "Underground Tutoring Price and Activity Indicators",
        "source_url": "https://www.scmp.com/tech/policy/article/3186924/",
        "source_authority": "Multiple media sources (SCMP, The Star, RFA, Bloomberg)",
        "api_endpoint": "N/A - manually extracted from news reports",
        "query_params": {},
        "fetch_date": now_utc(),
        "raw_file": str(raw_path.relative_to(BASE)),
        "processed_file": str(proc_path.relative_to(BASE)),
        "sha256_raw": sha256(raw_path),
        "sha256_processed": sha256(proc_path),
        "variables": [
            {"name": "value_yuan", "description": "Tutoring price per session/hour", "unit": "yuan", "dag_variable": "Underground tutoring price indices"},
            {"name": "value", "description": "Count of tutoring centers / operations", "unit": "count", "dag_variable": "Underground tutoring activity indicators"},
        ],
        "temporal_coverage": {"start": "2021-07-01", "end": "2024-09-01", "frequency": "event_based"},
        "observations": len(df_prices) + len(df_closure),
        "missing_pct": 0.0,
        "license": "News reports (fair use for research)",
        "notes": "Prices from individual cases reported in media -- not systematic survey data. Underground tutoring prices are inherently difficult to measure systematically. These are anecdotal data points that indicate the direction and approximate magnitude of price changes. The 43-50% average increase is corroborated across multiple independent sources. Caution: selection bias in reporting -- extreme cases more likely to be covered.",
        "status": "acquired",
    }


def acquire_crowding_in_evidence():
    """Evidence on public spending crowding-in effect from academic literature."""
    log.info("Assembling crowding-in evidence data...")

    findings = [
        {"study": "ScienceDirect 2025",
         "title": "Does increased public education spending reduce the financial burden on families?",
         "url": "https://www.sciencedirect.com/science/article/abs/pii/S1049007825001848",
         "finding": "Public education expenditure has significant crowding-in effect on family education expenditure in compulsory education",
         "mechanism": "Self-selection and competition mechanisms",
         "effect_primary": "positive_crowding_in",
         "effect_junior_high_gt_primary": True,
         "data_source": "CHIP county-level matched with micro-survey",
         "implication_for_dag3": "Supports DAG 3 -- increased public spending does not reduce household burden"},
        {"study": "Wei 2024 / CIEFR-HS",
         "title": "Household Expenditure on Education in China",
         "url": "https://journals.sagepub.com/doi/10.1177/20965311241243389",
         "finding": "In-school expenses are 73% of total education spending; tutoring is only 12%",
         "mechanism": "Compositional structure of education spending",
         "effect_primary": "scope_limitation",
         "effect_junior_high_gt_primary": None,
         "data_source": "CIEFR-HS 2019",
         "implication_for_dag3": "Supports DAG 3 -- policy targets wrong component"},
        {"study": "Lu 2025",
         "title": "No Less Than 4%: A Policy Review of China's Fiscal Spending on Education, 2000-2020",
         "url": "https://journals.sagepub.com/doi/full/10.1177/20965311241265374",
         "finding": "China has maintained >4% of GDP spending on education since 2012",
         "mechanism": "Policy commitment to education funding",
         "effect_primary": "sustained_public_investment",
         "effect_junior_high_gt_primary": None,
         "data_source": "NBS fiscal data",
         "implication_for_dag3": "Public spending continued to increase during policy period"},
    ]

    raw_path = RAW_DIR / "crowding_in_evidence.json"
    with open(raw_path, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    df = pd.DataFrame(findings)
    proc_path = PROC_DIR / "crowding_in_evidence.parquet"
    df.to_parquet(proc_path, index=False)

    log.info("Crowding-in evidence: %d studies", len(df))

    return {
        "name": "Crowding-In Effect Evidence (Academic Literature)",
        "source_url": "https://www.sciencedirect.com/science/article/abs/pii/S1049007825001848",
        "source_authority": "Peer-reviewed academic papers",
        "api_endpoint": "N/A",
        "query_params": {},
        "fetch_date": now_utc(),
        "raw_file": str(raw_path.relative_to(BASE)),
        "processed_file": str(proc_path.relative_to(BASE)),
        "sha256_raw": sha256(raw_path),
        "sha256_processed": sha256(proc_path),
        "variables": [
            {"name": "finding", "description": "Key empirical finding", "unit": "text", "dag_variable": "Crowding-in effect (DAG 3)"},
            {"name": "effect_primary", "description": "Direction of effect", "unit": "categorical", "dag_variable": "Public education expenditure effect"},
        ],
        "temporal_coverage": {"start": "2019-01-01", "end": "2025-01-01", "frequency": "study_publication"},
        "observations": len(df),
        "missing_pct": 0.0,
        "license": "Academic publications (citation use)",
        "notes": "Qualitative evidence compilation from peer-reviewed literature. These studies provide the empirical basis for DAG 3's crowding-in mechanism. The ScienceDirect 2025 finding is particularly important as it uses CHIP data with county-level matching.",
        "status": "acquired",
    }


def record_failed_acquisitions():
    """Document variables that could not be acquired as structured data."""
    log.info("Recording failed/unavailable data acquisitions...")

    failed = [
        {
            "name": "CFPS Microdata (Post-2021)",
            "source_url": "https://www.isss.pku.edu.cn/cfps/en/",
            "source_authority": "Peking University ISSS",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "household_education_expenditure_post_2021", "dag_variable": "Total household education expenditure"},
            ],
            "notes": "CFPS microdata requires formal application through Peking University ISSS. The 2020 wave is the latest publicly accessible. Post-2021 waves (which would capture Double Reduction effects) are not yet publicly available. This is a CRITICAL data gap -- no household-level microdata exists in the public domain for the post-policy period.",
        },
        {
            "name": "CIEFR-HS Wave 3 (2021-2022) Microdata",
            "source_url": "https://opendata.pku.edu.cn/dataverse/ciefrhs",
            "source_authority": "CIEFR, Peking University",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "post_policy_education_spending_decomposition", "dag_variable": "Off-campus tutoring expenditure / In-school fees"},
            ],
            "notes": "The 3rd CIEFR-HS wave was conducted in 2021-2022 (post-policy), but results have not yet been published. When available, this will be the most important dataset for testing all three DAGs, as it provides spending decomposition before and after the policy.",
        },
        {
            "name": "Underground Tutoring Systematic Survey",
            "source_url": "N/A",
            "source_authority": "N/A",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "underground_tutoring_participation_rate", "dag_variable": "Underground tutoring activity indicators"},
                {"name": "underground_tutoring_total_spending", "dag_variable": "Underground tutoring price indices"},
            ],
            "notes": "No systematic survey of underground tutoring activity exists. By definition, underground market activity is difficult to measure. Available data comes from enforcement reports (supply-side detection) and anecdotal media reports. The Ministry of Education's ~3,000 illegal operations detected in Q2 2022 is a lower bound. This is the SINGLE LARGEST data challenge for testing DAG 2.",
        },
        {
            "name": "Regional Enforcement Intensity Index",
            "source_url": "N/A",
            "source_authority": "N/A",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "enforcement_intensity_by_province", "dag_variable": "Policy enforcement intensity by locality"},
            ],
            "notes": "No standardized enforcement intensity index exists across provinces. Some academic papers have constructed indices from policy documents and media reports, but no publicly available dataset provides this. This limits the ability to exploit enforcement variation for identification.",
        },
        {
            "name": "Non-Academic Enrichment Spending Time Series",
            "source_url": "N/A",
            "source_authority": "N/A",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "non_academic_enrichment_spending", "dag_variable": "Non-academic enrichment spending"},
            ],
            "notes": "No public time series tracks non-academic enrichment spending (arts, sports, STEM camps) separately from academic tutoring. The CIEFR-HS interest-oriented tutoring data (Table 6) provides a 2019 snapshot but no post-policy comparison. Media reports suggest growth in this category but no quantification exists.",
        },
        {
            "name": "Parental Anxiety / Subjective Burden Index",
            "source_url": "N/A",
            "source_authority": "N/A",
            "fetch_date": now_utc(),
            "raw_file": "N/A",
            "processed_file": "N/A",
            "status": "failed",
            "variables": [
                {"name": "parental_anxiety_index", "dag_variable": "Parental anxiety indices"},
            ],
            "notes": "No public standardized index exists. Some academic surveys (e.g., PMC 2022 study on education anxiety) provide cross-sectional data but no pre-post comparison with the same instrument. Beijing Normal University survey (83.5% not taking tutoring) provides one data point but is self-reported compliance, not anxiety measurement.",
        },
    ]

    return failed


def main():
    log.info("=" * 60)
    log.info("SUPPLEMENTARY DATA ACQUISITION")
    log.info("=" * 60)

    registry = load_registry()

    # Acquire available data
    for name, func in [
        ("Underground Tutoring", acquire_underground_tutoring),
        ("Crowding-In Evidence", acquire_crowding_in_evidence),
    ]:
        log.info("Acquiring: %s", name)
        try:
            result = func()
            if result:
                registry["datasets"].append(result)
                log.info("SUCCESS: %s", name)
        except Exception as e:
            log.error("FAILED: %s - %s", name, e)

    # Record failed acquisitions
    failed = record_failed_acquisitions()
    for entry in failed:
        registry["datasets"].append(entry)
        log.info("RECORDED FAILED: %s", entry["name"])

    save_registry(registry)

    log.info("=" * 60)
    log.info("SUPPLEMENTARY ACQUISITION COMPLETE")
    log.info("Total datasets in registry: %d", len(registry["datasets"]))
    log.info("=" * 60)


if __name__ == "__main__":
    main()
