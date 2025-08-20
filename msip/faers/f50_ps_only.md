# FAERS — PS-only patient-level subset (Scenario 2)

**Purpose**  
Restrict to **Primary Suspect** only, then proceed with the same pipeline as the main and stratified analyses.

## Input (upstream logical name)
- `F_PLID` with columns including:
  - `primaryid` (case ID)
  - `role_code` (drug role; expected value for suspect: **"PS"**)
  - other columns used downstream (e.g., sex, age, number_of_drug, event dates if present)

## MSIP node (Row filter)
- **Condition**: `role_code == "PS"`
- **Keep all columns**.

## Output (logical name)
- `F_PLID_PS(primaryid, ... )` — PS-only patient-level subset

## Downstream (Scenario 2 flow)
Replace `F_PLID` with `F_PLID_PS` in all subsequent steps of the main/stratified pipeline:
- Strata base: derive `F_STRATA_BASE` from `F_PLID_PS`.
- 2×2 counts: use the existing specs (e.g., `msip/faers/f20_counts2x2.md`) but feed PS-only inputs.
- Metrics: reuse `raw_code/analysis/01_disproportionality.py` (no code change required).
- Figures/Tables: regenerate as in the main analysis from the PS-only outputs.

## Sanity checks
- Confirm that `role_code` uses the literal `"PS"` for Primary Suspect in your import.
- Record the number of rows in `F_PLID` vs `F_PLID_PS` for reproducibility logs.

## Mapping to repo logical names
- See `docs/DATA_INTERFACES.md` (F_PLID, F_STRATA_BASE, F_COUNTS2x2, etc.).
