"""Step 2.3: Structural break detection and DE index milestone validation."""

import logging
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from rich.logging import RichHandler
from scipy import stats
from statsmodels.tsa.stattools import adfuller

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")

DATA_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/processed")
FIG_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/figures")

df = pd.read_parquet(DATA_DIR / "analysis_ready.parquet")

# ===================================================
# Chow test implementation
# ===================================================
def chow_test(y, X, break_idx):
    """Chow breakpoint test. Returns F-statistic and p-value."""
    n = len(y)
    k = X.shape[1]
    
    # Full model
    from numpy.linalg import lstsq
    beta_full, res_full, _, _ = lstsq(X, y, rcond=None)
    rss_full = np.sum((y - X @ beta_full)**2)
    
    # Split models
    y1, X1 = y[:break_idx], X[:break_idx]
    y2, X2 = y[break_idx:], X[break_idx:]
    
    if len(y1) < k + 1 or len(y2) < k + 1:
        return np.nan, np.nan
    
    beta1, _, _, _ = lstsq(X1, y1, rcond=None)
    rss1 = np.sum((y1 - X1 @ beta1)**2)
    
    beta2, _, _, _ = lstsq(X2, y2, rcond=None)
    rss2 = np.sum((y2 - X2 @ beta2)**2)
    
    rss_split = rss1 + rss2
    
    F = ((rss_full - rss_split) / k) / (rss_split / (n - 2*k))
    p = 1 - stats.f.cdf(F, k, n - 2*k)
    return F, p

# ===================================================
# Sequential sup-Wald for unknown break dates
# ===================================================
log.info("=== STRUCTURAL BREAK DETECTION ===")

test_vars = [
    ("digital_economy_index", "DE Index"),
    ("employment_services_pct", "Services Emp."),
    ("employment_industry_pct", "Industry Emp."),
]

break_results = {}

for var, label in test_vars:
    series = df[var].dropna().values
    years = df.loc[df[var].notna(), "year"].values
    n = len(series)
    
    # Create X matrix with constant and trend
    X = np.column_stack([np.ones(n), np.arange(n)])
    
    # Test at known dates (2013, 2015)
    for break_year in [2013, 2015]:
        if break_year in years:
            break_idx = np.where(years == break_year)[0][0]
            F, p = chow_test(series, X, break_idx)
            log.info(f"Chow test {label} at {break_year}: F={F:.3f}, p={p:.4f}")
            break_results[f"{var}_chow_{break_year}"] = {"F": round(F, 3), "p": round(p, 4)}
    
    # Sup-Wald: scan all interior points
    trim = max(5, int(0.15 * n))  # 15% trimming
    F_stats = []
    test_years = []
    for i in range(trim, n - trim):
        F, p = chow_test(series, X, i)
        F_stats.append(F)
        test_years.append(years[i])
    
    if F_stats:
        max_F_idx = np.argmax(F_stats)
        max_F_year = test_years[max_F_idx]
        max_F = F_stats[max_F_idx]
        log.info(f"Sup-Wald {label}: max F={max_F:.3f} at year {max_F_year}")
        break_results[f"{var}_supwald"] = {"max_F": round(max_F, 3), "break_year": int(max_F_year)}

# Save break results
OUT_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/scripts")
with open(OUT_DIR / "structural_break_results.json", "w") as f:
    json.dump(break_results, f, indent=2)

# ===================================================
# FIGURE: Structural break visualization
# ===================================================
fig, axes = plt.subplots(2, 2, figsize=(20, 20))

# Panel (a): DE index with break window
ax = axes[0, 0]
ax.plot(df["year"], df["digital_economy_index"], "o-", color="#e74c3c", linewidth=2, markersize=5)
ax.axvspan(2013, 2015, alpha=0.15, color="gray", label="Pilot window 2013-2015")
ax.axvline(2015, ls=":", color="green", alpha=0.5, label="Internet Plus 2015")
ax.axvline(2020, ls=":", color="purple", alpha=0.5, label="COVID 2020")
ax.set_xlabel("Year", fontsize="small")
ax.set_ylabel("DE Composite Index", fontsize="small")
ax.legend(fontsize="x-small")
ax.tick_params(labelsize="x-small")

# Panel (b): Employment sectors with break window
ax = axes[0, 1]
ax.plot(df["year"], df["employment_services_pct"], "o-", color="#e74c3c", label="Services", linewidth=1.5)
ax.plot(df["year"], df["employment_industry_pct"], "s-", color="#3498db", label="Industry", linewidth=1.5)
ax.plot(df["year"], df["employment_agriculture_pct"], "^-", color="#2ecc71", label="Agriculture", linewidth=1.5)
ax.axvspan(2013, 2015, alpha=0.15, color="gray")
ax.set_xlabel("Year", fontsize="small")
ax.set_ylabel("Employment Share (%)", fontsize="small")
ax.legend(fontsize="x-small")
ax.tick_params(labelsize="x-small")

# Panel (c): First-difference scatter pre/post
ax = axes[1, 0]
d_de = df["d_digital_economy_index"]
d_serv = df["d_employment_services_pct"]
mask = d_de.notna() & d_serv.notna()
pre_mask = mask & (df["year"] < 2013)
post_mask = mask & (df["year"] > 2015)

