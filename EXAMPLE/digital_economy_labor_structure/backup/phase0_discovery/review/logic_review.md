# Logic Review: Phase 0 Discovery

## Review Summary
- **Phase**: 0 — Discovery
- **Artifacts reviewed**:
  - `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase0_discovery/exec/DISCOVERY.md`
  - `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase0_discovery/exec/DATA_QUALITY.md`
  - `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/registry.yaml`
  - `/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/experiment_log.md`
- **Date**: 2026-03-29
- **Verdict**: ITERATE
- **Category A issues**: 3
- **Category B issues**: 6
- **Category C issues**: 2

---

## Conventions Compliance

| Convention (from `conventions/causal_inference.md`) | Status | Notes |
|-----------------------------------------------------|--------|-------|
| Construct a DAG before selecting estimation strategy | COMPLIANT | Three DAGs constructed in Step 0.2, estimation strategy deferred to Phase 1. |
| Every causal claim must survive at least 3 refutation tests | N/A | Refutation testing occurs in Phase 3. Phase 0 correctly labels all edges as hypothesized/literature-supported, not DATA_SUPPORTED. |
| Report effect sizes with confidence intervals, not just p-values | N/A | No estimation performed in Phase 0. |
| Acknowledge and document all untestable assumptions | COMPLIANT | Hidden Assumptions section enumerates 6 assumptions including SUTVA, reverse causality, and measurement validity. |
| Use CausalTest from scripts/causal_pipeline.py | N/A | Phase 3. |
| Classification follows refutation-based taxonomy | PARTIALLY COMPLIANT | Phase 0 uses pre-analysis labels (LITERATURE_SUPPORTED, THEORIZED) which is correct for this phase. However, the SPECULATIVE label from the taxonomy is never used despite some edges arguably warranting it (see Issue B3). |
| EP values must be updated after each refutation battery | N/A | Phase 3. |
| Treating correlation as causation | COMPLIANT | All edges are explicitly hypothesized, none claimed as established. |
| Ignoring collider bias | SEE ISSUE A3 | DAG 2 has a potential collider bias issue. |
| Using causal language for CORRELATION edges | COMPLIANT | Language is appropriately hedged throughout. |

---

## EP Propagation Audit

### EP Arithmetic Verification (Edge-Level)

All EP values are computed as EP = truth x relevance. I verify each edge table entry below.

**DAG 1 — Technology-Push:**

| Edge | Truth | Relevance | Stated EP | Computed EP | Match |
|------|-------|-----------|-----------|-------------|-------|
| DE --> SUB | 0.7 | 0.7 | 0.49 | 0.49 | YES |
| DE --> CRE | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| DE --> PROD | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| SUB --> MID_DECLINE | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| CRE --> HIGH_GROW | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| CRE --> PLAT | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| PROD --> SEC_SHRINK | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| MID_DECLINE --> LS | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| HIGH_GROW --> LS | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| PLAT --> LS | 0.5 | 0.4 | 0.20 | 0.20 | YES |
| SEC_SHRINK --> LS | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| SCP --> DE | 0.7 | 0.6 | 0.42 | 0.42 | YES |

**DAG 2 — Institutional Mediation:**

| Edge | Truth | Relevance | Stated EP | Computed EP | Match |
|------|-------|-----------|-----------|-------------|-------|
| DE --> LS (direct) | 0.3 | 0.4 | 0.12 | 0.12 | YES |
| DE --> HC_INV | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| DE --> IND_UP | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| DE --> LM_REF | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| HC_INV --> SKILL_UP | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| IND_UP --> TERT_EMP | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| LM_REF --> MOB | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| SKILL_UP --> LS | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| TERT_EMP --> LS | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| MOB --> LS | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| SCP --> DE | 0.7 | 0.6 | 0.42 | 0.42 | YES |

**DAG 3 — Segmentation:**

