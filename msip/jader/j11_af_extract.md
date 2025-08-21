# JADER — AF extract (J_AF)

_Last updated: 2025-08-21_

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

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_AF(j_id)
