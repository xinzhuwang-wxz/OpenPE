"""
Extract detailed data tables from CIEFR-HS Wei (2024) paper.
These are manually transcribed from the PDF tables visible in the paper.

Usage: pixi run py phase0_discovery/scripts/extract_ciefr_tables.py
"""

import hashlib
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
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


def sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_table4():
    """Table 4: Household expenditure per student by level of education (2019 CIEFR-HS)."""
    log.info("Extracting Table 4: Expenditure by education level")

    rows = [
        {"area": "National", "kindergarten_yuan": 7402, "kindergarten_pct": 8.9,
         "elementary_yuan": 4014, "elementary_pct": 4.3,
         "junior_high_yuan": 6103, "junior_high_pct": 8.0,
         "senior_high_yuan": 10156, "senior_high_pct": 14.1,
         "vocational_high_yuan": 6873, "vocational_high_pct": 14.8,
         "higher_education_yuan": 22370, "higher_education_pct": 31.6},
        {"area": "Rural", "kindergarten_yuan": 4195, "kindergarten_pct": 8.5,
         "elementary_yuan": 1905, "elementary_pct": 3.7,
         "junior_high_yuan": 3820, "junior_high_pct": 7.9,
         "senior_high_yuan": 7771, "senior_high_pct": 15.2,
         "vocational_high_yuan": 7517, "vocational_high_pct": 18.5,
         "higher_education_yuan": 20397, "higher_education_pct": 35.9},
        {"area": "Urban", "kindergarten_yuan": 10511, "kindergarten_pct": 9.3,
         "elementary_yuan": 6578, "elementary_pct": 5.1,
         "junior_high_yuan": 9199, "junior_high_pct": 8.1,
         "senior_high_yuan": 12347, "senior_high_pct": 13.0,
         "vocational_high_yuan": 6038, "vocational_high_pct": 10.0,
         "higher_education_yuan": 23918, "higher_education_pct": 28.3},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_expenditure_by_level_detailed.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_table5():
    """Table 5: Subject-oriented tutoring participation and expenditure by area."""
    log.info("Extracting Table 5: Subject tutoring participation")

    # Top half: participation rates (%)
    # Bottom half: average expenditure (yuan)
    rows = [
        # Participation rates
        {"level": "Elementary", "metric": "participation_rate_pct",
         "total": 25.3, "urban": 32.4, "rural": 14.9,
         "first_tier": 44.1, "second_tier": 36.5, "county_towns": 20.8},
        {"level": "Junior_High", "metric": "participation_rate_pct",
         "total": 27.8, "urban": 36.5, "rural": 16.0,
         "first_tier": 57.3, "second_tier": 36.0, "county_towns": 22.8},
        {"level": "Senior_High", "metric": "participation_rate_pct",
         "total": 18.1, "urban": 23.2, "rural": 9.0,
         "first_tier": 39.6, "second_tier": 25.7, "county_towns": 16.0},
        {"level": "Total", "metric": "participation_rate_pct",
         "total": 24.4, "urban": 31.4, "rural": 14.1,
         "first_tier": 46.2, "second_tier": 34.0, "county_towns": 20.1},
        # Average expenditure (yuan, among participants)
        {"level": "Elementary", "metric": "avg_expenditure_yuan",
         "total": 6580, "urban": 7811, "rural": 2702,
         "first_tier": 18125, "second_tier": 7658, "county_towns": 2895},
        {"level": "Junior_High", "metric": "avg_expenditure_yuan",
         "total": 9887, "urban": 11772, "rural": 4167,
         "first_tier": 21748, "second_tier": 13318, "county_towns": 5012},
        {"level": "Senior_High", "metric": "avg_expenditure_yuan",
         "total": 12208, "urban": 13628, "rural": 6064,
         "first_tier": 28602, "second_tier": 13398, "county_towns": 8021},
        {"level": "Total", "metric": "avg_expenditure_yuan",
         "total": 8438, "urban": 9926, "rural": 3581,
         "first_tier": 20881, "second_tier": 10169, "county_towns": 4495},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_subject_tutoring_by_area.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_table6():
    """Table 6: Interest-oriented tutoring participation and expenditure by area."""
    log.info("Extracting Table 6: Interest tutoring participation")

    rows = [
        # Participation rates
        {"level": "Elementary", "metric": "participation_rate_pct",
         "total": 22.3, "urban": 32.5, "rural": 7.4,
         "first_tier": 47.5, "second_tier": 31.6, "county_towns": 21.3},
        {"level": "Junior_High", "metric": "participation_rate_pct",
         "total": 9.6, "urban": 14.5, "rural": 2.9,
         "first_tier": 24.0, "second_tier": 12.2, "county_towns": 10.3},
        {"level": "Senior_High", "metric": "participation_rate_pct",
         "total": 5.8, "urban": 6.7, "rural": 4.1,
         "first_tier": 10.1, "second_tier": 5.4, "county_towns": 7.4},
        {"level": "Total", "metric": "participation_rate_pct",
         "total": 15.5, "urban": 22.2, "rural": 5.5,
         "first_tier": 34.9, "second_tier": 20.8, "county_towns": 15.2},
        # Average expenditure (yuan)
        {"level": "Elementary", "metric": "avg_expenditure_yuan",
         "total": 5265, "urban": 5776, "rural": 1730,
         "first_tier": 10693, "second_tier": 5530, "county_towns": 2931},
        {"level": "Junior_High", "metric": "avg_expenditure_yuan",
         "total": 3808, "urban": 4122, "rural": 1833,
         "first_tier": 7097, "second_tier": 4624, "county_towns": 2026},
        {"level": "Senior_High", "metric": "avg_expenditure_yuan",
         "total": 9307, "urban": 7391, "rural": 9385,
         "first_tier": 11222, "second_tier": 12813, "county_towns": 2059},
        {"level": "Total", "metric": "avg_expenditure_yuan",
         "total": 5340, "urban": 5612, "rural": 3657,
         "first_tier": 10170, "second_tier": 5809, "county_towns": 2668},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_interest_tutoring_by_area.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_table7():
    """Table 7: Compulsory education expenditure comparison 2017 vs 2019."""
    log.info("Extracting Table 7: 2017 vs 2019 compulsory education spending")

    rows = [
        # AY 2016-2017
        {"academic_year": "2016-2017", "level": "Elementary",
         "total_expenditure_national": 6562, "total_expenditure_rural": 2625, "total_expenditure_urban": 8609,
         "in_school_expenditure_national": 3999, "in_school_expenditure_rural": 2214, "in_school_expenditure_urban": 4928,
         "out_of_school_expenditure_national": 5456, "out_of_school_expenditure_rural": 1724, "out_of_school_expenditure_urban": 6246,
         "education_pct_of_total_expenditure_national": 10.1, "education_pct_of_total_expenditure_rural": 7.1, "education_pct_of_total_expenditure_urban": 11.6},
        {"academic_year": "2016-2017", "level": "Junior_High",
         "total_expenditure_national": 8995, "total_expenditure_rural": 4387, "total_expenditure_urban": 11021,
         "in_school_expenditure_national": 6170, "in_school_expenditure_rural": 3931, "in_school_expenditure_urban": 7154,
         "out_of_school_expenditure_national": 5951, "out_of_school_expenditure_rural": 1729, "out_of_school_expenditure_urban": 6762,
         "education_pct_of_total_expenditure_national": 14.9, "education_pct_of_total_expenditure_rural": 13.2, "education_pct_of_total_expenditure_urban": 15.7},
        # AY 2018-2019
        {"academic_year": "2018-2019", "level": "Elementary",
         "total_expenditure_national": 4014, "total_expenditure_rural": 1905, "total_expenditure_urban": 6579,
         "in_school_expenditure_national": 1679, "in_school_expenditure_rural": 1423, "in_school_expenditure_urban": 1990,
         "out_of_school_expenditure_national": 6731, "out_of_school_expenditure_rural": 2449, "out_of_school_expenditure_urban": 8798,
         "education_pct_of_total_expenditure_national": 4.3, "education_pct_of_total_expenditure_rural": 3.7, "education_pct_of_total_expenditure_urban": 5.1},
        {"academic_year": "2018-2019", "level": "Junior_High",
         "total_expenditure_national": 6103, "total_expenditure_rural": 3821, "total_expenditure_urban": 9199,
         "in_school_expenditure_national": 3430, "in_school_expenditure_rural": 3078, "in_school_expenditure_urban": 3907,
         "out_of_school_expenditure_national": 9145, "out_of_school_expenditure_rural": 3960, "out_of_school_expenditure_urban": 12312,
         "education_pct_of_total_expenditure_national": 8.0, "education_pct_of_total_expenditure_rural": 7.9, "education_pct_of_total_expenditure_urban": 8.1},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_compulsory_education_2017_vs_2019.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_table8():
    """Table 8: Out-of-school tutoring 2017 vs 2019 comparison (CRITICAL for pre-policy trend)."""
    log.info("Extracting Table 8: Tutoring participation 2017 vs 2019")

    rows = [
        {"metric": "household_expenditure_per_student",
         "full_sample_2017": 10372, "full_sample_2019": 6090,
         "followup_sample_2017": 7553, "followup_sample_2019": 6504},
        {"metric": "subject_tutoring_participation_pct",
         "full_sample_2017": 38.0, "full_sample_2019": 24.4,
         "followup_sample_2017": 34.0, "followup_sample_2019": 26.8},
        {"metric": "interest_tutoring_participation_pct",
         "full_sample_2017": 21.0, "full_sample_2019": 15.5,
         "followup_sample_2017": 18.8, "followup_sample_2019": 14.1},
        {"metric": "subject_tutoring_expenditure_yuan",
         "full_sample_2017": 6139, "full_sample_2019": 8438,
         "followup_sample_2017": 6504, "followup_sample_2019": 9757},
        {"metric": "interest_tutoring_expenditure_yuan",
         "full_sample_2017": 4105, "full_sample_2019": 5340,
         "followup_sample_2017": 4467, "followup_sample_2019": 5583},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_tutoring_2017_vs_2019.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_figure4_data():
    """Figure 4: Government vs household spending by income quintile (2019, compulsory education)."""
    log.info("Extracting Figure 4: Spending by income quintile")

    # Values approximate from the stacked bar chart + line
    rows = [
        {"income_quintile": "Lowest_20pct", "govt_budgetary_per_student_yuan": 14000,
         "household_per_student_yuan": 3000, "govt_share_pct": 92.9},
        {"income_quintile": "Second_lowest_20pct", "govt_budgetary_per_student_yuan": 13500,
         "household_per_student_yuan": 5000, "govt_share_pct": 88.8},
        {"income_quintile": "Middle_20pct", "govt_budgetary_per_student_yuan": 13000,
         "household_per_student_yuan": 7000, "govt_share_pct": 85.6},
        {"income_quintile": "Second_highest_20pct", "govt_budgetary_per_student_yuan": 14000,
         "household_per_student_yuan": 10000, "govt_share_pct": 80.0},
        {"income_quintile": "Highest_20pct", "govt_budgetary_per_student_yuan": 15000,
         "household_per_student_yuan": 25000, "govt_share_pct": 64.7},
    ]
    df = pd.DataFrame(rows)
    path = PROC_DIR / "ciefr_spending_by_income_quintile.parquet"
    df.to_parquet(path, index=False)
    log.info("  Saved %d rows to %s", len(df), path.name)
    return df


def extract_key_statistics():
    """Key statistics mentioned throughout the paper text."""
    log.info("Extracting key statistics from paper text")

    stats = {
        "source": "Wei (2024) CIEFR-HS, ECNU Review of Education 7(3) 738-761",
        "survey_year": 2019,
        "key_findings": {
            "avg_expenditure_all_regular_fulltime_yuan": 8139,
            "avg_expenditure_all_regular_fulltime_pct_of_total_hh_expenditure": 10.8,
            "avg_total_expenditure_ay2018_2019_yuan": 11297,
            "education_pct_of_disposable_income_national": 40,
            "education_pct_of_disposable_income_rural": 56.1,
            "education_pct_of_disposable_income_urban": 36.2,
            "education_pct_of_hh_expenditure_national": 14.9,
            "education_pct_of_hh_expenditure_rural": 15.8,
            "education_pct_of_hh_expenditure_urban": 14.1,
            "education_per_student_pct_of_disposable_income_national": 28.8,
            "education_per_student_pct_of_disposable_income_rural": 37.5,
            "education_per_student_pct_of_disposable_income_urban": 28.1,
            "total_hh_expenditure_on_education_billion_yuan": 2163.2,
            "total_hh_expenditure_on_education_pct_of_gdp": 2.4,
            "total_investment_regular_education_billion_yuan": 6187.9,
            "total_investment_regular_education_pct_of_gdp": 6.87,
            "lifetime_education_cost_preschool_to_undergrad_yuan": 233000,
            "lifetime_cost_bottom_20pct_yuan": 180000,
            "lifetime_cost_middle_20pct_yuan": 224000,
            "lifetime_cost_top_20pct_yuan": 424000,
            "urban_expenditure_per_child_yuan": 14197,
            "rural_expenditure_per_child_yuan": 8205,
            "urban_spending_multiple_of_rural": 2.0,
            "fiscal_education_spending_2018_billion_yuan": 3699.6,
            "fiscal_education_spending_2018_pct_gdp": 4.11,
            "non_govt_funding_2018_billion_yuan": 914.7,
            "non_govt_funding_2018_pct_gdp": 1.02,
            "subject_tutoring_participation_rate_pct": 24.4,
            "interest_tutoring_participation_rate_pct": 15.5,
            "tutoring_provider_commercial_org_pct": 26.6,
            "tutoring_provider_individual_pct": 70.0,
            "after_school_care_offered_by_schools_pct": 36.0,
            "actual_after_school_care_provision_pct": 6.0,
            "after_school_care_expenditure_yuan": 1018,
            "kindergarten_gross_enrollment_rate_pct": 83.6,
            "senior_high_gross_enrollment_rate_pct": 89.1,
            "private_kindergarten_pct": 58.2,
            "private_elementary_pct": 10.1,
            "private_junior_high_pct": 12.9,
            "private_senior_high_pct": 12.8,
        },
        "pre_policy_trends_2017_to_2019": {
            "total_expenditure_declined": True,
            "subject_tutoring_participation_declined_38_to_24pct": True,
            "per_participant_tutoring_spending_increased_6139_to_8438": True,
            "note": "Even before Double Reduction, total education spending was declining while per-participant tutoring costs were rising. This suggests the 2017-2019 trend already showed declining participation but increasing unit costs -- a pattern that the Double Reduction policy would likely accelerate."
        }
    }

    raw_path = RAW_DIR / "ciefr_hs_detailed_statistics.json"
    with open(raw_path, "w") as f:
        json.dump(stats, f, indent=2, default=str)

    log.info("  Saved key statistics to %s", raw_path.name)
    return raw_path


def main():
    log.info("=" * 60)
    log.info("CIEFR-HS Data Table Extraction")
    log.info("=" * 60)

    extract_table4()
    extract_table5()
    extract_table6()
    extract_table7()
    extract_table8()
    extract_figure4_data()
    extract_key_statistics()

    log.info("=" * 60)
    log.info("Extraction complete. 6 parquet files + 1 JSON created.")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
