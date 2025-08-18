# Figure / Table mapping

This repository maps every public figure/table to the exact code and inputs used.

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

## Data interfaces
- Canonical logical table names: `docs/DATA_INTERFACES.md`.