| Edge | Truth | Relevance | Stated EP | Computed EP | Match |
|------|-------|-----------|-----------|-------------|-------|
| DE --> FORMAL | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| DE --> INFORMAL | 0.4 | 0.7 | 0.28 | 0.28 | YES |
| FORMAL --> AUTO | 0.7 | 0.6 | 0.42 | 0.42 | YES |
| INFORMAL --> PLAT_JOB | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| AUTO --> FORMAL_LOSS | 0.7 | 0.5 | 0.35 | 0.35 | YES |
| PLAT_JOB --> INFORMAL_GAIN | 0.5 | 0.4 | 0.20 | 0.20 | YES |
| FORMAL_LOSS --> REALLOC | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| INFORMAL_GAIN --> REALLOC | 0.4 | 0.5 | 0.20 | 0.20 | YES |
| REALLOC --> LS | 0.4 | 0.6 | 0.24 | 0.24 | YES |
| FORMAL_LOSS --> WAGE_POL | 0.7 | 0.4 | 0.28 | 0.28 | YES |
| INFORMAL_GAIN --> WAGE_POL | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| WAGE_POL --> LS | 0.4 | 0.4 | 0.16 | 0.16 | YES |
| SCP --> DE | 0.7 | 0.6 | 0.42 | 0.42 | YES |

**Edge-level arithmetic: all 36 EP values verified correct. No arithmetic errors.**

### Chain-Level Joint EP Audit

The DISCOVERY.md does not compute Joint_EP for any causal chains. This is a gap (see Issue A1). For reference, the key chains and their Joint_EP values (computed as the product of edge EPs along the chain) are:

**DAG 1 longest chains (SCP --> DE --> ... --> LS):**
- SCP --> DE --> SUB --> MID_DECLINE --> LS: 0.42 x 0.49 x 0.42 x 0.35 = 0.030
- SCP --> DE --> CRE --> HIGH_GROW --> LS: 0.42 x 0.42 x 0.35 x 0.35 = 0.022
- SCP --> DE --> PROD --> SEC_SHRINK --> LS: 0.42 x 0.24 x 0.16 x 0.16 = 0.003

**DAG 2 longest chains:**
- SCP --> DE --> HC_INV --> SKILL_UP --> LS: 0.42 x 0.42 x 0.42 x 0.35 = 0.026
- SCP --> DE --> IND_UP --> TERT_EMP --> LS: 0.42 x 0.35 x 0.35 x 0.35 = 0.018
- SCP --> DE --> LM_REF --> MOB --> LS: 0.42 x 0.24 x 0.16 x 0.16 = 0.003

**DAG 3 longest chains:**
- SCP --> DE --> FORMAL --> AUTO --> FORMAL_LOSS --> REALLOC --> LS: 0.42 x 0.42 x 0.42 x 0.35 x 0.24 x 0.24 = 0.0015
- SCP --> DE --> INFORMAL --> PLAT_JOB --> INFORMAL_GAIN --> REALLOC --> LS: 0.42 x 0.28 x 0.24 x 0.20 x 0.20 x 0.24 = 0.00054

**Critical observation:** All Joint_EP values through the full instrumented chain (starting from SCP) are below the soft truncation threshold of 0.15, and most are below the hard truncation threshold of 0.05. DAG 3's chains are below the hard truncation threshold entirely. This raises a serious question about whether the proposed DID identification strategy would have sufficient EP even if the data were available. See Issue A2.

Note: If we compute Joint_EP from DE (not SCP) as the starting node, the chains are more viable. For example, DE --> SUB --> MID_DECLINE --> LS = 0.49 x 0.42 x 0.35 = 0.072 (above hard truncation). The question is which starting point is analytically appropriate -- see the discussion under Issue A2.

### DAG Acyclicity

All three mermaid DAGs are directed acyclic graphs. No cycles detected. Confounders are correctly represented as dashed edges (not part of the causal chain). Moderators in DAG 3 (HUKOU, SOE) are dashed, which is appropriate.

### Label Consistency

- LITERATURE_SUPPORTED edges are consistently assigned truth = 0.7.
- THEORIZED edges are assigned truth = 0.3-0.5, within the documented range of 0.3-0.7.
- No SPECULATIVE edges appear in any DAG, which may be an understatement for some edges (see Issue B3).
- One edge (PLAT --> LS in DAG 1) has truth = 0.5 with a THEORIZED label. The justification mentions observable growth and statistical classification uncertainty, which weakly supports a truth value at the high end of THEORIZED range. This is borderline but acceptable.
- One edge (PLAT_JOB --> INFORMAL_GAIN in DAG 3) has truth = 0.5 with a THEORIZED label. Same reasoning. Acceptable.

