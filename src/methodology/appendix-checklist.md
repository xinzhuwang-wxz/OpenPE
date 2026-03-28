## Appendix B: Minimal Artifact Checklist

### Per-phase artifacts

| Phase | Artifact file | Must contain |
|-------|---------------|-------------|
| Strategy | `STRATEGY.md` | Signal/background enumeration, selection approach, blinding plan, systematics categories, literature citations, reference analysis systematic table |
| Exploration | `EXPLORATION.md` | Sample inventory, data quality assessment, variable ranking, preselection cutflow, data/MC comparisons |
| Processing | `SELECTION.md` | Selection definition, region definitions, background estimates, closure tests, per-cut distributions |
| 4a: Expected | `INFERENCE_EXPECTED.md` | Systematic table with per-source detail, fit model or correction procedure, expected results, validation tests, systematic completeness table vs references, covariance matrix |
| 4b: 10% validation | `INFERENCE_PARTIAL.md` + `ANALYSIS_NOTE_DRAFT.md` | 10% observed results, post-fit diagnostics, GoF, draft analysis note with full structure |
| 4c: Full data | `INFERENCE_OBSERVED.md` | Full observed results, post-fit diagnostics, anomaly assessment, comparison to expected |
| Documentation | `ANALYSIS_NOTE.md` + `results/` | Complete analysis note with all sections, figures, LaTeX math, machine-readable results |

### Analysis note completeness checklist

The Phase 5 analysis note must satisfy ALL of these. Each is a Category A
review finding if absent:

- [ ] LaTeX math delimiters used throughout (`$...$`, not plain text)
- [ ] One subsection per systematic source (not just a summary table)
- [ ] One subsection per cross-check (not just a mention)
- [ ] Per-cut event selection with individual cut distributions and efficiencies
- [ ] Full covariance matrix (statistical + systematic) in appendix
- [ ] Machine-readable `results/` directory with spectrum, covariance, parameters
- [ ] Comparison to published data with quantitative metric (not just "consistent")
- [ ] `pixi.toml` has an `all` task reproducing the full chain
- [ ] Experiment log is non-empty
- [ ] All intermediate phase artifacts exist on disk

### Experiment log minimum content

The experiment log must contain entries for at least:
- [ ] Data format discovery (branches, trees, event counts)
- [ ] Key parameter choices and their reasoning
- [ ] Failed approaches and why they were abandoned
- [ ] Any bugs encountered and how they were resolved

---
