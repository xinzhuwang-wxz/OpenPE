# Search / Limit-Setting Analyses

Conventions for analyses that test for the presence of a signal process
against a background-only hypothesis, producing either an exclusion limit
or a significance measurement.

## When this applies

Any analysis where the primary result is an observed (expected) upper limit
on a signal cross-section, coupling, or branching ratio, or a significance
(p-value) for rejecting the background-only hypothesis. This includes
bump hunts, cut-and-count searches, and shape-based searches using a
discriminant distribution.

If the primary result is a corrected spectrum or extracted physical
parameter, use `unfolding.md` or `extraction.md` instead.

---

## Standard configuration

- **CLs method.** Use the modified frequentist CLs method (CLs = CL_s+b /
  CL_b, not the simple CL_s+b) for upper limit calculations. CLs avoids
  excluding signal hypotheses to which the analysis has no sensitivity — a
  problem that arises with CL_s+b when the expected background is small.
- **Asymptotic approximation.** Acceptable for expected limits and initial
  observed limits when the expected event counts in each bin are > ~5. For
  final results with low statistics, validate against toy-based limits (or
  use toys directly).
- **Test statistic.** Use the profile likelihood ratio with the constraint
  mu >= 0 (one-sided) for upper limits. For discovery significance, use
  the unconstrained (two-sided) profile likelihood ratio.
- **Signal injection.** Inject signal at 0x, 1x, 2x, and 5x the expected
  cross-section. See Required validation check #2 for pass/fail criteria.
- **Blinding.** The signal region discriminant distribution in data is not
  examined until Phase 4b (10% subsample) or 4c (full data). See
  `methodology/04-blinding.md` for the full protocol.

---

## Required systematic sources

The sources below are organized for e+e- collider searches. For pp collider
searches, replace beam-related sources (ISR, beam energy) with the
pp-specific equivalents (PDF, pileup) and add luminosity as a normalization
source.

### Signal modeling

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Signal cross-section theory uncertainty | Scale variations (muR, muF), higher-order corrections | Affects the interpretation of the limit in terms of a physical parameter |
| Signal acceptance | Generator comparison, ISR variations | Different generators predict different acceptance at the same √s |
| Signal shape | Alternative signal MC or parameter variations (mass, width, coupling) | The discriminant shape determines how the signal distributes across bins |
| ISR modeling | Vary ISR treatment or compare generators with different ISR implementations | ISR shifts effective √s, affecting signal kinematics and acceptance — dominant beam-related systematic at LEP2 |

### Background estimation

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| 4-fermion backgrounds | Compare generators (e.g., KORALW, grc4f, EXCALIBUR) for WW/ZZ/Weν | Irreducible 4-fermion processes are the dominant background for many LEP2 searches; generator differences are significant |
| Background normalization | Vary normalization within CR-constrained or theory uncertainty | Transfer factor or theory cross-section uncertainty propagates to the SR prediction |
| Background shape | Alternative functional forms or MC generators | Mismodeled shape in the discriminant biases the limit |
| qq̄(γ) modeling | Compare generators (Pythia, Herwig, KK2f) for 2-fermion backgrounds | Fragmentation and hadronization differences affect jet multiplicity and event shapes |
| MC statistics | Barlow-Beeston (one NP per bin to absorb MC statistical uncertainty) or equivalent bin-by-bin MC stat terms | Finite MC sample size adds uncertainty to template shapes |

### Detector and reconstruction

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Detector simulation model | Compare data and MC for key observables; propagate data/MC differences | Detector response modeling (tracking efficiency, calorimeter resolution) directly affects acceptance and shape |
| Object calibration | Energy scale, resolution, efficiency scale factors for each object type | Affect both signal acceptance and background shape |
| Beam energy | Vary within the LEP energy calibration uncertainty | Affects reconstructed mass, cross-section normalization, and kinematic endpoint positions |
| Luminosity | Vary within the small-angle Bhabha counting uncertainty | Normalizes all simulation-based predictions |

