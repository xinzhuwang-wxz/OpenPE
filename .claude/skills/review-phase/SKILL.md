---
name: review-phase
description: Run the review cycle for a completed phase artifact with plot validation
user-invocable: true
---

# /review-phase -- Run Review Cycle for a Phase

Run the review cycle for a completed phase artifact. This enhanced protocol uses 4-bot review (replacing the previous 3-bot) for most phases, 5-bot for final documentation, and 1-bot for selection and observed results. All review tiers include plot-validator for phases that produce figures.

**Arguments:** `$ARGUMENTS`

The argument is optionally a phase identifier: `1`, `2`, `3`, `4a`, `4b`, `4c`, or `5`. If omitted, read STATE.md to determine the current phase.

## Step 1: Determine Phase and Review Tier

1. Read `STATE.md` to confirm the analysis state.
2. If a phase argument was given, use it. Otherwise use the current phase from STATE.md.
3. Read `analysis_config.yaml` for cost controls (`max_review_iterations`, `review_warn_threshold`).
4. Determine the review tier for this phase:

| Phase | Review tier | Plot-validator |
|-------|------------|----------------|
| 0 | 2-bot (logic, then arbiter) | Yes (if figures produced) |
| 1 | 2-bot (logic, then arbiter) | Yes (if figures produced) |
| 2 | self (no action needed -- return immediately) | No |
| 3 | 1-bot (critical only) per channel | Yes |
| 4a | 4-bot (physics + critical + constructive, then arbiter) | Yes |
| 4b | 4-bot | Yes |
| 4c | 1-bot | Yes |
| 5 | 3-bot (domain + rendering, then arbiter) | Yes |

If phase is 2, report "Phase 2 uses self-review. No external review required." and return.

## Step 2: Locate the Artifact Under Review

Find the latest artifact for this phase:

| Phase | Artifact pattern | Location |
|-------|-----------------|----------|
| 1 | `STRATEGY*.md` | `phase1_strategy/exec/` |
| 3 | `SELECTION*.md` | `phase3_selection/exec/` or `phase3_selection/channel_{name}/exec/` |
| 4a | `INFERENCE_EXPECTED*.md` | `phase4_inference/4a_expected/exec/` |
| 4b | `ANALYSIS_NOTE_DRAFT*.md` | `phase4_inference/4b_partial/exec/` |
| 4c | `INFERENCE_OBSERVED*.md` | `phase4_inference/4c_observed/exec/` |
| 5 | `ANALYSIS_NOTE*.md` | `phase5_documentation/exec/` |

Also locate upstream artifacts that reviewers need for context (see the dependency table in CLAUDE.md).

Read the experiment log for this phase if it exists.

Identify all figures in the `figures/` directory for this phase -- these will be passed to the plot-validator.

## Step 3: Run the Review

Update STATE.md: `status: reviewing`, timestamp.

Initialize iteration counter: `iteration = 0`.

### 2-bot Review (Phases 0, 1)

Loop until PASS, ESCALATE, or max iterations:

1. Increment iteration counter. Check cost controls (same thresholds as 4-bot).

2. **Spawn logic-reviewer in parallel with plot-validator** (if figures exist):

   Logic reviewer instructions:
   - Read: methodology spec (review focus for this phase), the artifact under review, upstream artifacts, experiment log
   - Evaluate: reasoning validity, DAG consistency, EP arithmetic, logical completeness
   - Classify every issue as (A) must resolve, (B) should address, (C) suggestion
   - Include structured fix instructions (exact or requires_reasoning) for every A/B item
   - Write output to: `review/logic/` with session-named filename

   Plot-validator: same instructions as 4-bot below.

3. **Spawn arbiter** via SendMessage:
   - Read: the artifact, logic review, plot-validation report (if exists)
   - Write output to: `review/arbiter/`
   - Decision: **PASS**, **ITERATE**, or **ESCALATE**

4-5. Handle decision same as 4-bot below.

### 4-bot Review (Phases 4a, 4b)

Loop until PASS, ESCALATE, or max iterations:

