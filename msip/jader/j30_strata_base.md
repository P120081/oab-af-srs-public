# JADER — Strata base
**Purpose**: Derive sex, ageband, and poly5 from drug_count.
**Input**: J_PLID(+ drug_count)
**Operation (MSIP)**: Compute ageband (20–69, 70–99), poly5 ( <5 / >=5 ).
**Output (logical)**: J_STRATA_BASE(j_id, sex, ageband, poly5)
**Downstream**: Downstream stratified analyses
-- J30_STRATA_BASE (JADER) 窶・normalize strata labels for downstream analyses
-- INPUT: JADER_PLID(j_id, sex, age, drug_count)  -- from your Python PLID

SELECT
  j_id,
  CASE WHEN sex IN ('M','Male','逕ｷ諤ｧ') THEN 'M'
       WHEN sex IN ('F','Female','螂ｳ諤ｧ') THEN 'F'
       ELSE NULL END AS sex,
  CASE WHEN age BETWEEN 20 AND 69 THEN '20-69'
       WHEN age BETWEEN 70 AND 99 THEN '70-99'
       ELSE NULL END AS ageband,
  CASE WHEN COALESCE(drug_count, 0) >= 5 THEN '>=5' ELSE '<5' END AS poly5
FROM JADER_PLID
WHERE sex IS NOT NULL AND age IS NOT NULL;

