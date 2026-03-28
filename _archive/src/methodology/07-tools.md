## 7. Tools and Paradigms

The agent uses standard HEP software. No bespoke analysis framework is
required, but the following tools and paradigms are preferred. This section
is maintained by the analysis team and reflects operational knowledge about
what works well in practice.

### 7.1 Preferred Tools

| Capability | Tool | Notes |
|-----------|------|-------|
| ROOT file I/O | uproot | Pythonic, no ROOT install required. Use `uproot.open()` to explore, `arrays()` to load. |
| Array operations | awkward-array, numpy | Columnar analysis — no event loops. awkward for jagged structure, numpy for flat. |
| Histogramming | hist, boost-histogram | Use `hist` for building and plotting; `boost-histogram` for performance-critical fills. Leverage ND histogram axes for systematic variations and cut categories — store variations as axis dimensions rather than separate histograms. |
| Statistical model | pyhf | HistFactory JSON workspaces. Portable, text-based, version-controllable. |
| Fitting / limits | pyhf, cabinetry | cabinetry for convenience wrappers (ranking, pulls). pyhf directly for custom fits. |
| Unbinned fits | zfit | For unbinned likelihood fits (mass fits, PDF fitting). Use when binned HistFactory is insufficient. |
| MVA | xgboost, scikit-learn | BDTs via xgboost. scikit-learn for preprocessing, train/test split, metrics. |
| Hyperparameter opt | optuna | Bayesian optimization. Pin `random_state=42` for reproducibility. |
| Plotting | matplotlib, mplhep (≥1.1) | Use a built-in `mplhep.style` if one exists for the experiment. If not, build a custom style using mplhep's generic style primitives (e.g., `mplhep.style.CMS` as a base, overriding experiment name, logo, fonts). mplhep ≥1.1 exposes the building blocks for constructing experiment styles programmatically. **Never use another experiment's style unmodified.** No figure titles — use captions. See Section 5 for full figure standards. All figures as PDF. |
| Columnar event model | coffea | `NanoEvents` schema gives physics-aware array access (`events.Jet.pt`, cross-references, nested structures). `PackedSelection` for cutflow management. Use coffea's data model when the event structure benefits from schema-driven access — the execution model (how processing is parallelized) is a separate concern handled by §7.3. |
| Scale-out | ProcessPoolExecutor, SLURM, coffea+dask | See §7.3 for decision thresholds and patterns. coffea's `Runner`/`DaskExecutor` is one option for event-level parallelism but not required — `ProcessPoolExecutor` or SLURM array jobs are simpler and often sufficient. |
| Jet clustering | fastjet | Python bindings via `fastjet`. For e+e− (LEP): Durham algorithm (`ee_genkt_algorithm`, p=−1). For pp (LHC): anti-kt. Use e+e− algorithms for e+e− data — pp-era algorithms assume beam remnants. |
| b-tagging | tiered (see below) | No pre-built tagger for ALEPH. Agent builds taggers during Phase 2 — see tiered tagging guidance below. |
| Dependency mgmt | pixi | All dependencies managed via pixi (conda-forge + pypi). `pixi.toml` / `pyproject.toml` is the single source of truth for the environment. |
| Logging | logging + rich | Python `logging` with `rich.logging.RichHandler`. No bare `print()`. See Section 11 for setup and enforcement. |
| Document preparation | pandoc (≥3.0) + pdflatex | Markdown for development, pandoc for PDF conversion. Install pandoc via pixi (`[dependencies] pandoc = ">=3.0"`). Do NOT use an LLM to convert markdown to LaTeX — pandoc handles this programmatically. Default figure width: `0.5\textwidth`. |
| Experiment knowledge | RAG (SciTreeRAG) | Retrieval over publication/thesis corpus. See Section 2.2. |

**Tiered tagging and classification.** When building taggers or classifiers
(b-tagging, tau-ID, quark/gluon, etc.), follow a tiered approach:

1. **Cut-based (cross-check).** Always build a simple cut-based version first
   using the most discriminating variables (e.g., impact parameter significance,
   secondary vertex mass for b-tagging). This serves as the baseline and
   independent cross-check — it should always exist even if a more powerful
   method is used as the primary.
2. **BDT (default primary).** A shallow BDT via xgboost on a handful of
   well-understood inputs is typically the right primary tagger. Fast to train,
   easy to interpret, robust with limited MC statistics. This is the expected
   choice for ALEPH/LEP-scale analyses.
3. **Neural networks (only if justified).** FCNs or GNNs are warranted only
   when the input space is large enough to benefit (many correlated low-level
   inputs) and sufficient MC is available for training. At LHC scale with
   millions of training events and dozens of inputs, this can be transformative.
   For ALEPH-scale analyses, a BDT will almost always suffice.

The agent defines working points during Phase 2 exploration based on the
efficiency vs. rejection trade-off in MC, then validates on data in Phase 3.

### 7.2 Paradigms

