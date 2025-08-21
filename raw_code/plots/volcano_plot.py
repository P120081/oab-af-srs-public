#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Volcano plot (Fig.4) — original look, robust p-value parsing
- Accepts MSIP `table` or CLI `--table` CSV.
- Parses p-values like "5.54E-18", "2.3e-45", "<1e-12", "≤1e-50".
- Clips non-positive/invalid p to a tiny positive floor (for plotting only).
- Adds a small headroom at the top so markers/labels are not cut off.
"""
import os, sys, tempfile, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.lines as mlines

plt.rcParams["font.family"] = "Arial"  # match the manuscript

# Optional MSIP PNGObject fallback
PNGObject = None
try:
    from msi.common.visualization import PNGObject as _PNGObject
    PNGObject = _PNGObject
except Exception:
    class PNGObject:
        def __init__(self, path): self.path = path
        def __repr__(self): return f"PNGObject({self.path})"


def _load_df(args):
    """Load DataFrame from CLI --table or MSIP global 'table'."""
    if args is not None and getattr(args, "table", None):
        return pd.read_csv(args.table)
    g = globals()
    if "table" in g:
        t = g["table"]
        if hasattr(t, "to_pandas"): return t.to_pandas()
        if isinstance(t, pd.DataFrame): return t.copy()
    raise RuntimeError("No input provided. Use --table <CSV> or supply MSIP 'table'.")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map common variants to expected names without changing content."""
    ren = {}
    low = {c.lower(): c for c in df.columns}
    # p-value
    for cand in ["p-value", "p_value", "p", "pval", "pvalue", "p-val"]:
        if cand in low: ren[low[cand]] = "p-value"; break
    # DB
    for cand in ["db", "database"]:
        if cand in low: ren[low[cand]] = "DB"; break
    # Subgroup
    for cand in ["subgroup", "group", "stratum", "strata"]:
        if cand in low: ren[low[cand]] = "Subgroup"; break
    # n11
    for cand in ["n11", "n_11", "n"]:
        if cand in low: ren[low[cand]] = "n11"; break
    # ROR
    for cand in ["ror", "ror_mean"]:
        if cand in low: ren[low[cand]] = "ROR"; break
    return df.rename(columns=ren) if ren else df


