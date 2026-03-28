# Sprint 8B: Test Coverage Gaps + Import Unification + analysis-note.md

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fill Sprint 6 test coverage gaps (IGM/SSR/VAR, archive, find_similar, temporal graph), unify test import convention, and create the missing analysis-note.md spec.

**Architecture:** Add unit tests for untested Sprint 6 code. Migrate 3 Sprint 7 test files from bare imports to qualified imports. Create `methodology/analysis-note.md` from the Phase 6 CLAUDE.md outline.

**Tech Stack:** Python 3.11+, pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `tests/test_audit_trail.py` | Modify | Add IGM/SSR/VAR tests |
| `tests/test_memory_store.py` | Modify | Add archive/find_similar tests |
| `tests/test_causal_knowledge_graph.py` | Modify | Add temporal field tests |
| `tests/test_state_manager.py` | Modify | Unify imports |
| `tests/test_experiment_logger.py` | Modify | Unify imports |
| `tests/test_data_extractor.py` | Modify | Unify imports |
| `src/methodology/analysis-note.md` | Create | Report format specification |

---

### Task 1: Audit Trail Unit Tests (IGM/SSR/VAR)

**Files:**
- Modify: `tests/test_audit_trail.py`

- [ ] **Step 1: Append tests**

Add to `tests/test_audit_trail.py`:

```python
from src.templates.scripts.audit_trail import (
    SourceRecord, VeracityRecord,
    compute_shi, construct_igm, construct_rm,
)


def test_compute_shi():
    sha = compute_shi("hello world")
    assert len(sha) == 64  # SHA-256 hex
    assert sha == compute_shi("hello world")  # deterministic
    assert sha != compute_shi("different")


def test_construct_igm():
    igm = construct_igm("C1", "abcdef1234567890abcdef", "phase3/data.csv:row42")
    assert igm == "[C1:abcdef1234:phase3/data.csv:row42]"


def test_construct_rm():
    rm = construct_rm("R1", "CAUSAL_CLAIM", ["C1", "C2"])
    assert rm == "(R1:CAUSAL_CLAIM:C1,C2)"


def test_source_record():
    sr = SourceRecord(
        shi="abc123", source_type="dataset",
        uri="https://api.worldbank.org/test",
        verification_status="VERIFIED",
    )
    d = sr.to_dict()
    assert d["shi"] == "abc123"
    assert d["verification_status"] == "VERIFIED"


def test_veracity_record():
    vr = VeracityRecord(
        relation_id="R1", relation_type="INFERENCE",
        dependent_claims=["C1", "C2"],
    )
    assert vr.audit_status == "PENDING"
    d = vr.to_dict()
    assert d["dependent_claims"] == ["C1", "C2"]


def test_verify_logic_all_supported():
    trail = AuditTrail(analysis_name="test")
    trail.add_claim(claim_id="C1", text="X causes Y",
                    source_type="analysis", source_ref="test.py",
                    evidence_type="DATA_SUPPORTED")
    trail.add_claim(claim_id="C2", text="Y causes Z",
                    source_type="analysis", source_ref="test.py",
                    evidence_type="DATA_SUPPORTED")
    trail.add_veracity(relation_id="R1", relation_type="INFERENCE",
                       dependent_claims=["C1", "C2"])
    trail.verify_logic()
    assert trail.veracity[0].audit_status == "VERIFIED_LOGIC"


def test_verify_logic_insufficient():
    trail = AuditTrail(analysis_name="test")
    trail.add_claim(claim_id="C1", text="X causes Y",
                    source_type="analysis", source_ref="test.py",
                    evidence_type="HYPOTHESIZED")
    trail.add_veracity(relation_id="R1", relation_type="INFERENCE",
                       dependent_claims=["C1"])
    trail.verify_logic()
    assert trail.veracity[0].audit_status == "INSUFFICIENT_PREMISE"


def test_save_load_with_ssr_var():
    trail = AuditTrail(analysis_name="test")
    trail.add_source(shi="abc123", source_type="dataset",
                     uri="test.csv", verification_status="VERIFIED")
    trail.add_veracity(relation_id="R1", relation_type="CAUSAL_CLAIM",
                       dependent_claims=["C1"])
    trail.save(TMP)

    loaded = AuditTrail.load(TMP)
    assert len(loaded.sources) == 1
    assert loaded.sources[0].shi == "abc123"
    assert len(loaded.veracity) == 1
    assert loaded.veracity[0].relation_id == "R1"
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_audit_trail.py -v`
Expected: all pass (new tests exercise existing code that was untested)

