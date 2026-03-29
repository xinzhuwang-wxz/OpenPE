"""
Step 4: Compositional Analysis.

- 8-category NBS consumption shares pre/post policy
- Education share trajectory vs synthetic counterfactual from stable categories
- Per-child normalization analysis

Produces: phase3_analysis/figures/fig_p3_06_*.pdf/png
"""
import json
import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich.logging import RichHandler
from scipy import stats
import statsmodels.api as sm

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

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

np.random.seed(42)

DATA_DIR_PROC = "phase0_discovery/data/processed"
DATA_DIR = "phase3_analysis/data"
FIG_DIR = "phase3_analysis/figures"

os.makedirs(FIG_DIR, exist_ok=True)

# ---- Load ----
cons = pd.read_parquet(f"{DATA_DIR_PROC}/nbs_consumption_categories.parquet")
df = pd.read_parquet(f"{DATA_DIR}/analysis_dataset.parquet")

log.info(f"Consumption categories: {cons.shape}, years: {cons['year'].min()}-{cons['year'].max()}")

# ---- 8-category share analysis ----
share_cols = [c for c in cons.columns if c.endswith("_share_pct")]
category_names = {
    "food_tobacco_liquor_share_pct": "Food/tobacco/liquor",
    "clothing_share_pct": "Clothing",
    "residence_share_pct": "Residence",
    "household_facilities_share_pct": "Household facilities",
    "transport_telecom_share_pct": "Transport/telecom",
    "education_culture_recreation_share_pct": "Education/culture/rec",
    "healthcare_share_pct": "Healthcare",
    "miscellaneous_share_pct": "Miscellaneous",
}

# Calculate pre-post changes for each category
# Pre-policy: 2019 (only clean pre-policy year in this dataset)
# Post-policy: 2022-2025 average
pre_year = 2019
pre = cons[cons["year"] == pre_year]
post = cons[cons["year"].between(2022, 2025)]

share_changes = []
for col in share_cols:
    name = category_names.get(col, col)
    pre_val = pre[col].values[0]
    post_val = post[col].mean()

    # Also compute 2025 value
    val_2025 = cons[cons["year"] == 2025][col].values[0]

    share_changes.append({
        "category": name,
        "col": col,
        "pre_2019": pre_val,
        "post_avg": post_val,
        "val_2025": val_2025,
        "change_pp": post_val - pre_val,
        "change_2025_pp": val_2025 - pre_val,
    })

share_df = pd.DataFrame(share_changes).sort_values("change_pp")
log.info("\n=== Consumption Share Changes (2019 vs post-policy avg) ===")
for _, row in share_df.iterrows():
    log.info(f"  {row['category']:25s}: {row['pre_2019']:5.1f}% -> {row['post_avg']:5.1f}% "
             f"(change: {row['change_pp']:+.1f} pp, 2025: {row['val_2025']:.1f}%)")

# ---- Education share: unique behavior test ----
# Compare education share change to the distribution of changes across all categories
all_changes = share_df["change_pp"].values
edu_change = share_df[share_df["col"] == "education_culture_recreation_share_pct"]["change_pp"].values[0]
other_changes = share_df[share_df["col"] != "education_culture_recreation_share_pct"]["change_pp"].values

# z-score of education change within all categories
z_score = (edu_change - other_changes.mean()) / other_changes.std() if other_changes.std() > 0 else 0
log.info(f"\nEducation share change: {edu_change:+.2f} pp")
log.info(f"Other categories mean change: {other_changes.mean():+.2f} pp (std: {other_changes.std():.2f})")
log.info(f"Z-score of education change: {z_score:.2f}")

# ---- Synthetic counterfactual from stable categories ----
# Use food and residence (most stable, largest) to predict education share
log.info("\n=== Synthetic Counterfactual for Education Share ===")