ax.scatter(d_de[pre_mask], d_serv[pre_mask], color="#3498db", s=50, zorder=3, label="Pre-2013")
ax.scatter(d_de[post_mask], d_serv[post_mask], color="#e74c3c", s=50, zorder=3, label="Post-2015")

# Regression lines
for m, c, lbl in [(pre_mask, "#3498db", "pre"), (post_mask, "#e74c3c", "post")]:
    x, y = d_de[m].values, d_serv[m].values
    if len(x) > 2:
        slope, intercept, r, p, se = stats.linregress(x, y)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, intercept + slope * xs, color=c, ls="--", alpha=0.7)

ax.set_xlabel("$\\Delta$ DE Index", fontsize="small")
ax.set_ylabel("$\\Delta$ Services Employment (%)", fontsize="small")
ax.legend(fontsize="small")
ax.tick_params(labelsize="x-small")

# Panel (d): Counterfactual trend extrapolation
ax = axes[1, 1]
pre = df[df["year"] <= 2012].copy()
post = df[df["year"] >= 2016].copy()
for var, color, label in [("employment_services_pct", "#e74c3c", "Services"), ("employment_industry_pct", "#3498db", "Industry")]:
    # Full series
    ax.plot(df["year"], df[var], "o-", color=color, linewidth=1.5, markersize=4, label=f"Observed {label}")
    # Pre-trend extrapolation
    x_pre = pre["year"].values - 2000  # normalize
    y_pre = pre[var].values
    slope, intercept, _, _, _ = stats.linregress(x_pre, y_pre)
    x_extrap = np.arange(2013, 2024) - 2000
    y_extrap = intercept + slope * x_extrap
    ax.plot(np.arange(2013, 2024), y_extrap, ls="--", color=color, alpha=0.5, label=f"Pre-trend {label}")

ax.axvspan(2013, 2015, alpha=0.15, color="gray")
ax.set_xlabel("Year", fontsize="small")
ax.set_ylabel("Employment Share (%)", fontsize="small")
ax.legend(fontsize="x-small")
ax.tick_params(labelsize="x-small")

save_path = FIG_DIR / "structural_break_analysis"
for ext in ["pdf", "png"]:
    fig.savefig(f"{save_path}.{ext}", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved structural_break_analysis")

# ===================================================
# DE Index Milestone Validation
# ===================================================
log.info("\n=== DE INDEX MILESTONE VALIDATION ===")
log.info("Known milestones:")
log.info("  2013-2015: Smart city pilot batches")
log.info("  2015: Internet Plus strategy announced")
log.info("  2020: COVID digital acceleration")

de = df[["year", "digital_economy_index"]].dropna()
de["yoy_change"] = de["digital_economy_index"].diff()

log.info(f"\nDE Index year-over-year changes:")
for _, row in de.iterrows():
    marker = ""
    yr = int(row["year"])
    if yr in [2013, 2014, 2015]:
        marker = " <-- Smart City Pilot"
    elif yr == 2020:
        marker = " <-- COVID year"
    yoy_str = f"{row['yoy_change']:.4f}" if pd.notna(row["yoy_change"]) else "NA"
    log.info(f"  {yr}: {row['digital_economy_index']:.4f} (yoy: {yoy_str}){marker}")

# Check if 2015+ shows acceleration
pre_2015_growth = de[de["year"].between(2005, 2014)]["yoy_change"].mean()
post_2015_growth = de[de["year"].between(2016, 2023)]["yoy_change"].mean()
log.info(f"\nAverage annual DE growth 2005-2014: {pre_2015_growth:.4f}")
log.info(f"Average annual DE growth 2016-2023: {post_2015_growth:.4f}")
log.info(f"Growth deceleration post-2015: {post_2015_growth - pre_2015_growth:.4f}")

# ===================================================
# COVID Impact Assessment
# ===================================================
log.info("\n=== COVID IMPACT ASSESSMENT (2020) ===")
covid_vars = ["employment_services_pct", "employment_industry_pct", "digital_economy_index",
              "gdp_per_capita_usd", "labor_force_total"]
for var in covid_vars:
    if var in df.columns:
        v2019 = df.loc[df["year"] == 2019, var].values[0]
        v2020 = df.loc[df["year"] == 2020, var].values[0]
        v2021 = df.loc[df["year"] == 2021, var].values[0]
        pct_chg = (v2020 - v2019) / v2019 * 100
        log.info(f"  {var}: 2019={v2019:.2f}, 2020={v2020:.2f} ({pct_chg:+.2f}%), 2021={v2021:.2f}")

# Zivot-Andrews unit root with structural break
log.info("\n=== ZIVOT-ANDREWS UNIT ROOT (break in trend) ===")
try:
    from statsmodels.tsa.stattools import zivot_andrews
    for var, label in [("digital_economy_index", "DE"), ("employment_services_pct", "Serv. Emp.")]:
        series = df[var].dropna()
        za_stat, za_p, za_lags, za_break, za_cv = zivot_andrews(series.values, trim=0.15)
        break_year = df.loc[df[var].notna(), "year"].values[za_break]
        log.info(f"  {label}: stat={za_stat:.3f}, break at index {za_break} (year ~{break_year}), 5% cv={za_cv['5%']:.3f}")
except ImportError:
    log.info("  Zivot-Andrews not available in this statsmodels version")
except Exception as e:
    log.info(f"  Zivot-Andrews error: {e}")
