-- F30_TTO_CANDIDATES — THER.start_dt × DEMO.event_dt for AF reports with OAB (2 drugs).
WITH
AF_CASES AS (
  SELECT DISTINCT primaryid
  FROM REAC
  WHERE pt = 'Atrial fibrillation'
),
OAB_STD AS (
  SELECT DISTINCT primaryid, drug_of_interest
  FROM table_051  -- from your Python node_003
  WHERE drug_of_interest IN ('solifenacin','mirabegron')
),
DRUG_THER AS ( -- DRUG × THER by sequence
  SELECT d.primaryid, d.drug_seq, t.start_dt
  FROM DRUG d
  FULL OUTER JOIN THER t
    ON d.primaryid = t.primaryid AND d.drug_seq = t.dsg_drug_seq
),
DEMO_STD AS (
  SELECT primaryid, event_dt, sex, CAST(age AS INT) AS age FROM F00_PLID_DEDUP
)
SELECT
  dt.primaryid,
  o.drug_of_interest,
  dt.start_dt,
  ds.event_dt
FROM DRUG_THER dt
JOIN OAB_STD o ON o.primaryid = dt.primaryid
JOIN DEMO_STD ds ON ds.primaryid = dt.primaryid
JOIN AF_CASES a ON a.primaryid = dt.primaryid;
