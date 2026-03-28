## Automation

> See `agents.md` for the literal prompt templates used in `run_agent` calls.
> See `sessions.md` for the directory layout this script populates.
> See `../methodology/04-orchestration.md` for the architectural rationale.

The following pseudocode illustrates the orchestration logic. It is not a
runnable script — helper functions like `find_latest_artifact`, `extract_decision`,
and `present_for_human_review` are orchestrator responsibilities whose
implementation depends on the agent system. The logic and control flow are
what matter.

```bash
# --- Configuration ---

# Hard cap on review iterations. Correctness is the real termination condition
# (arbiter PASS or reviewer finding no Category A issues), but this prevents
# infinite loops if something goes pathologically wrong.
max_review_iterations=${MAX_REVIEW_ITER:-10}

# --- Session naming ---

# Pool of human first names. The orchestrator picks randomly without
# replacement within an analysis run. See "Agent Session Identity" above.
pick_session_name() {
  # Returns an unused name from the pool. Implementation detail —
  # any unique-per-run naming scheme works.
  echo "$(shuf -n1 names_pool.txt)"
}

# --- Regression detection and upstream feedback ---

run_regression_check() {
  # Checks review output for regression triggers. If found, dispatches
  # investigation and fixes. Returns non-zero if regression was found,
  # signaling that the caller should not proceed to the next phase.
  dir=$1
  review_artifact=$(find_latest_review_artifact "$dir")

  if grep -q "regression trigger" "$review_artifact"; then
    origin_phase=$(extract_regression_origin "$review_artifact")
    echo "REGRESSION detected in $dir — origin: $origin_phase"
    echo "$(date): $dir -> $origin_phase" >> regression_log.md

    # Investigator produces a scoped regression ticket
    run_agent --name "$(pick_session_name)" \
      --output "$origin_phase/REGRESSION_TICKET.md" \
      "Investigate regression trigger from $dir."

    # Fix the origin phase
    run_agent --name "$(pick_session_name)" \
      --output "$origin_phase/exec" \
      "Fix regression described in $origin_phase/REGRESSION_TICKET.md"

    # Re-review at the original tier for that phase
    tier=$(get_review_tier "$origin_phase")
    if [ "$tier" = "4bot" ]; then
      run_4bot_review "$origin_phase"
    else
      run_1bot_review "$origin_phase"
    fi

    # Re-run all downstream phases from the regressed phase
    rerun_downstream_from "$origin_phase"
    return 1  # regression found — caller should not proceed
  fi
  return 0
}

check_upstream_feedback() {
  dir=$1
  feedback_file="$dir/UPSTREAM_FEEDBACK.md"
  if [ -f "$feedback_file" ]; then
    echo "Upstream feedback found in $dir — routing to next review"
    # The feedback file is in the directory; reviewers will discover it
    # when reading the phase contents for the next review gate.
  fi
}

# --- Review tier functions ---

# Returns 0 on PASS, 1 on regression, 2 on escalation/max-iterations.
# Callers should check the return code before proceeding to the next phase.
run_4bot_review() {
  dir=$1
  i=0
  while [ $i -lt $max_review_iterations ]; do
    i=$((i + 1))
    if [ $i -gt 3 ]; then
      echo "WARNING: review iteration $i for $dir"
    fi
    if [ $i -gt 5 ]; then
      echo "STRONG WARNING: review iteration $i for $dir"
    fi

    # Physics, critical, and constructive reviewers run in parallel (independent)
    run_agent --name "$(pick_session_name)" \
      --output "$dir/review/physics" "physics review" &
    run_agent --name "$(pick_session_name)" \
      --output "$dir/review/critical" "critical review" &
    run_agent --name "$(pick_session_name)" \
      --output "$dir/review/constructive" "constructive review" &
    wait

    # Arbiter reads all reviews and the artifact
    run_agent --name "$(pick_session_name)" \
      --output "$dir/review/arbiter" "arbitrate"
    decision=$(extract_decision "$dir/review/arbiter")

    case $decision in
      PASS)
        if ! run_regression_check "$dir"; then
          return 1  # regression found — do not proceed
        fi
        check_upstream_feedback "$dir"
        return 0
        ;;
      ITERATE)
        # Write new session-named inputs file for the next executor run.
        # Includes: arbiter assessment, Category A issues, original upstream
        # artifacts. No file is overwritten — session naming ensures each
        # iteration's inputs and outputs coexist on disk.
        exec_name=$(pick_session_name)
        write_iteration_inputs "$dir" "$i" "$exec_name"
        run_agent --name "$exec_name" \
          --output "$dir/exec" "iterate v$((i+1))"
        ;;
      ESCALATE)
        present_for_human_review "$dir"
        wait_for_human_input
        # Human may resolve and signal continue, or halt the analysis
        ;;
    esac
  done

  # Fell through — hit the hard cap
  echo "ERROR: 4-bot review reached $max_review_iterations iterations for $dir"
  present_for_human_review "$dir"
  wait_for_human_input
  return 2
}

# Returns 0 on PASS, 1 on regression, 2 on escalation/max-iterations.
run_1bot_review() {
  dir=$1
  i=0
  while [ $i -lt $max_review_iterations ]; do
    i=$((i + 1))
    if [ $i -gt 2 ]; then
      echo "WARNING: 1-bot review iteration $i for $dir"
    fi

    run_agent --name "$(pick_session_name)" \
      --output "$dir/review/critical" "critical review"

    if ! review_has_category_a_or_b "$dir/review/critical"; then
      # No Category A or B issues — review passes
      if ! run_regression_check "$dir"; then
        return 1
      fi
      check_upstream_feedback "$dir"
      return 0
    fi

    # Category A issues found — escalate after 3 iterations
    if [ $i -ge 3 ]; then
      echo "ESCALATING: 1-bot review not converging after $i iterations for $dir"
      present_for_human_review "$dir"
      wait_for_human_input
      # Human may resolve and signal continue, or halt
      continue
    fi

    # Iterate
    exec_name=$(pick_session_name)
    write_iteration_inputs_1bot "$dir" "$i" "$exec_name"
    run_agent --name "$exec_name" \
      --output "$dir/exec" "iterate v$((i+1))"
  done

  # Fell through — hit the hard cap
  echo "ERROR: 1-bot review reached $max_review_iterations iterations for $dir"
  present_for_human_review "$dir"
  wait_for_human_input
  return 2
}

# --- Main pipeline ---
#
# *** EXAMPLE PATTERN ***
# The channel names (channel_a, channel_b) and calibration names
# (calibration_1, calibration_2) below are placeholders. Replace them
# with your analysis-specific names. Single-channel analyses can drop
# the for-loop entirely.
#
# Unified flow for both measurements and searches:
#   4a → 4b → human gate → 4c → 5

run_agent --name "$(pick_session_name)" \
  --output "phase1_strategy/exec" "execute phase 1"
run_4bot_review "phase1_strategy" || exit 1
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase1): strategy"

run_agent --name "$(pick_session_name)" \
  --output "phase2_exploration/exec" "execute phase 2"
# Self-review only — no external review
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase2): exploration"

# Phase 3 — per channel (parallel execution, sequential review)
for channel in channel_a channel_b; do
  run_agent --name "$(pick_session_name)" \
    --output "phase3_selection/channel_$channel/exec" \
    "execute phase 3 ($channel)" &
done
wait
for channel in channel_a channel_b; do
  run_1bot_review "phase3_selection/channel_$channel" || exit 1
done
run_agent --name "$(pick_session_name)" \
  --output "phase3_selection/exec" "consolidate channels"
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase3): selection"

# Shared calibrations (can run in parallel with phases 2-3)
for cal in calibration_1 calibration_2; do
  run_agent --name "$(pick_session_name)" \
    --output "calibrations/$cal" "calibration: $cal" &
done
# Calibrations must complete before Phase 4a — calibration artifacts
# (scale factors, corrections) are required inputs for inference.
wait

# Phase 4a — agent gate (4-bot review must PASS to proceed)
run_agent --name "$(pick_session_name)" \
  --output "phase4_inference/4a_expected/exec" "execute phase 4a"
run_4bot_review "phase4_inference/4a_expected" || {
  echo "Phase 4a review did not pass."
  exit 1
}
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase4a): expected results"

# Unified flow: both measurements and searches use 4b + 4c
run_agent --name "$(pick_session_name)" \
  --output "phase4_inference/4b_partial/exec" "10% data validation"
run_4bot_review "phase4_inference/4b_partial" || exit 1
present_for_human_review "phase4_inference/4b_partial"
wait_for_human_decision  # APPROVE / REQUEST CHANGES / HALT
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase4b): partial validation"

run_agent --name "$(pick_session_name)" \
  --output "phase4_inference/4c_observed/exec" "full data"
run_1bot_review "phase4_inference/4c_observed" || exit 1
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase4c): observed results"

run_agent --name "$(pick_session_name)" \
  --output "phase5_documentation/exec" "execute phase 5"
run_4bot_review "phase5_documentation" || exit 1
git add phase*/ calibrations/ *.md pixi.toml && git commit -m "feat(phase5): analysis note"
```
