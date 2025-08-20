"""
Figure 5 — TTO distribution: Weibull PDF + histogram + boxplot (side)
MSIP Python node

Assumptions
- Input MSIP table convertible to pandas via table.to_pandas()
- Column index 2 is TTO (days). Non-positive and NaN values are ignored.

Outputs
- figure5_tto_distribution.png and figure5_tto_distribution.tif (300 dpi, RGB)
- Returns PNGObject for MSIP
"""

from msi.common.visualization import PNGObject

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import minimize
from scipy.stats import weibull_min

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.axisbelow'] = True

# Load
df = table.to_pandas()
tto = pd.to_numeric(df.iloc[:, 2], errors="coerce").dropna().astype(float).values
tto = tto[tto > 0.0]  # keep positive only for Weibull

if tto.size == 0:
    raise RuntimeError("No positive TTO values found in column index 2.")

# Weibull MLE
def nll(params):
    k, lam = params
    if k <= 0 or lam <= 0: return np.inf
    n = tto.size
    return -(n * np.log(k) - n * k * np.log(lam) + (k - 1) * np.sum(np.log(tto)) - np.sum((tto / lam)**k))

init = [1.0, float(np.median(tto))]
res = minimize(nll, init, method="L-BFGS-B", bounds=((1e-5,None),(1e-5,None)))
k_hat, lam_hat = res.x

# Axes sync
y_min, y_max = 0.0, 730.0
bin_width = 5.0
bins = np.arange(y_min, y_max + bin_width, bin_width)

# Figure
fig, (ax_pdf, ax_box) = plt.subplots(1, 2, figsize=(6.5, 8.0), gridspec_kw={"width_ratios":[5,1]})

# Left: Weibull PDF (x axis is density, y is days)
y_vals = np.linspace(y_min, y_max, 500)
pdf_vals = weibull_min.pdf(y_vals, k_hat, scale=lam_hat)
ax_pdf.set_ylim([y_min, y_max])
ax_pdf.plot(pdf_vals, y_vals, color="#E69F00", linewidth=3)
ax_pdf.set_xlabel("probability density")
ax_pdf.set_ylabel("days")
ax_pdf.grid(True)
ax_pdf.set_xlim(0, max(0.01, float(pdf_vals.max()) * 1.05))
ax_pdf.set_yticks(np.arange(y_min, y_max+1e-9, 50.0))

# Overlaid histogram on twinned x axis
ax_hist = ax_pdf.twiny()
counts, _, _ = ax_hist.hist(tto, bins=bins, color="#009E73", orientation="horizontal")
ax_hist.set_xlabel("histogram")
ax_hist.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax_hist.set_ylim(y_min, y_max)
ax_hist.set_xlim(0, max(1.0, counts.max() * 1.05))

# Right: boxplot with synchronized y
ax_box.boxplot(
    tto, vert=True, widths=0.6, patch_artist=False,
    boxprops=dict(color="#009E73", linewidth=2.5),
    whiskerprops=dict(color="#009E73", linewidth=2.5),
    flierprops=dict(markerfacecolor="#D55E00", marker='o', markersize=4),
    capprops=dict(color="#009E73", linewidth=2.5),
    medianprops=dict(color="#D55E00", linewidth=2.5),
    positions=[1]
)
ax_box.set_ylim(y_min, y_max)
ax_box.set_yticks(ax_pdf.get_yticks())
ax_box.yaxis.grid(True)
ax_box.set_xticks([])
ax_box.set_yticklabels([''] * len(ax_pdf.get_yticks()))
ax_box.tick_params(axis='y', which='both', length=0)

plt.subplots_adjust(left=0.12, right=0.9, wspace=0.05)

png_path  = os.path.abspath("./figure5_tto_distribution.png")
tif_path  = os.path.abspath("./figure5_tto_distribution.tif")
fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
fig.savefig(tif_path, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
plt.close(fig)

result = PNGObject(png_path)
