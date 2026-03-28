# OpenPE Sprint 1: Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform slop-X scaffolding, templates, and agent profiles into OpenPE's Phase 0–6 structure, archive HEP-specific content, and create the 4 new agents needed for Phase 0 (Discovery) and Phase 4 (Projection).

**Architecture:** In-place modification of `src/` infrastructure. The scaffolder creates 7 phase directories (phase0_discovery through phase6_documentation). Templates are rewritten for domain-agnostic first-principles analysis. Existing HEP agent profiles are archived; new agents (hypothesis, data_acquisition, data_quality, projector) are created. The pixi.toml template swaps HEP packages (uproot, pyhf) for causal inference packages (dowhy, pandas, wbgapi, fredapi).

**Tech Stack:** Python 3.11+, pixi, Claude Code agents, WebSearch/WebFetch for data acquisition, pandas/dowhy/wbgapi/fredapi for analysis.

**Spec:** `docs/superpowers/specs/2026-03-28-slop-fp-architecture-design.md`

---

## File Map

### Files to Create
- `src/templates/phase0_claude.md` — Phase 0 (Discovery) agent instructions
- `src/templates/phase4_claude.md` — Phase 4 (Projection) agent instructions (replaces old phase4 which was inference)
- `src/templates/phase5_claude.md` — Phase 5 (Verification) agent instructions (replaces old phase5 which was documentation)
- `src/templates/phase6_claude.md` — Phase 6 (Documentation) agent instructions
- `.claude/agents/hypothesis-agent.md` — Hypothesis agent profile
- `.claude/agents/data-acquisition-agent.md` — Data acquisition agent profile
- `.claude/agents/data-quality-agent.md` — Data quality agent profile
- `.claude/agents/projector-agent.md` — Projector agent profile
- `_archive/agents/` — Directory for archived HEP agent profiles
- `tests/test_scaffold.py` — Scaffolder tests

### Files to Modify
- `src/scaffold_analysis.py` — New phase list, new subdirs, new config format
- `src/templates/root_claude.md` — Orchestrator loop: `[0,1,2,3,4,5,6]`, generalized instructions
- `src/templates/phase1_claude.md` — Generalize from HEP strategy to domain-agnostic strategy
- `src/templates/phase2_claude.md` — Generalize from HEP exploration to data exploration
- `src/templates/phase3_claude.md` — Generalize from HEP selection to causal analysis
- `src/templates/pixi.toml` — Replace HEP deps with OpenPE deps
- `.claude/hooks/isolate.sh` — No changes needed (already handles `data_dir` + `allow=` lines)

### Files to Archive (move to `_archive/agents/`)
- `.claude/agents/detector-specialist.md`
- `.claude/agents/theory-scout.md`
- `.claude/agents/systematic-source-evaluator.md`
- `.claude/agents/background-estimator.md`
- `.claude/agents/systematics-fitter.md`
- `.claude/agents/investigator.md`

### Files to Rename (in `.claude/agents/`)
- `signal-lead.md` → `analyst.md`
- `cross-checker.md` → `verifier.md`
- `note-writer.md` → `report-writer.md`
- `physics-reviewer.md` → `domain-reviewer.md`
- `critical-reviewer.md` → `logic-reviewer.md`
- `constructive-reviewer.md` → `methods-reviewer.md`

---

## Task 1: Archive HEP-Specific Agents

**Files:**
- Create: `_archive/agents/` (directory)
- Move: 6 agent files from `.claude/agents/` to `_archive/agents/`

- [ ] **Step 1: Create archive directory and move files**

```bash
mkdir -p _archive/agents
mv .claude/agents/detector-specialist.md _archive/agents/
mv .claude/agents/theory-scout.md _archive/agents/
mv .claude/agents/systematic-source-evaluator.md _archive/agents/
mv .claude/agents/background-estimator.md _archive/agents/
mv .claude/agents/systematics-fitter.md _archive/agents/
mv .claude/agents/investigator.md _archive/agents/
```

- [ ] **Step 2: Verify archive contents**

Run: `ls _archive/agents/`
Expected: 6 `.md` files listed.

Run: `ls .claude/agents/ | wc -l`
Expected: 12 (was 18, minus 6 archived).

- [ ] **Step 3: Commit**

```bash
git add _archive/agents/ .claude/agents/
git commit -m "Archive 6 HEP-specific agent profiles to _archive/"
```

---

## Task 2: Rename Generalized Agents

**Files:**
- Rename: 6 agent files in `.claude/agents/`

- [ ] **Step 1: Rename files**

