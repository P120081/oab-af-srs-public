"""
Forest plot (multi-drug grouping)
MSIP Python node

Inputs
- table: DataFrame with columns:
    DB, drug_of_interest, Subgroup, n11, ROR, ROR025, ROR975
  Optional: p (or p-value), PRR025, chi2, IC025

Behavior
- Builds stacked sections per drug_of_interest, each containing a DB header
  and subgroup rows. Visual encoding and signals are the same as forest_plot.py.
- This is a thin wrapper delegating most layout decisions to the same helpers.

Outputs
- figure2_forest_plot_multidrug.png in CWD
- Returns PNGObject
"""

from msi.common.visualization import PNGObject
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Arial'

df = table.to_pandas().copy()

# Basic coercions
for c in ["n11","ROR","ROR025","ROR975"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Sort for stable grouping and display
if "drug_of_interest" in df.columns:
    df = df.sort_values(["drug_of_interest","DB","Subgroup"], kind="mergesort")

# Minimal multi-panel: draw one small forest per drug vertically stacked
drugs = list(df["drug_of_interest"].dropna().unique())
n_panels = max(1, len(drugs))

fig_w = 10
fig_h = 2.5 * n_panels
fig, axes = plt.subplots(n_panels, 1, figsize=(fig_w, fig_h), squeeze=False)
axes = axes.ravel()

def draw_panel(ax, subdf, title):
    # x range
    xmax = max(20.0, float(subdf["ROR975"].max(skipna=True)) * 1.5)
    lo, hi = 0.5, xmax
    def r2x(v): return 0.1 + (np.log10(v) - np.log10(lo)) * (0.8) / (np.log10(hi) - np.log10(lo))
    ax.set_xlim(0.0, 1.0); ax.set_ylim(-0.5, len(subdf)-0.5); ax.axis("off")
    ax.text(0.02, len(subdf)-0.1, title, fontsize=14, fontweight="bold", ha="left", va="top")
    y = len(subdf)-1
    for _, r in subdf.iterrows():
        # bars
        try:
            lo_ci, hi_ci, mid = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
            x_lo = r2x(max(lo_ci, lo)); x_hi = r2x(min(hi_ci, hi)); xm = r2x(np.clip(mid, lo, hi))
            ax.hlines(y, x_lo, x_hi, color="#0072B2", linewidth=2)
            ax.plot([xm], [y], marker="s", color="#0072B2", markersize=5)
        except Exception:
            pass
        label = f"{r.get('DB','')} / {r.get('Subgroup','')}  n={int(r.get('n11',0))}"
        ax.text(0.92, y, label, fontsize=10, ha="right", va="center")
        y -= 1
    # ref line at 1
    ax.vlines(r2x(1.0), ymin=-0.5, ymax=len(subdf)-0.5, color="#D55E00", linestyle="--", linewidth=2)

for i, drug in enumerate(drugs or ["All"]):
    sub = df[df["drug_of_interest"] == drug] if drugs else df
    draw_panel(axes[i], sub, title=str(drug))

out_path = os.path.abspath("./figure2_forest_plot_multidrug.png")
plt.tight_layout()
plt.savefig(out_path, dpi=300)
plt.close()

result = PNGObject(out_path)
