# FAERS — PLID de-duplication (DEMO→F_PLID)

_Last updated: 2025-08-21_

# FAERS — PLID de-duplication

**Purpose**: Deduplicate DEMO per case and retain core patient/event fields.  
**Input**: FAERS DEMO (primaryid, caseversion, sex, age, event_dt)  
**Operation (MSIP)**: For each primaryid, keep the row with the maximum caseversion; select core columns.  
**Output (logical)**: F_PLID(primaryid, sex, age, event_dt, …)  
**Downstream**: f02_attach_number_of_drug.md, f30_strata_base.md

## Pseudo-SQL
```sql
WITH latest AS (
  SELECT primaryid, MAX(CAST(caseversion AS INT)) AS maxv
  FROM DEMO
  GROUP BY primaryid
)
SELECT d.primaryid,
       d.sex,
       CAST(d.age AS INT)    AS age,
       CAST(d.event_dt AS DATE) AS event_dt
FROM DEMO d
JOIN latest l
  ON d.primaryid = l.primaryid AND d.caseversion = l.maxv;

```

---
## QA checklist
- [ ] Column names are ASCII-only (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `primaryid` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** F_PLID(primaryid, sex, age, event_dt, …)
