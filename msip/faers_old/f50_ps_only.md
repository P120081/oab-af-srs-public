# FAERS — PS-only PLID (Scenario 2)
**Purpose**: Restrict PLID to Primary Suspect only (`role_code = 'PS'`).  
**Input**: `F_PLID`, `DRUG(role_code)`.  
**Operation (MSIP)**: Select `primaryid` where `role_code = 'PS'`; subset PLID.  
**Output (logical)**: `F_PLID_PS(primaryid, ...)`  
**Downstream**: Use in Scenario 2 (PS-only) pipelines.

## Pseudo-SQL
```sql
WITH ps_ids AS (
  SELECT DISTINCT primaryid
  FROM DRUG
  WHERE role_code = 'PS'
)
SELECT p.*
FROM F_PLID p
JOIN ps_ids x ON x.primaryid = p.primaryid;
```
