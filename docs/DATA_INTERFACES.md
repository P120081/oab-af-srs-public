# Data Interfaces (Logical Names)

This document defines canonical *logical* table names used across the repo.  
They are **not** tied to any specific tool. MSIP nodes, raw Python, or exported CSVs should map to these names for clarity.

## Tokens and conventions
- Case IDs: `j_id` (JADER), `primaryid` (FAERS)
- OAB token (ASCII lowercase): one of  
  `oxybutynin, propiverine, solifenacin, imidafenacin, tolterodine, fesoterodine, mirabegron, vibegron`
- Polypharmacy flag: `<5` vs `>=5`
- AF term: MedDRA PT "Atrial fibrillation" (JADER term = 心房細動)

## JADER logical tables
- **J_PLID**(`j_id`, `sex`, `age`, `drug_count`, …)  
  Patient-level dataset produced by raw Python (already includes drug_count).
- **J_OAB_STD**(`j_id`, `drug_of_interest`)  
  OAB generic name normalization to ASCII tokens (from `raw_code/jader/01_oab_standardize.py`).
- **J_AF**(`j_id`)  
  AF cases selected in MSIP REAC node (`有害事象` == 心房細動).
- **J_STRATA_BASE**(`j_id`, `sex`, `ageband`, `poly5`)  
  Derived from J_PLID: `ageband` 20–69 / 70–99; `poly5` from `drug_count`.
- **J_TTO_CANDIDATES**(`j_id`, `drug_of_interest`, `start_date`, `event_date`)  
  Minimal pair columns for TTO; earliest pair selection happens downstream in Python.
- **J_COUNTS2x2**(`drug_of_interest`, `sex?`, `ageband?`, `poly5?`, `n11`, `n12`, `n21`, `n22`, `N`)  
  2×2 counts (strata columns optional / nullable).

## FAERS logical tables
- **F_PLID**(`primaryid`, `sex`, `age`, `event_dt`, `number_of_drug`, …)  
  DEMO dedup by max caseversion; raw Python attaches `number_of_drug`.
- **F_OAB_STD**(`primaryid`, `drug_of_interest`)  
  OAB normalization from `prod_ai` or prefilled column (ASCII lowercase).
- **F_AF**(`primaryid`)  
  AF cases: MSIP row filter `pt == "Atrial fibrillation"`.
- **F_STRATA_BASE**(`primaryid`, `sex`, `ageband`, `poly5`)  
  Derived from F_PLID.
- **F_TTO_CANDIDATES**(`primaryid`, `drug_of_interest`, `start_dt`, `event_dt`)
- **F_COUNTS2x2**(`drug_of_interest`, `sex?`, `ageband?`, `poly5?`, `n11`, `n12`, `n21`, `n22`, `N`)

## Filenames when exporting to CSV (suggested)
If you export intermediate tables for analysis:
