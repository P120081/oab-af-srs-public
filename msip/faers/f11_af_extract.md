# FAERS — AF extract (REAC→F_AF)

_Last updated: 2025-08-21_

# FAERS — AF extract (AF)

**Purpose**: Identify AF cases from REAC (MedDRA PT).  
**Input**: REAC(pt)  
**Operation (MSIP)**: Filter pt = "Atrial fibrillation"; DISTINCT primaryid.  
**Output (logical)**: F_AF(primaryid)  
**Downstream**: f20_counts2x2.md, f40_plid_timeseries.md

## Pseudo-SQL
```sql
SELECT DISTINCT primaryid
FROM REAC
WHERE pt = 'Atrial fibrillation';

```

---
## QA checklist
- [ ] Column names are ASCII-only (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `primaryid` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** F_AF(primaryid)
