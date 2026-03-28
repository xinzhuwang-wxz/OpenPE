"""Tests for data_extractor.py — structured data extraction from unstructured sources."""
import shutil
from pathlib import Path

import pandas as pd

from src.templates.scripts.data_extractor import (
    ExtractedValue,
    extract_numbers_from_text,
    extract_table_from_csv_text,
    build_dataset_from_extractions,
)

TMP = Path("/tmp/test_data_extractor")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_extracted_value_fields():
    v = ExtractedValue(
        value=52.3,
        unit="percent",
        context="52.3% of adults trust AI",
        source_url="https://example.com/report",
        source_location="page 7, paragraph 2",
        confidence="exact",
    )
    assert v.value == 52.3
    assert v.confidence in ("exact", "estimated", "interpolated")
    d = v.to_dict()
    assert d["confidence"] == "exact"
    assert d["source_location"] == "page 7, paragraph 2"


def test_extract_numbers_from_text():
    text = """
    According to the report, smartphone penetration reached 78.4% globally in 2024,
    up from about 72% in 2023. The market is valued at approximately $500 billion.
    """
    results = extract_numbers_from_text(text)
    values = [r.value for r in results]
    assert 78.4 in values
    assert any(r.confidence == "exact" for r in results)
    assert any(r.confidence == "estimated" for r in results)


def test_extract_table_from_csv_text():
    csv_text = """Year,Penetration,Users_Millions
2020,45.2,3500
2021,51.1,4000
2022,58.3,4500"""
    df = extract_table_from_csv_text(csv_text)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "Year" in df.columns


def test_build_dataset_from_extractions():
    extractions = [
        ExtractedValue(value=45.2, unit="percent", context="2020 penetration",
                       source_url="https://example.com", confidence="exact",
                       metadata={"year": 2020, "variable": "penetration"}),
        ExtractedValue(value=51.1, unit="percent", context="2021 penetration",
                       source_url="https://example.com", confidence="exact",
                       metadata={"year": 2021, "variable": "penetration"}),
    ]
    df = build_dataset_from_extractions(extractions, key_field="year")
    assert len(df) == 2
    assert "value" in df.columns
    assert "confidence" in df.columns
