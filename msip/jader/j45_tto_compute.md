# JADER — Compute TTO (days) (J_TTO)

_Last updated: 2025-08-21_

# JADER — Compute TTO (days)

**Purpose**: Compute TTO = (event_date - start_date) + 1; drop negatives; cast integer.  
**Input**: J_PLID_TS(start_date, event_date)  
**Operation (MSIP)**: Date diff, remove rows where TTO < 0, keep columns {j_id, drug_of_interest, TTO}.  
**Output (logical)**: J_TTO(j_id, drug_of_interest, TTO)  
**Downstream**: Figure 5/6 and TTO analyses

## Pseudo-SQL
```sql
SELECT j_id, drug_of_interest,
       CAST(DATEDIFF(day, start_date, event_date) + 1 AS INT) AS TTO
FROM J_PLID_TS
WHERE start_date IS NOT NULL AND event_date IS NOT NULL
  AND DATEDIFF(day, start_date, event_date) >= 0;

```

---
## QA checklist
- [ ] Column names are ASCII-only in public exports (`chi2`, `p_value`).
- [ ] Date fields parseable (YYYYMMDD/ISO); no future dates; timezone-agnostic.
- [ ] Null handling documented; duplicated `j_id` rows removed where intended.
- [ ] Row counts before→after are recorded in MSIP log.
- [ ] Deterministic ordering (ORDER BY) for reproducible exports.

**Outputs:** J_TTO(j_id, drug_of_interest, TTO)
**Public export(s):** data/derived/figure6_km_source.csv; data/derived/tto_*.csv

