# Methodology Specification

## Structure

The spec is organized into three tiers:

### Tier 1: Core analysis — "what to do"
- `03-phases.md` — Phase 1–5 definitions (requirements, deliverables, gates)

### Tier 2: Process and scaffolding — "how to manage it"
- `01-principles.md` — Scope and design principles
- `02-inputs.md` — Analysis prompt, RAG retrieval
- `04-orchestration.md` — Orchestrator loop, subagent management, context, scaling
- `05-artifacts.md` — Artifact format and experiment log
- `06-review.md` — Review protocol (classification, iteration, per-phase focus)
- `09-downscoping.md` — Scope management and feasibility

### Tier 3: Craft — "how to write good code, notes, and plots"
- `07-tools.md` — Tool preferences, paradigms, scale-out patterns
- `08-coding.md` — Git, code quality, testing, pixi tasks
- `appendix-plotting.md` — Figure template, sizing, labels, styling

### Appendices
- `appendix-dependencies.md` — Phase dependency graph
- `appendix-checklist.md` — Per-phase artifact checklists

## Reading guide

- **For a new analysis:** Read Tier 1 (phases) to understand what each phase does
- **For orchestration:** Read §3a for the agent coordination model
- **For coding:** Read Tier 3 for tool choices, code style, and plotting rules
- **Templates** (`src/templates/`) are thin references pointing to these files
