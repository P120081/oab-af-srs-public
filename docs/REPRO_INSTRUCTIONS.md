# Reproduction Instructions (Final)

This is the authoritative, step-by-step guide to regenerate every artifact.

## 0) Environment
```powershell
pip install -r requirements.txt
# or: conda env create -f environment.yml && conda activate oab-af-srs-public
```

## 1) Prepare inputs (data/derived)
See `DATA_INTERFACES.md` for required columns. Ensure ASCII headers for public files when possible.

## 2) One-shot build
```powershell
python raw_code/analysis/make_figures.py --prep
# dry-run only:
python raw_code/analysis/make_figures.py --prep --dry-run
```

## 3) Individual scripts

### Fig.2
```powershell
python raw_code/plots/forest_plot.py --table data/derived/figure2_source.csv `
  --out docs/figure2_forest_plot.png --tif docs/figure2_forest_plot.tif
```

### Fig.3
```powershell
python raw_code/plots/forest_plot_multidrug.py --table data/derived/figure3_stratified.csv `
  --out docs/figure3_forest_plot.png
```

### Fig.4 (Volcano)
```powershell
python raw_code/plots/volcano_plot.py --table data/derived/volcano_mirabegron.csv `
  --out docs/volcano_mirabegron.png --tif docs/volcano_mirabegron.tif --title MIRABEGRON

python raw_code/plots/volcano_plot.py --table data/derived/volcano_solifenacin.csv `
  --out docs/volcano_solifenacin.png --tif docs/volcano_solifenacin.tif --title SOLIFENACIN
```

### Fig.5 (TTO, y=0–730)
```powershell
python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_FAERS_mirabegron.csv `
  --out docs/figure5_tto_FAERS_mirabegron.png --tif docs/figure5_tto_FAERS_mirabegron.tif

python raw_code/plots/figure5_tto_distribution.py --table data/derived/tto_JADER_solifenacin.csv `
  --out docs/figure5_tto_JADER_solifenacin.png --tif docs/figure5_tto_JADER_solifenacin.tif
```

### Fig.6 (KM, raw)
```powershell
python raw_code/plots/kaplan_meier_raw.py --table data/derived/figure6_km_source.csv `
  --out docs/figure6_km_raw.png
```

## 4) Upstream (MSIP) companion nodes
- **JADER**
  - DEMO numericization + BMI: `raw_code/jader/00_demo_numeric_bmi.py`
  - DRUG add count (服薬数): `raw_code/jader/02_drug_attach_count.py`
  - Merge: DEMO (anchor) ← DRUG ← HIST on `識別番号`

- **FAERS**
  - DEMO deduplicate (latest caseversion): `raw_code/faers/00_demo_dedup.py`
  - DRUG add count: `raw_code/faers/02_drug_attach_count.py`
  - Merge: DEMO (anchor) ← DRUG ← OUTC ← INDI on `primaryid`

## 5) Publishing notes
- Keep generated figures under `docs/` (OK to include in the repo).  
- If file sizes are large, prefer GitHub Releases or Git LFS for `.tif`.  
- Ensure `DATA_INTERFACES.md` and this file travel with the release tag.
