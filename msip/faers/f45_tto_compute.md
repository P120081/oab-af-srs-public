-- Inputs: table_033( primaryid, prod_ai, start_dt, pt, event_dt, ... )

-- (3) Add a raw interval column: event_dt - start_dt
WITH t034 AS (
  SELECT
    *,
    (event_dt - start_dt) AS days_raw
  FROM table_033
),

-- (4) Extract the number of days from the interval
t035 AS (
  SELECT
    *,
    DATE_PART('day', days_raw) AS days
  FROM t034
),

-- (5) Add TTO = days + 1  (1-based)
t036 AS (
  SELECT
    *,
    (days + 1) AS TTO
  FROM t035
),

-- (6) Cast TTO to integer
t037 AS (
  SELECT
    *,
    CAST(TTO AS INTEGER) AS TTO_int
  FROM t036
),

-- (7) Select and order the four public columns
t038 AS (
  SELECT
    primaryid      AS primaryid,
    prod_ai        AS drug_name,
    pt             AS event_term,
    TTO_int        AS TTO
  FROM t037
),

-- (8) Exclude negative TTO
t039 AS (
  SELECT *
  FROM t038
  WHERE TTO >= 0
)

SELECT * FROM t039;
