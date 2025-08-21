
#!/usr/bin/env python3
"""
Volcano plot for a single OAB drug.
Dual mode (MSIP / CLI).
CLI:
  python raw_code/plots/volcano_plot.py --table data/derived/volcano_mirabegron.csv --out docs/volcano_mirabegron.png
"""
import os, argparse, numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib.patheffects as path_effects
from _common_utils import OKABE_ITO, load_table_like

plt.rcParams["font.family"] = "Arial"

def map_n11_to_size(n: float) -> float:
    if n < 10:   return 40
    if n < 100:  return 90
    if n < 200:  return 140
    return 200

def volcano_plot(df: pd.DataFrame, out_png: str, title_drug: str|None=None):
    # Normalize
    if "Subgroup" in df.columns:
        df["Subgroup"] = df["Subgroup"].astype(str).str.replace("≥", ">=")
    df["ROR"] = pd.to_numeric(df["ROR"], errors="coerce")
    df["n11"] = pd.to_numeric(df["n11"], errors="coerce")
    if "p" in df.columns:
        df["p"] = pd.to_numeric(df["p"], errors="coerce")
    elif "p-value" in df.columns:
        df["p"] = df["p-value"].astype(str).str.replace("<","",regex=False).pipe(pd.to_numeric, errors="coerce")

    df = df.dropna(subset=["ROR", "p", "n11"])
    df = df[df["n11"] >= 3]
    df.loc[df["p"] <= 0, "p"] = 1e-300
    df["lnROR"] = np.log(df["ROR"])
    df["neglog10_p"] = -np.log10(df["p"])

    # Colors
    db_color_map = {"JADER": OKABE_ITO["Orange"], "FAERS": OKABE_ITO["SkyBlue"]}
    df["color"] = df["DB"].map(db_color_map)
    df["size"] = df["n11"].apply(map_n11_to_size)

    # Draw
    fig, ax = plt.subplots(figsize=(7.09, 5.3))
    for db in df["DB"].dropna().unique():
        sub = df[df["DB"] == db]
        ax.scatter(sub["lnROR"], sub["neglog10_p"], s=sub["size"], c=sub["color"], alpha=0.6)

    # Labels for p<0.05
    for _, row in df.iterrows():
        if row["p"] < 0.05:
            label = f"{row['Subgroup']}\n({int(row['n11'])})"
            y_offset_custom = -0.15 if row["Subgroup"] == "Drugs>=5" else 0.0
            t = ax.text(row["lnROR"] + 0.02, row["neglog10_p"] + y_offset_custom, label,
                        fontsize=8, ha="left", va="top", color="black")
            t.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground="white"),
                                path_effects.Normal()])

    # Threshold lines and axes
    ax.axhline(y=1.3, color="black", linestyle="--", linewidth=1)  # p=0.05
    ax.axvline(x=0.0, color="black", linestyle="--", linewidth=1)  # lnROR=0
    ax.set_xlabel("lnROR", fontsize=14)
    ax.set_ylabel("-log10(p-value)", fontsize=14)
    ax.grid(True); plt.tick_params(axis="both", labelsize=12)

    # Title drug box
    if title_drug is None and "drug_of_interest" in df.columns and not df["drug_of_interest"].isna().all():
        title_drug = str(df["drug_of_interest"].dropna().iloc[0]).capitalize()
    if title_drug:
        ax.text(0.99, 0.99, f"Drug: {title_drug}", transform=ax.transAxes, fontsize=12, ha="right", va="top",
                bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    plt.tight_layout(); plt.savefig(out_png, dpi=300); plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=False, help="CSV for a single drug's volcano plot")
    ap.add_argument("--out",   required=False, default="volcano_plot.png")
    ap.add_argument("--title", required=False, default=None, help="Drug name for title box")
    args = ap.parse_args()

    if args.table is None and "table" in globals():
        df = load_table_like(globals()["table"])
    else:
        df = load_table_like(args.table)

    volcano_plot(df, out_png=args.out, title_drug=args.title)

if __name__ == "__main__":
    main()
