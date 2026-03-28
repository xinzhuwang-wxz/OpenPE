---
name: check-status
description: Display current analysis pipeline status
user-invocable: true
---

# /check-status -- Analysis Status Report

Display the current status of the analysis pipeline.

**Arguments:** `$ARGUMENTS` (ignored)

## Instructions

1. Find the analysis directory by locating `STATE.md` in the current directory or immediate subdirectories (including under `analyses/`).

2. Read `STATE.md` in full.

3. Read `analysis_config.yaml` to get the analysis name, channels, and blinding status.

4. Read `regression_log.md` if it exists and is non-empty.

5. Present a status report in the following format:

```
=== Analysis Status: {analysis_name} ===

Current phase:  {phase number and name}
Status:         {executing | reviewing | passed | blocked | human_gate | complete}
Last updated:   {timestamp from STATE.md}
Blinding:       {active | approved_for_unblinding}

--- Phase History ---

| Phase | Status | Artifact | Review Result | Iterations |
|-------|--------|----------|---------------|------------|
(reproduce the Phase History table from STATE.md)

--- Completed Artifacts ---

(For each passed phase, list the path to the final artifact file.
 Check the exec/ directory for each phase and list the latest artifact by timestamp.)

Phase 1: phase1_strategy/exec/STRATEGY*.md
Phase 2: phase2_exploration/exec/EXPLORATION*.md
Phase 3: phase3_selection/exec/SELECTION*.md
...etc, only for phases that have status=passed

--- Blockers ---

(reproduce the Blockers section from STATE.md, or "None" if empty)

--- Review Iteration Counts ---

(For each phase that has been reviewed, report the number of review iterations.
 Count the number of files in each review/ subdirectory to estimate this.)

Phase 1: {N} iterations (4-bot)
Phase 3: {N} iterations (1-bot)
...etc

--- Regressions ---

(If regression_log.md is non-empty, reproduce its contents.
 Otherwise: "No regressions recorded.")
```

6. If the status is `human_gate`, add a prominent note:

```
>>> HUMAN ACTION REQUIRED <<<
Phase 4b review has passed. The draft analysis note is ready for human review.
Run /approve-unblinding to review and approve or reject full unblinding.
```

7. If the status is `blocked`, add:

```
>>> BLOCKED <<<
Reason: {blocker description from STATE.md}
Human intervention is required to proceed.
```

8. If the status is `complete`, add:

```
>>> ANALYSIS COMPLETE <<<
Final analysis note: phase5_documentation/exec/ANALYSIS_NOTE*.md
```
