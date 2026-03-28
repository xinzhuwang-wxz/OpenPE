## 7. Tools and Paradigms

The agent uses standard analysis software. No bespoke analysis framework is
required, but the following tools and paradigms are preferred. This section
is maintained by the analysis team and reflects operational knowledge about
what works well in practice.

### 7.1 Preferred Tools

| Capability | Tool | Notes |
|-----------|------|-------|
| Tabular I/O | pandas, pyarrow | Parquet as the default serialization format. CSV for small files or human-readable output. Use `pd.read_parquet()` / `df.to_parquet()` for all intermediate data. |
| Array operations | numpy | Vectorized operations — no row-by-row loops. Use numpy for numerical computation; pandas for labeled data. |
| Causal inference | dowhy, statsmodels | dowhy for causal graph specification, identification, and estimation. statsmodels for regression, IV, DiD, and econometric methods. |
| Statistical testing | scipy.stats, statsmodels | scipy for hypothesis tests, distributions, bootstrap. statsmodels for regression diagnostics, heteroskedasticity tests, time series. |
| Bootstrap / resampling | scipy, custom | `scipy.stats.bootstrap` for confidence intervals. Custom implementations for complex statistics (pinned seeds). |
| Data sources (economics) | wbgapi, fredapi | wbgapi for World Bank indicators. fredapi for FRED time series. Both require API keys configured in `.env`. |
| Data sources (web) | WebSearch, WebFetch | For acquiring data not available through structured APIs. Document the URL, retrieval date, and any parsing logic. |
| ML (optional) | scikit-learn, xgboost | scikit-learn for preprocessing, cross-validation, feature selection. xgboost for gradient-boosted models when predictive performance matters. |
| Hyperparameter opt | optuna | Bayesian optimization. Pin `random_state=42` for reproducibility. |
| Plotting | matplotlib | Domain-agnostic styling. No experiment branding. See Appendix D for full figure standards. All figures as PDF. |
| Dependency mgmt | pixi | All dependencies managed via pixi (conda-forge + pypi). `pixi.toml` / `pyproject.toml` is the single source of truth for the environment. |
| Logging | logging + rich | Python `logging` with `rich.logging.RichHandler`. No bare `print()`. See Section 11 for setup and enforcement. |
| Document preparation | pandoc (>=3.0) + pdflatex | Markdown for development, pandoc for PDF conversion. Install pandoc via pixi (`[dependencies] pandoc = ">=3.0"`). Do NOT use an LLM to convert markdown to LaTeX — pandoc handles this programmatically. Default figure width: `0.5\textwidth`. |

### 7.2 Paradigms

**Prototype on a slice, scale up when it works.** Never run on the full
dataset first. Every new script, analysis step, or processing pipeline
should be developed and validated on a small subset (~1000 rows or a
single year/region) before scaling to the full sample. This applies at
every phase:
- **Discovery:** Load metadata, check columns and distributions. Do not
  process a multi-GB Parquet file to "see what's there."
- **Exploration:** Profile variables on a small slice. Only run full
  profiling once the logic is validated.
- **Analysis:** Prototype the estimation pipeline on a subset. Only run
  on the full sample once the pipeline runs clean.
- **Projection:** Build and test scenarios on a subset before scaling to
  the full model.

The pattern is: get the code right on a small sample where iteration is
cheap (seconds, not hours), then run once at scale. If a step takes more
than a few minutes, ask whether a subset would answer the same question.
The full dataset is for production runs, not for debugging.

**Read the API before working around it.** When a tool or library behaves
unexpectedly, the first action is ALWAYS to read the function's docstring
or documentation — not to hack around the behavior. Most "unexpected"
behavior is a documented feature with a documented parameter to control
it. The pattern of seeing unwanted output, wrapping it in post-hoc fixups,
creating brittle code that breaks on the next call is a common agent
failure mode. Concretely:
- Before calling a function with workarounds, run `help(function)` or
  read the source to check if there's a kwarg that does what you want.
- Before writing code to undo a library's default behavior, check if
  there's a configuration option or style parameter.
- If the tool is listed in Appendix C (Tool Heuristics), check there
  first. If it's not, query the docs, solve the problem correctly, and
  add the idiom to Appendix C so the next session doesn't repeat the
  mistake.

The 30 seconds spent reading a docstring saves minutes of debugging
cargo-culted workarounds.

**Vectorized analysis.** Operate on arrays and dataframes, not row-by-row
loops. Selections are boolean masks applied to dataframes. This is faster,
more readable, and less error-prone than loop-based code.

**Immutable transformations.** Express data transformations as a sequence
of named steps that produce new columns or filtered views. Never modify
the source data in place — create derived dataframes. This makes the
transformation chain traceable and reproducible.

**Registry as artifact.** The `registry.yaml` file is a version-controlled
artifact that maps every analysis artifact to its phase, commit hash,
review status, and EP assessment. It is not ephemeral in-memory state.
Write it to disk. Validate it. Commit it. Downstream steps read the
registry to understand what has been produced and reviewed.

```yaml
# registry.yaml — artifact registry
artifacts:
  - name: DISCOVERY.md
    phase: 0
    commit: abc123
    review_status: passed
    ep_summary: "All sub-questions have viable data paths"
  - name: STRATEGY.md
    phase: 1
    commit: def456
    review_status: passed
    ep_summary: "Method selection justified for all sub-questions"
  # ... one entry per artifact
```

