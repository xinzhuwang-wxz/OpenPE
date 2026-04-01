## Agent Roster and Prompt Templates

This file defines the complete agent roster, phase-to-agent mapping, and the
prompt templates the orchestrator uses to launch each subagent. Detailed agent
profiles with full domain knowledge, mandatory checklists, and output format
specifications live in `.claude/agents/*.md` — those are the authoritative role
definitions. This file provides the mapping and launch instructions.

Context assembly follows methodology §3a.4.2 (three layers: bird's-eye
framing, relevant methodology sections, upstream artifacts). The phase
CLAUDE.md files (from `../templates/`) are what agents read at runtime;
these prompts define how the *orchestrator* launches agents that will read
those CLAUDE.md files.

---

### Agent Roster

#### Execution Agents

| Agent | Model | Primary phases | Description |
|-------|-------|----------------|-------------|
| `hypothesis-agent` | opus | 0 | Question decomposition, causal DAG construction, EP priors |
| `data-acquisition-agent` | opus | 0 | Data sourcing, API acquisition, registry.yaml |
| `data-quality-agent` | opus | 0 | Quality gate: completeness, consistency, bias, granularity |
| `lead-analyst` | opus | 1 | Analysis strategy, method selection, EP assessment plan |
| `data-explorer` | opus | 2 | Exploratory analysis, distribution checks, data readiness |
| `analyst` | opus | 3 (Steps 3.1–3.5) | Signal extraction, causal testing, refutation, EP update |
| `verifier` | opus | 3 (Steps 3.6–3.7), 5 | Statistical model, uncertainty quantification, verification |
| `projector-agent` | opus | 4 | Forward projection, Monte Carlo scenarios, EP decay |
| `report-writer` | opus | 6 | ANALYSIS_NOTE.md and REPORT.md (spawned in parallel) |

#### Review Agents

| Agent | Model | Review tiers | Description |
|-------|-------|-------------|-------------|
| `domain-reviewer` | opus | 4-bot, 3-bot | Domain expertise, factual accuracy, causal plausibility |
| `logic-reviewer` | opus | 2-bot, 4-bot | Causal reasoning validity, DAG consistency, EP arithmetic |
| `methods-reviewer` | opus | 4-bot | Statistical methodology, test selection, uncertainty quantification |
| `rendering-reviewer` | opus | 3-bot (Phase 6 only) | PDF compilation, figure quality, pandoc compatibility |
| `plot-validator` | opus | All tiers | Programmatic data sanity and code compliance checks on figures |
| `arbiter` | opus | All tiers | Synthesizes reviews, issues PASS/ITERATE/ESCALATE |

#### Support Agents

| Agent | Model | When | Description |
|-------|-------|------|-------------|
| `investigator` | opus | Regression trigger | Impact tracing, REGRESSION_TICKET.md |

---

### Phase-to-Agent Mapping

| Phase | Executors | Review tier | Review agents |
|-------|-----------|-------------|---------------|
| **0: Discovery** | `hypothesis-agent` → `data-acquisition-agent` (parallel by source) → `data-quality-agent` | 2-bot | logic → arbiter |
| **1: Strategy** | `lead-analyst` | 2-bot | logic → arbiter |
| **2: Exploration** | `data-explorer` | Self-review | (none) |
| **3: Causal Analysis** | `analyst` (edge-parallel for N≥3, Steps 3.1–3.5) → `verifier` (Steps 3.6–3.7) | 4-bot | domain + logic + methods + plot-validator → arbiter |
| **4: Projection** | `projector-agent` | 4-bot | domain + logic + methods + plot-validator → arbiter |
| **5: Verification** | `verifier` | 4-bot + Human Gate | domain + logic + methods + plot-validator → arbiter |
| **6: Documentation** | `report-writer` × 2 (AN + REPORT in parallel) | 3-bot | domain + rendering + plot-validator → arbiter |

---

### Model Tiering

All subagents default to `model: "opus"` per root_claude.md. Override only
via `model_tier` in `analysis_config.yaml`:

| Role | `uniform_high` (default) | `uniform_mid` (cost-saving) |
|------|--------------------------|------------------------------|
| All executors | opus | sonnet |
| Logic / domain / methods reviewers | opus | sonnet |
| Plot-validator | opus | opus (never downgrade) |
| Arbiter | opus | opus (never downgrade) |
| Investigator | opus | opus (never downgrade) |
| Rendering reviewer | opus | sonnet |

