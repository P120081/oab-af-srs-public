# FAERS — PLID de-duplication
**Purpose**: Deduplicate DEMO per case (keep max caseversion) and retain core patient/event fields.
**Input**: FAERS DEMO (caseid/primaryid, caseversion, sex, age, event_dt)
**Operation (MSIP)**: Sort by primaryid/caseversion, take latest; select {primaryid, sex, age, event_dt, …}.
**Output (logical)**: F_PLID(primaryid, sex, age, event_dt, …)
**Downstream**: f02_attach_number_of_drug.md, f30_strata_base.md
-- F00_PLID_DEDUP 窶・keep the latest ICSR per case (max caseversion).
WITH DEMO_DEDUP AS (
  SELECT *
  FROM DEMO d
  QUALIFY ROW_NUMBER() OVER (PARTITION BY d.caseid ORDER BY d.caseversion DESC) = 1
)
SELECT primaryid, caseid, caseversion, sex, age, age_cod, wt, wt_cod, occr_country, event_dt
FROM DEMO_DEDUP;