---

## Causal Claim Consistency

### 1. Refutation Alignment

No DATA_SUPPORTED claims are made in Phase 0. All edges are appropriately labeled as pre-analysis hypotheses. This is correct for Phase 0.

### 2. DAG-Claim Consistency

The three DAGs are logically consistent with their stated narratives:
- DAG 1 routes effects through direct technology channels (substitution and creation), consistent with the SBTC framework.
- DAG 2 routes effects through institutional mediators, consistent with human capital and structural change theory.
- DAG 3 routes effects through segmented labor market channels, consistent with Doeringer-Piore theory.

**However, there is a logical issue with DAG 2.** The DAG includes a direct DE --> LS edge (EP=0.12) alongside the mediated paths. The stated kill condition is that this direct effect should be "small and statistically insignificant." But the DAG already encodes a weak direct effect (truth=0.3). This creates a tautological structure: the DAG assumes what it claims to test. A cleaner formulation would either (a) set the direct effect to zero and test whether it is needed, or (b) assign it a higher truth value and test whether mediation reduces it. See Issue B1.

### 3. Evidence Sufficiency

The DATA_QUALITY.md correctly identifies that the available data (national time series only) is insufficient to test most of the DAG edges at the intended granularity. The EP.truth cap of 0.30 for edges requiring city-level or individual-level data is appropriate. However, this cap is stated in DATA_QUALITY.md but is not reflected back into the DISCOVERY.md EP tables. See Issue A1 — the DISCOVERY.md still shows original EP values without the data quality adjustment.

### 4. Circular Reasoning Check

No circular causal dependencies detected. The confounders (HC, REG in DAG 1; GOV, URB in DAG 2; HUKOU, SOE in DAG 3) are correctly exogenous.

One concern: In DAG 2, the edge DE --> HC_INV --> SKILL_UP --> LS could have a reverse path (LS --> HC_INV, if labor structure changes drive education investment). This is acknowledged in the "Hidden Assumptions" section (assumption 5 about reverse causality) but is not explicitly modeled as a potential bidirectional edge. Documenting it in hidden assumptions is acceptable for Phase 0 but Phase 3 must address it.

### 5. Competing DAG Genuineness

The three DAGs are genuinely different in causal structure:
- DAG 1 has strong direct paths (DE --> SUB, DE --> CRE) with no institutional mediation.
- DAG 2 has weak direct path and strong mediated paths through institutions.
- DAG 3 has no aggregate direct path and instead models segment-specific effects.

These represent substantively different theories (technology determinism vs. institutional mediation vs. structural heterogeneity). The comparison table (lines 317-325) correctly identifies the divergence points.

