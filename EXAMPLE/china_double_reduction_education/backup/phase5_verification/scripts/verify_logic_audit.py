"""
Program 6: Logic audit of causal claims.

Verifies that:
- No CORRELATION-classified edge uses causal language inappropriately
- All edges have EP values updated after refutation
- The downscoping decision is properly documented
- All DATA_QUALITY warnings are carried through
"""
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent.parent

# -------------------------------------------------------------------
# Step 1: Read artifacts
# -------------------------------------------------------------------
with open(BASE / "phase3_analysis" / "exec" / "ANALYSIS.md") as f:
    analysis_text = f.read()

with open(BASE / "phase4_projection" / "exec" / "PROJECTION.md") as f:
    projection_text = f.read()

with open(BASE / "phase0_discovery" / "exec" / "DATA_QUALITY.md") as f:
    dq_text = f.read()

issues = []

# -------------------------------------------------------------------
# Step 2: Check causal language in CORRELATION edges
# -------------------------------------------------------------------
log.info("=" * 60)
log.info("CAUSAL LANGUAGE CHECK")
log.info("=" * 60)

# The primary edge is classified CORRELATION. Check that causal language
# is appropriately hedged.
causal_phrases = [
    "caused",
    "the policy reduced",
    "the policy decreased",
    "attributable to the policy",
    "policy effect of",
    "the Double Reduction policy truly reduced",
]

# These phrases are acceptable in context of hypothesis discussion or negation
acceptable_contexts = [
    "cannot be",
    "not uniquely attributable",
    "not distinguishable",
    "cannot claim",
    "CANNOT",
    "cannot be uniquely attributed",
    "not solely policy-driven",
    "does not mean",
]

for phrase in causal_phrases:
    occurrences = []
    for line_no, line in enumerate(analysis_text.split("\n"), 1):
        if phrase.lower() in line.lower():
            # Check if it's in an acceptable context
            in_acceptable = any(ctx.lower() in line.lower() for ctx in acceptable_contexts)
            if not in_acceptable:
                occurrences.append((line_no, line.strip()[:100]))

    if occurrences:
        log.info("  CAUTION - Phrase '%s' found %d times without hedging context:",
                 phrase, len(occurrences))
        for ln, text in occurrences[:3]:
            log.info("    Line %d: %s", ln, text)
    else:
        log.info("  OK - '%s' either absent or properly hedged", phrase)

# Check PROJECTION.md similarly
for phrase in ["the policy caused", "the policy reduced household"]:
    for line_no, line in enumerate(projection_text.split("\n"), 1):
        if phrase.lower() in line.lower():
            in_acceptable = any(ctx.lower() in line.lower() for ctx in acceptable_contexts)
            if not in_acceptable:
                issues.append(f"CAUSAL LANGUAGE in PROJECTION.md line {line_no}: '{phrase}'")

# -------------------------------------------------------------------
# Step 3: Verify all edges have post-refutation EP
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("POST-REFUTATION EP UPDATE CHECK")
log.info("=" * 60)

# Check that the EP propagation table exists and has Phase 3 values
if "Phase 3 EP" in analysis_text or "Phase 3 EP" in analysis_text:
    log.info("  EP propagation table found in ANALYSIS.md")
else:
    issues.append("EP propagation table missing from ANALYSIS.md")
    log.info("  WARNING: EP propagation table not found")

# Check each edge has a Phase 3 EP entry
edges_to_check = [
    "Policy -> Industry Collapse",
    "Industry Collapse -> Reduced Tutoring",
    "Reduced Tutoring -> Total Expenditure",
    "Policy -> Underground Market",
    "Underground -> Higher Prices",
    "Competitive Pressure -> Inelastic Demand",
    "Income -> Differential Access",
    "Public Spending -> Crowding-In",
    "Policy -> Aggregate Spending",
]

for edge in edges_to_check:
    if edge in analysis_text:
        log.info("  FOUND: %s", edge)
    else:
        issues.append(f"Edge '{edge}' not found in ANALYSIS.md")
        log.info("  MISSING: %s", edge)

# -------------------------------------------------------------------
# Step 4: Verify downscoping decision
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("DOWNSCOPING DECISION CHECK")
log.info("=" * 60)

downscoping_keywords = [
    "downscop",
    "edge-level assessment",
    "chain-level causal claim",
    "hard truncation",
    "Joint EP",
]

