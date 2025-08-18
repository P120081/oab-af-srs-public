-- F20_COUNTS2x2 (FAERS) — counts n11..n22 per DOI + overall
-- INPUT TABLES:
--   OAB_STD(primaryid, drug_of_interest)     -- from your Python OAB normalizer
--   AF_CASES(primaryid)                      -- FAERS AF cases (PT='Atrial fibrillation')
--   FAERS_PLID(primaryid, sex, age, number_of_drug)  -- from your Python PLID (already includes number_of_drug)

WITH BASE AS (
  SELECT DISTINCT
         primaryid,
         sex,
         CAST(age AS INT) AS age,
         CASE WHEN COALESCE(number_of_drug, 0) >= 5 THEN '>=5' ELSE '<5' END AS poly5
  FROM FAERS_PLID
),
DOI_LIST AS (SELECT DISTINCT drug_of_interest FROM OAB_STD),

COUNTS_PER_DOI AS (
  SELECT
    d.drug_of_interest,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NOT NULL THEN b.primaryid END) AS n11,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NOT NULL AND af.primaryid IS NULL THEN b.primaryid END)     AS n12,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NOT NULL THEN b.primaryid END)     AS n21,
    COUNT(DISTINCT CASE WHEN oc.primaryid IS NULL AND af.primaryid IS NULL THEN b.primaryid END)         AS n22
  FROM BASE b
  JOIN DOI_LIST d ON 1=1
  LEFT JOIN OAB_STD oc ON oc.primaryid = b.primaryid AND oc.drug_of_interest = d.drug_of_interest
  LEFT JOIN AF_CASES  af ON af.primaryid = b.primaryid
  WHERE NOT EXISTS (
    SELECT 1 FROM OAB_STD z
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
  LEFT JOIN OAB_STD oc ON oc.primaryid = b.primaryid
  LEFT JOIN AF_CASES  af ON af.primaryid = b.primaryid
  WHERE NOT EXISTS (
    SELECT 1 FROM OAB_STD z
    WHERE z.primaryid = b.primaryid
      AND oc.primaryid IS NULL
  )
)
SELECT * FROM COUNTS_PER_DOI
UNION ALL
SELECT * FROM COUNTS_OVERALL;
