# FAERS — AF-excluded PLID (INDI.indi_pt != "Atrial fibrillation")

**Purpose**: Remove PLIDs that have AF as indication/history.  
**Input**: F_PLID, INDI(indi_pt)  
**Operation (MSIP)**: Collect primaryid where indi_pt = "Atrial fibrillation" and exclude them from PLID.  
**Output (logical)**: F_PLID_NO_AF(primaryid, …)  
**Downstream**: Use in Scenario 3 (AF-excluded) pipelines

## Pseudo-SQL
```sql
WITH AF_INDICATED AS (
  SELECT DISTINCT primaryid
  FROM INDI
  WHERE indi_pt = 'Atrial fibrillation'
)
SELECT p.*
FROM F_PLID p
LEFT JOIN AF_INDICATED x USING (primaryid)
WHERE x.primaryid IS NULL;

```
