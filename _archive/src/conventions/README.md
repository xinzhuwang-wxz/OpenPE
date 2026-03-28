# Physics Conventions

This directory contains accumulated domain knowledge for specific analysis
techniques. These are **not** part of the methodology specification — the spec
describes process (phases, reviews, gates), while conventions encode what
experienced analysts know about how to do specific things correctly.

## Relationship to the spec

The spec principle "no encoded physics" remains intact. The spec tells the
agent *that* it must evaluate systematic uncertainties; a conventions document
tells it *which* systematic sources are standard for a given technique. The
spec is stable across analysis types; conventions grow as the collaboration
gains experience.

Conventions are consulted, not blindly followed. If a convention doesn't
apply to a specific analysis, the agent documents why and proceeds. If a
convention is missing, the agent uses literature and RAG to fill the gap,
then adds what it learned here for future analyses.

## Structure

One file per analysis technique or method. Each file covers:

- When to use this technique
- Standard configuration and parameters
- Required validation checks
- Required systematic sources with rationale
- Known pitfalls

## Maintenance

- **Living documents.** Updated after each analysis that uses the technique.
- **Empirically grounded.** Entries come from actual analysis experience and
  published reference analyses, not from speculation.
- **Agent-maintained.** Agents update conventions when they encounter new
  knowledge. Human review before merging.
- **Consulted at Phase 1 (Strategy) and Phase 4a (Systematics).** The
  strategy phase uses conventions to plan the systematic program. The
  Phase 4a review checks completeness against conventions.
