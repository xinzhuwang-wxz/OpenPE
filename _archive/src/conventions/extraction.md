# Extraction Measurements

Conventions for analyses that extract a physical parameter from event counts
or rates — double-tag counting, efficiency ratios, branching fractions, or
similar methods where the result comes from a formula applied to observed
yields rather than from a fit to a discriminant distribution.

## When this applies

Any analysis where the primary result is computed from a closed-form
expression of measured yields, efficiencies, or ratios — not from a
template fit or unfolding procedure. Common examples:

- Double-tag counting (e.g., R_b from N_tt / N_had)
- Efficiency extraction from tag-and-probe
- Branching fraction ratios
- Cross-section ratios where backgrounds are negligible or subtracted

If the analysis uses a binned likelihood fit to a discriminant shape, the
`unfolding.md` or search conventions apply instead.

---

## Standard configuration

- **MC pseudo-data for Phase 4a.** The expected result must be computed on
  MC-generated pseudo-data counts, not on real data. Generate counts from
  MC truth parameters using the extraction formula (e.g., for R_b:
  N_t = 2 * N_had * [eps_b * R_b + eps_nonb * (1 - R_b)]). Optionally
  Poisson-fluctuate to assess statistical reach.
- **Fixed random seed.** All pseudo-data generation and 10% subsample
  selection use documented fixed seeds for reproducibility.
- **Per-subperiod granularity.** When multiple data-taking periods exist,
  track the result per period as a standard cross-check.
- **Counting vs. likelihood extraction.** Pure counting (closed-form
  formula applied to yields) is appropriate when the extraction formula is
  simple and the systematic treatment is transparent. Likelihood extraction
  (fitting a model to binned or unbinned data) is preferred when: multiple
  parameters are extracted simultaneously, nuisance parameters need profiling,
  or correlations between inputs are complex. Document the choice and justify.
- **Uncertainty propagation.** For counting extractions with few inputs,
  analytical error propagation (partial derivatives) is standard. For
  extractions with many correlated inputs or non-linear formulas, toy-based
  propagation (Poisson-fluctuate inputs, repeat extraction, take RMS) is
  more robust. Report which method is used and, if analytical, verify
  against toys for at least the dominant sources.
- **Efficiency binning.** Efficiency corrections must be derived in bins
  fine enough to capture kinematic dependence but coarse enough for adequate
  statistics per bin. As a rule of thumb, each efficiency bin should contain
  at least ~100 MC events; below this, statistical noise in the correction
  dominates. Document the binning choice and its motivation.
- **Data-derived calibration (scale factors).** When the extraction depends
  on MC-derived efficiencies (e.g., tagging efficiency), derive data/MC
  scale factors from a control sample using tag-and-probe or similar
  methods. Apply these scale factors to the MC before extraction. If
  data-derived calibration is not feasible, assign the full data/MC
  difference as a systematic — but document why calibration was not done.
  Relying on uncalibrated MC efficiencies without justification is
  Category A.

---

## Required systematic sources

### Efficiency modeling

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Tag/selection efficiency | Vary efficiency corrections within their uncertainties | The extracted quantity depends directly on efficiency estimates |
| Efficiency correlation | Evaluate hemisphere or object correlation effects | Double-tag methods assume independence; violations bias the result |
| MC efficiency model | Compare efficiencies from alternative MC generators | Generator-dependent fragmentation affects tagging efficiency |

### Background contamination

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Non-signal contamination | Vary background fractions within estimated uncertainties | Residual backgrounds in the tagged sample bias the yield |
| Background composition | Use alternative models for background mixture | The relative contribution of different backgrounds affects the correction |

### MC model dependence

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Hadronization model | Compare generators with different fragmentation (string vs. cluster) | Fragmentation model affects both efficiencies and acceptance |
| Physics parameters | Vary heavy-quark mass, fragmentation function parameters | Input physics parameters propagate to the extracted quantity |

### Sample composition

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Flavour composition | Vary assumed non-signal flavour fractions | Extraction formulas depend on the composition of the inclusive sample |
| Production fractions | Vary assumed production ratios if used as inputs | Any external input contributes its uncertainty |

---

## Required validation checks

