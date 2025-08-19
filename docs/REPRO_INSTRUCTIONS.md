# Reproducibility instructions (MSIP + Python)

This document explains how to regenerate the public figures and tables from the provided code and intermediate exports.

## Environment
- Python packages (see `requirements.txt`):
  - pandas, numpy, scipy, matplotlib, joblib
- Fonts: Arial (used by plotting scripts)

---

## A. Disproportionality analysis (Figures 2–4)

### Step 1 — OAB normalization and AF extraction
- **JADER**: `raw_code/jader/01_oab_standardize.py` → outputs `OAB_STD_J(j_id, drug_of_interest)`
- **FAERS**: `raw_code/faers/01_oab_standardize.py` → outputs `OAB_STD_F(primaryid, drug_of_interest)`
- AF selection in MSIP:
  - FAERS: REAC.pt == `"Atrial fibrillation"` → `F_AF(primaryid)`
  - JADER: REAC.有害事象 == `"心房細動"` → `J_AF(j_id)`

### Step 2 — Patient-level IDs and drug counts
- **JADER**: patient-level with `drug_count`
- **FAERS**: deduped PLID with `number_of_drug`
- Logical names are listed in `docs/DATA_INTERFACES.md`.

### Step 3 — 2×2 counts
- Count tables per drug (`n11, n12, n21, n22`) are produced via MSIP according to the specs in `msip/jader/*` and `msip/faers/*`.
- Export as CSV as needed.

### Step 4 — Metrics (ROR/PRR/IC, p-values)
- Run `raw_code/analysis/01_disproportionality.py` inside MSIP with:
  - `table`: totals row `[N, n+1]`
  - `table1`: per-drug `[label, n1+, n11]`
- Output schema includes numeric `p` and `ROR`.
- Remove rows with `n11 < 3` when preparing figures.

### Step 5 — Figure 2 (forest plot)
- In MSIP, run `raw_code/plots/forest_plot.py` with `table=` a CSV containing at least `DB, drug_of_interest, n11, ROR, ROR025, ROR975` (optional: `p`/`p-value`, `PRR025`, `chi2`/`χ^2`, `IC025`); the script outputs `figure2_forest_plot.png` and `figure2_forest_plot.tif`.

### Step 6 — Figure 3 (Excel-based overview)
- Paste metrics into your Excel template:
  - `data/derived/jader_metrics.csv`
  - `data/derived/faers_metrics.csv`

### Step 7 — Figure 4 (volcano)
- Prepare one CSV per drug with columns:  
  `DB, drug_of_interest, Subgroup, n11, n12, n21, n22, ROR, p, PRR, PRR025, PRR975, chi2, IC, IC025, IC975`
- Run `raw_code/plots/volcano_plot.py` in MSIP (`table` = the CSV).
  - The script auto-normalizes:
    - `p` from `p` or `p-value`
    - `Subgroup`: `≥` → `>=`
  - Output: `volcano_plot.png`
- Optional: legend-only via `raw_code/plots/volcano_legend.py` (output: `volcano_legend_only.png`).

---

## B. Time-to-onset analysis (Table 2 & Figure 6)

### TS1 — Build time-series PLID
- **JADER**: `msip/jader/j40_plid_timeseries.md` → `J_PLID_TS(j_id, sex?, age?, drug_name, start_date, event_term, event_date)`
- **FAERS**: `msip/faers/f40_plid_timeseries.md` → `F_PLID_TS(primaryid, sex?, age?, drug_name, start_dt, event_term, event_dt)`

### TS2 — Select the earliest (start, event) pair
- MSIP Python: `raw_code/analysis/02_tto_earliest_pair.py`  
  - Defaults: date columns by position `(start_idx=2, event_idx=4)`; change constants if your column order differs.

### TS3 — Compute TTO (days) and filter negatives
- **JADER**: `msip/jader/j45_tto_compute.md` → `J_TTO(j_id, drug_name, event_term, TTO)`
- **FAERS**: `msip/faers/f45_tto_compute.md` → `F_TTO(primaryid, drug_name, event_term, TTO)`

### TS4 — Table 2 (Weibull)
- MSIP Python: `raw_code/analysis/03_tto_weibull.py` with `table=` the final TTO table.  
- Outputs: `table2_weibull_params.csv`, `weibull_bootstrap_hist.png` (also prints estimates and 95% CIs).

### TS5 — Figure 6 (KM, raw)
- MSIP Python: `raw_code/plots/kaplan_meier_raw.py`  
  - Minimum columns: `DB` (1/2 or strings) and `TTO` (days). Defaults: position 0 = `DB`, position 4 = `TTO`.  
  - Output: `figure6_km_raw.png`.

### TS6 — Figure 6 (KM, bootstrap IQR ribbon)
- MSIP Python: `raw_code/plots/kaplan_meier_bootstrap.py`  
  - Same inputs as TS5; outputs `figure6_km_bootstrap_iqr.png`.

---

## Notes
- Use ASCII logical names in public CSVs (e.g., `chi2`) and normalize any tool-specific column headers before committing.
- Font is unified to Arial in plotting scripts; add `joblib` to `requirements.txt` for bootstrap/parallel code.
