# FAERS — Compute TTO (days)

**Purpose**: Compute TTO = DATEDIFF(event_dt, start_dt) + 1; drop negatives; cast integer.  
**Input**: F_PLID_TS(start_dt, event_dt)  
**Operation (MSIP)**: Date diff, remove rows where TTO < 0, keep columns {primaryid, drug_of_interest, TTO}.  
**Output (logical)**: F_TTO(primaryid, drug_of_interest, TTO)  
**Downstream**: Figure 5/6 and TTO analyses

## Pseudo-SQL
```sql
SELECT primaryid, drug_of_interest,
       CAST(DATEDIFF(day, start_dt, event_dt) + 1 AS INT) AS TTO
FROM F_PLID_TS
WHERE start_dt IS NOT NULL AND event_dt IS NOT NULL
  AND DATEDIFF(day, start_dt, event_dt) >= 0;

```
