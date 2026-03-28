# Unfolding Measurements

Conventions for analyses that correct a measured distribution for detector
effects to produce a particle-level result.

## When this applies

Any analysis that constructs a response matrix from simulation and applies a
correction procedure (IBU, SVD, TUnfold, OmniFold, bin-by-bin correction
factors) to transform a detector-level distribution into a particle-level
result.

---

## Particle-level definition

Before anything else, define the particle-level target precisely:

- What particles are included (stable hadrons, charged-only, with/without
  neutrinos, etc.)
- What phase space (fiducial vs. full, any particle-level cuts)
- Treatment of ISR/FSR photons
- Treatment of hadron decays (lifetime threshold, e.g. c*tau > 10 mm)

This definition determines what the measurement *means*. It must be stated
in the strategy phase and held fixed throughout. Changing it invalidates the
response matrix.

---

## Response matrix construction

### Input validation

Before building the response matrix, validate the MC model that will be used
to construct it. Produce data/MC comparisons for all kinematic variables that
enter the observable calculation, resolved by reconstructed object category.

Rationale: the response matrix encodes the detector's effect on the
observable. If the MC mismodels the inputs to the observable, the response
matrix is wrong. Observable-level data/MC agreement can mask compensating
category-level mismodeling.

Required deliverables before proceeding:
- Per-category kinematic distributions with data/MC ratio panels
- Quantitative summary of agreement level
- Documentation of identified discrepancies and expected impact

### Matrix properties to report

- Dimension (N_reco x N_gen bins)
- Diagonal fraction (fraction of events staying in the same bin)
- Column normalization (should sum to 1 if properly constructed)
- Condition number (if matrix inversion is involved)
- Efficiency as a function of the particle-level observable

---

## Regularization and iteration

### Choosing the regularization strength

For iterative methods (IBU), the number of iterations is the regularization
parameter. For matrix methods (SVD), it's the number of kept singular values
or a Tikhonov parameter.

The selection criterion should be:
1. Closure test passes (unfolding MC truth through the response recovers
   the truth within statistical precision)
2. Stress test passes (unfolding a reweighted truth through the response
   recovers the reweighted truth)
3. Stable plateau (result does not change significantly with small changes
   in regularization)

**Additionally:** verify that the result is not prior-dominated in any bin.
Repeat the unfolding with a flat (uniform) prior at the nominal
regularization. If any bin's corrected value changes by more than 20%
relative (i.e., |flat − nominal| / nominal > 0.20), the regularization is
insufficient for that bin — increase iterations, merge bins, or exclude
the bin.

Rationale: closure and stress tests use the correct (or nearly correct)
prior. They can pass even when the regularization is too weak to overcome a
wrong prior. The flat-prior test exposes this.

### Reporting

- State the nominal regularization choice and the criterion used
- Show closure chi2/ndf and stress chi2/ndf vs. regularization strength
- Show the flat-prior sensitivity per bin
- Include the regularization variation in the systematic budget

---

## Required systematic sources

These are the standard sources for an unfolded measurement. Omitting any
of them requires explicit justification.

### Detector and reconstruction

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Object-level response | Scale/smear/remove reconstructed objects by category (tracking, calorimetry, etc.) | Probes detector modeling without redefining the observable |
| Selection cuts | Vary each event-level cut that has non-negligible rejection | Selection efficiency is part of the correction |
| Background contamination | Vary background normalization or removal | Residual backgrounds bias the measured spectrum |

### Unfolding method

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Regularization strength | Vary iterations or regularization parameter | Residual regularization bias |
| Prior dependence | Alternative priors (reweighted truth, flat) | Tests sensitivity to assumed shape |
| Alternative method | At least one independent unfolding method | Cross-check of the full procedure |

**BBB validity criterion:**
- Bin-by-bin (BBB) correction factors are a valid alternative method only
  when the response matrix diagonal fraction exceeds ~70% across the fit
  range.
- When diagonal fractions are lower (significant bin migrations), BBB is
  structurally incorrect — compute and report it as a cross-check, but
  exclude it from the systematic budget.
- In this regime, a proper alternative (SVD, TUnfold, or matrix inversion
  with regularization) is required for the method systematic.
- If no valid alternative is available, document this as a limitation.

### Generator model (hadronization / fragmentation)

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| Hadronization model | Compare generators with fundamentally different fragmentation models (e.g. string vs. cluster) | The response matrix depends on the particle-level model. Different hadronization produces different detector response. This is typically the dominant systematic for event-shape measurements. |

This is not optional for normalized shape measurements. Data-driven
reweighting of a single generator's response matrix is not a substitute —
it probes data/MC shape differences but not the fundamental dependence on
the fragmentation model.

If alternative generators with full detector simulation are unavailable,
reweighting at particle level is acceptable but must be documented as a
limitation.

### Theory inputs

