
#!/usr/bin/env python3
"""
KM-style cumulative curve (raw TTO).
Draws 4 curves: JADER/FAERS x MIRABEGRON/SOLIFENACIN by default.
CLI:
  python raw_code/plots/kaplan_meier_raw.py --table data/derived/figure6_km_source.csv --out docs/figure6_km_raw.png
"""
import os, argparse, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from _common_utils import OKABE_ITO, load_table_like

plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.size"]   = 12

MM_TO_INCH = 1.0 / 25.4
FIG_W = 180 * MM_TO_INCH
FIG_H = 120 * MM_TO_INCH
X_RIGHT = 730

def km_raw(df: pd.DataFrame, out_png: str, drugs=("MIRABEGRON","SOLIFENACIN")):
    def _col(cands, fallback_idx):
        cols = list(df.columns)
        for c in cols:
            if str(c).strip().lower() in cands:
                return c
        return cols[fallback_idx]

    DB_COL   = _col({"db"}, 0)
    DRUG_COL = _col({"prod_ai","drug","product"}, 1)
    TTO_COL  = _col({"tto","days","time","time_to_onset"}, 2)

    d = pd.DataFrame()
    d["_DB"]   = df[DB_COL].astype(str).str.strip().str.upper()
    d["_DRUG"] = df[DRUG_COL].astype(str).str.strip().str.upper()
    d["_TTO"]  = pd.to_numeric(df[TTO_COL], errors="coerce").fillna(-1)

    db_map_num_to_str = {"1": "JADER", "2": "FAERS"}
    d.loc[d["_DB"].isin(db_map_num_to_str.keys()), "_DB"] = d["_DB"].map(db_map_num_to_str)

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    groups = [
        ("FAERS", drugs[0],  OKABE_ITO["SkyBlue"], "-."),
        ("FAERS", drugs[1],  OKABE_ITO["SkyBlue"], "-"),
        ("JADER", drugs[0],  OKABE_ITO["Orange"],  "-."),
        ("JADER", drugs[1],  OKABE_ITO["Orange"],  "-"),
    ]
    any_curve = False
    for db_val, drug_val, color, lstyle in groups:
        t = d.loc[(d["_DB"] == db_val) & (d["_DRUG"] == drug_val), "_TTO"].values
        t = t[t >= 0]
        if t.size == 0: 
            continue
        t_sorted = np.sort(t)
        n = t_sorted.size
        cum = np.arange(1, n + 1) / n
        t_plot = np.insert(t_sorted, 0, 0.0)
        cum_plot = np.insert(cum, 0, 0.0)
        label = f"{db_val} - {drug_val.title()}"
        ax.step(t_plot, cum_plot, where="post", color=color, linestyle=lstyle, linewidth=2, label=label)
        any_curve = True

    ax.set_xlabel("Days since drug initiation (TTO)")
    ax.set_ylabel("Cumulative probability")
    ax.set_xlim(0, X_RIGHT); ax.set_ylim(0, 1.0)
    ax.grid(True, linestyle=":", linewidth=0.8)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    if any_curve:
        ax.legend(loc="lower right", fontsize=10, frameon=True, title="Database x Drug")

    plt.tight_layout(); plt.savefig(out_png, dpi=300, format="png", transparent=False); plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=False, help="CSV with columns [DB,prod_ai,TTO]")
    ap.add_argument("--out",   required=False, default="figure6_km_raw.png")
    ap.add_argument("--drugA", required=False, default="MIRABEGRON")
    ap.add_argument("--drugB", required=False, default="SOLIFENACIN")
    args = ap.parse_args()

    if args.table is None and "table" in globals():
        df = load_table_like(globals()["table"])
    else:
        df = load_table_like(args.table)

    km_raw(df, out_png=args.out, drugs=(args.drugA.upper(), args.drugB.upper()))

if __name__ == "__main__":
    main()
