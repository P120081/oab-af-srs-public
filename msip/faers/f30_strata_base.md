# FAERS — Strata base: sex/ageband/poly5 (F_STRATA_BASE)

_Last updated: 2025-08-21_

# FAERS — Strata base (sex, ageband, poly5)

**Purpose**: Derive stratification fields from PLID + number_of_drug.  
**Input**: F_PLID(+ number_of_drug)  
**Operation (MSIP)**: Compute ageband (20–69 / 70–99) from integer age; poly5 from number_of_drug (<5 vs >=5).  
**Output (logical)**: F_STRATA_BASE(primaryid, sex, ageband, poly5)  
**Downstream**: Stratified counts/analyses

## Pseudo-SQL
```sql
SELECT primaryid,
       sex,
       CASE WHEN age BETWEEN 20 AND 69 THEN '20-69'
            WHEN age BETWEEN 70 AND 99 THEN '70-99'
            ELSE NULL END AS ageband,
       CASE WHEN number_of_drug >= 5 THEN '>=5' ELSE '<5' END AS poly5
FROM F_PLID;

```

---
## QA checklist
- [ ] Column names are ASCII-only (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `primaryid` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** F_STRATA_BASE(primaryid, sex, ageband, poly5)
**Public export(s):** data/derived/figure3_stratified.csv (after join)

