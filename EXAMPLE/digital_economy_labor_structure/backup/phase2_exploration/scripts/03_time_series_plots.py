"""Step 2.3: Time series plots, ACF/PACF, correlation matrices, distributions."""

import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from rich.logging import RichHandler
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")

DATA_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/data/processed")
FIG_DIR = Path("/Users/bamboo/Githubs/OpenPE/analyses/digital_economy_labor_structure/phase2_exploration/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA_DIR / "analysis_ready.parquet")

def save_fig(fig, name):
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"{name}.{ext}", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info(f"Saved {name}")

# ===================================================
# FIGURE 1: Key time series with structural break window
# ===================================================
key_ts_vars = [
    ("digital_economy_index", "DE Composite Index"),
    ("employment_services_pct", "Services Employment (%)"),
    ("employment_industry_pct", "Industry Employment (%)"),
    ("employment_agriculture_pct", "Agriculture Employment (%)"),
    ("services_value_added_pct_gdp", "Services Value Added (% GDP)"),
    ("population_15_64_pct", "Working-Age Population (%)"),
]

fig, axes = plt.subplots(3, 2, figsize=(20, 30))
axes = axes.ravel()
for i, (var, label) in enumerate(key_ts_vars):
    ax = axes[i]
    ax.plot(df["year"], df[var], "o-", linewidth=1.5, markersize=4, color="#2c3e50")
    ax.axvspan(2013, 2015, alpha=0.15, color="red", label="Smart City Pilot Window")
    ax.axvline(2012, ls="--", alpha=0.4, color="orange", label="Working-age pop peak")
    ax.set_xlabel("Year", fontsize="small")
    ax.set_ylabel(label, fontsize="small")
    ax.tick_params(labelsize="x-small")
    if i == 0:
        ax.legend(fontsize="x-small")

save_fig(fig, "ts_key_variables")

# ===================================================
# FIGURE 2: DE index components
# ===================================================
de_components = [
    ("internet_users_pct", "Internet Users (%)"),
    ("mobile_subscriptions_per100", "Mobile Subs / 100"),
    ("fixed_broadband_per100", "Broadband / 100"),
]
de_available = [(v, l) for v, l in de_components if v in df.columns]

fig, axes = plt.subplots(2, 2, figsize=(20, 20))
axes = axes.ravel()
ax = axes[0]
ax.plot(df["year"], df["digital_economy_index"], "s-", linewidth=2, color="#e74c3c", markersize=5)
ax.set_ylabel("DE Composite Index", fontsize="small")
ax.set_xlabel("Year", fontsize="small")
ax.tick_params(labelsize="x-small")

for i, (var, label) in enumerate(de_available):
    ax = axes[i+1]
    ax.plot(df["year"], df[var], "o-", linewidth=1.5, markersize=4, color="#3498db")
    ax.set_ylabel(label, fontsize="small")
    ax.set_xlabel("Year", fontsize="small")
    ax.tick_params(labelsize="x-small")

# Milestone markers
for ax in axes[:len(de_available)+1]:
    ax.axvline(2015, ls=":", alpha=0.5, color="green", label="Internet Plus 2015")
    ax.axvline(2020, ls=":", alpha=0.5, color="purple", label="COVID 2020")

axes[0].legend(fontsize="x-small")
save_fig(fig, "de_index_components")

# ===================================================
# FIGURE 3: Employment structure stacked area
# ===================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
emp_vars = ["employment_agriculture_pct", "employment_industry_pct", "employment_services_pct"]
colors = ["#2ecc71", "#3498db", "#e74c3c"]
labels = ["Agriculture", "Industry", "Services"]
ax.stackplot(df["year"], [df[v] for v in emp_vars], labels=labels, colors=colors, alpha=0.7)
ax.axvspan(2013, 2015, alpha=0.1, color="black")
ax.set_xlabel("Year", fontsize="small")
ax.set_ylabel("Employment Share (%)", fontsize="small")
ax.legend(loc="center right", fontsize="small")
ax.tick_params(labelsize="x-small")
ax.set_ylim(0, 100)

save_fig(fig, "employment_structure_stacked")

# ===================================================
# FIGURE 4: Correlation matrix (levels)
# ===================================================
corr_vars = [
    "digital_economy_index", "employment_services_pct", "employment_industry_pct",
    "employment_agriculture_pct", "services_value_added_pct_gdp",
    "population_15_64_pct", "population_65plus_pct", "urban_population_pct", "log_gdp_pc",
]
corr_labels = ["DE Index", "Emp. Serv.", "Emp. Ind.", "Emp. Agri.", "Serv. VA/GDP",
               "Pop 15-64", "Pop 65+", "Urban %", "log GDP/cap"]

corr_data = df[corr_vars].dropna()
corr_mat = corr_data.corr()

fig, ax = plt.subplots(1, 1, figsize=(10, 10))
im = ax.imshow(corr_mat.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(corr_labels)))
ax.set_yticks(range(len(corr_labels)))
ax.set_xticklabels(corr_labels, rotation=45, ha="right", fontsize="x-small")
ax.set_yticklabels(corr_labels, fontsize="x-small")

