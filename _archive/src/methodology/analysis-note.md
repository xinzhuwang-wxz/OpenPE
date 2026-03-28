## Analysis Note Specification

The AN is a single evolving document across Phases 4b, 4c, and 5. Phase 4b
creates the complete AN with 10% results. Phase 4c updates numbers to
full-data results. Phase 5 polishes prose, adds final comparisons, and
renders the PDF. The structure, systematic descriptions, cross-checks, and
appendices are all written in 4b — later phases update results, not
structure.

---

### What an analysis note is

The AN is the complete, permanent record of the analysis — not a journal
paper. A journal publication is a distilled summary; the AN is the full
story. It must contain every detail a physicist needs to reproduce the
analysis from scratch using only the note and the data: every selection cut
and its motivation, every systematic variation and how it was evaluated,
every cross-check and its outcome, every correction and how it was derived.
ANs in real collaborations routinely reach 100–200+ pages. Length is not a
goal in itself, but completeness is — and completeness at this level of
detail requires substantial length. **Err on the side of too much detail,
not too little.** A reviewer who has to ask "but how exactly did you do X?"
has found a gap.

---

### Required sections

1. **Introduction** — Physics motivation, observable definition, theoretical
   context (perturbative order, resummation, non-perturbative effects where
   relevant). Prior measurements of the same or related observables with
   citations.

2. **Data samples** — Complete inventory: experiment, √s, integrated
   luminosity or event counts, data-taking periods, file-level details.
   For MC: generator, tune, cross-section, number of generated events,
   filter efficiency.

3. **Event selection** — Every cut listed with:
   - The physical motivation (why this cut exists)
   - The distribution of the cut variable, showing the effect of the cut
   - The numerical efficiency (per-cut and cumulative)
   - Sensitivity studies: what happens when the cut is varied or removed

4. **Corrections / unfolding** (for measurements) — Full description of the
   correction procedure: what is being corrected for, how corrections are
   derived, validation of the correction method (closure tests, stress
   tests). For unfolding: response matrix, regularization, number of
   iterations, convergence checks.

5. **Systematic uncertainties** — One subsection per source, each
   containing:
   - What the source is and why it affects the result
   - How the variation was evaluated (up/down shifts, alternative samples,
     reweighting, etc.)
   - The impact on the final result (table + figure showing the variation)
   - For literature-derived systematics: the source, its applicability,
     and any inflation applied
   - Summary table of all sources with per-bin or integrated impacts
   - Correlation information: which sources are correlated across bins,
     regions, or processes

6. **Cross-checks** — Each cross-check appears as a subsection within the
   section it validates (e.g., a BDT cross-check in the selection section,
   an alternative fit in the statistical method section). **Do not create a
   standalone "Cross-checks" section** — it disconnects the check from its
   context. If a cross-check is large (>2 pages), move it to an appendix
   with a forward reference. Each cross-check subsection must include:
   - What is being tested and what a failure would indicate
   - The quantitative result (ratio plots, chi2, p-values)
   - Interpretation: does it pass? If marginal, why?
   - Examples: year-by-year or run-period stability, subdetector
     comparisons, charged-only vs. full, alternative selections,
     alternative correction methods, kinematic subsamples, generator
     comparisons

7. **Statistical method** — For searches: likelihood construction, nuisance
   parameter treatment, test statistic, CLs or frequentist/Bayesian
   procedure. For measurements: bin-by-bin vs. unfolded, normalization,
   uncertainty propagation. In either case: fit validation, signal injection
   or closure tests, goodness-of-fit.

8. **Results** — The primary result with full uncertainties (stat + syst
   breakdown). Tables with per-bin values. Summary figures. For
   measurements: the corrected spectrum, moments or extracted parameters.
   For searches: observed and expected limits/significance.

9. **Comparison to prior results and theory** — If published measurements
   exist: overlay plots with ratio panels, chi2/p-value using the full
   covariance matrix. If theory predictions exist: overlay and quantitative
   comparison. **"Qualitative consistency" is insufficient when data points
   are available.** If no prior measurement exists, state this explicitly.

