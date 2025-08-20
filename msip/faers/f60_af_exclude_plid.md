# FAERS — AF-excluded PLID
**Purpose**: Exclude PLIDs with indication/history of AF.
**Input**: F_PLID, INDI(indi_pt)
**Operation (MSIP)**: Collect primaryid where indi_pt == "Atrial fibrillation"; subtract from PLID.
**Output (logical)**: F_PLID_NO_AF(primaryid, …)
**Downstream**: Use in Scenario 3 (AF-excluded) pipelines
# FAERS 窶・AF exclusion PLID (Scenario 3)

**Purpose**  
Remove cases where AF is present as INDICATION (and optionally HISTORY), then run the same pipeline as the main/stratified analyses.

## Step 1 窶・Build AF-in-INDICATION ID list
- **MSIP Row filter** on the INDICATION column:
  - Column: `indi_pt`
  - Condition: `indi_pt == "Atrial fibrillation"`
  - Output: `F_AF_INDI_IDS(primaryid)` *(1-column table with case IDs)*
- *(Optional)* If a HISTORY source exists, build `F_AF_HIST_IDS(primaryid)` the same way and **union** with `F_AF_INDI_IDS`.

## Step 2 窶・Exclude those IDs from PLID
- **MSIP Python node**: `raw_code/analysis/05b_faers_af_exclude_plid.py`
  - `table`  = `F_PLID` (full PLID)
  - `table1` = `F_AF_INDI_IDS` (or a union with HISTORY IDs if available)
  - Output: `F_PLID_AF_EXCL`
  - Behavior: chunked filtering; drops rows whose `primaryid` is in the AF list.

## Step 3 窶・Downstream
- Replace `F_PLID` with `F_PLID_AF_EXCL` in the standard flow (strata 竊・2ﾃ・ 竊・metrics 竊・figures).

## Notes
- Confirm the exact PT string is `"Atrial fibrillation"` and that `primaryid` exists in both inputs.

