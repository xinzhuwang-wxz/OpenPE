# Sprint 7B: Data Capabilities Enhancement

> **Execution order:** Plans 7A → 7B → 7C → 7D (sequential, not parallel) due to shared file modifications in pixi.toml and root_claude.md.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance data acquisition with structured extraction from unstructured sources, mid-analysis data callback mechanism, and more persistent data sourcing strategies.

**Architecture:** New `data_extractor.py` module in `src/templates/scripts/` for PDF/web extraction with confidence labeling. Data callback protocol added to Phase 0 and root CLAUDE.md templates. Extraction confidence field added to `registry.yaml` schema.

**Tech Stack:** Python 3.11+, pdfplumber, pandas, PyYAML, pytest

**Issues addressed:** I7 (hardcoded extraction), I8 (gave up too quickly), O1 (extraction pipeline), O2 (data callback), O6 (more aggressive search)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/templates/scripts/data_extractor.py` | Create | PDF table extraction, web number extraction with confidence labels |
| `src/templates/pixi.toml` | Modify | Add `pdfplumber` dependency |
| `src/templates/phase0_claude.md` | Modify | Add data callback protocol, multi-strategy search, extraction confidence |
| `src/templates/root_claude.md` | Modify | Add data callback orchestrator instructions |
| `tests/test_data_extractor.py` | Create | Tests for extraction module |

---

### Task 1: Data Extractor Module

**Files:**
- Create: `src/templates/scripts/data_extractor.py`
- Create: `tests/test_data_extractor.py`
- Modify: `src/templates/pixi.toml` (add pdfplumber)

Fixes: I7, O1

- [ ] **Step 1: Add pdfplumber to pixi.toml**

In `src/templates/pixi.toml` under `[pypi-dependencies]`, add:

```toml
pdfplumber = ">=0.10"    # PDF table extraction
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_data_extractor.py
"""Tests for data_extractor.py — structured data extraction from unstructured sources."""
import shutil
from pathlib import Path

import pandas as pd

from data_extractor import (
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
    assert any(r.confidence == "estimated" for r in results)  # "about 72%"


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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_data_extractor.py -v`
Expected: FAIL

- [ ] **Step 4: Implement data_extractor.py**

```python
# src/templates/scripts/data_extractor.py
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
    confidence: str = "estimated"  # "exact" | "estimated" | "interpolated"
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


# Patterns that indicate estimated (not exact) values
_ESTIMATE_PREFIXES = re.compile(
    r"(?:about|approximately|roughly|around|nearly|~|circa|estimated)\s+",
    re.IGNORECASE,
)

# Pattern to extract numbers with optional % or unit suffix
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
    """Extract numerical values from unstructured text with confidence labels.

    Values preceded by "about", "approximately", "~" etc. are labeled
    as "estimated". All others are labeled as "exact".
    """
    results = []
    for match in _NUMBER_PATTERN.finditer(text):
        raw_number = match.group("number").replace(",", "")
        try:
            value = float(raw_number)
        except ValueError:
            continue

        # Determine confidence based on prefix
        prefix = match.group("prefix")
        confidence = "estimated" if prefix else "exact"

        # Extract context (surrounding sentence)
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 80)
        context = text[start:end].strip()

        # Determine unit from suffix
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
    """Extract tables from a PDF file using pdfplumber.

    Returns a list of DataFrames, one per detected table.
    Falls back to empty list if pdfplumber is unavailable.
    """
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
    """Build a structured DataFrame from a list of ExtractedValues.

    Each extraction becomes a row with value, confidence, source, and
    any metadata fields.
    """
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_data_extractor.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add src/templates/scripts/data_extractor.py src/templates/pixi.toml tests/test_data_extractor.py
git commit -m "feat(sprint7b): add data_extractor module with confidence labeling

Fixes I7, O1 — extracts numbers from text with exact/estimated labels,
tables from PDFs via pdfplumber, builds structured datasets with provenance."
```

---

### Task 2: Data Callback Protocol in Templates

**Files:**
- Modify: `src/templates/phase0_claude.md`
- Modify: `src/templates/root_claude.md`

Fixes: O2, O6, I8

- [ ] **Step 1: Add data callback protocol to phase0_claude.md**

After the "Handle failures gracefully" table (around line 272), add:

```markdown
### Data Callback Protocol

Later phases (especially Phase 3) may discover they need additional data
not anticipated during initial acquisition. The orchestrator can invoke a
**data callback** — a re-run of Steps 0.3-0.5 for specific variables.

**Callback triggers (orchestrator decides):**
- A causal edge with EP > 0.30 cannot be tested due to missing data
- Phase 2 EDA reveals a confounding variable not in the original DAGs
- A reviewer flags a data gap as Category A

**Callback guards (prevent infinite loops):**
- Maximum 2 callbacks per analysis (hard cap)
- Each callback must justify: what new data is needed, which DAG edge it
  supports, and why Phase 0 didn't acquire it
- Re-acquired data goes through the same quality gate (Step 0.5)
- Callback data is appended to `registry.yaml`, never overwrites existing

**Multi-strategy search (before declaring "no data found"):**
When a required variable cannot be found through the primary source, the
data acquisition agent MUST try these fallback strategies in order:

1. **Alternative APIs:** World Bank, FRED, OECD, UN, IMF, national stats
2. **Proxy variables:** Find a measurable proxy for the unmeasurable concept
3. **Academic datasets:** Search data repositories (Harvard Dataverse, Zenodo, Kaggle)
4. **Report extraction:** Use `scripts/data_extractor.py` to extract numbers
   from PDF/web reports with confidence labeling
5. **Composite indicators:** Construct from available sub-components

Only after exhausting all 5 strategies may the agent declare "no data found."
Document each failed strategy in the experiment log.
```

- [ ] **Step 2: Add callback instructions to root_claude.md orchestrator protocol**

In the orchestrator loop section of `src/templates/root_claude.md`, after the Phase 3 context splitting paragraph, add:

```markdown
**Data callbacks.** If Phase 2 or 3 agents report that a high-EP edge
(EP > 0.30) cannot be tested due to missing data, the orchestrator MAY
invoke a data callback:

1. Spawn `data_acquisition_agent` with the specific variable request
2. The agent runs Steps 0.3-0.4 for the requested variable only
3. Spawn `data_quality_agent` for the new data (Step 0.5)
4. Append results to `phase0_discovery/data/registry.yaml`
5. Resume the requesting phase with the new data available

**Guards:** Maximum 2 callbacks per analysis. Each callback gets logged
in `experiment_log.md` with justification. If 2 callbacks have already
been used, log the data gap as a limitation instead.
```

- [ ] **Step 3: Commit**

```bash
git add src/templates/phase0_claude.md src/templates/root_claude.md
git commit -m "docs(sprint7b): add data callback protocol + multi-strategy search

Fixes O2, O6, I8 — orchestrator can re-invoke data acquisition
for high-EP edges (max 2 callbacks). Data agents must try 5
fallback strategies before declaring no data found."
```

---

## Verification

```bash
cd /Users/bamboo/Githubs/OpenPE
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_data_extractor.py -v
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v  # full suite
```
