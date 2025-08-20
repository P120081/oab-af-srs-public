# FAERS — OAB normalization
**Purpose**: Normalize OAB generic names to ASCII tokens (drug_of_interest).
**Input**: DRUG (prod_ai), mapping from raw_code/faers/01_oab_standardize.py
**Operation (MSIP)**: Lower/trim map to {oxybutynin,…,vibegron}; produce (primaryid, drug_of_interest).
**Output (logical)**: F_OAB_STD(primaryid, drug_of_interest)
**Downstream**: f20_counts2x2.md, f40_plid_timeseries.md
-- F10_OAB_AF_EXTRACT 窶・use Python-standardized OAB names; pick AF.
WITH OAB_STD AS (  -- from your Python node_003
  SELECT DISTINCT primaryid, drug_of_interest
  FROM table_051
),
AF_CASES AS (
  SELECT DISTINCT primaryid
  FROM REAC
  WHERE pt = 'Atrial fibrillation'
)
SELECT * FROM OAB_STD;     -- (primaryid, drug_of_interest)
-- SELECT * FROM AF_CASES; -- (primaryid)