**Prototype on a slice, scale up when it works.** Never run on the full
dataset first. Every new script, selection, or processing step should be
developed and validated on a small subset (~1000 events or a single file)
before scaling to the full sample. This applies at every phase:
- **Exploration:** Load one file, check branches and distributions. Do not
  process 22GB of ROOT files to "see what's there."
- **Selection development:** Optimize cuts on a small slice. Only run the
  full cutflow once the logic is validated.
- **MVA training:** Prototype the feature pipeline on a subset. Only train
  on the full sample once the pipeline runs clean.
- **Fit development:** Build and test the workspace on a few bins / one
  region before scaling to the full model.

The pattern is: get the code right on a small sample where iteration is
cheap (seconds, not hours), then run once at scale. If a step takes more
than a few minutes, ask whether a subset would answer the same question.
The full dataset is for production runs, not for debugging.

**Read the API before working around it.** When a tool or library behaves
unexpectedly, the first action is ALWAYS to read the function's docstring or
documentation — not to hack around the behavior. Most "unexpected" behavior
is a documented feature with a documented parameter to control it. The
pattern of seeing unwanted output → wrapping it in post-hoc fixups →
creating brittle code that breaks on the next call is a common agent
failure mode. Concretely:
- Before calling a function with workarounds, run `help(function)` or read
  the source to check if there's a kwarg that does what you want.
- Before writing code to undo a library's default behavior, check if there's
  a configuration option or style parameter.
- If the tool is listed in Appendix C (Tool Heuristics), check there first.
  If it's not, query the docs, solve the problem correctly, and add the
  idiom to Appendix C so the next session doesn't repeat the mistake.

The 30 seconds spent reading a docstring saves minutes of debugging
cargo-culted workarounds.

**Columnar analysis.** Operate on arrays of events, not event-by-event loops.
Selections are boolean masks applied to arrays. This is faster, more readable,
and less error-prone than loop-based code.

**Immutable cuts.** Express selections as a sequence of named boolean masks.
Never modify the underlying arrays — apply masks to produce filtered views.
This makes cutflows trivial (count `True` values at each stage) and cuts
composable (AND masks for combined selections).

**Workspace as artifact.** The statistical model (pyhf JSON workspace) is a
version-controlled artifact, not ephemeral in-memory state. Write it to disk.
Validate it. Commit it. Downstream steps read the workspace file.

**Fit reproducibility.** A human must be able to re-run every fit in the
analysis. Each fit gets its own pixi task (e.g., `pixi run fit`,
`pixi run limits`). The workspace file, input histograms, and fit script
are committed together. The fit script reads the workspace from disk and
writes results (pulls, impacts, limits) to disk. A human opening the
analysis should be able to run `pixi run fit` and reproduce the published
numbers without reading any agent conversation history.

**Plots are evidence.** Every claim in an artifact should have a corresponding
figure or table. Plots are not decoration — they are the primary evidence that
the analysis is correct. Label axes with units. Include ratio panels for
data/MC comparisons. Use consistent styling throughout.

**Reproducibility by default.** Pin random seeds. Record software versions in
artifact code-reference sections. Scripts should be re-runnable from a clean
state and produce identical outputs.

**Event weighting and MC normalization.** During event processing, the
processor tracks the sum of MC generator weights (Σw) for each sample. After
processing, templates are normalized to the target luminosity:
weight_per_event = σ × L / Σw_generated. This reweighting step is cheap and
happens after the event loop, not inside it. The resulting yields are a nominal
estimate — the real process normalizations are calibrated in-situ by fits in
control regions during Phase 4. For generators with negative weights (NLO), Σw
is the algebraic sum (positives minus negatives), not the count.

**Systematic variation naming.** Use the convention `{source}Up` /
`{source}Down` for systematic variation branches or histogram suffixes (e.g.,
`JES_Up`, `JES_Down`). This is the standard expected by pyhf and cabinetry
for automatic workspace construction.

**Binning.** Start with uniform binning during exploration. Before fitting,
rebin to ensure adequate statistics — no bin should have fewer than ~5 expected
events (summed over all processes) to avoid fit instabilities. Variable binning
is fine when physically motivated (e.g., finer bins near a mass peak, coarser
in tails).

### 7.3 Scale-Out

Before running any processing script at full scale, the agent must estimate
the resource requirements and choose the appropriate execution mode. Do not
default to single-core local execution — estimate first, then decide.

#### Estimation step

Before running a script on the full dataset, check:
1. **Input size:** `ls -lh` the input files, sum total bytes.
2. **Per-event cost:** Time the script on a 1000-event slice. Extrapolate to
   full dataset: `(total_events / 1000) * slice_time`.
3. **Memory:** Check peak memory on the slice (e.g., `/usr/bin/time -v` or
   `resource.getrusage`). Multiply by the chunk factor if loading in chunks,
   or by the full dataset factor if loading all at once.

This takes seconds and prevents the agent from sitting on a login node for
an hour processing what could have been a 2-minute SLURM job.