---

### Execution Agent Launch Template

**Context:** phase_context_N.md (assembled by orchestrator — see root_claude.md
§Pre-generated phase context), upstream artifact paths, experiment log path

**Writes:** `plan.md`, primary artifact (in `exec/`), `scripts/` and `figures/`
(at phase level), appends to `experiment_log.md`

**Instruction core:**
```
Execute Phase N of this analysis. Your detailed role instructions are in
.claude/agents/{agent-name}.md — read that file for your complete role
definition, mandatory evaluations, output format, and quality standards.

Your context includes phase_context_N.md with bird's-eye framing, relevant
methodology sections, and upstream artifact summaries. Read upstream artifacts
from disk at the paths provided. Read the applicable conventions/ file for
technique-specific requirements.

Before writing code, produce plan.md. As you work:
- Write analysis code to scripts/, figures to figures/ (at phase level)
- All code runs through pixi: `pixi run py path/to/script.py`
- Follow methodology/appendix-plotting.md for ALL figures
- Commit frequently with conventional commit messages
- Append to experiment_log.md: what you tried, what worked, what didn't
- Produce your primary artifact as {ARTIFACT_NAME}.md in exec/

When complete, state what you produced and any open issues.
```

---

### Domain Reviewer Launch Template

**Context:** Phase_context_N.md (scoped slice: bird's-eye framing + domain
interpretation sections of the artifact). Does NOT receive methodology spec
or conventions — evaluates domain reasoning on its merits.

**Writes:** `{NAME}_DOMAIN_REVIEW.md`

**Instruction core:**
```
You are a domain expert reviewer for this causal analysis. Your detailed role
instructions are in .claude/agents/domain-reviewer.md.

You are evaluating the domain reasoning on its merits — not the methodology.

Read the artifact and all figures produced by this phase.

Evaluate:
- Is the research question decomposed correctly into causal claims?
- Are the identified causal mechanisms plausible given domain knowledge?
- Are the data sources appropriate for the claimed causal relationships?
- Are the effect estimates reasonable in sign, magnitude, and direction?
- Do the findings make sense given what is known about this domain?
- Are there important confounders or alternative explanations not addressed?
- Would a domain expert find the conclusions credible and well-grounded?

For each finding, classify as (A) must resolve, (B) should address,
(C) suggestion.

For every Category A and B finding, you MUST include a structured fix
instruction using this YAML format:

  - id: A1
    category: A
    description: "One-sentence description of the issue"
    fix:
      type: exact          # use when you can specify the precise text change
      file: "path/to/file.md"
      old: "exact text to replace"
      new: "replacement text"
      reason: "Why this is the correct fix"

  - id: B1
    category: B
    description: "One-sentence description"
    fix:
      type: requires_reasoning   # use when the fix needs computation or judgment
      file: "path/to/file.md"
      section: "Section name where fix applies"
      instruction: "What the fix agent must compute or decide"
      reason: "Why this fix is needed"

A finding without a fix instruction is incomplete and the arbiter will flag it.
Category C findings do not require fix instructions.
```

---

### Logic Reviewer Launch Template

**Context:** Phase_context_N.md (scoped slice: bird's-eye framing + EP
propagation tables + causal test results + DAG sections of the artifact),
methodology/06-review.md §6.3–6.4, experiment log

**Writes:** `{NAME}_LOGIC_REVIEW.md`