# Pre-policy fit: 2019 only (not enough data for regression)
# Instead: use the average share of "stable" categories as benchmark
stable_cats = ["food_tobacco_liquor_share_pct", "residence_share_pct"]
cons_copy = cons.copy()
cons_copy["stable_mean"] = cons_copy[stable_cats].mean(axis=1)
cons_copy["edu_relative"] = (
    cons_copy["education_culture_recreation_share_pct"] / cons_copy["stable_mean"]
)

log.info("Education share relative to stable categories (food+residence avg):")
for _, row in cons_copy.iterrows():
    log.info(f"  {int(row['year'])}: edu={row['education_culture_recreation_share_pct']:.1f}%, "
             f"stable={row['stable_mean']:.1f}%, ratio={row['edu_relative']:.4f}")

# Pre-policy ratio (2019)
pre_ratio = cons_copy[cons_copy["year"] == 2019]["edu_relative"].values[0]
# Post-policy ratios
post_ratios = cons_copy[cons_copy["year"].between(2022, 2025)]["edu_relative"].values
ratio_change = post_ratios.mean() - pre_ratio
log.info(f"\nPre-policy ratio (2019): {pre_ratio:.4f}")
log.info(f"Post-policy avg ratio (2022-2025): {post_ratios.mean():.4f}")
log.info(f"Change: {ratio_change:+.4f}")

# ---- Per-child normalization ----
log.info("\n=== Per-Child Normalization Analysis ===")

# Per-birth spending
df_valid = df[df["births_millions"].notna()].copy()
df_valid["spending_per_birth"] = df_valid["real_national"] / df_valid["births_millions"]
df_valid["spending_per_birth_urban"] = df_valid["real_urban"] / df_valid["births_millions"]

log.info("Real spending per birth (national):")
for _, row in df_valid.iterrows():
    log.info(f"  {int(row['year'])}: {row['spending_per_birth']:.0f} yuan/birth "
             f"(spending={row['real_national']:.0f}, births={row['births_millions']:.2f}M)")

# ITS on per-birth series (excl 2020)
df_perbirth = df_valid[df_valid["year"] != 2020].copy()
df_perbirth["time"] = df_perbirth["year"] - df_perbirth["year"].min()
df_perbirth["post"] = (df_perbirth["year"] >= 2021).astype(int)

X = sm.add_constant(df_perbirth[["time", "post"]])
y = df_perbirth["spending_per_birth"]

if len(y) >= 4:
    model_perbirth = sm.OLS(y, X).fit()
    log.info(f"\nPer-birth ITS level shift: {model_perbirth.params['post']:.1f} "
             f"(SE={model_perbirth.bse['post']:.1f}, p={model_perbirth.pvalues['post']:.4f})")
    log.info(f"Per-birth ITS trend: {model_perbirth.params['time']:.1f} yuan/year per birth")

    perbirth_results = {
        "level_shift": float(model_perbirth.params["post"]),
        "level_shift_se": float(model_perbirth.bse["post"]),
        "level_shift_pvalue": float(model_perbirth.pvalues["post"]),
        "trend": float(model_perbirth.params["time"]),
        "r_squared": float(model_perbirth.rsquared),
    }
else:
    perbirth_results = {"note": "Insufficient data for per-birth ITS"}
    log.warning("Insufficient data for per-birth ITS")

# ---- Per-enrollment spending (where available) ----
df_enroll = df[df["compulsory_education_enrollment_millions"].notna()].copy()
df_enroll["spending_per_enrollment"] = df_enroll["real_national"] / df_enroll["compulsory_education_enrollment_millions"]

log.info("\nReal spending per enrolled student (national):")
for _, row in df_enroll.iterrows():
    log.info(f"  {int(row['year'])}: {row['spending_per_enrollment']:.2f} yuan/student "
             f"(enrollment={row['compulsory_education_enrollment_millions']:.2f}M)")


# ==== Figure: Compositional analysis ====
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# (a) Share changes bar chart
ax = axes[0, 0]
y_pos = np.arange(len(share_df))
colors = ["#F44336" if "education" in row["col"] else "#2196F3"
          for _, row in share_df.iterrows()]