#### Decision thresholds

| Estimated wall time | Input size | Execution mode |
|---------------------|-----------|----------------|
| < 2 minutes | < 1 GB | **Single-core local.** Just run it. |
| 2–15 minutes | 1–10 GB | **Multicore local.** `ProcessPoolExecutor` or equivalent. |
| > 15 minutes | > 10 GB | **SLURM.** `sbatch --wait` or array jobs. |

These are guidelines, not hard rules. If the cluster is idle, SLURM may be
faster even for small tasks. If the task is embarrassingly parallel across
files, prefer SLURM array jobs over multicore local.

#### Pattern 1: Multicore local

For tasks that fit on a single node but benefit from parallelism:

```python
from concurrent.futures import ProcessPoolExecutor

def process_file(path):
    """Process one ROOT file. Returns a dict of histograms/results."""
    import uproot, numpy as np
    with uproot.open(path) as f:
        # ... processing logic ...
        return result

files = ["file1.root", "file2.root", "file3.root"]
with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(process_file, files))
# Merge results
```

This works for any processing — uproot, awkward, coffea, plain numpy. No
framework dependency. Use `os.cpu_count()` or SLURM's `$SLURM_CPUS_PER_TASK`
to set `max_workers`.

#### Pattern 2: SLURM single job

For a single script that needs more resources than the login node allows.
The `--wait` flag makes `sbatch` block until done, so the agent treats it
like a local command:

```bash
#!/bin/bash
#SBATCH -p shared          # or serial_requeue for fast scheduling
#SBATCH -t 01:00:00
#SBATCH -c 4
#SBATCH --mem=8G
#SBATCH -A <account>
#SBATCH --requeue          # allows preemption for faster scheduling
#SBATCH -o .slurm_%j.out

cd /path/to/analysis
pixi run py my_script.py
```

Submit and wait: `sbatch --wait job.sh`

On clusters with requeue partitions, short jobs typically schedule within
seconds. This makes SLURM nearly as fast as local execution for anything
under ~1 hour.

#### Pattern 3: SLURM array jobs

For processing multiple files in parallel — each file gets its own job:

```bash
#!/bin/bash
#SBATCH -p shared
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -A <account>
#SBATCH --array=0-5        # one task per file
#SBATCH --requeue
#SBATCH -o .slurm_%A_%a.out

cd /path/to/analysis
pixi run py process_one_file.py --file-index $SLURM_ARRAY_TASK_ID
```

The script reads `$SLURM_ARRAY_TASK_ID` to pick its input file from a list.
All tasks run in parallel on different nodes. Submit and wait for all:
`sbatch --wait array_job.sh`

This is the preferred pattern for file-parallel processing (e.g., processing
6 years of data files independently). It scales to hundreds of files with
no code changes — just adjust `--array=0-N`.

#### Pattern 4: coffea + dask (for event-level processing)

When processing needs to be parallelized *within* files (chunked event
processing), coffea with dask provides built-in scale-out:

```python
from coffea import processor
from coffea.processor import Runner

# Local development
runner = Runner(executor=processor.FuturesExecutor(workers=4))

# SLURM production
from dask_jobqueue import SLURMCluster
cluster = SLURMCluster(
    cores=4, memory="8GB", walltime="01:00:00",
    job_extra_directives=["--requeue"],
)
cluster.scale(jobs=10)
from coffea.processor import DaskExecutor
runner = Runner(executor=DaskExecutor(client=cluster.get_client()))
```

The processing logic stays the same — only the executor changes. This is the
right choice when the bottleneck is event-level computation (complex
selections, jet clustering, MVA inference), not file I/O.

**When to use coffea vs. plain multiprocessing:** If your script loads full
files with uproot and processes them as arrays, `ProcessPoolExecutor` or
SLURM arrays are simpler and sufficient. coffea adds value when you need
chunked processing within large files, histogramming accumulation, or
systematic variation orchestration.

#### Rules

- **Always estimate before running.** The estimation step is not optional.
  Log the estimate: `log.info("Estimated wall time: %.0f min for %.1f GB",
  est_minutes, total_gb)`.
- **Never wait > 15 minutes on a login node** when SLURM is available. If
  the estimate exceeds this, submit a batch job.
- **Prefer the simplest pattern that works.** Single-core < multicore <
  SLURM single < SLURM array < coffea+dask. Don't use coffea when
  `ProcessPoolExecutor` suffices. Don't use dask when array jobs suffice.
- **Log the execution mode.** When a script runs, log whether it used
  single-core, multicore, or SLURM, and how long it took.

### 7.4 Retrieval

The agent has access to a SciTreeRAG system over the experiment's publication
corpus (~2,400 ALEPH and DELPHI papers) via MCP tools. The primary tool is
`search_lep_corpus` for hybrid dense + BM25 retrieval; use
`compare_measurements` when cross-checking between experiments. See Section 2.2
for retrieval expectations and `.mcp.json` for server configuration.

---
