
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forest plot (Fig.2) — MSIP-compatible + CLI-compatible
- In MSIP: uses `table.to_pandas()` and returns a PNGObject if available.
- In CLI:   pass `--table CSV` and `--out/--tif` to save images.
The rendering (fonts/colors/line widths/legend/scale) replicates the original.
"""

import os, sys, tempfile
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.colors as mcolors

# Font setup (Arial main; DejaVu Sans for symbols such as ✓)
matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Arial'
CHECK_FONT = fm.FontProperties(family='DejaVu Sans')

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
# Data loading
# ------------------------
def _load_df(args):
    # 1) CLI path takes priority
    if args is not None and getattr(args, "table", None):
        return pd.read_csv(args.table)

    # 2) MSIP: global `table` -> to_pandas() or DataFrame
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
    # coerce numerics
    for c in ["n11","ROR","ROR025","ROR975","PRR025","IC025","χ^2","p-value"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# Formatting helpers
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

def forest_plot_core(df: pd.DataFrame, out_png: str, out_tif: str):
    # Normalize
    df = _normalize_columns(df)

    # Signal flags (no EBGM in public version)
    df["Signal_ROR"] = (df["ROR025"] > 1) & (df["p-value"] < 0.05)
    df["Signal_PRR"] = (df["PRR025"] > 2) & (df["χ^2"] > 4) if "PRR025" in df.columns and "χ^2" in df.columns else False
    df["Signal_IC"]  = (df["IC025"] > 0) if "IC025" in df.columns else False

    # IC color scale
    def get_ic_color(ic025):
        if pd.isnull(ic025): return None
        if ic025 < 1.5: return mcolors.to_rgba("#0072B2", 0.3)
        if ic025 < 3.0: return mcolors.to_rgba("#0072B2", 0.7)
        return mcolors.to_rgba("#0072B2", 1.0)

    # Display strings
    df["ROR_CI_str"] = df.apply(lambda r: _format_ci(r["ROR"], r["ROR025"], r["ROR975"]), axis=1)
    df["p_str"] = df["p-value"].apply(_format_p)
    if "PRR025" in df.columns:
        df["PRR_str"] = df["PRR025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
    if "IC025" in df.columns:
        df["IC_str"] = df["IC025"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")
    if "χ^2" in df.columns:
        df["chi2_str"] = df["χ^2"].apply(lambda v: f"{v:.2f}" if pd.notnull(v) else "")

    # Column layout
    col_labels = ["Drug", "N", "ROR (95% CI)", "P value", "PRR025", "χ$^{2}$", "IC025", "Forest plot of ROR"]
    col_x = {"Drug": 1.5, "N": 3.0, "ROR (95% CI)": 5.0, "P value": 7.5, "PRR025": 9.0, "χ$^{2}$": 10.5, "IC025": 12.0}
    plot_start = col_x["IC025"] + 1
    plot_end   = plot_start + 4
    col_x["Forest plot of ROR"] = (plot_start + plot_end) / 2
    col_x["ROR"] = plot_end + 1
    col_x["PRR"] = plot_end + 2
    col_x["IC"]  = plot_end + 3

    fig_width  = max(col_x.values()) + 0.8
    row_height = 0.8
    row_bg     = '#f2f2f2'
    line_color = "#0072B2"
    marker_col = "#0072B2"
    ref_color  = "#D55E00"
    db_hdr     = {"JADER": "#fce4d6", "FAERS": "#ddebf7"}
    default_db = "#e0e0e0"

    # Build rows
    rows = []
    for db, sub_df in df.groupby("DB"):
        rows.append(("db", db, db_hdr.get(db, default_db)))
        rows.append(("header", None, None))
        for _, r in sub_df.iterrows():
            rows.append(("data", r, None))

    num_rows = len(rows) + 2
    fig_h = row_height * (num_rows + 1)

    fig, ax = plt.subplots(figsize=(fig_width, fig_h))
    ax.set_xlim(0, fig_width); ax.set_ylim(-0.5, num_rows - 0.5); ax.axis("off")

    # X scale (log ROR)
    max_ror975 = float(df["ROR975"].max(skipna=True))
    xmax = max(20.0, max_ror975 * 1.5)
    x_range_log = np.log10(xmax) - np.log10(0.5)
    def ror_to_x(val):
        return plot_start + (np.log10(val) - np.log10(0.5)) * (plot_end - plot_start) / x_range_log

    tick_exp_min = int(np.floor(np.log10(0.5)))
    tick_exp_max = int(np.ceil(np.log10(xmax)))
    tick_values = sorted(set([base * 10**exp for exp in range(tick_exp_min, tick_exp_max + 1) for base in [1,2,5] if 0.5 <= base * 10**exp <= xmax]))
    tick_pos = [ror_to_x(v) for v in tick_values]

    data_ys = []
    y = num_rows - 2

    for kind, content, bg in rows:
        yc = y + 0.5
        if kind == "db":
            ax.axhspan(y, y + 1, color=bg, alpha=0.3)
            ax.text(0.5, yc, content, fontsize=18, fontweight='bold', ha='left', va='center')
            ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=4)
            ax.hlines(y=y,     xmin=0, xmax=fig_width, color="black", linewidth=4)
        elif kind == "header":
            for label in col_labels:
                ax.text(col_x[label], yc, label, fontsize=18, fontweight='bold', ha='center', va='center')
            ax.hlines(y=y + 1, xmin=0, xmax=fig_width, color="black", linewidth=4)
            ax.hlines(y=y,     xmin=0, xmax=fig_width, color="black", linewidth=3)
            for key in ["ROR", "PRR", "IC"]:
                ax.text(col_x[key], yc, key, fontsize=18, fontweight='bold', ha='center', va='center')
        elif kind == "data":
            data_ys.append(y)
            row = content
            if y % 2 == 0:
                ax.axhspan(y, y + 1, color=row_bg)
            values = [row.get("drug_of_interest",""), str(int(row.get("n11",0))), row.get("ROR_CI_str",""), row.get("p_str","")]
            if "PRR_str" in row:  values.append(row["PRR_str"])
            if "chi2_str" in row: values.append(row["chi2_str"])
            if "IC_str"  in row:  values.append(row["IC_str"])
            values += [""] * 3
            for j, val in enumerate(values):
                x = list(col_x.values())[j]
                ax.text(x, yc, val, fontsize=16, ha='center', va='center')

            # CI bar + caps + marker
            try:
                lo, hi, mid = float(row["ROR025"]), float(row["ROR975"]), float(row["ROR"])
                if hi >= 0.5 and lo <= xmax:
                    x_lo = ror_to_x(max(lo, 0.5))
                    x_hi = ror_to_x(min(hi, xmax))
                    ax.hlines(yc, x_lo, x_hi, color=line_color, linewidth=3, zorder=3)
                    if lo >= 0.5: ax.vlines(x_lo, yc - 0.2, yc + 0.2, color=line_color, linewidth=3, zorder=3)
                    if hi <= xmax: ax.vlines(x_hi, yc - 0.2, yc + 0.2, color=line_color, linewidth=3, zorder=3)
                    if 0.5 <= mid <= xmax: ax.plot(ror_to_x(mid), yc, marker='s', color=marker_col, markersize=6)
                    if lo < 0.5:  ax.text(ror_to_x(0.5) - 0.2, yc, "<", fontsize=12, ha='right', va='center', color=line_color)
                    if hi > xmax: ax.text(ror_to_x(xmax) + 0.2, yc, ">", fontsize=12, ha='left',  va='center', color=line_color)
            except Exception:
                pass

            # Signal tiles
            if bool(row.get("Signal_ROR", False)):
                x = col_x["ROR"]
                ax.add_patch(plt.Rectangle((x - 0.3, y + 0.25), 0.6, 0.6, color="#009E73"))
                ax.text(x, yc, "✓", fontsize=16, color="white", ha='center', va='center', fontproperties=CHECK_FONT)
            if bool(row.get("Signal_PRR", False)):
                x = col_x["PRR"]
                ax.add_patch(plt.Rectangle((x - 0.3, y + 0.25), 0.6, 0.6, color="#F0E442"))
                ax.text(x, yc, "✓", fontsize=16, color="black", ha='center', va='center', fontproperties=CHECK_FONT)
            if bool(row.get("Signal_IC", False)):
                x = col_x["IC"]
                ic_color = get_ic_color(row.get("IC025"))
                if ic_color is not None:
                    ax.add_patch(plt.Rectangle((x - 0.3, y + 0.25), 0.6, 0.6, color=ic_color))
                    ax.text(x, yc, "✓", fontsize=16, color="white", ha='center', va='center', fontproperties=CHECK_FONT)

        y -= 1

    if data_ys:
        ax.hlines(y=min(data_ys), xmin=0, xmax=fig_width, color="black", linewidth=4)

    # Reference line at ROR=1 per DB section
    x_ref = ror_to_x(1.0)
    section_rows = []
    y = num_rows - 2
    for kind, _, _ in rows:
        if kind == "db":
            if section_rows:
                ymin = min(section_rows); ymax = max(section_rows) + 1
                ax.vlines(x_ref, ymin=ymin, ymax=ymax, color=ref_color, linestyle='--', linewidth=3)
                section_rows = []
        elif kind == "data":
            section_rows.append(y)
        y -= 1
    if section_rows:
        ymin = min(section_rows); ymax = max(section_rows) + 1
        ax.vlines(x_ref, ymin=ymin, ymax=ymax, color=ref_color, linestyle='--', linewidth=3, zorder=2)

    # X ticks
    for x, val in zip(tick_pos, tick_values):
        ax.text(x, 0.5, str(val), ha='center', va='top', fontsize=12)
        ax.vlines(x, ymin=1, ymax=0.7, color="black", linewidth=3)

    # IC025 legend
    legend_items = [
        ("IC025 < 1.5",       mcolors.to_rgba("#0072B2", 0.3)),
        ("1.5 ≤ IC025 < 3.0", mcolors.to_rgba("#0072B2", 0.7)),
        ("IC025 ≥ 3.0",       mcolors.to_rgba("#0072B2", 1.0)),
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
    fig.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.1)
    fig.savefig(out_tif, dpi=300, format="tiff", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

def main():
    # Default save paths (MSIP-style temp dir)
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
    forest_plot_core(df, out_png=args.out, out_tif=args.tif)

    po = PNGObject(args.out)  # returned in MSIP
    print("PNG saved to:", args.out)
    print("TIFF saved to:", args.tif)
    return po

if __name__ == "__main__":
    main()
