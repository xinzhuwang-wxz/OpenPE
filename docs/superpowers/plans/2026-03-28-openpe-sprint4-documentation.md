# OpenPE Sprint 4: Documentation + Review Runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build report generation, audit trail, and review orchestration utilities. After Sprint 4, the full Phase 0→6 pipeline has runtime support.

**Architecture:** Python modules in `src/templates/scripts/` copied into scaffolded analyses. The report generator collects artifacts from all 7 phase directories into a unified REPORT.md. The audit trail produces machine-readable YAML files linking claims to sources and methodology choices.

**Tech Stack:** Python 3.11+, pyyaml (serialization), pathlib (file I/O)

**Spec:** `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` — Sections 3.2 Phase 6 (Documentation), 5.4 (artifact structure)

---

## File Map

### Files to Create
- `src/templates/scripts/report_generator.py` — Report assembly from phase artifacts
- `src/templates/scripts/audit_trail.py` — Claims provenance and methodology audit
- `tests/test_report_generator.py` — Report generator unit tests
- `tests/test_audit_trail.py` — Audit trail unit tests
- `tests/test_sprint4_integration.py` — End-to-end integration test

---

## Task 1: Report Generator

**Files:**
- Create: `src/templates/scripts/report_generator.py`
- Create: `tests/test_report_generator.py`

Assembles REPORT.md from phase artifacts following the spec's 6-section structure.

- [ ] **Step 1: Write tests**

Create `tests/test_report_generator.py`:

```python
"""Tests for report generation."""
import pytest
from pathlib import Path
from src.templates.scripts.report_generator import ReportBuilder, ReportSection


def test_render_empty_report():
    builder = ReportBuilder(analysis_name="Test", question="Is X true?")
    md = builder.render()
    assert "# Test" in md
    assert "Executive Summary" in md


def test_add_sections():
    builder = ReportBuilder(analysis_name="Test")
    builder.add_section("Findings", "X causes Y with high confidence.")
    builder.add_section("Methods", "Used DoWhy propensity score matching.")
    assert len(builder.sections) == 2
    md = builder.render()
    assert "Findings" in md
    assert "Methods" in md


def test_collect_from_phases(tmp_path):
    """Create mock phase dirs and verify collection."""
    disc_dir = tmp_path / "phase0_discovery" / "exec"
    disc_dir.mkdir(parents=True)
    (disc_dir / "DISCOVERY.md").write_text("## Principles\n\nFirst principles identified.")

    strat_dir = tmp_path / "phase1_strategy" / "exec"
    strat_dir.mkdir(parents=True)
    (strat_dir / "STRATEGY.md").write_text("## Strategy\n\nUse DoWhy.")

    builder = ReportBuilder(analysis_name="Test", question="Why?")
    builder.collect_from_phases(tmp_path)
    assert len(builder.sections) >= 2


def test_save_report(tmp_path):
    builder = ReportBuilder(analysis_name="Test")
    builder.add_section("Results", "All good.")
    path = builder.save(tmp_path / "REPORT.md")
    assert path.exists()
    assert path.read_text().startswith("# Test")


def test_to_dict():
    builder = ReportBuilder(analysis_name="Test", question="Q?")
    builder.add_section("S1", "content")
    d = builder.to_dict()
    assert d["analysis_name"] == "Test"
    assert len(d["sections"]) == 1


def test_missing_artifacts_handled(tmp_path):
    """collect_from_phases doesn't crash on missing dirs."""
    builder = ReportBuilder(analysis_name="Test")
    builder.collect_from_phases(tmp_path)
    assert len(builder.sections) == 0
```

- [ ] **Step 2: Implement report_generator.py**

Create `src/templates/scripts/report_generator.py` with:

**Data structures:**
- `ReportSection`: dataclass with `title`, `content`, `level` (heading depth, default 2)
- `ReportBuilder`: dataclass with `analysis_name`, `question`, `sections` list