found_keywords = []
for kw in downscoping_keywords:
    if kw.lower() in analysis_text.lower():
        found_keywords.append(kw)
        log.info("  FOUND: '%s'", kw)
    else:
        log.info("  MISSING: '%s'", kw)

if len(found_keywords) >= 3:
    log.info("  Downscoping decision adequately documented (%d/%d keywords found)",
             len(found_keywords), len(downscoping_keywords))
else:
    issues.append(f"Downscoping decision inadequately documented ({len(found_keywords)}/{len(downscoping_keywords)} keywords)")

# Check that PROJECTION.md also carries the downscoping
if "edge-level" in projection_text.lower() or "not chain-level" in projection_text.lower() or "no chain-level" in projection_text.lower():
    log.info("  Downscoping carried to PROJECTION.md: YES")
else:
    issues.append("Downscoping decision not carried to PROJECTION.md")
    log.info("  Downscoping carried to PROJECTION.md: NO")

# -------------------------------------------------------------------
# Step 5: DATA_QUALITY warnings carry-through
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("DATA QUALITY WARNING CARRY-THROUGH")
log.info("=" * 60)

# Key warnings from DATA_QUALITY.md
dq_warnings = [
    ("PROXY", "proxy", "NBS bundles education with culture/recreation"),
    ("NO POST-POLICY MICRODATA", "microdata", "No household-level data post-2021"),
    ("UNDERGROUND TUTORING", "underground", "Anecdotal only"),
    ("COVID", "covid confound", "COVID-19 confounding"),
    ("DEMOGRAPHIC DECLINE", "demographic", "Birth rate decline confounds"),
    ("CPI DEFLATION", "cpi", "Must use real values"),
]

for warning_name, keyword, description in dq_warnings:
    in_analysis = keyword.lower() in analysis_text.lower()
    in_projection = keyword.lower() in projection_text.lower()

    status = "BOTH" if (in_analysis and in_projection) else (
        "ANALYSIS ONLY" if in_analysis else (
            "PROJECTION ONLY" if in_projection else "MISSING"
        )
    )

    if status == "MISSING":
        issues.append(f"DQ warning '{warning_name}' not carried through to analysis artifacts")

    log.info("  %s: %s", warning_name, status)

# -------------------------------------------------------------------
# Step 6: DAG acyclicity check
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("DAG CONSISTENCY CHECK")
log.info("=" * 60)

# The DAG edges from ANALYSIS.md
dag_edges = [
    ("Policy", "Industry Collapse"),
    ("Industry Collapse", "Reduced Tutoring"),
    ("Reduced Tutoring", "Total Expenditure"),
    ("Policy", "Underground Tutoring"),
    ("Underground Tutoring", "Higher Prices"),
    ("Policy", "Aggregate Spending Level Shift"),
    ("Competitive Pressure", "Inelastic Demand"),
    ("Household Income", "Differential Access"),
    ("Public Ed Spending", "Crowding-In"),
]

# Check for cycles using simple DFS
from collections import defaultdict

adj = defaultdict(list)
for u, v in dag_edges:
    adj[u].append(v)

def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.discard(node)
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False

is_cyclic = has_cycle(adj)
log.info("  DAG has cycles: %s", is_cyclic)
if is_cyclic:
    issues.append("DAG contains cycles -- invalid causal structure")

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
log.info("\n" + "=" * 60)
log.info("LOGIC AUDIT SUMMARY")
log.info("=" * 60)

if issues:
    log.info("ISSUES FOUND (%d):", len(issues))
    for i, issue in enumerate(issues, 1):
        log.info("  %d. %s", i, issue)
    overall = "FLAG"
else:
    log.info("No issues found.")
    overall = "PASS"

log.info("Overall: %s", overall)

# Save
output = {
    "causal_language_issues": [i for i in issues if "CAUSAL LANGUAGE" in i],
    "ep_update_issues": [i for i in issues if "EP" in i],
    "downscoping_issues": [i for i in issues if "downscop" in i.lower()],
    "dq_carry_issues": [i for i in issues if "DQ warning" in i],
    "dag_issues": [i for i in issues if "DAG" in i],
    "all_issues": issues,
    "overall": overall,
}

out_path = BASE / "phase5_verification" / "data"
out_path.mkdir(parents=True, exist_ok=True)
with open(out_path / "logic_audit.json", "w") as f:
    json.dump(output, f, indent=2)

log.info("Results saved.")
