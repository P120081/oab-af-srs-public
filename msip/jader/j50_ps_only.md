# JADER — PS-only PLID (role_code == "被疑薬/PS")

**Purpose**: Restrict PLID to suspected-drug rows only.  
**Input**: J_PLID, DRUG_J(医薬品の関与 role_code)  
**Operation (MSIP)**: Select j_id with any role_code == "被疑薬/PS"; subset PLID.  
**Output (logical)**: J_PLID_PS(j_id, …)  
**Downstream**: Use in Scenario 2 (PS-only) pipelines

## Pseudo-SQL
```sql
WITH PS AS (
  SELECT DISTINCT j_id
  FROM DRUG_J
  WHERE role_code = '被疑薬/PS'
)
SELECT p.*
FROM J_PLID p
JOIN PS USING (j_id);

```
