# Figure / Table mapping

This repository maps every public figure/table to the exact code and inputs used.

## Figure 2 — Forest plot
- **Input CSV columns (minimum)**  
  `DB, drug_of_interest, n11, ROR, ROR025, ROR975`  
  *(optional)* `p` or `p-value`, `PRR025`, `chi2` (or `χ^2`), `IC025`
- **Code**  
  `raw_code/plots/forest_plot.py`
- **Output**  
  `figure2_forest_plot.png`, `figure2_forest_plot.tif`
- **Notes**  
  Signals are annotated as:  
  ROR: `ROR025>1 & p<0.05` / PRR: `PRR025>2 & chi2>4` / IC: `IC025>0`

## Figure 3 — Disproportionality metrics overview (Excel-based)
- **Inputs**
  - `data/derived/jader_metrics.csv`
  - `data/derived/faers_metrics.csv`
  - Schema (columns):  
    `drug_of_interest, n11, n12, n21, n22, ROR, ROR025, ROR975, p, p_value, PRR, PRR025, PRR975, chi2, IC, IC025, IC975, IC_strength, met_ROR, met_PRR, met_IC`
- **Code**
  - Metrics generation: `raw_code/analysis/01_disproportionality.py`
- **Notes**
  - Rows with `n11 < 3` are excluded before pasting to Excel (analysis rule).

## Figure 4 — Volcano plot (per drug)
- **Inputs**
  - CSV per drug (e.g., Solifenacin) with schema:  
    `DB, drug_of_interest, Subgroup, n11, n12, n21, n22, ROR, p, PRR, PRR025, PRR975, chi2, IC, IC025, IC975`
  - `Subgroup` tokens are ASCII only (e.g., `Drugs>=5`).
- **Code**
  - Plot: `raw_code/plots/volcano_plot.py`
  - Legend-only (optional): `raw_code/plots/volcano_legend.py`
- **Rendering rules**
  - `x = ln(ROR)`, `y = -log10(p)`; points sized by `n11`; colors: JADER=orange, FAERS=sky blue.
  - Labels appear only if `p < 0.05` as `Subgroup (n11)`.

## Figure 6 — Kaplan–Meier–style cumulative curves
- **Raw curve (per DB)**  
  - **Inputs**: CSV with at least `DB` (1/2 or strings) and `TTO` (days). Default positions: column 0 = DB, column 4 = TTO.  
  - **Code**: `raw_code/plots/kaplan_meier_raw.py`  
  - **Output**: `figure6_km_raw.png`
- **Bootstrap median with IQR ribbon**  
  - **Inputs**: same as above  
  - **Code**: `raw_code/plots/kaplan_meier_bootstrap.py`  
  - **Output**: `figure6_km_bootstrap_iqr.png`

## Table 2 — Weibull parameters from TTO
- **Inputs**: CSV with `TTO` column (strictly positive).  
- **Code**: `raw_code/analysis/03_tto_weibull.py`  
- **Outputs**: `table2_weibull_params.csv`, `weibull_bootstrap_hist.png`

## Data interfaces
- Canonical logical table names: `docs/DATA_INTERFACES.md`.
