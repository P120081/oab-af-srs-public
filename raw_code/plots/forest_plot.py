"""
Figure 2 — Forest plot (single-drug per DB section)
MSIP Python node

Inputs
- table: DataFrame with columns (minimum)
    DB, drug_of_interest, n11, ROR, ROR025, ROR975
  Optional: p (or p-value), PRR025, chi2 (or x2, or 'χ^2'), IC025

Behavior
- Draws a forest plot of ROR with 95% CI per subgroup row.
- Highlights "Overall" row as a diamond.
- Annotates signal boxes for ROR/PRR/IC using conventional thresholds:
    ROR: n11>=3 & p<0.05 & ROR025>1
    PRR: n11>=3 & chi2>4 & PRR025>2
    IC : n11>=3 & IC025>0

Outputs
- figure2_forest_plot.png and figure2_forest_plot.tif saved to CWD
- Returns PNGObject for MSIP
"""

from msi.common.visualization import PNGObject

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties

# Font
plt.rcParams['font.family'] = 'Arial'

# Load
df = table.to_pandas()

# Normalize columns
def coerce_num(series, prefer=None):
    if series is None:
        return None
    try:
        return pd.to_numeric(series, errors="coerce")
    except Exception:
        return None

def pick_col(d, names):
    for n in names:
        if n in d.columns:
            return n
    return None

p_col = pick_col(df, ["p","p-value"])
if p_col and p_col != "p":
    df["p"] = pd.to_numeric(df[p_col].astype(str).str.replace("<","",regex=False), errors="coerce")

if "chi2" not in df.columns:
    alt = pick_col(df, ["x2","χ^2"])
    if alt:
        df["chi2"] = coerce_num(df[alt])
else:
    df["chi2"] = coerce_num(df["chi2"])

for c in ["n11","ROR","ROR025","ROR975","PRR025","IC025"]:
    if c in df.columns:
        df[c] = coerce_num(df[c])

# Display strings
def fmt_ci(val, lo, hi):
    if pd.isna(val) or pd.isna(lo) or pd.isna(hi): return ""
    return f"{val:.2f} ({lo:.2f}-{hi:.2f})"

def fmt_p(p):
    if pd.isna(p): return ""
    if p < 0.001: return "<0.001"
    if p < 0.05:  return "<0.05"
    return f"{p:.2f}"

df["ROR_CI_str"] = df.apply(lambda r: fmt_ci(r.get("ROR"), r.get("ROR025"), r.get("ROR975")), axis=1)
if "p" in df.columns: df["p_str"] = df["p"].apply(fmt_p)
if "PRR025" in df.columns: df["PRR_str"] = df["PRR025"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "")
if "IC025"  in df.columns: df["IC_str"]  = df["IC025"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "")
if "chi2"   in df.columns: df["chi2_str"]= df["chi2"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "")

# Layout and colors
row_bg = "#f2f2f2"
line_color = "#0072B2"
marker_color = "#0072B2"
ref_color = "#D55E00"
db_hdr = {"JADER":"#fce4d6","FAERS":"#ddebf7"}

# Column positions (data region is log scale from 0.5 to xmax)
col_x = {"Subgroup": 1.5, "N": 3.0, "ROR (95% CI)": 5.0, "P value": 7.5, "PRR025": 9.0, "chi2": 10.5, "IC025": 12.0}
plot_start = col_x["IC025"] + 1.0
plot_end   = plot_start + 4.0
col_x["Forest plot of ROR"] = (plot_start + plot_end) / 2.0
col_x["ROR"]  = plot_end + 1.0
col_x["PRR"]  = plot_end + 2.0
col_x["IC"]   = plot_end + 3.0

# X scale
xmax = max(20.0, float(df["ROR975"].max(skipna=True)) * 1.5)
def ror_to_x(val):
    lo, hi = 0.5, xmax
    return plot_start + (np.log10(val) - np.log10(lo)) * (plot_end - plot_start) / (np.log10(hi) - np.log10(lo))

ticks = [v for v in [0.5,1,2,5,10,20,50,100] if v <= xmax]
tick_pos = [ror_to_x(v) for v in ticks]

# Row blocks by DB
rows = []
for db, sub in df.groupby("DB"):
    rows.append(("db", db))
    rows.append(("header", None))
    for _, r in sub.iterrows():
        rows.append(("data", r))

num_rows = len(rows) + 2
fig_h = 0.8 * (num_rows + 1)
fig_w = max(col_x.values()) + 0.8
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_xlim(0, fig_w); ax.set_ylim(-0.5, num_rows - 0.5); ax.axis("off")