- [ ] **Step 3: Commit**

```bash
git add tests/test_audit_trail.py
git commit -m "test(sprint8b): add unit tests for IGM/SSR/VAR audit structures

Covers compute_shi, construct_igm, construct_rm, SourceRecord,
VeracityRecord, verify_logic, and save/load with SSR+VAR.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Memory Store Unit Tests (archive, find_similar)

**Files:**
- Modify: `tests/test_memory_store.py`

- [ ] **Step 1: Append tests**

Add to `tests/test_memory_store.py`:

```python
def test_archive_cold_l2():
    """archive() should move cold L2 entries to _archive/."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="cold_l2",
        content="Old detail",
        domain="test",
        memory_type="domain",
        tier="L2",
        confidence=0.3,
        active_count=0,
        updated="2020-01-01T00:00:00",
    ))
    archived = store.archive(threshold=0.5)
    assert "cold_l2" in archived
    assert "cold_l2" not in store.entries
    assert (TMP / "memory" / "L2" / "_archive" / "cold_l2.yaml").exists()


def test_archive_skips_hot_entries():
    """archive() should not touch hot entries."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="hot_l2",
        content="Recent detail",
        domain="test",
        memory_type="domain",
        tier="L2",
        confidence=0.8,
        active_count=10,
    ))
    archived = store.archive(threshold=0.5)
    assert "hot_l2" not in archived
    assert "hot_l2" in store.entries


def test_archive_skips_non_l2():
    """archive() should never archive L0 or L1 entries."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="l1_entry",
        content="L1 finding",
        domain="test",
        memory_type="domain",
        tier="L1",
        confidence=0.1,
        active_count=0,
        updated="2020-01-01T00:00:00",
    ))
    archived = store.archive(threshold=0.99)
    assert "l1_entry" not in archived


def test_find_similar_matches():
    """find_similar should return entries with keyword overlap."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="m1",
        content="Bootstrap confidence intervals for small samples",
        domain="statistics",
        memory_type="method",
        tier="L1",
    ))
    store.add(MemoryEntry(
        memory_id="m2",
        content="Completely unrelated topic about cooking recipes",
        domain="cooking",
        memory_type="domain",
        tier="L1",
    ))
    results = store.find_similar("bootstrap confidence interval estimation")
    assert len(results) >= 1
    assert results[0][0].memory_id == "m1"
    assert results[0][1] > 0.3  # similarity score


def test_find_similar_empty():
    """find_similar with no matches returns empty."""
    store = MemoryStore(TMP / "memory")
    store.add(MemoryEntry(
        memory_id="m1",
        content="Alpha beta gamma",
        domain="test",
        memory_type="domain",
        tier="L1",
    ))
    results = store.find_similar("completely different words xyz")
    assert len(results) == 0
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_memory_store.py -v`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_memory_store.py
git commit -m "test(sprint8b): add unit tests for archive() and find_similar()

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Causal Knowledge Graph Unit Tests (temporal fields)

**Files:**
- Modify: `tests/test_causal_knowledge_graph.py`

- [ ] **Step 1: Append tests**

Add to `tests/test_causal_knowledge_graph.py`:

```python
def test_invalidate_edge():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "CAUSES", confidence=0.8, analysis_id="test1")
    assert graph.relationships["A→B"].is_valid

    result = graph.invalidate_edge("A", "B", "test2")
    assert result is True
    assert not graph.relationships["A→B"].is_valid
    assert graph.relationships["A→B"].invalid_at != ""


