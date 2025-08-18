# Node F11: AF extraction (FAERS)

## Purpose
Select FAERS reports that mention "Atrial fibrillation" in REAC.pt.

## Input
- REAC(primaryid, pt)

## Operation (MSIP row filter)
- Condition: `pt == "Atrial fibrillation"`

## Output schema
- AF_F(primaryid)

## Pseudo-SQL (outline)
SELECT DISTINCT primaryid
FROM REAC
WHERE TRIM(pt) = 'Atrial fibrillation';
