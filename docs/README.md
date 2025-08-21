# Documentation

This folder contains everything needed to **reproduce** the public figures and to understand the **data interfaces** used across the project. It is written to be skimmed quickly by reviewers.

## What’s inside
- **FIGURE_TABLE_MAP.csv** — canonical mapping between each Figure/Table and the **exact** script, inputs, and outputs.
- **REPRO_INSTRUCTIONS.md** — step-by-step instructions (MSIP + Python) to regenerate figures.
- **DATA_INTERFACES.md** — canonical logical schemas and naming conventions (ASCII-only public columns).

## Quickstart (90 seconds)
```bash
# create environment
pip install -r requirements.txt    # or: conda env create -f environment.yml && conda activate oab-af-srs

# reproduce Figure 2 (forest) from a prepared CSV
python raw_code/plots/forest_plot.py --table data/derived/figure2_source.csv --out docs/figure2_forest_plot.png

# reproduce Figure 6 (raw KM)
python raw_code/plots/kaplan_meier_raw.py --table data/derived/figure6_km_source.csv --out docs/figure6_km_raw.png
```

## Conventions
- **ASCII-only column names** in public artifacts (e.g., `chi2`, `p_value`). Internally you may keep native encodings; normalize on export.
- **DB** ∈ {JADER, FAERS}. **OAB tokens**: oxybutynin, propiverine, solifenacin, imidafenacin, tolterodine, fesoterodine, mirabegron, vibegron.
- **Stability rule**: drop rows with `n11 < 3` prior to metrics/plots.
- **No ad-hoc truncation**: the supplementary KM (S5) uses the full window; main-text KM may show ≤2 years for readability.

(Generated 2025-08-21.)
