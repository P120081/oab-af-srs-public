"""
Volcano plot for a single OAB drug (MSIP Python node)

Inputs (MSIP):
- table: DataFrame with at least the following columns
    DB                # "JADER" or "FAERS" (for color)
    Subgroup          # e.g., "Overall", "Female", "Male", "20-60s", "70-90s", "Drugs>=5"
    n11               # co-occurrence count (used for point size; rows with n11<3 are dropped)
    ROR               # odds ratio (used for x = lnROR)
    p  or p-value     # numeric p (preferred) or display p-value like "<0.05"

Optional columns (kept if present): n12, n21, n22, PRR, PRR025, PRR975, chi2, IC, IC025, IC975, drug_of_interest

Outputs:
- PNG file saved to working directory
- PNGObject returned as MSIP node result
"""

# MSIP
from msi.common.dataframe import DataFrame
from msi.common.visualization import PNGObject

# General
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

# Font (paper-ready)
plt.rcParams["font.family"] = "Arial"

# Label placement
x_offset = 0.02
y_offset = 0.0
ha = "left"
va = "top"

# --- Load data from MSIP ---
df = table.to_pandas()

# --- Normalize headers/values for robustness ---
# 1) Prefer numeric 'p'; if only 'p-value' exists (e.g., "<0.05"), coerce to float
if "p" in df.columns:
    df["p"] = pd.to_numeric(df["p"], errors="coerce")
elif "p-value" in df.columns:
    df["p"] = (
        df["p-value"].astype(str)
        .str.replace("<", "", regex=False)   # "<0.05" -> "0.05"
        .pipe(pd.to_numeric, errors="coerce")
    )

# 2) ASCII-only Subgroup labels (normalize '≥' -> '>=')
if "Subgroup" in df.columns:
    df["Subgroup"] = df["Subgroup"].astype(str).str.replace("≥", ">=")

# 3) Basic numeric conversions
df["ROR"] = pd.to_numeric(df["ROR"], errors="coerce")
df["n11"] = pd.to_numeric(df["n11"], errors="coerce")

# 4) Guard p==0 for -log10
df.loc[df["p"] <= 0, "p"] = 1e-300

# 5) Drop missing and n11 < 3 (as per analysis rule)
df = df.dropna(subset=["ROR", "p", "n11"])
df = df[df["n11"] >= 3]

# --- Log transforms (ASCII column names for internal use) ---
df["lnROR"] = np.log(df["ROR"])
df["neglog10_p"] = -np.log10(df["p"])

# --- Color map (Okabe-Ito) ---
okabe_ito_palette = {
    "Orange":   "#E69F00",
    "SkyBlue":  "#56B4E9",
}
db_color_map = {
    "JADER": okabe_ito_palette["Orange"],
    "FAERS": okabe_ito_palette["SkyBlue"],
}
df["color"] = df["DB"].map(db_color_map)

# --- Size mapping from n11 ---
def map_n11_to_size(n: float) -> float:
    if n < 10:
        return 40
    elif n < 100:
        return 90
    elif n < 200:
        return 140
    else:
        return 200

df["size"] = df["n11"].apply(map_n11_to_size)

# --- Plot ---
fig, ax = plt.subplots(figsize=(7.09, 5.3))  # ~180mm x 135mm
for db in df["DB"].dropna().unique():
    sub = df[df["DB"] == db]
    ax.scatter(
        sub["lnROR"], sub["neglog10_p"],
        s=sub["size"], c=sub["color"], alpha=0.6
    )

# Label only if p < 0.05
for _, row in df.iterrows():
    if row["p"] < 0.05:
        label = f"{row['Subgroup']}\n({int(row['n11'])})"
        # Note: Subgroup already normalized to '>=' above
        y_offset_custom = -0.15 if row["Subgroup"] == "Drugs>=5" else y_offset
        t = ax.text(
            row["lnROR"] + x_offset,
            row["neglog10_p"] + y_offset_custom,
            label,
            fontsize=8, ha=ha, va=va, color="black",
        )
        t.set_path_effects([
            path_effects.Stroke(linewidth=1.5, foreground="white"),
            path_effects.Normal()
        ])

# Threshold lines: p=0.05 (~1.30103), lnROR=0
ax.axhline(y=1.3, color="black", linestyle="--", linewidth=1)
ax.axvline(x=0.0, color="black", linestyle="--", linewidth=1)

# Axes and grid
ax.set_xlabel("lnROR", fontsize=14)
ax.set_ylabel("-log10(p-value)", fontsize=14)
ax.grid(True)
plt.tick_params(axis="both", labelsize=12)

# Drug name box (top-right). If available, infer from 'drug_of_interest'.
if "drug_of_interest" in df.columns and not df["drug_of_interest"].isna().all():
    doi = str(df["drug_of_interest"].dropna().iloc[0])
    drug_name_text = f"Drug: {doi.capitalize()}"
else:
    drug_name_text = "Drug: Solifenacin"  # change as needed

ax.text(
    0.99, 0.99, drug_name_text,
    transform=ax.transAxes, fontsize=12, ha="right", va="top",
    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
)

plt.tight_layout()

# Save
out_path = os.path.abspath("./volcano_plot.png")
plt.savefig(out_path, dpi=300)
plt.close()

# MSIP result
result = PNGObject(out_path)
