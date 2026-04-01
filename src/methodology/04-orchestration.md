## 3a. Orchestration and Agent Architecture

This section covers how agents coordinate: the orchestrator loop, subagent
prompts, health monitoring, context management, and parallelism.

---

### 3a.1 Orchestrator Architecture

When a single agent session runs the full analysis, it operates as a **thin
orchestrator** that delegates work to subagents. The orchestrator's context
stays small; the heavy work happens in subagent contexts that are discarded
after each phase. This is the primary defense against context exhaustion.

**Architecture:** The main session (orchestrator) never writes analysis code
or produces figures itself. It spawns subagents for execution and review,
reads their summaries, makes phase-transition decisions, and commits. Each
subagent reads upstream artifacts from disk — not from the parent's context.

**The orchestrator loop** follows a repeating EXECUTE → REVIEW → CHECK →
COMMIT → ADVANCE cycle for each phase. The canonical, detailed loop
(including human gates, context splitting, and anti-patterns) lives in
`templates/root_claude.md` — that file is auto-loaded by Claude Code into
every orchestrator session, making it the authoritative reference agents
read at runtime. This methodology section provides the architectural
rationale; the template provides the operational instructions.

The cycle structure is: spawn an executor subagent for the phase work,
spawn reviewer subagent(s) at the appropriate tier, read review
findings and resolve any Category A/B issues or regression triggers, commit,
then advance. Phase 4 adds a human gate after 4b for both measurements and
searches.

**Why subagents solve context exhaustion:**
- The Phase 2 executor agent processes 40 MC files, debugs ROOT branch
  names, produces 12 figures. This consumes 50k+ tokens of context. When it
  finishes and returns a 500-token summary, all that bulk is gone. The
  orchestrator's context grows by 500 tokens, not 50k.
- By Phase 5, the orchestrator has accumulated only ~5k tokens of phase
  summaries. It has full context budget to spawn the AN-writing agent with a
  detailed prompt.
- If the orchestrator itself hits context limits despite staying thin, the
  committed artifacts + experiment log on disk are a complete checkpoint.
  A new session can read them and resume from the last committed phase.

The orchestrator reads: CLAUDE.md files, phase summaries returned by
subagents, review findings, and the experiment log when deciding next steps.
It writes: commit messages and (if needed) the physics prompt passed to
subagents. See `templates/root_claude.md` for the full list of what the
orchestrator does and does not do.

**Review is always by subagent.** Self-review is not an acceptable fallback.
If the agent framework cannot spawn subagents, the analysis cannot proceed
past Phase 2 (which uses self-review by design). All other phases require
independent reviewer agents. This is non-negotiable — the author reviewing
their own work produces systematically weaker quality.

**Anti-pattern:** Running straight from Phase 1 to Phase 5 in a single pass,
producing only the strategy document and the final analysis note, with no
intermediate artifacts, no experiment log entries, and no reviews. This is
the failure mode the orchestrator pattern exists to prevent.

**Anti-pattern:** The orchestrator doing the phase work itself instead of
delegating. If the orchestrator is writing analysis scripts, it is not
orchestrating — it is executing, and its context will fill up.

---

### 3a.2 Subagent Roles and Context

The orchestrator spawns subagents in two categories: **executors** and
**reviewers**. Each receives curated context assembled per §3a.4.2 (three
layers: bird's-eye framing, relevant methodology sections, upstream
artifacts). See `orchestration/agents.md` for literal, copy-pasteable
prompt templates for each role.

**Executor subagents** receive the phase CLAUDE.md, upstream artifact paths,
experiment log, and conventions path. They work in plan-then-code mode:
produce `plan.md` first, then scripts/figures, then the phase artifact last.

**Reviewer subagents** come in four roles:

| Role | Context | Goal |
|------|---------|------|
| Physics reviewer | Physics prompt + artifact only (no methodology, no conventions) | Evaluate as a senior collaboration member: "Would I approve this?" |
| Critical reviewer | Full context (methodology + conventions + artifact) | Find all flaws in correctness and completeness |
| Constructive reviewer | Same as critical | Strengthen: clarity, additional validation, presentation |
| Arbiter | All reviews + artifact | Adjudicate, issue PASS / ITERATE / ESCALATE |

**4-bot review** spawns all four (first three in parallel). See
`methodology/06-review.md` §6.2–6.4 for the full protocol. The arbiter
must not PASS with unresolved A or B items. The bar is high: ITERATE
liberally, PASS only when a senior physicist would be comfortable.

