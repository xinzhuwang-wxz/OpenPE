"""
Phase 2 Exploratory Data Analysis — china_double_reduction_education

Produces all EDA figures and summary statistics for EXPLORATION.md.
All figures saved as PDF+PNG to phase2_exploration/figures/.
"""

import logging
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

# --- Paths ---
DATA_DIR = "phase0_discovery/data/processed"
FIG_DIR = "phase2_exploration/figures"
os.makedirs(FIG_DIR, exist_ok=True)

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

POLICY_YEAR = 2021  # July 2021

def save_fig(fig, name):
    """Save as PDF+PNG, close."""
    for ext in ("pdf", "png"):
        fig.savefig(
            os.path.join(FIG_DIR, f"{name}.{ext}"),
            bbox_inches="tight", dpi=200, transparent=True,
        )
    plt.close(fig)
    log.info(f"Saved {name}")


# ============================================================
# 0. Load all datasets
# ============================================================
log.info("Loading datasets...")

edu = pd.read_parquet(os.path.join(DATA_DIR, "nbs_education_expenditure.parquet"))
cats = pd.read_parquet(os.path.join(DATA_DIR, "nbs_consumption_categories.parquet"))
income = pd.read_parquet(os.path.join(DATA_DIR, "nbs_disposable_income.parquet"))
cpi = pd.read_parquet(os.path.join(DATA_DIR, "nbs_cpi_deflator.parquet"))
demo = pd.read_parquet(os.path.join(DATA_DIR, "china_demographics.parquet"))
pub_edu = pd.read_parquet(os.path.join(DATA_DIR, "public_education_expenditure.parquet"))
tutoring = pd.read_parquet(os.path.join(DATA_DIR, "tutoring_industry_metrics.parquet"))
ciefr_comp = pd.read_parquet(os.path.join(DATA_DIR, "ciefr_spending_composition.parquet"))
ciefr_tut = pd.read_parquet(os.path.join(DATA_DIR, "ciefr_tutoring_2017_vs_2019.parquet"))
underground = pd.read_parquet(os.path.join(DATA_DIR, "underground_tutoring_prices.parquet"))
policy = pd.read_parquet(os.path.join(DATA_DIR, "policy_timeline.parquet"))

log.info("All datasets loaded successfully.")

# ============================================================
# 1. CPI-deflated real education expenditure time series
# ============================================================
log.info("--- Figure 1: Real education expenditure time series ---")

# Merge edu and CPI
merged = edu.merge(cpi[["year", "deflator_education", "deflator_overall"]], on="year", how="left")

# Real values (2015 yuan)
for area, col in [("national", "education_culture_recreation_national_yuan"),
                  ("urban", "education_culture_recreation_urban_yuan"),
                  ("rural", "education_culture_recreation_rural_yuan")]:
    merged[f"real_{area}"] = merged[col] * merged["deflator_education"]

fig, ax = plt.subplots(figsize=(8, 6))
years = merged["year"]

ax.plot(years, merged["real_national"], "o-", color="#2196F3", linewidth=2, label="National")
ax.plot(years, merged["real_urban"], "s-", color="#F44336", linewidth=2, label="Urban")
ax.plot(years, merged["real_rural"], "^-", color="#4CAF50", linewidth=2, label="Rural")

# Policy line
ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.text(2021.1, ax.get_ylim()[1] * 0.95, "Double\nReduction", fontsize="x-small", color="gray", va="top")

# COVID marker
ax.axvspan(2019.5, 2021.5, alpha=0.05, color="orange")
ax.text(2020.5, ax.get_ylim()[0] * 1.05 + 200, "COVID", fontsize="x-small", color="orange", ha="center")

ax.set_xlabel("Year")
ax.set_ylabel("Per capita expenditure [2015 yuan]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")
ax.set_xticks(range(2016, 2026))

save_fig(fig, "fig01_real_education_expenditure_timeseries")

