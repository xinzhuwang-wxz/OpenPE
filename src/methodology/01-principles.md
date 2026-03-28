# LLM-Driven Analysis Methodology

## 1. Scope and Principles

This document specifies a methodology for conducting a complete data-driven analysis using LLM-based agents. The specification is
intentionally minimal: it defines *what* must happen and *what* each phase must
produce, not *how* the agent should implement it. The agent selects tools,
writes code, and makes physics judgments within the constraints described here.

**Quality bar: publication-ready.** The standard for every phase is: would
a senior physicist on a collaboration review committee approve this? Not
"is it good enough to move on" but "is it good enough to publish." This
means: every systematic evaluated, every cross-check quantitative, every
plot physically sensible, every claim supported by evidence. Agents must
not rationalize shortcuts, accept weak closures, or paper over data/MC
disagreements. When something is wrong, go back and fix it — do not
document it as a "known limitation" and move on.

**Design principles:**

- **Prose over code.** The methodology is expressed in natural language. No
  bespoke library is required — agents use standard, community-maintained analysis
  software directly.
- **Artifacts over memory.** Each phase produces a self-contained written
  report. Subsequent phases read these reports, not prior conversation history.
  This bounds context consumption and makes the analysis auditable.
- **Review at every level.** Plans are reviewed before execution. Code is
  reviewed before results are trusted. Results are reviewed before they are
  written up. The final writeup is reviewed before the analysis is considered
  complete. Review artifacts are first-class outputs.
- **The agent adapts to the analysis.** Not every analysis needs multivariate
  techniques, multiple signal regions, or data-driven background estimates. The
  agent evaluates what is appropriate and documents its reasoning. Omitting an
  unnecessary step is correct; performing it without justification is not.
- **No encoded physics — but accumulated conventions.** This specification
  describes methodology, not physics. The agent derives its physics approach
  from the literature (via retrieval from the experiment's publication corpus)
  and first principles. However, operational knowledge about specific analysis
  techniques (e.g., standard systematic sources for unfolded measurements,
  required validation checks for template fits) is maintained in the
  `conventions/` directory. These are living documents updated after each
  analysis — empirically grounded, not speculative. The agent consults
  applicable conventions during strategy (Phase 1) and systematics (Phase 4a),
  and updates them with new knowledge gained during the analysis.
- **Downscope, don't block.** When a resource is unavailable (missing MC,
  insufficient statistics, inaccessible data, no GPU for large training),
  the agent downscopes to what is achievable now and documents what would
  improve the result with more resources. A complete analysis with a simpler
  method beats an incomplete analysis waiting for the ideal method. This is
  standard scientific practice — see Section 12.

