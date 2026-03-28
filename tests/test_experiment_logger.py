"""Tests for experiment_logger.py — structured experiment log entries."""
import shutil
from pathlib import Path

from experiment_logger import ExperimentLogger

TMP = Path("/tmp/test_experiment_logger")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_append_entry():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(
        phase=0,
        agent="hypothesis_agent",
        decision="Generated 2 competing DAGs",
        rationale="Rogers diffusion theory vs trust-gated adoption",
    )
    content = log_path.read_text()
    assert "## [Phase 0]" in content
    assert "hypothesis_agent" in content
    assert "2 competing DAGs" in content


def test_multiple_entries_chronological():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(phase=0, agent="hypothesis_agent", decision="D1")
    logger.log(phase=1, agent="lead_analyst", decision="D2")
    content = log_path.read_text()
    assert content.index("Phase 0") < content.index("Phase 1")


def test_log_with_data_fields():
    log_path = TMP / "experiment_log.md"
    log_path.write_text("# Experiment Log\n")
    logger = ExperimentLogger(log_path)
    logger.log(
        phase=3,
        agent="analyst",
        decision="Used DoWhy for digital divide",
        rationale="Panel data supports causal identification",
        data={"method": "panel_FE", "n_observations": 710},
    )
    content = log_path.read_text()
    assert "panel_FE" in content
    assert "710" in content
