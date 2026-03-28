## Appendix D: Plotting Template

All plotting code must follow this template. This is the reference for any
agent producing figures — whether the executor itself or a dedicated plotting
subagent.

### Base template

```python
import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np

np.random.seed(42)
mh.style.use("CMS")

# --- Single plot ---
fig, ax = plt.subplots(figsize=(10, 10))
# For MxN subplots, scale to keep ratio: 2x2 -> (20, 20), 1x3 -> (30, 10)

# --- Ratio plot ---
# fig, (ax, rax) = plt.subplots(
#     2, 1, figsize=(10, 10),
#     gridspec_kw={"height_ratios": [3, 1]},
#     sharex=True,
# )
# fig.subplots_adjust(hspace=0)  # REQUIRED — no gap between main and ratio

# --- Your plotting code ---

# For histograms: mh.histplot(...)
# For 2D histograms — use hist2dplot with cbarextend to keep square aspect:
#   mh.hist2dplot(H, cbarextend=True)
#   OR for manual control:
#   im = ax.pcolormesh(...)
#   cax = mh.utils.make_square_add_cbar(ax)
#   fig.colorbar(im, cax=cax)
# For data/MC comparisons: use mh.histplot on subaxes with ratio panel

# --- Labels (required on EVERY axes in multi-panel figures) ---
mh.label.exp_label(
    exp="<EXPERIMENT>",  # MANDATORY — set to your experiment, e.g. "ALEPH", "CMS"
    text="",         # e.g. "Preliminary" (leave "" for final)
    loc=0,
    data=False,      # True when real data is used (suppresses "Simulation")
    year=None,       # e.g. "1992-1995"
    lumi=None,       # e.g. 160 (in pb^-1 or fb^-1)
    lumi_format="{0}",
    com=None,        # centre-of-mass energy — NOTE: CMS style prints "TeV",
                     # so for non-LHC experiments use rlabel instead, e.g.
                     # rlabel=r"$\sqrt{s} = 91.2$ GeV"
    llabel=None,     # Overwrites left side (after exp). NOTE: when data=False,
                     # "Simulation" is auto-added. If you set llabel, also set
                     # text="" to avoid "Simulation" + llabel stacking.
    rlabel=None,     # Overwrites right side — use for custom annotations
    ax=ax,
)

fig.savefig("output.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("output.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
```

### Rules

- **Style:** Always `mh.style.use("CMS")` as the base. Experiment branding
  comes from `exp_label`, not the style.
- **Font sizes are LOCKED.** Do not pass absolute numeric `fontsize=` values
  to ANY matplotlib call (`set_xlabel`, `set_ylabel`, `set_title`,
  `tick_params`, `annotate`, `text`). The CMS stylesheet sets all font sizes
  correctly for the 10x10 figure size. Relative string sizes (`'small'`,
  `'x-small'`, `'xx-small'`) are allowed where needed (e.g., dense legends,
  annotation text). Any script that sets a numeric font size is a Category A
  review finding.
- **Legend font size.** Always pass `fontsize="x-small"` to `ax.legend(...)`.
- **Aspect.** Keep figures with square aspect. For 2D plots with colorbars,
  you MUST use one of these to prevent the colorbar from squashing the plot:
  - `mh.hist2dplot(H, cbarextend=True)` — preferred, handles it automatically
  - `cax = mh.utils.make_square_add_cbar(ax)` then `fig.colorbar(im, cax=cax)`
  - `cax = mh.utils.append_axes(ax, extend=True)` then `fig.colorbar(im, cax=cax)`
  Never just do `fig.colorbar(im)`, `fig.colorbar(im, ax=ax, shrink=...)`,
  or `plt.colorbar()` — these steal space from the axes and break the
  square aspect.
- **No titles.** Never `ax.set_title()`. Captions go in the analysis note.
  Instead additional info can go into `ax.legend(title="...")`. And when
  truly necessary it can go into `mh.utils.add_text(text, ax=ax)`.
- **No raw `ax.text()` or `ax.annotate()`.** Use `mh.utils.add_text(text,
  ax=ax)` for all text annotations — it respects mplhep styling and
  positioning. This includes panel labels like `(a)`, `(b)` in grids.
- **Axis labels with units.** Always `ax.set_xlabel(...)` and
  `ax.set_ylabel(...)` with units in brackets, e.g. `r"$p_T$ [GeV]"`.
  Do not increase axis label font size beyond the stylesheet default — no
  `fontsize=` argument on `set_xlabel`/`set_ylabel`.
- **Labels on every axes.** In multi-panel figures, call
  `mh.label.exp_label(...)` on EACH axes, not just the first one.
- **Label stacking pitfall (Category A).** When `data=False`, mplhep
  auto-adds "Simulation" as the left label. Do NOT also set `llabel` or
  `text` to something containing "MC", "Simulation", "truth", etc. — this
  produces mangled labels like "Simulation MC truth". The rules:
  - For simulation plots: `data=False` alone → displays "Simulation"
  - For data plots: `data=True` alone → displays nothing (or "Preliminary")
  - For full control: `data=True, llabel="your text"` to override entirely
  - Never combine `data=False` with `llabel` or `text` — this always stacks
- **Save as PDF and PNG.** PDF for the note, PNG for quick inspection.
  Always `bbox_inches="tight", dpi=200, transparent=True`.
- **Never use `tight_layout()` or `constrained_layout=True` with mplhep.**
  They conflict with mplhep's label positioning. Use `bbox_inches="tight"`
  at save time instead — this handles clipping without breaking the layout.
- **Close figures.** `plt.close(fig)` after saving to prevent memory leaks
  in long scripts.
