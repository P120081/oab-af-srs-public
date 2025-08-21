# JADER — PLID build

**Purpose**: Assemble patient-level IDs and core fields (sex, age, event_date).  
**Input**: JADER DEMO-like tables (j_id, sex, age, event_date)  
**Operation (MSIP)**: Create one row per j_id with required columns.  
**Output (logical)**: J_PLID(j_id, sex, age, event_date, …)  
**Downstream**: j02_attach_drug_count.md, j30_strata_base.md

## Pseudo-SQL
```sql
SELECT j_id, sex, CAST(age AS INT) AS age, CAST(event_date AS DATE) AS event_date
FROM DEMO_J;

```
