# JADER — AF exclusion PLID (Scenario 3)

**Purpose**  
Remove cases where AF is present in INDICATION (and optionally HISTORY), then proceed with the same pipeline as main/stratified analyses.

## Step 1 — Build AF-in-INDICATION ID list
- **MSIP Row filter** on the INDICATION-like column:
  - Column: `原疾患等`
  - Condition: `原疾患等 == "心房細動"`
  - Output: `J_AF_INDI_IDS(j_id)` *(one column with case IDs)*
- *(Optional)* If a HISTORY source exists, build `J_AF_HIST_IDS(j_id)` the same way and **union** with `J_AF_INDI_IDS`.

## Step 2 — Exclude those IDs from PLID
- **MSIP Python node**: `raw_code/analysis/05a_jader_af_exclude_plid.py`
  - `table`  = `J_PLID` (full PLID; must include `識別番号`)
  - `table1` = `J_AF_INDI_IDS` (or a union with HISTORY IDs if available)
  - Output: `J_PLID_AF_EXCL`
  - Behavior: NFKC-normalize & trim IDs and **exclude** matches.

## Step 3 — Downstream
- Replace `J_PLID` with `J_PLID_AF_EXCL` in the standard flow (strata → 2×2 → metrics → figures).

## Notes
- Ensure the AF term is exactly `心房細動` and normalize whitespace prior to filtering if needed.
