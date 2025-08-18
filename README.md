# OAB-AF SRS public code (MSIP + Python)

This repository contains MSIP node specs (pseudo-SQL) and Python scripts used to reproduce figures/tables in the manuscript:
"Atrial Fibrillation signals with Overactive Bladder drugs across JADER and FAERS".

> Code availability: this repo.  
> Data availability: 2x2 counts and minimal derived time-to-onset (TTO) samples sufficient to reproduce all statistics and plots. Raw FAERS/JADER data are NOT redistributed here.

## Repo structure
```
.
├── README.md
├── LICENSE
├── CITATION.cff
├── .gitignore
├── environment.yml        # or requirements.txt
├── data/
│   ├── counts_2x2/        # CSV/TSV for figures 2-3
│   └── tto_samples/       # CSV/TSV for figures 5-6 (derived, minimal)
├── msip/
│   ├── node_006_counts_to_metrics/
│   │   ├── README.md
│   │   └── pseudo.sql
│   ├── node_014_km_raw/
│   │   ├── README.md
│   │   └── pseudo.sql
│   └── node_015_km_bootstrap/
│       ├── README.md
│       └── pseudo.sql
├── python/
│   ├── 00_setup_checks.py
│   ├── 01_disproportionality.py
│   ├── 02_volcano_plots.py
│   ├── 03_tto_distributions.py
│   └── 04_km_curves.py
└── scripts/
    └── make_all.sh
```

## Figure/script mapping
- Figures 2-3: ROR/PRR/IC
  - MSIP: `msip/node_006_counts_to_metrics/`
  - Python: `python/01_disproportionality.py` (reads `data/counts_2x2/*.csv`)
- Figure 4: Volcano plots
  - Python: `python/02_volcano_plots.py`
- Figure 5: TTO distributions
  - Python: `python/03_tto_distributions.py` (reads `data/tto_samples/*.csv`)
- Figure 6: KM curves (+ bootstrap IQR)
  - MSIP: `msip/node_014_km_raw/`, `msip/node_015_km_bootstrap/`
  - Python: `python/04_km_curves.py`

## Environment
- Python >= 3.13
- Create environment:
  - conda: `conda env create -f environment.yml`
  - pip:   `pip install -r requirements.txt`

## Data policy
- Publish only aggregate 2x2 counts and minimal derived TTO samples required for full reproducibility.
- DO NOT include raw FAERS/JADER files.
- File/dir names: ASCII only.

## Quick start
```bash
python python/01_disproportionality.py
python python/02_volcano_plots.py
python python/03_tto_distributions.py
python python/04_km_curves.py
```

## How to cite
See `CITATION.cff`. After journal acceptance, update with the article DOI and full citation.
