# Logic Review: Phase 3 (Causal Analysis)

## Review Summary
- **Phase**: 3 -- Causal Analysis
- **Artifact reviewed**: `phase3_analysis/exec/ANALYSIS.md`
- **Upstream reference**: `phase1_strategy/exec/STRATEGY.md`
- **Date**: 2026-03-29
- **Verdict**: ITERATE
- **Category A issues**: 3
- **Category B issues**: 6
- **Category C issues**: 4

---

## Category A (Blocking)

**A-1: Refutation tests for DE-->IND_UP run on wrong specification**

The mediation first link (DE-->IND_UP) achieves strong significance with demographic control (W=15.81, p_boot=0.008) but refutation tests were run only on the bivariate specification (W=4.75, p=0.132). The note states: "The controlled specification was not separately refuted because it requires trivariate refutation testing which would reduce effective sample size further."

Per the Phase 3 CLAUDE.md non-negotiable rule 1: "Every causal claim must survive the refutation battery." Drawing inference from a specification that has not been refuted is a protocol violation.

**Fix**: Run the 3-test refutation battery on the controlled (trivariate) specification for DE-->IND_UP. If effective sample is too small for reliable refutation, document explicitly and cap edge at CORRELATION regardless of pass count.

**A-2: Relevance not reduced to 0.1 for zero-effect creation channel**

The EP update rules (Step 3.4) state: "Effect near zero: relevance drops to 0.1." The creation channel found no Granger signal at any significance level (p=0.565 bivariate, p=0.834 with control), no cointegration, and the effect estimate is not distinguishable from zero. Yet relevance was set to 0.40 (down from 0.60), not 0.10 as the rule requires.

With correct relevance (0.1), EP = 0.30 x 0.1 = 0.03, below hard truncation (0.05). This would reclassify the creation channel as "beyond analytical horizon" rather than "lightweight assessment." The downstream Joint_EP for DE-->IND_UP-->CRE would also change. Current EP of 0.120 overstates the evidence.

**Fix**: Set DE-->CRE relevance to 0.1, recompute EP to 0.03, mark as below hard truncation.

**A-3: DID coefficient values inconsistent between Sections 2.4 and 6.4**

Section 2.4 reports substitution beta_1 = 21.00 (SE=10.48, p=0.063), beta_2 = -12.53 (SE=14.84, p=0.412). Section 6.4 reports beta_1 = 20.51 (SE=16.33, p=0.209), beta_2 = -5.90 (SE=8.04 implied). The creation channel beta_2 reverses sign between sections (+17.67 in 2.4, -10.38 in 6.4). Two different sections report materially different regression coefficients for what appears to be the same specification.

**Fix**: Trace both sets back to generating scripts. Reconcile or explicitly label different specifications.

---

## Category B (Important)

**B-1: DEMO-->LS relevance reduction not fully justified**

DEMO-->LS found no Granger causality (W=1.93, p=0.397 for services; W=0.75, p=0.694 for industry). Per the "Effect near zero" rule, relevance should drop to 0.1 (giving EP = 0.03). Instead, relevance was set to 0.40. Either apply the mechanical rule or explicitly justify why the mechanical rule is overridden for confounders.

**B-2: Specification selection for DE-->SUB may involve implicit data snooping**

The controlled specification achieves CORRELATION (2/3 PASS, p=0.012) while bivariate only HYPOTHESIZED (1/3 PASS, p=0.087). Add a sentence noting the controlled specification was pre-committed in STRATEGY.md per DAG structure (DEMO is mandatory confounder).

**B-3: Out-of-sample validation not reported**

STRATEGY.md planned train-on-2000-2019 / test-on-2020-2023 split. Not reported in ANALYSIS.md. Report honestly even if COVID disrupts.

**B-4: No IV or endogeneity correction attempted**

All three reference analyses use GMM/IV. Add discussion of why IV was not feasible (no valid external instrument, T=24 insufficient for first-stage power).

**B-5: No nonlinearity test despite reference analysis finding inverted-U**

Zhao and Li (2022) find inverted-U. The quadratic sensitivity shows extreme shift (~95 pp) but is dismissed. Test piecewise-linear at DE median instead.

**B-6: Negative mediation share not adequately investigated**

VAR mediation yields -90% to -95%, contradicting all references. Test alternative Cholesky orderings and generalized impulse responses (Pesaran-Shin).

---

## Category C (Minor)

**C-1**: Figure paths from exec/ may not resolve during compilation.
**C-2**: Unnumbered "Warnings Carried Forward" section breaks numbering flow.
**C-3**: EP propagation figure color bands could be dashed threshold lines.
**C-4**: Uncertainty tornado aspect ratio compressed; functional form bar dominates.

---

## EP Propagation Audit

All EP arithmetic verified correct. Joint_EP chain computations accurate. Issue is input values (relevance for DE-->CRE), not arithmetic.

| Edge | Phase 1 EP | Phase 3 EP | Change | Consistent? |
|------|:---------:|:---------:|:------:|:-----------:|
| DE-->SUB | 0.32 | 0.315 | -0.005 | Yes |
| DE-->CRE | 0.27 | 0.120 | -0.150 | Yes direction, value disputed (A-2) |
| DE-->IND_UP | 0.23 | 0.090 | -0.140 | Yes |
| DEMO-->LS | 0.36 | 0.120 | -0.240 | Yes |
| DE-->LS | 0.06 | 0.010 | -0.050 | Yes |

No regressions detected. All changes in expected direction given empirical results.

### Sign Consistency Across Methods

The POSITIVE sign on DE-->industry employment is consistent across: Granger (positive in first differences), ARDL (+7.15 bivariate, +12.57 with controls), VECM (short-run gamma = +25.86), and DID beta_1 (+20.51). This consistency strengthens the "complement" interpretation.

### Circular Reasoning Check

No circular dependencies detected. The controlled specification selection for DE-->SUB is DAG-driven (B-2), not data-driven.

---

## Reference Analysis Comparison

Gaps relative to competing analyses:
1. No endogeneity correction (all references use GMM/IV)
2. No nonlinearity test (Zhao & Li find inverted-U)
3. No heterogeneity analysis (impossible with national time series)
4. Negative mediation share (-90%) contradicts Li et al.'s +22%
