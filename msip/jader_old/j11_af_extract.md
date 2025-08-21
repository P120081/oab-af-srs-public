# JADER — AF extract
**Purpose**: Identify AF cases from REAC.
**Input**: REAC(有害事象)
**Operation (MSIP)**: Filter 有害事象 == "心房細動"; distinct j_id.
**Output (logical)**: J_AF(j_id)
**Downstream**: j20_counts2x2.md, j40_plid_timeseries.md
# Node J11: AF extraction (JADER)

## Purpose
Select JADER reports that mention AF in Japanese term.

## Input
- REAC("隴伜挨逡ｪ蜿ｷ", "譛牙ｮｳ莠玖ｱ｡")

## Operation (MSIP row filter)
- Condition: `"譛牙ｮｳ莠玖ｱ｡" == '蠢・袷邏ｰ蜍・`

## Output schema
- AF_J(j_id)

## Pseudo-SQL (outline)
SELECT DISTINCT "隴伜挨逡ｪ蜿ｷ" AS j_id
FROM REAC
WHERE TRIM("譛牙ｮｳ莠玖ｱ｡") = '蠢・袷邏ｰ蜍・;

