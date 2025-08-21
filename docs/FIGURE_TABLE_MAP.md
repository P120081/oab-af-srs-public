# Figure / Table Map (Public Repro)

This document links **manuscript figures** to their **input files** and **rendering scripts** in this repository. Every figure can be regenerated from `data/derived/*` (no case‑level FAERS/JADER data required).

> Shell examples are given for **Windows PowerShell** (use backtick `` ` `` for line wrapping). On macOS/Linux, replace backticks with backslashes `\` or new lines.

---

## Fig. 2 — Forest plot (single drug per DB)

- **Script**: `raw_code/plots/forest_plot.py`
- **Input**: `data/derived/figure2_source.csv`
- **Output**: `docs/figure2_forest_plot.png` (+ `figure2_forest_plot.tif`)

**Run**:
```powershell
python raw_code/plots/forest_plot.py `
  --table data/derived/figure2_source.csv `
  --out   docs/figure2_forest_plot.png `
  --tif   docs/figure2_forest_plot.tif
```

**Required columns (flexible aliases supported)**:  
`DB`, `drug_of_interest`, `n11`, `ROR`, `ROR025`, `ROR975`, `p-value` (or `p`/`p_value`), optional `PRR025`, `χ^2` (or `chi2`/`x2`), `IC025`.

---

## Fig. 3 — Stratified forest plot (multi-drug)

- **Script**: `raw_code/plots/forest_plot_multidrug.py`
- **Input**: `data/derived/figure3_stratified.csv`
- **Output**: `docs/figure3_forest_plot.png`

**Run**:
```powershell
python raw_code/plots/forest_plot_multidrug.py `
  --table data/derived/figure3_stratified.csv `
  --out   docs/figure3_forest_plot.png
```

**Required columns**:  
`DB`, `drug_of_interest`, `Subgroup`, `n11`, `ROR`, `ROR025`, `ROR975`, `p-value` (aliases above), optional `PRR025`, `χ^2`, `IC025`.

---

## Fig. 4 — Volcano plots (per drug)

- **Script**: `raw_code/plots/volcano_plot.py`
- **Inputs**:  
  - MIRABEGRON: `data/derived/volcano_mirabegron.csv`  
  - SOLIFENACIN: `data/derived/volcano_solifenacin.csv`
- **Outputs**:  
  - `docs/volcano_mirabegron.png` (+ `.tif`)  
  - `docs/volcano_solifenacin.png` (+ `.tif`)

**Run**:
```powershell
# MIRABEGRON
python raw_code/plots/volcano_plot.py `
  --table data/derived/volcano_mirabegron.csv `
  --out   docs/volcano_mirabegron.png `
  --tif   docs/volcano_mirabegron.tif `
  --title MIRABEGRON

# SOLIFENACIN
python raw_code/plots/volcano_plot.py `
  --table data/derived/volcano_solifenacin.csv `
  --out   docs/volcano_solifenacin.png `
  --tif   docs/volcano_solifenacin.tif `
  --title SOLIFENACIN
```

**Required columns**:  
`DB`, `Subgroup`, `n11`, `ROR`, `p-value` (aliases allowed). Extremely small P values may be given in **scientific notation** (e.g., `5.54E-18`); the script parses and converts them before computing `-log10(p)`.

---

## Fig. 5 — Time-to-onset (TTO) distribution

- **Script**: `raw_code/plots/figure5_tto_distribution.py`
- **Inputs**:  
  - FAERS / MIRABEGRON: `data/derived/tto_FAERS_mirabegron.csv`  
  - JADER / SOLIFENACIN: `data/derived/tto_JADER_solifenacin.csv`
- **Outputs**:  
  - `docs/figure5_tto_FAERS_mirabegron.png` (+ `.tif`)  
  - `docs/figure5_tto_JADER_solifenacin.png` (+ `.tif`)

**Run (2‑year axis, 730 days)**:
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

**Required input**: single column of positive TTO values in **days** (script auto-detects the 3rd column if unnamed). Optional flags: `--binwidth`, `--hist-max`.

---

## Fig. 6 — Kaplan–Meier style cumulative curve

- **Script**: `raw_code/plots/kaplan_meier_raw.py`
- **Input**: `data/derived/figure6_km_source.csv`
- **Output**: `docs/figure6_km_raw.png`

**Run**:
```powershell
python raw_code/plots/kaplan_meier_raw.py `
  --table data/derived/figure6_km_source.csv `
  --out   docs/figure6_km_raw.png
```

**Required columns (case‑insensitive, flexible)**:  
`db` (JADER/FAERS or 1/2), `prod_ai`/`drug`/`product` (generic name: MIRABEGRON/SOLIFENACIN), and `tto`/`days`/`time`/`time_to_onset` (numeric).

---

### Supplementary mapping (for reference)

- **S1**: Methods — signal metrics & formulas.  
- **S2**: Source data for Fig. 2 (→ `figure2_source.csv`).  
- **S3**: Source data for Fig. 3 (→ `figure3_stratified.csv`).  
- **S4**: Sensitivity & negative‑control results.  
- **S5**: KM curve without the 2‑year restriction.