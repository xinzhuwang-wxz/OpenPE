# Domain Review

## Summary
- **Artifact reviewed**: phase1_strategy/exec/STRATEGY.md
- **Date**: 2026-03-29
- **Overall assessment**: Needs iteration
- **Category A issues**: 3
- **Category B issues**: 4
- **Category C issues**: 3

The strategy document demonstrates strong awareness of the data constraints inherited from Phase 0 and makes sensible downscoping decisions. The reference analysis survey is well-chosen and relevant. The EP accounting is transparent and conservative. However, three blocking issues require resolution: the proxy DID design is methodologically misleading and risks producing artifacts that overstate causal identification; the Cholesky-based mediation approach has a fundamental ordering problem given the simultaneous trending of all variables; and the ILO model endogeneity issue is acknowledged but not given adequate treatment priority given its potential to invalidate the main results.

---

## First Principles Assessment

The four first principles (Ricardo-Marx-Schumpeter displacement/compensation, SBTC/Acemoglu-Autor task framework, Lewis-Kuznets structural change, Doeringer-Piore segmentation) are well-chosen and standard for this domain. They are correctly sourced and defensible. The causal DAGs in Phase 0 were thoughtfully constructed with genuinely competing structures rather than minor variations.

The Phase 1 consolidation into a single testable DAG is an honest and appropriate response to data constraints. The decision to retain only measurable edges (manufacturing employment decline as substitution proxy, services employment growth as creation proxy, industrial upgrading as mediator) is defensible. However, the consolidated DAG obscures a critical conceptual issue: using sectoral employment shares as proxies for creation and substitution effects conflates the digital economy effect with the broader Lewis-Kuznets structural transformation that China would have experienced regardless of digitalization. This is acknowledged in the document (Section 12, "Domain Context") but is not elevated to the systematic uncertainty inventory with the severity it deserves.

The demographic confounder (working-age population peaking around 2012) is correctly identified as critical. The strategy appropriately treats it as the highest-EP confounder (EP=0.36) and mandates its inclusion in all specifications. This is one of the strongest aspects of the strategy.

---

## Data Source Validity Assessment

The DATA_QUALITY.md is one of the most honest data assessments I have seen in analyses of this type. The explicit acknowledgment that the DID design is infeasible, that skill-level data is missing, and that the digital economy composite index is a crude proxy are all appropriate and well-calibrated.

The construct validity concern for the DE composite index deserves emphasis. The index captures ICT infrastructure penetration (internet users, mobile subscriptions, broadband, R&D expenditure) but misses the core dimensions of China's digital economy: e-commerce transaction volume, digital financial inclusion, platform economy scale, and software/IT services revenue. The Peking University Digital Financial Inclusion Index (PKU-DFIIC) is the standard measure in Chinese digital economy research. Without it, any result attributed to "digital economy development" is actually measuring "ICT infrastructure maturity," which is a related but distinct concept. The strategy acknowledges this (Section 5.3) but the downstream implications for the creation/substitution decomposition are not fully drawn out -- ICT infrastructure penetration is more likely to correlate with substitution (automation enablement) than creation (platform economy expansion), potentially biasing the relative magnitudes of the two channels.

The T=24 constraint is severe. The strategy correctly notes this violates the T>=30 convention for Granger causality and proposes Toda-Yamamoto with bootstrap as mitigation. This is the standard remedy in the time series literature and is appropriate. However, the power analysis commitment (Section 8.1, "Low power" risk at 50% probability) should be executed before Phase 3, not during it. Knowing the statistical power ex ante would allow the strategy to set realistic expectations and avoid over-interpreting insignificant results.

---

## Methodology Assessment

### Strengths

1. **Method hierarchy is sound.** The progression from simple filters (rejected for spurious regression risk) through Granger causality to cointegration/VECM is the correct escalation for I(1) time series. The ARDL bounds test as a fallback for ambiguous stationarity results is a thoughtful addition.

