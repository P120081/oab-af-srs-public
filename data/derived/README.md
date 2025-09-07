# data/derived — Public *derived* inputs (final)

This folder contains **small, public, derived CSVs** used to regenerate the manuscript figures.
**No raw case‑level JADER/FAERS data** are stored here.

> This README supersedes the earlier “Suggested layout” and documents the **actual files** included for peer review.

## Current contents
```
data/
└─ derived/
   ├─ figure2_source.csv
   ├─ figure3_stratified.csv
   ├─ figure6_km_source.csv
   ├─ tto_FAERS_mirabegron.csv
   ├─ tto_JADER_solifenacin.csv
   ├─ volcano_mirabegron.csv
   └─ volcano_solifenacin.csv
```

## What each file is for
- **figure2_source.csv** — Source table for **Fig.2** (single‑drug forest).
- **figure3_stratified.csv** — Source table for **Fig.3** (multi‑drug / stratified forest).
- **volcano_mirabegron.csv**, **volcano_solifenacin.csv** — Per‑drug inputs for **Fig.4** (volcano).
- **tto_FAERS_mirabegron.csv**, **tto_JADER_solifenacin.csv** — TTO inputs for **Fig.5** (histogram + Weibull PDF + boxplot).
- **figure6_km_source.csv** — Combined input for **Fig.6** (KM, raw CDF by DB × drug).

## Quick commands (reproduction)
```bash
# Fig.2
python raw_code/plots/forest_plot.py   --table data/derived/figure2_source.csv   --out   docs/figure2_forest_plot.png   --tif   docs/figure2_forest_plot.tif

# Fig.3
python raw_code/plots/forest_plot_multidrug.py   --table data/derived/figure3_stratified.csv   --out   docs/figure3_forest_plot.png

# Fig.4 (two drugs)
python raw_code/plots/volcano_plot.py   --table data/derived/volcano_mirabegron.csv   --out   docs/volcano_mirabegron.png   --tif   docs/volcano_mirabegron.tif   --title MIRABEGRON

python raw_code/plots/volcano_plot.py   --table data/derived/volcano_solifenacin.csv   --out   docs/volcano_solifenacin.png   --tif   docs/volcano_solifenacin.tif   --title SOLIFENACIN

# Fig.5 (y-axis 0–730 days to match the paper)
python raw_code/plots/figure5_tto_distribution.py   --table data/derived/tto_FAERS_mirabegron.csv   --out   docs/figure5_tto_FAERS_mirabegron.png   --tif   docs/figure5_tto_FAERS_mirabegron.tif   --ymax 730

python raw_code/plots/figure5_tto_distribution.py   --table data/derived/tto_JADER_solifenacin.csv   --out   docs/figure5_tto_JADER_solifenacin.png   --tif   docs/figure5_tto_JADER_solifenacin.tif   --ymax 730

# Fig.6
python raw_code/plots/kaplan_meier_raw.py   --table data/derived/figure6_km_source.csv   --out   docs/figure6_km_raw.png
```

## Column conventions (public CSV)
- Use **ASCII headers**. Plotting scripts normalize common variants automatically:  
  - `p`, `p_value` → `p-value` (for forest/volcano)  
  - `chi2`, `χ²` → `χ^2`  
  - Subgroup labels: `≥` is normalized to `>=` internally.
- See **`docs/DATA_INTERFACES.md`** for canonical schemas and example rows.

## Policy reminder
- Do **not** place raw distributions here. Only **aggregated/derived** material required for figure reproduction belongs in this folder.
- Large images (`.tif`) should be handled via **GitHub Releases or Git LFS** if repository size becomes a concern.

_Last updated: 2025-09-07._
