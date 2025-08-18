#!/usr/bin/env python3
"""Compute disproportionality metrics (ROR/PRR/IC) from 2x2 counts.

Inputs:
  data/counts_2x2/*.csv  (ASCII headers: drug,event,n11,n12,n21,n22)
Outputs:
  figures/fig2_ror.png, figures/fig3_ic.png (example)
Notes:
  - ASCII labels only.
  - No raw FAERS/JADER data in the repo.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data" / "counts_2x2"
    out_dir = root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Reading 2x2 counts from", data_dir)
    files = list(data_dir.glob("*.csv"))
    if not files:
        print("No input CSVs found. Add files to data/counts_2x2/")
        return 0

    print("Found", len(files), "file(s). Computing metrics...")
    # TODO: real implementation

    import matplotlib.pyplot as plt
    plt.figure()
    plt.title("Placeholder: ROR/PRR/IC results")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.savefig(out_dir / "fig_placeholder_disproportionality.png", dpi=300)
    print("Saved figure:", out_dir / "fig_placeholder_disproportionality.png")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
