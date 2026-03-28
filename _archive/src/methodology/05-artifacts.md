## 5. Artifact Format

Every phase produces three types of written output, at different levels of
formality:

### 5.1 The Experiment Log

Each phase maintains an **experiment log** (`experiment_log.md`) — a persistent,
append-only record of what was tried and what happened. This is the analysis
lab notebook.

```markdown
## 2026-03-13 — Exploring jet clustering

Tried Durham algorithm with ycut=0.005 on the signal sample.
- Result: dijet mass resolution ~4 GeV, reasonable
- But: 8% of events have 3+ jets, losing signal efficiency

Tried ycut=0.008 (looser).
- Result: mass resolution ~5 GeV (slightly worse), but only 3% of events
  have 3+ jets. Better signal efficiency.
- Going with ycut=0.008 for now.

## 2026-03-13 — b-tag working point study

Tried tight WP (80% efficiency, 1% mistag).
- S/B = 2.3 in signal region, but only 45 signal events survive.

Tried medium WP (70% efficiency, 2% mistag).
- S/B = 1.1, but 62 signal events. Better expected limit.
- Medium WP gives ~15% better expected significance. Going with medium.
```

The experiment log is:
- **Not a formal artifact** — it does not follow the standard artifact
  structure and is not the handoff document
- **Readable by both agents and humans** — it provides context that the
  formal artifact compresses away
- **Append-only** — entries are never deleted or modified. Failed approaches
  are as valuable as successful ones.
- **Referenced by the formal artifact** — the artifact says "we chose Durham
  with ycut=0.008 (see experiment log for alternatives explored)"
- **Persists across agent sessions within a phase** — if the executor iterates
  10 times, all 10 sessions append to the same log
- **Never empty at the end of a phase.** An empty experiment log at the end
  of Phase 2 or later means the agent did not document its exploration
  process. This is a review finding.

The experiment log is especially valuable for Phases 2–3 where iteration is
high. It prevents agents from re-trying failed approaches and gives humans
visibility into the agent's decision-making without reading full session
transcripts.

**Context management:** The experiment log is a file on disk, not part of the
agent's default input context. Agents read the log on demand — typically at the
start of a session ("what has been tried so far?") and when deciding what to try
next ("have we already explored this direction?"). The log is not loaded into
every agent invocation's input; it is consulted as needed and appended to after
meaningful work. This prevents the log from consuming context budget as it grows.

**When to write:** Append an entry after every material decision, discovery, or
failed attempt. Concrete triggers:
- Discovering the structure of a data file (branches, tree names, event counts)
- Choosing a parameter value (cut threshold, number of iterations, bin edges)
  and the reasoning behind it
- Encountering and resolving a bug or unexpected behavior
- Trying an approach that didn't work (and why)
- Making a design decision that affects downstream phases

If the agent completes a phase without appending to the experiment log, the
phase should be considered incomplete.

### 5.2 The Primary Artifact

Every phase produces a primary artifact (markdown or LaTeX) that serves as the
handoff to subsequent phases and the permanent analysis record.

Artifacts must be **self-contained**: a reader with access only to the artifact
and the experiment corpus should understand what was done, why, and what the
results are.

**Artifacts are analysis note source material.** Phase 4 artifacts in
particular must be written at **publication quality** because the Phase 4b/5
agent reads them directly to draft the analysis note. The artifact quality
determines AN quality — a terse or poorly-written artifact produces a terse
or poorly-written AN section. Write descriptions of methods, systematic
evaluations, and cross-checks as if they were going straight into a journal
publication. Include full context: what was done, why, what the result means,
and how it relates to the physics goal.

### Standard artifact sections:

1. **Summary** — What was accomplished (1 paragraph)
2. **Method** — How it was done, in enough detail to reproduce
3. **Results** — Key findings: tables, figures (by path), numbers with
   uncertainties
4. **Validation** — Checks performed and their quantitative outcomes
5. **Open issues** — What subsequent phases should be aware of
6. **Code reference** — Where scripts live and how to re-execute. Every
   result must be traceable to a `pixi run` command. List the exact task
   names (e.g., `pixi run unfold`, `pixi run systematics`) that produced
   the results, in execution order. A human or agent debugging the analysis
   should be able to trace: result → artifact → `pixi run <task>` → script
   → inputs.

