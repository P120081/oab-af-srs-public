# FAERS — PS-only PLID (role_code == "PS")

**Purpose**: Restrict PLID to suspected-drug rows only.  
**Input**: F_PLID, DRUG(role_code)  
**Operation (MSIP)**: Select primaryid with any DRUG.role_code == "PS"; subset PLID.  
**Output (logical)**: F_PLID_PS(primaryid, …)  
**Downstream**: Use in Scenario 2 (PS-only) pipelines

## Pseudo-SQL
```sql
WITH PS AS (
  SELECT DISTINCT primaryid
  FROM DRUG
  WHERE role_code = 'PS'
)
SELECT p.*
FROM F_PLID p
JOIN PS USING (primaryid);

```