# Annotate
for i in range(len(corr_labels)):
    for j in range(len(corr_labels)):
        val = corr_mat.values[i, j]
        color = "white" if abs(val) > 0.7 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize="x-small", color=color)

fig.colorbar(im, ax=ax, shrink=0.8)
save_fig(fig, "correlation_matrix_levels")

# ===================================================
# FIGURE 5: Correlation matrix (first differences)
# ===================================================
d_vars = [f"d_{v}" for v in corr_vars if f"d_{v}" in df.columns]
d_labels = [l.replace("Emp.", "dEmp.").replace("DE", "dDE").replace("Pop", "dPop").replace("Serv.", "dServ.").replace("Urban", "dUrban").replace("log", "dlog") for l in corr_labels[:len(d_vars)]]

d_corr_data = df[d_vars].dropna()
d_corr_mat = d_corr_data.corr()

fig, ax = plt.subplots(1, 1, figsize=(10, 10))
im = ax.imshow(d_corr_mat.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(d_vars)))
ax.set_yticks(range(len(d_vars)))
d_short = [v.replace("d_", "d.").replace("_pct", "").replace("_per_100", "")[:20] for v in d_vars]
ax.set_xticklabels(d_short, rotation=45, ha="right", fontsize="x-small")
ax.set_yticklabels(d_short, fontsize="x-small")

for i in range(len(d_vars)):
    for j in range(len(d_vars)):
        val = d_corr_mat.values[i, j]
        color = "white" if abs(val) > 0.7 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize="x-small", color=color)

fig.colorbar(im, ax=ax, shrink=0.8)
save_fig(fig, "correlation_matrix_first_diffs")

# ===================================================
# FIGURE 6: ACF/PACF for DE index and employment services
# ===================================================
acf_vars = [
    ("digital_economy_index", "DE Composite Index"),
    ("employment_services_pct", "Services Employment (%)"),
    ("employment_industry_pct", "Industry Employment (%)"),
    ("population_15_64_pct", "Working-Age Pop (%)"),
]

fig, axes = plt.subplots(len(acf_vars), 2, figsize=(20, 10*len(acf_vars)))
for i, (var, label) in enumerate(acf_vars):
    series = df[var].dropna()
    plot_acf(series, ax=axes[i, 0], lags=10, alpha=0.05)
    axes[i, 0].set_ylabel(f"ACF: {label}", fontsize="small")
    axes[i, 0].tick_params(labelsize="x-small")
    
    plot_pacf(series, ax=axes[i, 1], lags=10, alpha=0.05, method="ywm")
    axes[i, 1].set_ylabel(f"PACF: {label}", fontsize="small")
    axes[i, 1].tick_params(labelsize="x-small")

save_fig(fig, "acf_pacf_key_variables")

