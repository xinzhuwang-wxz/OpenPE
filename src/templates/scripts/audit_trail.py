# Copyright 2025 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Max en Wong, 2026

"""Audit trail generator for OpenPE.

Generates machine-readable audit files linking every factual claim
to its data source and every inferential step to its methodology.

IGM/SSR/VAR patterns borrowed from ACG Protocol (UGVP):
- IGM: Inline Grounding Markers embedded in report text
- SSR: Structured Source Registry tracking data provenance
- VAR: Veracity Audit Registry tracking inferential logic

Reference: OpenPE spec Section 3.2 Phase 6, Step 3
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

import yaml


# --- ACG Protocol structures (adapted from UGVP protocol) ---

SHI_PREFIX_LENGTH = 10  # Source Hash Identifier prefix length


def compute_shi(content: str | bytes) -> str:
    """Compute Source Hash Identifier (SHA-256) for a data source."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def construct_igm(claim_id: str, source_hash: str, location: str) -> str:
    """Construct an Inline Grounding Marker (IGM).

    Format: [C1:a1b2c3d4e5:phase3/data.csv:row42]
    Borrowed from ACG Protocol ugvp_protocol.py construct_igm().
    """
    prefix = source_hash[:SHI_PREFIX_LENGTH]
    return f"[{claim_id}:{prefix}:{location}]"


def construct_rm(relation_id: str, relation_type: str, dep_claims: list[str]) -> str:
    """Construct a Relationship Marker (RM).

    Format: (R1:INFERENCE:C1,C2)
    Borrowed from ACG Protocol ugvp_protocol.py construct_relationship_marker().
    """
    deps = ",".join(dep_claims)
    return f"({relation_id}:{relation_type}:{deps})"


@dataclass
class SourceRecord:
    """Structured Source Registry (SSR) entry.

    Tracks data provenance with verification status.
    Borrowed from ACG Protocol SSR format.
    """
    shi: str                # SHA-256 of source content
    source_type: str        # "dataset" | "api" | "literature" | "computation"
    uri: str                # canonical location (URL, file path, API endpoint)
    location: str = ""      # specific selector (row, column, page, etc.)
    chunk_id: str = ""      # version/chunk identifier
    verification_status: str = "PENDING"  # VERIFIED | FAILED | PENDING

    @property
    def composite_key(self) -> str:
        return f"{self.shi[:SHI_PREFIX_LENGTH]}-{self.chunk_id}" if self.chunk_id else self.shi[:SHI_PREFIX_LENGTH]

    def to_dict(self) -> dict:
        return {
            "shi": self.shi,
            "source_type": self.source_type,
            "uri": self.uri,
            "location": self.location,
            "chunk_id": self.chunk_id,
            "verification_status": self.verification_status,
        }


@dataclass
class VeracityRecord:
    """Veracity Audit Registry (VAR) entry.

    Tracks inferential logic with dependency chain verification.
    Borrowed from ACG Protocol VAR format.
    """
    relation_id: str
    relation_type: str              # "INFERENCE" | "SUMMARY" | "CAUSAL_CLAIM"
    dependent_claims: list[str]     # [C1, C2, ...] — claim IDs this depends on
    synthesis_prose: str = ""       # human-readable explanation of the inference
    audit_status: str = "PENDING"   # VERIFIED_LOGIC | INSUFFICIENT_PREMISE | PENDING
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "relation_id": self.relation_id,
            "relation_type": self.relation_type,
            "dependent_claims": self.dependent_claims,
            "synthesis_prose": self.synthesis_prose,
            "audit_status": self.audit_status,
            "timestamp": self.timestamp,
        }


# --- Original OpenPE structures ---


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
    sources: list[SourceRecord] = field(default_factory=list)
    veracity: list[VeracityRecord] = field(default_factory=list)

    def add_claim(self, **kwargs) -> Claim:
        claim = Claim(**kwargs)
        self.claims.append(claim)
        return claim

    def add_methodology_choice(self, **kwargs) -> MethodologyChoice:
        choice = MethodologyChoice(**kwargs)
        self.methodology_choices.append(choice)
        return choice

    def add_source(self, **kwargs) -> SourceRecord:
        record = SourceRecord(**kwargs)
        self.sources.append(record)
        return record

    def add_veracity(self, **kwargs) -> VeracityRecord:
        record = VeracityRecord(**kwargs)
        self.veracity.append(record)
        return record

    def verify_logic(self) -> None:
        """Run ACG-style logical verification on veracity records.

        For each veracity record, check if all dependent claims have been
        verified (evidence_type != HYPOTHESIZED). Update audit_status.
        Borrowed from ACG Protocol agent.py Phase 2 verification.
        """
        claim_map = {c.claim_id: c for c in self.claims}
        for var in self.veracity:
            all_verified = True
            for dep_id in var.dependent_claims:
                claim = claim_map.get(dep_id)
                if claim is None or claim.evidence_type == "HYPOTHESIZED":
                    all_verified = False
                    break
            var.audit_status = "VERIFIED_LOGIC" if all_verified else "INSUFFICIENT_PREMISE"

    def save(self, output_dir: Path) -> tuple[Path, Path]:
        """Save claims.yaml, methodology.yaml, sources.yaml, veracity.yaml."""
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

        # ACG Protocol registries
        if self.sources:
            sources_path = output_dir / "sources.yaml"
            with open(sources_path, "w") as f:
                yaml.dump(
                    {"sources": [s.to_dict() for s in self.sources]},
                    f, default_flow_style=False, sort_keys=False,
                )

        if self.veracity:
            veracity_path = output_dir / "veracity.yaml"
            with open(veracity_path, "w") as f:
                yaml.dump(
                    {"veracity": [v.to_dict() for v in self.veracity]},
                    f, default_flow_style=False, sort_keys=False,
                )

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

        sources_path = output_dir / "sources.yaml"
        if sources_path.exists():
            with open(sources_path) as f:
                data = yaml.safe_load(f)
            for sd in data.get("sources", []):
                trail.sources.append(SourceRecord(**sd))

        veracity_path = output_dir / "veracity.yaml"
        if veracity_path.exists():
            with open(veracity_path) as f:
                data = yaml.safe_load(f)
            for vd in data.get("veracity", []):
                trail.veracity.append(VeracityRecord(**vd))

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

        if self.sources:
            lines.append("\n## Source Registry (SSR)\n")
            lines.append("| SHI | Type | URI | Status |")
            lines.append("|-----|------|-----|--------|")
            for s in self.sources:
                lines.append(
                    f"| {s.shi[:SHI_PREFIX_LENGTH]}... | {s.source_type} "
                    f"| {s.uri} | {s.verification_status} |"
                )

        if self.veracity:
            lines.append("\n## Veracity Audit (VAR)\n")
            lines.append("| Relation | Type | Dependencies | Status |")
            lines.append("|----------|------|-------------|--------|")
            for v in self.veracity:
                deps = ", ".join(v.dependent_claims)
                lines.append(
                    f"| {v.relation_id} | {v.relation_type} "
                    f"| {deps} | {v.audit_status} |"
                )

        return "\n".join(lines)
