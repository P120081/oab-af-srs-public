-- J30_STRATA_BASE (JADER) — normalize strata labels for downstream analyses
-- INPUT: JADER_PLID(j_id, sex, age, drug_count)  -- from your Python PLID

SELECT
  j_id,
  CASE WHEN sex IN ('M','Male','男性') THEN 'M'
       WHEN sex IN ('F','Female','女性') THEN 'F'
       ELSE NULL END AS sex,
  CASE WHEN age BETWEEN 20 AND 69 THEN '20-69'
       WHEN age BETWEEN 70 AND 99 THEN '70-99'
       ELSE NULL END AS ageband,
  CASE WHEN COALESCE(drug_count, 0) >= 5 THEN '>=5' ELSE '<5' END AS poly5
FROM JADER_PLID
WHERE sex IS NOT NULL AND age IS NOT NULL;