### Presentation requirements:

Artifacts are markdown documents with embedded figure references (paths to
PDF/PNG files in the phase's `figures/` directory). Every quantitative claim
must be supported by a figure or table.

**Figure captions must be self-contained.** A reader should understand what
a figure shows — what is plotted, what the axes are, what the different
curves/markers represent, and what conclusion to draw — from the caption
alone, without reading the surrounding text. Sparse captions like "Thrust
distribution" are insufficient. Write: "Corrected normalized thrust
distribution (1/N) dN/dτ compared to Pythia 6.4 (Lund string, tune X).
Error bars show statistical uncertainties; the shaded band shows the total
systematic uncertainty. The ratio panel shows data/MC."

- **Data/MC comparisons:** overlaid distributions with ratio panels
- **Cutflows:** tables with per-cut yields, efficiencies, and S/B ratios
- **Selection cuts:** each cut accompanied by the distribution that motivates
  it, showing where signal and background separate
- **Background estimates:** yield tables with stat + syst uncertainties per
  region
- **Fit results:** post-fit pull distributions, impact ranking plots,
  correlation matrices, GoF summaries
- **Limits/measurements:** Brazil band plots, observed vs expected comparisons

Figures are referenced using markdown image syntax with **detailed,
self-contained captions**:

```markdown
![Corrected normalized thrust distribution $(1/N)\,dN/d\tau$ compared to
Pythia 6.1 particle-level prediction. Error bars show statistical
uncertainties; the shaded band shows the total systematic uncertainty.
The ratio panel shows data divided by MC. The data is systematically
below the MC in the fit range $0.05 \leq \tau \leq 0.30$, reflecting the
known tendency of the Pythia 6.1 LEP tune to overpredict soft hadronic
activity.](figures/final_result_with_unc.pdf)
```

**Caption requirements:**
- State what is plotted (observable, axes, units)
- Identify all curves/markers/bands in the figure
- State the key conclusion the reader should draw
- A reader should understand the figure from the caption alone, without
  reading the surrounding text
- Sparse captions like "Thrust distribution" or "Data/MC comparison" are
  Category A review findings

**Figure numbering and cross-referencing:** Pandoc automatically numbers
figures in `\begin{figure}` environments when compiling to PDF. The
markdown text body must reference figures by description (e.g., "as shown
in the thrust distribution comparison (Figure X)") so that the compiled
PDF has proper cross-references. In intermediate markdown artifacts, use
descriptive references: "see the response matrix figure below."

### Figure standards:

All figures must follow the template and rules in **Appendix D (Plotting
Template)**. That appendix is the single source of truth for figure sizing,
styling, labels, and save conventions. Key non-negotiables:

- **No titles on figures** — captions in the note replace `ax.set_title()`
- **Axis labels with units** in brackets, e.g. `$p_T$ [GeV]`
- **mplhep styling** with explicit experiment labels via `mh.label.exp_label`
- **Wrong metadata** (√s, experiment name, luminosity) is a **Category A**
  review finding
- **PDF + PNG** output, `bbox_inches="tight"`, `dpi=200`, `transparent=True`

The artifact + its `figures/` directory must be self-contained — a reader
should be able to evaluate the analysis from these alone.

### Supplementary artifacts:

Phases also produce data files, figures, and scripts in phase-specific
subdirectories. Scripts are referenced from the artifact's code reference
section for reproducibility.

**Intermediate data files** (`.npz`, `.json`, pyhf workspaces, trained
models) must include a brief README or docstring in the artifact explaining:
what the file contains, how to load it (e.g., `np.load("results.npz")`
with key names listed), and which pixi task produced it. A human or
downstream agent encountering `results_phase3.npz` should know what's
inside without reading the script that produced it.

Additionally, any phase may produce these supplementary artifact types:

- **`UPSTREAM_FEEDBACK.md`** — produced by an executor that discovers something
  an earlier phase did not consider (e.g., an unexpected background shape, a
  missing systematic). Non-blocking: the executor continues its own work. The
  orchestrator routes the feedback to the next review gate for the upstream
  phase. See Section 6.8 for the full mechanism.
- **`REGRESSION_TICKET.md`** — produced by the Investigator role when a
  regression trigger is confirmed. Contains root cause, affected phases,
  unaffected phases, and fix scope. See Section 6.8.

---