---

### 3a.3 Health Monitoring

The orchestrator should:
- **Commit before spawning** each subagent, so work is checkpointed.
- **Check progress** every ~5 minutes for long-running subagents (where the
  agent framework supports non-blocking progress checks).
- **Respawn stalled agents** — if a subagent has not committed in >10 minutes
  and shows no progress, terminate and respawn from the last commit.
- When the agent framework supports **background/non-blocking agent spawning**,
  the orchestrator should use it for long-running subagents. This allows
  monitoring and respawning without blocking the orchestrator's context.

**Context splitting for heavy phases.** Phase 4b and Phase 5 are the most
context-intensive phases because they involve AN writing alongside statistical
analysis. When context pressure is high, the orchestrator should split these
into separate subagent invocations:
- One subagent for the statistical analysis (inference, diagnostics)
- A second subagent for the AN writing/rendering
The AN-writing subagent reads the inference artifact from disk — it does not
need the full statistical analysis context. This keeps each subagent within
comfortable context limits.

---

### 3a.4 Context Management

#### 3a.4.1 Artifacts as Handoffs

The only information that crosses phase boundaries is the written artifact. No
conversation history, no shared variables, no implicit state. Each agent session
starts from artifacts and instructions, not from prior conversations.

#### 3a.4.2 What Each Agent Receives

**Pre-generated phase context.** Before spawning any subagent for Phase N,
the orchestrator generates `phase_context_N.md` — a single file containing
all methodology sections, conventions, and framing that Phase N agents need.
This is assembled once per phase and passed to every subagent (executor,
reviewers, arbiter) as a single read, replacing 5-6 separate file reads.
The file is written to `phase*/context/phase_context_N.md` and regenerated
only if upstream methodology files change.

Every agent — executor, reviewer, arbiter — receives a curated context
assembled by the orchestrating agent or the human launching the session. The
context has three layers:

**Layer 1: Bird's-eye framing (~1 page).** All agents receive this. It
provides the analysis-level context that prevents agents from losing sight of
the end goal:

- The physics prompt (what we're measuring/searching for)
- The analysis type (measurement or search) and technique
- The current phase and what it must deliver
- The applicable conventions (by reference: "read `conventions/unfolding.md`")
- The end goal: a publication-quality analysis note suitable for journal
  submission. Every phase contributes to this goal.

This framing is critical. Without it, agents optimize for local phase
completion rather than the overall analysis quality. A reviewer who knows the
result will be submitted to a journal applies a higher standard than one who
thinks it's an internal exercise.

**Layer 2: Relevant methodology sections (~2-5 pages).** The orchestrating
agent selects which methodology sections each agent needs. Not every agent
reads the full spec — that would waste context on irrelevant material. The
selection depends on the role:

| Role | Methodology sections |
|------|---------------------|
| Phase 1 executor | Sections 1, 2, 3 (Phase 1), 5, 7 |
| Phase 2 executor | Sections 3 (Phase 2), 5, 7, Appendix D |
| Phase 3 executor | Sections 3 (Phase 3), 5, 7, 11, Appendix D |
| Phase 4 executor | Sections 3 (Phase 4), 4, 5, 7, 11, Appendix D |
| Phase 5 executor | Sections 3 (Phase 5), 5, Appendix D |
| 4/5-bot reviewer | Sections 6, applicable phase from 3, applicable conventions, appendix checklist |
| 1-bot reviewer | Section 6, applicable phase from 3, applicable conventions |
| Arbiter | Section 6, applicable conventions |
| Plot subagent | Appendix D (Plotting Template) |

The CLAUDE.md files (project-root and per-phase) are always loaded
automatically by Claude Code. These provide the essential rules (tool
requirements, pixi, coding standards) without needing to load the full
methodology.

**Layer 3: Upstream artifacts (~2-10 pages per phase).** The phase's input
artifacts from prior phases, plus the experiment log if continuing a session
within a phase.

#### 3a.4.3 Context Budget

Even at Phase 5, the total curated input should be bounded at ~20-30 pages.
The orchestrating agent is responsible for keeping context lean:

- Include only relevant methodology sections, not the full spec
- Summarize long upstream artifacts if they exceed ~5 pages
- The experiment log is consulted on demand, not loaded in full

#### 3a.4.4 What Goes Where

- **Artifact:** Decisions, results, reasoning, key figures (by path),
  validation outcomes. Everything a reader needs to evaluate the analysis.
- **Scripts directory:** Code that produced the results. Referenced from the
  artifact for reproducibility, but not read by downstream phases.
- **Supplementary files:** Full tables, workspaces, trained models. Referenced
  from the artifact, consulted only when needed.

#### 3a.4.5 Artifacts Before Speed

When context pressure mounts (approaching context limits, long session),
the agent must prioritize writing the current phase's artifact over rushing
to start the next phase. A completed Phase 3 with a written `SELECTION.md`
artifact is far more valuable than a half-finished Phase 4 with no
intermediate artifacts.

- The artifact is the checkpoint. Code on disk without a written artifact is
  recoverable but expensive — the next session must re-derive the reasoning.
- **Never skip an artifact to "save context."** Writing an artifact costs
  fewer tokens than re-doing the work it documents.
- If the session must stop, commit the current phase's work (artifact +
  scripts + experiment log) and stop cleanly. The next session reads the
  artifacts and resumes.

