# Figure / Table Map (Final)

This repository ships **inputs → scripts → outputs** mapping and how these relate to the manuscript.

| Figure | Input CSV (data/derived) | Script | Output (docs) | Notes |
|---|---|---|---|---|
| Fig.2 | `figure2_source.csv` | `raw_code/plots/forest_plot.py` | `figure2_forest_plot.png` + `figure2_forest_plot.tif` | uses ROR, PRR, IC; **p and chi2** normalized; per-DB sections with ROR=1 guide line |
| Fig.3 | `figure3_stratified.csv` | `raw_code/plots/forest_plot_multidrug.py` | `figure3_forest_plot.png` | grouped by **drug_of_interest** and DB; **Subgroup** column required |
| Fig.4 | `volcano_mirabegron.csv`, `volcano_solifenacin.csv` | `raw_code/plots/volcano_plot.py` | `volcano_*.png` (and `.tif` if requested) | accepts p in scientific notation; labels shown for **p<0.05** |
| Fig.5 | `tto_FAERS_mirabegron.csv`, `tto_JADER_solifenacin.csv` | `raw_code/plots/figure5_tto_distribution.py` | `figure5_tto_* .png` + `.tif` | y-range **0–730 days**; 3rd col = TTO days; Weibull fit + histogram + boxplot |
| Fig.6 | `figure6_km_source.csv` | `raw_code/plots/kaplan_meier_raw.py` | `figure6_km_raw.png` | raw KM (Excel/CSV source), no censoring imputation by script |

## Column harmonization
- `p-value` / `p_value` / `p` → **p**  
- `χ^2` / `chi2` / `Chi2` → **chi2**  
Scripts auto-normalize, so upstream sources can vary as above.

## Where each CSV comes from
- **`figure2_source.csv`**: counts/metrics by drug × DB (overall).  
- **`figure3_stratified.csv`**: counts/metrics by drug × DB × stratum (sex, age group, polypharmacy).  
- **`volcano_*.csv`**: per-drug stratified slice (the same strata as Fig.3).  
- **`tto_*.csv`**: raw TTO vectors (3rd column).  
- **`figure6_km_source.csv`**: KM-ready tidy table.

Re-generation (one-shot):
```powershell
python raw_code/analysis/make_figures.py --prep
```
Or individual calls as printed by `--dry-run`.