**One weakness:** DAGs 1 and 2 are not fully mutually exclusive. DAG 1 could accommodate mediation as a secondary channel, and DAG 2 could accommodate some direct technology effects. The kill conditions help, but they are formulated as "dominance" tests (e.g., DAG 2's kill condition: "direct effect remains large after controlling for mediators"). This means the DAGs can partially overlap in their predictions. This is not a blocking issue — it reflects genuine theoretical ambiguity — but Phase 1 strategy should define quantitative criteria for discriminating between them (e.g., "if mediation share > 60%, DAG 2 is preferred; if < 30%, DAG 1 is preferred"). See Issue B2.

---

## Reference Analysis Comparison

The DISCOVERY.md does not cite specific published analyses that serve as methodological benchmarks (the analysis_config CLAUDE.md states this table is filled in Phase 1). However, for Phase 0 review, the following gaps are notable compared to what a competing group would likely have:

1. **PKU-DFIIC data.** Any serious Chinese digital economy analysis published in 2024-2026 would use the Peking University Digital Financial Inclusion Index at the city or county level. This analysis correctly identifies the gap but the proxy index is a substantial weakness. A competing group with institutional access would have a decisive advantage.

2. **CFPS panel linkage.** Published studies (e.g., Finance Research Letters 2024, cited in DISCOVERY.md) use CFPS individual panel data to track employment transitions. Without this, the analysis cannot replicate or improve upon existing work.

3. **Staggered DID with heterogeneous treatment effects.** Recent econometrics literature (Callaway & Sant'Anna 2021, Sun & Abraham 2021) shows that two-way fixed effects DID is biased with staggered treatments. A competing analysis in 2026 would use robust staggered DID estimators. This methodological consideration is absent from DISCOVERY.md. See Issue B4.

4. **Synthetic control as robustness.** Published smart city DID studies increasingly pair DID with synthetic control methods (SCM) for robustness. Not mentioned.

5. **China Household Finance Survey (CHFS) or CHIP data.** Alternative micro-datasets that could supplement or substitute for CFPS are not discussed. See Issue B5.

---

## Issues

### Category A (Blocking)

1. **[A1]: Joint_EP not computed and data quality EP caps not propagated back to DAGs.**
   - Location: `DISCOVERY.md`, edge tables and DAG diagrams (lines 186-200, 238-251, 292-307)
   - Impact: Without Joint_EP values, Phase 1 cannot apply truncation thresholds (hard=0.05, soft=0.15) to decide which chains to pursue. Additionally, DATA_QUALITY.md caps EP.truth at 0.30 for skill-level edges, but the DISCOVERY.md EP tables still show the original uncapped values (e.g., SUB --> MID_DECLINE shows EP=0.42 but should be capped because mid-skill data is unavailable). Downstream agents will use incorrect EP values for prioritization.
   - Suggested fix: (a) Add a "Joint_EP by Chain" section to DISCOVERY.md computing the product of edge EPs along each major chain. (b) Add a "Data-Adjusted EP" column to the edge tables reflecting DATA_QUALITY.md caps (or add a post-quality-gate EP adjustment section). (c) Flag chains that fall below truncation thresholds.

2. **[A2]: All instrumented causal chains (from SCP) have Joint_EP below the soft truncation threshold of 0.15.**
   - Location: `DISCOVERY.md`, all three DAGs
   - Impact: The DID identification strategy (SCP --> DE --> ... --> LS) is the centerpiece of the analysis. But when Joint_EP is computed through the full chain, all values fall below 0.15 (the soft truncation threshold), and most below 0.05 (the hard truncation threshold). Under strict EP truncation rules, this would mean the DID-identified chain warrants only "lightweight assessment" or is "beyond analytical horizon." This is a logical tension: the analysis framework demands DID as the primary identification strategy, but the EP framework suggests it lacks explanatory power.
   - This likely reflects a conceptual issue with how Joint_EP should be interpreted for instrumental variable chains. The SCP --> DE edge is an instrument, not a primary causal mechanism. Its relevance (0.6) captures how well the instrument predicts the treatment, which is different from causal relevance in the mechanism sense. Phase 1 must resolve this tension explicitly.
   - Suggested fix: Add guidance in DISCOVERY.md on how to interpret Joint_EP for IV/DID chains versus mechanism chains. One approach: compute Joint_EP for mechanism chains (DE --> ... --> LS) separately from the instrument relevance (SCP --> DE), and apply truncation thresholds only to the mechanism chain portion. Document this decision explicitly.

3. **[A3]: DAG 2 has a potential collider bias issue that is not documented.**
   - Location: `DISCOVERY.md`, DAG 2 (lines 214-235)
   - Impact: In DAG 2, both GOV (Government Education Expenditure) and DE (Digital Economy) cause HC_INV (Human Capital Investment). If the analysis conditions on HC_INV (which it must to estimate mediation), this opens a spurious path between GOV and DE through the HC_INV collider. The current DAG shows GOV as a confounder of HC_INV and LS, but does not show a GOV --> DE path or acknowledge that conditioning on HC_INV in mediation analysis could introduce collider bias. This matters because government education expenditure and digital economy development are plausibly correlated through an omitted common cause (economic development level).
   - Suggested fix: Either (a) add an explicit edge or common cause linking GOV and DE (if theoretically justified), or (b) note in the DAG that mediation analysis conditioning on HC_INV must account for the collider structure, and document what identification assumption is needed to avoid bias. This must be resolved before Phase 3 mediation analysis.

### Category B (Important)

1. **[B1]: DAG 2 direct effect is tautologically weak.**
   - Location: `DISCOVERY.md`, DAG 2 edge table, DE --> LS direct edge (line 241)
   - Impact: The DAG encodes truth=0.3 for the direct effect, then proposes testing whether this direct effect is "small and statistically insignificant." The DAG structure already assumes the conclusion. This weakens the discriminating power of the kill condition.
   - Suggested improvement: Assign the direct effect truth=0.5 (agnostic prior) and let the data determine whether it should be revised downward. Alternatively, formulate the DAG 2 kill condition more precisely: "If the estimated direct effect accounts for more than 40% of the total effect, DAG 2 is rejected." The current kill condition is qualitative where a quantitative threshold would be more useful.

2. **[B2]: Quantitative DAG discrimination criteria are missing.**
   - Location: `DISCOVERY.md`, DAG Comparison section (lines 316-336)
   - Impact: The kill conditions are qualitative (e.g., "if mid-skill employment increases" for DAG 1, "if the direct effect remains large" for DAG 2). Without quantitative thresholds, Phase 3 analysts may reach ambiguous conclusions where multiple DAGs are "partially supported."
   - Suggested improvement: Add quantitative discrimination criteria. For example: "DAG 1 preferred if: direct effect > 50% of total effect AND skill polarization observed. DAG 2 preferred if: mediation share > 60% of total effect. DAG 3 preferred if: formal/informal sector effects are opposite-signed with |difference| > 0.1 standard deviations."

3. **[B3]: No SPECULATIVE edges in any DAG despite plausible candidates.**
   - Location: `DISCOVERY.md`, all DAG edge tables
   - Impact: The Phase 0 CLAUDE.md defines three pre-analysis labels: LITERATURE_SUPPORTED, THEORIZED, and SPECULATIVE. Every edge in all three DAGs is labeled either LITERATURE_SUPPORTED or THEORIZED. No SPECULATIVE edges exist. However, some edges have weak justification that arguably qualifies as SPECULATIVE:
     - WAGE_POL --> LS (DAG 3, EP=0.16): Wage polarization "driving" structural change is a reverse causal claim (structural change typically drives wage polarization, not vice versa). The justification is thin.
     - LM_REF (Labor Market Institutional Reform) in DAG 2: The justification explicitly states "evidence is limited and the causal direction is ambiguous." This sounds more SPECULATIVE than THEORIZED.
   - Suggested improvement: Review whether WAGE_POL --> LS and DE --> LM_REF should be downgraded to SPECULATIVE (truth capped at 0.2-0.3). This would lower their EP values and potentially push some DAG 3 chains below the hard truncation threshold.

4. **[B4]: Staggered DID methodological considerations absent.**
   - Location: `DISCOVERY.md`, DID discussion (lines 47-48, 107)
   - Impact: The analysis proposes using three staggered batches of smart city pilots (2012, 2014, 2015) for DID. Recent econometrics literature demonstrates that standard two-way fixed effects (TWFE) estimators are biased with staggered treatments and heterogeneous effects (Callaway & Sant'Anna 2021, de Chaisemartin & D'Haultfoeuille 2020, Sun & Abraham 2021). This is not mentioned anywhere in the DISCOVERY.md or DATA_QUALITY.md. A competing analysis published in 2026 would certainly use robust staggered DID estimators.
   - Suggested improvement: Add a note in the Open Issues section that Phase 1 strategy must address staggered DID bias. Cite the relevant methodological literature and specify that robust estimators (e.g., `did` package in R, or `csdid` in Stata) should be used if DID becomes feasible.

5. **[B5]: Alternative micro-datasets not explored.**
   - Location: `experiment_log.md`, data acquisition section
   - Impact: CFPS acquisition failed. The experiment log documents this and suggests a data callback. However, no alternative micro-datasets were explored: China Household Finance Survey (CHFS, by Southwestern University of Finance and Economics), Chinese Household Income Project (CHIP), or the China Labor-force Dynamics Survey (CLDS, by Sun Yat-sen University). Some of these may have more accessible data or better platform worker coverage.
   - Suggested improvement: Document in Open Issues that Phase 1 should evaluate whether CHFS, CHIP, or CLDS could serve as CFPS substitutes for specific DAG edges, particularly for DAG 3's employment segmentation analysis.

6. **[B6]: Relevance values across DAGs are not normalized for total causal attribution to LS.**
   - Location: `DISCOVERY.md`, all edge tables, edges terminating at LS
   - Impact: In DAG 1, four edges feed into LS with relevance values 0.5, 0.5, 0.4, and 0.4. Relevance is defined as "what share of the target event's variance does this edge explain?" If these are shares, they should not sum to more than 1.0. But 0.5 + 0.5 + 0.4 + 0.4 = 1.8, which implies more than 180% of LS variance is explained by its immediate causes. Similar over-attribution occurs in DAGs 2 and 3. This is a soft issue because relevance values are qualitative estimates in Phase 0, but it creates an inconsistency in interpretation.
   - Suggested improvement: Either (a) renormalize the relevance values entering LS so they sum to at most 1.0, or (b) clarify explicitly that relevance values are independent (not shares) and represent marginal explanatory contribution rather than variance partitioning. The latter interpretation is defensible but should be stated.

### Category C (Minor)

1. **[C1]: Mermaid diagrams use `graph TD` but the edges in DAG 2 flow both downward and across.**
   - Location: `DISCOVERY.md`, DAG 2 mermaid block (line 214)
   - Suggested fix: Purely cosmetic. The mermaid rendering is functional but some diagrams could benefit from `graph LR` for readability, especially DAG 3 which has parallel formal/informal tracks.

2. **[C2]: Experiment log describes digital economy index as "5 World Bank indicators" but only 4 were used.**
   - Location: `experiment_log.md`, line 78-80
   - Impact: The log first states "Composite index from 5 World Bank indicators" then corrects itself to note only 4 were used. This is confusing but self-correcting within the same entry.
   - Suggested fix: Edit the log entry to say "originally planned 5 indicators; 4 acquired and used" at first mention.

---

## Figure Review

No figures are produced in Phase 0. The mermaid DAG diagrams are code blocks, not rendered figures. No figure review applicable.

---

## Distribution Sanity Checks

No data plots or distribution visualizations are produced in Phase 0. The data quality assessment provides summary statistics (ranges, missing rates) which were verified against the stated data sources:

- GDP per capita: $969-$12,971 (2000-2023) -- consistent with China's development trajectory.
- Employment agriculture: 50.0% to 22.8% -- consistent with known structural transformation.
- Internet users: 1.8% to 90.6% -- consistent with known digitalization trajectory.
- Self-employed: 51.7% to 38.4% -- consistent with known formalization trend.
- Youth unemployment: 6.8% to 15.6% -- consistent with post-COVID surge.

All summary statistics are plausible. No anomalies detected.

---

## Regression Detection

This is the first review of Phase 0. No prior versions exist for regression comparison.

One internal consistency check: the experiment log states "26 indicators attempted, 24 acquired" for World Bank data, while registry.yaml lists 25 query indicators under `worldbank_china_indicators`. The DATA_QUALITY.md states "24 rows x 25 columns." These numbers are mutually consistent (26 attempted, 25 columns retrieved -- one indicator per column, with one indicator possibly consolidated or dropped during processing, and 24 annual observations as rows). No regression detected.

---

## Upstream Feedback

Not applicable for Phase 0 (this is the first phase). However, the following issues must be carried forward as binding constraints on Phase 1:

1. Phase 1 strategy must address the Joint_EP truncation tension for DID chains (Issue A2).
2. Phase 1 must define quantitative DAG discrimination thresholds (Issue B2).
3. Phase 1 must consider staggered DID bias (Issue B4).
4. Phase 1 must evaluate alternative micro-datasets (Issue B5).
5. All data quality caps from DATA_QUALITY.md must be propagated into Phase 1 EP tables.

---

## Verdict Justification

**ITERATE.** Three Category A issues must be resolved before Phase 1 can begin:

- **A1** (Joint_EP not computed, data quality caps not propagated) would cause downstream agents to work with incorrect EP values and fail to apply truncation thresholds.
- **A2** (DID chain Joint_EP below truncation thresholds) represents a fundamental tension between the proposed identification strategy and the EP framework that must be explicitly resolved in DISCOVERY.md.
- **A3** (collider bias in DAG 2) could invalidate the mediation analysis if not acknowledged and addressed in the DAG structure.

The Category B issues are important but do not block progress -- they can be addressed at the start of Phase 1 provided the Phase 0 artifact documents them as open items.