2. **Reference analyses are well-selected.** Zhu et al. (2023), Li et al. (2024), and Zhao and Li (2022) are directly relevant and represent the gold-standard designs (staggered DID, provincial panel FE+GMM) that this analysis cannot replicate. Using their results as calibration targets (e.g., 22% mediation share from Li et al.) is a good practice.

3. **Creation/substitution decomposition via sectoral employment.** Given the data constraints, using manufacturing employment share as a substitution proxy and services employment share as a creation proxy is the best available approach. The strategy correctly notes these are proxies, not direct measures.

4. **Conventions compliance is thorough.** The deviation from T>=30 is explicitly documented with mitigation. The non-applicability of DoWhy for time series is correctly justified. The panel analysis conventions are correctly marked as inapplicable.

### Concerns

1. **Proxy DID design (Section 2.5).** This is the most problematic element of the strategy. The "proxy DID" specification regresses `LS_t = alpha + beta_1*DE_t + beta_2*POST_t + beta_3*(DE_t*POST_t) + gamma*DEMO_t + epsilon_t` with POST=1 for 2016-2023. This is not a DID in any meaningful sense -- it is a regression with a structural break interaction term in a single time series. Calling it "proxy DID" risks misleading readers into attributing more causal identification to the design than it possesses. The limitations section (Section 2.5, "Limitations") correctly identifies the problems, but the label "proxy DID" persists throughout the document and into the analysis tree and milestone descriptions. In my experience with similar analyses, this kind of labeling creates presentational inertia that survives into the final report. The structural break interaction is a legitimate technique -- it should be presented as such, without the DID framing.

   More substantively, the 2013-2015 treatment window coincides with at least four concurrent national policy shifts (leadership transition, anti-corruption campaign, economic growth slowdown, supply-side reform). With T=24 and no control group, there is no way to attribute a structural break to smart city pilots specifically. The strategy acknowledges this (Section 5.2, "Structural break confounding: HIGH -- cannot be eliminated, only documented") but then proceeds to design a four-panel proxy DID figure (Section 2.5) that will visually suggest a before/after causal narrative. This is a tension between the honest uncertainty assessment and the presentational design.

2. **VAR-based mediation via Cholesky decomposition.** The strategy proposes estimating mediation through industrial upgrading using Cholesky-ordered impulse responses in a trivariate VAR (DE, services GDP share, employment structure). The Cholesky ordering (DE first, mediator second, outcome third) assumes that DE shocks affect the mediator contemporaneously but the mediator does not affect DE within the same period. At annual frequency, this assumption is difficult to defend -- digital economy development and industrial upgrading are likely simultaneous within a year. The strategy mentions generalized impulse responses (Pesaran and Shin 1998) as a robustness check (Section 6, Open Issue 4), but this should be the primary approach given the annual frequency. Cholesky ordering is more appropriate for monthly or quarterly data where the contemporaneous restriction is more plausible.

3. **ILO model endogeneity.** The strategy identifies this as Open Issue 6 and mentions running specifications with and without GDP/urbanization controls. However, the ILO endogeneity issue is more fundamental than a sensitivity check suggests. If ILO modeled employment estimates mechanically incorporate GDP growth and urbanization as inputs, then any regression of employment on a variable correlated with GDP growth (which the DE composite index certainly is, since it includes broadband and R&D spending that correlate with GDP) could produce spurious coefficients through the measurement model, not through the data-generating process. This is not a standard omitted variable problem -- it is a measurement-model-induced correlation. The strategy should explicitly discuss whether the ILO modeled estimates for China use input variables that overlap with the DE index components, and if so, quantify the expected mechanical correlation.

---

## Systematic Uncertainty Assessment

The uncertainty inventory (Section 5) is comprehensive. All seven DATA_QUALITY.md warnings are mapped to systematic entries (Section 5.4), with no silent omissions. The cross-referencing table is a model of transparency.