| Source | What to vary | Rationale |
|--------|-------------|-----------|
| ISR treatment | Correct for ISR or define measurement as ISR-inclusive; document the choice | Affects the particle-level definition |
| Heavy flavor | Vary b-quark mass or fragmentation if the observable is sensitive | Flavor composition affects the response |

### Normalized vs. absolute measurements

Systematic sources that affect only the overall normalization (luminosity,
total cross-section, trigger efficiency) cancel in **normalized** shape
measurements (e.g., (1/N) dN/dx) but remain relevant for **absolute**
cross-sections (e.g., dσ/dx). When planning the systematic program, the
agent must identify which type of measurement is being performed and
include or exclude normalization-only sources accordingly. Document the
reasoning — a reviewer will check that normalization sources are not
silently omitted from an absolute measurement.

---

## Required validation checks

The tests below formalize the criteria from the Regularization and
Covariance sections as explicit pass/fail gates.

1. **Closure test (Category A if fails).** Unfold MC truth through the
   response matrix and verify recovery of the input truth distribution
   within statistical precision (chi2 p-value > 0.05). Failure indicates
   a problem in the response matrix or unfolding procedure.

2. **Stress test.** Unfold a reweighted MC truth (different shape from the
   nominal) through the nominal response matrix. The unfolded result should
   recover the reweighted truth. Failure indicates the method is sensitive
   to the assumed prior shape.

3. **Flat-prior test.** Repeat the unfolding with a uniform prior at the
   nominal regularization strength. If any bin changes by more than 20%
   relative to the nominal result, the regularization is too strong for
   that bin — increase iterations, merge bins, or exclude the bin.

4. **Alternative method cross-check.** Apply at least one independent
   unfolding method. Agreement validates the procedure; disagreement beyond
   the assigned method systematic requires investigation. (See BBB validity
   criterion in the systematic sources section.)

5. **Covariance matrix validation.** Verify positive semi-definiteness
   (all eigenvalues ≥ 0). Report the condition number; flag if > 10^10
   (numerically unstable inverse). Visualize the correlation matrix.

---

## Covariance matrix

### Construction

- Statistical covariance: from analytical propagation through the unfolding
  or from bootstrap/toy replicas
- Systematic covariances: outer product of shift vectors (fully correlated
  per source) is the standard approach. Template-based approximations
  (using statistical correlation structure for systematic components)
  should be documented as approximations.
- Total: sum of all components

### Validation

See Required validation check #5 above for the specific criteria
(eigenvalue check, condition number threshold, correlation visualization).

---

## Comparison to reference measurements

When comparing the unfolded result to a published measurement of the same
quantity:

- Use the full covariance matrix (not diagonal uncertainties only)
- Report chi2/ndf and the corresponding p-value
- If chi2/ndf > 1.5 with the full covariance, investigate the source of
  tension before proceeding. Document the investigation even if the cause
  is understood.
- For robust validation, generate toy pseudo-experiments from the reference
  measurement (sampling from its covariance) and compare the observed chi2
  to the toy distribution.

---

## Pitfalls

- **Bin 0 with zero diagonal.** If any bin has zero (or near-zero) diagonal
  response, the unfolded result for that bin is entirely model-dependent.
  Either merge it with a neighbor or exclude it.
- **Normalizing before unfolding.** Normalize after unfolding + efficiency
  correction, not before. Pre-normalization introduces bin-to-bin
  correlations that the response matrix doesn't model.
- **Data/MC ratio as "MC modeling" systematic.** Reweighting the response
  matrix by the reco-level data/MC ratio probes shape mismodeling but does
  not replace a genuine alternative-generator comparison. It's a useful
  cross-check, not a substitute.
- **Covariance condition number.** A very large condition number (>10^10)
  means the inverse is numerically unstable. Consider regularizing the
  covariance or restricting the chi2 calculation to a well-conditioned
  sub-matrix.

---

## References

- D'Agostini, G., "A multidimensional unfolding method based on Bayes'
  theorem" (Nucl. Instrum. Meth. A362, 487, 1995). The foundational paper
  for iterative Bayesian unfolding (IBU).
- Hoecker, A. and Kartvelishvili, V., "SVD approach to data unfolding"
  (Nucl. Instrum. Meth. A372, 469, 1996). INSPIRE: Hocker:1995kb.
  Singular value decomposition method with regularization.
- Schmitt, S., "TUnfold: an algorithm for correcting migration effects in
  high energy physics" (JINST 7, T10003, 2012). INSPIRE: Schmitt:2012kp.
  Tikhonov-regularized matrix inversion with L-curve optimization.
- Andreassen, A. et al., "OmniFold: A Method to Simultaneously Unfold All
  Observables" (Phys. Rev. Lett. 124, 182001, 2020). INSPIRE:
  Andreassen:2019cjw. Machine-learning-based unfolding.
- Cowan, G., "Statistical Data Analysis" (Oxford University Press, 1998).
  General reference for unfolding, regularization, and covariance
  propagation in HEP.
