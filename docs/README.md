# docs/ — Generated figures

These images are generated from `data/derived/` using the scripts in `raw_code/plots/`. They serve as verified examples to compare against when reproducing the analysis.

## Contents (expected)

- `figure2_forest_plot.png` (+ `.tif`) — Forest plot (Fig.2)
- `figure3_forest_plot.png` — Stratified forest plot (Fig.3)
- `volcano_mirabegron.png` (+ `.tif`) — Volcano plot, MIRABEGRON
- `volcano_solifenacin.png` (+ `.tif`) — Volcano plot, SOLIFENACIN
- `figure5_tto_FAERS_mirabegron.png` (+ `.tif`) — TTO distribution (FAERS, 2-year view)
- `figure5_tto_JADER_solifenacin.png` (+ `.tif`) — TTO distribution (JADER, 2-year view)
- `figure6_km_raw.png` — Kaplan–Meier curve

> If `.tif` files make the repository large, track them with **Git LFS** or attach them to a GitHub Release/Zenodo and keep only PNG here.

## Regenerate

From repository root:

```bash
python raw_code/analysis/make_figures.py
```

Or individually (examples):

```bash
python raw_code/plots/forest_plot.py --table data/derived/figure2_source.csv   --out docs/figure2_forest_plot.png --tif docs/figure2_forest_plot.tif

python raw_code/plots/forest_plot_multidrug.py --table data/derived/figure3_stratified.csv   --out docs/figure3_forest_plot.png

python raw_code/plots/volcano_plot.py --table data/derived/volcano_mirabegron.csv   --out docs/volcano_mirabegron.png --tif docs/volcano_mirabegron.tif --title MIRABEGRON

python raw_code/plots/volcano_plot.py --table data/derived/volcano_solifenacin.csv   --out docs/volcano_solifenacin.png --tif docs/volcano_solifenacin.tif --title SOLIFENACIN

python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_FAERS_mirabegron.csv   --out docs/figure5_tto_FAERS_mirabegron.png --tif docs/figure5_tto_FAERS_mirabegron.tif --ymax 730

python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_JADER_solifenacin.csv   --out docs/figure5_tto_JADER_solifenacin.png --tif docs/figure5_tto_JADER_solifenacin.tif --ymax 730

python raw_code/plots/kaplan_meier_raw.py --table data/derived/figure6_km_source.csv   --out docs/figure6_km_raw.png
```