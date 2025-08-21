#!/usr/bin/env python3

"""
make_figures.py — One-shot runner for public figures.

Usage examples:
  # run everything (default)
  python raw_code/analysis/make_figures.py

  # run specific targets
  python raw_code/analysis/make_figures.py --fig2 --fig4 --fig6

  # dry-run (show commands only)
  python raw_code/analysis/make_figures.py --dry-run

Inputs (default locations):
  data/derived/figure2_source.csv
  data/derived/figure3_stratified.csv      (optional)
  data/derived/figure6_km_source.csv       (optional)
  data/derived/volcano_*.csv               (optional)
  data/derived/tto_*.csv                   (optional)

Outputs:
  docs/figure2_forest_plot.(png|tif)
  docs/figure3_forest_plot.png             (if stratified CSV exists)
  docs/volcano_<drug>.png                  (for each volcano_*.csv)
  docs/figure5_tto_<name>.png              (for each tto_*.csv)
  docs/figure6_km_raw.png                  (if figure6_km_source.csv exists)
"""
import argparse, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # repo root
PLOTS = REPO / "raw_code" / "plots"
DERIVED = REPO / "data" / "derived"
DOCS = REPO / "docs"

def run(cmd, dry_run=False):
    if dry_run:
        print("[DRY] ", " ".join(cmd)); return 0
    print("[RUN] ", " ".join(cmd))
    return subprocess.call(cmd)

def ensure_docs():
    DOCS.mkdir(parents=True, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig2", action="store_true", help="Build Figure 2 (forest)")
    ap.add_argument("--fig3", action="store_true", help="Build Figure 3 (stratified forest) if data present")
    ap.add_argument("--fig4", action="store_true", help="Build Figure 4 (volcano) for each volcano_*.csv")
    ap.add_argument("--fig5", action="store_true", help="Build Figure 5 (TTO distribution) for each tto_*.csv")
    ap.add_argument("--fig6", action="store_true", help="Build Figure 6 (KM raw) if data present")
    ap.add_argument("--all",  action="store_true", help="Build all (default if no flags)")
    ap.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    ap.add_argument("--py", default=sys.executable, help="Python executable to use for sub-commands")
    args = ap.parse_args()

    if not any([args.fig2, args.fig3, args.fig4, args.fig5, args.fig6, args.all]):
        args.all = True

    ensure_docs()

    # Validate data (if validator exists)
    validator = REPO / "raw_code" / "analysis" / "validate_data.py"
    if validator.exists():
        run([args.py, str(validator)], dry_run=args.dry_run)

    # FIGURE 2
    if args.fig2 or args.all:
        src = DERIVED / "figure2_source.csv"
        if src.exists():
            out_png = DOCS / "figure2_forest_plot.png"
            out_tif = DOCS / "figure2_forest_plot.tif"
            cmd = [args.py, str(PLOTS/"forest_plot.py"),
                   "--table", str(src),
                   "--out", str(out_png),
                   "--tif", str(out_tif)]
            run(cmd, dry_run=args.dry_run)
        else:
            print("[SKIP] Figure 2: missing", src)

    # FIGURE 3 (optional stratified forest)
    if args.fig3 or args.all:
        src = DERIVED / "figure3_stratified.csv"
        if src.exists():
            out_png = DOCS / "figure3_forest_plot.png"
            cmd = [args.py, str(PLOTS/"forest_plot_multidrug.py"),
                   "--table", str(src),
                   "--out", str(out_png)]
            run(cmd, dry_run=args.dry_run)
        else:
            print("[SKIP] Figure 3: missing", src)

    # FIGURE 4 (volcano per drug)
    if args.fig4 or args.all:
        found = False
        for csv in sorted(DERIVED.glob("volcano_*.csv")):
            found = True
            drug = csv.stem.replace("volcano_","")
            out_png = DOCS / f"volcano_{drug}.png"
            cmd = [args.py, str(PLOTS/"volcano_plot.py"),
                   "--table", str(csv),
                   "--out", str(out_png),
                   "--title", drug.upper()]
            run(cmd, dry_run=args.dry_run)
        if not found:
            print("[SKIP] Figure 4: no volcano_*.csv found under", DERIVED)

    # FIGURE 5 (TTO distributions per file)
    if args.fig5 or args.all:
        found = False
        for csv in sorted(DERIVED.glob("tto_*.csv")):
            found = True
            name = csv.stem.replace("tto_","")
            out_png = DOCS / f"figure5_tto_{name}.png"
            cmd = [args.py, str(PLOTS/"figure5_tto_distribution.py"),
                   "--table", str(csv),
                   "--out", str(out_png)]
            run(cmd, dry_run=args.dry_run)
        if not found:
            print("[SKIP] Figure 5: no tto_*.csv found under", DERIVED)

    # FIGURE 6 (KM raw)
    if args.fig6 or args.all:
        src = DERIVED / "figure6_km_source.csv"
        if src.exists():
            out_png = DOCS / "figure6_km_raw.png"
            cmd = [args.py, str(PLOTS/"kaplan_meier_raw.py"),
                   "--table", str(src),
                   "--out", str(out_png)]
            run(cmd, dry_run=args.dry_run)
        else:
            print("[SKIP] Figure 6: missing", src)

if __name__ == "__main__":
    main()