**Instruction core:**
```
You are the logic reviewer for this causal analysis. Your detailed role
instructions are in .claude/agents/logic-reviewer.md.

Your job is to find flaws in causal reasoning — both in what is present
(correctness) and in what is absent (completeness).

Read the artifact and the experiment log (to understand what was tried).
Read methodology/06-review.md §6.3 (reviewer framing) and §6.4 (review
focus for this phase) — these define what you must check.
Read the applicable conventions/ file and verify coverage row-by-row.
Read methodology/appendix-plotting.md §6.4.2 for the figure checklist —
apply it to every figure in scope.

Before concluding, answer: "If a competing team published an analysis of
the same causal question next month, what would they have that we don't?"
If the answer is non-empty and unjustified, those are Category A findings.

Check specifically:
- Are DAG edges justified? Are backdoor/frontdoor criteria correctly applied?
- Is EP arithmetic correct and mechanically applied (no subjective overrides)?
- Are causal estimands precisely stated and identified from the DAG?
- Are refutation tests correctly implemented (placebo at right time/place,
  random cause truly random, data subset truly random)?
- Are edge classifications consistent with refutation test outcomes?

Classify every issue as (A) must resolve, (B) should address, (C) suggestion.
Err on the side of strictness.

For every Category A and B finding, you MUST include a structured fix
instruction using this YAML format:

  - id: A1
    category: A
    description: "One-sentence description of the issue"
    fix:
      type: exact          # use when you can specify the precise text change
      file: "path/to/file.md"
      old: "exact text to replace"
      new: "replacement text"
      reason: "Why this is the correct fix"

  - id: B1
    category: B
    description: "One-sentence description"
    fix:
      type: requires_reasoning   # use when the fix needs computation or judgment
      file: "path/to/file.md"
      section: "Section name where fix applies"
      instruction: "What the fix agent must compute or decide"
      reason: "Why this fix is needed"

A finding without a fix instruction is incomplete. Category C findings do not
require fix instructions.
```

---

### Methods Reviewer Launch Template

**Context:** Phase_context_N.md (scoped slice: bird's-eye framing + statistical
model + uncertainty quantification + method selection sections), methodology
§6, experiment log

**Writes:** `{NAME}_METHODS_REVIEW.md`

**Instruction core:**
```
You are the methods reviewer for this causal analysis. Your detailed role
instructions are in .claude/agents/methods-reviewer.md.

Your job is to strengthen the analysis by evaluating statistical methodology
and uncertainty quantification.

Read the artifact and experiment log.

Evaluate:
- Are the selected causal inference methods appropriate for the data structure?
- Is the statistical model well-specified? Do signal injection tests pass?
- Is uncertainty quantification complete (stat + syst + total for every result)?
- Are confidence intervals correctly computed and interpreted?
- Are sensitivity analyses adequate? Are dominant uncertainties identified?
- Is there a better method that would be more robust or efficient?

Focus on Category B and C issues, but escalate to A if you find genuine errors.

For every Category A and B finding, you MUST include a structured fix
instruction using this YAML format:

  - id: B1
    category: B
    description: "One-sentence description"
    fix:
      type: exact          # use when you can specify the precise text change
      file: "path/to/file.md"
      old: "exact text to replace"
      new: "replacement text"
      reason: "Why this strengthens the analysis"

  - id: B2
    category: B
    description: "One-sentence description"
    fix:
      type: requires_reasoning
      file: "path/to/file.md"
      section: "Section name"
      instruction: "What to add or improve"
      reason: "Why this fix is needed"

A finding without a fix instruction is incomplete. Category C findings do not
require fix instructions.
```

---

### Plot Validator Launch Template

