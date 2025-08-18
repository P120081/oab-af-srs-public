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

## Figure 3 — Forest plot (per drug × DB)
- Input CSV schema: `DB, drug_of_interest, Subgroup, n11, ROR, ROR025, ROR975` (optional: `p`/`p-value`, `PRR025`, `chi2`/`χ^2`, `IC025`)
- Code: `raw_code/plots/forest_plot_multidrug.py`
- Output: `figure3_forest.png`, `figure3_forest.tif`
- Signals: ROR `ROR025>1 & p<0.05`, PRR `PRR025>2 & chi2>4`, IC `IC025>0`


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
