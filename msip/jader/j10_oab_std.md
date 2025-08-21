# JADER — OAB standardize (OAB_STD)

**Purpose**: Normalize Japanese generic names to ASCII tokens (drug_of_interest).  
**Input**: DRUG_J(一般名), mapping defined in raw_code/jader/01_oab_standardize.py  
**Operation (MSIP)**: Map to tokens {oxybutynin,…,vibegron}. DISTINCT per j_id,drug_of_interest.  
**Output (logical)**: J_OAB_STD(j_id, drug_of_interest)  
**Downstream**: j20_counts2x2.md, j40_plid_timeseries.md

## Pseudo-SQL
```sql
-- Conceptual: mapping is implemented in Python; here we show the logical result.
SELECT DISTINCT d.j_id, m.drug_of_interest
FROM DRUG_J d
JOIN OAB_NAME_MAP_J m  -- conceptual view produced by Python
  ON m.raw_name_jp = d.一般名;

```