**Methods on ReportBuilder:**
- `add_section(title, content, level)` — append a section
- `collect_from_phases(analysis_dir)` — scan phase directories for artifacts:
  - `phase0_discovery/exec/DISCOVERY.md` → "First Principles Identified"
  - `phase0_discovery/exec/DATA_QUALITY.md` → "Data Foundation"
  - `phase1_strategy/exec/STRATEGY.md` → "Analysis Strategy"
  - `phase3_analysis/exec/ANALYSIS.md` → "Analysis Findings"
  - `phase4_projection/exec/PROJECTION.md` → "Forward Projection"
  - `phase5_verification/exec/VERIFICATION.md` → "Verification Results"
- `build_executive_summary(summary_text)` — placeholder or provided text
- `render() -> str` — produce full Markdown with title, date, executive summary, numbered sections, appendix (data provenance, code references)
- `save(output_path) -> Path` — render and write to file
- `to_dict() -> dict` — metadata serialization

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_report_generator.py -v
```

Commit: `git commit -m "feat: implement report generator for Phase 6"`

---

## Task 2: Audit Trail Generator

**Files:**
- Create: `src/templates/scripts/audit_trail.py`
- Create: `tests/test_audit_trail.py`

Machine-readable audit linking claims to data sources and methodology choices.

- [ ] **Step 1: Write tests**

Create `tests/test_audit_trail.py`:

```python
"""Tests for audit trail generation."""
import pytest
from pathlib import Path
from src.templates.scripts.audit_trail import AuditTrail, Claim, MethodologyChoice


def test_add_claim():
    trail = AuditTrail(analysis_name="Test")
    claim = trail.add_claim(claim_id="C1", text="X causes Y",
                            source_type="analysis", source_ref="phase3/test.py",
                            evidence_type="DATA_SUPPORTED", confidence=0.8, phase="phase3")
    assert len(trail.claims) == 1
    assert claim.claim_id == "C1"


def test_add_methodology_choice():
    trail = AuditTrail(analysis_name="Test")
    trail.add_methodology_choice(choice_id="M1", description="Use propensity score",
                                  alternatives_considered=["IV", "DiD"],
                                  justification="Binary treatment, observational data",
                                  phase="phase3")
    assert len(trail.methodology_choices) == 1


def test_save_and_load(tmp_path):
    trail = AuditTrail(analysis_name="Test")
    trail.add_claim(claim_id="C1", text="Finding",
                    source_type="data", source_ref="data.csv",
                    evidence_type="CORRELATION", confidence=0.6, phase="phase3")
    trail.add_methodology_choice(choice_id="M1", description="Method",
                                  alternatives_considered=["A"],
                                  justification="Because", phase="phase3")
    trail.save(tmp_path)

    loaded = AuditTrail.load(tmp_path)
    assert loaded.analysis_name == "Test"
    assert len(loaded.claims) == 1
    assert len(loaded.methodology_choices) == 1


def test_summary():
    trail = AuditTrail(analysis_name="Test")
    trail.add_claim(claim_id="C1", text="A", source_type="data",
                    source_ref="x", evidence_type="DATA_SUPPORTED", phase="phase3")
    trail.add_claim(claim_id="C2", text="B", source_type="data",
                    source_ref="y", evidence_type="CORRELATION", phase="phase3")
    s = trail.summary()
    assert s["total_claims"] == 2
    assert s["claims_by_evidence_type"]["DATA_SUPPORTED"] == 1


def test_to_markdown():
    trail = AuditTrail(analysis_name="Test")
    trail.add_claim(claim_id="C1", text="Short claim",
                    source_type="data", source_ref="file.csv",
                    evidence_type="DATA_SUPPORTED", confidence=0.9, phase="phase3")
    md = trail.to_markdown()
    assert "Audit Trail" in md
    assert "C1" in md
    assert "Claims Provenance" in md


def test_empty_trail():
    trail = AuditTrail(analysis_name="Empty")
    md = trail.to_markdown()
    assert "Empty" in md
    s = trail.summary()
    assert s["total_claims"] == 0
