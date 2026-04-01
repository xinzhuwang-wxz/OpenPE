# Copyright 2026 OpenPE Contributors — Licensed under GPL-3.0
# Modified by Maxen Wong, 2026

"""Post-analysis session commit for OpenPE.

Extracts experiences from completed analysis artifacts and commits
them to the memory store and causal knowledge graph. Optionally
grows domain packs from accumulated L1 experiences.

Also supports promoting high-confidence findings to global memory
(at the spec root) so they persist across analyses.

Reference: OpenPE spec — Memory System Design, Session Commit
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

import yaml

# Ensure sibling scripts are importable when invoked as `pixi run py scripts/session_commit.py`
sys.path.insert(0, str(Path(__file__).parent))
from memory_store import MemoryEntry, MemoryStore
from causal_knowledge_graph import CausalKnowledgeGraph


@dataclass
class Experience:
    """An extracted experience from a completed analysis."""

    experience_type: str  # "domain" | "method" | "data_source" | "failure"
    content: str
    domain: str
    source_phase: str
    confidence: float = 0.5


def extract_experiences(analysis_dir: Path) -> list[Experience]:
    """Parse phase artifacts and extract reusable experiences.

    Scans DISCOVERY.md, DATA_QUALITY.md, STRATEGY.md, ANALYSIS.md,
    PROJECTION.md, VERIFICATION.md for extractable lessons.
    """
    analysis_dir = Path(analysis_dir)
    experiences: list[Experience] = []

    # Read analysis config for domain
    config_path = analysis_dir / "analysis_config.yaml"
    domain = "general"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
        domain = config.get("domain", "general")

    # Phase artifact extractors
    _extract_from_discovery(analysis_dir, domain, experiences)
    _extract_from_data_quality(analysis_dir, domain, experiences)
    _extract_from_strategy(analysis_dir, domain, experiences)
    _extract_from_analysis(analysis_dir, domain, experiences)
    _extract_from_verification(analysis_dir, domain, experiences)

    return experiences


def _find_artifact(analysis_dir: Path, filename: str) -> Path | None:
    """Search phase directories for an artifact file."""
    for phase_dir in sorted(analysis_dir.glob("phase*")):
        candidate = phase_dir / filename
        if candidate.exists():
            return candidate
        exec_dir = phase_dir / "exec"
        if exec_dir.exists():
            candidate = exec_dir / filename
            if candidate.exists():
                return candidate
    return None


def _extract_from_discovery(analysis_dir: Path, domain: str, out: list[Experience]) -> None:
    path = _find_artifact(analysis_dir, "DISCOVERY.md")
    if path is None:
        return
    text = path.read_text()

    # Extract named data sources (lines with URL, API, or dataset name patterns)
    source_lines = []
    for line in text.split("\n"):
        l = line.strip()
        if any(kw in l.lower() for kw in ["fred", "world bank", "wbgapi", "fredapi",
                                            "census", "oecd", "eurostat", "kaggle",
                                            "api", "dataset", "registry"]):
            if len(l) > 10 and not l.startswith("#"):
                source_lines.append(l[:120])
    if source_lines:
        out.append(Experience(
            experience_type="data_source",
            content=f"[{domain}] Data sources: " + " | ".join(source_lines[:3]),
            domain=domain,
            source_phase="phase0_discovery",
            confidence=0.55,
        ))

    # Extract initial EP values for primary edges
    ep_pattern = re.compile(r"([\w\s]+?)\s*[→\->]+\s*([\w\s]+?)\s*[:\|]\s*EP\s*[=:]\s*(0\.\d+)", re.IGNORECASE)
    ep_matches = ep_pattern.findall(text)
    if ep_matches:
        ep_summary = "; ".join(f"{s.strip()}→{t.strip()} EP={v}" for s, t, v in ep_matches[:4])
        out.append(Experience(
            experience_type="domain",
            content=f"[{domain}] Prior EP estimates from discovery: {ep_summary}",
            domain=domain,
            source_phase="phase0_discovery",
            confidence=0.55,
        ))


def _extract_from_data_quality(analysis_dir: Path, domain: str, out: list[Experience]) -> None:
    path = _find_artifact(analysis_dir, "DATA_QUALITY.md")
    if path is None:
        return
    text = path.read_text()

    # Extract specific dataset quality verdicts
    low_lines, medium_lines = [], []
    for line in text.split("\n"):
        l = line.strip()
        if "low" in l.lower() and ("quality" in l.lower() or "|" in l):
            low_lines.append(l[:100])
        elif "medium" in l.lower() and ("quality" in l.lower() or "|" in l):
            medium_lines.append(l[:100])

    if low_lines:
        out.append(Experience(
            experience_type="failure",
            content=f"[{domain}] LOW quality datasets: " + " | ".join(low_lines[:3]),
            domain=domain,
            source_phase="phase0_discovery",
            confidence=0.65,
        ))
    if medium_lines:
        out.append(Experience(
            experience_type="data_source",
            content=f"[{domain}] MEDIUM quality datasets (usable with caveats): " + " | ".join(medium_lines[:2]),
            domain=domain,
            source_phase="phase0_discovery",
            confidence=0.55,
        ))


def _extract_from_strategy(analysis_dir: Path, domain: str, out: list[Experience]) -> None:
    path = _find_artifact(analysis_dir, "STRATEGY.md")
    if path is None:
        return
    text = path.read_text()

    # Extract method choices with context (which edge uses which method)
    method_map: dict[str, list[str]] = {}
    edge_pattern = re.compile(
        r"([\w][\w\s\-]+?)\s*[→\->]+\s*([\w][\w\s\-]+?).*?"
        r"(DiD|diff.in.diff|IV|instrumental.variable|RDD|regression.discontinuity|"
        r"synthetic.control|ITS|interrupted.time|propensity|granger|Bayesian|bayesian)",
        re.IGNORECASE,
    )
    for m in edge_pattern.finditer(text):
        method = m.group(3).strip().lower()
        edge = f"{m.group(1).strip()}→{m.group(2).strip()}"
        method_map.setdefault(method, []).append(edge)

    if method_map:
        summary = "; ".join(f"{meth}: {', '.join(edges[:2])}" for meth, edges in list(method_map.items())[:4])
        out.append(Experience(
            experience_type="method",
            content=f"[{domain}] Causal methods selected — {summary}",
            domain=domain,
            source_phase="phase1_strategy",
            confidence=0.65,
        ))
    else:
        # Fallback: keyword scan
        found = [m for m in ["DiD", "IV", "RDD", "synthetic control", "ITS", "granger", "propensity score"]
                 if m.lower() in text.lower()]
        if found:
            out.append(Experience(
                experience_type="method",
                content=f"[{domain}] Causal methods used: {', '.join(found)}",
                domain=domain,
                source_phase="phase1_strategy",
                confidence=0.60,
            ))

    # Extract primary edge EP values from strategy
    ep_pattern = re.compile(r"([\w\s\-]+?)\s*[→\->]+\s*([\w\s\-]+?)\s*[:\|].*?EP\s*[=:]\s*(0\.\d+)", re.IGNORECASE)
    ep_hits = ep_pattern.findall(text)
    high_ep = [(s.strip(), t.strip(), v) for s, t, v in ep_hits if float(v) >= 0.30]
    if high_ep:
        ep_summary = "; ".join(f"{s}→{t} EP={v}" for s, t, v in high_ep[:4])
        out.append(Experience(
            experience_type="domain",
            content=f"[{domain}] High-EP edges (≥0.30) in strategy: {ep_summary}",
            domain=domain,
            source_phase="phase1_strategy",
            confidence=0.65,
        ))


def _extract_from_analysis(analysis_dir: Path, domain: str, out: list[Experience]) -> None:
    path = _find_artifact(analysis_dir, "ANALYSIS.md")
    if path is None:
        return
    text = path.read_text()

    # Extract specific edge classifications with effect sizes
    class_pattern = re.compile(
        r"\|\s*([\w][\w\s\-]+?)\s*\|\s*([\w][\w\s\-]+?)\s*\|.*?"
        r"(DATA_SUPPORTED|CORRELATION|HYPOTHESIZED|DISPUTED)",
        re.IGNORECASE,
    )
    classified: dict[str, list[str]] = {"DATA_SUPPORTED": [], "CORRELATION": [],
                                         "HYPOTHESIZED": [], "DISPUTED": []}
    for m in class_pattern.finditer(text):
        label = m.group(3).upper()
        edge = f"{m.group(1).strip()}→{m.group(2).strip()}"
        classified.setdefault(label, []).append(edge)

    for label, edges in classified.items():
        if edges:
            conf = {"DATA_SUPPORTED": 0.75, "CORRELATION": 0.65,
                    "HYPOTHESIZED": 0.55, "DISPUTED": 0.40}.get(label, 0.60)
            out.append(Experience(
                experience_type="domain",
                content=f"[{domain}] {label}: {', '.join(edges[:4])}",
                domain=domain,
                source_phase="phase3_analysis",
                confidence=conf,
            ))

    # Extract effect sizes for DATA_SUPPORTED edges
    effect_pattern = re.compile(
        r"([\w][\w\s\-]+?)\s*[→\->]+\s*([\w][\w\s\-]+?).*?"
        r"(?:effect|estimate|coefficient)[:\s]+([+-]?[0-9]+\.?[0-9]*)\s*"
        r"(?:\(.*?CI[:\s]+\[?([+-]?[0-9.]+)[,\s]+([+-]?[0-9.]+)\]?\))?",
        re.IGNORECASE,
    )
    effect_hits = effect_pattern.findall(text)
    if effect_hits:
        effects = "; ".join(
            f"{s.strip()}→{t.strip()} β={est}"
            + (f" CI=[{lo},{hi}]" if lo and hi else "")
            for s, t, est, lo, hi in effect_hits[:3]
        )
        out.append(Experience(
            experience_type="domain",
            content=f"[{domain}] Effect estimates: {effects}",
            domain=domain,
            source_phase="phase3_analysis",
            confidence=0.70,
        ))


def _extract_from_verification(analysis_dir: Path, domain: str, out: list[Experience]) -> None:
    path = _find_artifact(analysis_dir, "VERIFICATION.md")
    if path is None:
        return
    text = path.read_text()

    # Extract specific failure descriptions (lines near FAIL keyword)
    lines = text.split("\n")
    fail_contexts = []
    for i, line in enumerate(lines):
        if "fail" in line.lower() and len(line.strip()) > 10:
            context = line.strip()
            # grab next non-empty line for more context
            for j in range(i + 1, min(i + 3, len(lines))):
                if lines[j].strip():
                    context += " | " + lines[j].strip()[:80]
                    break
            fail_contexts.append(context[:150])

    if fail_contexts:
        out.append(Experience(
            experience_type="failure",
            content=f"[{domain}] Verification failures: " + " || ".join(fail_contexts[:2]),
            domain=domain,
            source_phase="phase5_verification",
            confidence=0.70,
        ))

    # Extract reproduction success/failure for specific findings
    repro_pattern = re.compile(r"(reproduced?|replicated?|confirmed?)[:\s]+([\w\s\-→]+)", re.IGNORECASE)
    repro_hits = repro_pattern.findall(text)
    if repro_hits:
        repro_summary = "; ".join(f"{verb} {target[:60]}" for verb, target in repro_hits[:3])
        out.append(Experience(
            experience_type="domain",
            content=f"[{domain}] Verification reproduction: {repro_summary}",
            domain=domain,
            source_phase="phase5_verification",
            confidence=0.70,
        ))


def _generate_l2_summary(
    analysis_dir: Path,
    analysis_id: str,
) -> MemoryEntry | None:
    """Generate an L2 summary entry from analysis artifacts."""
    analysis_dir = Path(analysis_dir)

    config_path = analysis_dir / "analysis_config.yaml"
    domain = "general"
    question = ""
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
        domain = config.get("domain", domain)
        question = config.get("question", "")

    parts = []
    if question:
        parts.append(f"Question: {question}")

    for artifact_name in ["DISCOVERY.md", "ANALYSIS.md", "VERIFICATION.md"]:
        path = _find_artifact(analysis_dir, artifact_name)
        if path:
            text = path.read_text()
            for line in text.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("|") and not line.startswith("-"):
                    parts.append(f"{artifact_name}: {line[:120]}")
                    break

    if not parts:
        return None

    return MemoryEntry(
        memory_id=f"{analysis_id}_summary_0",
        content=" | ".join(parts),
        domain=domain,
        memory_type="domain",
        tier="L2",
        confidence=0.6,  # must be >= GLOBAL_PROMOTION_THRESHOLD to reach global memory
        source_analysis=analysis_id,
    )


def commit_session(
    analysis_dir: Path,
    memory_store: MemoryStore,
    causal_graph: CausalKnowledgeGraph,
    analysis_id: str = "",
) -> list[MemoryEntry]:
    """Extract experiences and commit to memory store + causal graph.

    Idempotent: safe to call multiple times with the same analysis_id
    (e.g., after a crash and restart). Uses a commit marker file to
    prevent double-decay on re-invocation.

    Returns the list of newly created memory entries.
    """
    if not analysis_id:
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    analysis_dir = Path(analysis_dir)

    # Idempotency guard: prevent double-decay on re-invocation
    commit_marker = analysis_dir / "memory" / f".committed_{analysis_id}"
    already_committed = commit_marker.exists()

    if not already_committed:
        # Apply decay only on first commit (not on re-run after crash)
        memory_store.apply_decay()

    # Extract experiences
    experiences = extract_experiences(analysis_dir)

    # Commit to memory store
    new_entries = []
    for i, exp in enumerate(experiences):
        # L0 entries are created via promote_tier() (corroboration across analyses),
        # not via single-analysis extraction. The "principle" type is reserved for
        # manual seeding (e.g., user explicitly declares a universal principle).
        tier = "L0" if exp.experience_type == "principle" else "L1"
        entry = MemoryEntry(
            memory_id=f"{analysis_id}_{exp.experience_type}_{i}",
            content=exp.content,
            domain=exp.domain,
            memory_type=exp.experience_type,
            tier=tier,
            confidence=exp.confidence,
            source_analysis=analysis_id,
        )
        memory_store.add(entry)
        new_entries.append(entry)

    # Extract causal relationships from ANALYSIS.md artifacts
    _commit_causal_findings(analysis_dir, causal_graph, analysis_id)

    causal_graph.save()

    # Write commit marker for idempotency
    commit_marker.parent.mkdir(parents=True, exist_ok=True)
    commit_marker.write_text(datetime.now().isoformat())

    # Generate L2 analysis summary
    l2_entry = _generate_l2_summary(analysis_dir, analysis_id)
    if l2_entry:
        memory_store.add(l2_entry)
        new_entries.append(l2_entry)

    # Seed L0 universal principles on first commit (idempotent)
    seed_l0_principles(memory_store)

    # Tier transitions: promote well-corroborated L1→L0, demote contradicted L0→L1, forget stale
    memory_store.load_all()
    for mid in list(memory_store.entries.keys()):
        memory_store.promote_tier(mid)
        memory_store.demote_tier(mid)
    memory_store.forget()

    return new_entries


def _commit_causal_findings(
    analysis_dir: Path,
    graph: CausalKnowledgeGraph,
    analysis_id: str,
) -> None:
    """Extract causal findings from analysis artifacts into the graph."""
    path = _find_artifact(analysis_dir, "ANALYSIS.md")
    if path is None:
        return
    text = path.read_text()

    # Parse causal relationship patterns:
    # "X → Y: DATA_SUPPORTED" or "X causes Y (DATA_SUPPORTED)"
    arrow_pattern = re.compile(
        r"^(\w[\w ]*?)\s*(?:→|->|-->)+\s*(\w[\w ]*?):\s*(DATA_SUPPORTED|CORRELATION|HYPOTHESIZED)",
        re.IGNORECASE | re.MULTILINE,
    )
    for match in arrow_pattern.finditer(text):
        source = match.group(1).strip()
        target = match.group(2).strip()
        classification = match.group(3).upper()

        rel_type = {
            "DATA_SUPPORTED": "CAUSES",
            "CORRELATION": "CORRELATED_WITH",
            "HYPOTHESIZED": "HYPOTHESIZED",
        }.get(classification, "HYPOTHESIZED")

        confidence = {"CAUSES": 0.7, "CORRELATED_WITH": 0.4, "HYPOTHESIZED": 0.2}.get(rel_type, 0.2)

        # Check for contradictions before adding
        graph.detect_contradictions(source, target, rel_type, analysis_id)
        graph.add_relationship(
            source=source,
            target=target,
            relationship_type=rel_type,
            confidence=confidence,
            analysis_id=analysis_id,
        )


def grow_domain_pack(
    memory_store: MemoryStore,
    domain: str,
    output_dir: Path,
) -> Path:
    """Generate or update a domain pack YAML from accumulated L1 memories.

    Returns the path to the generated domain pack file.
    """
    entries = memory_store.load_for_analysis(domain)
    domain_entries = [e for e in entries if e.tier == "L1" and e.domain == domain]

    pack = {
        "domain": domain,
        "generated": datetime.now().isoformat(),
        "source_memories": len(domain_entries),
        "experiences": {},
    }

    for entry_type in ("domain", "method", "data_source", "failure"):
        typed = [e for e in domain_entries if e.memory_type == entry_type]
        if typed:
            pack["experiences"][entry_type] = [
                {"content": e.content, "confidence": round(e.confidence, 3)}
                for e in typed
            ]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pack_path = output_dir / f"{domain}.yaml"
    with open(pack_path, "w") as f:
        yaml.dump(pack, f, default_flow_style=False, sort_keys=False)

    return pack_path


# --- Global Memory Promotion ---

# Only entries with confidence above this threshold are promoted to global.
GLOBAL_PROMOTION_THRESHOLD = 0.6


def promote_to_global(
    analysis_dir: Path,
    global_memory_dir: Path,
    min_confidence: float = GLOBAL_PROMOTION_THRESHOLD,
) -> dict:
    """Promote high-confidence findings from analysis-local memory to global.

    This enables cross-analysis learning: domain knowledge, method
    experiences, and causal relationships persist across separate analyses.

    Args:
        analysis_dir: analysis root (contains memory/ and memory/causal_graph/)
        global_memory_dir: spec-root memory/ directory
        min_confidence: only promote entries above this confidence

    Returns:
        dict with counts: {"memories_promoted": int, "graph_edges_promoted": int}
    """
    analysis_dir = Path(analysis_dir)
    global_memory_dir = Path(global_memory_dir)
    stats = {"memories_promoted": 0, "graph_edges_promoted": 0}

    # Promote memory entries (L0 and L1 only — L2 is analysis-specific detail)
    # MemoryStore uses short tier names: L0, L1, L2
    for tier in ["L0", "L1"]:
        src_dir = analysis_dir / "memory" / tier
        dst_dir = global_memory_dir / tier
        if not src_dir.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)

        for entry_file in src_dir.glob("*.yaml"):
            with open(entry_file) as f:
                data = yaml.safe_load(f)
            if data and data.get("confidence", 0) >= min_confidence:
                dst = dst_dir / entry_file.name
                if dst.exists():
                    # Merge: keep higher confidence version
                    with open(dst) as f:
                        existing = yaml.safe_load(f) or {}
                    if data.get("confidence", 0) > existing.get("confidence", 0):
                        shutil.copy2(str(entry_file), str(dst))
                        stats["memories_promoted"] += 1
                else:
                    shutil.copy2(str(entry_file), str(dst))
                    stats["memories_promoted"] += 1

    # Promote causal graph relationships
    local_graph_path = analysis_dir / "memory" / "causal_graph" / "graph.json"
    global_graph_path = global_memory_dir / "causal_graph" / "graph.json"

    if local_graph_path.exists():
        global_graph_path.parent.mkdir(parents=True, exist_ok=True)

        local_graph = CausalKnowledgeGraph(local_graph_path)
        local_graph.load()

        global_graph = CausalKnowledgeGraph(global_graph_path)
        if global_graph_path.exists():
            global_graph.load()

        for rel in local_graph.relationships.values():
            if rel.confidence >= min_confidence and rel.is_valid:
                existing = global_graph.relationships.get(rel.edge_id)
                if existing:
                    # Corroborate if already exists
                    if rel.source_analyses:
                        existing.corroborate(rel.source_analyses[0])
                else:
                    global_graph.relationships[rel.edge_id] = rel
                stats["graph_edges_promoted"] += 1

        global_graph.save()

    return stats


# --- CLI ---

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OpenPE session commit / memory load")
    p.add_argument("--analysis-id", default="", help="Analysis identifier (e.g. my_analysis_20260402)")
    p.add_argument("--global-memory", default="", help="Path to spec-root memory/ directory")
    p.add_argument("--load-only", action="store_true",
                   help="Only load and print memory context (no commit)")
    p.add_argument("--domain", default="general", help="Domain for --load-only mode")
    p.add_argument("--analysis-dir", default=".", help="Analysis root directory (default: cwd)")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    analysis_dir = Path(args.analysis_dir).resolve()
    local_memory = analysis_dir / "memory"

    if args.load_only:
        # Print memory context string for injection into phase_context_N.md
        store = MemoryStore(local_memory)
        entries = store.load_for_analysis(args.domain)
        if not entries:
            print("## Prior Experience\n\n(none)")
        else:
            print("## Prior Experience\n")
            print(store.to_context_string(entries))
        return

    # Full commit flow
    if not args.analysis_id:
        print("ERROR: --analysis-id required for commit mode", file=sys.stderr)
        sys.exit(1)

    store = MemoryStore(local_memory)
    graph_path = local_memory / "causal_graph" / "graph.json"
    from causal_knowledge_graph import CausalKnowledgeGraph
    graph = CausalKnowledgeGraph(graph_path)
    if graph_path.exists():
        graph.load()

    new_entries = commit_session(analysis_dir, store, graph, args.analysis_id)
    print(f"Committed {len(new_entries)} memory entries for {args.analysis_id}")

    if args.global_memory:
        stats = promote_to_global(analysis_dir, Path(args.global_memory))
        print(f"Promoted to global: {stats['memories_promoted']} memories, "
              f"{stats['graph_edges_promoted']} graph edges")


if __name__ == "__main__":
    main()


# --- L0 Seed Principles ---

L0_PRINCIPLES: list[dict] = [
    {
        "memory_id": "openpe_principle_refutation_battery",
        "content": (
            "Every full-analysis causal edge requires exactly 3 refutation tests: "
            "(1) placebo treatment at correct time/place, (2) random common cause "
            "(truly random variable), (3) data subset (drop 20-30% at random). "
            "DATA_SUPPORTED requires 3/3 PASS. No exceptions."
        ),
        "memory_type": "principle",
        "confidence": 0.95,
    },
    {
        "memory_id": "openpe_principle_ep_arithmetic",
        "content": (
            "EP updates must be applied mechanically from the classification→truth table: "
            "DATA_SUPPORTED → truth=min(1.0,max(0.8,prior+0.2)); "
            "CORRELATION → truth unchanged; "
            "HYPOTHESIZED → truth=min(0.3,prior-0.1); "
            "DISPUTED → truth=0.1. No subjective overrides."
        ),
        "memory_type": "principle",
        "confidence": 0.95,
    },
    {
        "memory_id": "openpe_principle_four_numbers",
        "content": (
            "Every result must carry exactly 4 numbers: central value, statistical "
            "uncertainty, systematic uncertainty, total uncertainty. A result without "
            "all four is incomplete regardless of how clear the signal is."
        ),
        "memory_type": "principle",
        "confidence": 0.95,
    },
    {
        "memory_id": "openpe_principle_dowhy_required",
        "content": (
            "Causal inference must use DoWhy — not ad-hoc regression. DoWhy enforces "
            "explicit DAG specification, estimand derivation, and refutation testing. "
            "Pure regression without backdoor/frontdoor identification is not causal."
        ),
        "memory_type": "principle",
        "confidence": 0.92,
    },
    {
        "memory_id": "openpe_principle_two_methods",
        "content": (
            "Every primary causal edge requires at least 2 independent estimation methods. "
            "If methods disagree by >50% in point estimate or differ in sign, the edge "
            "cannot be classified higher than CORRELATION regardless of refutation results."
        ),
        "memory_type": "principle",
        "confidence": 0.92,
    },
    {
        "memory_id": "openpe_principle_ep_threshold",
        "content": (
            "EP thresholds: Joint_EP >= 0.30 → full analysis with refutation battery. "
            "0.15 <= Joint_EP < 0.30 → lightweight assessment (primary method only). "
            "0.05 <= Joint_EP < 0.15 → soft truncation, no analysis. "
            "Joint_EP < 0.05 → hard truncation, mark chain as resolved."
        ),
        "memory_type": "principle",
        "confidence": 0.95,
    },
    {
        "memory_id": "openpe_principle_data_callback_limit",
        "content": (
            "Data callbacks are capped at 2 per analysis. LOW quality callback data "
            "on a high-EP edge (EP > 0.30) must escalate to human — do not proceed "
            "automatically. LOW quality on EP <= 0.30 → auto-downgrade to lightweight."
        ),
        "memory_type": "principle",
        "confidence": 0.90,
    },
    {
        "memory_id": "openpe_principle_carry_forward_warnings",
        "content": (
            "All warnings from upstream phases must be explicitly carried forward: "
            "data quality warnings from Phase 0, assumption concerns from Phase 2, "
            "method caveats from Phase 1. Nothing is silently dropped. Each downstream "
            "artifact must have a section acknowledging prior-phase warnings."
        ),
        "memory_type": "principle",
        "confidence": 0.90,
    },
]


def seed_l0_principles(memory_store: MemoryStore) -> list[str]:
    """Write universal OpenPE principles to L0 if not already present.

    Safe to call multiple times — skips entries that already exist.
    Returns list of memory_ids written.
    """
    memory_store.load_all()
    written = []
    for spec in L0_PRINCIPLES:
        mid = spec["memory_id"]
        if mid in memory_store.entries:
            continue  # already seeded
        entry = MemoryEntry(
            memory_id=mid,
            content=spec["content"],
            domain="general",
            memory_type=spec["memory_type"],  # type: ignore[arg-type]
            tier="L0",
            confidence=spec["confidence"],
            source_analysis="openpe_spec",
        )
        memory_store.add(entry)
        written.append(mid)
    return written