1. Increment iteration counter.
2. Check cost controls:
   - If `iteration > review_warn_threshold`: log WARNING -- "Review iteration {iteration} for phase {phase}. Consider whether issues are fundamental enough to escalate."
   - If `iteration > 5`: log STRONG WARNING.
   - If `iteration >= max_review_iterations`: force ESCALATE to human. Update STATE.md: `status: blocked`. Report and stop.

3. **Spawn physics-reviewer, critical-reviewer, and constructive-reviewer in parallel** via SendMessage. If this phase has figures, also spawn **plot-validator** in parallel with the three reviewers:

   Physics reviewer instructions:
   - Read: `src/methodology/03-phases.md` (review focus for this phase), the artifact under review, upstream artifacts, experiment log
   - Evaluate physics correctness: signal model assumptions, background treatment, kinematic reasoning, systematic uncertainty coverage, statistical methodology
   - Classify every issue as (A) must resolve, (B) should address, (C) suggestion
   - Write output to: `review/physics/{REVIEW}.md` with session-named filename

   Critical reviewer instructions:
   - Read: methodology spec (review focus for this phase), the artifact under review, upstream artifacts, experiment log
   - Find flaws: incomplete estimates, missing systematics, unjustified assumptions, biases, physics errors, code bugs
   - Classify every issue as (A) must resolve, (B) should address, (C) suggestion
   - Write output to: `review/critical/` with session-named filename

   Constructive reviewer instructions:
   - Read: same inputs as critical reviewer
   - Strengthen the analysis: clarity, additional validation, presentation improvements
   - Focus on B and C issues but escalate to A if genuine errors found
   - Write output to: `review/constructive/` with session-named filename

   Plot-validator instructions (if figures exist):
   - **First iteration:** Read all figures in this phase's `figures/` directory
   - **Subsequent iterations:** Read only figures affected by the latest fixes (listed in arbiter's fix instructions) plus any newly created figures. Unmodified figures retain prior validation status.
   - Read: `conventions/` plotting standards (axis labels, font sizes, color schemes, legend placement, ratio panels, domain style requirements)
   - Validate each figure against the conventions
   - Check: axis labels and units, legend completeness, ratio panel presence where required, color accessibility, resolution and format, statistical uncertainty display, verification compliance (no signal region data shown before approval)
   - Classify issues as (A) must fix, (B) should fix, (C) cosmetic suggestion
   - Write output to: `review/plot-validation/{REVIEW}.md`

4. **After all reviewers complete, spawn arbiter** via SendMessage:
   - Read: the artifact, all review files (latest from `review/physics/`, `review/critical/`, `review/constructive/`, and `review/plot-validation/` if it exists)
   - For each issue: if multiple reviewers agree, accept; if they disagree, assess independently; if all missed something, raise it
   - Incorporate plot-validator findings: Category A plot issues are treated as Category A overall
   - Write output to: `review/arbiter/` with session-named filename
   - End with a clear decision: **PASS**, **ITERATE** (list Category A items including plot issues), or **ESCALATE** (document why)

5. **Read the arbiter decision** from the latest file in `review/arbiter/`.

6. **Handle the decision:**

   - **PASS**: Check for regression triggers in the review output. If none found, update STATE.md (`status: passed`), record in Phase History table (including iteration count), and return the result.

   - **ITERATE**: Apply fixes using the arbiter's structured instructions:
     1. **Exact fixes** (`type: exact`): Apply directly via Edit tool — no subagent needed.
     2. **Reasoning fixes** (`type: requires_reasoning`): Spawn fix agent with the section path, instruction, and previous artifact. Fix agent addresses only these items.
     3. **Re-verify** based on remaining issue severity:
        - **A-present**: Continue the arbiter via SendMessage with the updated artifact and fix diff. Arbiter re-checks only the fixed items. On 3rd+ iteration, spawn a fresh arbiter instead.
        - **B-only remaining**: Executor self-verifies against a checklist of the B items. If all addressed → PASS. If any fail → full re-review.
     4. Loop until PASS or iteration limit.

   - **ESCALATE**: Update STATE.md (`status: blocked`, record escalation reason). Report to user: "Phase {phase} review escalated. Reason: {reason}. Human intervention required." Stop.

### 3-bot Review (Phase 5 Documentation)

1. Increment iteration counter. Check cost controls (same thresholds).

2. **Spawn domain-reviewer and rendering-reviewer in parallel**, plus **plot-validator** if figures exist:

   Domain reviewer instructions:
   - Read: the artifact under review, upstream artifacts (ANALYSIS_NOTE, VERIFICATION, PROJECTION), experiment log
   - Check factual accuracy: numbers match upstream sources, claims are supported, no fabricated references
   - Classify issues as (A) must resolve, (B) should address, (C) suggestion
   - Include structured fix instructions for every A/B item
   - Write output to: `review/domain/` with session-named filename

   Rendering reviewer instructions:
   - Read: the final analysis note artifact, all figures, `conventions/` document formatting standards
   - Evaluate document quality: structure, readability, figure placement and referencing, table formatting, equation typesetting, abstract clarity, conclusion strength
   - Check cross-references between text and figures/tables
   - Classify issues as (A) must resolve, (B) should address, (C) suggestion
   - Write output to: `review/rendering/{REVIEW}.md`

   Plot-validator: same instructions as 4-bot above.

3. **Spawn arbiter** via SendMessage:
   - Read: the artifact, domain review, rendering review, plot-validation report
   - Synthesize all reviewer inputs; Category A issues from any reviewer are Category A overall
   - Write output to: `review/arbiter/`
   - Decision: **PASS**, **ITERATE**, or **ESCALATE**

4-5. Handle decision same as 4-bot.

### 1-bot Review (Phases 3, 4c)

For Phase 3 with multiple channels, run this loop for each channel directory independently.

Loop until no Category A issues, ESCALATE, or max iterations:

1. Increment iteration counter.
2. Check cost controls (same thresholds as 4-bot).

3. **Spawn critical-reviewer** via SendMessage. If this phase has figures, also spawn **plot-validator in parallel**:

   Critical reviewer:
   - Read: methodology spec (review focus for this phase), artifact, upstream artifacts, experiment log
   - Classify issues as A/B/C
   - Write output to: `review/critical/` with session-named filename

   Plot-validator (if figures exist):
   - Same instructions as in the 4-bot section
   - Write output to: `review/plot-validation/{REVIEW}.md`

4. **Read the review** from the latest file in `review/critical/`. Also read plot-validator output if produced.

5. **Check for Category A issues** (from critical reviewer AND plot-validator):

   - **No Category A from either**: Check for regression triggers. Update STATE.md, record in Phase History, return PASS.

   - **Category A found**: Re-spawn the phase executor with:
     - All original inputs
     - The critical review feedback
     - Plot-validator feedback (if any Category A plot issues)
     - The previous artifact
     - The experiment log
     - Instruction: "Address the Category A issues. Produce an updated artifact."
     - After executor completes, loop back to step 1.

   - **Max iterations reached**: Force ESCALATE. Update STATE.md: `status: blocked`. Report and stop.

## Step 4: Regression Detection

After any PASS decision, scan all review outputs for regression triggers. A regression trigger is any statement indicating that work done in a prior phase is now known to be incorrect, incomplete, or based on wrong assumptions. Examples:
- "The background model in Phase 3 used an incorrect normalization"
- "The systematic uncertainty source X was overlooked in the strategy"
- "The efficiency correction applied in Phase 2 is outdated"

If a regression trigger is found:
1. Update STATE.md: status=regression
2. Spawn an `investigator` agent with the trigger description
3. Investigator produces `REGRESSION_TICKET.md`
4. Re-run the origin phase, re-review, and re-run affected downstream phases
5. Log in `regression_log.md`

## Step 5: Report Results

After the review completes, report:

```
Phase {phase} review: {PASS | ESCALATE}
  Review tier: {4-bot | 5-bot | 1-bot}
  Reviewers: {list of reviewer types used}
  Plot validation: {included | skipped (no figures)}
  Iterations: {count}
  Artifact: {path to final artifact}
  Decision: {arbiter decision or 1-bot outcome}
  Category A issues resolved: {count if any}
  Plot issues resolved: {count if any}
  Regression triggers: {none | description}
```

If this is Phase 4b and the decision is PASS, additionally report:
```
Human gate reached. Run /approve-verification to review the draft analysis note and approve or reject full verification.
```
