# JADER — AF extract (AF)

**Purpose**: Identify AF cases from REAC.  
**Input**: REAC_J(有害事象)  
**Operation (MSIP)**: Filter 有害事象 = "心房細動"; DISTINCT j_id.  
**Output (logical)**: J_AF(j_id)  
**Downstream**: j20_counts2x2.md, j40_plid_timeseries.md

## Pseudo-SQL
```sql
SELECT DISTINCT j_id
FROM REAC_J
WHERE 有害事象 = '心房細動';

```