1. **Independent closure test (Category A if fails).** Apply the full
   extraction procedure to a statistically independent MC sample (not the
   sample used to derive efficiencies or corrections). Extract the quantity
   and compare to MC truth. The pull (extracted value minus truth, divided
   by the method's uncertainty) must be < 2 sigma. Failure indicates a bias
   in the method.

2. **Parameter sensitivity table.** For each MC-derived input parameter,
   compute |dResult/dParam| * sigma_param. Flag any parameter contributing
   more than 5x the data statistical uncertainty — these are the dominant
   systematics and require careful evaluation.

3. **Operating point stability (Category A if fails).** Scan the extracted
   result vs. the primary selection variable (e.g., the classifier working
   point or the cut threshold) over a range spanning at least 2x the
   optimized region. The result must be flat within uncertainties — a
   dramatic variation indicates the measurement is not robust and the
   operating point is not in a stable plateau. This is a physics red flag,
   not just a systematic: it means the result depends critically on an
   arbitrary choice. Investigate before proceeding.

4. **Per-subperiod consistency.** Extract the result independently for each
   data-taking period. Compute chi2/ndof across periods. A chi2/ndof >> 1
   indicates time-dependent effects (detector aging, calibration drift) not
   captured by the MC model.

5. **10% diagnostic sensitivity (Phase 4b).** The 10% data validation must
   include at least one diagnostic genuinely sensitive to data/MC
   differences — not just a comparison of the extracted quantity (which is
   dominated by correlated systematics and insensitive to subsample size).
   Required: data-derived tag rates or double-tag fractions compared to MC,
   and self-calibrated parameter comparison between 10% data and MC.

---

## Pitfalls

- **Running on real data in Phase 4a.** The entire point of the 4a → 4b →
  4c staged validation is that 4a uses MC-only pseudo-data. Computing the
  extraction on real data counts in 4a makes 4a and 4c identical and
  defeats the staged validation protocol.

- **Insensitive 10% test.** Comparing only the final extracted quantity on
  10% data vs. MC tells you almost nothing — the statistical uncertainty
  dominates and hides real data/MC differences. The 10% test must include
  intermediate diagnostics (tag rates, efficiency comparisons, per-period
  results) that are sensitive at the 10% statistics level.

- **Missing independent MC for closure.** The closure test must use an MC
  sample statistically independent from the one used to derive corrections
  and efficiencies. Using the same sample tests self-consistency, not the
  method's validity. If only one MC sample is available, split it (using a
  documented fixed seed) into derivation and validation halves.

- **Assuming hemisphere independence.** Double-tag methods often assume that
  tagging in one hemisphere is independent of the other. QCD correlations
  (gluon splitting, color reconnection) violate this. Evaluate the
  correlation coefficient from MC and propagate its uncertainty.

- **Neglecting non-primary flavours.** Extraction formulas typically include
  terms for non-signal flavours (e.g., charm and light quark contributions
  in an R_b measurement). Setting these to nominal MC values without
  uncertainty propagation underestimates the systematic error.

---

## References

- LEP/SLD EWWG combination: "Precision electroweak measurements on the Z
  resonance" (Phys. Rept. 427, 257, 2006). INSPIRE: ALEPH:2005ab.
  Defines the standard methodology for heavy-flavour extraction at the Z.
- ALEPH R_b measurement: "A measurement of R_b using a lifetime-mass tag"
  (Phys. Lett. B401, 163, 1997). INSPIRE: Barate:1997ha. Reference for
  double-tag counting with hemisphere correlations.
- DELPHI R_b/R_c: DELPHI double-tag measurements of R_b and R_c — multiple
  papers across 1995-2000. Use `search_lep_corpus` with query "DELPHI R_b
  double tag" to retrieve specific papers and their systematic programs.
- SLD R_b: "A measurement of R_b using a vertex mass tag" (Phys. Rev. Lett.
  80, 660, 1998). INSPIRE: Abe:1997sb. Reference for high-purity
  single/double tag methods with self-calibrating efficiencies.
- PDG review: "Electroweak model and constraints on new physics" in the
  Review of Particle Physics. Current world averages for R_b, R_c, and
  correlation matrices between electroweak observables.