```bash
mv .claude/agents/signal-lead.md .claude/agents/analyst.md
mv .claude/agents/cross-checker.md .claude/agents/verifier.md
mv .claude/agents/note-writer.md .claude/agents/report-writer.md
mv .claude/agents/physics-reviewer.md .claude/agents/domain-reviewer.md
mv .claude/agents/critical-reviewer.md .claude/agents/logic-reviewer.md
mv .claude/agents/constructive-reviewer.md .claude/agents/methods-reviewer.md
```

- [ ] **Step 2: Verify renames**

Run: `ls .claude/agents/`
Expected: `analyst.md`, `arbiter.md`, `data-explorer.md`, `domain-reviewer.md`, `lead-analyst.md`, `logic-reviewer.md`, `methods-reviewer.md`, `ml-specialist.md`, `plot-validator.md`, `rendering-reviewer.md`, `report-writer.md`, `verifier.md` — 12 files.

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/
git commit -m "Rename 6 agent profiles for OpenPE generalization"
```

---

## Task 3: Update Scaffolder — Phase Structure

**Files:**
- Modify: `src/scaffold_analysis.py`
- Create: `tests/test_scaffold.py`

- [ ] **Step 1: Write scaffolder test**

Create `tests/test_scaffold.py`:

```python
"""Tests for the OpenPE scaffolder."""
import shutil
from pathlib import Path
from src.scaffold_analysis import scaffold

TEST_DIR = Path("/tmp/test_openpe_scaffold")


def setup_function():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)


def teardown_function():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)


def test_phase_directories_created():
    """Scaffold creates all 7 phase directories with semantic names."""
    scaffold(TEST_DIR, "analysis")
    expected = [
        "phase0_discovery",
        "phase1_strategy",
        "phase2_exploration",
        "phase3_analysis",
        "phase4_projection",
        "phase5_verification",
        "phase6_documentation",
    ]
    for phase_name in expected:
        phase_dir = TEST_DIR / phase_name
        assert phase_dir.is_dir(), f"Missing: {phase_name}"
        assert (phase_dir / "exec").is_dir(), f"Missing: {phase_name}/exec"
        assert (phase_dir / "review").is_dir(), f"Missing: {phase_name}/review"
        assert (phase_dir / "CLAUDE.md").exists(), f"Missing: {phase_name}/CLAUDE.md"


def test_phase0_has_data_subdirs():
    """Phase 0 has data/raw, data/processed, data/registry.yaml."""
    scaffold(TEST_DIR, "analysis")
    data_dir = TEST_DIR / "phase0_discovery" / "data"
    assert (data_dir / "raw").is_dir()
    assert (data_dir / "processed").is_dir()


def test_analysis_config_has_input_mode():
    """The .analysis_config includes input_mode field."""
    scaffold(TEST_DIR, "analysis")
    config = (TEST_DIR / ".analysis_config").read_text()
    assert "input_mode=" in config


def test_state_md_starts_at_phase_0():
    """STATE.md starts at phase 0, not phase 1."""
    scaffold(TEST_DIR, "analysis")
    state = (TEST_DIR / "STATE.md").read_text()
    assert "Current phase**: 0" in state


def test_analysis_config_yaml_no_hep():
    """analysis_config.yaml has no HEP-specific fields."""
    scaffold(TEST_DIR, "analysis")
    yaml_content = (TEST_DIR / "analysis_config.yaml").read_text()
    assert "blinding" not in yaml_content
    assert "channels" not in yaml_content
    assert "input_mode" in yaml_content


def test_old_phase_names_not_present():
    """No slop-X phase names (phase3_selection, phase4_inference, etc.)."""
    scaffold(TEST_DIR, "analysis")
    for name in ["phase3_selection", "phase4_inference", "phase5_documentation"]:
        assert not (TEST_DIR / name).exists(), f"Old phase dir still exists: {name}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pixi run py -m pytest tests/test_scaffold.py -v`
Expected: FAIL (old scaffolder creates slop-X phases, not OpenPE phases).

- [ ] **Step 3: Update scaffolder**

Modify `src/scaffold_analysis.py`. Key changes:
1. Replace `PHASES` list with OpenPE phases
2. Replace `PHASE_TEMPLATE_MAP` with OpenPE mapping
3. Add Phase 0 data subdirs
4. Update `.analysis_config` to include `input_mode`
5. Update `STATE.md` to start at phase 0
6. Update `analysis_config.yaml` to remove HEP fields, add `input_mode`
7. Replace `--type measurement|search` with `--type analysis` (single type for OpenPE)
8. Remove HEP-specific conventions routing

Replace the full content of `src/scaffold_analysis.py` with:

```python
#!/usr/bin/env python
"""Scaffold a new OpenPE analysis directory with per-phase CLAUDE.md files.

Usage:
    pixi run scaffold analyses/my_analysis

The script creates the directory structure, generates CLAUDE.md files
from src/templates/, initializes a git repo, and creates the pixi environment.
"""

import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"

# ---------------------------------------------------------------------------
# Phase directories — OpenPE 7-phase pipeline
# ---------------------------------------------------------------------------

PHASES = [
    "phase0_discovery",
    "phase1_strategy",
    "phase2_exploration",
    "phase3_analysis",
    "phase4_projection",
    "phase5_verification",
    "phase6_documentation",
]

PHASE_SUBDIRS = ["exec", "scripts", "figures", "review"]

# Extra subdirs for specific phases
PHASE_EXTRA_SUBDIRS = {
    "phase0_discovery": ["data", "data/raw", "data/processed"],
    "phase3_analysis": ["sub_analyses"],
    "phase6_documentation": ["audit_trail"],
}

PHASE_TEMPLATE_MAP = {
    "phase0_discovery": "phase0_claude.md",
    "phase1_strategy": "phase1_claude.md",
    "phase2_exploration": "phase2_claude.md",
    "phase3_analysis": "phase3_claude.md",
    "phase4_projection": "phase4_claude.md",
    "phase5_verification": "phase5_claude.md",
    "phase6_documentation": "phase6_claude.md",
}


def _read_template(name: str) -> str:
    """Read a template file from src/templates/."""
    path = TEMPLATES / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text()


def _substitute(template: str, variables: dict) -> str:
    """Replace {{key}} placeholders in template with values from variables."""
    result = template
    for key, value in variables.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def scaffold(analysis_dir: Path, analysis_type: str = "analysis"):
    """Create the analysis directory structure with CLAUDE.md files."""
    analysis_dir.mkdir(parents=True, exist_ok=True)

    variables = {
        "name": analysis_dir.name,
        "analysis_type": analysis_type,
    }

    # Analysis-root CLAUDE.md from template
    root_claude = analysis_dir / "CLAUDE.md"
    if not root_claude.exists():
        template = _read_template("root_claude.md")
        root_claude.write_text(_substitute(template, variables))
        print(f"  wrote {root_claude}")

    # Per-phase directories and CLAUDE.md
    for phase_name in PHASES:
        phase_dir = analysis_dir / phase_name
        phase_dir.mkdir(exist_ok=True)
        for subdir in PHASE_SUBDIRS:
            (phase_dir / subdir).mkdir(exist_ok=True)
        # Phase-specific extra subdirs
        for subdir in PHASE_EXTRA_SUBDIRS.get(phase_name, []):
            (phase_dir / subdir).mkdir(parents=True, exist_ok=True)

        claude_path = phase_dir / "CLAUDE.md"
        template_name = PHASE_TEMPLATE_MAP.get(phase_name)
        if template_name and not claude_path.exists():
            template = _read_template(template_name)
            claude_path.write_text(_substitute(template, variables))
            print(f"  wrote {claude_path}")

    # Symlink conventions/, methodology/, and .claude/ into the analysis directory
    for link_name, src_path in [
        ("conventions", HERE / "conventions"),
        ("methodology", HERE / "methodology"),
        (".claude", HERE.parent / ".claude"),
    ]:
        link = analysis_dir / link_name
        if not link.exists() and src_path.exists():
            link.symlink_to(src_path.resolve())
            print(f"  linked {link} -> {src_path}")

    # .analysis_config (for isolation hook)
    config_path = analysis_dir / ".analysis_config"
    if not config_path.exists():
        config_path.write_text(
            "# OpenPE analysis configuration.\n"
            "# The isolation hook allows access to these directories.\n"
            "# Set data_dir if you are providing your own data (Mode B).\n"
            "input_mode=A\n"
            "data_dir=\n"
            "# allow=/path/to/extra/data\n"
        )
        print(f"  wrote {config_path}")

    # Analysis-local pixi.toml from template
    pixi_path = analysis_dir / "pixi.toml"
    if not pixi_path.exists():
        template = _read_template("pixi.toml")
        pixi_path.write_text(template.replace("{name}", variables["name"]))
        print(f"  wrote {pixi_path}")

    # STATE.md for pipeline state tracking
    state_path = analysis_dir / "STATE.md"
    if not state_path.exists():
        state_path.write_text(
            "# Analysis State\n\n"
            f"- **Analysis**: {variables['name']}\n"
            "- **Current phase**: 0\n"
            "- **Status**: initialized\n"
            "- **Last updated**: (not started)\n\n"
            "## Phase History\n\n"
            "| Phase | Status | Artifact | Review | Iterations | Notes |\n"
            "|-------|--------|----------|--------|------------|-------|\n\n"
            "## Blockers\n- (none)\n\n"
            "## Regression Log\n- (none)\n"
        )
        print(f"  wrote {state_path}")

    # analysis_config.yaml for orchestration config
    yaml_config_path = analysis_dir / "analysis_config.yaml"
    if not yaml_config_path.exists():
        yaml_config_path.write_text(
            f"analysis_name: {variables['name']}\n"
            "input_mode: A  # A=question only, B=question+data, C=question+context\n"
            "question: \"\"  # The user's question or scenario\n"
            "domain: \"\"  # Auto-detected or user-specified domain\n"
            "model_tier: auto\n"
            "cost_controls:\n"
            "  max_review_iterations: 10\n"
            "  review_warn_threshold: 3\n"
            "ep_thresholds:\n"
            "  hard_truncation: 0.05\n"
            "  soft_truncation: 0.15\n"
            "  subchain_expansion: 0.30\n"
        )
        print(f"  wrote {yaml_config_path}")

    # regression_log.md
    regression_path = analysis_dir / "regression_log.md"
    if not regression_path.exists():
        regression_path.write_text("# Regression Log\n")
        print(f"  wrote {regression_path}")

    # Experiment log
    log_path = analysis_dir / "experiment_log.md"
    if not log_path.exists():
        log_path.write_text("# Experiment Log\n")
        print(f"  wrote {log_path}")

    # Initialize git repo for the analysis
    git_dir = analysis_dir / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=analysis_dir, check=True,
                       capture_output=True)
        gitignore = analysis_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(
                "# pixi\n"
                ".pixi/\n"
                "pixi.lock\n"
                "\n"
                "# Python\n"
                "__pycache__/\n"
                "*.pyc\n"
                "\n"
                "# Data cache (large files)\n"
                "phase0_discovery/data/raw/\n"
            )
            print(f"  wrote {gitignore}")
        print(f"  initialized git repo")

    print(f"\nScaffolded {analysis_dir}/ (OpenPE analysis)")
    print(f"\nNext steps:")
    print(f"  1. Edit analysis_config.yaml to set your question")
    print(f"  2. cd {analysis_dir} && pixi install")
    print(f"  3. claude   # starts the orchestrator agent")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new OpenPE analysis."
    )
    parser.add_argument("dir", type=Path, help="Analysis directory to create")
    parser.add_argument(
        "--type",
        default="analysis",
        dest="analysis_type",
        help="Analysis type (default: analysis)",
    )
    args = parser.parse_args()
    scaffold(args.dir, args.analysis_type)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pixi run py -m pytest tests/test_scaffold.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/scaffold_analysis.py tests/test_scaffold.py
git commit -m "feat: update scaffolder for OpenPE 7-phase structure"
```

