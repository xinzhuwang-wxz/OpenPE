## 12. Scope Management and Downscoping

This section details the "downscope, don't block" principle from Section 1.
When a resource is unavailable, the agent downscopes to what is achievable
and documents the limitation — in the experiment log during execution, and
in the final analysis note for the record.

### 12.1 When to Downscope

- **Data or MC is unavailable** (inaccessible, corrupt, doesn't exist)
- **MC statistics are insufficient** for the intended method
- **Compute exceeds what's available** (e.g., multi-GPU training infeasible)
- **External inputs are missing** (calibrations, efficiency maps)
- **The method is disproportionate to the gain** (GNN for 5% improvement
  when a BDT gets 90% of the way)

### 12.2 How to Downscope

1. **Document the constraint** in the experiment log: what is unavailable,
   why, and what it prevents.
2. **Choose the best achievable method.** Fall back along the complexity
   ladder (GNN → BDT → cut-based), or reduce scope (fewer channels, fewer
   systematics, simpler background model).
3. **Quantify the impact.** Estimate what the missing resource would have
   contributed, using literature or cross-section ratios where possible.
4. **Carry it through to the analysis note.** Every downscoping decision
   must appear in the final AN: in the relevant method section (explaining
   what was done instead and why), in the systematic uncertainty table (as
   a literature-derived entry or documented omission), and in the Future
   Directions section (as a concrete improvement for follow-up work). A
   limitation that exists only in the experiment log has not been properly
   documented.

### 12.3 Key Scenarios

**Missing MC samples.** Omit if the process is small, or estimate its
contribution from theory (cross-section × efficiency from a similar process).

**Insufficient MC statistics.** Coarser binning, merged regions, or
cut-and-count instead of shape fit. Include MC stat uncertainty as a
systematic (simplified uncertainty parameterization).

**Systematic sources that cannot be evaluated from own data/MC.** The agent
must **not leave it as zero** — zero is never valid for a known non-zero
effect. Instead: search the literature (via RAG) for the same or analogous
measurement, adopt a conservative estimate, inflate if the phase space
differs, and mark the systematic as "literature-derived" with a citation.
Example: "Hadronization uncertainty estimated as 2% based on Pythia vs.
Herwig variation in [published analysis]; conservative for our phase space."

**Missing external measurements.** Use the best available literature value
with a conservative uncertainty. Cite the source.

### 12.4 Downscoping and Review

Reviewers evaluate downscoping on two axes:
1. **Is the chosen method adequate for the physics goal?** A reviewer should
   NOT flag "you could have used a more complex method" as Category A unless
   the simpler method is demonstrably inadequate.
2. **Is the limitation properly documented?** The analysis note must
   acknowledge what was not done, why, and the estimated impact.

### 12.5 Redirect, Don't Stop

A blocked resource is a redirect signal, not a stop signal. When one path
is blocked, the agent seeks parallel work that remains unblocked:

- **Measure everything the data supports.** If MC blocks unfolding, measure
  detector-level distributions for every relevant observable.
- **Cross-check exhaustively.** Year-by-year stability, subdetector
  comparisons, alternative selections — these validate the measurement and
  often surface issues visible only from multiple angles.
- **Consult the literature.** Published correction factors, efficiency maps,
  and previous measurements can substitute for missing MC. The RAG corpus
  exists for this.

**Anti-pattern:** "MC unavailable → unfolding blocked → stop." Correct:
"MC unavailable → measure everything else, extract maximum physics from
detector-level data → document what unfolding will add when MC arrives."

### 12.6 Feasibility for LLM Agents

When evaluating feasibility, the question is "can an LLM agent do this?" —
not "would a human find this easy?" LLM agents have different strengths and
limitations than human analysts:

**Agents are good at:** Systematic, repetitive processing (evaluating 20
systematic sources one by one), following documented procedures, producing
complete artifacts, checking completeness against checklists, querying
literature corpora.

**Agents struggle with:** Tasks requiring persistent state across many
sessions, visual inspection of plots, novel physics reasoning not grounded
in training data or retrieved literature, tasks requiring interactive tools
(GUIs, interactive fitting).

**Agents CAN:**
- Compile and run Fortran code (e.g., EVENT2, NNLO programs)
- Install packages via `pixi add` — if conda-forge has it (`pixi search <pkg>`),
  the agent can use it
- Build external physics codes (EVENT2, MCFM, etc.) from source if the code is
  accessible and build instructions exist
- Dependencies like Fortran compilers (`gfortran`) are available via conda-forge

The question is whether a procedural path exists in documentation, not whether
the task is "hard" for a human.

When a task falls in the "agents struggle" category, the agent should:
1. Attempt it if it affects the core result and a procedural path exists
2. Document the limitation clearly if it cannot be resolved
3. Flag it for human review at the next gate

### 12.7 Future Directions

The Phase 5 analysis note must include a **Future Directions** section that
collects all downscoping decisions into a concrete roadmap: what was
descoped, what resources are needed, what improvement is expected
(quantitative where possible), and rough priority ordering.

---