ax.barh(y_pos, share_df["change_pp"], color=colors, edgecolor="black", linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(share_df["category"], fontsize=9)
ax.set_xlabel("Change in consumption share [pp]")
ax.axvline(0, color="black", linewidth=0.5)
ax.text(0.02, 0.98, "(a) Share changes: 2019 vs post-policy avg",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

# (b) Education share time series
ax = axes[0, 1]
years_cons = cons["year"]
edu_share = cons["education_culture_recreation_share_pct"]
ax.plot(years_cons, edu_share, "o-", color="#F44336", linewidth=2, label="Education/culture/rec")
ax.axhline(edu_share.iloc[0], color="gray", linestyle=":", linewidth=1, label=f"2019 level ({edu_share.iloc[0]:.1f}%)")
ax.axvline(2021, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Year")
ax.set_ylabel("Share of total consumption [%]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "(b) Education share trajectory",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

# (c) All category shares
ax = axes[1, 0]
cat_colors = ["#F44336", "#E91E63", "#9C27B0", "#3F51B5",
              "#2196F3", "#FF9800", "#4CAF50", "#607D8B"]
for i, col in enumerate(share_cols):
    name = category_names.get(col, col)
    lw = 2.5 if "education" in col else 1
    alpha = 1.0 if "education" in col else 0.6
    ax.plot(years_cons, cons[col], "o-", color=cat_colors[i], linewidth=lw,
            alpha=alpha, markersize=4, label=name)
ax.axvline(2021, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Year")
ax.set_ylabel("Share of total consumption [%]")
ax.legend(fontsize="x-small", loc="center left", bbox_to_anchor=(0.0, 0.5))
ax.text(0.02, 0.98, "(c) All category shares",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

# (d) Per-child spending
ax = axes[1, 1]
valid_mask = df["births_millions"].notna()
ax.plot(df.loc[valid_mask, "year"],
        df.loc[valid_mask, "real_national"] / df.loc[valid_mask, "births_millions"],
        "o-", color="#2196F3", linewidth=2, label="Per birth")

enroll_mask = df["compulsory_education_enrollment_millions"].notna()
ax.plot(df.loc[enroll_mask, "year"],
        df.loc[enroll_mask, "real_national"] / df.loc[enroll_mask, "compulsory_education_enrollment_millions"],
        "s-", color="#4CAF50", linewidth=2, label="Per enrolled student")

ax.axvline(2021, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Year")
ax.set_ylabel("Real spending per child [2015 yuan]")
ax.legend(fontsize="small")
ax.text(0.02, 0.98, "(d) Per-child normalized spending",
        transform=ax.transAxes, fontsize=10, va="top", ha="left", fontweight="bold")

axes[0, 0].text(0.02, 1.06, "OpenPE Analysis", transform=axes[0, 0].transAxes, fontsize=8,
                va="top", ha="left", color="gray", style="italic")

fig.tight_layout()
fig.savefig(f"{FIG_DIR}/fig_p3_06_compositional.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(f"{FIG_DIR}/fig_p3_06_compositional.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info(f"\nSaved compositional figure to {FIG_DIR}/fig_p3_06_compositional.pdf")

# ---- Save results ----
comp_results = {
    "share_changes": {row["category"]: {
        "pre_2019": float(row["pre_2019"]),
        "post_avg": float(row["post_avg"]),
        "val_2025": float(row["val_2025"]),
        "change_pp": float(row["change_pp"]),
    } for _, row in share_df.iterrows()},
    "education_z_score": float(z_score),
    "education_change_pp": float(edu_change),
    "synthetic_ratio_pre": float(pre_ratio),
    "synthetic_ratio_post_avg": float(post_ratios.mean()),
    "synthetic_ratio_change": float(ratio_change),
    "perbirth_its": perbirth_results,
}

with open(f"{DATA_DIR}/compositional_results.json", "w") as f:
    json.dump(comp_results, f, indent=2)

log.info(f"Saved compositional results to {DATA_DIR}/compositional_results.json")
log.info("\nStep 4 (Compositional Analysis) complete.")