10. **Conclusions** — Summary of the result, its precision, the dominant
    limitations, and the physics interpretation.

11. **Future directions** — Concrete roadmap per Section 12.7.

12. **Appendices** — Supporting material that would interrupt the main flow:
    full systematic tables per bin, auxiliary distributions, extended cutflow
    tables, full correlation/covariance matrices, additional cross-checks.
    Appendices are not optional padding — they are where the bulk of the
    detail lives. A 10-page main text with 150 pages of appendices is a
    normal AN structure.

---

### Additional requirements

- All quantitative results must be inline — the document must be
  self-contained
- Figures must be publication-quality (see `appendix-plotting.md`)
- All citations must reference published literature with proper identifiers
- **Machine-readable results:** All tabulated results (spectra,
  uncertainties, covariance matrices) must also be provided in a
  machine-readable format (CSV, JSON, or YAML) in a `results/` directory
  alongside the note. Results that exist only inside a PDF are not reusable.

---

### Completeness test

A physicist unfamiliar with the analysis should be able to read the AN
alone — without access to code, experiment logs, or phase artifacts — and
understand every choice that was made, reproduce every number in the
results, and evaluate whether the conclusions are supported. If a choice
requires reading the code to understand, the AN has a gap.

---

### Depth calibration

The AN is not a summary — it is the complete record. Concrete minimum
expectations:

- **Systematics section:** One subsection per source. A summary table alone
  is insufficient. Each source gets: description, method, impact figure,
  per-bin table. If the analysis has 5 systematic sources, there are 5
  subsections plus a summary.
- **Cross-checks:** One subsection per cross-check, placed in the section
  it validates. "Bin-by-bin cross-check confirms the result" is a one-liner,
  not a subsection. A subsection shows the comparison plot, states the chi2,
  and interprets the level of agreement.
- **Event selection:** Every cut gets its own paragraph with a figure
  reference showing the distribution before and after the cut. A two-row
  cutflow table ("before" and "after all cuts") is not a cutflow — it must
  show each cut individually with per-cut and cumulative efficiencies.
- **Appendices:** Full per-bin systematic tables, covariance/correlation
  matrices (as tables, not just figures), extended cutflow, auxiliary
  distributions. The appendices will typically be longer than the main text.

As a rough calibration: a measurement analysis with 5 systematic sources,
3 cross-checks, 6 selection cuts, and 18 result bins should produce an AN
of approximately 50–100 pages when rendered. If the AN is under 30 rendered
pages, it is almost certainly missing required detail.

---

### Bibliography

Citations use pandoc's `[@key]` syntax with a `references.bib` BibTeX file
in the analysis note directory. Populate `references.bib` as sources are
cited — every retrieved paper, every published measurement used for
comparison, every theory prediction. The `build-pdf` task includes
`--citeproc` to process citations automatically.

BibTeX entries must include `doi`, `url` (journal or arXiv link), and
`eprint` (arXiv ID) fields where available. Use `unsrt`-style formatting
as a reference. When citing a paper discovered via RAG, use `get_paper` to
retrieve its metadata and construct a proper BibTeX entry with the INSPIRE
key. Never cite as bare INSPIRE IDs (e.g., `inspire:123456`) — always use
proper bibliography entries with `[@key]` syntax.

---

### LaTeX compilation

The working format during development is markdown. Conversion to PDF uses
**pandoc** (≥3.0, installed via pixi as a conda-forge dependency) with
pdflatex as the PDF engine. This is a programmatic step — do not use an
LLM agent to convert markdown to LaTeX manually. The `build_pdf.py` script
in the analysis's `phase5_documentation/exec/` directory handles the
conversion, including:
- Collecting referenced figures into a local `figures/` directory (symlinks)
- Converting inline figure references to markdown image syntax
- Setting default figure width to `0.5\textwidth` for half-page-width
  figures
- Running `pandoc → PDF` with `--number-sections --toc`

The compiled PDF is a deliverable.

---
