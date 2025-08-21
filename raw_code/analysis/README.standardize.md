# Standardization runner

- `raw_code/faers/01_oab_standardize.py` — FAERS OAB標準化（MSIP/CLI）
- `raw_code/jader/01_oab_standardize.py` — JADER OAB標準化（MSIP/CLI）
- `raw_code/analysis/prep_standardize.py` — 両者を一括で動かすための小さなラッパー。

## Example
```bash
python raw_code/analysis/prep_standardize.py   --faers-in data/faers_DRUG.csv --faers-out data/derived/faers_oab_standardized.csv   --jader-in data/jader_DRUG.csv --jader-out data/derived/jader_oab_standardized.csv
```
_Last updated: 2025-08-21._
