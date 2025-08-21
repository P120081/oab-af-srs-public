# JADER — Attach drug_count
**Purpose**: Count drugs per j_id and attach as drug_count.
**Input**: J_PLID, DRUG
**Operation (MSIP)**: Group by j_id in DRUG; join count back to J_PLID.
**Output (logical)**: J_PLID(+ drug_count)
**Downstream**: j30_strata_base.md
-- J02_ATTACH_DRUG_COUNT (JADER)
-- Goal: Attach per-report drug_count (from your Python node_002) to the PLID.
-- Inputs:
--   J00_PLID(j_id, sex, age, ...)             -- from your MSIP merge of DEMO+HIST
--   table_003("隴伜挨逡ｪ蜿ｷ", "譛崎脈謨ｰ", ...)          -- from your Python (count of "蛹ｻ阮ｬ蜩・｣逡ｪ")
-- Output:
--   JADER_PLID(j_id, sex, age, drug_count, ...)

WITH DRUGCOUNT AS (
  SELECT DISTINCT
         t."隴伜挨逡ｪ蜿ｷ" AS j_id,
         t."譛崎脈謨ｰ"    AS drug_count
  FROM table_003 AS t
  WHERE t."隴伜挨逡ｪ蜿ｷ" IS NOT NULL
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

