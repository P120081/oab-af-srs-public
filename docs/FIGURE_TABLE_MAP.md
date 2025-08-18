# Figure/Table mapping

This file maps public figures/tables in the manuscript to the exact code and inputs used in this repository.

## Figure 3 (…title…)
- Input: `data/derived/jader_metrics.csv`, `data/derived/faers_metrics.csv`
- Code: `raw_code/analysis/01_disproportionality.py` (metrics generation)
- Notes: Rows with `n11 < 3` are excluded before pasting to Excel.

## Figure 4 (Volcano plot: {drug})
- Input CSV schema:  
  `DB, drug_of_interest, Subgroup, n11, n12, n21, n22, ROR, p, PRR, PRR025, PRR975, chi2, IC, IC025, IC975`
- Code: `raw_code/plots/volcano_plot.py`
- Optional: legend only → `raw_code/plots/volcano_legend.py`

## Table X (…)
- Input: …
- Code: …
- Notes: …

## Data sources / interfaces
- Logical table names are defined in `docs/DATA_INTERFACES.md`.
