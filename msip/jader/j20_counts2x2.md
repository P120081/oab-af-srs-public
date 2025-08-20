# JADER — 2×2 counts
**Purpose**: Build n11,n12,n21,n22 per drug_of_interest.
**Input**: J_PLID, J_OAB_STD, J_AF
**Operation (MSIP)**: Per drug, cross-tab (OAB vs AF) to form 2×2 counts.
**Output (logical)**: J_COUNTS2x2(drug_of_interest, n11, n12, n21, n22, N)
**Downstream**: raw_code/analysis/01_disproportionality.py
-- J20_COUNTS2x2 (JADER) 窶・counts n11..n22 per DOI + overall
-- Inputs (logical):
--   J_PLID(j_id, sex, age, drug_count)
--   J_OAB_STD(j_id, drug_of_interest)
--   J_AF(j_id)

WITH BASE AS (
  SELECT DISTINCT
         j_id,
         sex,
         age,
         CASE WHEN COALESCE(drug_count,0) >= 5 THEN '>=5' ELSE '<5' END AS poly5
  FROM J_PLID
),
DOI_LIST AS (SELECT DISTINCT drug_of_interest FROM J_OAB_STD),

COUNTS_PER_DOI AS (
  SELECT
    d.drug_of_interest,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NOT NULL AND af.j_id IS NOT NULL THEN b.j_id END) AS n11,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NOT NULL AND af.j_id IS NULL THEN b.j_id END)     AS n12,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NULL AND af.j_id IS NOT NULL THEN b.j_id END)     AS n21,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NULL AND af.j_id IS NULL THEN b.j_id END)         AS n22
  FROM BASE b
  JOIN DOI_LIST d ON 1=1
  LEFT JOIN J_OAB_STD oc ON oc.j_id = b.j_id AND oc.drug_of_interest = d.drug_of_interest
  LEFT JOIN J_AF      af ON af.j_id = b.j_id
  -- exclude from background any report containing the DOI
  WHERE NOT EXISTS (
    SELECT 1 FROM J_OAB_STD z
    WHERE z.j_id = b.j_id
      AND z.drug_of_interest = d.drug_of_interest
      AND oc.j_id IS NULL
  )
  GROUP BY d.drug_of_interest
),

COUNTS_OVERALL AS (
  SELECT
    'Overall' AS drug_of_interest,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NOT NULL AND af.j_id IS NOT NULL THEN b.j_id END) AS n11,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NOT NULL AND af.j_id IS NULL THEN b.j_id END)     AS n12,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NULL AND af.j_id IS NOT NULL THEN b.j_id END)     AS n21,
    COUNT(DISTINCT CASE WHEN oc.j_id IS NULL AND af.j_id IS NULL THEN b.j_id END)         AS n22
  FROM BASE b
  LEFT JOIN J_OAB_STD oc ON oc.j_id = b.j_id
  LEFT JOIN J_AF      af ON af.j_id = b.j_id
  WHERE NOT EXISTS (
    SELECT 1 FROM J_OAB_STD z
    WHERE z.j_id = b.j_id AND oc.j_id IS NULL
  )
)

SELECT * FROM COUNTS_PER_DOI
UNION ALL
SELECT * FROM COUNTS_OVERALL;

