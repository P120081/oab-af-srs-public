"""
Figure 3 — Multi-drug forest plot (MSIP Python node)

This script renders a forest plot grouped by drug and DB (JADER/FAERS),
with per-subgroup rows and signal check boxes (ROR/PRR/IC).

Inputs (MSIP `table` -> pandas DataFrame)
Required columns:
  - DB                      # "JADER" or "FAERS"
  - drug_of_interest        # ASCII token (e.g., "solifenacin")
  - Subgroup                # e.g., "Male", "Female", "20-60s", "70-90s", "Drugs>=5", "Overall"
  - n11                     # used as N in table
  - ROR, ROR025, ROR975

Optional columns (auto-detected if present):
  - p (numeric) OR p-value (display, e.g. "<0.05")
  - PRR, PRR025, PRR975
  - chi2 OR χ^2
  - IC, IC025, IC975

Signals:
  - ROR:  (ROR025 > 1) & (p < 0.05)
  - PRR:  (PRR025 > 2) & (chi2 > 4)
  - IC:   (IC025 > 0)

Outputs:
  - PNG:  ./figure3_forest.png
  - TIFF: ./figure3_forest.tif
  - MSIP result: PNGObject of the PNG
"""

# MSIP
from msi.common.dataframe import DataFrame
from msi.common.visualization import PNGObject

# General
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors

# Headless + fonts
matplotlib.use("Agg")
plt.rcParams["font.family"] = "Arial"
check_font = fm.FontProperties(family="DejaVu Sans")  # for the ✓ glyph

# ---------- I/O ----------
png_path  = os.path.abspath("./figure3_forest.png")
tiff_path = os.path.abspath("./figure3_forest.tif")

# ---------- Load ----------
df = table.to_pandas().copy()

# ---------- Normalize columns ----------
# p (numeric) from either 'p' or 'p-value'
if "p" in df.columns:
    df["p"] = pd.to_numeric(df["p"], errors="coerce")
elif "p-value" in df.columns:
    df["p"] = (
        df["p-value"].astype(str)
        .str.replace("<", "", regex=False)    # "<0.05" -> "0.05"
        .pipe(pd.to_numeric, errors="coerce")
    )
else:
    df["p"] = np.nan

# chi2 from either 'chi2' or 'χ^2'
if "chi2" not in df.columns and "χ^2" in df.columns:
    df["chi2"] = pd.to_numeric(df["χ^2"], errors="coerce")
elif "chi2" in df.columns:
    df["chi2"] = pd.to_numeric(df["chi2"], errors="coerce")

# ASCII for subgroup tokens (≥ -> >=)
df["Subgroup"] = df["Subgroup"].astype(str).str.replace("≥", ">=")

# ---------- Signals ----------
df["Signal_ROR"] = (df["ROR025"] > 1) & (df["p"] < 0.05)
df["Signal_PRR"] = False
if "PRR025" in df.columns and "chi2" in df.columns:
    df["Signal_PRR"] = (pd.to_numeric(df["PRR025"], errors="coerce") > 2) & (df["chi2"] > 4)
df["Signal_IC"] = False
if "IC025" in df.columns:
    df["Signal_IC"] = pd.to_numeric(df["IC025"], errors="coerce") > 0

# ---------- Display strings ----------
def format_ci(val, lo, hi):
    if pd.isna(val) or pd.isna(lo) or pd.isna(hi):
        return ""
    return f"{val:.2f} ({lo:.2f}–{hi:.2f})"

def format_p(p):
    if pd.isna(p):     return ""
    if p < 0.001:      return "<0.001"
    if p < 0.05:       return "<0.05"
    return f"{p:.2f}"

df["ROR_CI_str"] = df.apply(lambda r: format_ci(r["ROR"], r["ROR025"], r["ROR975"]), axis=1)
df["p_str"]       = df["p"].map(format_p)
if "PRR025" in df.columns: df["PRR_str"]  = df["PRR025"].apply(lambda v: f"{float(v):.2f}" if pd.notnull(v) else "")
if "IC025"  in df.columns: df["IC_str"]   = df["IC025"].apply(lambda v: f"{float(v):.2f}" if pd.notnull(v) else "")
if "chi2"   in df.columns: df["chi2_str"] = df["chi2"].apply(lambda v: f"{float(v):.2f}" if pd.notnull(v) else "")

# ---------- Colors ----------
# Okabe–Ito
signal_ror_color = "#009E73"  # green
signal_prr_color = "#F0E442"  # yellow
signal_ic_base   = "#0072B2"  # blue

line_color   = "#0072B2"
marker_color = "#0072B2"
fill_color   = "#D55E00"
ref_line     = "#D55E00"
row_bg       = "#f2f2f2"

db_colors = {"JADER": "#fce4d6", "FAERS": "#ddebf7"}
default_db_color = "#e0e0e0"