_num = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
def _parse_p(v):
    """Parse p-value from float/int/str incl. scientific notation and inequalities."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, (float, int)):
        return float(v)
    s = str(v).strip()
    m = _num.search(s)
    try:
        return float(m.group(0)) if m else np.nan
    except Exception:
        return np.nan


def _map_n11_to_size(n):
    if n < 10:   return 40
    if n < 100:  return 90
    if n < 200:  return 140
    return 200


def volcano_plot_core(df: pd.DataFrame, out_png: str, out_tif: str | None, title_drug: str | None):
    # Normalize & validate
    df = _normalize_columns(df)
    required = ["DB", "Subgroup", "n11", "ROR", "p-value"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Required columns missing: {missing}. Available: {list(df.columns)}")

    # Cast & basic filters (match the original)
    df["ROR"] = pd.to_numeric(df["ROR"], errors="coerce")
    df["n11"] = pd.to_numeric(df["n11"], errors="coerce")
    # Robust p parsing
    p_parsed = df["p-value"].map(_parse_p).astype(float)
    # Plotting floor for invalid/non-positive p (does not affect statistics)
    pos = p_parsed[(p_parsed > 0) & np.isfinite(p_parsed)]
    floor = float(pos.min()) * 0.5 if len(pos) > 0 else 1e-300
    p_safe = p_parsed.mask((~np.isfinite(p_parsed)) | (p_parsed <= 0), floor)

    # Keep a clean column API for downstream lines (original names)
    df["p-value"] = p_safe
    df = df.dropna(subset=["ROR", "p-value", "n11"])
    df = df[df["n11"] >= 3]

    # Transforms
    df["lnROR"] = np.log(df["ROR"])
    df["-log10(p-value)"] = -np.log10(df["p-value"])

    # Colors (Okabe–Ito palette subset)
    okabe_ito = {"Orange": "#E69F00", "Sky Blue": "#56B4E9"}
    db_color_map = {"JADER": okabe_ito["Orange"], "FAERS": okabe_ito["Sky Blue"]}
    df["color"] = df["DB"].map(db_color_map).fillna("#808080")  # fallback gray
    df["size"] = df["n11"].apply(_map_n11_to_size)

    # Plot
    fig, ax = plt.subplots(figsize=(7.09, 5.3))
    for db in df["DB"].dropna().unique():
        sub = df[df["DB"] == db]
        ax.scatter(sub["lnROR"], sub["-log10(p-value)"], s=sub["size"], c=sub["color"], alpha=0.6)

    # Labels (only p < 0.05, by the safe p-value)
    for _, row in df.iterrows():
        if row["p-value"] < 0.05 and np.isfinite(row["-log10(p-value)"]):
            label = f"{row['Subgroup']}\n({int(row['n11'])})"
            y_off = -0.15 if str(row["Subgroup"]) == "Drugs≥5" else 0.0
            txt = ax.text(row["lnROR"] + 0.02, row["-log10(p-value)"] + y_off,
                          label, fontsize=8, ha="left", va="top", color="black")
            txt.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground="white"),
                                  path_effects.Normal()])

    # Threshold lines
    ax.axhline(y=1.3, color="black", linestyle="--", linewidth=1)  # p=0.05
    ax.axvline(x=0.0, color="black", linestyle="--", linewidth=1)  # lnROR=0

    # Axes & grid
    ax.set_xlabel("lnROR", fontsize=14)
    ax.set_ylabel("-log10(p-value)", fontsize=14)
    ax.grid(True)
    plt.tick_params(axis="both", labelsize=12)

    # Ensure a small headroom so the top-most points/labels are not clipped
    y_max = float(np.nanmax(df["-log10(p-value)"])) if len(df) else 0.0
    if np.isfinite(y_max):
        ax.set_ylim(top=y_max + 0.5)

    # Drug name box (upper-right)
    if title_drug:
        ax.text(0.99, 0.99, f"Drug: {title_drug}", transform=ax.transAxes,
                fontsize=12, ha="right", va="top",
                bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    # Legend (colors + size bins)
    legend_elements = []
    for db, color in db_color_map.items():
        legend_elements.append(mlines.Line2D([], [], color=color, marker="o",
                                             linestyle="None", markersize=8, label=f"{db}"))
    for mid, lab in [(5, "n < 10"), (50, "10 ≤ n < 100"), (150, "100 ≤ n < 200"), (250, "n ≥ 200")]:
        legend_elements.append(plt.scatter([], [], s=_map_n11_to_size(mid), color="gray", alpha=0.6, label=lab))
    legend_elements.insert(0, mlines.Line2D([], [], linestyle="None", label="Label: Subgroup (n)"))
    ax.legend(handles=legend_elements, title="DB / Report Count",
              loc="upper left", fontsize=10, title_fontsize=11,
              borderpad=1.0, labelspacing=1.0, handletextpad=1.2,
              frameon=True, facecolor="white", edgecolor="black")

    # Save (match the original: tight_layout, no bbox="tight")
    fig.tight_layout()
    fig.savefig(out_png, dpi=300)
    if out_tif:
        fig.savefig(out_tif, dpi=300, format="tiff")
    plt.close(fig)


def main():
    save_dir = tempfile.gettempdir()
    default_png = os.path.join(save_dir, "volcano_plot_with_embedded_legend.png")

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="CSV path (omit when using MSIP 'table')")
    ap.add_argument("--out",   default=default_png)
    ap.add_argument("--tif",   default=None)
    ap.add_argument("--title", default="Solifenacin")
    args, _ = ap.parse_known_args()

    df = _load_df(args)
    volcano_plot_core(df, out_png=args.out, out_tif=args.tif, title_drug=args.title)

    po = PNGObject(args.out)
    print("PNG saved to:", args.out)
    if args.tif:
        print("TIFF saved to:", args.tif)
    return po


if __name__ == "__main__":
    main()
