# oab-af-srs-public

Reproducible code and derived data to accompany the manuscript submitted to *Frontiers in Pharmacology* on signals of atrial fibrillation (AF) associated with overactive bladder (OAB) drugs using FAERS and JADER.

This repository contains the **public** analysis pipeline and the **minimal derived inputs** required to regenerate the figures/tables reported in the paper (no case-level FAERS/JADER data are redistributed).

---

## What’s here

```
data/
  derived/                  # Minimal inputs to reproduce all plots (CSV)
docs/                       # Generated figures (PNG/TIFF)
msip/                       # Step-by-step pipeline notes for FAERS/JADER (documentation)
raw_code/
  analysis/                 # End-to-end helpers and orchestration
  plots/                    # Standalone figure scripts (CLI/MSIP compatible)
```

Key docs:

- `REPRO_INSTRUCTIONS.md` – end-to-end commands to regenerate all outputs.
- `FIGURE_TABLE_MAP.md` – figure numbers ↔ source files ↔ scripts.
- `DATA_INTERFACES.md` – expected column names & schema for inputs/outputs.
- `docs/README.md` – what’s in `docs/` and how to re-create each image.
- `msip/faers/README.md`, `msip/jader/README.md` – MSIP node notes (merge keys, dedup, feature adds).

---

## Quickstart

### 1) Environment

Using Conda (recommended):

```bash
conda env create -f environment.yml
conda activate oab-af-srs
```

Or pip:

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
.venv\Scriptsctivate.bat

pip install -r requirements.txt
```

> We rely on `numpy`, `pandas`, `matplotlib`, `scipy`, **`joblib`** (bootstrap parallelism), and **`lifelines`** (survival utilities). All figure scripts are pure-Python and have **no hard dependency** on MSIP (MSIP-specific utilities are optional fallbacks).

### 2) Reproduce figures

From repo root:

```bash
# (Optional) discover inputs & standardize (if you have raw FAERS/JADER)
python raw_code/analysis/make_figures.py --prep

# Regenerate all figures from data/derived (no raw data required)
python raw_code/analysis/make_figures.py
```

Or run any script directly, e.g.:

```bash
# Fig.2
python raw_code/plots/forest_plot.py --table data/derived/figure2_source.csv   --out docs/figure2_forest_plot.png --tif docs/figure2_forest_plot.tif

# Fig.3
python raw_code/plots/forest_plot_multidrug.py --table data/derived/figure3_stratified.csv   --out docs/figure3_forest_plot.png --tif docs/figure3_forest_plot.tif

# Volcano (mirabegron / solifenacin)
python raw_code/plots/volcano_plot.py --table data/derived/volcano_mirabegron.csv   --out docs/volcano_mirabegron.png --tif docs/volcano_mirabegron.tif --title MIRABEGRON
python raw_code/plots/volcano_plot.py --table data/derived/volcano_solifenacin.csv   --out docs/volcano_solifenacin.png --tif docs/volcano_solifenacin.tif --title SOLIFENACIN

# Fig.5 (TTO) — 2-year (730 days) view
python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_FAERS_mirabegron.csv   --out docs/figure5_tto_FAERS_mirabegron.png --tif docs/figure5_tto_FAERS_mirabegron.tif --ymax 730
python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_JADER_solifenacin.csv   --out docs/figure5_tto_JADER_solifenacin.png --tif docs/figure5_tto_JADER_solifenacin.tif --ymax 730

# Fig.6 (KM)
python raw_code/plots/kaplan_meier_raw.py --table data/derived/figure6_km_source.csv   --out docs/figure6_km_raw.png
```

**Windows (PowerShell) line continuation** uses backticks (\`):

```powershell
python raw_code/plots/forest_plot.py `
  --table data/derived/figure2_source.csv `
  --out docs/figure2_forest_plot.png `
  --tif docs/figure2_forest_plot.tif
```

> **Tip (CI/smoke):** For Fig.5 you can speed up bootstrap by adding `--B 2000` for a quick check; the manuscript build uses `--B 10000`.

---

## Data availability

- **Derived counts & sources** needed to reproduce all disproportionality results are in `data/derived/` and Supplementary Data S1–S4.
- **FAERS/JADER** case-level data are publicly accessible from their official portals; we do **not** redistribute case-level data here.
- All scripts required to recompute metrics from the 2×2 counts are provided under `raw_code/`.

**Notes for CSV headers**

- Public CSVs favor ASCII headers (`p_value`, `chi2`). Plot scripts are tolerant to `p`, `p-value`, and scientific notation like `5.54E-18` (converted to float then `-log10(p)`).

---

## Supplementary files mapping (final)

- **S1**: Methods — signal metrics & formulas.
- **S2**: Source data for Fig. 2.
- **S3**: Source data for Fig. 3.
- **S4**: Kaplan–Meier curve **without** 2‑year restriction (full horizon).
- **S5**: Sensitivity and negative‑control analyses (Excel‑only).

See `FIGURE_TABLE_MAP.md` for exact filenames and columns.

---

## Version & citation

- Latest tagged release: **v1.0.0** (public peer‑review package).  
- A `CITATION.cff` file is included. After acceptance, consider adding a Zenodo DOI (and list it under `identifiers`).

---

## License

- **Code**: see `LICENSE` (MIT).  
- **Figures/Docs**: unless otherwise noted, © Authors. If you intend to re-use figures, please cite the paper. Optionally apply CC BY 4.0 for figures and docs (add a `LICENSE-media` if desired).

---

## Contact

Maintainers: **Sagara Laboratory** — Division of Medical Safety Science, Faculty of Pharmaceutical Sciences, Sanyo‑Onoda city University  
Contact: **Hidenori Sagara** — hsagara@rs.socu.ac.jp
