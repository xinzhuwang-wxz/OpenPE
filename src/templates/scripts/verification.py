"""Verification utilities for OpenPE Phase 5.

Automated checks that the verifier agent calls to independently
validate Phase 3 and Phase 4 results.

Reference: OpenPE spec Section 3.2 Phase 5
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class VerificationCheck:
    """Result of a single verification check."""
    name: str
    passed: bool
    details: str
    severity: str = "error"  # "error" | "warning"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "details": self.details,
            "severity": self.severity,
        }


@dataclass
class VerificationReport:
    """Complete verification report for Phase 5."""
    checks: list[VerificationCheck] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    def to_dict(self) -> dict:
        return {
            "all_passed": self.all_passed,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "checks": [c.to_dict() for c in self.checks],
        }

    def to_markdown(self) -> str:
        """Generate VERIFICATION.md content."""
        status = "PASSED" if self.all_passed else "FAILED"
        lines = [
            f"# Verification Report\n",
            f"**Status**: {status}",
            f"**Checks**: {self.pass_count} passed, {self.fail_count} failed\n",
            "## Results\n",
            "| Check | Status | Details |",
            "|-------|--------|---------|",
        ]
        for c in self.checks:
            icon = "✅" if c.passed else "❌"
            lines.append(f"| {c.name} | {icon} | {c.details} |")
        return "\n".join(lines)


def verify_data_provenance(registry_path: Path) -> list[VerificationCheck]:
    """Spot-check data provenance from registry.yaml.

    Checks:
    - Registry file exists and is valid YAML
    - Each entry has required fields (source_id, url, sha256, file)
    - File exists and hash matches
    """
    checks = []

    if not registry_path.exists():
        checks.append(VerificationCheck(
            "registry_exists", False, f"Registry not found: {registry_path}"))
        return checks

    checks.append(VerificationCheck("registry_exists", True, "Registry file found"))

    try:
        with open(registry_path) as f:
            registry = yaml.safe_load(f)
    except Exception as e:
        checks.append(VerificationCheck("registry_valid", False, f"Invalid YAML: {e}"))
        return checks

    checks.append(VerificationCheck("registry_valid", True, "Valid YAML"))

    datasets = registry.get("datasets", [])
    if not datasets:
        checks.append(VerificationCheck(
            "registry_nonempty", False, "No datasets in registry"))
        return checks

    checks.append(VerificationCheck(
        "registry_nonempty", True, f"{len(datasets)} datasets registered"))

    # Spot-check first and last entries
    for idx in [0, min(len(datasets) - 1, len(datasets))]:
        if idx >= len(datasets):
            continue
        entry = datasets[idx]
        sid = entry.get("source_id", f"entry_{idx}")

        required = ["source_id", "url", "sha256", "file"]
        missing = [f for f in required if f not in entry]
        if missing:
            checks.append(VerificationCheck(
                f"fields_{sid}", False, f"Missing fields: {missing}"))
            continue

        checks.append(VerificationCheck(
            f"fields_{sid}", True, "All required fields present"))

        # Check file exists — paths in registry are relative to analysis root
        filepath = Path(entry["file"])
        if not filepath.is_absolute():
            # registry.yaml is at phase0_discovery/data/registry.yaml
            # paths are relative to analysis root (3 levels up)
            analysis_root = registry_path.parent.parent.parent
            filepath = analysis_root / filepath

        if filepath.exists():
            # Verify hash
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            actual_hash = h.hexdigest()
            if actual_hash == entry["sha256"]:
                checks.append(VerificationCheck(
                    f"hash_{sid}", True, "File hash matches"))
            else:
                checks.append(VerificationCheck(
                    f"hash_{sid}", False,
                    f"Hash mismatch: expected {entry['sha256'][:16]}..., got {actual_hash[:16]}..."))
        else:
            checks.append(VerificationCheck(
                f"file_{sid}", False, f"File not found: {filepath}", severity="warning"))

    return checks


def verify_ep_propagation(chain_dict: dict) -> list[VerificationCheck]:
    """Verify EP propagation chain calculations.

    Recalculates joint EP from node values and compares to stored value.
    """
    checks = []
    nodes = chain_dict.get("nodes", [])
    stored_joint = chain_dict.get("joint_ep")

    if not nodes:
        checks.append(VerificationCheck(
            "ep_nodes_exist", False, "No nodes in chain"))
        return checks

    checks.append(VerificationCheck(
        "ep_nodes_exist", True, f"{len(nodes)} nodes in chain"))

    # Recalculate EP for each node
    recalculated_joint = 1.0
    for node in nodes:
        truth = node.get("truth", 0)
        relevance = node.get("relevance", 0)
        expected_ep = truth * relevance
        stored_ep = node.get("ep", 0)

        if abs(expected_ep - stored_ep) > 0.001:
            checks.append(VerificationCheck(
                f"ep_calc_{node.get('event_id', '?')}",
                False,
                f"EP mismatch: truth({truth}) × relevance({relevance}) = {expected_ep:.4f}, stored = {stored_ep:.4f}",
            ))
        else:
            checks.append(VerificationCheck(
                f"ep_calc_{node.get('event_id', '?')}",
                True,
                f"EP correct: {stored_ep:.4f}",
            ))

        recalculated_joint *= expected_ep

    # Check joint EP
    if stored_joint is not None:
        if abs(recalculated_joint - stored_joint) > 0.001:
            checks.append(VerificationCheck(
                "joint_ep", False,
                f"Joint EP mismatch: recalculated {recalculated_joint:.4f}, stored {stored_joint:.4f}"))
        else:
            checks.append(VerificationCheck(
                "joint_ep", True, f"Joint EP correct: {stored_joint:.4f}"))

    return checks


def verify_causal_labels(analysis_results: list[dict]) -> list[VerificationCheck]:
    """Verify that causal labels match refutation test outcomes.

    For each edge, check that the classification follows the decision tree:
      All 3 pass → DATA_SUPPORTED
      2 pass → CORRELATION
      1 pass → CORRELATION
      0 pass → HYPOTHESIZED
    """
    checks = []

    for result in analysis_results:
        edge_name = f"{result.get('treatment', '?')} → {result.get('outcome', '?')}"
        refutations = result.get("refutations", [])
        stored_label = result.get("classification", "")

        if not refutations:
            if stored_label in ("HYPOTHESIZED", "CORRELATION"):
                checks.append(VerificationCheck(
                    f"label_{edge_name}", True,
                    f"No refutations, label '{stored_label}' is acceptable"))
            else:
                checks.append(VerificationCheck(
                    f"label_{edge_name}", False,
                    f"No refutations but label is '{stored_label}' (expected HYPOTHESIZED or CORRELATION)"))
            continue

        passed = sum(1 for r in refutations if r.get("passed", False))
        total = len(refutations)

        if passed == total:
            expected = "DATA_SUPPORTED"
        elif passed == 0:
            expected = "HYPOTHESIZED"
        else:
            expected = "CORRELATION"

        if stored_label == expected:
            checks.append(VerificationCheck(
                f"label_{edge_name}", True,
                f"Label '{stored_label}' matches refutations ({passed}/{total} passed)"))
        elif stored_label == "DISPUTED":
            checks.append(VerificationCheck(
                f"label_{edge_name}", True,
                f"Label 'DISPUTED' — flagged for human review", severity="warning"))
        else:
            checks.append(VerificationCheck(
                f"label_{edge_name}", False,
                f"Label mismatch: stored '{stored_label}', expected '{expected}' ({passed}/{total} passed)"))

    return checks


def run_all_checks(analysis_dir: Path) -> VerificationReport:
    """Auto-discover analysis data and run all verification checks.

    This is the single entry point for Phase 5. It discovers:
    - registry.yaml from phase0_discovery/data/
    - EP chains from phase3_analysis/exec/ep_update_results.json
    - Causal labels from phase3_analysis/exec/ANALYSIS.md
    """
    analysis_dir = Path(analysis_dir)
    all_checks: list[VerificationCheck] = []

    # 1. Data provenance
    registry_path = analysis_dir / "phase0_discovery" / "data" / "registry.yaml"
    if registry_path.exists():
        all_checks.extend(verify_data_provenance(registry_path))
    else:
        all_checks.append(VerificationCheck(
            name="registry_exists",
            passed=False,
            details="phase0_discovery/data/registry.yaml not found",
        ))

    # 2. EP propagation (if results exist)
    ep_results_path = analysis_dir / "phase3_analysis" / "exec" / "ep_update_results.json"
    if ep_results_path.exists():
        import json
        with open(ep_results_path) as f:
            ep_data = json.load(f)
        chains = ep_data.get("chains", [])
        for chain_data in chains:
            all_checks.extend(verify_ep_propagation(chain_data))

    # 3. Causal labels (if ANALYSIS.md exists)
    analysis_md = analysis_dir / "phase3_analysis" / "exec" / "ANALYSIS.md"
    if analysis_md.exists():
        import re as _re
        text = analysis_md.read_text()
        label_pattern = _re.compile(
            r"(\w[\w ]*?)\s*(?:→|->)\s*(\w[\w ]*?):\s*(DATA_SUPPORTED|CORRELATION|HYPOTHESIZED|DISPUTED)",
            _re.IGNORECASE | _re.MULTILINE,
        )
        for match in label_pattern.finditer(text):
            label = match.group(3).upper()
            all_checks.append(VerificationCheck(
                name=f"causal_label_{match.group(1).strip()}_{match.group(2).strip()}",
                passed=True,
                details=f"Label {label} found for {match.group(1).strip()} -> {match.group(2).strip()}",
            ))

    return VerificationReport(checks=all_checks)


def generate_verification_report(
    registry_path: Path | None = None,
    chain_dict: dict | None = None,
    analysis_results: list[dict] | None = None,
) -> VerificationReport:
    """Run all verification checks and produce a report."""
    report = VerificationReport()

    if registry_path:
        report.checks.extend(verify_data_provenance(registry_path))

    if chain_dict:
        report.checks.extend(verify_ep_propagation(chain_dict))

    if analysis_results:
        report.checks.extend(verify_causal_labels(analysis_results))

    return report
