# FAERS — OAB normalization
**Purpose**: Normalize OAB generic names to ASCII tokens (`drug_of_interest`).  
**Input**: `DRUG(prod_ai)` and the mapping in `raw_code/faers/01_oab_standardize.py`.  
**Operation (MSIP)**: Lower/trim and map to tokens: oxybutynin, propiverine, solifenacin, imidafenacin, tolterodine, fesoterodine, mirabegron, vibegron.  
**Output (logical)**: `F_OAB_STD(primaryid, drug_of_interest)`  
**Downstream**: `f20_counts2x2.md`, `f40_plid_timeseries.md`

## Notes
- Keep distinct pairs per `primaryid` and `drug_of_interest`.

## Pseudo-SQL
```sql
SELECT DISTINCT
  d.primaryid,
  MAP_TO_OAB_TOKEN(LOWER(TRIM(d.prod_ai))) AS drug_of_interest
FROM DRUG d
WHERE MAP_TO_OAB_TOKEN(LOWER(TRIM(d.prod_ai))) IS NOT NULL;
```
