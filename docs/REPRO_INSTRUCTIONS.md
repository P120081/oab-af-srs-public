# Reproduction Instructions (Public)

This is the **one‑page recipe** to rebuild every public figure from this repository.

---

## 0) Environment

Using Conda (recommended):
```bash
conda env create -f environment.yml
conda activate oab-af-srs
```

Using pip + venv:
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

> All scripts are pure‑Python based on `numpy`, `pandas`, `matplotlib`, and `scipy`. **MSIP is not required** (MSIP utilities are gracefully bypassed in CLI mode).

---

## 1) Minimal inputs

Everything needed is under `data/derived/`:
- `figure2_source.csv`
- `figure3_stratified.csv`
- `volcano_mirabegron.csv`, `volcano_solifenacin.csv`
- `tto_FAERS_mirabegron.csv`, `tto_JADER_solifenacin.csv`
- `figure6_km_source.csv`

Column schemas: see `DATA_INTERFACES.md`.

---

## 2) Rebuild all at once

From repo root:
```powershell
# Discover inputs & standardize (optional, for users with raw data)
python raw_code/analysis/make_figures.py --prep

# Generate all figures from data/derived
python raw_code/analysis/make_figures.py
```

Dry‑run (show commands only):
```powershell
python raw_code/analysis/make_figures.py --prep --dry-run
```

---

## 3) Rebuild individually (examples, PowerShell)

**Fig.2**
```powershell
python raw_code/plots/forest_plot.py `
  --table data/derived/figure2_source.csv `
  --out   docs/figure2_forest_plot.png `
  --tif   docs/figure2_forest_plot.tif
```

**Fig.3**
```powershell
python raw_code/plots/forest_plot_multidrug.py `
  --table data/derived/figure3_stratified.csv `
  --out   docs/figure3_forest_plot.png
```

**Fig.4 (Volcano)**
```powershell
python raw_code/plots/volcano_plot.py `
  --table data/derived/volcano_mirabegron.csv `
  --out   docs/volcano_mirabegron.png `
  --tif   docs/volcano_mirabegron.tif `
  --title MIRABEGRON

python raw_code/plots/volcano_plot.py `
  --table data/derived/volcano_solifenacin.csv `
  --out   docs/volcano_solifenacin.png `
  --tif   docs/volcano_solifenacin.tif `
  --title SOLIFENACIN
```

**Fig.5 (TTO, 2‑year axis)**  
```powershell
python raw_code/plots/figure5_tto_distribution.py `
  --table data/derived/tto_FAERS_mirabegron.csv `
  --out   docs/figure5_tto_FAERS_mirabegron.png `
  --tif   docs/figure5_tto_FAERS_mirabegron.tif `
  --ymax  730

python raw_code/plots/figure5_tto_distribution.py `
  --table data/derived/tto_JADER_solifenacin.csv `
  --out   docs/figure5_tto_JADER_solifenacin.png `
  --tif   docs/figure5_tto_JADER_solifenacin.tif `
  --ymax  730
```

**Fig.6**
```powershell
python raw_code/plots/kaplan_meier_raw.py `
  --table data/derived/figure6_km_source.csv `
  --out   docs/figure6_km_raw.png
```

---

## 4) Troubleshooting

- **`ModuleNotFoundError: msi`** – Expected: the public scripts don’t require MSIP. All scripts have a CLI path that bypasses MSIP; use the commands above with `--table`/`--out` flags.
- **Glyph warning for ✓ in Arial** – Harmless. We embed the check mark with a DejaVu fallback when needed.
- **`Axis limits cannot be NaN or Inf` (volcano)** – Caused by zero/invalid p. The script parses scientific notation and drops invalid rows; ensure `p-value` is a valid numeric or numeric string.
- **Plots cut off (volcano labels)** – This figure intentionally uses tight layout. If labels extend beyond, render PNG and adjust in the manuscript layout, or reduce label count in the CSV.
- **TTO y‑axis** – Use `--ymax 730` for 2‑year view; adjust `--hist-max` if histogram counts clip.

---

## 5) License & citation

- **Code**: see `LICENSE` (e.g., MIT).  
- **Figures/Docs**: © Authors. Consider CC BY 4.0 if redistribution is desired.

Cite using the included `CITATION.cff`. After acceptance, add a GitHub Release + Zenodo archive for a DOI.