The severity assessments are reasonable. Spurious regression is correctly rated HIGH. Structural break confounding is correctly rated HIGH. The construct validity of the DE index is appropriately flagged.

One gap: the uncertainty inventory does not address the possibility of reverse causality from employment structure to digital economy development. The strategy mentions this in DISCOVERY.md (Hidden Assumption 5: "Labor shortages or surpluses might drive digital adoption") but does not include it as a systematic uncertainty source. The Granger causality tests will partially address this (by testing DE-->employment but also employment-->DE), but the systematic uncertainty table should explicitly list "reverse causality" and its quantification strategy.

---

## Verification Assessment

The milestone structure (Section 12) is well-designed with clear pass/fail criteria. The fallback strategy (Section 8.2) for null results is unusually honest: "Report the null result honestly as the primary finding." This is the correct approach.

The out-of-sample validation plan (train 2000-2019, test 2020-2023) has a known problem that the strategy acknowledges: the test period includes the COVID-19 structural break. With only 4 test observations, one of which is an extreme outlier year, the out-of-sample validation will have essentially no discriminating power. The strategy should either acknowledge this validation is pro forma or propose an alternative (e.g., leave-one-out cross-validation within the pre-COVID sample, which at least avoids the structural break problem even if the effective sample is small).

---

## EP and Causal Claim Assessment

The EP updating from Phase 0 to Phase 1 is transparent and conservative. The construct validity penalty (-0.10 for all DE-related edges) and method credibility adjustments (-0.05 to -0.10) are reasonable and well-justified. The resulting Phase 1 EP values (highest: DE-->SUB at 0.32, DEMO-->LS at 0.36) appropriately set expectations that any causal claims will be hedged.

The Joint_EP computation for mechanism chains is correct. The critical observation that the three-link mediation chain (DE-->IND_UP-->TERT_EMP-->LS, Joint_EP=0.021) falls below hard truncation while individual links are above soft truncation is handled with the right solution: test reduced-form relationships rather than the full chain. The VAR impulse response decomposition does not require link-by-link EP multiplication, and this is correctly noted.

The chain classification is reasonable. The decision to classify DAG 3 (segmentation) as "beyond horizon" and DAG 1 skill-level chains as EP=0.00 is correct given the data constraints.

One concern: the substitution channel (DE-->employment_industry_pct) receives EP=0.32 and "full analysis" treatment, but this edge conflates digital-economy-driven manufacturing decline with the broader Lewis-Kuznets deindustrialization trend. China's manufacturing employment share has been declining since the early 2000s due to rising wages, trade patterns, and income-driven demand shifts toward services. The DE index will correlate with this trend mechanically (both are trending). The Granger test and cointegration approach may find a "relationship" that is really just shared trend dynamics, even if technically not spurious in the Engle-Granger sense (cointegration means the residual is stationary, not that the relationship is causal). The EP=0.32 may overstate the causal content of what this edge can deliver.

---

## Result Plausibility

The strategy's risk assessment (Section 8.1) assigns a 40% probability to "demographic confounding dominates" and a 50% probability to "low power." These are realistic and suggest the analyst expects the most likely outcome is either a null result or a result dominated by demographics. This is plausible given the domain context -- China's demographic transition is the dominant macro trend affecting labor structure, and the digital economy is one of several concurrent forces. The strategy is appropriately calibrated for this expectation.

The calibration targets from reference analyses are useful. Li et al. (2024) finding 22% mediation through industrial upgrading provides a benchmark. Zhao and Li (2022) finding an inverted-U shape provides a nonlinearity prediction. These can serve as plausibility checks on the Phase 3 results.

---

## Issues by Category

### Category A (Blocking)

