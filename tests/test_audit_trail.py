"""Tests for audit trail generator."""
import shutil
from pathlib import Path
import yaml
from src.templates.scripts.audit_trail import AuditTrail, Claim, MethodologyChoice
from src.templates.scripts.audit_trail import (
    SourceRecord, VeracityRecord,
    compute_shi, construct_igm, construct_rm,
)

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


def test_compute_shi():
    sha = compute_shi("hello world")
    assert len(sha) == 64
    assert sha == compute_shi("hello world")
    assert sha != compute_shi("different")


def test_construct_igm():
    igm = construct_igm("C1", "abcdef1234567890abcdef", "phase3/data.csv:row42")
    assert igm == "[C1:abcdef1234:phase3/data.csv:row42]"


def test_construct_rm():
    rm = construct_rm("R1", "CAUSAL_CLAIM", ["C1", "C2"])
    assert rm == "(R1:CAUSAL_CLAIM:C1,C2)"


def test_source_record():
    sr = SourceRecord(shi="abc123", source_type="dataset",
                      uri="https://api.worldbank.org/test",
                      verification_status="VERIFIED")
    d = sr.to_dict()
    assert d["shi"] == "abc123"
    assert d["verification_status"] == "VERIFIED"


def test_veracity_record():
    vr = VeracityRecord(relation_id="R1", relation_type="INFERENCE",
                        dependent_claims=["C1", "C2"])
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
