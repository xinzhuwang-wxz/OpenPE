# Phase 5: Verification

> **Phase 5: Verification** independently verifies the analysis chain through
> reproduction, provenance auditing, logic auditing, and EP verification —
> then gates on human approval.

You are running Phase 5 for a **{{analysis_type}}** analysis named
**{{name}}**.

**Start in plan mode.** Before running any verification checks, produce a
plan: which key result you will independently reproduce, which data sources
you will spot-check, which causal claims you will audit, and what the human
gate presentation will contain. Execute after the plan is set.

---

## Input requirements

Phase 5 depends on completed Phase 4 artifacts. Before beginning, verify:

1. `exec/PROJECTION.md` exists with scenario simulations and convergence classification
2. `exec/ANALYSIS.md` exists with post-refutation causal findings
3. `data/registry.yaml` is complete with provenance for every dataset
4. All figures referenced in Phase 3 and Phase 4 artifacts exist in `figures/`
5. The experiment log is up to date through Phase 4

If any of these are missing, halt and request completion of prior phases.

---

## Output artifact

| Artifact | Path | Contents |
|----------|------|----------|
| **VERIFICATION.md** | `exec/VERIFICATION.md` | Reproduction results, provenance audit, logic audit, EP verification, overall pass/fail, human gate materials |

VERIFICATION.md must exist and pass automated checks before the human gate.

---

## Agent profile

Phase 5 uses the verifier agent. Read the profile before beginning:

| Agent | Profile | Steps |
|-------|---------|-------|
| Verifier agent | `.claude/agents/verifier.md` | 5.1 – 5.5 |

**Independence requirement:** The verifier agent must not reuse code from
Phases 1–4. It writes its own scripts to reproduce results. This is the
entire point — an independent check catches systematic errors that
self-consistency checks miss.

---

## Step 5.1 — Independent Reproduction

**Goal:** Independently re-derive at least one key statistical result from
the analysis without reusing any Phase 1–4 code.

**The agent must:**

1. **Select the reproduction target.** Choose the single most important
   quantitative result from Phase 3 — typically the primary causal effect
   size or the highest-EP edge's statistical test. Document why this result
   was chosen.

2. **Write independent code.** Starting from the processed data in
   `data/processed/`, implement the statistical computation from scratch.
   Do not import, copy, or reference Phase 3 scripts. Use different
   libraries or methods where feasible (e.g., if Phase 3 used scipy,
   the verifier may use statsmodels or a manual implementation).

3. **Compare results.** The reproduction passes if:
   - Point estimates agree within 2σ of the reported uncertainty
   - Confidence intervals overlap substantially (>50% overlap)
   - The qualitative conclusion (direction and significance) matches

4. **Document discrepancies.** If results disagree:
   - Investigate the source of disagreement
   - Determine whether the discrepancy is due to methodology differences
     (acceptable) or errors in Phase 3 code (Category A finding)
   - Report the discrepancy magnitude and likely cause

**Output:** Reproduction results table in VERIFICATION.md with pass/fail
verdict and discrepancy analysis if applicable.

---

## Step 5.2 — Data Provenance Audit

**Goal:** Spot-check that data in `data/raw/` actually came from the claimed
sources and contains the claimed values.

**The agent must:**

1. **Select audit targets.** Choose at least 3 datasets from `registry.yaml`,
   prioritizing:
   - Datasets supporting the highest-EP causal edges
   - Any datasets flagged with quality warnings in Phase 0
   - At least one user-provided dataset (if Mode B)

2. **Verify source URLs.** For each selected dataset:
   - Fetch the source URL listed in `registry.yaml`
   - Confirm the URL is still accessible and points to the claimed source
   - If the URL is dead, search for the dataset at the source organization

3. **Spot-check values.** For each selected dataset:
   - Pick 5 randomly selected data points
   - Verify their values against the source (re-download or cross-reference)
   - Check units, temporal alignment, and geographic scope match claims

4. **Verify file integrity.** Recompute SHA-256 hashes for audited raw files
   and compare to `registry.yaml` entries.

5. **Report findings:**

   | Dataset | URL valid | Values match | Hash match | Verdict |
   |---------|-----------|-------------|------------|---------|
   | ds_001  | YES       | 5/5         | YES        | PASS    |
   | ds_003  | NO (301)  | 4/5         | YES        | FLAG    |

**Output:** Provenance audit table in VERIFICATION.md.

---

## Step 5.3 — Logic Audit

**Goal:** Verify that causal claims in Phase 3 are logically consistent with
the refutation test results.

**The agent must:**

1. **For each causal edge labeled DATA_SUPPORTED:** Verify that the
   refutation test actually tested the causal claim (not a weaker
   correlational claim). Check:
   - Was the appropriate statistical test used?
   - Were confounders controlled for?
   - Does the effect size justify the causal interpretation?

2. **For each edge labeled REFUTED:** Confirm the refutation evidence is
   compelling — not a false negative due to insufficient power or data
   quality issues.

3. **For each edge labeled CORRELATION:** Verify that the analysis correctly
   identified why causation could not be established (confounders,
   reverse causation, common cause, insufficient data).

4. **Check DAG consistency.** Verify that the final causal DAG is a valid
   DAG (no cycles) and that all edges are accounted for in the analysis.

5. **Flag logical gaps.** Common issues:
   - Claiming causation without controlling for confounders
   - Ignoring reverse causation possibility
   - Treating statistical significance as proof of causation
   - Missing edges that would create alternative explanations

**Output:** Logic audit findings in VERIFICATION.md with pass/flag/fail
per edge.

