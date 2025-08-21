
#!/usr/bin/env python3
"""
Figure 5: TTO distribution — Weibull PDF + histogram + boxplot.
Dual mode (MSIP / CLI).
CLI:
  python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_FAERS_mirabegron.csv --out docs/figure5_tto_distribution.png
"""
import os, argparse, numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib.ticker as ticker
from scipy.optimize import minimize
from scipy.stats import weibull_min

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.axisbelow'] = True

def fit_weibull_mle(tto):
    def nll(params):
        k, lam = params
        if k <= 0 or lam <= 0: return np.inf
        n = tto.size
        return -(n * np.log(k) - n * k * np.log(lam) + (k - 1) * np.sum(np.log(tto)) - np.sum((tto / lam)**k))
    init = [1.0, float(np.median(tto))]
    res = minimize(nll, init, method="L-BFGS-B", bounds=((1e-5,None),(1e-5,None)))
    return res.x  # k_hat, lam_hat

def tto_distribution(df: pd.DataFrame, out_png: str, out_tif: str|None=None, y_max: float=730.0):
    tto = pd.to_numeric(df.iloc[:, 2], errors="coerce").dropna().astype(float).values
    tto = tto[tto > 0.0]
    if tto.size == 0:
        raise RuntimeError("No positive TTO values found.")
    k_hat, lam_hat = fit_weibull_mle(tto)

    y_min = 0.0
    bin_width = 5.0
    bins = np.arange(y_min, y_max + bin_width, bin_width)

    fig, (ax_pdf, ax_box) = plt.subplots(1, 2, figsize=(6.5, 8.0), gridspec_kw={"width_ratios":[5,1]})

    # Left: Weibull PDF
    y_vals = np.linspace(y_min, y_max, 500)
    pdf_vals = weibull_min.pdf(y_vals, k_hat, scale=lam_hat)
    ax_pdf.set_ylim([y_min, y_max])
    ax_pdf.plot(pdf_vals, y_vals, linewidth=3)
    ax_pdf.set_xlabel("probability density"); ax_pdf.set_ylabel("days")
    ax_pdf.grid(True); ax_pdf.set_xlim(0, max(0.01, float(pdf_vals.max()) * 1.05))
    ax_pdf.set_yticks(np.arange(y_min, y_max+1e-9, 50.0))

    # Overlaid histogram on twinned x axis
    ax_hist = ax_pdf.twiny()
    counts, _, _ = ax_hist.hist(tto, bins=bins, orientation="horizontal")
    ax_hist.set_xlabel("histogram")
    ax_hist.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax_hist.set_ylim(y_min, y_max)
    ax_hist.set_xlim(0, max(1.0, counts.max() * 1.05))

    # Right: boxplot
    ax_box.boxplot(
        tto, vert=True, widths=0.6, patch_artist=False,
        boxprops=dict(linewidth=2.5), whiskerprops=dict(linewidth=2.5),
        flierprops=dict(marker='o', markersize=4),
        capprops=dict(linewidth=2.5), medianprops=dict(linewidth=2.5),
        positions=[1]
    )
    ax_box.set_ylim(y_min, y_max)
    ax_box.set_yticks(ax_pdf.get_yticks())
    ax_box.yaxis.grid(True)
    ax_box.set_xticks([]); ax_box.set_yticklabels([''] * len(ax_pdf.get_yticks()))
    ax_box.tick_params(axis='y', which='both', length=0)

    plt.subplots_adjust(left=0.12, right=0.9, wspace=0.05)
    plt.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.1)
    if out_tif:
        plt.savefig(out_tif, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=False, help="CSV with TTO as the 3rd column")
    ap.add_argument("--out",   required=False, default="figure5_tto_distribution.png")
    ap.add_argument("--tif",   required=False, default="figure5_tto_distribution.tif")
    ap.add_argument("--ymax",  required=False, default=730.0, type=float)
    args = ap.parse_args()

    if args.table is None and "table" in globals():
        df = globals()["table"].to_pandas()
    else:
        df = pd.read_csv(args.table)

    tto_distribution(df, out_png=args.out, out_tif=args.tif, y_max=args.ymax)

if __name__ == "__main__":
    main()