**Reproducibility by default.** Pin random seeds. Record software versions
in artifact code-reference sections. Scripts should be re-runnable from a
clean state and produce identical outputs. Every analytical step gets its
own pixi task (e.g., `pixi run analyze`, `pixi run project`,
`pixi run verify`). A human opening the analysis should be able to run
`pixi run analyze` and reproduce the published findings without reading
any agent conversation history.

**Plots are evidence.** Every claim in an artifact should have a
corresponding figure or table. Plots are not decoration — they are the
primary evidence that the analysis is correct. Label axes with units.
Include comparison panels where appropriate. Use consistent styling
throughout.

**EP tracking in code.** Every script that produces a finding must also
produce an EP assessment for that finding, written to a structured
format (YAML or JSON). The EP assessment includes: the finding value,
the EP score, the factors contributing to the EP (statistical power,
assumption quality, robustness across specifications), and any EP
penalties applied. This machine-readable EP trail feeds into the
`ep_trajectory.csv` deliverable.

```python
import yaml

finding = {
    "sub_question": "H1",
    "value": -0.023,
    "ci_95": [-0.041, -0.005],
    "ep": 0.78,
    "ep_factors": {
        "statistical_power": 0.90,
        "confounder_coverage": 0.85,
        "robustness": 0.82,
        "data_quality": 0.88,
    },
    "ep_penalties": [
        {"reason": "proxy variable for X", "penalty": -0.05},
    ],
    "phase": 3,
    "script": "analyze_h1.py",
}
with open("results/finding_H1.yaml", "w") as f:
    yaml.dump(finding, f)
```

**Uncertainty propagation.** When combining findings across sub-questions
or propagating through a chain, uncertainty must be propagated explicitly.
Use bootstrap resampling for complex statistics where analytical formulas
are not available. Document the propagation method in the artifact.

### 7.3 Scale-Out

Before running any processing script at full scale, the agent must estimate
the resource requirements and choose the appropriate execution mode. Do not
default to single-core local execution — estimate first, then decide.

#### Estimation step

Before running a script on the full dataset, check:
1. **Input size:** `ls -lh` the input files, sum total bytes.
2. **Per-row cost:** Time the script on a 1000-row slice. Extrapolate to
   full dataset: `(total_rows / 1000) * slice_time`.
3. **Memory:** Check peak memory on the slice (e.g., `/usr/bin/time -v` or
   `resource.getrusage`). Multiply by the chunk factor if loading in
   chunks, or by the full dataset factor if loading all at once.

This takes seconds and prevents the agent from sitting idle for an hour
processing what could have been a 2-minute parallel job.

#### Decision thresholds

| Estimated wall time | Input size | Execution mode |
|---------------------|-----------|----------------|
| < 2 minutes | < 1 GB | **Single-core local.** Just run it. |
| 2–15 minutes | 1–10 GB | **Multicore local.** `ProcessPoolExecutor` or equivalent. |
| > 15 minutes | > 10 GB | **Batch processing.** SLURM or chunked parallel. |

These are guidelines, not hard rules. If the cluster is available, batch
submission may be faster even for small tasks. If the task is embarrassingly
parallel across files or partitions, prefer array jobs over multicore local.

#### Pattern 1: Multicore local

For tasks that fit on a single node but benefit from parallelism:

```python
from concurrent.futures import ProcessPoolExecutor

def process_partition(path):
    """Process one data partition. Returns a dict of results."""
    import pandas as pd
    df = pd.read_parquet(path)
    # ... processing logic ...
    return result

files = ["part1.parquet", "part2.parquet", "part3.parquet"]
with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(process_partition, files))
# Merge results
```

This works for any processing — pandas, numpy, scikit-learn. No framework
dependency. Use `os.cpu_count()` to set `max_workers`.

#### Pattern 2: SLURM single job

For a single script that needs more resources than the login node allows.
The `--wait` flag makes `sbatch` block until done, so the agent treats it
like a local command:

```bash
#!/bin/bash
#SBATCH -p shared
#SBATCH -t 01:00:00
#SBATCH -c 4
#SBATCH --mem=8G
#SBATCH -o .slurm_%j.out

cd /path/to/analysis
pixi run py my_script.py
```

Submit and wait: `sbatch --wait job.sh`

#### Pattern 3: SLURM array jobs

For processing multiple partitions in parallel — each partition gets its
own job:

```bash
#!/bin/bash
#SBATCH -p shared
#SBATCH -t 00:30:00
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH --array=0-5
#SBATCH -o .slurm_%A_%a.out

cd /path/to/analysis
pixi run py process_partition.py --partition-index $SLURM_ARRAY_TASK_ID
```

The script reads `$SLURM_ARRAY_TASK_ID` to pick its input partition from
a list. All tasks run in parallel on different nodes. Submit and wait:
`sbatch --wait array_job.sh`

#### Rules

- **Always estimate before running.** The estimation step is not optional.
  Log the estimate: `log.info("Estimated wall time: %.0f min for %.1f GB",
  est_minutes, total_gb)`.
- **Never wait > 15 minutes on a login node** when SLURM is available. If
  the estimate exceeds this, submit a batch job.
- **Prefer the simplest pattern that works.** Single-core < multicore <
  SLURM single < SLURM array. Don't use SLURM when
  `ProcessPoolExecutor` suffices.
- **Log the execution mode.** When a script runs, log whether it used
  single-core, multicore, or SLURM, and how long it took.

---