```

- [ ] **Step 2: Implement audit_trail.py**

Create `src/templates/scripts/audit_trail.py` with:

**Data structures:**
- `Claim`: dataclass with `claim_id`, `text`, `source_type` ("data" | "analysis" | "projection" | "literature"), `source_ref`, `evidence_type`, `confidence`, `phase`, `to_dict()`
- `MethodologyChoice`: dataclass with `choice_id`, `description`, `alternatives_considered` (list), `justification`, `phase`, `to_dict()`
- `AuditTrail`: dataclass with `analysis_name`, `claims` list, `methodology_choices` list

**Methods on AuditTrail:**
- `add_claim(**kwargs) -> Claim`
- `add_methodology_choice(**kwargs) -> MethodologyChoice`
- `save(output_dir) -> tuple[Path, Path]` — write `claims.yaml` and `methodology.yaml`
- `load(output_dir) -> AuditTrail` (classmethod) — read from YAML files
- `summary() -> dict` — counts by evidence type and phase
- `to_markdown() -> str` — render as Markdown table with Claims Provenance and Methodology Choices sections

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_audit_trail.py -v
```

Commit: `git commit -m "feat: implement audit trail generator for Phase 6"`

---

## Task 3: Integration Test — Full Report with Audit Trail

**Files:**
- Create: `tests/test_sprint4_integration.py`

- [ ] **Step 1: Write integration test**

```python
"""Sprint 4 integration: build report + audit trail from mock analysis."""
import pytest
from pathlib import Path
from src.templates.scripts.report_generator import ReportBuilder
from src.templates.scripts.audit_trail import AuditTrail


def test_full_report_with_audit_trail(tmp_path):
    # Create mock phase artifacts
    for phase, artifact, content in [
        ("phase0_discovery", "DISCOVERY.md", "## Principles\nIdentified X→Y."),
        ("phase1_strategy", "STRATEGY.md", "## Strategy\nUse DoWhy."),
        ("phase3_analysis", "ANALYSIS.md", "## Findings\nX causes Y (DATA_SUPPORTED)."),
    ]:
        d = tmp_path / phase / "exec"
        d.mkdir(parents=True)
        (d / artifact).write_text(content)

    # Build report
    builder = ReportBuilder(analysis_name="Integration Test", question="Does X cause Y?")
    builder.collect_from_phases(tmp_path)
    report_path = builder.save(tmp_path / "REPORT.md")
    assert report_path.exists()
    report_text = report_path.read_text()
    assert "First Principles" in report_text
    assert "Analysis Findings" in report_text

    # Build audit trail
    trail = AuditTrail(analysis_name="Integration Test")
    trail.add_claim(claim_id="C1", text="X causes Y",
                    source_type="analysis", source_ref="phase3/causal_test.py",
                    evidence_type="DATA_SUPPORTED", confidence=0.85, phase="phase3")
    trail.add_methodology_choice(choice_id="M1", description="Propensity score matching",
                                  alternatives_considered=["IV", "DiD"],
                                  justification="Binary treatment", phase="phase3")

    claims_path, method_path = trail.save(tmp_path / "audit")
    assert claims_path.exists()
    assert method_path.exists()

    # Verify markdown output
    md = trail.to_markdown()
    assert "C1" in md
    assert "M1" in md
```

- [ ] **Step 2: Run all Sprint 4 tests**

```bash
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_report_generator.py tests/test_audit_trail.py tests/test_sprint4_integration.py -v
```

Commit: `git commit -m "test: add Sprint 4 integration tests"`

---

## Verification

```bash
# Run all Sprint 4 tests
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_report_generator.py tests/test_audit_trail.py tests/test_sprint4_integration.py -v

# Full regression
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Report generator | `report_generator.py` + `test_report_generator.py` | 20 min |
| 2 | Audit trail generator | `audit_trail.py` + `test_audit_trail.py` | 20 min |
| 3 | Integration test | `test_sprint4_integration.py` | 10 min |
| **Total** | | **5 files** | **~50 min** |
