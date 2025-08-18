-- J00_PLID (JADER) — DEMO normalized, joined with HIST.
WITH DEMO_STD AS (
  SELECT
    DEMO."識別番号"         AS j_id,
    DEMO."性別"            AS sex,
    CAST(DEMO."年齢" AS INT) AS age,
    DEMO."体重"            AS weight,
    DEMO."身長"            AS height
  FROM DEMO
),
PLID AS (
  SELECT d.*, h.*
  FROM DEMO_STD d
  LEFT JOIN HIST h ON h."識別番号" = d.j_id
)
SELECT * FROM PLID;
