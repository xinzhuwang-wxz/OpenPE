## Appendix D: Plotting Standards

All plotting code must follow these standards. This is the reference for
any agent producing figures — whether the executor itself or a dedicated
plotting subagent.

### Base template

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)

# --- OpenPE default style ---
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# --- Single plot ---
fig, ax = plt.subplots(figsize=(8, 6))
# For MxN subplots, scale proportionally: 2x2 -> (14, 12), 1x3 -> (18, 6)

# --- Comparison plot with residual panel ---
# fig, (ax, rax) = plt.subplots(
#     2, 1, figsize=(8, 8),
#     gridspec_kw={"height_ratios": [3, 1]},
#     sharex=True,
# )
# fig.subplots_adjust(hspace=0.05)  # minimal gap between panels

# --- Your plotting code ---

# --- Labels (required on EVERY axes) ---
ax.set_xlabel("Variable [unit]")
ax.set_ylabel("Count / bin width")

# --- Source annotation (top-left, small) ---
ax.text(0.02, 0.98, "OpenPE Analysis",
        transform=ax.transAxes, fontsize=8, va="top", ha="left",
        color="gray", style="italic")

fig.savefig("output.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig("output.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
```

### Rules

- **Style:** Use the rcParams block above as the base. No experiment
  branding, no third-party style sheets. The style is intentionally
  minimal and domain-agnostic.
- **Font sizes are set by rcParams.** Do not override font sizes with
  absolute numeric `fontsize=` values except where explicitly needed
  (e.g., small annotations). The rcParams above are calibrated for the
  default figure size. Any script that overrides axis label or tick font
  sizes is a Category A review finding.
- **Legend font size.** Use the rcParams default (10pt). For dense legends,
  `fontsize="small"` or `fontsize="x-small"` is acceptable.
- **Clean spines.** Top and right spines are removed by default. This is
  the OpenPE standard — do not re-enable them unless the plot requires a
  closed frame (e.g., heatmaps).
- **No titles.** Never `ax.set_title()`. Captions go in the analysis
  report. Additional info can go into `ax.legend(title="...")` or a
  small text annotation.
- **Axis labels with units.** Always `ax.set_xlabel(...)` and
  `ax.set_ylabel(...)` with units in brackets, e.g., `"GDP growth [%]"`,
  `"Unemployment rate [pp]"`.
- **Save as PDF and PNG.** PDF for the report, PNG for quick inspection.
  Always `bbox_inches="tight", dpi=200, transparent=True`.
- **Close figures.** `plt.close(fig)` after saving to prevent memory leaks
  in long scripts.
- **Figure sizing.** Default single plot: `figsize=(8, 6)`. Scale
  proportionally for multi-panel layouts. The rcParams font sizes are
  calibrated for this default.
- **PDF rendering size.** Single figures are rendered at `0.5\linewidth`
  in the compiled report PDF. Multi-panel figures use `\linewidth` (full
  width). Override with pandoc-crossref attributes when a figure genuinely
  needs a different width.
- **Residual panel hspace.** `fig.subplots_adjust(hspace=0.05)` for
  comparison plots with residual panels. A large gap between main and
  residual panels is a Category A review finding.
- **Log scale.** Use `ax.set_yscale("log")` when the y-axis range spans
  more than 2 orders of magnitude.
- **Deterministic.** `np.random.seed(42)` if any randomness is involved.

### EP Decay Chart Template

The EP decay chart is the core OpenPE visualization. It shows how
epistemic probability evolves across phases for each sub-question.

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_ep_decay(ep_trajectory, sub_questions, thresholds, output_path):
    """
    Plot EP decay across phases.

    Parameters
    ----------
    ep_trajectory : dict
        {sub_question_id: [ep_phase0, ep_phase1, ..., ep_phase6]}
    sub_questions : dict
        {sub_question_id: "Human-readable label"}
    thresholds : dict
        {"high_confidence": 0.85, "reportable": 0.70, "speculative": 0.50}
    output_path : str
        Path to save the figure (without extension).
    """
    phases = ["P0\nDiscovery", "P1\nStrategy", "P2\nExplore",
              "P3\nAnalysis", "P4\nProject", "P5\nVerify", "P6\nDoc"]
    x = np.arange(len(phases))

    fig, ax = plt.subplots(figsize=(10, 6))

    # Threshold bands
    ax.axhspan(thresholds["high_confidence"], 1.0,
               alpha=0.08, color="green", label="High confidence")
    ax.axhspan(thresholds["reportable"], thresholds["high_confidence"],
               alpha=0.08, color="blue", label="Reportable")
    ax.axhspan(thresholds["speculative"], thresholds["reportable"],
               alpha=0.08, color="orange", label="Speculative zone")
    ax.axhspan(0, thresholds["speculative"],
               alpha=0.08, color="red", label="Below threshold")

    # EP trajectories
    for sq_id, ep_values in ep_trajectory.items():
        label = sub_questions.get(sq_id, sq_id)
        ax.plot(x[:len(ep_values)], ep_values, "o-", linewidth=2,
                markersize=6, label=label)

    ax.set_xticks(x)
    ax.set_xticklabels(phases)
    ax.set_ylabel("Epistemic Probability (EP)")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize="small", loc="lower left")
    ax.text(0.02, 0.98, "EP Decay Chart",
            transform=ax.transAxes, fontsize=8, va="top", ha="left",
            color="gray", style="italic")

    fig.savefig(f"{output_path}.pdf", bbox_inches="tight",
                dpi=200, transparent=True)
    fig.savefig(f"{output_path}.png", bbox_inches="tight",
                dpi=200, transparent=True)
    plt.close(fig)
```

### Scenario Comparison Chart Template

For forecasting and projection analyses, compare outcomes across scenarios.

```python
def plot_scenario_comparison(scenarios, output_path):
    """
    Plot scenario comparison with uncertainty bands.

    Parameters
    ----------
    scenarios : dict
        {scenario_name: {"x": array, "y": array, "ci_lo": array,
                         "ci_hi": array}}
    output_path : str
    """
    colors = {"baseline": "#2196F3", "optimistic": "#4CAF50",
              "pessimistic": "#F44336", "stress": "#FF9800"}

    fig, ax = plt.subplots(figsize=(10, 6))

    for name, data in scenarios.items():
        color = colors.get(name, "gray")
        ax.plot(data["x"], data["y"], "-", color=color, linewidth=2,
                label=name.capitalize())
        ax.fill_between(data["x"], data["ci_lo"], data["ci_hi"],
                        alpha=0.15, color=color)

    ax.set_xlabel("Time")
    ax.set_ylabel("Outcome [unit]")
    ax.legend(fontsize="small")
    ax.text(0.02, 0.98, "Scenario Comparison",
            transform=ax.transAxes, fontsize=8, va="top", ha="left",
            color="gray", style="italic")

    fig.savefig(f"{output_path}.pdf", bbox_inches="tight",
                dpi=200, transparent=True)
    fig.savefig(f"{output_path}.png", bbox_inches="tight",
                dpi=200, transparent=True)
    plt.close(fig)
```

### Sensitivity Tornado Chart Template

Visualize which assumptions or parameters drive the largest variation
in findings.

```python
def plot_tornado(sensitivities, finding_label, output_path):
    """
    Plot sensitivity tornado chart.

    Parameters
    ----------
    sensitivities : list of dict
        [{"parameter": str, "low": float, "high": float, "baseline": float}]
        Sorted by total range (largest first).
    finding_label : str
        Label for the x-axis (the finding being varied).
    output_path : str
    """
    fig, ax = plt.subplots(figsize=(8, max(4, len(sensitivities) * 0.5 + 1)))

    params = [s["parameter"] for s in sensitivities]
    baseline = sensitivities[0]["baseline"]
    y_pos = np.arange(len(params))

    for i, s in enumerate(sensitivities):
        low_delta = s["low"] - baseline
        high_delta = s["high"] - baseline
        ax.barh(i, high_delta, left=baseline, height=0.6,
                color="#2196F3", alpha=0.7)
        ax.barh(i, low_delta, left=baseline, height=0.6,
                color="#F44336", alpha=0.7)

    ax.axvline(baseline, color="black", linewidth=1, linestyle="--",
               label=f"Baseline: {baseline:.3f}")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(params)
    ax.set_xlabel(finding_label)
    ax.legend(fontsize="small")
    ax.text(0.02, 0.98, "Sensitivity Analysis",
            transform=ax.transAxes, fontsize=8, va="top", ha="left",
            color="gray", style="italic")

    fig.savefig(f"{output_path}.pdf", bbox_inches="tight",
                dpi=200, transparent=True)
    fig.savefig(f"{output_path}.png", bbox_inches="tight",
                dpi=200, transparent=True)
    plt.close(fig)
```

### Error propagation for derived quantities

When plotting derived quantities (ratios, normalized distributions,
rates), uncertainties must be propagated manually — matplotlib does
not do this automatically.

**Common formulas:**
- **Normalized distribution** `(1/N) dN/dx`: `yerr[i] = sqrt(n[i]) / (N * dx[i])` where `N = sum(n)` and `dx[i]` is the bin width.
- **Ratio** `R = A/B`: `sigma_R = R * sqrt((sigma_A/A)^2 + (sigma_B/B)^2)` (uncorrelated errors)
- **Rate / proportion** `p = k/n`: use Clopper-Pearson (binomial) intervals, not Gaussian propagation. `scipy.stats.binom` provides these.
- **Bin-width-normalized** `dN/dx`: `yerr[i] = sqrt(n[i]) / dx[i]`
- **Difference of means**: `sigma_diff = sqrt(sigma_A^2 + sigma_B^2)` (independent samples)
- **Bootstrap**: For complex statistics, use `scipy.stats.bootstrap` with `n_resamples=10000` and pinned `random_state=42`.

Always pass `yerr=` explicitly for derived quantities. Auto-errors are
only correct for raw counts — NOT for rates, ratios, normalized
distributions, or other post-processed quantities. Relying on auto-errors
for derived quantities is a Category A review finding.

### Captions

See §5.2 for caption requirements. Captions must be self-contained: state
what is plotted, identify all curves/markers/bands, and state the key
conclusion. Sparse captions are Category A.

### Subfigures and figure grouping

Group related figures into grids rather than presenting them as separate
figures. Use letter labels (`(a)`, `(b)`, etc.) with `ax.text()` in each
panel. Write a single caption describing all sub-panels. This keeps the
report compact and makes comparisons easier for the reader.

**Grid sizing:** Related comparisons (e.g., results across countries or
time periods) should be side-by-side. A 2x2 grid uses `figsize=(14, 12)`,
a 3x3 uses `figsize=(18, 18)` — scaling proportionally from the base.

### Figure cross-referencing

Use pandoc-crossref syntax for numbered figure references in reports:

- **Label every figure:** `![Caption text](figures/name.pdf){#fig:name}`
- **Reference figures:** `@fig:name` (produces "fig. X")
- **At sentence start:** `Figure @fig:name` (capitalized)
- Tables use `{#tbl:name}` and `@tbl:name`; equations use `{#eq:name}`
  and `@eq:name`

### Correlation and covariance visualizations

Correlations between variables must be shown as **matrix heatmaps**
(using `ax.pcolormesh` with a diverging colormap like `RdBu_r`, centered
at 0 for correlations). Never show correlations as overlaid 1D
distributions or scatter-plot grids — these are unreadable for more than
~3 variables. For the correlation matrix specifically:
- Use `vmin=-1, vmax=1` with a diverging colormap
- Annotate cells with values if the matrix is small enough (< 10x10)
- For large matrices, show the heatmap without annotations but with a
  clear colorbar

### Delegation to plotting subagent

Plotting should be delegated to a dedicated subagent. When spawning a
plotting subagent, the parent agent must include in the prompt:

1. **This entire appendix** (copy the template and rules above into the
   subagent prompt so it has the style reference in context)
2. The data to plot (file paths or serialized arrays)
3. What kind of plot (EP decay, scenario comparison, tornado, histogram,
   scatter, time series)
4. Axis labels and ranges
5. Output path

The plotting agent applies these standards and produces the figure. It
does not make analytical decisions about what to plot or how to interpret
the result.
