# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Structured data extraction from unstructured sources for OpenPE.

Extracts numerical values from text, tables from PDFs, and builds
structured datasets with confidence labeling and source traceability.

Confidence levels:
  - "exact": number appears literally in the source
  - "estimated": prefixed with "about", "approximately", "~", or inferred
  - "interpolated": computed from surrounding data points
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class ExtractedValue:
    """A single extracted data point with provenance and confidence."""

    value: float
    unit: str = ""
    context: str = ""
    source_url: str = ""
    source_location: str = ""
    confidence: str = "estimated"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "unit": self.unit,
            "context": self.context,
            "source_url": self.source_url,
            "source_location": self.source_location,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


_NUMBER_PATTERN = re.compile(
    r"(?P<prefix>(?:about|approximately|roughly|around|nearly|~|circa|estimated)\s+)?"
    r"(?P<number>\d[\d,]*\.?\d*)"
    r"(?P<suffix>\s*(?:%|percent|billion|million|thousand|pp|percentage points)?)",
    re.IGNORECASE,
)


def extract_numbers_from_text(
    text: str,
    source_url: str = "",
    source_location: str = "",
) -> list[ExtractedValue]:
    """Extract numerical values from unstructured text with confidence labels."""
    results = []
    for match in _NUMBER_PATTERN.finditer(text):
        raw_number = match.group("number").replace(",", "")
        try:
            value = float(raw_number)
        except ValueError:
            continue

        prefix = match.group("prefix")
        confidence = "estimated" if prefix else "exact"

        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 80)
        context = text[start:end].strip()

        suffix = (match.group("suffix") or "").strip().lower()
        unit = suffix if suffix else ""

        results.append(ExtractedValue(
            value=value,
            unit=unit,
            context=context,
            source_url=source_url,
            source_location=source_location,
            confidence=confidence,
        ))
    return results


def extract_table_from_csv_text(csv_text: str) -> pd.DataFrame:
    """Parse a CSV-formatted text block into a DataFrame."""
    return pd.read_csv(io.StringIO(csv_text.strip()))


def extract_tables_from_pdf(
    pdf_path: Path,
    pages: list[int] | None = None,
) -> list[pd.DataFrame]:
    """Extract tables from a PDF file using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return []

    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        target_pages = pages if pages else range(len(pdf.pages))
        for page_num in target_pages:
            if page_num >= len(pdf.pages):
                continue
            page = pdf.pages[page_num]
            for table in page.extract_tables():
                if table and len(table) > 1:
                    header = table[0]
                    rows = table[1:]
                    df = pd.DataFrame(rows, columns=header)
                    tables.append(df)
    return tables


def build_dataset_from_extractions(
    extractions: list[ExtractedValue],
    key_field: str = "year",
) -> pd.DataFrame:
    """Build a structured DataFrame from a list of ExtractedValues."""
    records = []
    for ev in extractions:
        row = {
            "value": ev.value,
            "unit": ev.unit,
            "confidence": ev.confidence,
            "source_url": ev.source_url,
            "source_location": ev.source_location,
        }
        row.update(ev.metadata)
        records.append(row)
    return pd.DataFrame(records)
