"""
Forest plot (Figure 2) for OAB drugs across DBs (MSIP Python node)

Inputs (MSIP `table` -> pandas DataFrame):
  Required columns:
    - DB                 # "JADER" or "FAERS"
    - drug_of_interest   # ASCII lowercase token
    - n11                # co-occurrence count per drug (used as N here)
    - ROR, ROR025, ROR975
  Optional columns (used if present):
    - p        (numeric) or p-value (display; e.g., "<0.05")
    - PRR025
    - chi2     or χ^2
    - IC025

Behavior:
  - Signals:
      Signal_ROR = (ROR025 > 1) & (p < 0.05)
      Signal_PRR = (PRR025 > 2) & (chi2 > 4)    # if both columns exist
      Signal_IC  = (IC025 > 0)                  # if present
  - IC025 color legend: <1.5, 1.5–<3.0, >=3.0 (Okabe–Ito Blue, alpha gradation)
  - Saves PNG & TIFF in the working directory.

Outputs:
  - PNGObject for the PNG file
  - Prints file paths for PNG/TIFF
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

# Headless backend & font
matplotlib.use("Agg")
plt.rcParams["font.family"] = "Arial"
check_font = fm.FontProperties(family="DejaVu Sans")  # for '✓'

# -------- I/O paths --------
png_path = os.path.abspath("./figure2_forest_plot.png")
tiff_path = os.path.abspath("./figure2_forest_plot.tif")

# -------- Load data --------
df = table.to_pandas().copy()

# --- Normalize p / chi2 column names and values ---
# numeric p: prefer 'p' if available; otherwise coerce from 'p-value'
p_col = None
if "p" in df.columns:
    df["p"] = pd.to_numeric(df["p"], errors="coerce")
    p_col = "p"
elif "p-value" in df.columns:
    # "<0.05" -> 0.05 (display-style string to numeric)
    df["p"] = (
        df["p-value"].astype(str)
        .str.replace("<", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )
    p_col = "p"

# chi2 column (accept either ASCII or Greek chi)
chi2_col = "chi2" if "chi2" in df.columns else ("χ^2" if "χ^2" in df.columns else None)

# --- Signals (only if required columns exist) ---
df["Signal_ROR"] = False
if p_col is not None:
    df["Signal_ROR"] = (df["ROR025"] > 1) & (df[p_col] < 0.05)

df["Signal_PRR"] = False
if ("PRR025" in df.columns) and (chi2_col is not None):
    df["Signal_PRR"] = (df["PRR025"] > 2) & (df[chi2_col] > 4)

df["Signal_IC"] = False
if "IC025" in df.columns:
    df["Signal_IC"] = df["IC025"] > 0

# --- IC color function (Okabe–Ito Blue with alpha gradation) ---
def get_ic_color(ic025):
    if pd.isnull(ic025):
        return None
    if ic025 < 1.5:
        return mcolors.to_rgba("#0072B2", 0.3)
    if ic025 < 3.0:
        return mcolors.to_rgba("#0072B2", 0.7)
    return mcolors.to_rgba("#0072B2", 1.0)

# --- Formatting helpers ---
def format_ci(val, ci_min, ci_max):
    if pd.isnull(val) or pd.isnull(ci_min) or pd.isnull(ci_max):
        return ""
    return f"{val:.2f} ({ci_min:.2f}–{ci_max:.2f})"

def format_p(p):
    if pd.isnull(p):
        return ""
    if p < 0.001:
        return "<0.001"
    if p < 0.05:
        return "<0.05"
    return f"{p:.2f}"

# Display strings (use numeric p if available; else keep empty)
df["ROR_CI_str"] = df.apply(lambda r: format_ci(r["ROR"], r["ROR025"], r["ROR975"]), axis=1)
df["p_str"] = df[p_col].apply(format_p) if p_col is not None else ""

if "PRR025" in df.columns:
    df["PRR_str"] = df["PRR025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
if "IC025" in df.columns:
    df["IC_str"] = df["IC025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
if chi2_col is not None:
    df["chi2_str"] = df[chi2_col].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")

# -------- Layout config --------
# Column labels (EBGM excluded)
col_labels = ["Drug", "N", "ROR (95% CI)", "P value", "PRR025", "χ$^{2}$", "IC025", "Forest plot of ROR"]

# X positions per column (header row)
col_x_dict = {
    "Drug": 1.5, "N": 3.0, "ROR (95% CI)": 5.0, "P value": 7.5,
    "PRR025": 9.0, "χ$^{2}$": 10.5, "IC025": 12.0
}
# Forest panel range
plot_start = col_x_dict["IC025"] + 1.0
plot_end = plot_start + 4.0
col_x_dict["Forest plot of ROR"] = (plot_start + plot_end) / 2.0
# Signal boxes
col_x_dict["ROR"] = plot_end + 1.0
col_x_dict["PRR"] = plot_end + 2.0
col_x_dict["IC"]  = plot_end + 3.0

fig_width = max(col_x_dict.values()) + 0.8
row_height = 0.8
row_bg_color = "#f2f2f2"
line_color = "#0072B2"
marker_color = "#0072B2"
ref_line_color = "#D55E00"
db_colors = {"JADER": "#fce4d6", "FAERS": "#ddebf7"}
default_db_color = "#e0e0e0"

# -------- Prepare rows: group by DB, then header, then data --------
rows = []
for db, sub_df in df.groupby("DB"):
    rows.append(("db", db, db_colors.get(db, default_db_color)))
    rows.append(("header", None, None))
    for _, row in sub_df.iterrows():
        rows.append(("data", row, None))

num_rows = len(rows) + 2
fig_height = row_height * (num_rows + 1)

fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.set_xlim(0, fig_width)
ax.set_ylim(-0.5, num_rows - 0.5)
ax.axis("off")

# -------- X mapping for ROR axis (log10 scale from 0.5 to xmax) --------
max_ror975 = df["ROR975"].max(skipna=True)
xmax = max(20.0, float(max_ror975) * 1.5 if pd.notnull(max_ror975) else 20.0)
x_range_log = np.log10(xmax) - np.log10(0.5)

def ror_to_x(val):
    return plot_start + (np.log10(val) - np.log10(0.5)) * (plot_end - plot_start) / x_range_log

# Tick positions at {1,2,5}×10^k within [0.5, xmax]
tick_exp_min = int(np.floor(np.log10(0.5)))
tick_exp_max = int(np.ceil(np.log10(xmax)))
tick_values = sorted(set([
    base * 10**exp
    for exp in range(tick_exp_min, tick_exp_max + 1)
    for base in [1, 2, 5]
    if 0.5 <= base * 10**exp <= xmax
]))
tick_positions = [ror_to_x(v) for v in tick_values]

# -------- Render rows --------
data_row_ys = []
y_cursor = num_rows - 2

for kind, content, bg_color in rows:
    yc = y_cursor + 0.5

    if kind == "db":
        ax.axhspan(y_cursor, y_cursor + 1, color=bg_color, alpha=0.3)
        ax.text(0.5, yc, content, fontsize=18, fontweight="bold", ha="left", va="center")
        ax.hlines(y=y_cursor + 1, xmin=0, xmax=fig_width, color="black", linewidth=4)
        ax.hlines(y=y_cursor,     xmin=0, xmax=fig_width, color="black", linewidth=4)

    elif kind == "header":
        for label in col_labels:
            ax.text(col_x_dict[label], yc, label, fontsize=18, fontweight="bold", ha="center", va="center")
        ax.hlines(y=y_cursor + 1, xmin=0, xmax=fig_width, color="black", linewidth=4)
        ax.hlines(y=y_cursor,     xmin=0, xmax=fig_width, color="black", linewidth=3)
        for key in ["ROR", "PRR", "IC"]:
            ax.text(col_x_dict[key], yc, key, fontsize=18, fontweight="bold", ha="center", va="center")

    elif kind == "data":
        data_row_ys.append(y_cursor)
        row = content
        # zebra
        if y_cursor % 2 == 0:
            ax.axhspan(y_cursor, y_cursor + 1, color=row_bg_color)

        # left columns
        values = [
            row["drug_of_interest"], str(int(row["n11"])), row["ROR_CI_str"], row["p_str"]
        ]
        if "PRR_str" in row:
            values.append(row["PRR_str"])
        if "chi2_str" in row:
            values.append(row["chi2_str"])
        if "IC_str" in row:
            values.append(row["IC_str"])
        values += ["", "", ""]  # placeholders for ROR/PRR/IC signal boxes

        for j, val in enumerate(values):
            x = list(col_x_dict.values())[j]
            ax.text(x, yc, val, fontsize=16, ha="center", va="center")

        # forest CI and point estimate
        try:
            ci_min, ci_max, ror = row["ROR025"], row["ROR975"], row["ROR"]
            if pd.notnull(ci_min) and pd.notnull(ci_max):
                if ci_max >= 0.5 and ci_min <= xmax:
                    ci_min_x = ror_to_x(max(ci_min, 0.5))
                    ci_max_x = ror_to_x(min(ci_max, xmax))
                    ax.hlines(yc, ci_min_x, ci_max_x, color=line_color, linewidth=3, zorder=3)
                    if ci_min >= 0.5:
                        ax.vlines(ci_min_x, yc - 0.2, yc + 0.2, color=line_color, linewidth=3, zorder=3)
                    if ci_max <= xmax:
                        ax.vlines(ci_max_x, yc - 0.2, yc + 0.2, color=line_color, linewidth=3, zorder=3)
                    if 0.5 <= ror <= xmax:
                        ax.plot(ror_to_x(ror), yc, marker="s", color=marker_color, markersize=6)
                    if ci_min < 0.5:
                        ax.text(ror_to_x(0.5) - 0.2, yc, "<", fontsize=12, ha="right", va="center", color=line_color)
                    if ci_max > xmax:
                        ax.text(ror_to_x(xmax) + 0.2, yc, ">", fontsize=12, ha="left", va="center", color=line_color)
        except Exception:
            pass

        # Signal ticks
        if bool(row.get("Signal_ROR", False)):
            x = col_x_dict["ROR"]
            ax.add_patch(plt.Rectangle((x - 0.3, y_cursor + 0.25), 0.6, 0.6, color="#009E73"))
            ax.text(x, yc, "✓", fontsize=16, color="white", ha="center", va="center", fontproperties=check_font)
        if bool(row.get("Signal_PRR", False)):
            x = col_x_dict["PRR"]
            ax.add_patch(plt.Rectangle((x - 0.3, y_cursor + 0.25), 0.6, 0.6, color="#F0E442"))
            ax.text(x, yc, "✓", fontsize=16, color="black", ha="center", va="center", fontproperties=check_font)
        if bool(row.get("Signal_IC", False)):
            x = col_x_dict["IC"]
            ic_color = get_ic_color(row.get("IC025"))
            if ic_color is not None:
                ax.add_patch(plt.Rectangle((x - 0.3, y_cursor + 0.25), 0.6, 0.6, color=ic_color))
                ax.text(x, yc, "✓", fontsize=16, color="white", ha="center", va="center", fontproperties=check_font)

    y_cursor -= 1

# bottom border under last data block
if data_row_ys:
    ax.hlines(y=min(data_row_ys), xmin=0, xmax=fig_width, color="black", linewidth=4)

# reference vertical line at ROR=1, drawn per-DB block
x_ref = ror_to_x(1.0)
section_data_rows = []
y_cursor = num_rows - 2

for kind, content, _ in rows:
    if kind == "db":
        if section_data_rows:
            ymin = min(section_data_rows)
            ymax = max(section_data_rows) + 1
            ax.vlines(x_ref, ymin=ymin, ymax=ymax, color=ref_line_color, linestyle="--", linewidth=3)
            section_data_rows = []
    elif kind == "data":
        section_data_rows.append(y_cursor)
    y_cursor -= 1

if section_data_rows:
    ymin = min(section_data_rows)
    ymax = max(section_data_rows) + 1
    ax.vlines(x_ref, ymin=ymin, ymax=ymax, color=ref_line_color, linestyle="--", linewidth=3, zorder=2)

# x-axis tick labels for ROR scale
for x, val in zip(tick_positions, tick_values):
    ax.text(x, 0.5, str(val), ha="center", va="top", fontsize=12)
    ax.vlines(x, ymin=1, ymax=0.7, color="black", linewidth=3)

# IC025 legend (ASCII labels)
legend_items = [
    ("IC025 < 1.5",  mcolors.to_rgba("#0072B2", 0.3)),
    ("1.5 <= IC025 < 3.0", mcolors.to_rgba("#0072B2", 0.7)),
    ("IC025 >= 3.0", mcolors.to_rgba("#0072B2", 1.0)),
]

legend_box_width = 0.6
text_spacing = 0.2
inter_item_spacing = 0.5

# To measure text width in data coords, we need a draw first
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
transform = ax.transData

def text_width_in_data(s: str) -> float:
    txt = ax.text(0, 0, s, fontsize=14)
    bbox = txt.get_window_extent(renderer=renderer)
    inv = ax.transData.inverted()
    width_data = inv.transform((bbox.width, 0))[0] - inv.transform((0, 0))[0]
    txt.remove()
    return width_data

item_widths = [legend_box_width + text_spacing + text_width_in_data(lbl) + inter_item_spacing
               for (lbl, _) in legend_items]

legend_total_width = sum(item_widths)
legend_x_start = fig_width - legend_total_width
legend_y = -0.6

x = legend_x_start
for (label, color), width in zip(legend_items, item_widths):
    ax.add_patch(plt.Rectangle((x, legend_y), legend_box_width, 0.6, color=color))
    ax.text(x + legend_box_width + text_spacing, legend_y + 0.3, label, fontsize=14, va="center", ha="left")
    x += width

# Save
fig.savefig(png_path,  dpi=300, bbox_inches="tight", pad_inches=0.1)
fig.savefig(tiff_path, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
plt.close(fig)

result = PNGObject(png_path)
print("PNG saved to:", png_path)
print("TIFF saved to:", tiff_path)
