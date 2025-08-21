# OAB–AF SRS: Public Reproducibility Package

This repository contains all materials to **reproduce** the analyses and figures in our manuscript submitted to *Frontiers in Pharmacology*.  
It is designed for **fast review** and **clear traceability** from raw(ish) inputs → derived CSVs → plots.

## Quickstart

> Python ≥ 3.11 is recommended (works with 3.13 as well). Use Conda if you prefer an isolated env.

```bash
# (A) Using pip (minimal)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: standardize OAB names (FAERS/JADER) if you have DRUG tables available
python raw_code/analysis/prep_standardize.py \\
  --faers-in data/faers_DRUG.csv --faers-out data/derived/faers_oab_standardized.csv \\
  --jader-in data/jader_DRUG.csv --jader-out data/derived/jader_oab_standardized.csv

# Rebuild all public figures (Fig.2–6)
python raw_code/analysis/make_figures.py --prep
```

**Outputs** are written to `docs/` by default, with one file per figure.

- Fig.2 → `docs/figure2_forest_plot.(png|tif)`  
- Fig.3 → `docs/figure3_forest_plot.png`  
- Fig.4 → `docs/volcano_<drug>.png`  
- Fig.5 → `docs/figure5_tto_<DB>_<drug>.png`  
- Fig.6 → `docs/figure6_km_raw.png`

> Windows note: we set a sans-serif fallback (DejaVu Sans → Arial/Segoe) to ensure the ✓ glyph renders correctly.

## Data interfaces & mapping

- **How to reproduce (step-by-step)**: see `docs/REPRO_INSTRUCTIONS.md`  
- **Figure ⇄ Table ⇄ Script map**: see `docs/FIGURE_TABLE_MAP.md`

All public CSVs use **ASCII-only headers** (e.g., `chi2`, `p_value`). Rows with **`n11 < 3`** are excluded before metrics/plots.  
Supplementary items: S1–S5 as described in the manuscript and `docs/`.

## Environment options

- **pip**: `requirements.txt` (minimal, upper-bounds-free)  
- **conda**: `environment.yml` (pins Python + adds system libs for SciPy/Matplotlib)

## Citation

Please cite the manuscript once the DOI is available. A machine-readable `CITATION.cff` is included at the repository root.

---
*Last updated: 2025-08-21.*
