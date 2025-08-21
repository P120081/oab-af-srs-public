# JADER — Compute TTO (days)

**Purpose**: Compute TTO = (event_date - start_date) + 1; drop negatives; cast integer.  
**Input**: J_PLID_TS(start_date, event_date)  
**Operation (MSIP)**: Date diff, remove rows where TTO < 0, keep columns {j_id, drug_of_interest, TTO}.  
**Output (logical)**: J_TTO(j_id, drug_of_interest, TTO)  
**Downstream**: Figure 5/6 and TTO analyses

## Pseudo-SQL
```sql
SELECT j_id, drug_of_interest,
       CAST(DATEDIFF(day, start_date, event_date) + 1 AS INT) AS TTO
FROM J_PLID_TS
WHERE start_date IS NOT NULL AND event_date IS NOT NULL
  AND DATEDIFF(day, start_date, event_date) >= 0;

```
