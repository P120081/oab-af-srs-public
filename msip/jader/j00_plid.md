
# JADER — PLID build (with DEMO numeric/BMI preprocessing)

**Purpose**: Assemble patient-level IDs and core fields (sex, AGE, HEIGHT, WEIGHT, BMI, event_date).  
**Inputs**: DEMO_J, DRUG_J, HIST_J (merged in MSIP in this order with DEMO as the left base).  
**Downstream**: `j02_attach_drug_count.md`, `j30_strata_base.md`

## Preprocessing (Python nodes)
1. **DEMO numericization + BMI** — `raw_code/jader/00_demo_numeric_bmi.py`  
   - Convert Japanese string fields to numerics: **年齢 → AGE**, **身長 → HEIGHT**, **体重 → WEIGHT**.  
   - Business rule: strings containing “未満” are treated as **0**; numeric extraction uses the first integer token found.  
   - Apply **+5** offset to HEIGHT and WEIGHT (AGE is not offset).  
   - Compute **BMI = WEIGHT / (HEIGHT[m])²** (HEIGHT in meters).  
   - Outputs keep original Japanese columns and add ASCII aliases (AGE/HEIGHT/WEIGHT/BMI).

2. **Attach drug count (per case)** — `raw_code/jader/02_drug_attach_count.py`  
   - Group DRUG_J by **識別番号** (fallback: `j_id`) and count **医薬品連番** (fallback: `drug_seq`).  
   - Merge back as both **服薬数** and **drug_count** for downstream (poly5 derivation).

## MSIP merge order
- In MSIP, perform **left outer joins** with **DEMO** as the anchor:  
  `DEMO` **LEFT JOIN** `DRUG` **LEFT JOIN** `HIST` using the case identifier (**識別番号** / `j_id`).  
  This produces **J_PLID** (one row per case id), now including AGE/HEIGHT/WEIGHT/BMI and drug_count after merges.

## Public field naming
- Public exports should prefer ASCII keys: `age`, `height`, `weight`, `bmi`, `drug_count`.

## QA checklist
- [ ] Field names for public CSVs are ASCII-only (`chi2`, `p_value` also).  
- [ ] Date fields parse successfully; no future dates.  
- [ ] Left-join cardinality checked (no unintended row multiplication).  
- [ ] Row counts recorded before/after each step for reproducibility.  
- [ ] Deterministic ordering (ORDER BY) when exporting.