# per-drug banner color (muted Okabe–Ito, excluding signal colors)
oi_palette = ["#E69F00", "#56B4E9", "#CC79A7", "#000000"]
def drug_color_for(name, idx):
    base = oi_palette[idx % len(oi_palette)]
    return mcolors.to_rgba(base, 0.3)

# IC shade by IC025
def ic_color(ic025):
    if pd.isna(ic025): return None
    v = float(ic025)
    if v < 1.5: return mcolors.to_rgba(signal_ic_base, 0.3)
    if v < 3.0: return mcolors.to_rgba(signal_ic_base, 0.7)
    return mcolors.to_rgba(signal_ic_base, 1.0)

# ---------- Build row blocks (by drug then DB) ----------
row_height = 0.8
blocks = []
header_cols = ["Subgroup","N","ROR (95% CI)","P value","PRR025","χ²","IC025","Forest plot of ROR","ROR","PRR","IC"]

for d_idx, (drug, df_d) in enumerate(df.groupby("drug_of_interest")):
    blocks.append(("drug", drug, {"bg": drug_color_for(drug, d_idx)}))
    for db, df_db in df_d.groupby("DB"):
        blocks.append(("db", db, {"bg": db_colors.get(db, default_db_color)}))
        blocks.append(("header", header_cols, None))
        for _, r in df_db.iterrows():
            row_vals = [
                r["Subgroup"], f"{int(r['n11'])}", r["ROR_CI_str"], r["p_str"],
                r.get("PRR_str",""), r.get("chi2_str",""), r.get("IC_str",""),
                "", "", "", ""  # placeholders for signal boxes + forest panel
            ]
            blocks.append(("data", row_vals, r))

num_rows = len(blocks) + 2
fig_height = row_height * (num_rows + 2)

# ---------- Layout / axes ----------
col_x = {
    "Subgroup": 1.5, "N": 3.0, "ROR (95% CI)": 5.0, "P value": 7.5,
    "PRR025": 9.0, "χ²": 10.5, "IC025": 12.0
}
plot_start = col_x["IC025"] + 1.0
plot_end   = plot_start + 4.0
col_x["Forest plot of ROR"] = (plot_start + plot_end) / 2.0
col_x["ROR"] = plot_end + 1.0
col_x["PRR"] = plot_end + 2.0
col_x["IC"]  = plot_end + 3.0

fig_width = max(col_x.values()) + 0.6

max_ror975 = float(df["ROR975"].max(skipna=True))
xmax = max(20.0, max_ror975 * 1.5)
def ror_to_x(val):
    return plot_start + (np.log10(val) - np.log10(0.5)) * (plot_end - plot_start) / (np.log10(xmax) - np.log10(0.5))

tick_vals = [v for v in [0.5,1,2,5,10,20,50,100] if v <= xmax]
tick_pos  = [ror_to_x(v) for v in tick_vals]

fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, fig_width)
ax.set_ylim(-0.5, num_rows - 0.5)
ax.axis("off")

# ---------- Render ----------
y = num_rows - 2
section_rows = []
data_rows_in_section = []

