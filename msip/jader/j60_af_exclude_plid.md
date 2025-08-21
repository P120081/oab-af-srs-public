# JADER — AF-excluded PLID (J_PLID_NO_AF)

_Last updated: 2025-08-21_

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

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_PLID_NO_AF(j_id, …)
