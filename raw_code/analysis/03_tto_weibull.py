"""
Table 2 — Weibull shape/scale estimation from TTO (MSIP Python node)

- Input (MSIP `table` -> pandas): the 4th column must be TTO in days (integer, >0).
  In your flow, the table columns are: [ID, drug_name, event_term, TTO]; hence TTO is iloc[:, 3].
- Estimation: MLE via L-BFGS-B for k (shape) and lambda (scale), with percentile bootstrap CIs.
- Output:
    1) Printed summary (k, lambda, median and their 95% CIs)
    2) Histogram figure of bootstrap draws: data/derived/weibull_bootstrap_hist.png (returned as PNGObject)
    3) CSV summary: data/derived/table2_weibull_params.csv

Notes:
- Keep TTO > 0. Negative or zero TTOs should be removed upstream.
- You can tune bootstrap iterations and parallelism below.
"""

# ----- MSIP / IO -----
from msi.common.dataframe import DataFrame
from msi.common.visualization import PNGObject

# ----- Standard libs -----
import os
import csv
import numpy as np
import pandas as pd

# ----- SciPy / plotting -----
from scipy.optimize import minimize
from scipy.stats import weibull_min
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----- Parallel bootstrap -----
from joblib import Parallel, delayed

# ----- Config -----
plt.rcParams["font.family"] = "Arial"   # publication font
N_BOOTSTRAP = 10000                     # bootstrap iterations (adjust if needed)
N_JOBS = -1                             # joblib parallelism: -1 = use all cores
VERBOSE_BOOTSTRAP = False               # True -> print head of resampled draws (noisy)
SEED = None                             # set e.g. 12345 for deterministic sampling

# ----- Optional CLI overrides (safe in MSIP as well) -----
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_boot", type=int, default=N_BOOTSTRAP, help="Bootstrap iterations (default: 10000)")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for bootstrap (default: None)")
    args, _ = ap.parse_known_args()
    N_BOOTSTRAP = int(args.n_boot)
    SEED = args.seed

# ----- Load data -----
df = table.to_pandas()
# TTO is the 4th column (0-based index 3)
tto = pd.to_numeric(df.iloc[:, 3], errors="coerce").dropna().astype(float)

if (tto <= 0).any():
    raise ValueError("TTO must be strictly positive (>0) for Weibull MLE. Check upstream filtering.")

# optional seeding
if SEED is not None:
    np.random.seed(int(SEED))

# ----- Negative log-likelihood for Weibull(k, lambda) -----
def neg_log_likelihood(params, data):
    k, lam = float(params[0]), float(params[1])
    if k <= 0 or lam <= 0:
        return np.inf
    n = data.size
    ll = n * np.log(k) - n * k * np.log(lam) + (k - 1) * np.sum(np.log(data)) - np.sum((data / lam) ** k)
    return -ll

# ----- MLE -----
init = np.array([1.0, float(np.median(tto))])  # k, lambda
opt = minimize(
    neg_log_likelihood, init, args=(tto,),
    method="L-BFGS-B",
    bounds=((1e-5, None), (1e-5, None)),
    options={"maxiter": 1000}
)
if not opt.success:
    raise RuntimeError(f"MLE did not converge: {opt.message}")

k_hat, lam_hat = float(opt.x[0]), float(opt.x[1])
median_hat = float(np.median(tto))

print(f"[MLE] shape k = {k_hat:.6f}")
print(f"[MLE] scale lambda = {lam_hat:.6f}")
print(f"[MLE] median = {median_hat:.6f}")

# optional: mode of Weibull PDF (unused downstream)
x_plot = np.linspace(1e-9, lam_hat * 3.0, 500)
pdf = weibull_min.pdf(x_plot, k_hat, scale=lam_hat)
_ = x_plot[np.argmax(pdf)]  # x_mode (unused)

# ----- Bootstrap -----
def bootstrap_once(data, initial_guess):
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
        k_b, lam_b = float(res.x[0]), float(res.x[1])
        med_b = float(np.median(resampled))
        return k_b, lam_b, med_b
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

print(f"[CI 95%] k: [{k_lo:.6f}, {k_hi:.6f}]")
print(f"[CI 95%] lambda: [{lam_lo:.6f}, {lam_hi:.6f}]")
print(f"[CI 95%] median: [{med_lo:.6f}, {med_hi:.6f}]")

# ----- Outputs -----
os.makedirs("data/derived", exist_ok=True)

# Figure: bootstrap histograms
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(k_bs,   bins=30, alpha=0.7, label="k (shape)")
ax.hist(lam_bs, bins=30, alpha=0.7, label="lambda (scale)")
ax.set_title("Bootstrap distributions for Weibull parameters")
ax.legend()
png_path = os.path.abspath("data/derived/weibull_bootstrap_hist.png")
fig.savefig(png_path, dpi=300, bbox_inches="tight")
plt.close(fig)

# CSV summary (Table 2)
csv_path = os.path.abspath("data/derived/table2_weibull_params.csv")
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

# MSIP return
result = PNGObject(png_path)