---

## Step 5.4 — EP Verification

**Goal:** Verify that EP propagation calculations are mathematically correct
throughout the analysis chain.

**The agent must:**

1. **Recompute all EP values.** For every edge in the final DAG:
   - Verify EP = truth × relevance using the reported values
   - Verify that post-refutation EP updates follow the documented rules
   - Check that DATA_SUPPORTED edges have truth ≥ 0.7

2. **Recompute all Joint_EP chains.** For every causal chain reported:
   - Verify Joint_EP = product of individual EPs along the chain
   - Verify truncation thresholds were applied correctly
   - Check that soft-truncated chains received lightweight treatment only

3. **Verify projection EP decay.** From Phase 4:
   - Confirm decay multipliers match the documented schedule
   - Verify that CORRELATION edges decay at 2x rate
   - Confirm HYPOTHESIZED edges contribute only to scenario spread

4. **Report calculation errors.** Any arithmetic error in EP propagation is
   a Category A finding that blocks Phase 6. Report the incorrect value,
   the correct value, and the downstream impact.

**Output:** EP verification table in VERIFICATION.md:

```markdown
## EP Verification

| Chain | Reported Joint_EP | Recomputed Joint_EP | Match | Notes |
|-------|-------------------|---------------------|-------|-------|
| A→B→C | 0.33 | 0.33 | YES | — |
| D→E | 0.28 | 0.24 | NO | truth for D→E should be 0.6, not 0.7 |
```

---

## Step 5.5 — Human Gate Protocol

**Goal:** After all automated verification completes, present findings to the
human decision-maker for final approval.

**The agent must prepare and present the following materials:**

### 1. Verification Report Summary

| Check | Result | Details |
|-------|--------|---------|
| Independent reproduction | PASS/FAIL | [1-line summary] |
| Data provenance audit | PASS/FLAG/FAIL | [N/M sources verified] |
| Logic audit | PASS/FLAG/FAIL | [N flagged edges] |
| EP verification | PASS/FAIL | [N calculation errors] |
| **Overall** | **PASS/FAIL** | — |

**Overall FAIL** if any individual check is FAIL. Overall FLAG if any check
is FLAG but none is FAIL.

### 2. Key Causal Findings Table

| Edge | Classification | EP | 95% CI | Phase 3 evidence |
|------|---------------|-----|--------|------------------|
| A → B | DATA_SUPPORTED | 0.49 | [0.35, 0.63] | [1-line summary] |

### 3. EP Propagation Summary

The main causal chain(s) with Joint_EP at each node, showing how confidence
accumulates and decays.

### 4. Projection Scenario Summaries

For each scenario from Phase 4, a summary of ≤3 paragraphs covering:
trajectory, key assumptions, and endgame classification.

### 5. Warnings and Disputes

- Any DISPUTED edges from the logic audit
- Data quality warnings carried from Phase 0
- Reproduction discrepancies from Step 5.1
- Any EP calculation errors found in Step 5.4

### 6. Human Decision Options

Present these options clearly:

| Option | When to choose | Effect |
|--------|---------------|--------|
| **(a) Approve** | All checks pass or flags are acceptable | Proceed to Phase 6 (Documentation) |
| **(b) Request re-analysis** | Specific findings need revision | Return to specified phase with instructions |
| **(c) Request more data** | Data gaps identified that could strengthen analysis | Return to Phase 0 Step 0.4 for additional acquisition |
| **(d) Terminate** | Analysis question is resolved or no longer relevant | Archive current state; no Phase 6 |

**Wait for human response.** Do not proceed to Phase 6 without explicit
human approval (option a).

---

## Methodology references

- Architecture design: `docs/superpowers/specs/2026-03-28-openpe-architecture-design.md` (Sections 2-5)
- Phase requirements: `methodology/03-phases.md` (for gate protocol)
- Artifacts: `methodology/05-artifacts.md`
- Review protocol: `methodology/06-review.md` Section 6.2 (4-bot review)

---

## Non-negotiable rules

1. **Independence is sacred.** The verifier must not reuse Phase 1–4 code.
   Importing a Phase 3 function into a "verification" script is not
   verification — it is tautology. Write fresh code.

2. **Never rubber-stamp.** If a check cannot be completed (e.g., source URL
   is inaccessible), report it as FLAG, not PASS. Incomplete verification
   is flagged, not assumed passing.

3. **Human gate is mandatory.** No automated process can approve the analysis.
   The human must see the verification report and choose an option. Skipping
   the human gate is a protocol violation.

4. **Category A findings block Phase 6.** If any verification step finds a
   Category A issue (EP calculation error, fabricated data, broken causal
   logic), the analysis cannot proceed to Documentation. It must return to
   the appropriate phase for correction.

5. **Carry forward all caveats.** Every warning, flag, and limitation
   discovered in verification must appear in the human gate presentation.
   Do not suppress inconvenient findings.

6. **Append to the experiment log.** Document all verification decisions:
   reproduction target selection rationale, audit sample selection, any
   discrepancies found and their resolution.

---

## Review

**4-bot review + Human Gate** — see `methodology/06-review.md` for protocol.

Reviewers evaluate:
- Is the reproduction genuinely independent (no code reuse)?
- Are provenance spot-checks representative (not cherry-picked easy cases)?
- Does the logic audit catch all common causal reasoning errors?
- Are EP calculations correctly verified?
- Is the human gate presentation complete and honest?
- Are all warnings and disputes surfaced prominently?

Write findings to `review/REVIEW_NOTES.md`.
