#!/usr/bin/env python
"""Scaffold a new analysis directory with per-phase CLAUDE.md files.

Usage:
    pixi run scaffold analyses/my_analysis --type measurement
    pixi run scaffold analyses/my_analysis --type search

The script creates the directory structure, generates CLAUDE.md files
from src/templates/, initializes a git repo, and creates the pixi environment.
The technique (unfolding, template fit, etc.) is determined during Phase 1,
not at scaffold time.
"""

import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"

# ---------------------------------------------------------------------------
# Conventions routing — determines which conventions files apply per type
# ---------------------------------------------------------------------------

CONVENTIONS_FOR_TYPE = {
    "measurement": (
        "- `conventions/unfolding.md` — for unfolded measurements\n"
        "- `conventions/extraction.md` — for extraction/counting measurements\n"
        "\n"
        "The technique selected in Phase 1 determines which file applies.\n"
        "Read the \"When this applies\" section of each to confirm."
    ),
    "search": (
        "- `conventions/search.md`"
    ),
}

# ---------------------------------------------------------------------------
# Phase directories
# ---------------------------------------------------------------------------

PHASES = [
    "phase1_strategy",
    "phase2_exploration",
    "phase3_selection",
    "phase4_inference",
    "phase5_documentation",
]

PHASE_SUBDIRS = ["exec", "scripts", "figures", "review", "review/plot-validation"]

PHASE_TEMPLATE_MAP = {
    "phase1_strategy": "phase1_claude.md",
    "phase2_exploration": "phase2_claude.md",
    "phase3_selection": "phase3_claude.md",
    "phase4_inference": "phase4_claude.md",
    "phase5_documentation": "phase5_claude.md",
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
        "conventions_files": CONVENTIONS_FOR_TYPE.get(analysis_type, ""),
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

        claude_path = phase_dir / "CLAUDE.md"
        template_name = PHASE_TEMPLATE_MAP.get(phase_name)
        if template_name and not claude_path.exists():
            template = _read_template(template_name)
            claude_path.write_text(_substitute(template, variables))
            print(f"  wrote {claude_path}")

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
            "# Set data_dir to the path where your input ROOT files live.\n"
            "# Add extra allow= lines for additional paths (one per line).\n"
            "data_dir=\n"
            "# allow=/path/to/mc/samples\n"
            "# allow=/path/to/calibration\n"
        )
        print(f"  wrote {config_path}")

    # Analysis-local pixi.toml from template
    pixi_path = analysis_dir / "pixi.toml"
    if not pixi_path.exists():
        template = _read_template("pixi.toml")
        pixi_path.write_text(template.replace("{name}", variables["name"]))
        print(f"  wrote {pixi_path}")

    # STATE.md for pipeline state tracking and resumption
    state_path = analysis_dir / "STATE.md"
    if not state_path.exists():
        state_path.write_text(
            "# Analysis State\n\n"
            f"- **Analysis**: {variables['name']}\n"
            "- **Current phase**: 1\n"
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
            "physics_prompt_path: prompt.md\n"
            "model_tier: auto\n"
            "channels: []  # populated during Phase 1\n"
            "calibrations: []  # populated during Phase 1\n"
            "cost_controls:\n"
            "  max_review_iterations: 10\n"
            "  review_warn_threshold: 3\n"
            "blinding:\n"
            "  active: true\n"
            "  approved_for_unblinding: false\n"
        )
        print(f"  wrote {yaml_config_path}")

    # regression_log.md
    regression_path = analysis_dir / "regression_log.md"
    if not regression_path.exists():
        regression_path.write_text("# Regression Log\n")
        print(f"  wrote {regression_path}")

    # Experiment log and retrieval log
    for log_name in ["experiment_log.md", "retrieval_log.md"]:
        log_path = analysis_dir / log_name
        if not log_path.exists():
            log_path.write_text(
                f"# {log_name.replace('_', ' ').replace('.md', '').title()}\n"
            )
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
            )
            print(f"  wrote {gitignore}")
        print(f"  initialized git repo")

    print(f"\nScaffolded {analysis_dir}/ ({analysis_type})")
    print(f"\nNext steps:")
    print(f"  1. Edit .analysis_config to set data_dir")
    print(f"  2. cd {analysis_dir} && pixi install")
    print(f"  3. claude   # starts the orchestrator agent")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new analysis with per-phase CLAUDE.md files."
    )
    parser.add_argument("dir", type=Path, help="Analysis directory to create")
    parser.add_argument(
        "--type",
        choices=["measurement", "search"],
        required=True,
        dest="analysis_type",
        help="Analysis type",
    )
    args = parser.parse_args()
    scaffold(args.dir, args.analysis_type)


if __name__ == "__main__":
    main()