---

## Task 4: Update pixi.toml Template

**Files:**
- Modify: `src/templates/pixi.toml`

- [ ] **Step 1: Replace pixi.toml template**

Replace the full content of `src/templates/pixi.toml` with:

```toml
# Auto-generated by scaffold_analysis.py — edit as needed for this analysis.
# This is the pixi environment for the analysis. All scripts run through:
#   pixi run py script.py

[workspace]
name = "{name}"
version = "0.1.0"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64"]

[dependencies]
python = ">=3.11"
pandoc = ">=3.0"
pandoc-crossref = ">=0.3"

# --- Core stack (always needed) ---
[pypi-dependencies]
numpy = ">=1.24"
scipy = ">=1.11"
pandas = ">=2.0"
matplotlib = ">=3.8"
rich = ">=13.0"
pyarrow = ">=14.0"

# --- Data acquisition ---
requests = ">=2.31"
wbgapi = ">=1.0"         # World Bank API
fredapi = ">=0.5"        # FRED API
openpyxl = ">=3.1"       # Excel reading

# --- Causal inference ---
dowhy = ">=0.11"
# causica — install manually if needed for causal discovery

# --- Uncomment as needed ---
# scikit-learn = ">=1.3"
# statsmodels = ">=0.14"
# xgboost = ">=2.0"

[tasks]
py = "python"
build-pdf = "cd phase6_documentation/exec && pandoc REPORT.md -o REPORT.pdf --pdf-engine=xelatex -V geometry:margin=1in -V documentclass:article -V fontsize:11pt --number-sections --toc --filter pandoc-crossref --citeproc -V header-includes='\\usepackage{graphicx}\\setkeys{Gin}{width=0.45\\linewidth,keepaspectratio}'"
```

- [ ] **Step 2: Commit**

