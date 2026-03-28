"""Tests for state_manager.py — STATE.md read/write/update."""
import shutil
from pathlib import Path

from state_manager import StateManager

TMP = Path("/tmp/test_state_manager")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_create_initial_state():
    sm = StateManager(TMP / "STATE.md", analysis_name="test_analysis")
    sm.save()
    assert (TMP / "STATE.md").exists()
    content = (TMP / "STATE.md").read_text()
    assert "Current phase**: 0" in content
    assert "initialized" in content


def test_advance_phase():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.advance_phase(0, artifact="DISCOVERY.md", review="4-bot PASS", notes="2 DAGs")
    content = (TMP / "STATE.md").read_text()
    assert "Current phase**: 1" in content
    assert "DISCOVERY.md" in content


def test_record_review_iteration():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.record_review_iteration(phase=0, issues_a=1, issues_b=2)
    sm.record_review_iteration(phase=0, issues_a=0, issues_b=0)
    assert sm.get_iteration_count(0) == 2


def test_iteration_warning_thresholds():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    for i in range(3):
        sm.record_review_iteration(phase=0, issues_a=1, issues_b=0)
    assert sm.should_warn(0) is True
    assert sm.should_hard_stop(0) is False


def test_iteration_hard_stop():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    for i in range(10):
        sm.record_review_iteration(phase=0, issues_a=1, issues_b=0)
    assert sm.should_hard_stop(0) is True


def test_add_blocker():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.add_blocker("Missing GDP data for 2024")
    content = (TMP / "STATE.md").read_text()
    assert "Missing GDP data" in content


def test_load_existing_state():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.advance_phase(0, artifact="DISCOVERY.md")

    sm2 = StateManager(TMP / "STATE.md")
    sm2.load()
    assert sm2.current_phase == 1


def test_data_callback_tracking():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    assert sm.can_data_callback() is True
    assert sm.record_data_callback("need GDP data") is True
    assert sm.record_data_callback("need trust survey") is True
    assert sm.can_data_callback() is False
    assert sm.record_data_callback("third attempt") is False  # denied


def test_full_state_roundtrip():
    """All state fields survive write → load (cross-session reliability)."""
    sm = StateManager(TMP / "STATE.md", analysis_name="roundtrip_test")
    sm.save()

    # Build up state across a simulated session
    sm.record_review_iteration(phase=0, issues_a=2, issues_b=1)
    sm.record_review_iteration(phase=0, issues_a=0, issues_b=0)
    sm.advance_phase(0, artifact="DISCOVERY.md", review="4-bot PASS", notes="2 DAGs")
    sm.advance_phase(1, artifact="STRATEGY.md", review="4-bot PASS")
    sm.add_blocker("Missing trust survey data")
    sm.record_data_callback("need trust data")

    # Simulate crash → restart: fresh object, load from disk
    sm2 = StateManager(TMP / "STATE.md")
    sm2.load()

    # All scalar fields restored
    assert sm2.analysis_name == "roundtrip_test"
    assert sm2.current_phase == 2
    assert sm2.data_callbacks_used == 1

    # Phase history restored
    assert len(sm2.phase_history) == 2
    assert sm2.phase_history[0]["artifact"] == "DISCOVERY.md"
    assert sm2.phase_history[1]["artifact"] == "STRATEGY.md"

    # Iteration counts restored
    assert sm2.get_iteration_count(0) == 2

    # Blockers restored
    assert len(sm2.blockers) == 1
    assert "trust survey" in sm2.blockers[0]

    # Can continue operating after load
    assert sm2.should_warn(0) is False  # 2 < 3
    assert sm2.can_data_callback() is True  # 1 < 2


def test_data_callback_persists_across_load():
    sm = StateManager(TMP / "STATE.md", analysis_name="test")
    sm.save()
    sm.record_data_callback("need GDP data")

    sm2 = StateManager(TMP / "STATE.md")
    sm2.load()
    assert sm2.data_callbacks_used == 1
    assert sm2.can_data_callback() is True

    sm2.record_data_callback("need trust survey")
    sm3 = StateManager(TMP / "STATE.md")
    sm3.load()
    assert sm3.data_callbacks_used == 2
    assert sm3.can_data_callback() is False
