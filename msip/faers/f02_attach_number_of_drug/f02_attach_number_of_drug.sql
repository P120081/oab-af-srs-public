-- F02_ATTACH_NUMBER_OF_DRUG (FAERS)
-- Goal: Attach per-report number_of_drug (from your Python node_002) to the PLID.
-- Inputs:
--   F00_PLID_DEDUP(primaryid, sex, age, event_dt, ...) -- DEMO deduped by max caseversion
--   table_045(primaryid, number_of_drug, ...)          -- from your Python (count of drug_seq)
-- Output:
--   FAERS_PLID(primaryid, sex, age, event_dt, number_of_drug, ...)

WITH DRUGCOUNT AS (
  SELECT DISTINCT
         t.primaryid,
         t.number_of_drug
  FROM table_045 AS t
  WHERE t.primaryid IS NOT NULL
)
, PLID_WITH_COUNT AS (
  SELECT
    p.*,
    COALESCE(d.number_of_drug, 0) AS number_of_drug
  FROM F00_PLID_DEDUP AS p
  LEFT JOIN DRUGCOUNT AS d
    ON d.primaryid = p.primaryid
)
SELECT * FROM PLID_WITH_COUNT;
