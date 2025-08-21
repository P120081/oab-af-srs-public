# FAERS — AF-excluded PLID (Scenario 3)
**Purpose**: Exclude PLIDs with indication/history of AF.  
**Input**: `F_PLID`, `INDI(indi_pt)`.  
**Operation (MSIP)**: Collect `primaryid` where `indi_pt = 'Atrial fibrillation'`; subtract from PLID.  
**Output (logical)**: `F_PLID_NO_AF(primaryid, ...)`  
**Downstream**: Use in Scenario 3 (AF-excluded) pipelines.

## Pseudo-SQL
```sql
WITH af_ids AS (
  SELECT DISTINCT primaryid
  FROM INDI
  WHERE indi_pt = 'Atrial fibrillation'
)
SELECT p.*
FROM F_PLID p
LEFT JOIN af_ids a ON a.primaryid = p.primaryid
WHERE a.primaryid IS NULL;
```