def test_invalidate_nonexistent():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    result = graph.invalidate_edge("X", "Y", "test")
    assert result is False


def test_query_only_valid():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "CAUSES", confidence=0.8, analysis_id="t1")
    graph.add_relationship("C", "D", "CAUSES", confidence=0.7, analysis_id="t1")
    graph.invalidate_edge("A", "B", "t2")

    valid = graph.query(only_valid=True)
    assert len(valid) == 1
    assert valid[0].source == "C"

    all_rels = graph.query(only_valid=False)
    assert len(all_rels) == 2


def test_prune_stale():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "HYPOTHESIZED", confidence=0.3, analysis_id="old")
    graph.relationships["A→B"].updated = "2020-01-01T00:00:00"

    expired = graph.prune_stale(max_age_days=30)
    assert "A→B" in expired
    assert graph.relationships["A→B"].is_expired


def test_prune_keeps_confident():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "CAUSES", confidence=0.8, analysis_id="old")
    graph.relationships["A→B"].updated = "2020-01-01T00:00:00"

    expired = graph.prune_stale(max_age_days=30)
    assert "A→B" not in expired  # confidence ≥ 0.5 exempt


def test_temporal_fields_roundtrip():
    graph = CausalKnowledgeGraph(TMP / "graph.json")
    graph.add_relationship("A", "B", "CAUSES", confidence=0.8, analysis_id="t1")
    graph.relationships["A→B"].valid_at = "2024-01-01T00:00:00"
    graph.relationships["A→B"].episodes = ["t1", "t2"]
    graph.save()

    graph2 = CausalKnowledgeGraph(TMP / "graph.json")
    graph2.load()
    rel = graph2.relationships["A→B"]
    assert rel.valid_at == "2024-01-01T00:00:00"
    assert rel.episodes == ["t1", "t2"]
    assert rel.is_valid  # not invalidated
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_causal_knowledge_graph.py -v`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_causal_knowledge_graph.py
git commit -m "test(sprint8b): add unit tests for temporal graph fields

Covers invalidate_edge, prune_stale, only_valid query, temporal
field roundtrip through save/load.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Unify Test Import Convention

**Files:**
- Modify: `tests/test_state_manager.py`
- Modify: `tests/test_experiment_logger.py`
- Modify: `tests/test_data_extractor.py`

Change all 3 files from bare imports to qualified imports to match the other 18 test files.

- [ ] **Step 1: Fix test_state_manager.py**

Change line 5 from:
```python
from state_manager import StateManager
```
to:
```python
from src.templates.scripts.state_manager import StateManager
```

- [ ] **Step 2: Fix test_experiment_logger.py**

Change line 5 from:
```python
from experiment_logger import ExperimentLogger
```
to:
```python
from src.templates.scripts.experiment_logger import ExperimentLogger
```

- [ ] **Step 3: Fix test_data_extractor.py**

Change lines 7-12 from:
```python
from data_extractor import (
    ExtractedValue,
    extract_numbers_from_text,
    extract_table_from_csv_text,
    build_dataset_from_extractions,
)
```
to:
```python
from src.templates.scripts.data_extractor import (
    ExtractedValue,
    extract_numbers_from_text,
    extract_table_from_csv_text,
    build_dataset_from_extractions,
)
```

- [ ] **Step 4: Also fix test_verification.py line 174**

The existing `test_verification.py` has a mixed import — the `run_all_checks` test uses a bare import. Find the line `from verification import run_all_checks` and change to `from src.templates.scripts.verification import run_all_checks`.

- [ ] **Step 5: Run full suite**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v --tb=short`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add tests/test_state_manager.py tests/test_experiment_logger.py tests/test_data_extractor.py tests/test_verification.py
git commit -m "refactor(sprint8b): unify test imports to src.templates.scripts.X

All 21 test files now use qualified imports consistently.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Create methodology/analysis-note.md

**Files:**
- Create: `src/methodology/analysis-note.md`

