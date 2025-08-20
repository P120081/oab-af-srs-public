"""
Figure 5 — TTO distribution (Weibull PDF + histogram + boxplot with bootstrap mean CI)
MSIP Python node (public, ASCII-only)

Assumptions
- MSIP passes a table named `table`.
- The 3rd column (index 2) contains TTO in days (positive numeric).
  *If headers differ, position-based indexing ensures this works for both JADER/FAERS exports.*

Output
- PNG `figure5_tto_distribution.png` (RGB, 300 dpi)
- TIFF `figure5_tto_distribution.tif` (300 dpi)
- `result` = PNGObject pointing to the PNG path (for MSIP preview)
"""

# MSIP
from msi.common.visualization import PNGObject

# General
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import minimize
from scipy.stats import weibull_min

# ---------- Config ----------
# Reproducibility
BOOTSTRAP_B = 10000    # 5,000–10,000 recommended for final
RNG_SEED = 12345
rng = np.random.default_rng(RNG_SEED)

# Figure & axis
Y_MIN, Y_MAX = 0, 730
Y_TICK_STEP = 50
BIN_WIDTH = 5           # histogram bin width in days
HIST_MAX = None         # None=auto; set a number (e.g., 20) to cap the count axis

# Fonts & style
plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.axisbelow"] = True  # grid under artists

# ---------- Load ----------
df = table.to_pandas()
data = df.iloc[:, 2].to_numpy(dtype=float)

# Ensure strictly positive (Weibull PDF assumes x>0); drop non-positive
data = data[np.isfinite(data)]
data = data[data > 0]
if data.size == 0:
    raise ValueError("No positive TTO values found in column index 2.")

# ---------- Weibull MLE ----------
def neg_log_likelihood(params, arr):
    k, lam = params
    if k <= 0 or lam <= 0:
        return np.inf
    if np.any(arr <= 0):
        return np.inf
    n = arr.size
    return -(n*np.log(k) - n*k*np.log(lam) + (k-1)*np.sum(np.log(arr)) - np.sum((arr/lam)**k))

init = [1.0, float(np.median(data))]
res = minimize(neg_log_likelihood, init, args=(data,), method="L-BFGS-B",
               bounds=((1e-5, None), (1e-5, None)))
k_est, lam_est = res.x

# PDF on 0..2000 days (adjust as needed)
x_pdf = np.linspace(0, 2000, 500)
pdf = weibull_min.pdf(x_pdf, k_est, scale=lam_est)

# ---------- Bootstrap CI for mean ----------
n = data.size
means = np.empty(BOOTSTRAP_B, dtype=float)
for b in range(BOOTSTRAP_B):
    sample = rng.choice(data, size=n, replace=True)
    means[b] = sample.mean()
mean_point = float(data.mean())
ci_low, ci_high = np.percentile(means, [2.5, 97.5])

# ---------- Colors (Okabe–Ito) ----------
GREEN = "#009E73"
BLUE  = "#0072B2"
RED   = "#D55E00"
BLACK = "#000000"
ORANGE = "#E69F00"
SKY   = "#56B4E9"

# ---------- Figure ----------
# Side-by-side: left PDF+hist (twiny), right boxplot+diamond
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 7), gridspec_kw={"width_ratios": [5, 1]})

# Left panel: set Y first for coherent grid/overlays
ax1.set_ylim([Y_MIN, Y_MAX])
ax1.set_yticks(np.arange(Y_MIN, Y_MAX + 1, Y_TICK_STEP))
ax1.set_ylabel("Days", fontsize=12)
ax1.set_xlabel("Probability density", fontsize=12)
ax1.tick_params(axis="x", labelsize=11)
ax1.tick_params(axis="y", labelsize=11)
ax1.grid(True, linestyle=":", linewidth=0.8)

# Plot Weibull PDF against Y (days): horizontal x=pdf, y=days
ax1.plot(pdf, x_pdf, color=ORANGE, linewidth=3)

# Histogram on a twin X-axis (horizontal)
bins = np.arange(Y_MIN, Y_MAX + BIN_WIDTH, BIN_WIDTH)
ax3 = ax1.twiny()
counts, _, _ = ax3.hist(data, bins=bins, color=GREEN, orientation="horizontal")
ax3.set_xlabel("Histogram (count)", fontsize=12, labelpad=8)
ax3.tick_params(axis="x", labelsize=11)
ax3.set_ylim(Y_MIN, Y_MAX)
ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
if HIST_MAX is None:
    ax3.set_xlim(0, max(1, counts.max()) * 1.05)
else:
    ax3.set_xlim(0, float(HIST_MAX))

# Right panel: boxplot + bootstrap diamond (mean & 95% CI)
ax2.boxplot(
    data, vert=True, widths=0.6, patch_artist=False,
    boxprops=dict(color=GREEN, linewidth=2.5),
    whiskerprops=dict(color=GREEN, linewidth=2.5),
    flierprops=dict(markerfacecolor=RED, marker='o', markersize=4),
    capprops=dict(color=GREEN, linewidth=2.5),
    medianprops=dict(color=RED, linewidth=2.5),
    positions=[1],
)
ax2.set_ylim(Y_MIN, Y_MAX)
ax2.set_yticks(ax1.get_yticks())
ax2.yaxis.grid(True, linestyle=":", linewidth=0.8)
ax2.set_xticks([])
ax2.set_yticklabels([""] * len(ax1.get_yticks()))
ax2.tick_params(axis="y", which="both", length=0)

# Diamond overlay (mean and CI)
dx = [0.75, 1.0, 1.25, 1.0, 0.75]
dy = [mean_point, ci_high, mean_point, ci_low, mean_point]
ax2.plot(dx, dy, color=BLACK, linewidth=2.5)

# Tight layout and save
out_png = os.path.abspath("./figure5_tto_distribution.png")
out_tif = os.path.abspath("./figure5_tto_distribution.tif")
plt.tight_layout()
fig.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.1)
fig.savefig(out_tif, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
plt.close(fig)

# MSIP result
result = PNGObject(out_png)

# Log
print(f"Weibull k={k_est:.4f}, lambda={lam_est:.4f}; mean={mean_point:.2f}, 95%CI=[{ci_low:.2f}, {ci_high:.2f}]")