```bash
git add src/templates/pixi.toml
git commit -m "feat: update pixi.toml template for OpenPE dependencies"
```

---

## Task 5: Create Phase 0 Template

**Files:**
- Create: `src/templates/phase0_claude.md`

- [ ] **Step 1: Write the Phase 0 template**

Create `src/templates/phase0_claude.md`:

```markdown
# Phase 0: Discovery

> This phase is unique to OpenPE — it does not exist in the original slop-X framework.

You are conducting the Discovery phase for a **{{analysis_type}}** analysis.

**Start in plan mode.** Before any data acquisition, produce a plan:
what hypotheses you will generate, what data sources you will search for,
what the quality assessment criteria will be. Execute after the plan is set.

## Input Classification

Check `analysis_config.yaml` for `input_mode`:
- **Mode A (question only):** Generate hypotheses and acquire data autonomously.
- **Mode B (question + user data):** User data is in the path specified by `data_dir` in `.analysis_config`. Assess it with the same rigor as acquired data. Supplement gaps.
- **Mode C (question + context):** User-provided hypotheses are ONE candidate among your independently generated ones. They receive NO trust privilege.

## Steps

### 0.1 Question Decomposition
Parse the user's question (from `analysis_config.yaml:question`) into:
- **Domain**: What field(s) does this question belong to?
- **Entities**: What are the key variables/actors?
- **Relationships**: What connections does the question imply?
- **Timeframe**: What temporal scope?
- **Implied concerns**: What is the user really asking about?

### 0.2 First-Principles Hypothesization
- Generate ≥3 candidate first principles for the identified domain.
- For each principle, construct a falsifiable causal DAG.
- Each DAG edge must be labeled: `LITERATURE_SUPPORTED` | `THEORIZED` | `SPECULATIVE`
  (see DAG Label Taxonomy in the spec — these are pre-analysis labels).
- Assess initial EP for each edge using qualitative mapping:
  - Strong theoretical link → relevance 0.7
  - Moderate → 0.4
  - Weak → 0.2
- **Generate ≥2 competing DAGs** (avoid anchoring on your first hypothesis).

### 0.3 Data Requirements Derivation
For each DAG edge, determine what data variables are needed to test it.
Output a data requirements matrix: variable × source × priority.

### 0.4 Data Acquisition
- Use WebSearch to discover public data sources.
- Use wrapped APIs (FRED, World Bank) for structured data.
- For each acquired dataset, log in `data/registry.yaml`:
  - URL, retrieval date, API query parameters, file hash (SHA-256)
- Store raw files in `data/raw/`, processed files in `data/processed/`.
- If a required variable has no public data: state explicitly what analysis CANNOT be done.

### 0.5 Data Quality Assessment (HARD GATE)
For each dataset, assess:
- **Completeness**: % missing values, temporal coverage gaps
- **Consistency**: Cross-source agreement where overlapping
- **Bias assessment**: Sampling bias, survivorship bias, measurement methodology changes
- **Granularity**: Spatial/temporal resolution vs. what analysis requires
- **Verdict**: HIGH / MEDIUM / LOW

**Gate rule**: If overall quality is LOW, analysis proceeds with prominent warnings.
Never fabricate precision from poor data.

## Output Artifacts

- `exec/DISCOVERY.md` — Question decomposition + causal DAGs (mermaid) + first-principles hypotheses + data requirements matrix + initial EP assessments
- `data/` — Acquired raw and processed data
- `data/registry.yaml` — Full data provenance
- `exec/DATA_QUALITY.md` — Per-dataset quality assessment + gate decision

## Agent Profiles

Read these before starting:
- `.claude/agents/hypothesis-agent.md` — for steps 0.1-0.2
- `.claude/agents/data-acquisition-agent.md` — for steps 0.3-0.4
- `.claude/agents/data-quality-agent.md` — for step 0.5

## Non-Negotiable Rules

1. Never fabricate data. If data cannot be found, say so.
2. Always cite sources with URL + retrieval date.
3. User-provided data receives no trust privilege.
4. Generate competing hypotheses — never anchor on first idea.
```

- [ ] **Step 2: Commit**

```bash
git add src/templates/phase0_claude.md
git commit -m "feat: add Phase 0 (Discovery) template"
```

---

## Task 6: Create New Agent Profiles (4 agents)

**Files:**
- Create: `.claude/agents/hypothesis-agent.md`
- Create: `.claude/agents/data-acquisition-agent.md`
- Create: `.claude/agents/data-quality-agent.md`
- Create: `.claude/agents/projector-agent.md`

- [ ] **Step 1: Write hypothesis-agent.md**

