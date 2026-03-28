# Phase 3: Processing

> Read `methodology/03-phases.md` → "Phase 3" for full requirements.
> Read `methodology/appendix-plotting.md` for figure standards.

You are implementing the analysis approach defined in the Phase 1 strategy
for a **{{analysis_type}}** analysis. Read the strategy first — it determines
what this phase must deliver.

**Start in plan mode.** Before writing any code, produce a plan: what scripts
you will write, what selection you will implement, what figures you will
produce, what the artifact structure will be. Execute after the plan is set.

## Output artifact

`exec/SELECTION.md` — final object definitions, event selection with
optimization, cutflow table, and technique-specific deliverables.

## Methodology references

- Phase requirements: `methodology/03-phases.md` → Phase 3
- Technique-specific requirements: `methodology/03-phases.md` → Phase 3 "Correction infrastructure" / "Background estimation" subsections
- Review protocol: `methodology/06-review.md` → §6.2 (1-bot), §6.4
- Plotting: `methodology/appendix-plotting.md`
- Coding: `methodology/11-coding.md`

## RAG queries (mandatory)

Query the experiment corpus for:
1. Published selection criteria for similar analyses
2. Known correction factors or efficiency maps
3. Background estimation techniques used in reference analyses

Cite sources in the artifact.

## MVA classification checklist

Default to multivariate techniques (BDT, NN) for multi-dimensional
classification. See `methodology/03-phases.md` → Phase 3 "Selection" for
full guidance including when to use cuts vs. MVA.

- [ ] Sub-delegate MVA training to a sub-agent (see §3a.5.1)
- [ ] Train primary classifier (BDT or NN)
- [ ] Train ≥1 alternative architecture (NN if BDT, vice versa)
- [ ] Try multiclass if >2 physics classes (e.g., b/c/light)
- [ ] Produce validation plots: ROC, score distributions (train/test overlaid), feature importance
- [ ] Check data/MC agreement on classifier output — investigate before accepting systematic
- [ ] Optimize working point with figure of merit
- [ ] Save trained model, hyperparameters, split seed, validation plots as artifacts

## Sensitivity optimization (when initial selection is insufficient)

If the initial selection does not meet the physics goal, systematically
explore alternatives. Maintain a **sensitivity log** (`sensitivity_log.md`)
tracking each approach, figure of merit, and limiting factor.

Progress through qualitatively different strategies (not just parameter
tuning). Not all apply to every analysis type — select those relevant:
1. Optimize the current approach (tune cuts for S/sqrt(B) or equivalent)
2. Try a more powerful discriminant (cut-based → BDT → GNN)
3. Try different inference strategies (shape fit vs. counting, different
   discriminant variables) — primarily for searches and template fits
4. Revisit region design (tighter SR, different background decomposition,
   alternative efficiency binning)

**Stop when:** sensitivity meets the goal, OR 3+ materially different
approaches tried AND marginal improvement (<10% relative). Document all
attempts — "we tried X, Y, Z; Y performed best because [reason]" is a
valid conclusion. See `methodology/03-phases.md` → Phase 3 for full details.

## Review

**1-bot review** — see `methodology/06-review.md` for protocol.
Write findings to `review/REVIEW_NOTES.md`.
