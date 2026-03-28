"""Sprint 4 integration: report generation + audit trail from mock analysis."""
import shutil
from pathlib import Path
from src.templates.scripts.report_generator import ReportBuilder
from src.templates.scripts.audit_trail import AuditTrail

TMP = Path("/tmp/test_s4_integration")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_full_report_with_audit_trail():
    """Build mock analysis → generate report → generate audit trail → verify linkage."""
    analysis_dir = TMP / "mock"

    # Create mock phase artifacts
    artifacts = {
        "phase0_discovery/exec/DISCOVERY.md": "## First Principles\nUrbanization drives birth rate decline.",
        "phase0_discovery/exec/DATA_QUALITY.md": "## Data Quality\nOverall: MEDIUM",
        "phase1_strategy/exec/STRATEGY.md": "## Strategy\nMethod: difference-in-differences",
        "phase3_analysis/exec/ANALYSIS.md": "## Analysis\nurbanization → birth_rate: DATA_SUPPORTED (EP=0.47)",
        "phase4_projection/exec/PROJECTION.md": "## Projection\nEndgame: EQUILIBRIUM",
        "phase5_verification/exec/VERIFICATION.md": "## Verification\nAll checks passed.",
    }
    for path, content in artifacts.items():
        full = analysis_dir / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)

    # Generate report
    builder = ReportBuilder(analysis_name="Birth Rate Analysis", question="Why is birth rate declining?")
    builder.collect_from_phases(analysis_dir)
    report_path = builder.save(analysis_dir / "phase6_documentation" / "exec" / "REPORT.md")

    assert report_path.exists()
    report = report_path.read_text()
    assert "Birth Rate Analysis" in report
    assert "DATA_SUPPORTED" in report
    assert "EQUILIBRIUM" in report

    # Generate audit trail
    trail = AuditTrail(analysis_name="Birth Rate Analysis")
    trail.add_claim(
        claim_id="C1", text="Urbanization drives birth rate decline",
        source_type="analysis", source_ref="phase3_analysis/scripts/causal_test.py",
        evidence_type="DATA_SUPPORTED", confidence=0.85, phase="phase3",
    )
    trail.add_methodology_choice(
        choice_id="M1", description="Difference-in-differences",
        alternatives_considered=["Synthetic control", "IV regression"],
        justification="Panel data with clear policy change timing",
        phase="phase1",
    )

    audit_dir = analysis_dir / "phase6_documentation" / "audit_trail"
    claims_path, meth_path = trail.save(audit_dir)
    assert claims_path.exists()
    assert meth_path.exists()

    # Verify audit trail content
    loaded = AuditTrail.load(audit_dir)
    assert len(loaded.claims) == 1
    assert loaded.claims[0].evidence_type == "DATA_SUPPORTED"
    summary = loaded.summary()
    assert summary["total_claims"] == 1
    assert summary["claims_by_evidence_type"]["DATA_SUPPORTED"] == 1
