"""
Figure 6 — Kaplan–Meier–style cumulative curve with bootstrap IQR ribbon
MSIP Python node

Assumptions
- Column 0 = DB code (1=JADER, 2=FAERS). Strings "JADER"/"FAERS" are also accepted.
- Column 4 = TTO (days; integer/float). Negative or NaN are removed upstream.

Method
- For each DB separately, bootstrap resample TTO (B iterations).
- For each resample, compute the empirical cumulative curve and interpolate on a
  common x-grid (anchor at (0,0) to start from origin).
- Plot the median curve with a shaded IQR (25th–75th percentile) ribbon.

Output
- PNG saved at ./figure6_km_bootstrap_iqr.png
- MSIP result returns PNGObject
"""

# MSIP
from msi.common.visualization import PNGObject

# General
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# ---------- Config ----------
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 12

OKABE_ITO = {
    "Black": "#000000",
    "Orange": "#E69F00",
    "Sky Blue": "#56B4E9",
    "Bluish Green": "#009E73",
    "Yellow": "#F0E442",
    "Blue": "#0072B2",
    "Vermilion": "#D55E00",
    "Reddish Purple": "#CC79A7",
}

DRUG_NAME = "Solifenacin"  # shown in legend header

# Column positions (0-based)
DB_COL_IDX = 0
TTO_COL_IDX = 4

# Accept both numeric {1,2} and string {"JADER","FAERS"}
DB_MAP = {
    1: {"label": "JADER", "color": OKABE_ITO["Orange"]},
    2: {"label": "FAERS", "color": OKABE_ITO["Sky Blue"]},
    "JADER": {"label": "JADER", "color": OKABE_ITO["Orange"]},
    "FAERS": {"label": "FAERS", "color": OKABE_ITO["Sky Blue"]},
}

B = 1000             # bootstrap iterations
N_X = 200            # number of x grid points for interpolation
X_MAX_DEFAULT = 2750 # cap for x-axis; if None, auto from data

# ---------- Load ----------
df = table.to_pandas()
db_col = df.columns[DB_COL_IDX]
tto_col = df.columns[TTO_COL_IDX]

# Prepare per-DB arrays and detect a global x-maximum for a shared grid
series_by_db = {}
xmax_detected = 0.0

for db_val in df[db_col].dropna().unique():
    info = DB_MAP.get(db_val) or DB_MAP.get(str(db_val).upper())
    if info is None:
        continue
    tto = pd.to_numeric(df.loc[df[db_col] == db_val, tto_col], errors="coerce").dropna().astype(float)
    tto = tto[tto >= 0]
    if tto.size == 0:
        print(f"[WARN] No TTO rows for {db_val}.")
        continue
    series_by_db[info["label"]] = {"color": info["color"], "tto": tto.values}
    xmax_detected = max(xmax_detected, float(tto.max()))

# Shared x-grid (for comparable ribbons across DBs)
x_right = X_MAX_DEFAULT if X_MAX_DEFAULT is not None else max(1.0, xmax_detected * 1.05)
x_common = np.linspace(0.0, x_right, N_X)

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(8, 6))
# legend header
ax.plot([], [], " ", label=f"Drug: {DRUG_NAME}")

for label, payload in series_by_db.items():
    color = payload["color"]
    time = payload["tto"]
    n = int(time.size)

    # Bootstrap matrix: B x N_X
    y_matrix = np.zeros((B, N_X), dtype=float)

    for b in range(B):
        sample = np.random.choice(time, size=n, replace=True)
        sample_sorted = np.sort(sample)
        cumulative = (np.arange(1, n + 1) / n) * 100.0

        # anchor (0,0) to start from origin
        xs = np.insert(sample_sorted, 0, 0.0)
        ys = np.insert(cumulative,    0, 0.0)

        # interpolate onto shared grid
        y_matrix[b, :] = np.interp(x_common, xs, ys)

    # Median and IQR across bootstraps
    median_curve = np.percentile(y_matrix, 50, axis=0)
    lower_bound  = np.percentile(y_matrix, 25, axis=0)
    upper_bound  = np.percentile(y_matrix, 75, axis=0)
    median_val   = int(np.median(time))

    line_label = f"{label} (N={n}, median={median_val}d)"
    ax.plot(x_common, median_curve, color=color, linewidth=2, label=line_label)
    ax.fill_between(x_common, lower_bound, upper_bound, color=color, alpha=0.2)

# ---------- Axes / legend ----------
ax.set_xlabel("Time to onset (days)")
ax.set_ylabel("Cumulative incidence (%)")
ax.set_xlim(left=0, right=x_right)
ax.set_ylim(0, 100)
ax.grid(True)
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
ax.legend(loc="lower right", fontsize=10, frameon=True)

plt.tight_layout()
out_path = os.path.abspath("./figure6_km_bootstrap_iqr.png")
plt.savefig(out_path, dpi=300)
plt.close()

result = PNGObject(out_path)
