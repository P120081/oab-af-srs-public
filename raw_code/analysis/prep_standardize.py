#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
prep_standardize.py — one-shot OAB standardization for JADER/FAERS (CLI)

Examples:
  python raw_code/analysis/prep_standardize.py \
    --faers-in data/faers_DRUG.csv --faers-out data/derived/faers_oab_standardized.csv \
    --jader-in data/jader_DRUG.csv --jader-out data/derived/jader_oab_standardized.csv
"""
import argparse, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
JADER = REPO / "raw_code" / "jader" / "01_oab_standardize.py"
FAERS = REPO / "raw_code" / "faers" / "01_oab_standardize.py"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--faers-in",  type=str)
    ap.add_argument("--faers-out", type=str)
    ap.add_argument("--jader-in",  type=str)
    ap.add_argument("--jader-out", type=str)
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cmds = []
    if args.faers_in and args.faers_out:
        cmds.append([args.py, str(FAERS), "--in", args.faers_in, "--out", args.faers_out])
    if args.jader_in and args.jader_out:
        cmds.append([args.py, str(JADER), "--in", args.jader_in, "--out", args.jader_out])

    if not cmds:
        print("Nothing to do. Provide --faers-in/--faers-out and/or --jader-in/--jader-out.")
        return

    for cmd in cmds:
        if args.dry_run:
            print("[DRY]", " ".join(cmd))
        else:
            print("[RUN]", " ".join(cmd))
            rc = subprocess.call(cmd)
            if rc != 0:
                sys.exit(rc)

if __name__ == "__main__":
    main()
