"""Audit trail generator for OpenPE.

Generates machine-readable audit files linking every factual claim
to its data source and every inferential step to its methodology.

Reference: OpenPE spec Section 3.2 Phase 6, Step 3
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

import yaml


@dataclass
class Claim:
    """A factual claim in the report with provenance."""
    claim_id: str
    text: str
    source_type: str  # "data" | "analysis" | "projection" | "literature"
    source_ref: str   # path to data file, script, or citation
    evidence_type: str = "DATA_SUPPORTED"  # DATA_SUPPORTED | CORRELATION | HYPOTHESIZED
    confidence: float = 0.5
    phase: str = ""   # which phase produced this claim

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "source_type": self.source_type,
            "source_ref": self.source_ref,
            "evidence_type": self.evidence_type,
            "confidence": round(self.confidence, 3),
            "phase": self.phase,
        }


@dataclass
class MethodologyChoice:
    """A methodology choice with justification."""
    choice_id: str
    description: str
    alternatives_considered: list[str]
    justification: str
    phase: str = ""

    def to_dict(self) -> dict:
        return {
            "choice_id": self.choice_id,
            "description": self.description,
            "alternatives_considered": self.alternatives_considered,
            "justification": self.justification,
            "phase": self.phase,
        }


@dataclass
class AuditTrail:
    """Complete audit trail for an OpenPE analysis."""
    analysis_name: str
    claims: list[Claim] = field(default_factory=list)
    methodology_choices: list[MethodologyChoice] = field(default_factory=list)

    def add_claim(self, **kwargs) -> Claim:
        claim = Claim(**kwargs)
        self.claims.append(claim)
        return claim

    def add_methodology_choice(self, **kwargs) -> MethodologyChoice:
        choice = MethodologyChoice(**kwargs)
        self.methodology_choices.append(choice)
        return choice

    def save(self, output_dir: Path) -> tuple[Path, Path]:
        """Save claims.yaml and methodology.yaml to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)

        claims_path = output_dir / "claims.yaml"
        claims_data = {
            "analysis_name": self.analysis_name,
            "generated": datetime.now().isoformat(),
            "total_claims": len(self.claims),
            "claims": [c.to_dict() for c in self.claims],
        }
        with open(claims_path, "w") as f:
            yaml.dump(claims_data, f, default_flow_style=False, sort_keys=False)

        methodology_path = output_dir / "methodology.yaml"
        methodology_data = {
            "analysis_name": self.analysis_name,
            "generated": datetime.now().isoformat(),
            "total_choices": len(self.methodology_choices),
            "choices": [m.to_dict() for m in self.methodology_choices],
        }
        with open(methodology_path, "w") as f:
            yaml.dump(methodology_data, f, default_flow_style=False, sort_keys=False)

        return claims_path, methodology_path

    @classmethod
    def load(cls, output_dir: Path) -> AuditTrail:
        """Load audit trail from claims.yaml and methodology.yaml."""
        claims_path = output_dir / "claims.yaml"
        methodology_path = output_dir / "methodology.yaml"

        trail = cls(analysis_name="")

        if claims_path.exists():
            with open(claims_path) as f:
                data = yaml.safe_load(f)
            trail.analysis_name = data.get("analysis_name", "")
            for cd in data.get("claims", []):
                trail.claims.append(Claim(**cd))

        if methodology_path.exists():
            with open(methodology_path) as f:
                data = yaml.safe_load(f)
            if not trail.analysis_name:
                trail.analysis_name = data.get("analysis_name", "")
            for md in data.get("choices", []):
                trail.methodology_choices.append(MethodologyChoice(**md))

        return trail

    def summary(self) -> dict:
        """Generate summary statistics of the audit trail."""
        by_type = {}
        for c in self.claims:
            by_type[c.evidence_type] = by_type.get(c.evidence_type, 0) + 1

        by_phase = {}
        for c in self.claims:
            by_phase[c.phase] = by_phase.get(c.phase, 0) + 1

        return {
            "total_claims": len(self.claims),
            "total_methodology_choices": len(self.methodology_choices),
            "claims_by_evidence_type": by_type,
            "claims_by_phase": by_phase,
        }

    def to_markdown(self) -> str:
        """Generate audit trail section for the report."""
        lines = [
            "# Audit Trail\n",
            f"**Analysis:** {self.analysis_name}",
            f"**Total claims:** {len(self.claims)}",
            f"**Methodology choices:** {len(self.methodology_choices)}\n",
        ]

        if self.claims:
            lines.append("## Claims Provenance\n")
            lines.append("| ID | Claim | Evidence | Source | Confidence |")
            lines.append("|-----|-------|----------|--------|------------|")
            for c in self.claims:
                lines.append(
                    f"| {c.claim_id} | {c.text[:60]}{'...' if len(c.text) > 60 else ''} "
                    f"| {c.evidence_type} | {c.source_ref} | {c.confidence:.2f} |"
                )

        if self.methodology_choices:
            lines.append("\n## Methodology Choices\n")
            for m in self.methodology_choices:
                lines.append(f"### {m.choice_id}: {m.description}")
                lines.append(f"**Justification:** {m.justification}")
                if m.alternatives_considered:
                    lines.append(f"**Alternatives:** {', '.join(m.alternatives_considered)}")
                lines.append("")

        return "\n".join(lines)
