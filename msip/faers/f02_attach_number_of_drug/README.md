# Node F02: Attach number_of_drug to PLID (FAERS)

## Inputs
- F00_PLID_DEDUP(primaryid, sex, age, event_dt, ...)
- table_045(primaryid, number_of_drug)  # raw Python: groupby('primaryid').count('drug_seq')

## Output
- FAERS_PLID(primaryid, sex, age, event_dt, number_of_drug, ...)