for kind, content, meta in blocks:
    yc = y + 0.5

    if kind == "drug":
        ax.axhspan(y, y+1, color=meta["bg"])
        ax.text(0.5, yc, content, fontsize=24, fontweight="bold", ha="left", va="center")
        ax.hlines(y=y+1, xmin=0, xmax=fig_width, color="black", linewidth=4)

    elif kind == "db":
        # draw ROR=1 reference for previous section
        if data_rows_in_section:
            x_ref = ror_to_x(1.0)
            ax.vlines(x_ref, ymin=min(data_rows_in_section), ymax=max(data_rows_in_section)+1,
                      color=ref_line, linestyle="--", linewidth=3, zorder=1)
            data_rows_in_section = []
        ax.axhspan(y, y+1, color=meta["bg"], alpha=0.3)
        ax.text(1.0, yc, content, fontsize=20, ha="left", va="center")
        ax.hlines(y=y+1, xmin=0, xmax=fig_width, color="black", linewidth=3)

    elif kind == "header":
        for label in content:
            if label in col_x:
                ax.text(col_x[label], yc, label, fontsize=20, fontweight="bold", ha="center", va="center")
        ax.hlines(y=y+1, xmin=0, xmax=fig_width, color="black", linewidth=3)
        ax.hlines(y=y,   xmin=0, xmax=fig_width, color="black", linewidth=3)

    elif kind == "data":
        if y % 2 == 0:
            ax.axhspan(y, y+1, color=row_bg)
        data_rows_in_section.append(y)

        # left cells
        vals = content
        for j, label in enumerate(vals):
            key = header_cols[j]
            if key in col_x:
                ax.text(col_x[key], yc, str(label), fontsize=18, ha="center", va="center")

        # forest element (CI / square / diamond for Overall)
        r = meta
        try:
            lo, hi, est = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
            if str(r["Subgroup"]).lower() != "overall":
                if hi >= 0.5 and lo <= xmax:
                    lo_x = ror_to_x(max(lo, 0.5)); hi_x = ror_to_x(min(hi, xmax))
                    ax.hlines(yc, lo_x, hi_x, color=line_color, linewidth=3, zorder=3)
                    if lo >= 0.5: ax.vlines(lo_x, yc-0.2, yc+0.2, color=line_color, linewidth=3, zorder=3)
                    else:         ax.text(lo_x-0.2, yc, "<", fontsize=14, ha="right", va="center", color=line_color)
                    if hi <= xmax: ax.vlines(hi_x, yc-0.2, yc+0.2, color=line_color, linewidth=3)
                    else:          ax.text(hi_x+0.2, yc, ">", fontsize=14, ha="left", va="center", color=line_color)
                    if 0.5 <= est <= xmax:
                        ax.plot(ror_to_x(est), yc, marker="s", markersize=6, color=marker_color)
            else:
                lo_x = ror_to_x(lo); hi_x = ror_to_x(hi); est_x = ror_to_x(est)
                dx = [lo_x, est_x, hi_x, est_x, lo_x]
                dy = [yc, yc+0.15, yc, yc-0.15, yc]
                ax.fill(dx, dy, color=fill_color, alpha=1, zorder=2)
                ax.hlines(y=y, xmin=0, xmax=fig_width, color="black", linewidth=3)
        except Exception:
            pass

        # signal boxes
        if bool(r.get("Signal_ROR", False)):
            x = col_x["ROR"]; ax.add_patch(plt.Rectangle((x-0.3, y+0.25), 0.6, 0.6, color=signal_ror_color))
            ax.text(x, yc, "✓", fontsize=18, color="white", ha="center", va="center", fontproperties=check_font)
        if bool(r.get("Signal_PRR", False)):
            x = col_x["PRR"]; ax.add_patch(plt.Rectangle((x-0.3, y+0.25), 0.6, 0.6, color=signal_prr_color))
            ax.text(x, yc, "✓", fontsize=18, color="black", ha="center", va="center", fontproperties=check_font)
        if bool(r.get("Signal_IC", False)):
            x = col_x["IC"];  col = ic_color(r.get("IC025"))
            if col is not None:
                ax.add_patch(plt.Rectangle((x-0.3, y+0.25), 0.6, 0.6, color=col))
                ax.text(x, yc, "✓", fontsize=18, color="white", ha="center", va="center", fontproperties=check_font)

    y -= 1

# draw final reference if needed
if data_rows_in_section:
    x_ref = ror_to_x(1.0)
    ax.vlines(x_ref, ymin=min(data_rows_in_section), ymax=max(data_rows_in_section)+1,
              color=ref_line, linestyle="--", linewidth=3, zorder=1)

# x-axis ticks for ROR scale
for x, val in zip(tick_pos, tick_vals):
    ax.text(x, 0.5, str(val), ha="center", va="top", fontsize=14)
    ax.vlines(x, ymin=1, ymax=0.7, color="black", linewidth=3)

# IC025 shade legend (ASCII labels)
legend_items = [
    ("IC025 < 1.5",          mcolors.to_rgba(signal_ic_base, 0.3)),
    ("1.5 <= IC025 < 3.0",   mcolors.to_rgba(signal_ic_base, 0.7)),
    ("IC025 >= 3.0",         mcolors.to_rgba(signal_ic_base, 1.0)),
]

legend_box_w = 0.6
text_spacing = 0.2
gap = 0.5

# measure text widths in data coords
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
def text_width(s):
    t = ax.text(0, 0, s, fontsize=14)
    bb = t.get_window_extent(renderer=renderer)
    inv = ax.transData.inverted()
    w  = inv.transform((bb.width, 0))[0] - inv.transform((0, 0))[0]
    t.remove()
    return w

item_w = [legend_box_w + text_spacing + text_width(lbl) + gap for (lbl, _) in legend_items]
legend_total = sum(item_w)
legend_x0 = fig_width - legend_total
legend_y  = -0.6

x = legend_x0
for (lbl, col), w in zip(legend_items, item_w):
    ax.add_patch(plt.Rectangle((x, legend_y), legend_box_w, 0.6, color=col))
    ax.text(x + legend_box_w + text_spacing, legend_y + 0.3, lbl, fontsize=14, va="center", ha="left")
    x += w

# Save
fig.savefig(png_path,  dpi=300, bbox_inches="tight", pad_inches=0.1)
fig.savefig(tiff_path, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
plt.close(fig)

result = PNGObject(png_path)
print("PNG saved to:", png_path)
print("TIFF saved to:", tiff_path)
