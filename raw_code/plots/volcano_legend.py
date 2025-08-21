
#!/usr/bin/env python3
import matplotlib.pyplot as plt, matplotlib.lines as mlines
from _common_utils import OKABE_ITO

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams['font.sans-serif'] = ['DejaVu Sans','Arial','Segoe UI','Helvetica']

def map_n11_to_size(n: float) -> float:
    if n < 10:   return 40
    if n < 100:  return 90
    if n < 200:  return 140
    return 200

def legend_only(out_png: str):
    db_color_map = {"JADER": OKABE_ITO["Orange"], "FAERS": OKABE_ITO["SkyBlue"]}
    size_labels = ["n < 10","10 ≤ n < 100","100 ≤ n < 200","n ≥ 200"]
    size_vals = [40, 90, 140, 200]
    fig, ax = plt.subplots(figsize=(4.0, 2.0)); ax.axis("off")
    handles = [mlines.Line2D([], [], linestyle="None", label="Label: Subgroup (n)")]
    for db, color in db_color_map.items():
        handles.append(mlines.Line2D([], [], color=color, marker="o", linestyle="None", markersize=8, label=db))
    for s, label in zip(size_vals, size_labels):
        handles.append(plt.scatter([], [], s=s, color="gray", alpha=0.6, label=label))
    ax.legend(handles=handles, title="DB / Report Count", loc="center", fontsize=10, title_fontsize=11, frameon=False)
    plt.savefig(out_png, dpi=300, bbox_inches="tight", transparent=True); plt.close()

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=False, default="volcano_legend_only.png")
    args = ap.parse_args()
    legend_only(out_png=args.out)

if __name__ == "__main__":
    main()
