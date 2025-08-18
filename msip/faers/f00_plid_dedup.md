-- F00_PLID_DEDUP — keep the latest ICSR per case (max caseversion).
WITH DEMO_DEDUP AS (
  SELECT *
  FROM DEMO d
  QUALIFY ROW_NUMBER() OVER (PARTITION BY d.caseid ORDER BY d.caseversion DESC) = 1
)
SELECT primaryid, caseid, caseversion, sex, age, age_cod, wt, wt_cod, occr_country, event_dt
FROM DEMO_DEDUP;
