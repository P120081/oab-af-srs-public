# FAERS — Attach number_of_drug (DRUG count→F_PLID+)

_Last updated: 2025-08-21_

# FAERS — Attach number_of_drug

**Purpose**: Count drugs per primaryid and attach as number_of_drug.  
**Input**: F_PLID, DRUG  
**Operation (MSIP)**: GROUP BY primaryid in DRUG; LEFT JOIN counts back to F_PLID.  
**Output (logical)**: F_PLID(+ number_of_drug)  
**Downstream**: f30_strata_base.md

## Pseudo-SQL
```sql
WITH drug_counts AS (
  SELECT primaryid, COUNT(*) AS number_of_drug
  FROM DRUG
  GROUP BY primaryid
)
SELECT p.*, COALESCE(c.number_of_drug,0) AS number_of_drug
FROM F_PLID p
LEFT JOIN drug_counts c USING (primaryid);

```

---
## QA checklist
- [ ] Column names are ASCII-only (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `primaryid` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** F_PLID(+ number_of_drug)
