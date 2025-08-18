#!/usr/bin/env bash
set -euo pipefail

python python/01_disproportionality.py
python python/02_volcano_plots.py
python python/03_tto_distributions.py
python python/04_km_curves.py

echo "All steps completed."
