# JADER — Compute TTO
**Purpose**: Compute TTO = (event_date - start_date) + 1 (days).
**Input**: J_PLID_TS(start_date, event_date)
**Operation (MSIP)**: Date diff → TTO; drop negative; cast integer.
**Output (logical)**: J_TTO(j_id, drug_of_interest, TTO)
**Downstream**: Figure 5/6 and time-to-onset analyses
-- Inputs: table_033( 隴伜挨逡ｪ蜿ｷ, 蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・ 謚穂ｸ朱幕蟋区律, 譛牙ｮｳ莠玖ｱ｡, 譛牙ｮｳ莠玖ｱ｡縺ｮ逋ｺ迴ｾ譌･, ... )

-- (3) Add a raw interval column: event_date - start_date
WITH t034 AS (
  SELECT
    *,
    ("譛牙ｮｳ莠玖ｱ｡縺ｮ逋ｺ迴ｾ譌･" - "謚穂ｸ朱幕蟋区律") AS 譌･謨ｰ_險育ｮ礼ｵ先棡
  FROM table_033
),

-- (4) Extract the number of days from the interval
t035 AS (
  SELECT
    *,
    DATE_PART('day', 譌･謨ｰ_險育ｮ礼ｵ先棡) AS 譌･謨ｰ
  FROM t034
),

-- (5) Add TTO = days + 1  (1-based)
t036 AS (
  SELECT
    *,
    (譌･謨ｰ + 1) AS TTO
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
    "隴伜挨逡ｪ蜿ｷ"        AS j_id,
    "蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・ AS drug_name,
    "譛牙ｮｳ莠玖ｱ｡"        AS event_term,
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