Create `.claude/agents/hypothesis-agent.md`. Follow the depth and structure of existing agent profiles (see `lead-analyst.md` for the gold standard). Must include: frontmatter with tools/model, role description, initialization steps, mandatory checklist, output format, constraints. Full content provided in the spec Section 4.3 — expand to match slop-X agent depth (~200 lines).

Key sections:
- Frontmatter: tools (Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch), model: opus
- Role: First-principles identification and causal DAG construction
- Initialization: read experiment_log.md, analysis_config.yaml, memory L0+L1 if available
- Mandatory checklist: 8 items from spec Section 4.3
- Output format: DISCOVERY.md structure
- Constraints: never assume causation, always competing hypotheses, no trust privilege for user hypotheses

- [ ] **Step 2: Write data-acquisition-agent.md**

Create `.claude/agents/data-acquisition-agent.md`. Key sections:
- Frontmatter: tools (Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch), model: opus
- Role: Autonomous data discovery and acquisition from public sources
- Data providers: WebSearch (general), FRED API (economics), World Bank API (global development)
- Caching protocol: raw files with immutable naming, registry.yaml
- Fallback behavior: retry, alternative sources, explicit "data not found" declarations
- Output format: data/ directory structure + registry.yaml

- [ ] **Step 3: Write data-quality-agent.md**

Create `.claude/agents/data-quality-agent.md`. Key sections:
- Frontmatter: tools (Read, Bash, Grep, Glob), model: opus
- Role: Data quality assessment and gate decision
- Assessment dimensions: completeness, consistency, bias, granularity
- Verdict system: HIGH/MEDIUM/LOW with specific criteria for each
- Gate decision logic: LOW → proceed with warnings, never fabricate precision
- Output format: DATA_QUALITY.md structure (from spec Section 5.3)

- [ ] **Step 4: Write projector-agent.md**