1. **[A1]: Proxy DID labeling and design creates misleading causal framing**
   - Domain impact: The term "proxy DID" implies a level of causal identification (treatment vs. control comparison) that does not exist in a single time series with a structural break interaction. Readers familiar with DID methodology will expect parallel trends tests, treatment/control comparisons, and SUTVA discussions -- none of which apply. The four-panel figure design (Section 2.5) will visually suggest a before/after causal story that the data cannot support. Multiple concurrent national policy changes in 2013-2015 make attribution to smart city pilots impossible at the national aggregate level.
   - Required action: Rename "proxy DID" to "structural break analysis" or "pre/post comparison" throughout the document. Retain the structural break methodology (Chow test, Bai-Perron) -- these are legitimate techniques. Remove or heavily caveat the four-panel figure that implies a DID-style treatment effect. The figure can show pre/post trends, but must not include counterfactual extrapolation lines that suggest a treatment effect without a control group.

2. **[A2]: ILO model endogeneity requires primary treatment, not sensitivity-check treatment**
   - Domain impact: If ILO modeled employment estimates for China use GDP growth and urbanization as model inputs (which is standard practice for the ILO's imputed data in developing countries), then any regression of these employment variables on GDP-correlated regressors (including the DE composite index) could produce mechanically significant coefficients. This is not an omitted variable problem -- it is a measurement-induced correlation that cannot be fixed by adding or removing controls. It could invalidate the primary Granger and VECM results.
   - Required action: Before Phase 3, investigate the ILO modeling methodology for China's employment estimates. Document which input variables the ILO model uses. If GDP and/or urbanization are inputs, elevate this from a sensitivity check (Open Issue 6) to a primary systematic uncertainty. Consider using China's National Bureau of Statistics employment data from the Population Census / 1% sample surveys (available for census years) as a validation cross-check, even if only for a few time points.

3. **[A3]: Reverse causality must appear in the systematic uncertainty inventory**
   - Domain impact: The omission of reverse causality (employment structure changes driving digital economy adoption) from the systematic uncertainty inventory (Section 5) is a gap. DISCOVERY.md Hidden Assumption 5 identifies this as a concern. Labor shortages from demographic aging may simultaneously drive both digital technology adoption and employment structure change, creating a classic simultaneity problem distinct from the demographic confounding already addressed. The Toda-Yamamoto Granger test partially addresses this by testing bidirectional causality, but the systematic inventory should explicitly name reverse causality and the Granger bidirectional test as its quantification method.
   - Required action: Add "reverse causality: employment structure --> DE" as a row in Section 5.2 (Systematic Uncertainty Sources), cross-referenced to the bidirectional Granger test. Assign severity MEDIUM (the demographic confounder control partially addresses this, but cannot fully resolve simultaneity).

### Category B (Important)

1. **[B1]: Cholesky-ordered mediation should not be the primary method at annual frequency**
   - Domain impact: Cholesky ordering assumes a within-period causal ordering that is difficult to defend at annual frequency. Digital economy development and industrial upgrading are likely simultaneous within a year. The mediation share estimate will be sensitive to the ordering assumption, and at T=24, there is insufficient data to test ordering robustness empirically.
   - Suggested action: Make generalized impulse responses (Pesaran and Shin 1998) the primary mediation method. Cholesky ordering becomes the secondary/robustness check. Document the ordering sensitivity explicitly.

2. **[B2]: Lewis-Kuznets structural transformation confounding is underweighted**
   - Domain impact: China's sectoral employment shift (agriculture to services) is a well-documented structural transformation driven by income growth, urbanization, and demographic change. Using manufacturing employment decline as a "substitution" proxy and services employment growth as a "creation" proxy risks attributing the entire structural transformation to the digital economy. The DE index is trending upward over the same period by construction (ICT penetration grows monotonically). Even with cointegration, the Granger test cannot distinguish "digital economy accelerates structural transformation" from "both are driven by the same underlying development process."
   - Suggested action: Include GDP per capita and urbanization rate in the Granger/VECM specifications as controls (already planned) but also run a specification that tests whether DE Granger-causes employment structure after partialling out GDP growth and urbanization growth. If DE loses significance after removing the trend component shared with GDP, the "digital economy effect" is likely a relabeled development effect. Report this test prominently.

3. **[B3]: Power analysis should precede Phase 3 testing, not accompany it**
   - Domain impact: With T=24, power is the binding constraint. The strategy assigns 50% probability to "low power" preventing detection of moderate effects. Running power analysis before hypothesis testing allows the analysis to set minimum detectable effect sizes and interpret null results properly. Running it alongside results risks post-hoc rationalization.
   - Suggested action: In Phase 2, compute the minimum detectable effect size (MDES) for the Toda-Yamamoto Granger test at T=24 with 1 and 2 lags, using simulation. Report the MDES in the Phase 2 artifact. This sets expectations: "We can detect effects larger than X at 80% power; effects smaller than X would appear insignificant even if real."

4. **[B4]: Out-of-sample validation plan needs revision**
   - Domain impact: The 2020-2023 test window contains the COVID structural break, making it uninformative for validation. Four observations with an outlier year provide no discriminating power.
   - Suggested action: Replace or supplement with leave-one-out or rolling-window cross-validation within the 2000-2019 sample. Alternatively, acknowledge that formal out-of-sample validation is not feasible at T=24 and rely on in-sample robustness checks (lag sensitivity, specification sensitivity) as the primary validation.

### Category C (Minor)

1. **[C1]: Bai-Perron implementation gap**
   - The `ruptures` package availability is flagged as uncertain (Open Issue 2). The sequential sup-Wald approach for unknown break dates is implementable manually but non-trivial. If only Chow tests at known dates are feasible, this reduces the structural break analysis to confirmatory testing (testing where you expect to find a break), which has less evidential value than exploratory break detection.
   - Suggested action: Confirm `ruptures` availability in Phase 2. If unavailable, add it to pixi.toml or implement the Bai-Perron test manually using the algorithm from the original paper.

2. **[C2]: COVID-19 handling decision deferred to Phase 2**
   - The three options (COVID dummy, sample truncation to 2019, test with/without) are all reasonable. However, sample truncation to T=20 further reduces power.
   - Suggested action: Prefer the COVID dummy approach (retains all observations while controlling for the shock). Document sensitivity to this choice.

3. **[C3]: Collider bias in mediation (Open Issue 4) needs explicit DAG representation**
   - The concern that conditioning on IND_UP may open a collider path via government expenditure is raised but not illustrated. A small DAG showing the collider path would make the concern concrete and testable.
   - Suggested action: Add a mini-DAG in the open issues section showing the potential collider structure and how generalized impulse responses avoid the problem.

---

## Acceptance Readiness

I would not accept this strategy in its current form. The three Category A issues must be resolved before proceeding to Phase 2.

The most critical issue is A1 (proxy DID labeling). In the Chinese digital economy literature, DID with smart city pilots is a well-established and specific methodological choice (as demonstrated by Reference 1, Zhu et al. 2023). Presenting a national time series structural break as a "proxy DID" creates a false equivalence that would not survive peer scrutiny. The structural break analysis itself is a legitimate and useful technique -- it does not need the DID label to justify its inclusion.

Issue A2 (ILO model endogeneity) is potentially the most damaging to the analysis if left unaddressed, because it could produce mechanically significant results that appear to confirm the DE-->employment relationship but are actually artifacts of the ILO's modeling methodology. This needs investigation before Phase 3 estimation, not a post-hoc sensitivity check.

Issue A3 (reverse causality in the uncertainty inventory) is a straightforward addition that completes the systematic uncertainty accounting.

With these three issues resolved, the strategy would be ready for advancement. The four Category B issues would strengthen the analysis but are not blocking -- they can be addressed during Phase 2 and Phase 3 execution as long as the strategy document acknowledges them as planned enhancements.
