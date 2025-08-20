# FAERS — AF extract
**Purpose**: Identify AF cases from REAC.
**Input**: REAC(pt)
**Operation (MSIP)**: Filter pt == "Atrial fibrillation"; distinct primaryid.
**Output (logical)**: F_AF(primaryid)
**Downstream**: f20_counts2x2.md, f40_plid_timeseries.md
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