# ===================================================
# FIGURE 7: Distribution histograms + normality
# ===================================================
fig, axes = plt.subplots(3, 3, figsize=(30, 30))
axes = axes.ravel()
dist_vars = corr_vars
for i, var in enumerate(dist_vars):
    ax = axes[i]
    s = df[var].dropna()
    ax.hist(s, bins=12, density=True, alpha=0.7, color="#3498db", edgecolor="white")
    # Overlay normal fit
    mu, sigma = s.mean(), s.std()
    x = np.linspace(s.min(), s.max(), 100)
    ax.plot(x, stats.norm.pdf(x, mu, sigma), "r-", linewidth=1.5)
    
    # Shapiro-Wilk
    sw_stat, sw_p = stats.shapiro(s)
    short_name = var[:25]
    ax.set_xlabel(short_name, fontsize="x-small")
    ax.text(0.95, 0.95, f"SW p={sw_p:.3f}", transform=ax.transAxes, ha="right", va="top", fontsize="x-small",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    ax.tick_params(labelsize="x-small")

save_fig(fig, "distributions_levels")

# ===================================================
# FIGURE 8: Scatter DE vs employment (levels)
# ===================================================
fig, axes = plt.subplots(1, 3, figsize=(30, 10))
scatter_targets = [
    ("employment_services_pct", "Services Emp. (%)"),
    ("employment_industry_pct", "Industry Emp. (%)"),
    ("services_value_added_pct_gdp", "Services VA/GDP (%)"),
]
for i, (var, label) in enumerate(scatter_targets):
    ax = axes[i]
    x = df["digital_economy_index"]
    y = df[var]
    mask = x.notna() & y.notna()
    colors_arr = ["#3498db" if yr < 2013 else ("#e74c3c" if yr > 2015 else "#f39c12") for yr in df["year"]]
    ax.scatter(x[mask], y[mask], c=[colors_arr[j] for j in range(len(mask)) if mask.iloc[j]], s=40, zorder=3)
    
    # Annotate years
    for j, yr in enumerate(df["year"]):
        if mask.iloc[j]:
            ax.annotate(str(yr), (x.iloc[j], y.iloc[j]), fontsize="x-small", alpha=0.6, textcoords="offset points", xytext=(3, 3))
    
    ax.set_xlabel("DE Composite Index", fontsize="small")
    ax.set_ylabel(label, fontsize="small")
    ax.tick_params(labelsize="x-small")
    
    # Pearson r
    r, p = stats.pearsonr(x[mask], y[mask])
    ax.text(0.05, 0.95, f"r={r:.3f}, p={p:.4f}", transform=ax.transAxes, va="top", fontsize="small",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

save_fig(fig, "scatter_de_vs_employment")

# ===================================================
# FIGURE 9: Demographic transition plot
# ===================================================
fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))
ax1.plot(df["year"], df["population_15_64_pct"], "o-", color="#2c3e50", label="Working-age pop (15-64) %", linewidth=2)
ax2 = ax1.twinx()
ax2.plot(df["year"], df["population_65plus_pct"], "s-", color="#e74c3c", label="Elderly pop (65+) %", linewidth=2)
ax1.axvspan(2013, 2015, alpha=0.1, color="red")

# Find peak
peak_year = df.loc[df["population_15_64_pct"].idxmax(), "year"]
ax1.axvline(peak_year, ls="--", color="#2c3e50", alpha=0.5)
ax1.text(peak_year + 0.3, df["population_15_64_pct"].max() - 0.3, f"Peak: {peak_year}", fontsize="small")

ax1.set_xlabel("Year", fontsize="small")
ax1.set_ylabel("Working-Age Pop (%)", fontsize="small", color="#2c3e50")
ax2.set_ylabel("Elderly Pop (%)", fontsize="small", color="#e74c3c")
ax1.tick_params(labelsize="x-small")
ax2.tick_params(labelsize="x-small")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize="small")

save_fig(fig, "demographic_transition")

log.info("\nAll figures generated.")

# === Print correlation summary for report ===
log.info("\n=== KEY CORRELATIONS (levels) ===")
for v in ["employment_services_pct", "employment_industry_pct", "employment_agriculture_pct"]:
    r, p = stats.pearsonr(df["digital_economy_index"].dropna(), df[v].dropna())
    log.info(f"  DE Index vs {v}: r={r:.3f}, p={p:.4f}")

log.info("\n=== KEY CORRELATIONS (first differences) ===")
for v in ["d_employment_services_pct", "d_employment_industry_pct", "d_employment_agriculture_pct"]:
    if v in df.columns:
        mask = df["d_digital_economy_index"].notna() & df[v].notna()
        r, p = stats.pearsonr(df.loc[mask, "d_digital_economy_index"], df.loc[mask, v])
        log.info(f"  dDE Index vs {v}: r={r:.3f}, p={p:.4f}")

# === Shapiro-Wilk normality for key variables ===
log.info("\n=== NORMALITY TESTS (Shapiro-Wilk) ===")
for var in key_ts_vars:
    v = var[0]
    if v in df.columns:
        s = df[v].dropna()
        sw_stat, sw_p = stats.shapiro(s)
        log.info(f"  {v}: W={sw_stat:.3f}, p={sw_p:.4f} {'(normal)' if sw_p > 0.05 else '(non-normal)'}")
