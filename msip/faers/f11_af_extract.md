# FAERS — AF extract (AF)

**Purpose**: Identify AF cases from REAC (MedDRA PT).  
**Input**: REAC(pt)  
**Operation (MSIP)**: Filter pt = "Atrial fibrillation"; DISTINCT primaryid.  
**Output (logical)**: F_AF(primaryid)  
**Downstream**: f20_counts2x2.md, f40_plid_timeseries.md

## Pseudo-SQL
```sql
SELECT DISTINCT primaryid
FROM REAC
WHERE pt = 'Atrial fibrillation';

```
