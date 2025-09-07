# Standardization Runner

This folder contains utilities to **standardize Overactive Bladder (OAB) records** for both **FAERS** and **JADER**. You can run them inside **MSIP** or from the **command line**.

## Scripts
- `raw_code/faers/01_oab_standardize.py` — FAERS OAB standardization (MSIP/CLI).
- `raw_code/jader/01_oab_standardize.py` — JADER OAB standardization (MSIP/CLI).
- `raw_code/analysis/prep_standardize.py` — Lightweight wrapper to run both at once.

## Example
```bash
python raw_code/analysis/prep_standardize.py   --faers-in data/faers_DRUG.csv   --faers-out data/derived/faers_oab_standardized.csv   --jader-in data/jader_DRUG.csv   --jader-out data/derived/jader_oab_standardized.csv
```

_Last updated: 2025-09-07._
