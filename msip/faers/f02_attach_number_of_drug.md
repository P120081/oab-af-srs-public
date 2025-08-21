# FAERS — Attach number_of_drug

**Purpose**: Count drugs per primaryid and attach as number_of_drug.  
**Input**: F_PLID, DRUG  
**Operation (MSIP)**: GROUP BY primaryid in DRUG; LEFT JOIN counts back to F_PLID.  
**Output (logical)**: F_PLID(+ number_of_drug)  
**Downstream**: f30_strata_base.md

## Pseudo-SQL
```sql
WITH drug_counts AS (
  SELECT primaryid, COUNT(*) AS number_of_drug
  FROM DRUG
  GROUP BY primaryid
)
SELECT p.*, COALESCE(c.number_of_drug,0) AS number_of_drug
FROM F_PLID p
LEFT JOIN drug_counts c USING (primaryid);

```
