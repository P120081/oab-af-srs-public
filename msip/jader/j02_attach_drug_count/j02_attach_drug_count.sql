-- J02_ATTACH_DRUG_COUNT (JADER)
-- Goal: Attach per-report drug_count (from your Python node_002) to the PLID.
-- Inputs:
--   J00_PLID(j_id, sex, age, ...)             -- from your MSIP merge of DEMO+HIST
--   table_003("識別番号", "服薬数", ...)          -- from your Python (count of "医薬品連番")
-- Output:
--   JADER_PLID(j_id, sex, age, drug_count, ...)

WITH DRUGCOUNT AS (
  SELECT DISTINCT
         t."識別番号" AS j_id,
         t."服薬数"    AS drug_count
  FROM table_003 AS t
  WHERE t."識別番号" IS NOT NULL
)
, PLID_WITH_COUNT AS (
  SELECT
    p.*,
    COALESCE(d.drug_count, 0) AS drug_count
  FROM J00_PLID AS p
  LEFT JOIN DRUGCOUNT AS d
    ON d.j_id = p.j_id
)
SELECT * FROM PLID_WITH_COUNT;
