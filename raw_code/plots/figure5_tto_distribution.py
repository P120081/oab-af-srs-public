#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Figure 5 — Time-to-onset (TTO) distribution
# - Reproduces the original MSIP script behavior but works both in MSIP and CLI.
# - Fits a Weibull (k, lambda) by MLE (L-BFGS-B), with robust fallbacks.
# - Plots PDF (left, x along horizontal) vs. days (vertical), with a twinned histogram.
# - Adds a boxplot panel (right) with a diamond for mean and its bootstrap 95% CI.
# - Defaults match the original: y-range [0, 2750], bin width 5, PDF x-limit [0, 0.01].
# CLI options let you override y-max, bin width, histogram max, bootstrap B, seed, etc.

import os, sys, tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import minimize
from scipy.stats import weibull_min

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.axisbelow"] = True  # grid behind artists

# Optional MSIP PNGObject fallback
PNGObject = None
try:
    from msi.common.visualization import PNGObject as _PNGObject
    PNGObject = _PNGObject
except Exception:
    class PNGObject:
        def __init__(self, path): self.path = path
        def __repr__(self): return f"PNGObject({self.path})"


# -------------------- Data loading --------------------
def _load_df(args):
    if args is not None and getattr(args, "table", None):
        return pd.read_csv(args.table)
    g = globals()
    if "table" in g:
        t = g["table"]
        if hasattr(t, "to_pandas"): return t.to_pandas()
        if isinstance(t, pd.DataFrame): return t.copy()
    raise RuntimeError("No input provided. Use --table <CSV> or supply MSIP 'table'.")


def _pick_tto_series(df: pd.DataFrame, col: str | None):
    """Pick the TTO numeric series.
    Priority: explicit --column -> common name guesses -> 3rd column (0-based idx 2)."""
    if col is not None:
        if col not in df.columns:
            raise KeyError(f"--column '{col}' not found. Available: {list(df.columns)}")
        s = pd.to_numeric(df[col], errors="coerce")
        return s

    # Try common names
    candidates = [c for c in df.columns if str(c).lower() in
                  ("tto", "tto_days", "days", "onset_days", "time_to_onset", "time-to-onset")]
    if candidates:
        return pd.to_numeric(df[candidates[0]], errors="coerce")

    # Fallback: 3rd column
    if df.shape[1] < 3:
        raise ValueError("Data has fewer than 3 columns; cannot fallback to the 3rd column.")
    return pd.to_numeric(df.iloc[:, 2], errors="coerce")


