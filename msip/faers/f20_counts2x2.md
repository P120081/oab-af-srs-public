# FAERS — 2x2 counts
**Purpose**: Build `n11`, `n12`, `n21`, `n22` per `drug_of_interest`.  
**Input**: `F_PLID`, `F_OAB_STD`, `F_AF`.  
**Operation (MSIP)**: For each drug, cross-tab (OAB vs AF) to form 2x2 counts.  
**Output (logical)**: `F_COUNTS2x2(drug_of_interest, n11, n12, n21, n22, N)`  
**Downstream**: `raw_code/analysis/01_disproportionality.py`

## Definitions
- n11: OAB and AF present.
- n12: OAB present, AF absent.
- n21: OAB absent, AF present.
- n22: neither OAB nor AF.
- N = n11 + n12 + n21 + n22.

## Pseudo-SQL
```sql
WITH pop AS (
  SELECT DISTINCT primaryid FROM F_PLID
),
oab AS (
  SELECT DISTINCT primaryid, drug_of_interest FROM F_OAB_STD
),
af AS (
  SELECT DISTINCT primaryid FROM F_AF
),
grid AS (
  SELECT p.primaryid, o.drug_of_interest
  FROM pop p
  CROSS JOIN (SELECT DISTINCT drug_of_interest FROM oab) o
),
flags AS (
  SELECT
    g.drug_of_interest,
    g.primaryid,
    CASE WHEN o.primaryid IS NOT NULL THEN 1 ELSE 0 END AS has_oab,
    CASE WHEN a.primaryid IS NOT NULL THEN 1 ELSE 0 END AS has_af
  FROM grid g
  LEFT JOIN oab o ON o.primaryid = g.primaryid AND o.drug_of_interest = g.drug_of_interest
  LEFT JOIN af  a ON a.primaryid = g.primaryid
)
SELECT
  drug_of_interest,
  SUM(CASE WHEN has_oab=1 AND has_af=1 THEN 1 ELSE 0 END) AS n11,
  SUM(CASE WHEN has_oab=1 AND has_af=0 THEN 1 ELSE 0 END) AS n12,
  SUM(CASE WHEN has_oab=0 AND has_af=1 THEN 1 ELSE 0 END) AS n21,
  SUM(CASE WHEN has_oab=0 AND has_af=0 THEN 1 ELSE 0 END) AS n22,
  COUNT(*) AS N
FROM flags
GROUP BY drug_of_interest;
```