Create `.claude/agents/projector-agent.md`. Key sections:
- Frontmatter: tools (Read, Write, Edit, Bash, Grep, Glob), model: opus
- Role: Forward projection from established causal relationships to endgame
- Scenario simulation: Monte Carlo with ≥3 scenarios
- Sensitivity analysis: ±X% impact ranking, controllable vs exogenous
- Endgame convergence detection: 4 categories (robust, fork, equilibrium, unstable)
- EP decay visualization: confidence bands widening over projection distance
- Output format: PROJECTION.md structure

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/hypothesis-agent.md .claude/agents/data-acquisition-agent.md .claude/agents/data-quality-agent.md .claude/agents/projector-agent.md
git commit -m "feat: add 4 new OpenPE agent profiles"
```

---

## Task 7: Rewrite Phase 1-3 Templates

**Files:**
- Modify: `src/templates/phase1_claude.md`
- Modify: `src/templates/phase2_claude.md`
- Modify: `src/templates/phase3_claude.md`

- [ ] **Step 1: Rewrite phase1_claude.md**

Replace full content. Key changes from slop-X:
- Remove: RAG corpus queries (search_lep_corpus, compare_measurements)
- Remove: "physics motivation", "sample inventory", HEP technique selection
- Add: Method selection (regression, diff-in-diff, synthetic control, etc.)
- Add: Initial EP assessment for each causal DAG edge
- Add: Chain planning (main chain depth, sub-chain expansion points)
- Add: Systematic uncertainty inventory (generalized)
- Reference: `.claude/agents/lead-analyst.md` (to be generalized in Task 8)
- Output: `exec/STRATEGY.md` with EP assessments and causal DAG visualization

- [ ] **Step 2: Rewrite phase2_claude.md**

Replace full content. Key changes:
- Remove: ROOT file inventory, MC sample checks, blinding region avoidance
- Add: Data cleaning + feature engineering
- Add: Exploratory analysis (distributions, trends, correlations)
- Add: Signal vs baseline preliminary separation
- Add: Variable ranking by EP contribution
- Reference: `.claude/agents/data-explorer.md` (to be generalized in Task 8)

- [ ] **Step 3: Rewrite phase3_claude.md**

Replace full content. This is the most complex template — maps to spec Phase 3. Key changes:
- Remove: event selection cuts, background estimation, HEP systematics
- Add: Signal extraction (patterns consistent with causal hypotheses)
- Add: Baseline estimation (null-hypothesis model)
- Add: Causal testing pipeline (3-refutation protocol with decision tree)
- Add: EP update using actual test results
- Add: Sub-chain expansion decision logic
- Add: Statistical model construction (from spec Phase 3 step 6)
- Add: Uncertainty quantification (statistical + systematic + total)
- Add: Context splitting note (steps 1-5 vs 6-7)
- Reference: `.claude/agents/analyst.md`, `.claude/agents/verifier.md`

- [ ] **Step 4: Commit**

```bash
git add src/templates/phase1_claude.md src/templates/phase2_claude.md src/templates/phase3_claude.md
git commit -m "feat: rewrite Phase 1-3 templates for OpenPE"
```

---

## Task 8: Create Phase 4-6 Templates

**Files:**
- Create: `src/templates/phase4_claude.md` (replaces old HEP phase4)
- Create: `src/templates/phase5_claude.md` (replaces old HEP phase5)
- Create: `src/templates/phase6_claude.md` (new)

- [ ] **Step 1: Write phase4_claude.md (Projection)**

Key content:
- Scenario simulation (Monte Carlo, ≥3 scenarios)
- Sensitivity analysis (causal lever ranking)
- Endgame convergence detection (4 categories)
- EP decay visualization
- Reference: `.claude/agents/projector-agent.md`
- Output: `exec/PROJECTION.md`, figures/

- [ ] **Step 2: Write phase5_claude.md (Verification)**

Key content:
- Independent reproduction of key results
- Data provenance audit (spot-check URLs and values)
- Logic audit (causal claims match refutation tests)
- EP verification (propagation chain correctness)
- Human gate protocol (what to present, approval options)
- Reference: `.claude/agents/verifier.md`
- Output: `exec/VERIFICATION.md`

- [ ] **Step 3: Write phase6_claude.md (Documentation)**

Key content:
- Report generation (6-section structure from spec)
- EP decay visualization (core report chart)
- Audit trail (every claim linked to source)
- PDF generation via pandoc
- Reference: `.claude/agents/report-writer.md`, `.claude/agents/plot-validator.md`
- Output: `exec/REPORT.md`, `REPORT.pdf`, `audit_trail/`

- [ ] **Step 4: Commit**

```bash
git add src/templates/phase4_claude.md src/templates/phase5_claude.md src/templates/phase6_claude.md
git commit -m "feat: add Phase 4 (Projection), 5 (Verification), 6 (Documentation) templates"
```

---

## Task 9: Rewrite Root Orchestrator Template

**Files:**
- Modify: `src/templates/root_claude.md`

This is the most critical file — it's the orchestrator's brain.

- [ ] **Step 1: Rewrite root_claude.md**

Key changes from slop-X version:
1. **Orchestrator loop**: Change from `[1, 2, 3, 4a, 4b, 4c, 5]` to `[0, 1, 2, 3, 4, 5, 6]`
2. **Phase 4 flow**: Remove 4a/4b/4c sub-phases. Phase 3 absorbs 4a work. Phase 5 has the human gate.
3. **Human gate**: Move from "after 4b" to "after Phase 5 (Verification)"
4. **Agent roster**: Update to OpenPE agent names (analyst, verifier, domain-reviewer, etc.)
5. **Methodology table**: Update phase definitions, remove HEP references
6. **Anti-patterns**: Generalize (remove "physics prompt", "ROOT files", etc.)
7. **Context splitting**: Add note about Phase 3 splitting (steps 1-5 vs 6-7)
8. **EP monitoring**: Orchestrator checks Joint_EP at sub-chain expansion points
9. **Memory loading**: At analysis start, copy global memory/ to analysis-local memory/
10. **Environment section**: Remove uproot/mplhep references, add pandas/dowhy

Preserve the structure and depth of the original — this file must be comprehensive.

- [ ] **Step 2: Verify template substitution works**

Run: `pixi run scaffold /tmp/test_root_template --type analysis`
Then: `head -20 /tmp/test_root_template/CLAUDE.md`
Expected: Title shows analysis name, no `{{name}}` placeholders remaining.

Clean up: `rm -rf /tmp/test_root_template`

- [ ] **Step 3: Commit**

```bash
git add src/templates/root_claude.md
git commit -m "feat: rewrite orchestrator template for OpenPE pipeline"
```

---

## Task 10: Generalize Retained Agent Profiles

**Files:**
- Modify: `.claude/agents/analyst.md` (was signal-lead.md)
- Modify: `.claude/agents/verifier.md` (was cross-checker.md)
- Modify: `.claude/agents/report-writer.md` (was note-writer.md)
- Modify: `.claude/agents/domain-reviewer.md` (was physics-reviewer.md)
- Modify: `.claude/agents/logic-reviewer.md` (was critical-reviewer.md)
- Modify: `.claude/agents/methods-reviewer.md` (was constructive-reviewer.md)
- Modify: `.claude/agents/lead-analyst.md`
- Modify: `.claude/agents/data-explorer.md`
- Modify: `.claude/agents/arbiter.md`
- Modify: `.claude/agents/plot-validator.md`
- Modify: `.claude/agents/ml-specialist.md`
- Modify: `.claude/agents/rendering-reviewer.md`

- [ ] **Step 1: Generalize analyst.md**

Key changes:
- Remove: particle physics terminology (event selection, physics cuts, jet calibration)
- Remove: ROOT/uproot/coffea references
- Add: Signal extraction as pattern filtering
- Add: Baseline estimation (null-hypothesis model)
- Add: Causal testing pipeline integration (DoWhy)
- Add: EP update protocol
- Add: Sub-chain expansion assessment
- Preserve: Overall structure, mandatory checklist pattern, output format rigor

- [ ] **Step 2: Generalize verifier.md**

Key changes:
- Remove: HEP cross-check programs (re-selection, alternative unfolding)
- Add: Independent result reproduction
- Add: Data provenance audit (spot-check URLs)
- Add: Logic audit (causal claims vs refutation results)
- Add: EP verification (propagation correctness)
- Preserve: Independence requirement (no shared context with analyst)

- [ ] **Step 3: Generalize remaining 10 agents**

For each agent:
- Remove HEP-specific terminology and references
- Add OpenPE terminology (EP, causal DAG, explanatory chain)
- Update phase references (e.g., "Phase 4a" → "Phase 3")
- Update agent name references in cross-references
- Preserve: structure depth, mandatory checklists, output formats

Each agent needs individual care — read the existing profile fully before modifying.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/
git commit -m "feat: generalize all retained agent profiles for OpenPE"
```

