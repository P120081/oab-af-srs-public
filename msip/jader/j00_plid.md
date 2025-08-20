# JADER — PLID
**Purpose**: Assemble patient-level IDs and core fields.
**Input**: JADER DEMO-like tables (j_id, sex, age, event_date)
**Operation (MSIP)**: Build per j_id record with required columns.
**Output (logical)**: J_PLID(j_id, sex, age, event_date, …)
**Downstream**: j02_attach_drug_count.md, j30_strata_base.md
-- J00_PLID (JADER) 窶・DEMO normalized, joined with HIST.
WITH DEMO_STD AS (
  SELECT
    DEMO."隴伜挨逡ｪ蜿ｷ"         AS j_id,
    DEMO."諤ｧ蛻･"            AS sex,
    CAST(DEMO."蟷ｴ鮨｢" AS INT) AS age,
    DEMO."菴馴㍾"            AS weight,
    DEMO."霄ｫ髟ｷ"            AS height
  FROM DEMO
),
PLID AS (
  SELECT d.*, h.*
  FROM DEMO_STD d
  LEFT JOIN HIST h ON h."隴伜挨逡ｪ蜿ｷ" = d.j_id
)
SELECT * FROM PLID;

