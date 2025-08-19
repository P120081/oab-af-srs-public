"""
Select the earliest (start_date, event_date) pair per record key.
MSIP Python node — works for both JADER and FAERS by column POSITION.

Behavior
- Treats two date columns by 0-based positions (default: index 2 = start, index 4 = event).
- Keeps only rows where BOTH dates are the earliest within each group (group = all other columns).
- Drops exact duplicates.
- (Optional) Exclude negative TTO by enforcing start <= event.

If your PLID table uses different column order, just change START_COL_IDX / EVENT_COL_IDX.
Examples:
  - If columns are [id, drug, start_date, event_term, event_date] -> (2, 4)  # default
  - If you use the pseudo-SQL layout we drafted earlier
    [j_id, sex, age, drug_name, start_date, event_term, event_date] -> set (4, 6)

Input:  MSIP `table` -> pandas DataFrame
Output: DataFrame with earliest pairs only (returned to MSIP)
"""

from msi.common.dataframe import DataFrame
from msi.common.dataframe import pandas_to_dataframe
import pandas as pd

# ---- Adjust here if your column order differs ----
START_COL_IDX = 2   # start-date column (0-based index)
EVENT_COL_IDX = 4   # event-date column (0-based index)
ENFORCE_START_LE_EVENT = False  # set True to drop negative TTO pairs

# ---- Load ----
df = table.to_pandas().copy()

# Validate indices quickly (prevent out-of-range surprises)
ncols = len(df.columns)
if START_COL_IDX >= ncols or EVENT_COL_IDX >= ncols:
    raise IndexError(
        f"Configured date column indexes ({START_COL_IDX}, {EVENT_COL_IDX}) "
        f"exceed available columns (n={ncols})."
    )

start_col = df.columns[START_COL_IDX]
event_col = df.columns[EVENT_COL_IDX]

# Parse dates (invalid -> NaT)
df[start_col] = pd.to_datetime(df[start_col], errors="coerce")
df[event_col] = pd.to_datetime(df[event_col], errors="coerce")

# Keep rows having BOTH valid dates
df_valid = df[df[start_col].notna() & df[event_col].notna()].copy()

# (Optional) enforce start <= event to drop negative TTO
if ENFORCE_START_LE_EVENT:
    df_valid = df_valid[df_valid[start_col] <= df_valid[event_col]]

# Group key = all columns EXCEPT the two date columns
group_keys = [c for i, c in enumerate(df_valid.columns) if i not in (START_COL_IDX, EVENT_COL_IDX)]

if group_keys:
    # Compute group-wise minima for both dates
    gmin = df_valid.groupby(group_keys)[[start_col, event_col]].transform("min")
    # Keep only the rows that match BOTH minima
    df_earliest = df_valid[
        (df_valid[start_col] == gmin[start_col]) &
        (df_valid[event_col] == gmin[event_col])
    ].copy()
else:
    # If the table has only the two date columns
    min_start = df_valid[start_col].min()
    min_event = df_valid[event_col].min()
    df_earliest = df_valid[
        (df_valid[start_col] == min_start) &
        (df_valid[event_col] == min_event)
    ].copy()

# Drop exact duplicates and reindex
df_earliest = df_earliest.drop_duplicates().reset_index(drop=True)

# Return to MSIP
result = pandas_to_dataframe(df_earliest)
