# Data Interfaces (Logical Names)

This document defines canonical **logical** table names used across the repo.
They are not tied to any specific tool. MSIP nodes, raw Python, or exported CSVs
should map to these names for clarity and reproducibility.

---

## Tokens and conventions

- **Case IDs**: `j_id` (JADER), `primaryid` (FAERS)
- **DB code**: `DB ∈ {JADER, FAERS}` (used in figures)
- **OAB token (ASCII, lowercase)**: one of  
  `oxybutynin, propiverine, solifenacin, imidafenacin, tolterodine, fesoterodine, mirabegron, vibegron`
- **Polypharmacy flag**: `poly5 ∈ {"<5", ">=5"}`
- **Age band**: `ageband ∈ {"20-69", "70-99"}`
- **Sex**: `sex ∈ {"M", "F"}`
- **AF term**:
  - FAERS (MedDRA PT): `"Atrial fibrillation"`
  - JADER (日本語): `心房細動`  *(string literal in source data)*

> Logical column names use ASCII (e.g., `chi2` instead of `χ^2`). When importing
> tool-specific outputs, normalize to these logical names before sharing.

---

## JADER logical tables

- **J_PLID**  
  Schema: `j_id, sex, age, drug_count, ...`  
  Notes: patient-level dataset (raw Python attaches `drug_count`).

- **J_OAB_STD**  
  Schema: `j_id, drug_of_interest`  
  Notes: OAB generic-name normalization to ASCII token (see `raw_code/jader/01_oab_standardize.py`).

- **J_AF**  
  Schema: `j_id`  
  Selector: MSIP REAC row filter `有害事象 == "心房細動"`.

- **J_STRATA_BASE**  
  Schema: `j_id, sex, ageband, poly5`  
  Derivations: `ageband` from `age` (20–69 → `"20-69"`, 70–99 → `"70-99"`), `poly5` from `drug_count` (`"<5"`/`">=5"`).

- **J_TTO_CANDIDATES**  
  Schema: `j_id, drug_of_interest, start_date, event_date`  
  Notes: minimal pairs; earliest-pair selection downstream in Python.

- **J_COUNTS2x2**  
  Schema: `drug_of_interest, sex?, ageband?, poly5?, n11, n12, n21, n22, N`  
  Notes: optional strata columns may be null if not stratified.

---

## FAERS logical tables

- **F_PLID**  
  Schema: `primaryid, sex, age, event_dt, number_of_drug, ...`  
  Notes: DEMO dedup by max `caseversion`; raw Python attaches `number_of_drug`.

- **F_OAB_STD**  
  Schema: `primaryid, drug_of_interest`  
  Notes: OAB normalization from `prod_ai` (ASCII lowercase tokens).

- **F_AF**  
  Schema: `primaryid`  
  Selector: MSIP row filter `pt == "Atrial fibrillation"`.

- **F_STRATA_BASE**  
  Schema: `primaryid, sex, ageband, poly5`

- **F_TTO_CANDIDATES**  
  Schema: `primaryid, drug_of_interest, start_dt, event_dt`

- **F_COUNTS2x2**  
  Schema: `drug_of_interest, sex?, ageband?, poly5?, n11, n12, n21, n22, N`

---

## CSV filenames (suggested)

```
data/derived/jader_plid.csv
data/derived/j_oab_std.csv
data/derived/j_af.csv
data/derived/j_counts2x2.csv
data/derived/j_tto_candidates.csv

data/derived/faers_plid.csv
data/derived/f_oab_std.csv
data/derived/f_af.csv
data/derived/f_counts2x2.csv
data/derived/f_tto_candidates.csv
```

---

## Compatibility notes

- Prefer ASCII logical names in public outputs (e.g., `chi2`); retain original
  non-ASCII column names only in tool-specific intermediate nodes if necessary.
- Figures expect:
  - **Figure 2** minimum columns: `DB, drug_of_interest, n11, ROR, ROR025, ROR975`  
    *(optional)* `p` or `p-value`, `PRR025`, `chi2`/`χ^2`, `IC025`
  - **Figure 4** per-drug CSV:  
    `DB, drug_of_interest, Subgroup, n11, n12, n21, n22, ROR, p, PRR, PRR025, PRR975, chi2, IC, IC025, IC975`  
    with `Subgroup` normalized to ASCII tokens (e.g., "Drugs>=5").
