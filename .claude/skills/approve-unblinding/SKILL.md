---
name: approve-unblinding
description: Human gate for reviewing and approving full unblinding after Phase 4b
user-invocable: true
---

# /approve-unblinding -- Human Gate for Full Unblinding

This command implements the human gate between Phase 4b (partial unblinding) and Phase 4c (full unblinding). The analysis pauses here until a human explicitly approves.

**Arguments:** `$ARGUMENTS` (ignored)

## Step 1: Verify State

1. Read `STATE.md`. Confirm the current status is `human_gate` and the current phase is `4b`.
   - If the status is NOT `human_gate`, report: "The analysis is not at the human gate. Current status: {status}, phase: {phase}. This command can only be run after Phase 4b review passes." Stop.
   - If Phase 4b has not passed review, report: "Phase 4b review has not yet passed. Run the Phase 4b review first." Stop.

2. Read `analysis_config.yaml`. Confirm `blinding.approved_for_unblinding` is `false`.
   - If already `true`, report: "Unblinding has already been approved. Phase 4c can proceed." Stop.

## Step 2: Gather Review Materials

Read the following files and present a summary to the user:

### Draft Analysis Note
- Read the latest `ANALYSIS_NOTE_DRAFT*.md` from `phase4_inference/4b_partial/exec/`
- Summarize: title, physics process, key methodology choices, 10% observed results, main conclusions

### Unblinding Checklist
- Read the latest `UNBLINDING_CHECKLIST*.md` from `phase4_inference/4b_partial/exec/`
- Present each checklist item with its status (passed/failed/not evaluated)

The checklist should cover:
1. Background model validated (closure tests pass in all VRs)
2. Systematic uncertainties evaluated and fit model stable
3. Expected results physically sensible
4. Signal injection tests confirm fit recovers injected signals
5. 10% partial unblinding shows no unexpected pathologies
6. All agent review cycles resolved (arbiter PASS)
7. Draft analysis note reviewed and considered publication-ready modulo full observed results

### 4-bot Review Result
- Read the latest arbiter file from `phase4_inference/4b_partial/review/arbiter/`
- Summarize the arbiter's decision and any residual Category B/C items

### Key Results Summary
- Read the latest `INFERENCE_PARTIAL*.md` from `phase4_inference/4b_partial/exec/`
- Report: expected vs 10% observed results, goodness-of-fit, any notable nuisance parameter pulls

## Step 3: Present to User

Format the summary clearly:

```
================================================================
         UNBLINDING APPROVAL REQUEST -- {analysis_name}
================================================================

DRAFT ANALYSIS NOTE SUMMARY
----------------------------
{summary of the draft note -- 5-10 lines covering the analysis,
methodology, and 10% results}

UNBLINDING CHECKLIST
--------------------
[x] 1. Background model validated -- closure tests pass in all VRs
[x] 2. Systematic uncertainties evaluated -- fit model stable
[x] 3. Expected results physically sensible
[x] 4. Signal injection tests pass
[x] 5. 10% partial unblinding -- no unexpected pathologies
[x] 6. Agent review cycles resolved -- arbiter PASS
[x] 7. Draft analysis note reviewed -- publication-ready

4-BOT REVIEW RESULT
--------------------
Decision: PASS
Iterations: {N}
Residual items: {list any B/C items}

KEY RESULTS (10% data)
-----------------------
Expected: {expected result}
Observed (10%): {observed result}
Goodness-of-fit: {GoF metric}
Notable NP pulls: {any pulls > 1 sigma}

================================================================
ARTIFACTS FOR DETAILED REVIEW:
  - Draft note: phase4_inference/4b_partial/exec/ANALYSIS_NOTE_DRAFT*.md
  - Partial results: phase4_inference/4b_partial/exec/INFERENCE_PARTIAL*.md
  - Expected results: phase4_inference/4a_expected/exec/INFERENCE_EXPECTED*.md
  - Checklist: phase4_inference/4b_partial/exec/UNBLINDING_CHECKLIST*.md
  - Arbiter review: phase4_inference/4b_partial/review/arbiter/
================================================================

Please review the above and respond with one of:
  APPROVE          -- Proceed to full unblinding (Phase 4c)
  REQUEST_CHANGES  -- Send Phase 4b back for revisions (describe what to change)
  HALT             -- Stop the analysis (provide reason)
```

## Step 4: Wait for User Response

The user will respond with one of three decisions. Handle each:

### APPROVE

1. Update `analysis_config.yaml`: set `blinding.approved_for_unblinding: true`
2. Update `STATE.md`:
   - Phase 4b status: `passed` (with note: "human approved")
   - Current phase: `4c`
   - Status: `executing`
   - Timestamp
3. Report: "Full unblinding approved. Proceeding to Phase 4c."
4. Begin Phase 4c execution:
   - Spawn `systematics-fitter` to run the full fit on complete dataset
   - Spawn `cross-checker` to validate consistency
   - Then run 1-bot review (with plot-validator)
   - Continue the pipeline through Phase 5

### REQUEST_CHANGES

1. Update `STATE.md`:
   - Status: `executing` (Phase 4b re-execution)
   - Add note: "Human requested changes: {description}"
   - Timestamp
2. Re-spawn the Phase 4b executor via SendMessage with:
   - All original inputs
   - The human's change request as additional input
   - The previous draft note and partial results
   - Instruction: "The human reviewer has requested changes before approving unblinding. Address the following: {user's description}. Produce updated artifacts."
3. After executor completes, re-run 4-bot review (with plot-validator) for Phase 4b
4. On PASS, return to the human gate (present the updated summary)

### HALT

1. Update `STATE.md`:
   - Status: `halted`
   - Add to Blockers: "Human halted analysis at unblinding gate. Reason: {user's reason}"
   - Timestamp
2. Update `analysis_config.yaml`: `blinding.approved_for_unblinding: false`
3. Report: "Analysis halted at human request. Reason: {reason}. To resume, the user must address the concerns and re-run `/approve-unblinding`."
