# FAERS — PLID time-series
**Purpose**: Build start_dt × event_dt pairs for AF reports with OAB.
**Input**: DRUG, THER (start_dt), DEMO (event_dt), F_OAB_STD, F_AF
**Operation (MSIP)**: Join DRUG×THER by dsg_drug_seq; join DEMO; filter primaryid in AF & OAB.
**Output (logical)**: F_PLID_TS(primaryid, drug_of_interest, start_dt, event_dt)
**Downstream**: f45_tto_compute.md
-- FAERS time-series PLID (pseudo-SQL for MSIP)

WITH demo_dedup AS (
  -- keep the primaryid belonging to the max caseversion per caseid
  SELECT d1.*
  FROM DEMO d1
  JOIN (
    SELECT caseid, MAX(caseversion) AS max_ver
    FROM DEMO
    GROUP BY caseid
  ) m
    ON d1.caseid = m.caseid AND d1.caseversion = m.max_ver
),

demo_reac AS (
  SELECT de.primaryid,
         de.sex,
         de.age,
         de.event_dt,
         rc.pt AS event_term
  FROM demo_dedup de
  LEFT JOIN REAC rc
    ON de.primaryid = rc.primaryid
),

drug_ther AS (
  -- complete outer join on (primaryid, drug_seq) 竕・(primaryid, dsg_drug_seq)
  SELECT COALESCE(dr.primaryid, th.primaryid) AS primaryid,
         dr.prod_ai                           AS drug_name,
         th.start_dt                          AS start_dt
  FROM DRUG dr
  FULL OUTER JOIN THER th
    ON  dr.primaryid   = th.primaryid
    AND dr.drug_seq    = th.dsg_drug_seq
),

base AS (
  SELECT dt.primaryid,
         dt.sex,
         dt.age,
         dt.event_dt,
         dt.event_term,
         t.drug_name,
         t.start_dt
  FROM demo_reac dt
  LEFT JOIN drug_ther t
    ON dt.primaryid = t.primaryid
)

-- remove rows without valid TTO dates
SELECT  primaryid,
        sex,
        age,
        drug_name,
        start_dt,
        event_term,
        event_dt
FROM    base
WHERE   start_dt IS NOT NULL
  AND   event_dt  IS NOT NULL
  AND   start_dt <> 'NA' AND start_dt <> 'ERROR'
  AND   event_dt  <> 'NA' AND event_dt  <> 'ERROR';
-- Save as: F_PLID_TS

