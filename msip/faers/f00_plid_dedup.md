
# FAERS — PLID de-duplication & merge (updated)

**Purpose**: Build FAERS patient-level dataset with the latest case state and attach outcomes/indications and drug info.

## Inputs (MSIP nodes)
- **DEMO** (case-level; has `caseid`, `caseversion`, `primaryid`, sex, age, event_dt, ...)
- **DRUG** (drug-level; has `primaryid`, `drug_seq`, role, ...)
- **OUTC** (outcome; has `primaryid`, outc_cod, ...)
- **INDI** (indication; has `primaryid`, indi_drug_seq, indi_pt, ...)

## Step 1 — DEMO de-duplication (Python node)
Use `raw_code/faers/00_demo_dedup.py` to **keep only the latest `caseversion` per `caseid`**.

## Step 2 — DRUG drug-count (Python node)
Use `raw_code/faers/02_drug_attach_count.py` to compute **`number_of_drug` per `primaryid`** and merge back into DRUG.

## Step 3 — MSIP merge (left-joins on `primaryid`)
Anchor DEMO (deduped) and **LEFT JOIN** DRUG, OUTC, INDI **in this order**, keying on `primaryid`:
1. DEMO_dedup **LEFT JOIN** DRUG_counted  ON (`primaryid`)
2. result **LEFT JOIN** OUTC              ON (`primaryid`)
3. result **LEFT JOIN** INDI              ON (`primaryid`)

> Rationale: `primaryid` (ISR) is the stable link across FAERS tables; we retain latest `caseversion` at the `caseid` level before attaching table-level details.

## Output (logical)
- `F_PLID` (case anchor with latest attributes) plus attached drug/outcome/indication columns; downstream: `f30_strata_base.md` etc.

## Pseudo-SQL
```sql
WITH latest AS (
  SELECT caseid, MAX(CAST(caseversion AS INT)) AS maxv
  FROM DEMO
  GROUP BY caseid
),
demo_dedup AS (
  SELECT d.*
  FROM DEMO d
  JOIN latest l ON d.caseid = l.caseid AND CAST(d.caseversion AS INT) = l.maxv
),
drug_cnt AS (
  SELECT primaryid, COUNT(drug_seq) AS number_of_drug
  FROM DRUG GROUP BY primaryid
)
SELECT *
FROM demo_dedup dd
LEFT JOIN (SELECT d.*, dc.number_of_drug FROM DRUG d LEFT JOIN drug_cnt dc USING (primaryid)) d2 USING (primaryid)
LEFT JOIN OUTC o USING (primaryid)
LEFT JOIN INDI i USING (primaryid);
```

## QA checklist
- [ ] Column names ASCII for public exports (e.g., `chi2`, `p_value`).
- [ ] Date fields parseable; no future dates.
- [ ] De-dup correctness: one DEMO row per `caseid` after Step 1.
- [ ] Left-join cardinality checked (no explosion on OUTC/INDI).
- [ ] Row counts recorded pre/post each step; deterministic export ordering.