# -------------------- Stats helpers --------------------
def weibull_mle_pos(data: np.ndarray):
    """MLE fit for Weibull (k, lambda) with positive data; returns (k, lambda)."""
    x = np.asarray(data, dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if x.size == 0:
        raise ValueError("No positive finite observations for Weibull fit.")
    def nll(params):
        k, lam = params
        if k <= 0 or lam <= 0:
            return np.inf
        n = x.size
        # log-likelihood for Weibull with loc=0
        ll = (n * np.log(k)
              - n * k * np.log(lam)
              + (k - 1) * np.sum(np.log(x))
              - np.sum((x / lam) ** k))
        return -ll
    init = np.array([1.0, float(np.median(x))], dtype=float)
    bounds = ((1e-6, None), (1e-6, None))
    res = minimize(nll, init, method="L-BFGS-B", bounds=bounds)
    if not res.success or not np.all(np.isfinite(res.x)):
        # Fallback to scipy fit with loc fixed at 0
        c, loc, scale = weibull_min.fit(x, floc=0)
        return float(c), float(scale)
    k_est, lam_est = res.x
    return float(k_est), float(lam_est)


def bootstrap_mean_ci(x: np.ndarray, B: int, rng: np.random.Generator):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n == 0:
        return np.nan, (np.nan, np.nan)
    means = np.empty(B, dtype=float)
    for b in range(B):
        sample = rng.choice(x, size=n, replace=True)
        means[b] = np.mean(sample)
    return float(np.mean(x)), (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


# -------------------- Plot core --------------------
def plot_figure5_core(df: pd.DataFrame, out_png: str, out_tif: str | None,
                      column: str | None, ymax: float, bin_width: float,
                      hist_max: float | None, B: int, seed: int,
                      pdf_xmax: float | None):
    # Colors (Okabe–Ito subset)
    green = "#009E73"
    blue  = "#0072B2"
    red   = "#D55E00"
    black = "#000000"
    water = "#56B4E9"

    # Select TTO series
    s = _pick_tto_series(df, column)
    data = s.to_numpy(dtype=float)
    data = data[np.isfinite(data) & (data > 0)]  # Weibull requires > 0
    if data.size == 0:
        raise ValueError("No valid positive TTO values after parsing.")

    # Fit Weibull
    k_est, lam_est = weibull_mle_pos(data)

    # PDF grid along horizontal axis, y vertical is days
    y_min, y_max = 0.0, float(ymax)
    y_grid = np.linspace(y_min, y_max, 500)
    # weibull_min.pdf(y, c=k, scale=lambda)
    pdf_vals = weibull_min.pdf(y_grid, k_est, scale=lam_est)

    # Bootstrap mean CI
    rng = np.random.default_rng(seed)
    mean_point, (ci_low, ci_high) = bootstrap_mean_ci(data, B=B, rng=rng)

    # Figure layout (left: pdf + histogram as twinx-x, right: boxplot)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 7), gridspec_kw={"width_ratios": [5, 1]})

    # Left axis: PDF vs days (vertical)
    ax1.set_ylim([y_min, y_max])
    # grid ticks every 50 by default
    step = 50.0
    ax1.set_yticks(np.arange(y_min, y_max + 1e-9, step))
    ax1.plot(pdf_vals, y_grid, label="PDF", color=water, linewidth=4)
    ax1.set_ylabel("days", fontsize=15)
    ax1.set_xlabel("probability density", fontsize=15)
    ax1.tick_params(axis="x", labelsize=15)
    ax1.tick_params(axis="y", labelsize=15)
    ax1.xaxis.set_tick_params(pad=10)
    # Respect original default; allow override if pdf overtops
    if pdf_xmax is None:
        # auto: 5% headroom
        ax1.set_xlim(0, max(0.01, float(np.nanmax(pdf_vals)) * 1.05))
    else:
        ax1.set_xlim(0, float(pdf_xmax))
    ax1.grid(True)

    # Histogram as twin-x (horizontal bars)
    bin_edges = np.arange(y_min, y_max + bin_width, bin_width)
    ax3 = ax1.twiny()
    counts, _, _ = ax3.hist(data, bins=bin_edges, color=green, orientation="horizontal")
    ax3.set_xlabel("histogram", fontsize=15, labelpad=10)
    ax3.tick_params(axis="x", labelsize=15)
    ax3.set_ylim(y_min, y_max)
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    if hist_max is None:
        ax3.set_xlim(0, max(1.0, float(counts.max())) * 1.05)
    else:
        ax3.set_xlim(0, float(hist_max))

    # Right axis: boxplot with mean CI diamond
    ax2.boxplot(data, vert=True, widths=0.6, patch_artist=False,
                boxprops=dict(color=green, linewidth=3),
                whiskerprops=dict(color=green, linewidth=3),
                flierprops=dict(markerfacecolor=red, marker='o', markersize=5),
                capprops=dict(color=green, linewidth=3),
                medianprops=dict(color=red, linewidth=3),
                positions=[1])
    ax2.set_ylim(y_min, y_max)
    ax2.set_yticks(ax1.get_yticks())
    ax2.yaxis.grid(True)
    ax2.set_xticks([])
    ax2.set_yticklabels([''] * len(ax1.get_yticks()))
    ax2.tick_params(axis='y', which='both', length=0)

    # Mean CI diamond
    diamond_x = [0.75, 1.00, 1.25, 1.00, 0.75]
    diamond_y = [mean_point, ci_high, mean_point, ci_low, mean_point]
    ax2.plot(diamond_x, diamond_y, color=black, linewidth=3)

    plt.subplots_adjust(left=0.15, right=0.9, wspace=0.05)

    fig.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.1)
    if out_tif:
        fig.savefig(out_tif, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main():
    save_dir = tempfile.gettempdir()
    default_png = os.path.join(save_dir, "combined_plot.png")
    default_tif = os.path.join(save_dir, "combined_plot.tif")

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="CSV path (omit when using MSIP 'table')")
    ap.add_argument("--out", default=default_png)
    ap.add_argument("--tif", default=default_tif)
    ap.add_argument("--column", default=None, help="Column name for TTO (optional). If omitted, auto-detect or 3rd col.")
    ap.add_argument("--ymax", type=float, default=2750.0, help="Max of days axis (default 2750).")
    ap.add_argument("--binwidth", type=float, default=5.0, help="Histogram bin width (default 5).")
    ap.add_argument("--hist-max", type=float, default=None, help="Max of histogram x-axis (default auto).")
    ap.add_argument("--B", type=int, default=10000, help="Bootstrap iterations (default 10000).")
    ap.add_argument("--seed", type=int, default=12345, help="Random seed (default 12345).")
    ap.add_argument("--pdf-xmax", type=float, default=0.01, help="Right limit of PDF x-axis (default 0.01). Set negative for auto.")
    args, _ = ap.parse_known_args()

    # Allow auto behavior if user sets negative pdf-xmax
    pdf_xmax = None if (args.pdf_xmax is None or args.pdf_xmax < 0) else args.pdf_xmax

    df = _load_df(args)
    plot_figure5_core(df, out_png=args.out, out_tif=args.tif,
                      column=args.column, ymax=args.ymax, bin_width=args.binwidth,
                      hist_max=args.hist_max, B=args.B, seed=args.seed,
                      pdf_xmax=pdf_xmax)

    po = PNGObject(args.out)
    print("PNG saved to:", args.out)
    print("TIFF saved to:", args.tif)
    return po


if __name__ == "__main__":
    main()
