# FAERS — 2×2 counts per drug

**Purpose**: Build n11, n12, n21, n22 per drug_of_interest.  
**Input**: F_PLID, F_OAB_STD, F_AF  
**Operation (MSIP)**: For each drug_of_interest, count AF vs non-AF among OAB-exposed and non-exposed cases.  
**Output (logical)**: F_COUNTS2x2(drug_of_interest, n11, n12, n21, n22, N, n1plus, nplus1)  
**Downstream**: raw_code/analysis/01_disproportionality.py

## Pseudo-SQL
```sql
WITH base AS (
  SELECT p.primaryid,
         CASE WHEN o.primaryid IS NOT NULL THEN 1 ELSE 0 END AS oab_exposed,
         CASE WHEN a.primaryid IS NOT NULL THEN 1 ELSE 0 END AS is_af,
         o.drug_of_interest
  FROM F_PLID p
  LEFT JOIN F_OAB_STD o USING (primaryid)
  LEFT JOIN F_AF a       USING (primaryid)
),
per_drug AS (
  SELECT drug_of_interest,
         SUM(CASE WHEN oab_exposed=1 AND is_af=1 THEN 1 ELSE 0 END) AS n11,
         SUM(CASE WHEN oab_exposed=1 AND is_af=0 THEN 1 ELSE 0 END) AS n12,
         SUM(CASE WHEN oab_exposed=0 AND is_af=1 THEN 1 ELSE 0 END) AS n21,
         SUM(CASE WHEN oab_exposed=0 AND is_af=0 THEN 1 ELSE 0 END) AS n22,
         COUNT(*) AS N,
         SUM(CASE WHEN oab_exposed=1 THEN 1 ELSE 0 END) AS n1plus,
         SUM(CASE WHEN is_af=1 THEN 1 ELSE 0 END)     AS nplus1
  FROM base
  WHERE drug_of_interest IS NOT NULL
  GROUP BY drug_of_interest
)
SELECT * FROM per_drug;

```
