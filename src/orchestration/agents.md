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
| `lead-analyst` | opus | 1, 2 (consolidation) | Strategy development, Phase 2 consolidation |
| `hypothesis-agent` | sonnet | 2 | Literature, hypotheses, model generators |
| `data-acquisition-agent` | haiku | 2 | Fast sample inventory, data quality |
| `data-quality-agent` | sonnet | 2 | Object definitions, data validation |
| `projector-agent` | sonnet | 3 | Selection optimization, signal projection |
| `signal-lead` | sonnet | 3 | Event selection (5-step philosophy) |
| `ml-specialist` | opus | 3 (if MVA) | BDT/DNN/ME discriminants |
| `background-estimator` | sonnet | 3 | Background estimation, CR/VR design |
| `systematic-source-evaluator` | sonnet | 4a | Per-source systematic (×N parallel) |
| `systematics-fitter` | opus | 4a, 4b, 4c | Likelihood, fits, diagnostics |
| `cross-checker` | sonnet | 4c | Independent validation |
| `note-writer` | sonnet | 4b, 5 | Analysis note drafting |

#### Review Agents

| Agent | Model | Review tiers | Description |
|-------|-------|-------------|-------------|
| `physics-reviewer` | opus | 4-bot, 5-bot | Senior physicist review (no methodology) |
| `critical-reviewer` | opus | All tiers | Find flaws (bad cop) |
| `constructive-reviewer` | opus | 4-bot, 5-bot | Strengthen analysis (good cop) |
| `rendering-reviewer` | sonnet | 5-bot only | PDF compilation and rendering QA |
| `plot-validator` | opus | All tiers | Programmatic + physics sanity checks on figures |
| `arbiter` | opus | 4-bot, 5-bot | Adjudicate, issue PASS/ITERATE/ESCALATE |

#### Support Agents

| Agent | Model | When | Description |
|-------|-------|------|-------------|
| `investigator` | opus | Regression trigger | Impact tracing, REGRESSION_TICKET.md |

---

### Phase-to-Agent Mapping

| Phase | Executors | Review tier | Review agents |
|-------|-----------|-------------|---------------|
| **1: Strategy** | `lead-analyst` | 4-bot | physics + critical + constructive + plot-validator → arbiter |
| **2: Exploration** | `data-acquisition-agent` + `data-quality-agent` + `hypothesis-agent` (parallel) → `lead-analyst` (consolidation) | Self-review | (none) |
| **3: Selection** | `signal-lead` + `background-estimator` (per channel); `ml-specialist` if MVA | 1-bot | critical + plot-validator |
| **4a: Expected** | `systematic-source-evaluator` (×N parallel) → `systematics-fitter` | 4-bot | physics + critical + constructive + plot-validator → arbiter |
| **4b: Partial** | `systematics-fitter` + `note-writer` | 4-bot → human gate | physics + critical + constructive + plot-validator → arbiter |
| **4c: Observed** | `systematics-fitter` + `cross-checker` | 1-bot | critical + plot-validator |
| **5: Documentation** | `note-writer` | 5-bot | physics + critical + constructive + rendering + plot-validator → arbiter |

---

### Model Tiering

Read `model_tier` from `analysis_config.yaml`:

| Role | `auto` (default) | `uniform_high` | `uniform_mid` |
|------|-------------------|----------------|----------------|
| Phase 1 executor | opus | opus | sonnet |
| Phase 2 executors | haiku/sonnet | opus | sonnet |
| Phase 3 executors | sonnet | opus | sonnet |
| Phase 4 executors | opus (fitter), sonnet (others) | opus | sonnet |
| Phase 5 executor | sonnet | opus | sonnet |
| 4/5-bot reviewers | opus | opus | sonnet |
| 1-bot reviewer | opus | opus | sonnet |
| Plot-validator | opus | opus | sonnet |
| Arbiter | opus | opus | sonnet |
| Investigator | opus | opus | sonnet |

---

### Execution Agent Launch Template

**Context:** Bird's-eye framing, relevant methodology sections (per §3a.4.2
table), physics prompt, upstream artifacts, experiment log (if exists),
experiment corpus (via RAG), phase CLAUDE.md

**Writes:** `plan.md`, primary artifact (in `exec/`), `scripts/` and `figures/`
(at phase level), appends to `experiment_log.md`

**Instruction core:**
```
Execute Phase N of this analysis. Your detailed role instructions are in
.claude/agents/{agent-name}.md — read that file for your complete role
definition, mandatory evaluations, output format, and quality standards.

Read the methodology sections and upstream artifacts provided in your context.
Read the applicable conventions/ file for technique-specific requirements.
Query the retrieval corpus as needed.

Before writing code, produce plan.md. As you work:
- Write analysis code to ../scripts/, figures to ../figures/ (phase level)
- All code runs through pixi: `pixi run py path/to/script.py`
- Follow the plotting template in methodology/appendix-plotting.md for ALL figures
- Commit frequently with conventional commit messages
- Append to experiment_log.md: what you tried, what worked, what didn't
- Produce your primary artifact as {ARTIFACT_NAME}.md

When complete, state what you produced and any open issues.
```