- **Figure size is LOCKED at `figsize=(10, 10)`.** Do not use any other
  figure size. This is non-negotiable — the font sizes in the CMS stylesheet
  are calibrated for this size. Using `figsize=(8, 6)` or `figsize=(12, 8)`
  produces figures where text is too large or too small relative to the plot
  elements. For ratio plots, use `figsize=(10, 10)` with
  `height_ratios=[3, 1]`. For 2×2 subplots, use `figsize=(20, 20)`. The
  rule is: 10 inches per subplot column, 10 inches per subplot row.
  **Any script that uses a custom figsize is a Category A review finding.**
- **PDF rendering size.** Single figures are rendered at `0.45\linewidth`
  in the compiled analysis note PDF. Grid/multi-panel figures use
  `\linewidth` (full width). The 10x10 matplotlib figure size produces
  clean, readable plots at `0.45\linewidth`. The default in the pandoc
  preamble is `0.45\linewidth`; override with pandoc-crossref attributes
  when a figure genuinely needs full width (e.g., large correlation
  matrices, multi-panel comparisons).
- **Ratio plot hspace.** `fig.subplots_adjust(hspace=0)` is non-negotiable
  for ratio plots. Any visible gap between the main panel and ratio panel
  is a Category A review finding.
- **Log scale.** Use `ax.set_yscale("log")` when the y-axis range spans
  more than 2 orders of magnitude. Linear scale is appropriate otherwise.
- **Prefer mplhep functions** (`mh.histplot`, `mh.hist2dplot`) over raw
  matplotlib `ax.hist` / `ax.pcolormesh`. They handle binning, styling,
  and error bars correctly for HEP conventions.
- **Deterministic.** `np.random.seed(42)` if any randomness is involved.

### Error propagation for derived quantities

When plotting derived quantities (ratios, normalized distributions,
efficiencies), uncertainties must be propagated manually — matplotlib does
not do this automatically.

**Common formulas:**
- **Normalized distribution** `(1/N) dN/dx`: `yerr[i] = sqrt(n[i]) / (N * dx[i])` where `N = sum(n)` and `dx[i]` is the bin width. For Poisson counts, `sqrt(n[i])` is the per-bin uncertainty.
- **Ratio** `R = A/B`: `sigma_R = R * sqrt((sigma_A/A)^2 + (sigma_B/B)^2)` (uncorrelated errors)
- **Efficiency** `ε = k/n`: use Clopper-Pearson (binomial) intervals, not Gaussian propagation. `scipy.stats.binom` provides these.
- **Bin-width-normalized** `dN/dx`: `yerr[i] = sqrt(n[i]) / dx[i]`

Always pass `yerr=` explicitly to `mh.histplot()` or `ax.errorbar()` for
derived quantities. `mh.histplot` auto-errors are only correct for raw event
counts or weighted histograms — NOT for `(1/N) dN/dx`, ratios, efficiencies,
or other post-processed quantities. Relying on auto-errors for derived
quantities is a Category A review finding.

### Captions

See §5.2 for caption requirements. Captions must be self-contained: state
what is plotted, identify all curves/markers/bands, and state the key
conclusion. Sparse captions are Category A.

### Subfigures and figure grouping

Group related figures into grids rather than presenting them as separate
figures. Use letter labels (`(a)`, `(b)`, etc.) with
`mh.utils.add_text("(a)", ax=ax)` in each panel.
Write a single caption describing all sub-panels. This keeps the note
compact and makes comparisons easier for the reader.

**Grid sizing:** Selection cut distributions can be grouped into a 3×3 grid
with a single caption. Related comparisons (e.g., data/MC for multiple
variables) should be side-by-side. A 2×2 grid uses `figsize=(20, 20)`, a
3×3 uses `figsize=(30, 30)` — following the 10-inches-per-subplot rule.

### Figure cross-referencing

Use pandoc-crossref syntax for numbered figure references in analysis notes:

- **Label every figure:** `![Caption text](figures/name.pdf){#fig:name}`
- **Reference figures:** `@fig:name` (produces "fig. X")
- **At sentence start:** `Figure @fig:name` (capitalized)
- **Never use** `[-@fig:...]` — always use `@fig:name` for full references
- Tables use `{#tbl:name}` and `@tbl:name`; equations use `{#eq:name}` and
  `@eq:name`

### Correlation and covariance visualizations

Correlations between variables, bins, or systematic sources must be shown
as **matrix heatmaps** (using `mh.hist2dplot` or `ax.pcolormesh` with a
diverging colormap like `RdBu_r`, centered at 0 for correlations). Never
show correlations as overlaid 1D distributions or scatter-plot grids —
these are unreadable for more than ~3 variables. For the correlation
matrix specifically:
- Use `vmin=-1, vmax=1` with a diverging colormap
- Annotate cells with values if the matrix is small enough (< 10×10)
- For large matrices, show the heatmap without annotations but with a
  clear colorbar

### Systematic breakdown plots

When a systematic breakdown shows any single source with relative uncertainty
>100% in a bin, investigate — this typically indicates a bug in the variation
processing or an edge effect in a low-stats bin. Clip or flag such bins rather
than letting them dominate the y-axis scale. If the large variation is genuine
(e.g., a very low-stats bin), document the explanation in the artifact.

### Delegation to plotting subagent

Plotting should be delegated to a dedicated subagent. When
spawning a plotting subagent, the parent agent must include in the prompt:

1. **This entire appendix** (copy the template and rules above into the
   subagent prompt so it has the style reference in context)
2. The data to plot (file paths or serialized arrays)
3. What kind of plot (histogram, ratio, 2D, overlay)
4. Axis labels and ranges
5. The experiment label parameters (exp, com, lumi, data flag)
6. Output path

The plotting agent applies this template and produces the figure. It does not
make physics decisions about what to plot or how to interpret the result.
