# JADER — PLID time-series
**Purpose**: Build start_date × event_date pairs for AF reports with OAB.
**Input**: DRUG, THER(start_date), DEMO(event_date), J_OAB_STD, J_AF
**Operation (MSIP)**: Join DRUG×THER by sequence; join DEMO; filter j_id in AF & OAB.
**Output (logical)**: J_PLID_TS(j_id, drug_of_interest, start_date, event_date)
**Downstream**: j45_tto_compute.md
-- JADER time-series PLID (pseudo-SQL for MSIP)

WITH demo_hist AS (
  SELECT d.隴伜挨逡ｪ蜿ｷ AS j_id,
         d.諤ｧ蛻･     AS sex,
         d.蟷ｴ鮨｢     AS age,
         h.*        -- keep additional history fields if needed
  FROM DEMO d
  LEFT JOIN HIST h
    ON d.隴伜挨逡ｪ蜿ｷ = h.隴伜挨逡ｪ蜿ｷ
),

drug_reac AS (
  -- complete outer join on patient id to keep rows present in either DRUG or REAC
  SELECT COALESCE(dr.隴伜挨逡ｪ蜿ｷ, rc.隴伜挨逡ｪ蜿ｷ) AS j_id,
         dr.蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・              AS drug_name,
         dr.謚穂ｸ朱幕蟋区律                     AS start_date,
         rc.譛牙ｮｳ莠玖ｱ｡                       AS event_term,
         rc.譛牙ｮｳ莠玖ｱ｡逋ｺ迴ｾ譌･                 AS event_date
  FROM DRUG dr
  FULL OUTER JOIN REAC rc
    ON dr.隴伜挨逡ｪ蜿ｷ = rc.隴伜挨逡ｪ蜿ｷ
),

base AS (
  SELECT dh.j_id,
         dh.sex,
         dh.age,
         dr.drug_name,
         dr.start_date,
         dr.event_term,
         dr.event_date
  FROM demo_hist dh
  LEFT JOIN drug_reac dr
    ON dh.j_id = dr.j_id
)

-- remove records without valid dates for TTO (NULL/NA/ERROR-like values)
SELECT  j_id,
        sex,
        age,
        drug_name,
        start_date,
        event_term,
        event_date
FROM    base
WHERE   start_date IS NOT NULL
  AND   event_date IS NOT NULL
  AND   start_date <> 'NA' AND start_date <> 'ERROR'
  AND   event_date <> 'NA'  AND event_date <> 'ERROR';
-- Save as: J_PLID_TS

