## Appendix C: Tool Heuristics (Agent-Maintained)

This appendix is a living document. On first encounter with a tool, the agent
queries the tool's current documentation, extracts best practices and common
pitfalls, and records a concise summary here. Subsequent agents (or sessions)
consult this appendix first and only re-query upstream docs if something is
out of date or missing.

**Purpose:** Avoid repeated full-doc lookups. Each entry captures what the agent
learned so the next session starts with working knowledge rather than reading
the full API surface from scratch. This is analogous to the blessed snippets
library but for tool-level idioms and gotchas.

**Format:** One subsection per tool. Each entry should include:
- Version tested against
- Key idioms and recommended patterns
- Common pitfalls and how to avoid them
- Performance notes if relevant

**Maintenance rules:**
- The agent **must** check this appendix before querying external docs for any
  tool listed in Section 7.1.
- If an entry exists and is sufficient, use it — do not re-query.
- If an entry is missing or incomplete, query the current docs and use the
  result. **Do not modify this file during analysis execution** — it lives
  in the spec directory. Instead, note the missing/outdated entry in the
  experiment log. Updates to this appendix happen after the analysis completes,
  following the same process as `conventions/` updates.
- Keep entries concise — heuristics and gotchas, not full API references.

<!-- Agent: populate entries below as you encounter each tool. -->

### mplhep

**Version:** 0.3.x+

**Key idioms:**
- Use `mplhep.style.use("CMS")` for the default style sheet. This sets fonts,
  tick sizes, and figure aesthetics. It does NOT add experiment labels.
- Experiment labels are added via `mplhep.label.exp_label(...)` — the generic
  function that works for any experiment. See Appendix D for the full template
  and parameter reference (`exp`, `text`, `llabel`, `rlabel`, `data`, `com`,
  `lumi`, etc.).
- **Do NOT** hack around unwanted label text by patching rcParams or removing
  matplotlib text objects after the fact. The `exp_label` function exposes all
  the controls you need as kwargs. Read `help(mplhep.label.exp_label)`.
- For ALEPH analyses using CMS style: call
  `mplhep.label.exp_label(exp='ALEPH', data=True, rlabel=r'$\sqrt{s} = 91.2$ GeV')`
  to get clean labeling without CMS branding.

**Common pitfalls:**
- Using experiment-specific functions (e.g., `mplhep.cms.label`) instead of
  the generic `mplhep.label.exp_label`. The generic function works for any
  experiment; experiment-specific functions add unwanted branding.
- Forgetting `rlabel=''` and getting a default "(13 TeV)" watermark from CMS
  style. Always set `rlabel` explicitly.
- When `data=False`, mplhep auto-adds "Simulation" as text. Setting `llabel`
  on top of this causes stacking. Either use `data=False` alone, or set
  `data=True, llabel="MC Simulation"` to fully control the left side.

**Performance:** No concerns — plotting is never the bottleneck.
