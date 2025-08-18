# Node J11: AF extraction (JADER)

## Purpose
Select JADER reports that mention AF in Japanese term.

## Input
- REAC("識別番号", "有害事象")

## Operation (MSIP row filter)
- Condition: `"有害事象" == '心房細動'`

## Output schema
- AF_J(j_id)

## Pseudo-SQL (outline)
SELECT DISTINCT "識別番号" AS j_id
FROM REAC
WHERE TRIM("有害事象") = '心房細動';