### Theory inputs

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| QCD scale variations | Independent muR, muF variation | Probes missing higher-order terms in signal and background cross-sections |
| Fragmentation model | Alternative generators (string vs. cluster hadronization) | Affects jet properties, b-tagging performance, and event shape distributions |
| Heavy flavour treatment | Vary b-quark mass, fragmentation function | Relevant when the search involves b-tagged final states |

---

## Required validation checks

1. **Closure tests in validation regions.** Predict VR yields from CR
   extrapolation and compare to data. A closure test passes at p > 0.05
   (chi2-based). Failure is Category A — fix the background model before
   proceeding.

2. **Signal injection and recovery.** Inject signal at known strengths into
   pseudo-data and verify the fit recovers them. Report the injected vs.
   fitted signal strength for each injection point. Bias > 20% at any
   injection point requires investigation.

3. **Nuisance parameter pulls and constraints.** Post-fit nuisance parameter
   values should be within +/-1 sigma of their pre-fit values. Any pull
   > 2 sigma indicates the data is constraining a nuisance beyond its
   prior — investigate whether the prior is too loose or the model is
   absorbing a real effect.

4. **Impact ranking.** Rank nuisance parameters by their impact on the
   signal strength (or limit). The top-ranked parameters should correspond
   to physically expected dominant uncertainties. If a minor systematic
   ranks unexpectedly high, investigate.

5. **Goodness-of-fit.** Report chi2/ndf in each region (SR, CRs, VRs) and
   a toy-based p-value for the combined fit. Acceptable: p > 0.05.

6. **Look-elsewhere effect (for bump hunts).** If the signal mass or
   location is not fixed a priori, report both the local and global
   significance. The global significance accounts for the trials factor
   from scanning over the mass range.

---

## Pitfalls

- **Ignoring the look-elsewhere effect.** A 3-sigma local excess in a scan
  over a wide mass range may be < 2 sigma globally. Always report both.
  For fixed-mass searches (mass predicted by theory), the local significance
  is the relevant one — state this explicitly.

- **Optimizing cuts on observed data.** Selection optimization must use
  expected sensitivity (MC-based S/sqrt(B) or equivalent), never observed
  data in the signal region. Optimizing on data biases the result.

- **Blind spot in VR coverage.** Validation regions must cover the
  kinematic interpolation between CRs and SR. If the VRs are kinematically
  distant from the SR, closure there does not validate the extrapolation.
  Document the VR placement relative to both CR and SR.

- **Transfer factor instability.** If the background transfer factor
  (CR→SR extrapolation ratio) varies steeply as a function of a kinematic
  variable, small mismodeling produces large SR prediction errors. Check
  the transfer factor as a function of key variables and flag regions of
  instability.

- **Pruning too aggressively.** Removing systematic sources that are "small"
  individually can collectively bias the limit. When pruning, verify that
  the total pruned impact (summed in quadrature) is < 5% of the dominant
  systematic.

- **Asymptotic approximation with low statistics.** If any SR bin has
  fewer than ~5 expected events, the asymptotic approximation for the
  test statistic distribution may not hold. Validate against toy-based
  limits or use toys directly.

---

## References

- The CLs method: Read, A.L., "Presentation of search results: the CLs
  technique" (J. Phys. G: Nucl. Part. Phys. 28, 2693, 2002).
- Asymptotic formulas: Cowan, Cranmer, Gross, Vitells, "Asymptotic
  formulae for likelihood-based tests of new physics" (Eur. Phys. J. C71,
  1554, 2011; erratum 2013). INSPIRE: Cowan:2010js.
- pyhf: Heinrich, Feickert, Schreiner, "pyhf: pure-Python implementation
  of HistFactory statistical models" (JOSS 6, 2823, 2021).
- Look-elsewhere effect: Gross, Vitells, "Trial factors for the look
  elsewhere effect in high energy physics" (Eur. Phys. J. C70, 525, 2010).
  INSPIRE: Gross:2010qma.
