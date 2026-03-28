---
name: run-analysis
description: Initialize and run the full automated HEP analysis pipeline from physics prompt to final documentation
user-invocable: true
---

# /run-analysis -- Main Analysis Pipeline Entry Point

You are the pipeline orchestrator. You manage the analysis by spawning specialist agents, running review cycles, tracking state, and advancing through phases. You do NOT perform analysis work yourself.

**Arguments:** `$ARGUMENTS`

The argument is either:
- A physics prompt as inline text, OR
- A path to a `.md` file containing the physics prompt, OR
- A path to a `.md` prompt followed by a path to a `.yaml` config file

## Step 1: Parse Inputs

1. If `$ARGUMENTS` contains a path ending in `.md`, read that file as the physics prompt. Otherwise, treat the full argument text as the prompt.
2. If `$ARGUMENTS` contains a path ending in `.yaml`, read that as the analysis config. Otherwise, you will create a default config in Step 4.
3. Derive a short snake_case `analysis_name` from the physics prompt (e.g., `zh_nunubb_aleph`, `ttbar_dilepton_cms`).

## Step 2: Read Methodology

Read the following files to understand the phase requirements and orchestration protocol:

- `src/methodology/03-phases.md` -- what each phase must produce
- `src/methodology/04-blinding.md` -- blinding protocol and human gate
- `src/methodology/06-review.md` -- review tiers and iteration rules
- `orchestration/agents.md` -- agent session definitions
- `orchestration/automation.md` -- automation pseudocode
- `orchestration/sessions.md` -- session isolation and naming
- `CLAUDE.md` -- your operating model

## Step 3: Scaffold the Analysis Directory

Run the scaffolder to create the analysis directory structure:

```bash
pixi run scaffold analyses/{analysis_name} --type {measurement|search}
```

Choose `measurement` or `search` based on the physics prompt (searches involve new particle or signature discovery; measurements quantify known processes).

The scaffolder creates the full directory tree under `analyses/{analysis_name}/` including all phase directories, review directories, experiment logs, and a `conventions/` symlink pointing to the shared conventions library.

Copy the physics prompt into `analyses/{analysis_name}/prompt.md`.

## Step 4: Write analysis_config.yaml

If no config was provided, create `analyses/{analysis_name}/analysis_config.yaml` with:

```yaml
analysis_name: {analysis_name}
physics_prompt_path: prompt.md
model_tier: auto
channels: []  # populated during Phase 1
calibrations: []  # populated during Phase 1
data_dir: ""  # USER MUST SET THIS -- path to input ROOT files or NTuples
cost_controls:
  max_review_iterations: 10
  review_warn_threshold: 3
blinding:
  active: true
  approved_for_unblinding: false
pixi:
  environment: default
  workflow_prefix: "pixi run"
```

If a config was provided, copy it to `analyses/{analysis_name}/analysis_config.yaml`, ensuring at minimum the `blinding`, `cost_controls`, and `pixi` sections exist.

**IMPORTANT:** After writing the config, remind the user:
> "analysis_config.yaml has been created. Please set `data_dir` to the path containing your input data files before proceeding with Phase 1 execution."

## Step 5: Initialize STATE.md

Write `analyses/{analysis_name}/STATE.md`:

```markdown
# Analysis State

- **Analysis**: {analysis_name}
- **Current phase**: 1
- **Status**: initialized
- **Last updated**: {current timestamp}

## Phase History

| Phase | Status | Artifact | Review | Iterations | Notes |
|-------|--------|----------|--------|------------|-------|

## Blockers
- (none)

## Regression Log
- (none)
```

Initialize `analyses/{analysis_name}/regression_log.md` as empty.

## Step 6: Execute the Pipeline

Now execute the full pipeline. At each phase transition, update STATE.md with the current phase, status, and timestamp. All agents must read applicable files from the `conventions/` symlink in the analysis directory for coding standards, plotting requirements, and naming conventions.

### Phase 1: Strategy

1. Update STATE.md: phase=1, status=executing
2. Spawn `lead-analyst` agent via `SendMessage`:
   - Task: Execute Phase 1 (Strategy)
   - Inputs: `prompt.md`, `src/methodology/03-phases.md` (Phase 1 section), `analysis_config.yaml`
   - **Must read:** applicable `conventions/` files for naming and coding standards
   - Working directory: `analyses/{analysis_name}/phase1_strategy/`
   - Output: `exec/STRATEGY.md`, append to `experiment_log.md`, code in `scripts/`, figures in `figures/`
   - All scripts must use `pixi run` for execution
3. Update STATE.md: status=reviewing
4. Run 4-bot review by invoking `/review-phase` with phase "1"
5. On PASS: update STATE.md (phase=1, status=passed), record artifact and review info in Phase History table
6. Advance to Phase 2

### Phase 2: Exploration

1. Update STATE.md: phase=2, status=executing
2. Spawn three agents **in parallel** via `SendMessage`:
   - `data-explorer`: inventory samples, check data quality
   - `detector-specialist`: validate detector model, object definitions
   - `theory-scout`: survey theory predictions, cross-sections, backgrounds
   - All read: `prompt.md`, `phase1_strategy/exec/STRATEGY.md` (latest), `src/methodology/03-phases.md` (Phase 2 section)
   - **Must read:** applicable `conventions/` files
   - All write to: `analyses/{analysis_name}/phase2_exploration/`
   - All scripts must use `pixi run` for execution
3. After all three complete, spawn `lead-analyst` to consolidate their outputs into `exec/EXPLORATION.md`
4. Phase 2 is self-review -- no external review needed
5. Update STATE.md: phase=2, status=passed
6. Advance to Phase 3

