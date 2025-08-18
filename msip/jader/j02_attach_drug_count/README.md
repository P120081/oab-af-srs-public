# Node J02: Attach drug_count to PLID (JADER)

## Purpose
Attach the per-report drug_count computed in Python (count of "医薬品連番") to the JADER PLID.

## Inputs
- J00_PLID(j_id, sex, age, ...)
- table_003("識別番号", "服薬数")  # produced by raw Python: groupby('識別番号').count('医薬品連番')

## Assumptions / Filters
- Keep only rows where "識別番号" is not NULL.
- Deduplicate to one row per "識別番号" before joining.

## Output schema
- JADER_PLID(j_id, sex, age, drug_count, ...)

## Pseudo-SQL (outline)
WITH DRUGCOUNT AS (
  SELECT DISTINCT t."識別番号" AS j_id, t."服薬数" AS drug_count
  FROM table_003 t
  WHERE t."識別番号" IS NOT NULL
)
SELECT p.*, COALESCE(d.drug_count, 0) AS drug_count
FROM J00_PLID p
LEFT JOIN DRUGCOUNT d ON d.j_id = p.j_id;
