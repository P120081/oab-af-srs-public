# FAERS — PLID time-series (start_dt×event_dt→F_PLID_TS)

_Last updated: 2025-08-21_

# FAERS — PLID time-series (start_dt × event_dt)

**Purpose**: Build start_dt × event_dt pairs for AF reports with OAB.  
**Input**: DRUG, THER(start_dt via dsg_drug_seq), DEMO(event_dt), F_OAB_STD, F_AF  
**Operation (MSIP)**: Join DRUG×THER by primaryid & dsg_drug_seq; join DEMO; filter to primaryid in both AF and OAB.  
**Output (logical)**: F_PLID_TS(primaryid, drug_of_interest, start_dt, event_dt)  
**Downstream**: f45_tto_compute.md

## Pseudo-SQL
```sql
WITH AF_CASES AS (
  SELECT DISTINCT primaryid FROM F_AF
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
  SELECT primaryid, CAST(event_dt AS DATE) AS event_dt
  FROM F_PLID
)
SELECT
  dt.primaryid,
  o.drug_of_interest,
  dt.start_dt,
  ds.event_dt
FROM DRUG_THER dt
JOIN OAB_STD o  ON o.primaryid = dt.primaryid
JOIN DEMO_STD ds ON ds.primaryid = dt.primaryid
JOIN AF_CASES a  ON a.primaryid = dt.primaryid;

```

---
## QA checklist
- [ ] Column names are ASCII-only (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `primaryid` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** F_PLID_TS(primaryid, drug_of_interest, start_dt, event_dt)
