# Sprint 7C: Verification & Review Enhancements

> **Execution order:** Plans 7A → 7B → 7C → 7D (sequential, not parallel) due to shared file modifications in pixi.toml and root_claude.md.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make verification fully modular (single `run_all_checks()` entry point), add artifact path enforcement, and update Phase 6 CLAUDE.md for method-environment consistency checking.

**Architecture:** Extend existing `verification.py` with auto-discovery and a unified entry point. Add path validation to scaffolder. Update Phase 1 template to require method-dependency cross-check.

**Tech Stack:** Python 3.11+, PyYAML, pytest

**Issues addressed:** I9 (method availability check), I15 (verification modularity)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/templates/scripts/verification.py` | Modify | Add `run_all_checks()` auto-discovery entry point |
| `src/templates/phase1_claude.md` | Modify | Add method-dependency cross-check requirement |
| `tests/test_verification.py` | Modify | Add test for `run_all_checks()` |

---

### Task 1: Verification Module — `run_all_checks()` Entry Point

**Files:**
- Modify: `src/templates/scripts/verification.py`
- Modify: `tests/test_verification.py`

Fixes: I15

- [ ] **Step 1: Write failing test**

Add to `tests/test_verification.py`:

```python
def test_run_all_checks_auto_discovery():
    """run_all_checks should auto-discover data from analysis directory."""
    analysis_dir = TMP / "analysis"
    analysis_dir.mkdir(parents=True)

    # Create minimal phase structure
    p0_data = analysis_dir / "phase0_discovery" / "data"
    p0_data.mkdir(parents=True)
    p0_exec = analysis_dir / "phase0_discovery" / "exec"
    p0_exec.mkdir(parents=True)
    p3_exec = analysis_dir / "phase3_analysis" / "exec"
    p3_exec.mkdir(parents=True)

    # Create registry
    import hashlib
    raw_dir = p0_data / "raw"
    raw_dir.mkdir()
    test_csv = raw_dir / "test.csv"
    test_csv.write_text("a,b\n1,2\n")
    sha = hashlib.sha256(test_csv.read_bytes()).hexdigest()
    registry = p0_data / "registry.yaml"
    registry.write_text(
        f"datasets:\n"
        f"  - source_id: ds_001\n"
        f"    url: https://example.com/test.csv\n"
        f"    file: phase0_discovery/data/raw/test.csv\n"
        f"    sha256: {sha}\n"
    )

    from verification import run_all_checks
    report = run_all_checks(analysis_dir)
    assert report.all_passed
    assert report.pass_count >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_verification.py::test_run_all_checks_auto_discovery -v`
Expected: FAIL — `run_all_checks` not found

- [ ] **Step 3: Add run_all_checks to verification.py**

Append to `src/templates/scripts/verification.py`:

```python
def run_all_checks(analysis_dir: Path) -> VerificationReport:
    """Auto-discover analysis data and run all verification checks.

    This is the single entry point for Phase 5. It discovers:
    - registry.yaml from phase0_discovery/data/
    - EP chains from phase3_analysis/exec/ep_update_results.json
    - Causal labels from phase3_analysis/exec/ANALYSIS.md

    Returns a complete VerificationReport ready for writing to
    phase5_verification/exec/VERIFICATION.md.
    """
    analysis_dir = Path(analysis_dir)
    all_checks: list[VerificationCheck] = []

    # 1. Data provenance
    registry_path = analysis_dir / "phase0_discovery" / "data" / "registry.yaml"
    if registry_path.exists():
        provenance_report = verify_data_provenance(
            registry_path=registry_path,
            analysis_root=analysis_dir / "phase0_discovery",
        )
        all_checks.extend(provenance_report.checks)
    else:
        all_checks.append(VerificationCheck(
            name="registry_exists",
            passed=False,
            details="phase0_discovery/data/registry.yaml not found",
        ))

    # 2. EP propagation (if results exist)
    ep_results_path = analysis_dir / "phase3_analysis" / "exec" / "ep_update_results.json"
    if ep_results_path.exists():
        import json
        with open(ep_results_path) as f:
            ep_data = json.load(f)
        chains = ep_data.get("chains", [])
        for chain_data in chains:
            nodes = chain_data.get("nodes", [])
            reported_joint = chain_data.get("joint_ep", 0)
            ep_report = verify_ep_propagation(
                chain_name=chain_data.get("name", "unknown"),
                nodes=nodes,
                reported_joint_ep=reported_joint,
            )
            all_checks.extend(ep_report.checks)

    # 3. Causal labels (if ANALYSIS.md exists)
    analysis_md = analysis_dir / "phase3_analysis" / "exec" / "ANALYSIS.md"
    if analysis_md.exists():
        # Read the text for causal label patterns
        text = analysis_md.read_text()
        # Look for classification results in the text
        import re
        label_pattern = re.compile(
            r"(\w[\w ]*?)\s*(?:→|->)\s*(\w[\w ]*?):\s*(DATA_SUPPORTED|CORRELATION|HYPOTHESIZED|DISPUTED)",
            re.IGNORECASE | re.MULTILINE,
        )
        for match in label_pattern.finditer(text):
            label = match.group(3).upper()
            all_checks.append(VerificationCheck(
                check_name=f"causal_label_{match.group(1).strip()}_{match.group(2).strip()}",
                passed=True,
                details=f"Label {label} found for {match.group(1).strip()} → {match.group(2).strip()}",
            ))

    return VerificationReport(checks=all_checks)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bamboo/Githubs/OpenPE && PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_verification.py -v`
Expected: all passed

- [ ] **Step 5: Commit**

```bash
git add src/templates/scripts/verification.py tests/test_verification.py
git commit -m "feat(sprint7c): add run_all_checks() auto-discovery entry point

Fixes I15 — single function discovers registry, EP results, and
causal labels from analysis directory structure."
```

---

### Task 2: Method-Environment Consistency Check in Strategy

**Files:**
- Modify: `src/templates/phase1_claude.md`

Fixes: I9

- [ ] **Step 1: Add method availability requirement**

In `src/templates/phase1_claude.md`, in the Step 1.1 "Evaluate candidate methods" section, add after the method evaluation table:

```markdown
**Method-environment cross-check (non-negotiable):** For every method
selected in the strategy, verify that the required Python package is
available in `pixi.toml`. Check:

```python
# Run this check before finalizing STRATEGY.md:
# pixi run py -c "import dowhy; import statsmodels; import scipy"
```

If a method requires a package not in `pixi.toml`, either:
1. Add it to `pixi.toml` and run `pixi install`, OR
2. Replace the method with one that uses available packages

**Never recommend a method whose implementation is not installable.**
Document the availability check result in `experiment_log.md`.
```

- [ ] **Step 2: Commit**

```bash
git add src/templates/phase1_claude.md
git commit -m "docs(sprint7c): require method-dependency cross-check in Phase 1

Fixes I9 — strategy agent must verify every recommended method
has an available package in pixi.toml before finalizing strategy."
```

---

## Verification

```bash
cd /Users/bamboo/Githubs/OpenPE
PYTHONPATH=src/templates/scripts:. python -m pytest tests/test_verification.py -v
PYTHONPATH=src/templates/scripts:. python -m pytest tests/ -v
```

Note: I10 (artifact path enforcement) and I11 (self-review quality) are deferred to a future sprint as they require more design work.
