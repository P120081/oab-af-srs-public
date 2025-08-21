# FAERS — PLID time-series (start_dt × event_dt)
**Purpose**: Build start-date and event-date pairs for AF reports with OAB.  
**Input**: `DRUG`, `THER(start_dt via dsg_drug_seq)`, `DEMO(event_dt)`, `F_OAB_STD`, `F_AF`.  
**Operation (MSIP)**: Join DRUG×THER by sequence; join DEMO; filter to AF and OAB cases.  
**Output (logical)**: `F_PLID_TS(primaryid, drug_of_interest, start_dt, event_dt)`  
**Downstream**: `f45_tto_compute.md`

## Pseudo-SQL
```sql
WITH
AF_CASES AS (
  SELECT DISTINCT primaryid FROM REAC WHERE pt = 'Atrial fibrillation'
),
OAB_STD AS (
  SELECT DISTINCT primaryid, drug_of_interest FROM F_OAB_STD
),
DRUG_THER AS (
  SELECT d.primaryid, d.drug_seq, t.start_dt
  FROM DRUG d
  FULL OUTER JOIN THER t
    ON d.primaryid = t.primaryid AND d.drug_seq = t.dsg_drug_seq
),
DEMO_STD AS (
  SELECT primaryid, event_dt, sex, CAST(age AS INT) AS age FROM F_PLID
)
SELECT
  dt.primaryid,
  o.drug_of_interest,
  dt.start_dt,
  ds.event_dt
FROM DRUG_THER dt
JOIN OAB_STD o ON o.primaryid = dt.primaryid
JOIN DEMO_STD ds ON ds.primaryid = dt.primaryid
JOIN AF_CASES a ON a.primaryid = dt.primaryid;
```
