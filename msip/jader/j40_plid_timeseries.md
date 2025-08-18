-- JADER time-series PLID (pseudo-SQL for MSIP)

WITH demo_hist AS (
  SELECT d.識別番号 AS j_id,
         d.性別     AS sex,
         d.年齢     AS age,
         h.*        -- keep additional history fields if needed
  FROM DEMO d
  LEFT JOIN HIST h
    ON d.識別番号 = h.識別番号
),

drug_reac AS (
  -- complete outer join on patient id to keep rows present in either DRUG or REAC
  SELECT COALESCE(dr.識別番号, rc.識別番号) AS j_id,
         dr.医薬品（一般名）               AS drug_name,
         dr.投与開始日                     AS start_date,
         rc.有害事象                       AS event_term,
         rc.有害事象発現日                 AS event_date
  FROM DRUG dr
  FULL OUTER JOIN REAC rc
    ON dr.識別番号 = rc.識別番号
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
