# JADER — Attach drug_count

**Purpose**: Count drugs per j_id and attach as drug_count.  
**Input**: J_PLID, DRUG_J  
**Operation (MSIP)**: GROUP BY j_id in DRUG_J; LEFT JOIN counts back to J_PLID.  
**Output (logical)**: J_PLID(+ drug_count)  
**Downstream**: j30_strata_base.md

## Pseudo-SQL
```sql
WITH drug_counts AS (
  SELECT j_id, COUNT(*) AS drug_count
  FROM DRUG_J
  GROUP BY j_id
)
SELECT p.*, COALESCE(c.drug_count,0) AS drug_count
FROM J_PLID p
LEFT JOIN drug_counts c USING (j_id);

```
