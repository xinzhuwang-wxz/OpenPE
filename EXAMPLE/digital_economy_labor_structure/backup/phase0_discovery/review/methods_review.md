# Methods Review: Phase 0 Discovery

## Review Summary
- **Phase**: Phase 0 (Discovery)
- **Artifacts reviewed**: `phase0_discovery/exec/DISCOVERY.md`, `phase0_discovery/exec/DATA_QUALITY.md`, `data/registry.yaml`, `experiment_log.md`
- **Date**: 2026-03-29
- **Category A issues**: 1
- **Category B issues**: 5
- **Category C issues**: 3
- **Positive markers**: 6

## What Works Well

[+] **Three genuinely competing DAGs.** The DAGs represent structurally distinct causal hypotheses -- direct technology channels (DAG 1), institutional mediation (DAG 2), and labor market segmentation (DAG 3). These are not minor variations; each generates meaningfully different testable predictions and kill conditions. This is exactly what competing DAGs should look like.

[+] **Honest data quality assessment.** The DATA_QUALITY.md document is unusually candid about what the data can and cannot support. The explicit "PROCEED WITH WARNINGS" verdict, the binding constraints documented for all downstream phases, and the EP truth caps for edges lacking adequate data (capped at 0.30) are well-calibrated and prevent downstream analysts from over-claiming.

[+] **Smart city pilot panel construction.** The staggered treatment indicator across 286 cities and 3 batches is cleanly structured for a DID design. The cross-validation against published DID studies and the decision to exclude district/county/town-level units for cleaner identification is methodologically sound.

[+] **Kill conditions are falsifiable.** Each DAG has a clearly stated kill condition that would disconfirm the hypothesis. DAG 1 fails if mid-skill employment increases in pilot cities; DAG 2 fails if the direct effect remains large after mediator controls; DAG 3 fails if formal and informal sectors respond in the same direction. These are concrete and testable.

[+] **EP framework applied consistently.** The EP = truth x relevance formula is applied uniformly across all edge tables, with truth values calibrated to the LITERATURE_SUPPORTED / THEORIZED / SPECULATIVE taxonomy. The edge tables are complete and internally consistent.

[+] **Experiment log is thorough.** Every material decision -- from EPS identification to batch timing conventions to index construction choices -- is documented with rationale. The log explicitly records failed data sources and their implications.

## Suggested Improvements

### Category A (Blocking)

1. **[A1]: Granger causality requires >=30 observations per the time series conventions; the available data has only 24.**

   - Current state: DATA_QUALITY.md acknowledges 24 observations is "short for time series econometrics" and recommends parsimony (4-5 regressors). The experiment log notes bivariate Granger tests and possibly trivariate VAR(1) are feasible. However, the time series conventions file (`conventions/time_series.md`) explicitly states: "Granger causality requires sufficient time series length (>=30 observations)."
   - Suggested improvement: DISCOVERY.md and DATA_QUALITY.md must explicitly acknowledge that the primary fallback identification strategy (Granger causality) violates the project's own conventions threshold of 30 observations. The downstream strategy must either (a) justify why 24 observations is acceptable for the specific tests planned (with citations to small-sample Granger test literature, e.g., Toda-Yamamoto procedure), (b) identify alternative identification strategies that work with T=24 (e.g., structural break tests using known policy dates, cointegration-based VECM with known cointegrating relationships), or (c) trigger a data callback to obtain quarterly or monthly sub-indicators that would increase T.
   - Why it matters: If Phase 1 builds its entire strategy around Granger causality with T=24, and Phase 3 reviewers flag the conventions violation, it forces a regression back to Phase 0/1. Flagging this now prevents that regression.
   - Effort: Low (documentation clarification and strategy note; no new data needed).

### Category B (Important)

2. **[B1]: The DID-to-time-series downscoping lacks a formal feasibility evaluation.**

   - Current state: DATA_QUALITY.md correctly identifies that DID is not executable and the analysis must fall back to "weaker identification strategies (time series, structural breaks, Granger causality)." The experiment log records this as a constraint. But there is no structured assessment of what causal claims these weaker methods can actually support, nor how the EP framework should be adjusted.
   - Suggested improvement: Add a "Feasibility Evaluation" section to DATA_QUALITY.md (or as an addendum) that maps the original research question's causal claims to the achievable identification strength with T=24 national time series. Specifically: (a) which DAG edges can be tested with time series methods and at what confidence level, (b) which DAG edges become untestable and should be flagged as "beyond current data," (c) what the maximum achievable EP.truth is for time-series-only identification (typically lower than DID). The methodology spec references `methodology/09-downscoping.md` for this purpose.
   - Why it matters: Without this mapping, Phase 1 may attempt to test edges that the data fundamentally cannot support, leading to wasted effort or misleading results. The downscoping protocol exists precisely for this situation.
   - Effort: Medium (requires systematic mapping of edges to methods).

