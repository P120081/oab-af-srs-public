# JADER — AF-excluded PLID
**Purpose**: Exclude PLIDs with indication/history of AF.
**Input**: J_PLID, INDI(原疾患等/indi_pt)
**Operation (MSIP)**: Collect j_id where 有害事象/原疾患等 == 心房細動; subtract from PLID.
**Output (logical)**: J_PLID_NO_AF(j_id, …)
**Downstream**: Use in Scenario 3 (AF-excluded) pipelines
# JADER 窶・AF exclusion PLID (Scenario 3)

**Purpose**  
Remove cases where AF is present in INDICATION (and optionally HISTORY), then proceed with the same pipeline as main/stratified analyses.

## Step 1 窶・Build AF-in-INDICATION ID list
- **MSIP Row filter** on the INDICATION-like column:
  - Column: `蜴溽明謔｣遲荏
  - Condition: `蜴溽明謔｣遲・== "蠢・袷邏ｰ蜍・`
  - Output: `J_AF_INDI_IDS(j_id)` *(one column with case IDs)*
- *(Optional)* If a HISTORY source exists, build `J_AF_HIST_IDS(j_id)` the same way and **union** with `J_AF_INDI_IDS`.

## Step 2 窶・Exclude those IDs from PLID
- **MSIP Python node**: `raw_code/analysis/05a_jader_af_exclude_plid.py`
  - `table`  = `J_PLID` (full PLID; must include `隴伜挨逡ｪ蜿ｷ`)
  - `table1` = `J_AF_INDI_IDS` (or a union with HISTORY IDs if available)
  - Output: `J_PLID_AF_EXCL`
  - Behavior: NFKC-normalize & trim IDs and **exclude** matches.

## Step 3 窶・Downstream
- Replace `J_PLID` with `J_PLID_AF_EXCL` in the standard flow (strata 竊・2ﾃ・ 竊・metrics 竊・figures).

## Notes
- Ensure the AF term is exactly `蠢・袷邏ｰ蜍描 and normalize whitespace prior to filtering if needed.

