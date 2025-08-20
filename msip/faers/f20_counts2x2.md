# FAERS — 2×2 counts
**Purpose**: Build n11,n12,n21,n22 per drug_of_interest.
**Input**: F_PLID, F_OAB_STD, F_AF
**Operation (MSIP)**: Per drug, cross-tab (OAB vs AF) to form 2×2 counts.
**Output (logical)**: F_COUNTS2x2(drug_of_interest, n11, n12, n21, n22, N)
**Downstream**: raw_code/analysis/01_disproportionality.py
-- F20_COUNTS2x2 (FAERS) 窶・counts n11..n22 per DOI + overall
-- Inputs (logical):
--   F_PLID(primaryid, sex, age, number_of_drug)
--   F_OAB_STD(primaryid, drug_of_interest)
--   F_AF(primaryid)

WITH BASE AS (
  SELECT DISTINCT
         primaryid,
         sex,
         CAST(age AS INT) AS age,
         CASE WHEN COALESCE(number_of_drug,0) >= 5 THEN '>=5' ELSE '<5' END AS poly5
  FROM F_PLID
),
DOI_LIST AS (SELECT DISTINCT drug_of_interest FROM F_OAB_STD),

COUNTS_PER_DOI AS (
  SELECT
    d.drug_of_interest,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NOT NULL THEN b.primaryid END) AS n11,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NULL THEN b.primaryid END)     AS n12,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NOT NULL THEN b.primaryid END)     AS n21,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NULL THEN b.primaryid END)         AS n22
  FROM BASE b
  JOIN DOI_LIST d ON 1=1
  LEFT JOIN F_OAB_STD oc ON oc.primaryid = b.primaryid AND oc.drug_of_interest = d.drug_of_interest
  LEFT JOIN F_AF      af ON af.primaryid = b.primaryid
  WHERE NOT EXISTS (
    SELECT 1 FROM F_OAB_STD z
    WHERE z.primaryid = b.primaryid
      AND z.drug_of_interest = d.drug_of_interest
      AND oc.primaryid IS NULL
  )
  GROUP BY d.drug_of_interest
),

COUNTS_OVERALL AS (
  SELECT
    'Overall' AS drug_of_interest,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NOT NULL THEN b.primaryid END) AS n11,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NULL THEN b.primaryid END)     AS n12,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NOT NULL THEN b.primaryid END)     AS n21,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NULL THEN b.primaryid END)         AS n22
  FROM BASE b
  LEFT JOIN F_OAB_STD oc ON oc.primaryid = b.primaryid
  LEFT JOIN F_AF      af ON af.primaryid = b.primaryid
  WHERE NOT EXISTS (
    SELECT 1 FROM F_OAB_STD z
    WHERE z.primaryid = b.primaryid AND oc.primaryid IS NULL
  )
)

SELECT * FROM COUNTS_PER_DOI
UNION ALL
SELECT * FROM COUNTS_OVERALL;