3. **[B2]: The digital economy composite index lacks sensitivity analysis guidance for downstream phases.**

   - Current state: DATA_QUALITY.md rates the index bias as LOW (45/100) and notes it "measures ICT infrastructure penetration, not the broader digital economy construct." The experiment log documents that 2 of 6 intended components failed to fetch. The construct validity concern is well-articulated.
   - Suggested improvement: DISCOVERY.md should specify that Phase 2 EDA must include a construct validity check: correlate the composite index against known digital economy milestones (Internet Plus 2015, COVID acceleration 2020, tech sector crackdown 2021) and report whether inflection points align. Additionally, Phase 3 should run sensitivity analysis using individual components (internet penetration alone, broadband alone, R&D alone) as alternative treatment measures. If results are qualitatively different across component choices, the composite index findings should be downgraded. This guidance should be explicit in the data requirements or open issues section, not left for Phase 1 to discover.
   - Why it matters: Equal-weight composites can mask the fact that one component drives all the variation. If broadband penetration drives the index and the other components are noise, the causal interpretation changes substantially. Documenting the sensitivity requirement now ensures Phase 3 does not skip it.
   - Effort: Low (documentation; the actual sensitivity runs happen in Phase 2-3).

4. **[B3]: Mediation analysis design (DAG 2) needs stronger specification of statistical approach.**

   - Current state: DISCOVERY.md states DAG 2's testable prediction is that "mediation analysis shows that human capital investment and industrial upgrading account for >60% of the total effect" and mentions "Sobel/bootstrap mediation test." The experiment log notes this as the key test for DAG 2 vs DAG 1 discrimination.
   - Suggested improvement: The >60% threshold is stated without justification. Phase 0 should note that: (a) the Sobel test assumes normally distributed indirect effects and performs poorly in small samples (T=24 is small); the bootstrap mediation test (Preacher and Hayes, 2008) is strongly preferred and should be specified as the primary method; (b) the 60% threshold should be derived from published mediation studies in the digital economy literature, or explicitly labeled as an analyst's prior that will be refined in Phase 1; (c) with T=24, the power to detect mediation is very low -- a power analysis or minimum detectable effect size should be estimated before committing to this test. The causal inference conventions require that "every causal claim must survive at least 3 refutation tests" -- mediation claims are causal claims and should be held to the same standard.
   - Why it matters: Mediation analysis with 24 observations is statistically fragile. If Phase 3 runs the test and gets wide confidence intervals, the DAG 2 vs DAG 1 discrimination becomes uninformative. Setting realistic expectations now prevents over-interpretation later.
   - Effort: Medium (requires literature review for threshold justification and power calculation).

5. **[B4]: SUTVA violation concern for smart city DID is identified but no mitigation strategy is specified.**

   - Current state: DISCOVERY.md lists SUTVA violation as open issue #7: "Smart city pilots may generate digital economy spillovers to neighboring non-pilot cities." The experiment log also flags spatial spillovers. Two potential mitigations are mentioned in passing -- "spatial DID" and "buffer-zone exclusion" -- but no detail is provided.
   - Suggested improvement: Since DID is currently blocked by missing outcome data, the SUTVA concern is not immediately operational. However, if a data callback acquires city-level outcomes, the mitigation strategy must be pre-specified to avoid post-hoc specification search. DISCOVERY.md should specify: (a) buffer-zone exclusion radius (e.g., exclude cities within 100km of pilot cities from the control group, per common practice in Chinese DID studies); (b) which spatial DID approach to use if spillovers are detected (spatial Durbin DID is standard); (c) a spillover falsification test (check whether outcomes in cities neighboring pilots change post-treatment). This does not need to be detailed code, but the methodological choices should be documented now so that a data callback can proceed without re-opening DAG design.
   - Why it matters: If a data callback is triggered and city-level data becomes available, the analysis will need to implement DID quickly. Pre-specifying the SUTVA mitigation avoids ad-hoc choices under time pressure.
   - Effort: Low (documentation of pre-specified choices).

