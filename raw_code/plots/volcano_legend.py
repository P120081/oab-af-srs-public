"""
Legend-only figure for the volcano plot (MSIP Python node)

- Colors: Okabe-Ito palette (JADER = Orange, FAERS = SkyBlue)
- Sizes: mapped from n11 thresholds consistent with the volcano plot
- Output: transparent PNG with just the legend (no axes)

Inputs: none (standalone)
Outputs:
  - PNG saved to working directory as 'volcano_legend_only.png'
  - PNGObject returned as MSIP node result
"""

# MSIP
from msi.common.visualization import PNGObject

# General
import os
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# Paper-ready font
plt.rcParams["font.family"] = "Arial"

# --- Okabe-Ito palette (keys align with volcano_plot.py) ---
okabe_ito_palette = {
    "Orange":  "#E69F00",
    "SkyBlue": "#56B4E9",
}

# DB -> color
db_color_map = {
    "JADER": okabe_ito_palette["Orange"],
    "FAERS": okabe_ito_palette["SkyBlue"],
}

# --- Size mapping consistent with volcano_plot.py ---
def map_n11_to_size(n: float) -> float:
    if n < 10:
        return 40
    elif n < 100:
        return 90
    elif n < 200:
        return 140
    else:
        return 200

# Size legend bins/labels (ASCII only)
size_bins   = [(0, 10), (10, 100), (100, 200), (200, float("inf"))]
size_labels = ["n < 10", "10 <= n < 100", "100 <= n < 200", "n >= 200"]
# Representative sizes (midpoints; last bin uses a large sentinel)
size_vals = [
    map_n11_to_size((low + (high if high != float("inf") else 250)) // 2)
    for (low, high) in size_bins
]

# --- Build legend-only figure ---
fig, ax = plt.subplots(figsize=(4.0, 2.0))  # compact legend canvas
ax.axis("off")

legend_handles = []

# Color legend (DB)
for db, color in db_color_map.items():
    legend_handles.append(
        mlines.Line2D([], [], color=color, marker="o",
                      linestyle="None", markersize=8, label=db)
    )

# Size legend (n11)
for s, label in zip(size_vals, size_labels):
    # empty scatter just to show marker size
    handle = plt.scatter([], [], s=s, color="gray", alpha=0.6, label=label)
    legend_handles.append(handle)

# Prefix line explaining text labels in the volcano plot
legend_handles.insert(0, mlines.Line2D([], [], linestyle="None", label="Label: Subgroup (n)"))

legend = ax.legend(
    handles=legend_handles,
    title="DB / Report Count",
    loc="center",
    fontsize=10,
    title_fontsize=11,
    borderpad=1.0,
    labelspacing=1.0,
    handletextpad=1.2,
    frameon=False,
)

# --- Save & return ---
out_path = os.path.abspath("./volcano_legend_only.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight", transparent=True)
plt.close()

result = PNGObject(out_path)
