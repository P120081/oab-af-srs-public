"""
Figure 6 — Kaplan–Meier style cumulative curve (raw TTO, 4 groups)
MSIP Python node

Assumptions
- Input table is MSIP DataFrame convertible to pandas via `table.to_pandas()`.
- Columns (case-insensitive) are expected as:
    * DB code/name: one of {"db"} or column #0 (fallback).
      Accepts numeric 1/2 or strings "JADER"/"FAERS".
    * drug name: one of {"prod_ai","drug","product"} or column #1 (fallback).
      Expect standardized generic names (e.g., "MIRABEGRON","SOLIFENACIN").
    * TTO (days): one of {"tto","days","time","time_to_onset"} or column #2 (fallback).
      Non-numeric/negative rows are dropped.
- Four curves are drawn: JADER/FAERS × MIRABEGRON/SOLIFENACIN.
  MIRABEGRON is plotted with dash-dot line style.

Output
- Saves `./figure6_km_raw.png` (RGB, 300 dpi, width 180 mm, height 120 mm).
- Returns PNGObject for MSIP.
"""

# MSIP
from msi.common.visualization import PNGObject

# General
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# ---------------- Config ----------------
# Font (unified across repo)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"]   = 12

# Okabe–Ito palette
OKABE_ITO = {
    "Orange":  "#E69F00",  # JADER
    "SkyBlue": "#56B4E9",  # FAERS
}

# Figure size: width 180 mm × height 120 mm
MM_TO_INCH = 1.0 / 25.4
FIG_W = 180 * MM_TO_INCH  # 7.0866 in
FIG_H = 120 * MM_TO_INCH  # 4.7244 in

# X-range: 0–730 days
X_RIGHT = 730

# ---------------- Load ----------------
df = table.to_pandas()

def _find_col(candidates_lower, fallback_idx):
    cols = list(df.columns)
    for c in cols:
        if str(c).strip().lower() in candidates_lower:
            return c
    return cols[fallback_idx]

DB_COL   = _find_col({"db"}, 0)
DRUG_COL = _find_col({"prod_ai", "drug", "product"}, 1)
TTO_COL  = _find_col({"tto", "days", "time", "time_to_onset"}, 2)

# Normalize values
df["_DB"]   = df[DB_COL].astype(str).str.strip().str.upper()
df["_DRUG"] = df[DRUG_COL].astype(str).str.strip().str.upper()
df["_TTO"]  = pd.to_numeric(df[TTO_COL], errors="coerce")

# Map numeric DB codes if present
db_map_num_to_str = {"1": "JADER", "2": "FAERS"}
df.loc[df["_DB"].isin(db_map_num_to_str.keys()), "_DB"] = df["_DB"].map(db_map_num_to_str)

# ---------------- Plot ----------------
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

groups = [
    ("FAERS", "MIRABEGRON",  OKABE_ITO["SkyBlue"], "-."), # dash-dot for mirabegron
    ("FAERS", "SOLIFENACIN", OKABE_ITO["SkyBlue"], "-"),
    ("JADER", "MIRABEGRON",  OKABE_ITO["Orange"],  "-."),
    ("JADER", "SOLIFENACIN", OKABE_ITO["Orange"],  "-"),
]

any_curve = False
for db_val, drug_val, color, lstyle in groups:
    sub = df[(df["_DB"] == db_val) & (df["_DRUG"] == drug_val)].copy()
    t = pd.to_numeric(sub["_TTO"], errors="coerce").dropna().astype(float).values
    t = t[t >= 0]  # safety
    if t.size == 0:
        print(f"[KM] No TTO rows for {db_val} × {drug_val}")
        continue

    t_sorted = np.sort(t)
    n = t_sorted.size
    cum = np.arange(1, n + 1) / n  # 0..1

    # include origin for step extrapolation
    t_plot = np.insert(t_sorted, 0, 0.0)
    cum_plot = np.insert(cum, 0, 0.0)

    label = f"{db_val} – {drug_val.title()}"
    ax.step(t_plot, cum_plot, where="post", color=color, linestyle=lstyle, linewidth=2, label=label)
    any_curve = True

# Axes/legend
ax.set_xlabel("Days since drug initiation (TTO)")
ax.set_ylabel("Cumulative probability")
ax.set_xlim(0, X_RIGHT)
ax.set_ylim(0, 1.0)
ax.grid(True, linestyle=":", linewidth=0.8)
ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
ax.legend(loc="lower right", fontsize=10, frameon=True, title="Database × Drug")

# Save (RGB)
plt.tight_layout()
out_path = os.path.abspath("./figure6_km_raw.png")
plt.savefig(out_path, dpi=300, format="png", transparent=False)
plt.close()

result = PNGObject(out_path)
