# JADER — AF-excluded PLID (exclude indi_pt = 心房細動)

**Purpose**: Remove PLIDs that have AF as indication/history.  
**Input**: J_PLID, INDI_J(原疾患等=indi_pt)  
**Operation (MSIP)**: Collect j_id where 原疾患等 == "心房細動" and exclude them from PLID.  
**Output (logical)**: J_PLID_NO_AF(j_id, …)  
**Downstream**: Use in Scenario 3 (AF-excluded) pipelines

## Pseudo-SQL
```sql
WITH AF_INDICATED AS (
  SELECT DISTINCT j_id
  FROM INDI_J
  WHERE 原疾患等 = '心房細動'
)
SELECT p.*
FROM J_PLID p
LEFT JOIN AF_INDICATED x USING (j_id)
WHERE x.j_id IS NULL;

```
