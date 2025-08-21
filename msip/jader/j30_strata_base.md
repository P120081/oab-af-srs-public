# JADER — Strata base: sex/ageband/poly5 (J_STRATA_BASE)

_Last updated: 2025-08-21_

# JADER — Strata base (sex, ageband, poly5)

**Purpose**: Derive stratification fields from PLID + drug_count.  
**Input**: J_PLID(+ drug_count)  
**Operation (MSIP)**: Compute ageband (20–69 / 70–99) from integer age; poly5 from drug_count (<5 vs >=5).  
**Output (logical)**: J_STRATA_BASE(j_id, sex, ageband, poly5)  
**Downstream**: Stratified analyses

## Pseudo-SQL
```sql
SELECT j_id,
       sex,
       CASE WHEN age BETWEEN 20 AND 69 THEN '20-69'
            WHEN age BETWEEN 70 AND 99 THEN '70-99'
            ELSE NULL END AS ageband,
       CASE WHEN drug_count >= 5 THEN '>=5' ELSE '<5' END AS poly5
FROM J_PLID;

```

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_STRATA_BASE(j_id, sex, ageband, poly5)
**Public export(s):** data/derived/figure3_stratified.csv (after join)

