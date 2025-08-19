"""
Figure 6 — Kaplan–Meier style cumulative curve (raw TTO)
MSIP Python node (works with your position-based columns)

Assumptions
- Column 0 = DB code (1=JADER, 2=FAERS). Strings "JADER"/"FAERS" also accepted.
- Column 4 = TTO (days; integer/float). Negative or NaN are dropped upstream.

Output
- PNG saved at ./figure6_km_raw.png
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
# Font (unify across repo)
plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"] = 12

# Okabe–Ito palette
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

# Figure title (drug name shown in legend header)
DRUG_NAME = "Solifenacin"

# Input column positions (0-based)
DB_COL_IDX = 0
TTO_COL_IDX = 4

# Accept both numeric {1,2} and string {"JADER","FAERS"}
DB_MAP = {
    1: {"label": "JADER", "color": OKABE_ITO["Orange"]},
    2: {"label": "FAERS", "color": OKABE_ITO["Sky Blue"]},
    "JADER": {"label": "JADER", "color": OKABE_ITO["Orange"]},
    "FAERS": {"label": "FAERS", "color": OKABE_ITO["Sky Blue"]},
}

# X-axis cap (days). If None, auto = max(TTO)*1.05
X_MAX_DEFAULT = 2750

# ---------- Load ----------
df = table.to_pandas()

db_col = df.columns[DB_COL_IDX]
tto_col = df.columns[TTO_COL_IDX]

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([], [], " ", label=f"Drug: {DRUG_NAME}")  # legend header

xmax_detected = 0.0

# Iterate each DB present in data (respect both numeric and string codes)
unique_db_vals = df[db_col].dropna().unique()
for db_val in unique_db_vals:
    info = DB_MAP.get(db_val)
    if info is None:
        # Try mapping numeric <-> string if needed
        key = str(db_val).upper()
        info = DB_MAP.get(key)
    if info is None:
        # Unknown DB code; skip safely
        continue

    sub = df[df[db_col] == db_val]
    tto = pd.to_numeric(sub[tto_col], errors="coerce").dropna().astype(float)
    tto = tto[tto >= 0]  # keep non-negative just in case

    n = int(tto.size)
    if n == 0:
        print(f"[WARN] No TTO rows for {info['label']}.")
        continue

    t_sorted = np.sort(tto.values)
    cum = (np.arange(1, n + 1) / n) * 100.0

    # start from (0,0)
    t_sorted = np.insert(t_sorted, 0, 0.0)
    cum = np.insert(cum, 0, 0.0)

    median_val = int(np.median(tto))
    label = f"{info['label']} (N={n}, median={median_val}d)"

    ax.step(t_sorted, cum, where="post", color=info["color"], linewidth=2, label=label)

    xmax_detected = max(xmax_detected, float(t_sorted.max()))

# Axes and legend
ax.set_xlabel("Time to onset (days)")
ax.set_ylabel("Cumulative incidence (%)")
x_right = X_MAX_DEFAULT if X_MAX_DEFAULT is not None else xmax_detected * 1.05
ax.set_xlim(left=0, right=max(1.0, x_right))
ax.set_ylim(0, 100)
ax.grid(True)
ax.xaxis.set_major_locator(MaxNLocator(nbins=10))
ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
ax.legend(loc="lower right", fontsize=10, frameon=True)

plt.tight_layout()
out_path = os.path.abspath("./figure6_km_raw.png")
plt.savefig(out_path, dpi=300)
plt.close()

result = PNGObject(out_path)