### Phase 3: Selection and Background Modeling

1. Update STATE.md: phase=3, status=executing
2. Read `analysis_config.yaml` to check for defined channels
   - If channels are populated (multi-channel): create per-channel subdirectories under `phase3_selection/channel_{name}/` with `experiment_log.md`, `sensitivity_log.md`, `scripts/`, `figures/`, `exec/`, `review/critical/`
   - If no channels defined: work in `phase3_selection/` directly
3. For each channel (or the single analysis), spawn agents **in parallel**:
   - `signal-lead`: implement event selection, define regions
   - `background-estimator`: estimate backgrounds, perform closure tests
   - Inputs: `prompt.md`, `STRATEGY.md`, `EXPLORATION.md`, `src/methodology/03-phases.md` (Phase 3 section)
   - **Must read:** applicable `conventions/` files
   - Output: `exec/SELECTION.md` (or `exec/SELECTION_{CHANNEL}.md`)
   - All scripts must use `pixi run` for execution
4. Update STATE.md: status=reviewing
5. Run 1-bot review per channel by invoking `/review-phase` with phase "3" (includes plot-validator)
6. On PASS (all channels): update STATE.md (phase=3, status=passed)
7. Advance to Phase 4a

### Phase 4a: Expected Results

1. Update STATE.md: phase=4a, status=executing
2. Spawn `systematic-source-evaluator` agents **in parallel** (one per systematic source identified in the strategy)
   - Each evaluates one systematic uncertainty source
   - Inputs: `STRATEGY.md`, `SELECTION.md`, `src/methodology/03-phases.md` (Phase 4a section)
   - **Must read:** applicable `conventions/` files
   - All scripts must use `pixi run` for execution
3. After all complete, spawn `systematics-fitter`:
   - Constructs the statistical model, runs Asimov fits, signal injection tests
   - Output: `exec/INFERENCE_EXPECTED.md`
4. Update STATE.md: status=reviewing
5. Run 4-bot review by invoking `/review-phase` with phase "4a" (includes plot-validator)
6. On PASS: update STATE.md (phase=4a, status=passed)
7. Advance to Phase 4b

### Phase 4b: Partial Unblinding

1. Update STATE.md: phase=4b, status=executing
2. Spawn `systematics-fitter`:
   - Runs fit on 10% SR data subsample
   - Output: `exec/INFERENCE_PARTIAL.md`
   - Must use `pixi run` for execution
3. Spawn `note-writer`:
   - Produces draft analysis note: `exec/ANALYSIS_NOTE_DRAFT.md`
   - Produces unblinding checklist: `exec/UNBLINDING_CHECKLIST.md`
   - **Must read:** applicable `conventions/` files for document formatting
4. Update STATE.md: status=reviewing
5. Run 4-bot review by invoking `/review-phase` with phase "4b" (includes plot-validator)
6. On PASS: update STATE.md (phase=4b, status=human_gate)
7. **PAUSE the pipeline.** Report to the user:
   - "Phase 4b review passed. The draft analysis note, unblinding checklist, and review results are ready for human review."
   - "Run `/approve-unblinding` to review and approve or reject full unblinding."
   - Do NOT proceed to Phase 4c automatically.

### After Human Approval (Phase 4c)

When the user runs `/approve-unblinding` and approves:

1. Confirm `analysis_config.yaml` has `approved_for_unblinding: true`
2. Update STATE.md: phase=4c, status=executing
3. Spawn `systematics-fitter`:
   - Runs full fit on complete dataset
   - Output: `exec/INFERENCE_OBSERVED.md`
   - Must use `pixi run` for execution
4. Spawn `cross-checker`:
   - Validates results, checks consistency with partial and expected
5. Update STATE.md: status=reviewing
6. Run 1-bot review by invoking `/review-phase` with phase "4c" (includes plot-validator)
7. On PASS: update STATE.md (phase=4c, status=passed)
8. Advance to Phase 5

### Phase 5: Documentation

1. Update STATE.md: phase=5, status=executing
2. Spawn `note-writer`:
   - Updates draft note with full observed results
   - Inputs: all phase artifacts, `ANALYSIS_NOTE_DRAFT.md`, `INFERENCE_OBSERVED.md`
   - **Must read:** applicable `conventions/` files for document and figure formatting
   - Output: `exec/ANALYSIS_NOTE.md`
3. Update STATE.md: status=reviewing
4. Run 5-bot review by invoking `/review-phase` with phase "5" (physics + critical + constructive + rendering + arbiter, with plot-validator)
5. On PASS: update STATE.md (phase=5, status=passed, overall=COMPLETE)
6. Report: "Analysis complete. Final analysis note: `analyses/{analysis_name}/phase5_documentation/exec/ANALYSIS_NOTE.md`"

## State Update Protocol

Every time you transition between states, update STATE.md with:
- The current phase number
- The current status (executing, reviewing, passed, blocked, human_gate)
- A timestamp
- The Phase History table row for completed phases

## Regression Handling

After any review PASS, check the review output for regression triggers. If found:
1. Update STATE.md: status=regression
2. Spawn an `investigator` agent to produce `REGRESSION_TICKET.md`
3. Re-run the origin phase executor with the ticket
4. Re-review at the original tier
5. Re-run all affected downstream phases
6. Log in `regression_log.md`

## Cost Controls

- Track review iteration counts per phase
- Warn at `review_warn_threshold` (default 3) iterations
- Hard cap at `max_review_iterations` (default 10) -- escalate to human
- If a phase executor appears stuck, produce best-effort artifact and proceed to review