This file is referenced by `03-phases.md`, `root_claude.md`, and `phase6_claude.md` but does not exist.

- [ ] **Step 1: Create the file**

Create `src/methodology/analysis-note.md` based on the Phase 6 CLAUDE.md outline (already defined in `src/templates/phase6_claude.md` lines 59-122):

```markdown
# Analysis Note Specification

The Analysis Note is the primary deliverable of an OpenPE analysis. It is a
pandoc-compatible markdown document that compiles into a professional PDF.

## Required Sections

### Executive Summary
2-4 paragraphs: question, approach, key findings, confidence assessment.
State the endgame classification. Include the primary EP chain with Joint_EP.
No jargon — a non-specialist should understand this section.

### 1. First Principles Identified
Causal DAG visualization (mermaid format). Literature support for each
principle. Competing DAGs considered and why the final structure was selected.
Edge labels and EP values.

### 2. Data Foundation
Sources used (table from registry.yaml). Quality assessment summary per
source. Limitations and caveats. Any data gaps and their impact on conclusions.

### 3. Analysis Findings
For each causal edge in the final DAG:

#### 3.X [Edge name: A → B]
- **Classification:** DATA_SUPPORTED / CORRELATION / HYPOTHESIZED / DISPUTED
- **EP:** [value] (95% CI: [lower, upper])
- **Evidence:** summary of statistical test, effect size, confounders
- **Uncertainty range:** quantified

Classification labels:

| Label | Meaning | Reader interpretation |
|-------|---------|----------------------|
| DATA_SUPPORTED | Survived refutation testing with quantitative evidence | Strong basis for conclusions |
| CORRELATION | Statistical association found, causation not established | Suggestive but not conclusive |
| HYPOTHESIZED | Not yet testable with available data | Speculative; treat with caution |
| DISPUTED | Contradictory evidence — placebo-anchored tests conflict | Requires human review |

### 4. Forward Projection
Scenario descriptions and results. Sensitivity analysis with tornado diagram.
Endgame classification with evidence. EP decay chart. Fork conditions.

### 5. Audit Trail
Data provenance summary. Methodology choices and alternatives considered.
Refutation test results. Verification report summary. Human gate decision.

### Appendices
- **A. Raw Code References:** Paths to all analysis scripts
- **B. Statistical Details:** Full regression tables, test statistics, CIs
- **C. Data Quality Report:** Full DATA_QUALITY.md content
- **D. Experiment Log:** Complete experiment log

## Format Requirements

- **LaTeX math:** `$...$` inline, `$$...$$` display
- **Figures:** `![Caption](figures/name.pdf){#fig:label}` — pandoc converts
  to `\includegraphics`
- **No raw HTML.** Pandoc markdown only.
- **Tables:** Pipe tables (`| col1 | col2 |`)
- **Cross-references:** pandoc-crossref syntax — `{#fig:label}`, `@fig:label`.
  At sentence start: `Figure @fig:name`. Every figure MUST have a label.
- **Citations:** `[@key]` with a `references.bib` BibTeX file
- **Sections:** `#`, `##`, `###` — pandoc adds numbering

## PDF Generation

```bash
pixi run build-pdf
```

Uses `openpe-metadata.yaml` for professional styling (branded headers,
executive summary box, figure sizing). See `scripts/openpe-metadata.yaml`.
```

- [ ] **Step 2: Verify references resolve**

```bash
grep -rn "analysis-note.md" /Users/bamboo/Githubs/OpenPE/src/methodology/ /Users/bamboo/Githubs/OpenPE/src/templates/
```
Expected: references to `methodology/analysis-note.md` which now exists.

- [ ] **Step 3: Commit**

```bash
git add src/methodology/analysis-note.md
git commit -m "docs(sprint8b): create methodology/analysis-note.md

Fills the missing report format specification referenced by
03-phases.md, root_claude.md, and phase6_claude.md.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Verification

```bash
cd /Users/bamboo/Githubs/OpenPE
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v --tb=short
```

Expected: all tests pass, including ~20 new tests from Tasks 1-3.
