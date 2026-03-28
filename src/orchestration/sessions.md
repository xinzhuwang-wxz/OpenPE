# Orchestration Guide

> See `../methodology/03a-orchestration.md` for the architectural rationale.
> See `agents.md` for the agent prompt templates that populate this layout.

How to execute the methodology specification using Claude Code or any
multi-session LLM agent system.

## Core Principle: Session Isolation

Every agent invocation — execution, review, arbitration — is a **separate,
isolated session** with explicitly defined inputs and outputs. No shared
conversation history, no shared memory, no implicit state. Each session
reads files, writes files, and exits. The files are the interface.

```
┌─────────────┐     ┌──────────┐     ┌──────────────┐
│   inputs/   │────►│  agent   │────►│   outputs/   │
│  (read-only)│     │ session  │     │  (new files) │
└─────────────┘     └──────────┘     └──────────────┘
                         │
                         ▼
                    session.log
                (full conversation transcript)
```

**Exception: the experiment log.** Each phase has an `experiment_log.md` that
persists across executor sessions within that phase. Every executor session
reads the existing log and appends to it. This is the only mutable shared state
within a phase — it prevents agents from re-trying failed approaches and gives
humans visibility into decision-making.

**Concurrency note:** Parallel tracks (per-channel work in Phase 3, concurrent
calibrations) each have their own experiment log in their own directory. The
experiment log is shared only across *sequential* sessions within a single
track — never across parallel agents. If sub-agents within a single session
need to append to the same log, they must do so sequentially.

## Agent Session Identity

Every agent session is assigned a **session name** — a random human first name
(e.g., "Gerald", "Margaret", "Tomoko"). The orchestrator draws from a pool of
names and never reuses a name within an analysis run. This serves two purposes:

1. **Traceability.** Every file produced by a session includes the session name
   and timestamp. When reading artifacts, agents and humans can trace who
   produced what and when.

2. **No clobbering.** Iteration produces new files rather than overwriting
   previous versions. The second executor run creates a new artifact alongside
   the first. Agents always read the most recent artifact (by timestamp);
   humans can compare versions.

**Naming convention for handoff files:**
```
{ARTIFACT}_{session_name}_{YYYY-MM-DD}_{HH-MM}.md
```

Examples:
- `STRATEGY_gerald_2026-03-13_14-30.md`
- `STRATEGY_CRITICAL_REVIEW_florence_2026-03-13_15-00.md`
- `STRATEGY_ARBITER_hiroshi_2026-03-13_15-30.md`
- `inputs_margaret_2026-03-13_15-45.md`

The orchestrator tells each agent its assigned session name in the input
prompt. The agent uses this name when naming its output files. Downstream
agents discover the current artifact by finding the most recent file matching
the artifact type pattern (e.g., `STRATEGY_*_*.md`), sorted by timestamp.
This eliminates the need to overwrite files on iteration — each session's
work is preserved and the history is self-documenting.

## Directory Layout

```
analysis_name/
  prompt.md
  regression_log.md              # Tracks any phase regressions (if triggered)

  calibrations/                  # Shared sub-analyses (may scale to near-full
    calibration_1/               #   sub-analysis structure if complexity warrants)
      experiment_log.md          #   e.g., btag, jet_corrections, trigger_eff
      retrieval_log.md
      CALIBRATION_1.md
      scripts/
      figures/
    calibration_2/
      experiment_log.md
      retrieval_log.md
      CALIBRATION_2.md
      scripts/
      figures/

  phase1_strategy/
    experiment_log.md            # Lab notebook for this phase
    retrieval_log.md
    UPSTREAM_FEEDBACK.md         # Feedback from downstream phases (if any)
    REGRESSION_TICKET.md         # Regression investigation output (if triggered)
    scripts/                     # Phase-level codebase (can grow to thousands of lines)
    figures/
    exec/
      inputs_gerald_2026-03-13_14-30.md       # Session-named inputs
      session.log
      plan_gerald_2026-03-13_14-30.md
      STRATEGY_gerald_2026-03-13_14-30.md     # Session-named artifact
      # On iteration, new files appear alongside (no overwrites):
      # inputs_margaret_2026-03-13_16-00.md
      # STRATEGY_margaret_2026-03-13_16-00.md
    review/
      critical/
        inputs_florence_2026-03-13_15-00.md
        session.log
        STRATEGY_CRITICAL_REVIEW_florence_2026-03-13_15-00.md
      constructive/
        inputs_tomoko_2026-03-13_15-00.md
        session.log
        STRATEGY_CONSTRUCTIVE_REVIEW_tomoko_2026-03-13_15-00.md
      arbiter/
        inputs_hiroshi_2026-03-13_15-30.md
        session.log
        STRATEGY_ARBITER_hiroshi_2026-03-13_15-30.md

  phase2_exploration/
    experiment_log.md
    retrieval_log.md
    UPSTREAM_FEEDBACK.md
    REGRESSION_TICKET.md
    scripts/
    figures/
    exec/
      ...
    # Self-review only — no review/ directory

  phase3_selection/              # Per-channel if multi-channel
    channel_a/                   # Replace with analysis-specific names
      experiment_log.md
      retrieval_log.md
      sensitivity_log.md         # Tracks optimization attempts
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      scripts/                   # Per-channel codebase
      figures/
      exec/
        ...
        SELECTION_CHANNEL_A.md
      review/
        critical/                # 1-bot review per channel
          ...
    channel_b/
      experiment_log.md
      retrieval_log.md
      sensitivity_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      scripts/
      figures/
      exec/
        ...
        SELECTION_CHANNEL_B.md
      review/
        critical/
          ...
    SELECTION_COMBINED.md        # Consolidation artifact

  phase4_inference/
    4a_expected/
      experiment_log.md
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      scripts/
      figures/
      exec/
        ...
        INFERENCE_EXPECTED.md
        INFERENCE_EXPECTED.md
      review/
        physics/                # 4-bot review (agent gate)
          ...
        critical/
          ...
        constructive/
          ...
        arbiter/
          ...
    4b_partial/
      experiment_log.md
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      scripts/
      figures/
      exec/
        ...
        INFERENCE_PARTIAL.md
        ANALYSIS_NOTE_DRAFT.md
        VERIFICATION_CHECKLIST.md
      review/
        physics/                # 4-bot review before human
          ...
        critical/
          ...
        constructive/
          ...
        arbiter/
          ...
    4c_observed/                 # Created after human approval
      retrieval_log.md
      UPSTREAM_FEEDBACK.md
      REGRESSION_TICKET.md
      scripts/
      figures/
      exec/
        ...
        INFERENCE_OBSERVED.md
      review/
        critical/               # 1-bot review
          ...

  phase5_documentation/
    retrieval_log.md
    UPSTREAM_FEEDBACK.md
    REGRESSION_TICKET.md
    exec/
      ...
      ANALYSIS_NOTE.md
    review/
      physics/                  # 5-bot review
        ...
      critical/
        ...
      constructive/
        ...
      rendering/
        ...
      arbiter/
        ...
```
