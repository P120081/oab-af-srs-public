# FAERS — Strata base
**Purpose**: Derive `sex`, `ageband`, and `poly5` from `number_of_drug`.  
**Input**: `F_PLID(+ number_of_drug)`.  
**Operation (MSIP)**: Compute `ageband` (20–69, 70–99) and `poly5` (<5 vs >=5).  
**Output (logical)**: `F_STRATA_BASE(primaryid, sex, ageband, poly5)`  
**Downstream**: Stratified analyses (counts, metrics, figures).

## Pseudo-SQL
```sql
SELECT
  primaryid,
  sex,
  CASE WHEN age BETWEEN 20 AND 69 THEN '20-69'
       WHEN age BETWEEN 70 AND 99 THEN '70-99'
       ELSE NULL END AS ageband,
  CASE WHEN number_of_drug >= 5 THEN '>=5' ELSE '<5' END AS poly5
FROM F_PLID;
```
