"""Tests for audit trail generator."""
import shutil
from pathlib import Path
import yaml
from src.templates.scripts.audit_trail import AuditTrail, Claim, MethodologyChoice

TMP = Path("/tmp/test_audit_trail")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_add_claim():
    trail = AuditTrail(analysis_name="test")
    trail.add_claim(
        claim_id="C1",
        text="Urbanization causes birth rate decline",
        source_type="analysis",
        source_ref="phase3_analysis/scripts/causal_test.py",
        evidence_type="DATA_SUPPORTED",
        confidence=0.85,
        phase="phase3",
    )
    assert len(trail.claims) == 1
    assert trail.claims[0].evidence_type == "DATA_SUPPORTED"


def test_add_methodology_choice():
    trail = AuditTrail(analysis_name="test")
    trail.add_methodology_choice(
        choice_id="M1",
        description="Used difference-in-differences for policy analysis",
        alternatives_considered=["Regression discontinuity", "Synthetic control"],
        justification="Panel data with clear pre/post periods available",
        phase="phase1",
    )
    assert len(trail.methodology_choices) == 1


def test_save_and_load():
    trail = AuditTrail(analysis_name="roundtrip_test")
    trail.add_claim(claim_id="C1", text="Test claim", source_type="data",
                    source_ref="data.csv", evidence_type="CORRELATION", confidence=0.6, phase="p3")
    trail.add_methodology_choice(choice_id="M1", description="Method A",
                                  alternatives_considered=["B"], justification="Because", phase="p1")

    claims_path, meth_path = trail.save(TMP / "audit")
    assert claims_path.exists()
    assert meth_path.exists()

    # Verify YAML content
    with open(claims_path) as f:
        data = yaml.safe_load(f)
    assert data["total_claims"] == 1
    assert data["claims"][0]["claim_id"] == "C1"

    # Roundtrip
    loaded = AuditTrail.load(TMP / "audit")
    assert loaded.analysis_name == "roundtrip_test"
    assert len(loaded.claims) == 1
    assert len(loaded.methodology_choices) == 1


def test_summary():
    trail = AuditTrail(analysis_name="summary_test")
    trail.add_claim(claim_id="C1", text="A", source_type="data", source_ref="x",
                    evidence_type="DATA_SUPPORTED", phase="p3")
    trail.add_claim(claim_id="C2", text="B", source_type="analysis", source_ref="y",
                    evidence_type="CORRELATION", phase="p3")
    trail.add_claim(claim_id="C3", text="C", source_type="projection", source_ref="z",
                    evidence_type="HYPOTHESIZED", phase="p4")

    s = trail.summary()
    assert s["total_claims"] == 3
    assert s["claims_by_evidence_type"]["DATA_SUPPORTED"] == 1
    assert s["claims_by_evidence_type"]["CORRELATION"] == 1
    assert s["claims_by_phase"]["p3"] == 2


def test_to_markdown():
    trail = AuditTrail(analysis_name="md_test")
    trail.add_claim(claim_id="C1", text="Test claim", source_type="data",
                    source_ref="data.csv", evidence_type="DATA_SUPPORTED", confidence=0.9)
    trail.add_methodology_choice(choice_id="M1", description="DiD",
                                  alternatives_considered=["RDD"], justification="Best fit")
    md = trail.to_markdown()
    assert "Audit Trail" in md
    assert "C1" in md
    assert "DATA_SUPPORTED" in md
    assert "DiD" in md


def test_empty_trail():
    trail = AuditTrail(analysis_name="empty")
    md = trail.to_markdown()
    assert "Total claims:** 0" in md
    s = trail.summary()
    assert s["total_claims"] == 0
