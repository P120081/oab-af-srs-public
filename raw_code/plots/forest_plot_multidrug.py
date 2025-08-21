
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest plot (Fig.3, multi-drug stratified) — MSIP-compatible + CLI-compatible
- MSIP: uses `table.to_pandas()`; returns a PNGObject if available.
- CLI:  use `--table CSV` and `--out/--tif` to save the figure.
The rendering mirrors the original: drug & DB section headers, log-scale ROR,
reference line at ROR=1 per section, signal tiles (ROR/PRR/IC), and IC opacity legend.
"""

import os, tempfile
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Arial'                 # main font
CHECK_FONT = fm.FontProperties(family='DejaVu Sans')  # for glyphs like ✓

# Optional MSIP PNGObject
PNGObject = None
try:
    from msi.common.visualization import PNGObject as _PNGObject
    PNGObject = _PNGObject
except Exception:
    class PNGObject:  # fallback for non-MSIP environments
        def __init__(self, path): self.path = path
        def __repr__(self): return f"PNGObject({self.path})"


# ------------------------
# Data loading & normalization
# ------------------------
def _load_df(args):
    if args is not None and getattr(args, "table", None):
        return pd.read_csv(args.table)
    glob = globals()
    if "table" in glob:
        t = glob["table"]
        if hasattr(t, "to_pandas"):
            return t.to_pandas()
        if isinstance(t, pd.DataFrame):
            return t.copy()
    raise RuntimeError("No input provided. Use --table <CSV> or supply MSIP 'table'.")

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Minimal header normalization so public CSVs also work."""
    df = df.copy()
    # p-value
    if "p-value" not in df.columns and "p_value" in df.columns:
        df = df.rename(columns={"p_value": "p-value"})
    if "p-value" not in df.columns and "p" in df.columns:
        df = df.rename(columns={"p": "p-value"})
    # chi-square
    for cand in ["chi2", "χ²", "Chi2", "X2", "x2"]:
        if "χ^2" not in df.columns and cand in df.columns:
            df = df.rename(columns={cand: "χ^2"}); break
    # drug label
    if "drug_of_interest" not in df.columns and "Drug" in df.columns:
        df = df.rename(columns={"Drug": "drug_of_interest"})
    # subgroup
    if "Subgroup" not in df.columns and "subgroup" in df.columns:
        df = df.rename(columns={"subgroup": "Subgroup"})
    # coerce numerics
    for c in ["n11","ROR","ROR025","ROR975","PRR025","IC025","χ^2","p-value"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# ------------------------
# Formatting helpers
# ------------------------
def _format_ci(val, lo, hi):
    import pandas as _pd
    if _pd.isnull(val) or _pd.isnull(lo) or _pd.isnull(hi):
        return ""
    return f"{val:.2f} ({lo:.2f}–{hi:.2f})"

def _format_p(p):
    import pandas as _pd
    if _pd.isnull(p): return ""
    if p < 0.001:     return "<0.001"
    if p < 0.05:      return "<0.05"
    return f"{p:.2f}"


# ------------------------
# Plot core
# ------------------------
def forest_plot_multidrug_core(df: pd.DataFrame, out_png: str, out_tif: str):
    df = _normalize_columns(df)

    # Signals
    df["Signal_ROR"] = (df["ROR025"] > 1) & (df["p-value"] < 0.05)
    df["Signal_PRR"] = (df["PRR025"] > 2) & (df["χ^2"] > 4) if "PRR025" in df.columns and "χ^2" in df.columns else False
    df["Signal_IC"]  = (df["IC025"] > 0) if "IC025" in df.columns else False

    # Display strings
    df["ROR_CI_str"] = df.apply(lambda r: _format_ci(r["ROR"], r["ROR025"], r["ROR975"]), axis=1)
    df["p_str"] = df["p-value"].apply(_format_p)
    if "PRR025" in df.columns:
        df["PRR_str"]  = df["PRR025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
    if "IC025" in df.columns:
        df["IC_str"]   = df["IC025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
    if "χ^2" in df.columns:
        df["chi2_str"] = df["χ^2"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")

    # Okabe–Ito palette (excluding colors used elsewhere)
    okabe_ito = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
    signal_ror = "#009E73"     # green
    signal_prr = "#F0E442"     # yellow
    signal_ic_base = "#0072B2" # blue

    line_color   = "#0072B2"
    marker_color = "#0072B2"
    fill_color   = "#D55E00"
    ref_color    = "#D55E00"
    row_bg_color = "#f2f2f2"
    db_colors    = {"JADER": "#fce4d6", "FAERS": "#ddebf7"}
    default_db   = "#e0e0e0"

    # Build drug color dictionary (light alpha)
    excluded = {signal_ror, signal_prr, signal_ic_base, "#000000"}
    drug_palette = [c for c in okabe_ito if c not in excluded]
    idx = 0
    drug_color = {}
    for drug in df["drug_of_interest"].dropna().unique():
        color = drug_palette[idx % len(drug_palette)]; idx += 1
        drug_color[drug] = mcolors.to_rgba(color, alpha=0.3)

    def ic_color(ic025):
        if pd.isnull(ic025): return None
        if ic025 < 1.5: return mcolors.to_rgba(signal_ic_base, 0.3)
        if ic025 < 3.0: return mcolors.to_rgba(signal_ic_base, 0.7)
        return mcolors.to_rgba(signal_ic_base, 1.0)

    # Row blocks: [drug header] -> [DB header] -> header -> data...
    row_height = 0.8
    grouped = df.groupby(["drug_of_interest", "DB"])
    row_blocks = []
    prev_drug = None
    header = ["Subgroup", "N", "ROR (95% CI)", "P value", "PRR025", "χ²", "IC025",
              "Forest plot of ROR", "ROR_check", "PRR_check", "IC_check"]

    for (drug, db), sub_df in grouped:
        block = []
        if drug != prev_drug:
            block.append(("drug", drug, {"bg_color": drug_color.get(drug, (0.9,0.9,0.9,0.3))}))
        block.append(("db", db, {"bg_color": db_colors.get(db, default_db)}))
        block.append(("header", header, None))
        prev_drug = drug
        for _, r in sub_df.iterrows():
            row = [r["Subgroup"], f"{int(r['n11'])}", r["ROR_CI_str"], r["p_str"], r.get("PRR_str",""),
                   r.get("chi2_str",""), r.get("IC_str",""), "", "", "", ""]
            block.append(("data", row, r))
        row_blocks.append(block)

    # Layout and axes
    num_rows = sum(len(b) for b in row_blocks) + 2
    fig_height = row_height * (num_rows + 2)
    col_x = {
        "Subgroup": 1.5, "N": 3.0, "ROR (95% CI)": 5.0, "P value": 7.5,
        "PRR025": 9.0, "χ²": 10.5, "IC025": 12.0
    }
    plot_start = col_x["IC025"] + 1
    plot_end   = plot_start + 4
    col_x["Forest plot of ROR"] = (plot_start + plot_end) / 2
    col_x["ROR_check"] = plot_end + 1
    col_x["PRR_check"] = col_x["ROR_check"] + 1
    col_x["IC_check"]  = col_x["PRR_check"] + 1
    fig_width = max(col_x.values()) + 0.5

    max_ror975 = float(df["ROR975"].max(skipna=True))
    xmax = max(20.0, max_ror975 * 1.5)
    def ror_to_x(val):
        return plot_start + (np.log10(val) - np.log10(0.5)) * (plot_end - plot_start) / (np.log10(xmax) - np.log10(0.5))

    tick_values = [v for v in [0.5, 1, 2, 5, 10, 20, 50, 100] if v <= xmax]
    tick_pos = [ror_to_x(v) for v in tick_values]

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_xlim(0, fig_width); ax.set_ylim(-0.5, num_rows - 0.5); ax.axis("off")

    y = num_rows - 2
    for block in row_blocks:
        data_rows = []
        for i, (kind, content, r) in enumerate(block):
            yc = y + 0.5
            if kind == "drug":
                ax.axhspan(y, y + 1, color=r["bg_color"])
                ax.text(0.5, yc, content, fontsize=24, fontweight='bold', ha='left', va='center')
                ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=4)
            elif kind == "db":
                ax.axhspan(y, y + 1, color=r["bg_color"], alpha=0.3)
                ax.text(1.0, yc, content, fontsize=20, ha='left', va='center')
                ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=3)
            elif kind == "header":
                for label in content:
                    if label in col_x:
                        disp = label.replace("_check","") if "_check" in label else label
                        ax.text(col_x[label], yc, disp, fontsize=20, fontweight='bold', ha='center', va='center')
                ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=3)
                ax.hlines(y=y,     xmin=0, xmax=fig_width, color="black", linewidth=3)
            elif kind == "data":
                if y % 2 == 0:
                    ax.axhspan(y, y + 1, color=row_bg_color)
                data_rows.append(y)

                # table text
                for j, label in enumerate(content):
                    x_key = header[j]
                    if x_key in col_x:
                        ax.text(col_x[x_key], yc, str(label), fontsize=18, ha='center', va='center')

                # CI bars / diamond for "Overall"
                try:
                    lo, hi, mid = float(r["ROR025"]), float(r["ROR975"]), float(r["ROR"])
                    if str(r["Subgroup"]).lower() != "overall":
                        if hi >= 0.5 and lo <= xmax:
                            x_lo = ror_to_x(max(lo, 0.5))
                            x_hi = ror_to_x(min(hi, xmax))
                            ax.hlines(yc, x_lo, x_hi, color=line_color, linewidth=3)
                            if lo >= 0.5:
                                ax.vlines(x_lo, yc - 0.2, yc + 0.2, color=line_color, linewidth=3, zorder=2)
                            else:
                                ax.text(ror_to_x(0.5) - 0.2, yc, "<", fontsize=14, ha='right', va='center', color=line_color)
                            if hi <= xmax:
                                ax.vlines(x_hi, yc - 0.2, yc + 0.2, color=line_color, linewidth=3)
                            else:
                                ax.text(ror_to_x(xmax) + 0.2, yc, ">", fontsize=14, ha='left', va='center', color=line_color)
                            if 0.5 <= mid <= xmax:
                                ax.plot(ror_to_x(mid), yc, marker='s', markersize=6, color=marker_color)
                    else:
                        x_lo = ror_to_x(lo); x_hi = ror_to_x(hi); x_mid = ror_to_x(mid)
                        dx = [x_lo, x_mid, x_hi, x_mid, x_lo]
                        dy = [yc, yc + 0.15, yc, yc - 0.15, yc]
                        ax.fill(dx, dy, color=fill_color, alpha=1.0, zorder=2)
                        ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=3)
                except Exception:
                    pass

                # Signal tiles
                if bool(r.get("Signal_ROR", False)):
                    ax.add_patch(plt.Rectangle((col_x["ROR_check"] - 0.3, y + 0.25), 0.6, 0.6, color=signal_ror))
                    ax.text(col_x["ROR_check"], yc, "✓", fontsize=18, color="white", ha='center', va='center', fontproperties=CHECK_FONT)
                if bool(r.get("Signal_PRR", False)):
                    ax.add_patch(plt.Rectangle((col_x["PRR_check"] - 0.3, y + 0.25), 0.6, 0.6, color=signal_prr))
                    ax.text(col_x["PRR_check"], yc, "✓", fontsize=18, color="black", ha='center', va='center', fontproperties=CHECK_FONT)
                if bool(r.get("Signal_IC", False)):
                    c = ic_color(r.get("IC025"))
                    if c is not None:
                        ax.add_patch(plt.Rectangle((col_x["IC_check"] - 0.3, y + 0.25), 0.6, 0.6, color=c))
                        ax.text(col_x["IC_check"], yc, "✓", fontsize=18, color="white", ha='center', va='center', fontproperties=CHECK_FONT)

                # bottom border of block
                if i == len(block) - 1:
                    ax.hlines(y=y, xmin=0, xmax=fig_width, color="black", linewidth=4)
            y -= 1

        # vertical reference line at ROR=1 for this block
        if data_rows:
            ax.vlines(ror_to_x(1.0), ymin=min(data_rows), ymax=max(data_rows) + 1,
                      color=ref_color, linestyle='--', linewidth=3, zorder=1)

    # X ticks
    for x, val in zip(tick_pos, tick_values):
        ax.text(x, 0.5, str(val), ha='center', va='top', fontsize=14)
        ax.vlines(x, ymin=1, ymax=0.7, color="black", linewidth=3)

    # IC025 legend (opacity scale)
    legend_items = [
        ("IC025 < 1.5",       mcolors.to_rgba(signal_ic_base, 0.3)),
        ("1.5 ≤ IC025 < 3.0", mcolors.to_rgba(signal_ic_base, 0.7)),
        ("IC025 ≥ 3.0",       mcolors.to_rgba(signal_ic_base, 1.0)),
    ]
    legend_box_w = 0.6; text_gap = 0.2; item_gap = 0.5
    renderer = fig.canvas.get_renderer()

    widths = []
    for label, _ in legend_items:
        tmp = ax.text(0, 0, label, fontsize=14)
        bbox = tmp.get_window_extent(renderer=renderer)
        inv = ax.transData.inverted()
        text_w = inv.transform((bbox.width, 0))[0] - inv.transform((0, 0))[0]
        tmp.remove()
        widths.append(legend_box_w + text_gap + text_w + item_gap)

    legend_total_w = sum(widths)
    legend_x = fig_width - legend_total_w
    legend_y = -0.6

    x_c = legend_x
    for (label, color), w in zip(legend_items, widths):
        ax.add_patch(plt.Rectangle((x_c, legend_y), legend_box_w, 0.6, color=color))
        ax.text(x_c + legend_box_w + text_gap, legend_y + 0.3, label, fontsize=14, va='center', ha='left')
        x_c += w

    # Save
    fig.savefig(out_tif, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
    fig.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def main():
    save_dir = tempfile.gettempdir()
    default_png = os.path.join(save_dir, "forest_plot.png")
    default_tif = os.path.join(save_dir, "forest_plot.tif")

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="CSV path (omit when using MSIP 'table')")
    ap.add_argument("--out",   default=default_png)
    ap.add_argument("--tif",   default=default_tif)
    args, _ = ap.parse_known_args()

    df = _load_df(args)
    forest_plot_multidrug_core(df, out_png=args.out, out_tif=args.tif)

    po = PNGObject(args.out)
    print("PNG saved to:", args.out)
    print("TIFF saved to:", args.tif)
    return po


if __name__ == "__main__":
    main()
