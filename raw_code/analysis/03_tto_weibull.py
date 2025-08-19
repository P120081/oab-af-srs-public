"""
Table 2 — Weibull shape/scale estimation from TTO (MSIP Python node)

- Input (MSIP `table` -> pandas): the 4th column must be TTO in days (integer, >0).
  In your flow, table_039 columns are: [ID, drug_name, event_term, TTO]; hence TTO is iloc[:, 3].
- Estimation: MLE via L-BFGS-B for k (shape) and λ (scale), with percentile bootstrap CIs.
- Output:
    1) Printed summary (k, λ, median and their 95% CIs)
    2) Histogram figure of bootstrap draws: ./weibull_bootstrap_hist.png (returned as PNGObject)
    3) CSV summary: ./table2_weibull_params.csv

Notes:
- Keep TTO > 0. Negative TTOs are already excluded upstream.
- You can tune bootstrap iterations and parallelism below.
"""

# -------- MSIP / I/O --------
from msi.common.dataframe import DataFrame
from msi.common.visualization import PNGObject
# from msi.common.dataframe import pandas_to_dataframe  # (not needed; returning PNG)

# -------- Standard libs --------
import os
import numpy as np
import pandas as pd

# -------- SciPy / plotting --------
from scipy.optimize import minimize
from scipy.stats import weibull_min
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors

# -------- Parallel bootstrap --------
from joblib import Parallel, delayed

# -------- Config --------
plt.rcParams["font.family"] = "Arial"   # publication font
N_BOOTSTRAP = 10000                     # bootstrap iterations (heavy; adjust if needed)
N_JOBS = -1                             # joblib parallelism: -1 = use all cores
VERBOSE_BOOTSTRAP = False               # if True, print first 10 resampled values each draw

# -------- Load data --------
df = table.to_pandas()
# TTO is the 4th column in your pipeline (0-based index 3)
tto = pd.to_numeric(df.iloc[:, 3], errors="coerce").dropna().astype(float)

# basic checks
if (tto <= 0).any():
    raise ValueError("TTO must be strictly positive (>0) for Weibull MLE. Check upstream filtering.")

# -------- Negative log-likelihood for Weibull(k, λ) --------
def neg_log_likelihood(params, data):
    k, lam = float(params[0]), float(params[1])
    if k <= 0 or lam <= 0:
        return np.inf
    # log-likelihood
    n = data.size
    ll = n * np.log(k) - n * k * np.log(lam) + (k - 1) * np.sum(np.log(data)) - np.sum((data / lam) ** k)
    return -ll  # minimize the negative

# -------- Initial guess and MLE --------
init = np.array([1.0, float(np.median(tto))])  # k, λ
opt = minimize(
    neg_log_likelihood, init, args=(tto,),
    method="L-BFGS-B",
    bounds=((1e-5, None), (1e-5, None)),
    options={"maxiter": 1000}
)
if not opt.success:
    raise RuntimeError(f"MLE did not converge: {opt.message}")

k_hat, lam_hat = [float(x) for x in opt.x]
median_hat = float(np.median(tto))

print(f"[MLE] shape k = {k_hat:.4f}")
print(f"[MLE] scale λ = {lam_hat:.4f}")
print(f"[MLE] median  = {median_hat:.4f}")

# -------- Optional: mode (peak) of Weibull PDF (not used in table, kept for completeness) --------
x_plot = np.linspace(1e-9, lam_hat * 3.0, 500)
pdf = weibull_min.pdf(x_plot, k_hat, scale=lam_hat)
x_mode = x_plot[np.argmax(pdf)]

# -------- Bootstrap --------
def bootstrap_once(data, initial_guess):
    # resample with replacement
    resampled = np.random.choice(data, size=data.size, replace=True)
    if VERBOSE_BOOTSTRAP:
        print("Resampled head:", resampled[:10])
    res = minimize(
        neg_log_likelihood, initial_guess, args=(resampled,),
        method="L-BFGS-B",
        bounds=((1e-5, None), (1e-5, None)),
        options={"maxiter": 500}
    )
    if res.success:
        k_b, lam_b = [float(x) for x in res.x]
        med_b = float(np.median(resampled))
        return k_b, lam_b, med_b
    else:
        return None

bootstrap_res = Parallel(n_jobs=N_JOBS)(
    delayed(bootstrap_once)(tto.values, init) for _ in range(N_BOOTSTRAP)
)
bootstrap_res = np.array([r for r in bootstrap_res if r is not None])

if bootstrap_res.size == 0:
    raise ValueError("Empty bootstrap results. Check input TTO and optimization settings.")

print("[Bootstrap] first 10 rows:")
print(bootstrap_res[:10])

k_bs = bootstrap_res[:, 0]
lam_bs = bootstrap_res[:, 1]
med_bs = bootstrap_res[:, 2]

# percentile CIs
k_lo,   k_hi   = np.percentile(k_bs,   [2.5, 97.5])
lam_lo, lam_hi = np.percentile(lam_bs, [2.5, 97.5])
med_lo, med_hi = np.percentile(med_bs, [2.5, 97.5])

print(f"[CI 95%] k      : [{k_lo:.4f}, {k_hi:.4f}]")
print(f"[CI 95%] λ      : [{lam_lo:.4f}, {lam_hi:.4f}]")
print(f"[CI 95%] median : [{med_lo:.4f}, {med_hi:.4f}]")

# -------- Figure: bootstrap histograms --------
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(k_bs,   bins=30, alpha=0.7, label="k (shape)")
ax.hist(lam_bs, bins=30, alpha=0.7, label="lambda (scale)")
ax.set_title("Bootstrap distributions for Weibull parameters")
ax.legend()
png_path = os.path.abspath("./weibull_bootstrap_hist.png")
fig.savefig(png_path, dpi=300, bbox_inches="tight")
plt.close(fig)

# -------- CSV summary (Table 2) --------
import csv
csv_path = os.path.abspath("./table2_weibull_params.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["n", "k", "k_ci_low", "k_ci_high", "lambda", "lambda_ci_low", "lambda_ci_high", "median", "median_ci_low", "median_ci_high"])
    w.writerow([
        int(tto.size),
        f"{k_hat:.6f}", f"{k_lo:.6f}", f"{k_hi:.6f}",
        f"{lam_hat:.6f}", f"{lam_lo:.6f}", f"{lam_hi:.6f}",
        f"{median_hat:.6f}", f"{med_lo:.6f}", f"{med_hi:.6f}",
    ])

print("Saved CSV:", csv_path)
print("Saved PNG:", png_path)

# -------- MSIP return --------
result = PNGObject(png_path)
