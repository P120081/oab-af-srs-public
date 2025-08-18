-- J10_OAB_STD (JADER) — normalize OAB generics to ASCII tokens
-- Input: DRUG("識別番号", "医薬品（一般名）")
-- Output: OAB_STD_J(j_id, drug_of_interest)

WITH DRUG_STD AS (
  SELECT
    d."識別番号" AS j_id,
    d."医薬品（一般名）" AS jp_generic
  FROM DRUG d
  WHERE d."識別番号" IS NOT NULL
    AND d."医薬品（一般名）" IS NOT NULL
),
OAB_STD_J AS (
  SELECT DISTINCT
    j_id,
    CASE
      WHEN jp_generic LIKE '%ソリフェナシン%'   THEN 'solifenacin'
      WHEN jp_generic LIKE '%ミラベグロン%'     THEN 'mirabegron'
      WHEN jp_generic LIKE '%オキシブチニン%'   THEN 'oxybutynin'
      WHEN jp_generic LIKE '%プロピベリン%'     THEN 'propiverine'
      WHEN jp_generic LIKE '%イミダフェナシン%' THEN 'imidafenacin'
      WHEN jp_generic LIKE '%トルテロジン%'     THEN 'tolterodine'
      WHEN jp_generic LIKE '%フェソテロジン%'   THEN 'fesoterodine'
      WHEN jp_generic LIKE '%ビベグロン%'       THEN 'vibegron'
      ELSE NULL
    END AS drug_of_interest
  FROM DRUG_STD
)
SELECT *
FROM OAB_STD_J
WHERE drug_of_interest IS NOT NULL;
