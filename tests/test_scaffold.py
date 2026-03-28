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
    """Phase 0 has data/raw, data/processed."""
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


def test_memory_directory_created():
    """Memory directory structure is created for forward compatibility."""
    scaffold(TEST_DIR, "analysis")
    memory_dir = TEST_DIR / "memory"
    assert memory_dir.is_dir()
    assert (memory_dir / "L0_universal").is_dir()
    assert (memory_dir / "L1_domain").is_dir()
    assert (memory_dir / "L2_detailed").is_dir()
    assert (memory_dir / "causal_graph").is_dir()


def test_ep_thresholds_in_config():
    """analysis_config.yaml contains EP thresholds."""
    scaffold(TEST_DIR, "analysis")
    yaml_content = (TEST_DIR / "analysis_config.yaml").read_text()
    assert "hard_truncation: 0.05" in yaml_content
    assert "soft_truncation: 0.15" in yaml_content
    assert "subchain_expansion: 0.30" in yaml_content
