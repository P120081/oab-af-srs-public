-- F10_OAB_AF_EXTRACT — use Python-standardized OAB names; pick AF.
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
