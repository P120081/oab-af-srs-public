# Figure / Table mapping

This file lists, for each public object, the **script**, **inputs**, **required columns**, **outputs**, and any **parameters**. A CSV version is provided as `FIGURE_TABLE_MAP.csv`.

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

## Figure 3 — Disproportionality metrics overview
- **Inputs**
  - `data/derived/jader_metrics.csv`
  - `data/derived/faers_metrics.csv`
  - Schema (columns):  
    `drug_of_interest, n11, n12, n21, n22, ROR, ROR025, ROR975, p, p_value, PRR, PRR025, PRR975, chi2, IC, IC025, IC975, IC_strength, met_ROR, met_PRR, met_IC`
- **Code**
  - Metrics generation: `raw_code/analysis/01_disproportionality.py`
- **Notes**
  - Rows with `n11 < 3` are excluded before pasting to Excel (as per analysis rule).

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

## Figure 5 — TTO distribution (Weibull PDF + histogram + boxplot)
- **Code**: `raw_code/plots/figure5_tto_distribution.py`
- **Input**: MSIP table where column index 2 is `TTO` (days). The script drops non-positive or non-numeric values.
- **Output**: `figure5_tto_distribution.png` (RGB, 300 dpi), `figure5_tto_distribution.tif` (300 dpi)
- **Details**:
  - Left panel: Weibull PDF estimated by MLE (k, lambda) plotted against days, with a horizontal histogram (bin width 5 days) on a twin X-axis.
  - Right panel: boxplot with a *bootstrap percentile 95% CI* diamond for the mean (B=10,000; seed=12345).
  - Y-axis range is 0–730 days by default; adjust in the script config if needed.

## Figure 6 — Kaplan–Meier style cumulative curve (raw)
- **Code**: `raw_code/plots/kaplan_meier_raw.py`
- **Input**: table with `DB`, `prod_ai` (drug), `TTO` (days). Auto-fallback to first 3 columns if headers differ.
- **Output**: `figure6_km_raw.png` (180 mm × 120 mm, 300 dpi, RGB)
- **Curves**: JADER/FAERS × MIRABEGRON/SOLIFENACIN (MIRABEGRON uses dash-dot line style)

---

## Scenario overlays (applies to Figures 2, 3, 4, 5, and 6)
- **Scenario 2 (PS-only)**  
  Upstream PLIDs are replaced with suspects-only versions before counts/metrics:  
  `J_PLID_PS`, `F_PLID_PS` (see MSIP node specs `msip/jader/j50_ps_only.md`, `msip/faers/f50_ps_only.md`).
- **Scenario 3 (AF-excluded)**  
  Upstream PLIDs are replaced with AF-excluded versions:  
  `J_PLID_AF_EXCL`, `F_PLID_AF_EXCL` (see specs `msip/jader/j60_af_exclude_plid.md`, `msip/faers/f60_af_exclude_plid.md`; Python `raw_code/analysis/05a_jader_af_exclude_plid.py`, `raw_code/analysis/05b_faers_af_exclude_plid.py`). Downstream code and figure mapping are unchanged.


---
## CSV version (summary)

- See `FIGURE_TABLE_MAP.csv` for a machine-readable mapping used by CI/checkers.