# Also create nominal vs real comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for ax_i, label, suffix in [(ax1, "Nominal", ""), (ax2, "Real (2015 yuan)", "real_")]:
    for area, col, color, marker in [
        ("National", f"{suffix}national" if suffix else "education_culture_recreation_national_yuan", "#2196F3", "o"),
        ("Urban", f"{suffix}urban" if suffix else "education_culture_recreation_urban_yuan", "#F44336", "s"),
        ("Rural", f"{suffix}rural" if suffix else "education_culture_recreation_rural_yuan", "#4CAF50", "^"),
    ]:
        vals = merged[col] if suffix else merged[col]
        ax_i.plot(years, vals, f"{marker}-", color=color, linewidth=2, label=area)
    ax_i.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax_i.set_xlabel("Year")
    ax_i.set_ylabel(f"Per capita expenditure [{label.split('(')[0].strip().lower()} yuan]")
    ax_i.legend(fontsize="small", title=label)
    ax_i.set_xticks(range(2016, 2026))
    ax_i.text(0.02, 0.98, "OpenPE Analysis", transform=ax_i.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig02_nominal_vs_real_expenditure")

# ============================================================
# 2. Education spending as share of total consumption and income
# ============================================================
log.info("--- Figure 2: Education share of consumption and income ---")

# Share of consumption from edu dataset
share_data = edu[["year", "education_share_national_pct", "education_share_urban_pct", "education_share_rural_pct"]].copy()

# Share of income
merged_inc = edu.merge(income[["year", "national_yuan", "urban_yuan", "rural_yuan"]], on="year", how="left", suffixes=("", "_inc"))
merged_inc["edu_share_income_national"] = (merged_inc["education_culture_recreation_national_yuan"] / merged_inc["national_yuan"]) * 100
merged_inc["edu_share_income_urban"] = (merged_inc["education_culture_recreation_urban_yuan"] / merged_inc["urban_yuan"]) * 100
merged_inc["edu_share_income_rural"] = (merged_inc["education_culture_recreation_rural_yuan"] / merged_inc["rural_yuan"]) * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Share of consumption
for area, col, color in [("National", "education_share_national_pct", "#2196F3"),
                          ("Urban", "education_share_urban_pct", "#F44336"),
                          ("Rural", "education_share_rural_pct", "#4CAF50")]:
    ax1.plot(share_data["year"], share_data[col], "o-", color=color, linewidth=2, label=area)
ax1.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax1.set_xlabel("Year")
ax1.set_ylabel("Share of total consumption [%]")
ax1.legend(fontsize="small", title="Consumption share")
ax1.set_xticks(range(2016, 2026))
ax1.text(0.02, 0.98, "OpenPE Analysis", transform=ax1.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

# Share of income
for area, col, color in [("National", "edu_share_income_national", "#2196F3"),
                          ("Urban", "edu_share_income_urban", "#F44336"),
                          ("Rural", "edu_share_income_rural", "#4CAF50")]:
    ax2.plot(merged_inc["year"], merged_inc[col], "o-", color=color, linewidth=2, label=area)
ax2.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax2.set_xlabel("Year")
ax2.set_ylabel("Share of disposable income [%]")
ax2.legend(fontsize="small", title="Income share")
ax2.set_xticks(range(2016, 2026))
ax2.text(0.02, 0.98, "OpenPE Analysis", transform=ax2.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig03_education_share_consumption_income")


# ============================================================
# 3. 8-category consumption composition
# ============================================================
log.info("--- Figure 3: 8-category consumption composition ---")

cat_cols = ["food_tobacco_liquor", "clothing", "residence", "household_facilities",
            "transport_telecom", "education_culture_recreation", "healthcare", "miscellaneous"]
cat_labels = ["Food/Tobacco/Liquor", "Clothing", "Residence", "Household",
              "Transport/Telecom", "Edu/Culture/Rec", "Healthcare", "Miscellaneous"]
cat_colors = ["#E53935", "#8E24AA", "#1E88E5", "#43A047", "#FB8C00", "#FDD835", "#00897B", "#757575"]

# Stacked area chart
fig, ax = plt.subplots(figsize=(8, 6))
share_cols = [c + "_share_pct" for c in cat_cols]
y_data = np.array([cats[c].values for c in share_cols])
ax.stackplot(cats["year"], y_data, labels=cat_labels, colors=cat_colors, alpha=0.85)
ax.axvline(2021, color="black", linestyle="--", linewidth=1, alpha=0.5)
ax.set_xlabel("Year")
ax.set_ylabel("Share of total consumption [%]")
ax.legend(fontsize="x-small", loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.set_xticks(cats["year"].values)
ax.set_ylim(0, 100)
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig04_consumption_composition_stacked")

# Line chart of shares for clarity
fig, ax = plt.subplots(figsize=(8, 6))
for col, label, color in zip(share_cols, cat_labels, cat_colors):
    lw = 2.5 if "education" in col else 1.2
    alpha = 1.0 if "education" in col else 0.6
    ax.plot(cats["year"], cats[col], "o-", color=color, linewidth=lw, alpha=alpha, label=label, markersize=4 if "education" not in col else 6)
ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.set_xlabel("Year")
ax.set_ylabel("Share of total consumption [%]")
ax.legend(fontsize="x-small", loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.set_xticks(cats["year"].values)
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig05_consumption_shares_lines")


# ============================================================
# 4. Per-child education spending
# ============================================================
log.info("--- Figure 4: Per-child normalized spending ---")

# Merge edu with demographics
merged_demo = merged.merge(demo[["year", "births_millions", "compulsory_education_enrollment_millions"]], on="year", how="left")

# Per-child = national edu spending * population (approx) / number of children
# We use compulsory enrollment as the denominator where available
# For simplicity: per-child = per-capita-spending * (proxy: assume ~200M school-age children from enrollment data)
# But better: ratio of per-capita spending to enrollment where available

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel (a): Births and enrollment
ax1.plot(demo["year"], demo["births_millions"], "o-", color="#F44336", linewidth=2, label="Annual births")
ax1_twin = ax1.twinx()
enrollment = demo[["year", "compulsory_education_enrollment_millions"]].dropna()
ax1_twin.plot(enrollment["year"], enrollment["compulsory_education_enrollment_millions"], "s-", color="#2196F3", linewidth=2, label="Compulsory enrollment")
ax1.set_xlabel("Year")
ax1.set_ylabel("Births [millions]", color="#F44336")
ax1_twin.set_ylabel("Enrollment [millions]", color="#2196F3")
ax1.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
lines1 = ax1.get_lines() + ax1_twin.get_lines()
ax1.legend(lines1, [l.get_label() for l in lines1], fontsize="small")
ax1.set_xticks(range(2016, 2025))
ax1.text(0.02, 0.98, "OpenPE Analysis", transform=ax1.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

# Panel (b): Spending indexed to births (per-birth spending proxy)
# Use national real spending / births as a proxy for per-child spending intensity
valid = merged_demo.dropna(subset=["births_millions", "real_national"]).copy()
valid["spending_per_birth"] = valid["real_national"] / valid["births_millions"]
ax2.plot(valid["year"], valid["spending_per_birth"], "o-", color="#2196F3", linewidth=2, label="Real spending / births")

# Also do enrollment-normalized where available
valid_enr = merged_demo.dropna(subset=["compulsory_education_enrollment_millions", "real_national"]).copy()
if len(valid_enr) > 0:
    valid_enr["spending_per_enrollment"] = valid_enr["real_national"] / valid_enr["compulsory_education_enrollment_millions"]
    ax2.plot(valid_enr["year"], valid_enr["spending_per_enrollment"], "s--", color="#F44336", linewidth=2, label="Real spending / enrollment")

ax2.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax2.set_xlabel("Year")
ax2.set_ylabel("Spending intensity [2015 yuan / million]")
ax2.legend(fontsize="small")
ax2.set_xticks(range(2016, 2026))
ax2.text(0.02, 0.98, "OpenPE Analysis", transform=ax2.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig06_per_child_spending")


# ============================================================
# 5. Tutoring industry collapse
# ============================================================
log.info("--- Figure 5: Tutoring industry collapse ---")

log.info(f"Tutoring columns: {list(tutoring.columns)}")
log.info(f"Tutoring data:\n{tutoring.to_string()}")

# Load separate tutoring sub-files
tut_closures = pd.read_parquet(os.path.join(DATA_DIR, "tutoring_center_closures.parquet"))
tut_financials = pd.read_parquet(os.path.join(DATA_DIR, "tutoring_company_financials.parquet"))

log.info(f"Closures columns: {list(tut_closures.columns)}")
log.info(f"Closures:\n{tut_closures.to_string()}")
log.info(f"Financials columns: {list(tut_financials.columns)}")
log.info(f"Financials:\n{tut_financials.to_string()}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel (a): Company revenues (New Oriental, TAL)
for company in tut_financials["company"].unique():
    sub = tut_financials[tut_financials["company"] == company].sort_values("fiscal_year")
    if "revenue_billion_usd" in sub.columns:
        ax1.plot(sub["fiscal_year"], sub["revenue_billion_usd"], "o-", linewidth=2, label=company)
    elif "revenue" in sub.columns:
        ax1.plot(sub["fiscal_year"], sub["revenue"], "o-", linewidth=2, label=company)
ax1.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax1.set_xlabel("Fiscal year")
ax1.set_ylabel("Revenue [billion USD]")
ax1.legend(fontsize="small")
ax1.text(0.02, 0.98, "OpenPE Analysis", transform=ax1.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

# Panel (b): Center closures or industry metrics
if "count" in tut_closures.columns or "value" in tut_closures.columns:
    val_col = "count" if "count" in tut_closures.columns else "value"
    ax2.bar(range(len(tut_closures)), tut_closures[val_col], color="#F44336", alpha=0.8)
    if "metric" in tut_closures.columns:
        ax2.set_xticks(range(len(tut_closures)))
        ax2.set_xticklabels(tut_closures["metric"], rotation=45, ha="right", fontsize="x-small")
    elif "year" in tut_closures.columns:
        ax2.set_xticks(range(len(tut_closures)))
        ax2.set_xticklabels(tut_closures["year"], rotation=45, ha="right")
    ax2.set_ylabel("Count / Value")
else:
    # Fallback: plot whatever numeric columns exist
    num_cols = tut_closures.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        for c in num_cols[:3]:
            ax2.plot(tut_closures.index, tut_closures[c], "o-", label=c)
        ax2.legend(fontsize="small")
ax2.set_xlabel("Metric")
ax2.text(0.02, 0.98, "OpenPE Analysis", transform=ax2.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig07_tutoring_industry_collapse")


# ============================================================
# 6. CIEFR-HS spending decomposition
# ============================================================
log.info("--- Figure 6: CIEFR spending decomposition ---")
log.info(f"CIEFR composition columns: {list(ciefr_comp.columns)}")
log.info(f"CIEFR composition:\n{ciefr_comp.to_string()}")

fig, ax = plt.subplots(figsize=(8, 6))

if "category" in ciefr_comp.columns and "share_of_total_pct" in ciefr_comp.columns:
    colors = ["#2196F3", "#F44336", "#4CAF50"]
    bars = ax.barh(ciefr_comp["category"], ciefr_comp["share_of_total_pct"], color=colors[:len(ciefr_comp)], alpha=0.85)
    for bar, val in zip(bars, ciefr_comp["share_of_total_pct"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{val:.0f}%", va="center", fontsize="small")
    ax.set_xlabel("Share of total education expenditure [%]")
    ax.set_ylabel("Spending category")
elif "component" in ciefr_comp.columns:
    col_val = [c for c in ciefr_comp.columns if "pct" in c.lower() or "share" in c.lower()]
    if col_val:
        colors = ["#2196F3", "#F44336", "#4CAF50"]
        bars = ax.barh(ciefr_comp["component"], ciefr_comp[col_val[0]], color=colors[:len(ciefr_comp)], alpha=0.85)
        ax.set_xlabel(f"{col_val[0]} [%]")
        ax.set_ylabel("Component")
else:
    log.warning(f"Unexpected CIEFR composition structure: {ciefr_comp.columns.tolist()}")
    ax.text(0.5, 0.5, "Data format unexpected", transform=ax.transAxes, ha="center")

ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig08_ciefr_spending_decomposition")


# ============================================================
# 7. Distribution checks: stationarity (ADF/KPSS), ACF/PACF
# ============================================================
log.info("--- Figure 7: Stationarity and autocorrelation ---")

from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Prepare the primary real national series
real_national = merged.set_index("year")["real_national"].sort_index()

# ADF test
adf_result = adfuller(real_national, maxlag=2)
log.info(f"ADF test on real national edu spending:")
log.info(f"  Test statistic: {adf_result[0]:.4f}")
log.info(f"  p-value: {adf_result[1]:.4f}")
log.info(f"  Critical values: {adf_result[4]}")

# KPSS test
try:
    kpss_result = kpss(real_national, regression="ct", nlags="auto")
    log.info(f"KPSS test on real national edu spending:")
    log.info(f"  Test statistic: {kpss_result[0]:.4f}")
    log.info(f"  p-value: {kpss_result[1]:.4f}")
    log.info(f"  Critical values: {kpss_result[3]}")
except Exception as e:
    log.warning(f"KPSS test failed: {e}")
    kpss_result = None

# ADF/KPSS on first differences
diff_series = real_national.diff().dropna()
adf_diff = adfuller(diff_series, maxlag=1)
log.info(f"ADF on first differences: stat={adf_diff[0]:.4f}, p={adf_diff[1]:.4f}")

# Also test urban and rural
for area_name, area_col in [("urban", "real_urban"), ("rural", "real_rural")]:
    series = merged.set_index("year")[area_col].sort_index()
    adf_r = adfuller(series, maxlag=2)
    log.info(f"ADF {area_name}: stat={adf_r[0]:.4f}, p={adf_r[1]:.4f}")

# ACF/PACF plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# ACF levels
plot_acf(real_national, lags=4, ax=axes[0, 0], alpha=0.05)
axes[0, 0].set_xlabel("Lag")
axes[0, 0].set_ylabel("ACF")
axes[0, 0].text(0.02, 0.98, "(a) ACF — levels", transform=axes[0, 0].transAxes, fontsize="small", va="top")

# PACF levels
plot_pacf(real_national, lags=4, ax=axes[0, 1], alpha=0.05, method="ywm")
axes[0, 1].set_xlabel("Lag")
axes[0, 1].set_ylabel("PACF")
axes[0, 1].text(0.02, 0.98, "(b) PACF — levels", transform=axes[0, 1].transAxes, fontsize="small", va="top")

# ACF first differences
plot_acf(diff_series, lags=4, ax=axes[1, 0], alpha=0.05)
axes[1, 0].set_xlabel("Lag")
axes[1, 0].set_ylabel("ACF")
axes[1, 0].text(0.02, 0.98, "(c) ACF — first differences", transform=axes[1, 0].transAxes, fontsize="small", va="top")

# PACF first differences
plot_pacf(diff_series, lags=3, ax=axes[1, 1], alpha=0.05, method="ywm")
axes[1, 1].set_xlabel("Lag")
axes[1, 1].set_ylabel("PACF")
axes[1, 1].text(0.02, 0.98, "(d) PACF — first differences", transform=axes[1, 1].transAxes, fontsize="small", va="top")

for ax_i in axes.flat:
    ax_i.text(0.98, 0.98, "OpenPE Analysis", transform=ax_i.transAxes, fontsize=8, va="top", ha="right", color="gray", style="italic")

save_fig(fig, "fig09_acf_pacf_stationarity")


# ============================================================
# 8. Summary statistics table
# ============================================================
log.info("--- Summary statistics ---")

# Build summary table for key variables
summary_rows = []

# Real national spending
s = merged["real_national"]
summary_rows.append({
    "Variable": "Real edu/culture/rec (national)",
    "Unit": "2015 yuan",
    "N": len(s),
    "Mean": f"{s.mean():.0f}",
    "Std": f"{s.std():.0f}",
    "Min": f"{s.min():.0f}",
    "Max": f"{s.max():.0f}",
    "Missing": 0,
})

for area in ["urban", "rural"]:
    s = merged[f"real_{area}"]
    summary_rows.append({
        "Variable": f"Real edu/culture/rec ({area})",
        "Unit": "2015 yuan",
        "N": len(s),
        "Mean": f"{s.mean():.0f}",
        "Std": f"{s.std():.0f}",
        "Min": f"{s.min():.0f}",
        "Max": f"{s.max():.0f}",
        "Missing": 0,
    })

# Income
for area, col in [("national", "national_yuan"), ("urban", "urban_yuan"), ("rural", "rural_yuan")]:
    s = income[col]
    summary_rows.append({
        "Variable": f"Disposable income ({area})",
        "Unit": "nominal yuan",
        "N": len(s),
        "Mean": f"{s.mean():.0f}",
        "Std": f"{s.std():.0f}",
        "Min": f"{s.min():.0f}",
        "Max": f"{s.max():.0f}",
        "Missing": 0,
    })

# Education share
s = edu["education_share_national_pct"]
summary_rows.append({
    "Variable": "Education share of consumption (national)",
    "Unit": "%",
    "N": len(s),
    "Mean": f"{s.mean():.1f}",
    "Std": f"{s.std():.1f}",
    "Min": f"{s.min():.1f}",
    "Max": f"{s.max():.1f}",
    "Missing": 0,
})

# Births
s = demo["births_millions"]
summary_rows.append({
    "Variable": "Annual births",
    "Unit": "millions",
    "N": len(s),
    "Mean": f"{s.mean():.1f}",
    "Std": f"{s.std():.1f}",
    "Min": f"{s.min():.1f}",
    "Max": f"{s.max():.1f}",
    "Missing": int(s.isnull().sum()),
})

summary_df = pd.DataFrame(summary_rows)
log.info(f"Summary statistics table:\n{summary_df.to_string(index=False)}")

# Write summary CSV for reference
summary_df.to_csv(os.path.join(FIG_DIR, "summary_statistics.csv"), index=False)


# ============================================================
# 9. Urban-rural divergence analysis
# ============================================================
log.info("--- Figure 9: Urban-rural divergence ---")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel (a): Urban vs rural real spending indexed to 2019=100
for area, color, marker in [("urban", "#F44336", "s"), ("rural", "#4CAF50", "^")]:
    series = merged.set_index("year")[f"real_{area}"]
    base = series.loc[2019]
    indexed = (series / base) * 100
    ax1.plot(indexed.index, indexed.values, f"{marker}-", color=color, linewidth=2, label=f"{area.capitalize()} (2019=100)")
ax1.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax1.axhline(100, color="black", linestyle=":", linewidth=0.5, alpha=0.5)
ax1.set_xlabel("Year")
ax1.set_ylabel("Index [2019 = 100]")
ax1.legend(fontsize="small")
ax1.set_xticks(range(2016, 2026))
ax1.text(0.02, 0.98, "OpenPE Analysis", transform=ax1.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

# Panel (b): Urban-rural gap (urban - rural)
gap = merged.set_index("year")["real_urban"] - merged.set_index("year")["real_rural"]
ax2.plot(gap.index, gap.values, "o-", color="#9C27B0", linewidth=2)
ax2.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax2.set_xlabel("Year")
ax2.set_ylabel("Urban-rural gap [2015 yuan]")
ax2.set_xticks(range(2016, 2026))
ax2.text(0.02, 0.98, "OpenPE Analysis", transform=ax2.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig10_urban_rural_divergence")


# ============================================================
# 10. Public education expenditure vs household
# ============================================================
log.info("--- Figure 10: Public vs household education spending ---")

fig, ax = plt.subplots(figsize=(8, 6))

# Public education as % GDP
ax.plot(pub_edu["year"], pub_edu["pct_of_gdp"], "o-", color="#2196F3", linewidth=2, label="Public edu spending [% GDP]")
ax_twin = ax.twinx()

# Household education share of consumption
edu_sub = edu[edu["year"].isin(pub_edu["year"])].copy()
if len(edu_sub) > 0:
    ax_twin.plot(edu_sub["year"], edu_sub["education_share_national_pct"], "s-", color="#F44336", linewidth=2, label="Household edu/culture/rec [% consumption]")

ax.set_xlabel("Year")
ax.set_ylabel("Public spending [% GDP]", color="#2196F3")
ax_twin.set_ylabel("Household share [% consumption]", color="#F44336")
ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)

lines = ax.get_lines() + ax_twin.get_lines()
ax.legend(lines, [l.get_label() for l in lines], fontsize="small", loc="lower right")
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig11_public_vs_household_spending")


# ============================================================
# 11. COVID dip and recovery pattern
# ============================================================
log.info("--- Figure 11: COVID dip and recovery ---")

fig, ax = plt.subplots(figsize=(8, 6))

# YoY growth rates
ax.bar(edu["year"], edu["yoy_growth_national_pct"], color=["#4CAF50" if v >= 0 else "#F44336" for v in edu["yoy_growth_national_pct"]], alpha=0.8)
ax.axvline(2021, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.axhline(0, color="black", linewidth=0.5)
ax.set_xlabel("Year")
ax.set_ylabel("YoY growth rate [%]")
ax.set_xticks(range(2016, 2026))
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

# Annotate key values
for i, row in edu.iterrows():
    ax.text(row["year"], row["yoy_growth_national_pct"] + (1 if row["yoy_growth_national_pct"] >= 0 else -2),
            f"{row['yoy_growth_national_pct']:.1f}%", ha="center", fontsize="x-small")

save_fig(fig, "fig12_yoy_growth_rates")


# ============================================================
# 12. Correlation matrix of key variables
# ============================================================
log.info("--- Figure 12: Correlation heatmap ---")

# Build a correlation dataset
corr_data = merged[["year", "real_national", "real_urban", "real_rural"]].copy()
corr_data = corr_data.merge(income[["year", "national_yuan"]], on="year", how="left")
corr_data = corr_data.merge(demo[["year", "births_millions"]], on="year", how="left")
corr_data = corr_data.merge(cpi[["year", "deflator_education"]], on="year", how="left")
corr_data = corr_data.rename(columns={
    "real_national": "Real edu (nat)",
    "real_urban": "Real edu (urban)",
    "real_rural": "Real edu (rural)",
    "national_yuan": "Income (nat)",
    "births_millions": "Births",
    "deflator_education": "CPI deflator",
})
corr_data = corr_data.drop(columns=["year"]).dropna()

corr_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.pcolormesh(corr_matrix.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(np.arange(len(corr_matrix.columns)) + 0.5)
ax.set_yticks(np.arange(len(corr_matrix.columns)) + 0.5)
ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="right", fontsize="x-small")
ax.set_yticklabels(corr_matrix.columns, fontsize="x-small")
ax.invert_yaxis()

# Annotate cells
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        ax.text(j + 0.5, i + 0.5, f"{corr_matrix.iloc[i, j]:.2f}",
                ha="center", va="center", fontsize="x-small",
                color="white" if abs(corr_matrix.iloc[i, j]) > 0.6 else "black")

fig.colorbar(im, ax=ax, shrink=0.8)
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig13_correlation_heatmap")


# ============================================================
# 13. Pre-trend analysis for urban-rural parallel trends
# ============================================================
log.info("--- Figure 13: Pre-trend parallel trends check ---")

pre_policy = merged[merged["year"] <= 2020].copy()

fig, ax = plt.subplots(figsize=(8, 6))

# Index both to 2016 = 100
for area, color, marker in [("urban", "#F44336", "s"), ("rural", "#4CAF50", "^")]:
    series = pre_policy.set_index("year")[f"real_{area}"]
    indexed = (series / series.iloc[0]) * 100
    ax.plot(indexed.index, indexed.values, f"{marker}-", color=color, linewidth=2, label=f"{area.capitalize()}")

ax.set_xlabel("Year")
ax.set_ylabel("Index [2016 = 100]")
ax.legend(fontsize="small", title="Pre-policy trends")
ax.set_xticks(range(2016, 2021))
ax.text(0.02, 0.98, "OpenPE Analysis", transform=ax.transAxes, fontsize=8, va="top", ha="left", color="gray", style="italic")

save_fig(fig, "fig14_parallel_trends_precheck")

# Log the growth rates
for area in ["urban", "rural"]:
    series = pre_policy.set_index("year")[f"real_{area}"]
    growth = ((series.iloc[-1] / series.iloc[0]) ** (1 / (len(series) - 1)) - 1) * 100
    log.info(f"Pre-policy CAGR ({area}): {growth:.2f}% per year")


# ============================================================
# Final: print summary of all stationarity tests
# ============================================================
log.info("=" * 60)
log.info("STATIONARITY TEST SUMMARY")
log.info("=" * 60)
log.info(f"Real national edu spending (levels):")
log.info(f"  ADF: stat={adf_result[0]:.4f}, p={adf_result[1]:.4f} ({'stationary' if adf_result[1] < 0.05 else 'NON-stationary'})")
if kpss_result:
    log.info(f"  KPSS: stat={kpss_result[0]:.4f}, p={kpss_result[1]:.4f} ({'stationary' if kpss_result[1] > 0.05 else 'NON-stationary'})")
log.info(f"First differences:")
log.info(f"  ADF: stat={adf_diff[0]:.4f}, p={adf_diff[1]:.4f} ({'stationary' if adf_diff[1] < 0.05 else 'NON-stationary'})")

log.info("")
log.info("EDA complete. All figures saved to %s", FIG_DIR)
