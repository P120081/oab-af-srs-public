# FAERS — OAB normalization (OAB_STD)

**Purpose**: Normalize OAB generic names to ASCII tokens (drug_of_interest).  
**Input**: DRUG (prod_ai), mapping defined in raw_code/faers/01_oab_standardize.py  
**Operation (MSIP)**: Lower/trim prod_ai and map to tokens {oxybutynin,…,vibegron}. DISTINCT per primaryid,drug_of_interest.  
**Output (logical)**: F_OAB_STD(primaryid, drug_of_interest)  
**Downstream**: f20_counts2x2.md, f40_plid_timeseries.md

## Pseudo-SQL
```sql
-- Conceptual: mapping is implemented in Python; here we show the logical result.
SELECT DISTINCT d.primaryid, m.drug_of_interest
FROM DRUG d
JOIN OAB_NAME_MAP m  -- conceptual view produced by Python
  ON LOWER(TRIM(d.prod_ai)) = m.raw_name;

```
