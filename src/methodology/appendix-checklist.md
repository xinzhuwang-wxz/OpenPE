## Appendix B: Minimal Artifact Checklist

### Per-phase artifacts

| Phase | Artifact file | Must contain |
|-------|---------------|-------------|
| Phase 0: Discovery | `DISCOVERY.md` + `DATA_QUALITY.md` | Question decomposition, causal DAG, data sources, quality verdicts |
| Phase 1: Strategy | `STRATEGY.md` | Method selection, EP assessment, chain plan, systematic inventory |
| Phase 2: Exploration | `EXPLORATION.md` | Data summary, quality pre-screen, variable ranking by EP |
| Phase 3: Analysis | `ANALYSIS.md` | Causal test results, EP propagation, statistical model, uncertainties |
| Phase 4: Projection | `PROJECTION.md` | Scenarios, sensitivity ranking, endgame classification, EP decay chart |
| Phase 5: Verification | `VERIFICATION.md` | Independent reproduction, provenance audit, logic audit, EP verification |
| Phase 6: Documentation | `REPORT.md` + `audit_trail/` | Complete report, EP decay visualization, machine-readable audit trail |

### Report completeness checklist

The Phase 6 report must satisfy ALL of these. Each is a Category A
review finding if absent:

- [ ] LaTeX math delimiters used throughout (`$...$`, not plain text)
- [ ] Every causal claim labeled: DATA_SUPPORTED / CORRELATION / HYPOTHESIZED
- [ ] Every numerical estimate has confidence interval
- [ ] EP decay chart showing confidence bands widening with projection distance
- [ ] Data provenance table with URL, retrieval date, and SHA-256 for each dataset
- [ ] Refutation test results for every tested causal edge
- [ ] Machine-readable `audit_trail/` with claims.yaml and methodology.yaml
- [ ] `pixi.toml` has an `all` task reproducing the full chain
- [ ] Experiment log is non-empty
- [ ] All intermediate phase artifacts exist on disk

### Experiment log minimum content

The experiment log must contain entries for at least:
- [ ] Data discovery (sources found, quality assessment, gaps identified)
- [ ] Key parameter choices and their reasoning
- [ ] Failed approaches and why they were abandoned
- [ ] Any bugs encountered and how they were resolved

---
