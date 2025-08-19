-- Inputs: table_033( 識別番号, 医薬品（一般名）, 投与開始日, 有害事象, 有害事象の発現日, ... )

-- (3) Add a raw interval column: event_date - start_date
WITH t034 AS (
  SELECT
    *,
    ("有害事象の発現日" - "投与開始日") AS 日数_計算結果
  FROM table_033
),

-- (4) Extract the number of days from the interval
t035 AS (
  SELECT
    *,
    DATE_PART('day', 日数_計算結果) AS 日数
  FROM t034
),

-- (5) Add TTO = days + 1  (1-based)
t036 AS (
  SELECT
    *,
    (日数 + 1) AS TTO
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
    "識別番号"        AS j_id,
    "医薬品（一般名）" AS drug_name,
    "有害事象"        AS event_term,
    TTO_int           AS TTO
  FROM t037
),

-- (8) Exclude negative TTO
t039 AS (
  SELECT *
  FROM t038
  WHERE TTO >= 0
)

SELECT * FROM t039;