6. **[B5]: Refutation test design for time series fallback methods is not specified.**

   - Current state: The causal inference conventions require "at least 3 refutation tests (placebo, random common cause, data subset)" for every causal claim. DISCOVERY.md designs refutation tests implicitly for the DID framework (parallel trends is mentioned). But since DID is blocked and the analysis will use time series methods, the refutation tests need to be re-designed for the actual methods that will be used.
   - Suggested improvement: Add a section to DISCOVERY.md or DATA_QUALITY.md that outlines how the three required refutation tests translate to the time series context: (a) **Placebo treatment test:** Use a variable known to be unrelated to digital economy (e.g., agricultural commodity prices) as a pseudo-treatment in the Granger causality framework; if it "Granger-causes" employment structure changes, the method has a false positive problem. (b) **Random common cause test:** Add random noise variables to the VAR/Granger specification and check whether results are robust. (c) **Data subset test:** Split the time series at a meaningful break point (e.g., pre-2015 vs post-2015, or pre-COVID vs full sample) and check whether the relationship holds in both subsets. These translations are not trivial -- the DoWhy refutation tests are designed for cross-sectional/panel data, and their time series equivalents require explicit design.
   - Why it matters: If Phase 3 applies DoWhy's standard refutation tests to time series data without adaptation, the tests may be meaningless or misleading. Pre-specifying the time series refutation design ensures the conventions are met substantively, not just formally.
   - Effort: Medium (requires methodological design work).

### Category C (Minor)

7. **[C1]: EP values for definitional edges (e.g., MID_DECLINE --> LS, HIGH_GROW --> LS) should be 1.0 or flagged as non-empirical.**

   - Suggested improvement: Edges like "Mid-skill employment decline --> Labor structure change" and "High-skill employment growth --> Labor structure change" are definitional (labor structure change is by definition the sum of its skill-level components). These edges have EP = 0.35 in the edge table, which implies epistemic uncertainty where none exists. Either set their truth to 1.0 (making EP = 0.5 or 0.7 depending on relevance) or flag them as "DEFINITIONAL -- not subject to empirical testing" to avoid confusion in Phase 3 when the analyst decides which edges to test.
   - Effort: Low.

8. **[C2]: The smart city pilot panel shows `treated` and `post` columns as identical, which is noted but could cause downstream confusion.**

   - Suggested improvement: DATA_QUALITY.md correctly notes this is expected for a pilot-only panel. However, the column naming is misleading -- in standard DID notation, `treated` indicates group assignment (time-invariant) and `post` indicates the post-treatment period (time-varying). Since this panel contains only treated cities, the `treated` column is always 1 and `post` is the operative indicator. Rename `treated` to `is_pilot` (always 1) or drop it entirely, and keep only `post` as the treatment timing indicator. This prevents a downstream analyst from mistakenly constructing `treated * post` interactions (which would be identical to `post` alone).
   - Effort: Low.

9. **[C3]: The edge table for DAG 3 labels hukou and SOE reform as "Moderators" rather than confounders.**

   - Suggested improvement: In the DAG 3 mermaid diagram, HUKOU and SOE are drawn with dotted arrows labeled "Moderator." Moderators are interaction effects in regression, not separate nodes in a DAG. If these variables modify the strength of the DE --> FORMAL or REALLOC paths, they should be represented as interaction terms in the estimation strategy, not as separate DAG nodes. The mermaid diagram should either represent them as confounders (if they affect both treatment and outcome) or remove them from the DAG and note them as heterogeneity dimensions for subgroup analysis. This is a notation issue that could confuse the Phase 3 analyst about whether to condition on these variables or interact them.
   - Effort: Low.

## Method Appropriateness Assessment

**Causal inference method selection:** The original DID design using smart city pilots is well-chosen for this research question. Staggered DID with three treatment batches is the standard approach in the Chinese digital economy literature, and the pilot selection provides plausibly exogenous variation in digital economy exposure. The decision to use smart city pilots rather than "Internet Plus" (which is national-level with no cross-sectional variation) is correct.

**Forced fallback to time series methods:** The downscoping from DID to national time series is an unavoidable consequence of data constraints, but it fundamentally changes the identification strength. DID provides difference-in-differences identification under parallel trends; Granger causality provides only temporal precedence, which is necessary but not sufficient for causation. The analysis must be explicit that time series results are associational with temporal ordering, not causal in the DID sense. The EP framework should reflect this -- EP.truth for edges tested only via time series should be capped lower than for edges that would have been tested via DID.

