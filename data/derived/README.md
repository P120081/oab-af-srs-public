# data/ — Working area for derived CSVs

This folder holds small **derived** CSVs used by the public Python scripts.
Do **NOT** commit any raw JADER/FAERS distributions here.

## Suggested layout

```
data/
└─ derived/
   ├─ jader_plid.csv
   ├─ j_oab_std.csv
   ├─ j_af.csv
   ├─ j_counts2x2.csv
   ├─ j_tto.csv
   ├─ faers_plid.csv
   ├─ f_oab_std.csv
   ├─ f_af.csv
   ├─ f_counts2x2.csv
   ├─ f_tto.csv
   ├─ jader_metrics.csv        # for Figure 3
   └─ faers_metrics.csv        # for Figure 3
```

- Column names should be **ASCII**; see `docs/DATA_INTERFACES.md` for canonical schemas.
- For Figure 3, paste metrics into your Excel template using `jader_metrics.csv` and `faers_metrics.csv`.
- For Figure 6, provide a small CSV with at least `DB`, `prod_ai` (drug), and `TTO` (days) as described in docs.

This directory is kept in Git via a placeholder file `.gitkeep`.
