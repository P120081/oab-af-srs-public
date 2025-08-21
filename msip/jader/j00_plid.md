# JADER — PLID build (J_PLID)

_Last updated: 2025-08-21_

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

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_PLID(j_id, sex, age, event_date, …)