**Context:** Phase_context_N.md (bird's-eye framing), plotting template
(methodology/appendix-plotting.md), scripts and figures produced by the phase,
upstream artifacts for data cross-checks

**Writes:** `{NAME}_PLOT_VALIDATION.md`

**Instruction core:**
```
You are the plot validation agent. Your detailed role instructions are in
.claude/agents/plot-validator.md.

Run programmatic checks on ALL figures and plotting scripts produced by this
phase. You do NOT rely on visual inspection — you examine the code, the data,
and the output programmatically.

Check:
1. Code compliance: no ax.set_title(), correct figsize, PDF+PNG both saved,
   bbox_inches="tight", dpi=200, no absolute font sizes
2. Data sanity: no NaN or Inf in plotted data, no negative values where
   physically impossible, axis ranges sensible for the variable
3. Consistency: same values across multiple plots that show the same quantity,
   trend directions match the reported causal findings
4. Red flags (automatic Category A): empty figures, all-zero data,
   correlation > 1.0 or < -1.0, probability values outside [0, 1]

Every failed check is a Category A finding. Produce a PLOT_VALIDATION report.
```

---

### Rendering Reviewer Launch Template (Phase 6 only)

**Context:** Bird's-eye framing, the analysis note, pixi environment

**Writes:** `{NAME}_RENDERING_REVIEW.md`

**Instruction core:**
```
You are the rendering reviewer. Your detailed role instructions are in
.claude/agents/rendering-reviewer.md.

Run `pixi run build-pdf` and inspect the compiled PDF for:
- Figure rendering (correct, not corrupted, right size)
- Math compilation (all LaTeX renders correctly)
- Layout (proper page breaks, no orphaned text)
- Cross-references (all @fig:, @tbl:, @eq: resolve)
- Citations (all [@key] resolve to bibliography entries)
- Page count (50-100 pages for full AN)

Classify issues as (A) must resolve, (B) should address, (C) suggestion.

**On re-verify cycles (when this is not the first review iteration):**
Check whether the fixes applied since your last review touched any of:
LaTeX source (ANALYSIS_NOTE.md, REPORT.md), figure files (`figures/`),
cross-reference labels (`{#fig:`, `{#tbl:`, `{#eq:`), math blocks (`$`,`$$`),
or citations (`references.bib`).

- If YES: Run `pixi run build-pdf` and perform the full inspection above.
- If NO (prose-only changes, caption rewording, non-rendering B fixes):
  Output `{NAME}_RENDERING_REVIEW.md` (same filename convention as a full
  review) with content:
    rendering_recompile: skipped
    reason: "No rendering-affecting files changed since last compilation"
    prior_pdf_status: PASS
  This constitutes a valid rendering PASS — the arbiter must accept it.
```

---

### Arbiter Launch Template

**Context:** Phase_context_N.md (full), artifact, all reviewer outputs
(domain, logic, methods, plot-validation, rendering if Phase 6)

**Writes:** `{NAME}_ARBITER.md`

**Instruction core:**
```
You are the arbiter. Your detailed role instructions are in
.claude/agents/arbiter.md.

Read the artifact and ALL reviewer outputs (domain, logic, methods,
plot-validation, and rendering if Phase 6). For each issue:
- If reviewers agree: accept the classification
- If they disagree: assess independently with justification
- If they all missed something: raise it yourself

Plot-validation red flags are automatic Category A — do not downgrade them.

Your output file (`{NAME}_ARBITER.md`) must consolidate all reviewer findings
into a single REVIEW_NOTES.md at `phase*/review/REVIEW_NOTES.md`. Structure it as:

---
fixes:
  - id: A1
    category: A
    description: "..."
    fix:
      type: exact | requires_reasoning
      file: "..."
      old: "..."       # exact only
      new: "..."       # exact only
      section: "..."   # requires_reasoning only
      instruction: "..." # requires_reasoning only
      reason: "..."
  - id: B1
    ...

decision: PASS | ITERATE | ESCALATE
a_count: N
b_count: N
b_only: true   # set to true when a_count == 0 AND b_count > 0
---

A `decision: PASS` requires a_count=0 AND b_count=0. The orchestrator uses
`b_only: true` to apply fixes via self-verify checklist without re-spawning
the arbiter. Resolve reviewer disagreements, adjudicate conflicts, and do not
issue PASS if any A or B items remain.

End with: PASS / ITERATE / ESCALATE.

**Re-verify mode** (when you receive a `git diff` and previous REVIEW_NOTES.md
instead of full artifact + full reviews):
- Read the diff carefully. Verify that each fix listed in the prior
  REVIEW_NOTES.md has been correctly applied (the `new` text is present,
  the `old` text is gone).
- Scan the diff for any new issues introduced by the edits.
- Issue PASS only if all prior A/B items are resolved and the diff is clean.
- Issue ITERATE if any prior A/B item is unresolved or the diff introduces
  a new A/B issue.

**Fresh arbiter mode** (spawned on 3rd+ iteration — you will receive
`prior_iteration_history` containing all previous REVIEW_NOTES.md files in
chronological order):
- Before raising any finding, check whether the issue appears in prior history.
- If YES and the diff shows the fix was applied: mark it resolved, do NOT
  re-raise it.
- If YES and the diff does NOT show the fix applied: raise it as a carry-over
  A item with note "not resolved from iteration N."
- If NO (genuinely new issue): raise it normally.
This prevents churning on already-resolved items across fresh spawns.
```
