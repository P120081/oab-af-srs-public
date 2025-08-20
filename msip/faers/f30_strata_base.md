# FAERS — Strata base
**Purpose**: Derive sex, ageband, and poly5 from number_of_drug.
**Input**: F_PLID(+ number_of_drug)
**Operation (MSIP)**: Compute ageband (20–69, 70–99), poly5 ( <5 / >=5 ).
**Output (logical)**: F_STRATA_BASE(primaryid, sex, ageband, poly5)
**Downstream**: Downstream stratified analyses
# FAERS 窶・STRATA_BASE specification (ageband / polypharmacy)

**Goal**  
From `F_PLID(primaryid, sex, age, number_of_drug, 窶ｦ)`, derive a light-weight table for stratified analyses:

**Output**: `F_STRATA_BASE(primaryid, sex, ageband, poly5)`

- `sex` is normalized to `Male` / `Female` if possible (other/unknown left as NULL).
- `ageband` is a coarse age band used in figures: `20-60s` or `70-90s` (others NULL).
- `poly5` is the polypharmacy flag used in figures: `Drugs<5` or `Drugs竕･5`.

---

## MSIP node steps (pseudo-SQL)

**Input**: `F_PLID`

1. **Column add 窶・normalize sex**
   ```text
   sex_norm = CASE
     WHEN LOWER(TRIM(sex)) IN ('m','male') THEN 'Male'
     WHEN LOWER(TRIM(sex)) IN ('f','female') THEN 'Female'
     ELSE NULL
   END
   ```

2. **Column add 窶・sanitize age (years)**
   ```text
   age_years = CASE
     WHEN TRY_TO_NUMBER(age) BETWEEN 0 AND 120 THEN CAST(age AS NUMBER)
     ELSE NULL
   END
   ```
   > If your `F_PLID` already has numeric `age`, use it directly.

3. **Column add 窶・ageband**
   ```text
   ageband = CASE
     WHEN age_years >= 20 AND age_years < 70 THEN '20-60s'
     WHEN age_years >= 70 AND age_years <= 99 THEN '70-90s'
     ELSE NULL
   END
   ```

4. **Column add 窶・poly5 from number_of_drug**
   ```text
   poly5 = CASE
     WHEN TRY_TO_NUMBER(number_of_drug) >= 5 THEN 'Drugs竕･5'
     WHEN TRY_TO_NUMBER(number_of_drug) > 0 THEN 'Drugs<5'
     ELSE NULL
   END
   ```

5. **Column select 窶・order & rename**
   ```text
   SELECT
     primaryid,
     sex_norm   AS sex,
     ageband,
     poly5
   竊・F_STRATA_BASE
   ```

6. **(Optional) Row filter 窶・keep rows with at least one usable stratum**
   ```text
   WHERE sex IS NOT NULL OR ageband IS NOT NULL OR poly5 IS NOT NULL
   ```

---

## Notes
- Label tokens match plotting/volcano scripts (`20-60s`, `70-90s`, `Drugs<5`, `Drugs竕･5`).
- If `sex` uses numeric codes in your PLID, insert a mapping step before *Step 1*.
- The table is intentionally minimal; downstream 2ﾃ・ count nodes may join back to richer PLID if needed.