---

### 3a.5 Parallelism and Sub-delegation

This specification is written for a single agent executing phases sequentially.
For parallel execution:

- **Within a phase:** Multiple agents may work in parallel provided they write
  to separate sub-artifacts and a consolidation step merges outputs before
  review.
- **Across phases:** Sequential by design. An agent beginning Phase N reads the
  completed artifact from Phase N-1.
- **Review as a separate agent:** Results and writeup reviews should be distinct
  agent invocations. This provides adversarial review that self-review cannot.
- **Per-channel parallelism:** In multi-channel analyses, channel-specific work
  in Phases 2–3 can proceed in parallel as separate agent teams, merging in
  Phase 4.

#### 3a.5.1 Sub-delegation Within a Phase

Phase executors should sub-delegate compute-heavy or narrowly-scoped tasks to
sub-agents rather than attempting everything in a single session. The executor
acts as coordinator: it plans the work, delegates execution, and integrates
results.

Tasks well-suited for sub-delegation:
- **MVA training** — hyperparameter search, overtraining validation, feature
  importance. The sub-agent receives the training data specification and
  returns the trained model + performance metrics.
- **Systematic variation evaluation** — each systematic source (or group of
  related sources) can be evaluated independently.
- **Plot generation** — once the data is prepared, producing a batch of
  standard plots is mechanical work suitable for a dedicated sub-agent.
- **Closure tests** — running fits or comparisons in validation regions.

Sub-agents within a phase:
- Run **sequentially by default** (to avoid conflicting file writes), unless
  their outputs are guaranteed independent (separate directories).
- Receive **explicit, bounded inputs** — the executor writes an input
  specification, the sub-agent reads it and writes output files.
- Share the phase's **experiment log** — sub-agents append to the same log.
- Use **dedicated sub-agents** — BDT training and plot generation can use
  dedicated sub-agents; the executor coordinates them.

The executor should not sub-delegate *judgment* — decisions about which
backgrounds to include, what selection approach to use, or whether closure
tests pass are the executor's responsibility. Sub-agents handle execution.

---

### 3a.6 STATE.md Management

The `StateManager` module (`scripts/state_manager.py`) provides programmatic
STATE.md read/write with cross-session persistence:

- **Phase tracking:** `advance_phase(N, artifact, review, notes)` records
  completion and advances to the next phase.
- **Review iteration counting:** `record_review_iteration(phase, issues_a, issues_b)`
  increments per-phase counters. `should_warn(phase)` at 3 iterations,
  `should_hard_stop(phase)` at 10.
- **Data callback tracking:** `record_data_callback(reason)` enforces the
  2-callback hard cap. `can_data_callback()` checks before spawning.
- **Blocker tracking:** `add_blocker(description)` persists blockers.
- **Cross-session reliability:** `load()` fully restores all state fields
  (phase history, iteration counts, blockers, callback count) from STATE.md
  on session restart.

---

### 3a.7 Cross-Analysis Memory System

The memory system enables learning across analyses:

- **Global memory** (`<repo>/memory/{L0,L1,L2,causal_graph}/`) persists
  high-confidence findings across analyses.
- **Scaffolding:** `scaffold_analysis.py` copies global memory into each
  new analysis's local `memory/` directory.
- **Session commit:** After analysis completion, `session_commit.py`
  extracts experiences and `promote_to_global()` copies entries with
  confidence ≥ 0.6 back to global.
- **Lifecycle:** Entries decay (-0.01 per analysis), quarantine at conf < 0.1,
  archive when hotness < 0.1. Prevents unbounded growth.

---
