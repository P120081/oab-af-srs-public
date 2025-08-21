
#!/usr/bin/env python3
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from _common_utils import OKABE_ITO, load_table_like

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans','Arial','Segoe UI','Helvetica']

def draw_panel(ax, subdf, title):
    xmax = max(20.0, float(subdf["ROR975"].max(skipna=True)) * 1.5)
    lo, hi = 0.5, xmax
    def r2x(v): return 0.1 + (np.log10(v) - np.log10(lo)) * (0.8) / (np.log10(hi) - np.log10(lo))
    ax.set_xlim(0.0, 1.0); ax.set_ylim(-0.5, len(subdf)-0.5); ax.axis("off")
    ax.text(0.02, len(subdf)-0.1, title, fontsize=14, fontweight="bold", ha="left", va="top")
    y = len(subdf)-1
    for _, r in subdf.iterrows():
        try:
            lo_ci, hi_ci, mid = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
            x_lo = r2x(max(lo_ci, lo)); x_hi = r2x(min(hi_ci, hi)); xm = r2x(np.clip(mid, lo, hi))
            ax.hlines(y, x_lo, x_hi, color="#0072B2", linewidth=2)
            ax.plot([xm], [y], marker="s", color="#0072B2", markersize=5)
        except Exception:
            pass
        label = f"{r.get('DB','')} / {r.get('Subgroup','')}  n={int(r.get('n11',0))}"
        ax.text(0.98, y, label, fontsize=10, ha="right", va="center")
        y -= 1
    ax.vlines(r2x(1.0), ymin=-0.5, ymax=len(subdf)-0.5, color="#D55E00", linestyle="--", linewidth=2)

def forest_multidrug(df: pd.DataFrame, out_png: str):
    for c in ["n11","ROR","ROR025","ROR975"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "drug_of_interest" in df.columns:
        df = df.sort_values(["drug_of_interest","DB","Subgroup"], kind="mergesort")
    drugs = list(df["drug_of_interest"].dropna().unique())
    n_panels = max(1, len(drugs))
    fig_w = 10; fig_h = 2.5 * n_panels
    fig, axes = plt.subplots(n_panels, 1, figsize=(fig_w, fig_h), squeeze=False)
    axes = axes.ravel()
    for i, drug in enumerate(drugs or ["All"]):
        sub = df[df["drug_of_interest"] == drug] if drugs else df
        draw_panel(axes[i], sub, title=str(drug))
    plt.tight_layout()
    plt.savefig(out_png, dpi=300); plt.close()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=False)
    ap.add_argument("--out",   required=False, default="figure3_forest_plot.png")
    args = ap.parse_args()
    df = load_table_like(globals()["table"] if args.table is None and "table" in globals() else args.table)
    forest_multidrug(df, out_png=args.out)

if __name__ == "__main__":
    main()
