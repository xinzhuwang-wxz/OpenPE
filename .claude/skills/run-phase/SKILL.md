---
name: run-phase
description: Execute a single phase of the analysis pipeline by phase identifier
user-invocable: true
---

# /run-phase -- Execute a Single Analysis Phase

Run a single phase of the analysis pipeline.

**Arguments:** `$ARGUMENTS`

The argument is a phase identifier: `1`, `2`, `3`, `4a`, `4b`, `4c`, or `5`.

## Step 1: Read Current State

1. Find the analysis directory (look for `STATE.md` in the current directory or immediate subdirectories, including under `analyses/`).
2. Read `STATE.md` to confirm the analysis is at the correct phase. If the requested phase does not match the current phase in STATE.md, report the mismatch and stop unless the user explicitly confirms they want to run this phase out of order.
3. Read `analysis_config.yaml` for configuration (model tier, channels, cost controls, pixi settings).

## Step 2: Read Phase Methodology

Read `src/methodology/03-phases.md` and locate the section for the requested phase. Also read:
- `orchestration/agents.md` -- agent definitions
- `orchestration/sessions.md` -- session naming and isolation
- `CLAUDE.md` -- orchestration model

Read the `conventions/` symlink in the analysis directory to identify applicable coding, plotting, and naming conventions. All spawned agents must follow these conventions.

## Step 3: Identify Upstream Artifacts

Each phase depends on artifacts from prior phases. Locate the latest version of each required artifact by finding the most recent file matching the artifact pattern (sorted by timestamp in the filename).

| Phase | Required upstream artifacts |
|-------|---------------------------|
| 1 | `prompt.md` only |
| 2 | `prompt.md`, `phase1_strategy/exec/STRATEGY*.md` (latest) |
| 3 | `prompt.md`, `STRATEGY*.md`, `phase2_exploration/exec/EXPLORATION*.md` |
| 4a | `prompt.md`, `STRATEGY*.md`, `SELECTION*.md` (per channel or combined) |
| 4b | `prompt.md`, `STRATEGY*.md`, `SELECTION*.md`, `phase4_inference/4a_expected/exec/INFERENCE_EXPECTED*.md` |
| 4c | All of 4b's inputs plus `phase4_inference/4b_partial/exec/INFERENCE_PARTIAL*.md`, and confirmed `approved_for_verification: true` in config |
| 5 | All prior phase artifacts |

## Step 4: Execute the Phase

Update STATE.md: `status: executing`, `current phase: {phase}`, timestamp.

All agents use `pixi run` for script execution and must read applicable `conventions/` files.

### Phase 1: Strategy

Spawn `lead-analyst` via SendMessage:
- Inputs: `prompt.md`, methodology (Phase 1 section), `analysis_config.yaml`
- **Must read:** applicable `conventions/` files for naming and coding standards
- Working directory: `phase1_strategy/`
- Expected output: `exec/STRATEGY.md`, updates to `experiment_log.md`
- The agent should query the data corpus, identify signal/backgrounds, propose selection, define verification strategy, outline systematics
- All scripts use `pixi run` for execution

### Phase 2: Exploration

Spawn three agents **in parallel** via SendMessage:
- `data-explorer`: sample inventory, data quality checks, baseline yields
- `domain-specialist`: variable definitions, data validation
- `domain-scout`: expected relationships, domain predictions, prior results

All read: `prompt.md`, latest `STRATEGY.md`, methodology (Phase 2 section)
All read: applicable `conventions/` files
All write to: `phase2_exploration/`
All use `pixi run` for script execution

After all complete, spawn `lead-analyst` to consolidate into `exec/EXPLORATION.md`.

### Phase 3: Selection and Background Modeling

Check `analysis_config.yaml` for channels. For each channel (or the single analysis):
- Spawn `signal-lead` and `background-estimator` in parallel
- Inputs: `prompt.md`, `STRATEGY.md`, `EXPLORATION.md`, methodology (Phase 3 section)
- **Must read:** applicable `conventions/` files
- Output: `exec/SELECTION.md` (or per-channel `SELECTION_{CHANNEL}.md`)
- All scripts use `pixi run` for execution

If multi-channel, after all channels complete, spawn `lead-analyst` to produce `SELECTION_COMBINED.md`.

### Phase 4a: Expected Results

1. Identify systematic sources from the strategy and selection artifacts
2. Spawn `systematic-source-evaluator` agents **in parallel** (one per source)
   - **Must read:** applicable `conventions/` files
   - All scripts use `pixi run` for execution
3. After all complete, spawn `systematics-fitter`:
   - Builds statistical model, runs Asimov fits, signal injection tests
   - Output: `exec/INFERENCE_EXPECTED.md`

### Phase 5: Partial Verification

1. Spawn `systematics-fitter`:
   - Runs fit on 10% SR data subsample (fixed random seed)
   - Output: `exec/INFERENCE_PARTIAL.md`
   - Uses `pixi run` for execution
2. Spawn `note-writer`:
   - Produces `exec/ANALYSIS_NOTE_DRAFT.md` and `exec/VERIFICATION_CHECKLIST.md`
   - **Must read:** applicable `conventions/` files for document formatting

### Phase 6: Full Verification

1. **Verify** `analysis_config.yaml` has `approved_for_verification: true`. If not, STOP and instruct the user to run `/approve-verification` first.
2. Spawn `systematics-fitter`:
   - Runs full fit on complete dataset
   - Output: `exec/INFERENCE_OBSERVED.md`
   - Uses `pixi run` for execution
3. Spawn `cross-checker`:
   - Validates consistency with partial and expected results

### Phase 5: Documentation

Spawn `note-writer`:
- Reads all phase artifacts including `ANALYSIS_NOTE_DRAFT.md` and `INFERENCE_OBSERVED.md`
- **Must read:** applicable `conventions/` files for document and figure formatting
- Output: `exec/ANALYSIS_NOTE.md`

## Step 5: Run Review

After execution completes, update STATE.md: `status: reviewing`.

Invoke the review by running `/review-phase` with the current phase number, OR run the review inline:

| Phase | Review tier |
|-------|------------|
| 1 | 4-bot (physics + critical + constructive in parallel, then arbiter) with plot-validator |
| 2 | Self-review (no separate review -- already done by executor) |
| 3 | 1-bot per channel (critical reviewer) with plot-validator |
| 4a | 4-bot with plot-validator |
| 4b | 4-bot, then PAUSE for human gate, with plot-validator |
| 4c | 1-bot with plot-validator |
| 5 | 5-bot (physics + critical + constructive + rendering in parallel, then arbiter) with plot-validator |

## Step 6: Update State and Report

On review PASS:
1. Update STATE.md: `status: passed` for this phase, add row to Phase History table
2. For Phase 4b specifically: set `status: human_gate` and PAUSE
3. Report: which phase completed, artifact location, review outcome, iteration count

On review ITERATE:
- The review command handles re-spawning the executor. Wait for it to complete.

On review ESCALATE:
- Update STATE.md: `status: blocked`
- Report the escalation reason to the user

Check for regression triggers in review output. If found, handle per the regression protocol in CLAUDE.md.
