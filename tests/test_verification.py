"""Tests for verification utilities."""
from pathlib import Path
import yaml
import hashlib
import pytest
from src.templates.scripts.verification import (
    verify_data_provenance,
    verify_ep_propagation,
    verify_causal_labels,
    generate_verification_report,
)

TMP = Path("/tmp/test_verification")


def setup_function():
    TMP.mkdir(parents=True, exist_ok=True)


def teardown_function():
    import shutil
    if TMP.exists():
        shutil.rmtree(TMP)


def test_provenance_missing_registry():
    checks = verify_data_provenance(TMP / "nonexistent.yaml")
    assert not checks[0].passed
    assert "not found" in checks[0].details


def test_provenance_valid_registry():
    # Create a test file and registry
    data_file = TMP / "test.csv"
    data_file.write_text("a,b\n1,2\n")
    file_hash = hashlib.sha256(data_file.read_bytes()).hexdigest()

    registry = {
        "datasets": [{
            "source_id": "test_001",
            "url": "https://example.com/data.csv",
            "sha256": file_hash,
            "file": str(data_file),
        }]
    }
    reg_path = TMP / "registry.yaml"
    with open(reg_path, "w") as f:
        yaml.dump(registry, f)

    checks = verify_data_provenance(reg_path)
    assert all(c.passed for c in checks)


def test_provenance_hash_mismatch():
    data_file = TMP / "test2.csv"
    data_file.write_text("x,y\n3,4\n")

    registry = {
        "datasets": [{
            "source_id": "test_002",
            "url": "https://example.com",
            "sha256": "wrong_hash",
            "file": str(data_file),
        }]
    }
    reg_path = TMP / "registry.yaml"
    with open(reg_path, "w") as f:
        yaml.dump(registry, f)

    checks = verify_data_provenance(reg_path)
    hash_check = [c for c in checks if "hash" in c.name]
    assert len(hash_check) > 0
    assert not hash_check[0].passed


def test_ep_propagation_correct():
    chain = {
        "nodes": [
            {"event_id": "e1", "truth": 0.85, "relevance": 0.55, "ep": 0.4675},
            {"event_id": "e2", "truth": 0.70, "relevance": 0.30, "ep": 0.21},
        ],
        "joint_ep": 0.0982,  # 0.4675 * 0.21
    }
    checks = verify_ep_propagation(chain)
    assert all(c.passed for c in checks)


def test_ep_propagation_wrong_joint():
    chain = {
        "nodes": [
            {"event_id": "e1", "truth": 0.85, "relevance": 0.55, "ep": 0.4675},
        ],
        "joint_ep": 0.99,  # wrong!
    }
    checks = verify_ep_propagation(chain)
    joint_check = [c for c in checks if c.name == "joint_ep"]
    assert len(joint_check) > 0
    assert not joint_check[0].passed


def test_causal_labels_correct():
    results = [{
        "treatment": "X",
        "outcome": "Y",
        "classification": "DATA_SUPPORTED",
        "refutations": [
            {"test_name": "placebo", "passed": True},
            {"test_name": "random_common_cause", "passed": True},
            {"test_name": "data_subset", "passed": True},
        ],
    }]
    checks = verify_causal_labels(results)
    assert all(c.passed for c in checks)


def test_causal_labels_mismatch():
    results = [{
        "treatment": "A",
        "outcome": "B",
        "classification": "DATA_SUPPORTED",  # wrong! only 1/3 passed
        "refutations": [
            {"test_name": "placebo", "passed": True},
            {"test_name": "random_common_cause", "passed": False},
            {"test_name": "data_subset", "passed": False},
        ],
    }]
    checks = verify_causal_labels(results)
    label_checks = [c for c in checks if "label" in c.name]
    assert not label_checks[0].passed


def test_full_report():
    chain = {
        "nodes": [{"event_id": "e1", "truth": 0.8, "relevance": 0.5, "ep": 0.4}],
        "joint_ep": 0.4,
    }
    report = generate_verification_report(chain_dict=chain)
    assert report.all_passed
    md = report.to_markdown()
    assert "PASSED" in md
