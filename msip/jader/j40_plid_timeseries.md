# JADER — PLID time-series (J_PLID_TS)

_Last updated: 2025-08-21_

# JADER — PLID time-series (start_date × event_date)

**Purpose**: Build start_date × event_date pairs for AF reports with OAB.  
**Input**: DRUG_J, THER_J(start_date via sequence), DEMO_J(event_date), J_OAB_STD, J_AF  
**Operation (MSIP)**: Join DRUG_J×THER_J by j_id & sequence; join DEMO_J; filter to j_id in both AF and OAB.  
**Output (logical)**: J_PLID_TS(j_id, drug_of_interest, start_date, event_date)  
**Downstream**: j45_tto_compute.md

## Pseudo-SQL
```sql
WITH AF_CASES AS (
  SELECT DISTINCT j_id FROM J_AF
),
OAB_STD AS (
  SELECT DISTINCT j_id, drug_of_interest FROM J_OAB_STD
),
DRUG_THER AS (
  SELECT d.j_id, d.drug_seq, t.start_date
  FROM DRUG_J d
  FULL OUTER JOIN THER_J t
    ON d.j_id = t.j_id AND d.drug_seq = t.drug_seq
),
DEMO_STD AS (
  SELECT j_id, CAST(event_date AS DATE) AS event_date
  FROM J_PLID
)
SELECT
  dt.j_id,
  o.drug_of_interest,
  dt.start_date,
  ds.event_date
FROM DRUG_THER dt
JOIN OAB_STD  o ON o.j_id = dt.j_id
JOIN DEMO_STD ds ON ds.j_id = dt.j_id
JOIN AF_CASES a  ON a.j_id = dt.j_id;

```

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_PLID_TS(j_id, drug_of_interest, start_date, event_date)
