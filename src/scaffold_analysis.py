#!/usr/bin/env python
"""Scaffold a new OpenPE analysis directory with per-phase CLAUDE.md files.

Usage:
    pixi run scaffold analyses/my_analysis
    pixi run scaffold analyses/my_analysis --type analysis

The script creates the directory structure, generates CLAUDE.md files
from src/templates/, initializes a git repo, and creates the pixi environment.
"""

import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"

# ---------------------------------------------------------------------------
# Phase directories
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

# Extra subdirectories for specific phases
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


def scaffold(analysis_dir: Path, analysis_type: str):
    """Create the analysis directory structure with CLAUDE.md files."""
    analysis_dir.mkdir(parents=True, exist_ok=True)

    variables = {
        "name": analysis_dir.name,
        "analysis_type": analysis_type,
    }

    # Analysis-root CLAUDE.md from template
    root_claude = analysis_dir / "CLAUDE.md"
    if not root_claude.exists():
        try:
            template = _read_template("root_claude.md")
            root_claude.write_text(_substitute(template, variables))
            print(f"  wrote {root_claude}")
        except FileNotFoundError as e:
            print(f"  warning: {e}")
            root_claude.write_text(f"# {analysis_dir.name}\n\n> Template not yet created.\n")
            print(f"  wrote {root_claude} (placeholder)")

    # Per-phase directories and CLAUDE.md
    for phase_name in PHASES:
        phase_dir = analysis_dir / phase_name
        phase_dir.mkdir(exist_ok=True)
        for subdir in PHASE_SUBDIRS:
            (phase_dir / subdir).mkdir(exist_ok=True)

        # Extra subdirs for this phase
        for extra in PHASE_EXTRA_SUBDIRS.get(phase_name, []):
            (phase_dir / extra).mkdir(exist_ok=True)

        claude_path = phase_dir / "CLAUDE.md"
        template_name = PHASE_TEMPLATE_MAP.get(phase_name)
        if template_name and not claude_path.exists():
            try:
                template = _read_template(template_name)
                claude_path.write_text(_substitute(template, variables))
                print(f"  wrote {claude_path}")
            except FileNotFoundError as e:
                print(f"  warning: {e}")
                claude_path.write_text(f"# {phase_name}\n\n> Template not yet created.\n")
                print(f"  wrote {claude_path} (placeholder)")

    # Copy data acquisition helper scripts into Phase 0
    scripts_src = TEMPLATES / "scripts"
    scripts_dst = analysis_dir / "phase0_discovery" / "scripts"
    if scripts_src.exists():
        for script in scripts_src.glob("*.py"):
            dst = scripts_dst / script.name
            if not dst.exists():
                dst.write_text(script.read_text())
                print(f"  copied {dst}")

    # Memory directory for forward compatibility
    memory_dir = analysis_dir / "memory"
    for subdir in ["L0_universal", "L1_domain", "L2_detailed", "causal_graph"]:
        (memory_dir / subdir).mkdir(parents=True, exist_ok=True)
    print(f"  created memory/ structure")

    # Symlink conventions/, methodology/, and .claude/ into the analysis directory
    # Each analysis gets its own git repo, so Claude Code won't walk up to
    # the parent slopspec/.claude/. Symlinking ensures agents, skills, hooks,
    # and settings are available inside each analysis directory.
    conventions_link = analysis_dir / "conventions"
    conventions_src = HERE / "conventions"
    if not conventions_link.exists() and conventions_src.exists():
        conventions_link.symlink_to(conventions_src.resolve())
        print(f"  linked {conventions_link} -> {conventions_src}")

    methodology_link = analysis_dir / "methodology"
    methodology_src = HERE / "methodology"
    if not methodology_link.exists() and methodology_src.exists():
        methodology_link.symlink_to(methodology_src.resolve())
        print(f"  linked {methodology_link} -> {methodology_src}")

    claude_link = analysis_dir / ".claude"
    claude_src = HERE.parent / ".claude"
    if not claude_link.exists() and claude_src.exists():
        claude_link.symlink_to(claude_src.resolve())
        print(f"  linked {claude_link} -> {claude_src}")

    # .analysis_config (for isolation hook — set data_dir before running)
    config_path = analysis_dir / ".analysis_config"
    if not config_path.exists():
        config_path.write_text(
            "# The isolation hook allows access to these directories.\n"
            "# Set data_dir to the path where your input files live.\n"
            "# Add extra allow= lines for additional paths (one per line).\n"
            "data_dir=\n"
            "input_mode=A\n"
            "# allow=/path/to/additional/data\n"
        )
        print(f"  wrote {config_path}")

    # Analysis-local pixi.toml from template
    pixi_path = analysis_dir / "pixi.toml"
    if not pixi_path.exists():
        try:
            template = _read_template("pixi.toml")
            pixi_path.write_text(template.replace("{name}", variables["name"]))
            print(f"  wrote {pixi_path}")
        except FileNotFoundError as e:
            print(f"  warning: {e}")

    # STATE.md for pipeline state tracking and resumption
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
            f"analysis_type: {analysis_type}\n"
            "input_mode: A\n"
            "question: ''\n"
            "domain: ''\n"
            "model_tier: auto\n"
            "ep_thresholds:\n"
            "  hard_truncation: 0.05\n"
            "  soft_truncation: 0.15\n"
            "  subchain_expansion: 0.30\n"
            "cost_controls:\n"
            "  max_review_iterations: 10\n"
            "  review_warn_threshold: 3\n"
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
        # Create .gitignore
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
                "# SLURM logs\n"
                ".slurm_*.out\n"
                "\n"
                "# Raw data (large files, not tracked)\n"
                "phase0_discovery/data/raw/\n"
            )
            print(f"  wrote {gitignore}")
        print(f"  initialized git repo")

    print(f"\nScaffolded {analysis_dir}/ ({analysis_type})")
    print(f"\nNext steps:")
    print(f"  1. Edit .analysis_config to set data_dir and input_mode")
    print(f"  2. Edit analysis_config.yaml to set question and domain")
    print(f"  3. cd {analysis_dir} && pixi install")
    print(f"  4. claude   # starts the orchestrator agent")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new OpenPE analysis with per-phase CLAUDE.md files."
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
