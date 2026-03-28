"""Tests for report generator."""
import shutil
from pathlib import Path
from src.templates.scripts.report_generator import ReportBuilder

TMP = Path("/tmp/test_report_gen")


def setup_function():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)


def teardown_function():
    if TMP.exists():
        shutil.rmtree(TMP)


def test_render_empty_report():
    """Empty report has title and executive summary."""
    builder = ReportBuilder(analysis_name="Test Analysis", question="Why is X happening?")
    md = builder.render()
    assert "# Test Analysis" in md
    assert "Executive Summary" in md


def test_add_sections():
    builder = ReportBuilder(analysis_name="Test")
    builder.add_section("Findings", "Some findings here.")
    builder.add_section("Projection", "Future looks bright.")
    md = builder.render()
    assert "Findings" in md
    assert "Projection" in md
    assert "Some findings here." in md


def test_collect_from_phases():
    """Collect artifacts from a mock analysis directory."""
    # Create mock phase artifacts
    analysis_dir = TMP / "mock_analysis"
    for phase, artifact in [
        ("phase0_discovery", "DISCOVERY.md"),
        ("phase0_discovery", "DATA_QUALITY.md"),
        ("phase1_strategy", "STRATEGY.md"),
        ("phase3_analysis", "ANALYSIS.md"),
        ("phase4_projection", "PROJECTION.md"),
        ("phase5_verification", "VERIFICATION.md"),
    ]:
        exec_dir = analysis_dir / phase / "exec"
        exec_dir.mkdir(parents=True, exist_ok=True)
        (exec_dir / artifact).write_text(f"Content of {artifact}")

    builder = ReportBuilder(analysis_name="Mock", question="Test question")
    builder.collect_from_phases(analysis_dir)
    assert len(builder.sections) == 6
    md = builder.render()
    assert "Content of DISCOVERY.md" in md
    assert "Content of ANALYSIS.md" in md


def test_save_report():
    builder = ReportBuilder(analysis_name="Save Test")
    builder.add_section("Results", "Test results.")
    path = builder.save(TMP / "REPORT.md")
    assert path.exists()
    assert path.read_text().startswith("# Save Test")


def test_to_dict():
    builder = ReportBuilder(analysis_name="Dict Test", question="Q?")
    builder.add_section("S1", "Content")
    d = builder.to_dict()
    assert d["analysis_name"] == "Dict Test"
    assert len(d["sections"]) == 1


def test_missing_artifacts_handled():
    """Missing phase artifacts don't cause errors."""
    analysis_dir = TMP / "empty_analysis"
    analysis_dir.mkdir(parents=True)
    builder = ReportBuilder(analysis_name="Empty")
    builder.collect_from_phases(analysis_dir)
    assert len(builder.sections) == 0
    md = builder.render()
    assert "# Empty" in md  # still renders


def test_collect_figures():
    """collect_figures should find all PDF figures across phases."""
    analysis_dir = TMP / "analysis"
    for phase in ["phase2_exploration", "phase3_analysis", "phase4_projection"]:
        fig_dir = analysis_dir / phase / "figures"
        fig_dir.mkdir(parents=True)
        (fig_dir / "test_plot.pdf").write_text("fake pdf")
        (fig_dir / "test_plot.png").write_text("fake png")

    from report_generator import ReportBuilder
    builder = ReportBuilder(analysis_name="test", question="q")
    figures = builder.collect_figures(analysis_dir)
    assert len(figures) >= 3
    assert all(f.suffix == ".pdf" for f in figures)