# Draw
y = num_rows - 2
data_section_ys = []
for kind, payload in rows:
    yc = y + 0.5
    if kind == "db":
        db = payload
        ax.axhspan(y, y+1, color=db_hdr.get(db, "#e0e0e0"), alpha=0.3)
        ax.text(0.5, yc, db, fontsize=18, fontweight="bold", ha="left", va="center")
        ax.hlines(y=y+1, xmin=0, xmax=fig_w, color="black", linewidth=4)
        ax.hlines(y=y,   xmin=0, xmax=fig_w, color="black", linewidth=4)
    elif kind == "header":
        for label in ["Subgroup","N","ROR (95% CI)","P value","PRR025","chi2","IC025","Forest plot of ROR","ROR","PRR","IC"]:
            ax.text(col_x[label], yc, label, fontsize=16, fontweight="bold", ha="center", va="center")
        ax.hlines(y=y+1, xmin=0, xmax=fig_w, color="black", linewidth=3)
        ax.hlines(y=y,   xmin=0, xmax=fig_w, color="black", linewidth=3)
    elif kind == "data":
        r = payload
        data_section_ys.append(y)
        if y % 2 == 0:
            ax.axhspan(y, y+1, color=row_bg)
        values = [
            r.get("Subgroup",""), f"{int(r.get('n11',0))}", r.get("ROR_CI_str",""), r.get("p_str",""),
            r.get("PRR_str",""), r.get("chi2_str",""), r.get("IC_str",""), ""
        ]
        for j, val in enumerate(values):
            x = list(col_x.values())[j]
            ax.text(x, yc, val, fontsize=14, ha="center", va="center")
        # CI bar
        try:
            lo, hi, mid = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
            if hi >= 0.5 and lo <= xmax:
                x_lo = ror_to_x(max(lo, 0.5))
                x_hi = ror_to_x(min(hi, xmax))
                ax.hlines(yc, x_lo, x_hi, color=line_color, linewidth=3, zorder=3)
                if lo >= 0.5: ax.vlines(x_lo, yc-0.2, yc+0.2, color=line_color, linewidth=3, zorder=3)
                else: ax.text(ror_to_x(0.5)-0.2, yc, "<", fontsize=12, ha="right", va="center", color=line_color)
                if hi <= xmax: ax.vlines(x_hi, yc-0.2, yc+0.2, color=line_color, linewidth=3, zorder=3)
                else: ax.text(ror_to_x(xmax)+0.2, yc, ">", fontsize=12, ha="left", va="center", color=line_color)
                if 0.5 <= mid <= xmax: ax.plot(ror_to_x(mid), yc, marker="s", color=marker_color, markersize=6)
        except Exception:
            pass
        # Overall diamond if Subgroup == "Overall"
        if str(r.get("Subgroup","")).strip().lower() == "overall":
            try:
                lo, hi, mid = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
                dx = [ror_to_x(lo), ror_to_x(mid), ror_to_x(hi), ror_to_x(mid), ror_to_x(lo)]
                dy = [yc, yc+0.15, yc, yc-0.15, yc]
                ax.fill(dx, dy, color="#D55E00", alpha=1.0, zorder=2)
            except Exception:
                pass
        # Signal flags
        n = float(r.get("n11",0) or 0)
        p = float(r.get("p",1) or 1)
        ror025 = float(r.get("ROR025",0) or 0)
        prr025 = float(r.get("PRR025",0) or 0)
        chi2   = float(r.get("chi2",0) or 0)
        ic025  = float(r.get("IC025",0) or 0)
        def _box(xc, color, text_color):
            ax.add_patch(plt.Rectangle((xc - 0.3, y + 0.25), 0.6, 0.6, color=color))
            ax.text(xc, yc, "✓", fontsize=14, color=text_color, ha="center", va="center")
        if n >= 3 and p < 0.05 and ror025 > 1: _box(col_x["ROR"], "#009E73", "white")
        if n >= 3 and chi2 > 4 and prr025 > 2: _box(col_x["PRR"], "#F0E442", "black")
        if n >= 3 and ic025 > 0: _box(col_x["IC"], mcolors.to_rgba("#0072B2", 0.7), "white")
    y -= 1

# vertical ref line at ROR=1 for each DB section
if data_section_ys:
    ymin = min(data_section_ys); ymax = max(data_section_ys)+1
    ax.vlines(ror_to_x(1.0), ymin=ymin, ymax=ymax, color=ref_color, linestyle="--", linewidth=3, zorder=2)

# X ticks
for x, val in zip(tick_pos, ticks):
    ax.text(x, 0.5, str(val), ha="center", va="top", fontsize=12)
    ax.vlines(x, ymin=1, ymax=0.7, color="black", linewidth=3)

# Save
png_path  = os.path.abspath("./figure2_forest_plot.png")
tiff_path = os.path.abspath("./figure2_forest_plot.tif")
fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
fig.savefig(tiff_path, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
plt.close(fig)

result = PNGObject(png_path)