---

### Physics Reviewer Launch Template

**Context:** Bird's-eye framing, physics prompt, artifact under review.
**Does NOT receive:** Methodology spec, conventions files, review criteria.
The physics reviewer evaluates the work purely as a senior collaboration
member (ARC/L2 convener) would.

**Writes:** `{NAME}_PHYSICS_REVIEW.md`

**Instruction core:**
```
You are a senior collaboration member reviewing this analysis for physics
approval. Your detailed role instructions are in .claude/agents/physics-reviewer.md.

You have NOT read the methodology spec or conventions — you are
reviewing the physics on its merits.

Read the artifact. Read all figures produced by this phase.

Evaluate:
- Is the physics motivation sound and complete?
- Are the backgrounds correctly identified and estimated?
- Is the systematic treatment appropriate for this measurement?
- Are the cross-checks adequate?
- Do the plots and numbers make physical sense?
- Are yields in the expected ballpark?
- Do distributions have the right shapes?
- Would you approve this analysis for publication?

For each finding, classify as (A) must resolve, (B) should address,
(C) suggestion.
```

---

### Critical Reviewer Launch Template

**Context:** Bird's-eye framing, review methodology (§6), applicable phase
section from §3, artifact under review, upstream artifacts, experiment log,
experiment corpus (via RAG)

**Writes:** `{NAME}_CRITICAL_REVIEW.md`

**Instruction core:**
```
You are a critical reviewer for a physics analysis that will be submitted
for journal publication. Your detailed role instructions are in
.claude/agents/critical-reviewer.md.

Your job is to find flaws — both in what is present (correctness) and in
what is absent (completeness).

Read the artifact and the experiment log (to understand what was tried).
Read methodology/06-review.md §6.3 (reviewer framing) and §6.4 (review
focus for this phase) — these define what you must check.
Read the applicable conventions/ file and verify coverage row-by-row.
Read methodology/appendix-plotting.md §6.4.2 for the figure checklist —
apply it to every figure.

Before concluding, answer: "If a competing group published a measurement of
the same quantity next month, what would they have that we don't?" If the
answer is non-empty and unjustified, those are Category A findings.

Classify every issue as (A) must resolve, (B) should address, (C) suggestion.
Err on the side of strictness.
```

---

### Constructive Reviewer Launch Template

**Context:** same as critical reviewer

**Writes:** `{NAME}_CONSTRUCTIVE_REVIEW.md`

**Instruction core:**
```
You are a constructive reviewer for a physics analysis targeting journal
publication. Your detailed role instructions are in
.claude/agents/constructive-reviewer.md.

Your job is to strengthen the analysis.

Read the artifact and experiment log.

Identify where the argument could be clearer, where additional validation
would build confidence, and where the presentation could be improved.
Focus on Category B and C issues, but escalate to A if you find genuine
errors.
```

---

### Plot Validator Launch Template

**Context:** Bird's-eye framing, plotting template (appendix-plotting.md),
scripts and figures produced by the phase, upstream artifacts for yield
cross-checks

**Writes:** `{NAME}_PLOT_VALIDATION.md`

**Instruction core:**
```
You are the plot validation agent. Your detailed role instructions are in
.claude/agents/plot-validator.md.

Run programmatic and physics sanity checks on ALL figures and plotting
scripts produced by this phase. You do NOT rely on visual inspection —
you examine the code, the data, and the output programmatically.

Check:
1. Plotting code compliance (matplotlib styling, figure size, no titles, etc.)
2. Physics sanity (yields reasonable, distributions physical, ratios sensible)
3. Consistency (same yields across plots, cutflow monotonic, normalization correct)
4. Red flags (negative yields, efficiency > 1, chi2/ndf > 5, NP pull > 3σ)

Every failed check is a Category A finding. Produce a PLOT_VALIDATION report.
```

---

### Rendering Reviewer Launch Template (Phase 5 only)

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
```

---

### Arbiter Launch Template

**Context:** Bird's-eye framing, review methodology (§6), artifact, all
reviews (physics, critical, constructive, plot-validation, rendering if Phase 5)

**Writes:** `{NAME}_ARBITER.md`

**Instruction core:**
```
You are the arbiter. Your detailed role instructions are in
.claude/agents/arbiter.md.

Read the artifact and ALL reviews (physics, critical, constructive,
plot-validation, and rendering if Phase 5). For each issue:
- If reviewers agree: accept the classification
- If they disagree: assess independently with justification
- If they all missed something: raise it yourself

Plot-validation red flags are automatic Category A — do not downgrade them.

End with: PASS / ITERATE (list Category A items) / ESCALATE (document why).
```