---

## Task 11: Update pyproject.toml

**Files:**
- Modify: `pyproject.toml` (root)

- [ ] **Step 1: Update root pyproject.toml**

The scaffolder CLI argument changes from `--type measurement|search` to `--type analysis` (with default). Update the task definition if needed, and ensure the `scaffold` task still works.

- [ ] **Step 2: Test scaffold command**

Run: `pixi run scaffold /tmp/test_e2e --type analysis`
Expected: Full directory structure created with all 7 phases, no errors.

Run: `ls /tmp/test_e2e/phase0_discovery/data/raw`
Expected: Directory exists.

Run: `cat /tmp/test_e2e/analysis_config.yaml`
Expected: Contains `input_mode`, `ep_thresholds`, no `blinding` or `channels`.

Clean up: `rm -rf /tmp/test_e2e`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: update root pyproject.toml for OpenPE scaffold command"
```

---

## Task 12: End-to-End Smoke Test

- [ ] **Step 1: Scaffold a full test analysis**

```bash
pixi run scaffold /tmp/openpe_smoke_test
```

Expected: Clean output, all 7 phase directories created.

- [ ] **Step 2: Verify all CLAUDE.md files exist and have no unsubstituted placeholders**

```bash
find /tmp/openpe_smoke_test -name "CLAUDE.md" -exec grep -l '{{' {} \;
```

Expected: No output (no unsubstituted placeholders).

- [ ] **Step 3: Verify all agent profiles exist**

```bash
ls .claude/agents/
```

Expected: 16 files (12 retained/renamed + 4 new).

- [ ] **Step 4: Verify no HEP terminology in templates**

```bash
grep -r "uproot\|ROOT file\|particle physics\|HEP\|detector\|collider\|luminosity\|cross.section" src/templates/
```

Expected: No matches (or only in comments explaining the heritage).

- [ ] **Step 5: Clean up and commit**

```bash
rm -rf /tmp/openpe_smoke_test
git add -A
git commit -m "chore: Sprint 1 complete — OpenPE foundation ready"
```

---

## Summary

| Task | Description | Files | Est. Effort |
|------|-------------|-------|-------------|
| 1 | Archive HEP agents | 6 moved | 2 min |
| 2 | Rename generalized agents | 6 renamed | 2 min |
| 3 | Update scaffolder | 2 files | 15 min |
| 4 | Update pixi.toml template | 1 file | 3 min |
| 5 | Create Phase 0 template | 1 file | 10 min |
| 6 | Create 4 new agent profiles | 4 files | 30 min |
| 7 | Rewrite Phase 1-3 templates | 3 files | 20 min |
| 8 | Create Phase 4-6 templates | 3 files | 15 min |
| 9 | Rewrite orchestrator template | 1 file | 25 min |
| 10 | Generalize retained agents | 12 files | 40 min |
| 11 | Update pyproject.toml | 1 file | 3 min |
| 12 | End-to-end smoke test | — | 5 min |
| **Total** | | **~40 files** | **~170 min** |