**Composite index construction:** Equal-weight min-max normalization is the simplest defensible approach given the constraints. Principal component analysis (PCA) would be preferable (and is what the PKU-DFIIC uses), but with only 4 components and 24 observations, PCA is not well-identified. The equal-weight choice is acceptable for Phase 0 but should be tested against PCA in Phase 2 as a robustness check.

**DoWhy pipeline applicability:** The causal inference conventions mandate DoWhy for all causal edges. DoWhy is designed primarily for cross-sectional and panel data with clearly defined treatment-outcome pairs. Its applicability to national time series with T=24 is limited. The Phase 1 strategy must specify how DoWhy will be adapted (e.g., treating each year as an observation in a cross-sectional-like framework with lagged variables as instruments), or justify using `statsmodels` time series tools with DoWhy-inspired refutation logic applied manually.

## Alternative Approaches to Consider

1. **Synthetic control method (SCM) as partial DID substitute.** If even one province's data can be obtained (e.g., from publicly available provincial statistical yearbooks for a few key provinces), SCM could construct a synthetic counterfactual for a treated province using donor provinces. This requires far less data than full panel DID -- even 5-10 provinces with outcome data would suffice. SCM also handles T=24 better than Granger causality for causal claims. This should be evaluated as a data callback target: acquiring provincial employment data for 10-15 provinces from NBS yearbooks is likely feasible and would unlock a stronger identification strategy than pure time series.

2. **Structural break tests at known policy dates.** Rather than Granger causality (which requires >=30 observations per conventions), the analysis could use Chow tests or Bai-Perron tests for structural breaks at the known policy dates (2012 first smart city batch, 2015 Internet Plus, 2020 COVID). If employment structure variables show statistically significant breaks at these dates but not at placebo dates, this provides suggestive (not definitive) evidence of policy effects. This method works well with T=24 and does not require the minimum observation count that Granger causality does.

3. **Bayesian VAR (BVAR) for small-sample time series.** Classical VAR with T=24 and multiple variables is poorly identified. Bayesian VAR with Minnesota priors (Litterman, 1986) is specifically designed for short time series and provides coherent posterior inference. If Phase 1 proceeds with VAR-type methods, BVAR should be the default rather than classical VAR, with the prior specification documented and sensitivity-tested.

4. **Augmenting T with quarterly data.** Some World Bank indicators (GDP, trade) and FRED series (exchange rates) are available quarterly. If the key employment variables can be interpolated or proxied at quarterly frequency (e.g., using PMI employment sub-indices as monthly proxies), T could be increased to ~96, which comfortably exceeds the 30-observation threshold. This is a data callback candidate that would resolve issue A1.

## Figure and Table Assessment

No figures are produced in Phase 0. The mermaid DAG diagrams are well-structured and readable. The edge tables are complete with all required columns (edge, label, truth, relevance, EP, justification). The DAG comparison table effectively summarizes the key differences across the three competing hypotheses.

One concern: the mermaid DAGs use `<br>` tags for line breaks within node labels, which renders correctly in GitHub-flavored markdown but may not render in all mermaid viewers. Phase 6 should convert these to proper mermaid formatting if the DAGs appear in the final report.

## Notation and Consistency

- EP notation is consistent throughout: EP = truth x relevance, with both components in [0, 1].
- The abbreviation "DE" is used for both "Digital Economy" (the conceptual construct) and the DAG node label. This is clear in context but could cause confusion if "DE" is also used as a variable name in code (e.g., `DE_index`). Phase 1 should establish a variable naming convention.
- "SCP" (Smart City Pilot), "HC_INV" (Human Capital Investment), "IND_UP" (Industrial Upgrading), "LS" (Labor Structure) are used consistently across all three DAGs.
- The term "DID" is used throughout; "DiD" appears nowhere. This is consistent (pick one and stick with it).
- Edge labels use the Phase 0 taxonomy (LITERATURE_SUPPORTED, THEORIZED, SPECULATIVE). The causal inference conventions reference a different taxonomy (DATA_SUPPORTED, CORRELATION, HYPOTHESIZED, DISPUTED) for post-refutation classification. This distinction is correct -- the Phase 0 labels are pre-analysis and will be updated in Phase 3 -- but a note clarifying this transition would prevent confusion.
