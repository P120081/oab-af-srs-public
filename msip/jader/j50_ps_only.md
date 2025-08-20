# JADER — PS-only patient-level subset (Scenario 2)

**Purpose**  
Restrict to **Primary Suspect** only, then proceed with the same pipeline as the main and stratified analyses.

## Input (upstream logical name)
- `J_PLID` with columns including:
  - `j_id` (case ID)
  - `医薬品の関与` (drug role; expected value for suspect: **"被疑薬"**)
  - other columns used downstream (e.g., sex, age, drug_count, event dates if present)

## MSIP node (Row filter)
- **Condition**: `医薬品の関与 == "被疑薬"`
- **Keep all columns**.

## Output (logical name)
- `J_PLID_PS(j_id, ... )` — PS-only patient-level subset

## Downstream (Scenario 2 flow)
Replace `J_PLID` with `J_PLID_PS` in all subsequent steps of the main/stratified pipeline:
- Strata base: derive `J_STRATA_BASE` from `J_PLID_PS` (ageband, poly5, etc.).
- 2×2 counts: use the existing specs (e.g., `msip/jader/j20_counts2x2.md`) but feed PS-only inputs.
- Metrics: reuse `raw_code/analysis/01_disproportionality.py` (no code change required).
- Figures/Tables: regenerate as in the main analysis from the PS-only outputs.

## Sanity checks
- Confirm exact Unicode match for `"被疑薬"` (no extra spaces). If needed, equalize full/half width in a cleaning node.
- Record the number of rows in `J_PLID` vs `J_PLID_PS` for reproducibility logs.

## Mapping to repo logical names
- See `docs/DATA_INTERFACES.md` (J_PLID, J_STRATA_BASE, J_COUNTS2x2, etc.).
