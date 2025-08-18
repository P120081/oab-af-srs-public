#!/usr/bin/env python3
"""Time-to-onset (TTO) distributions.

Inputs:
  data/tto_samples/*.csv  (derived, minimal)
Outputs:
  figures/fig5_tto.png
"""
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data" / "tto_samples"
    out_dir = root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.title("Placeholder: TTO distributions")
    plt.xlabel("Days")
    plt.ylabel("Frequency")
    plt.savefig(out_dir / "fig_placeholder_tto.png", dpi=300)
    print("Saved figure:", out_dir / "fig_placeholder_tto.png")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
