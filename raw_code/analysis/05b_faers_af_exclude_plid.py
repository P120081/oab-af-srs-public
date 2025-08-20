# FAERS — Build AF-excluded PLID (Scenario 3), memory-friendly
# MSIP Python node
#
# Inputs:
#   - table  : PLID (patient-level) with column 'primaryid'
#   - table1 : AF-in-INDICATION ID list with column 'primaryid'
#
# Behavior:
#   - Collects AF-indication IDs from table1 in chunks.
#   - Streams `table` in chunks and drops rows whose 'primaryid' appears in the ID set.
#   - Returns the filtered PLID (preserving original columns/order).

from msi.common.dataframe import pandas_to_dataframe, rbind
import pandas as pd

def nrows_msip(df) -> int:
    if hasattr(df, 'nrow'):
        n = df.nrow
        return n() if callable(n) else int(n)
    if hasattr(df, 'nrows'):
        n = df.nrows
        return n() if callable(n) else int(n)
    raise RuntimeError("MSIP DataFrame does not expose nrow/nrows")

# ---- checks ----
if 'primaryid' not in table.colnames:
    raise RuntimeError("Column 'primaryid' not found in table.")
if 'primaryid' not in table1.colnames:
    raise RuntimeError("Column 'primaryid' not found in table1.")

# ---- chunk sizes (tune for your environment) ----
CHUNK_T1 = 1_000_000
CHUNK_T0 = 1_000_000

# ---- collect IDs from table1 ----
id_set = set()
# Handle both method and property styles for shape
try:
    n1 = nrows_msip(table1)
except Exception:
    # Fallback: convert to pandas once
    n1 = len(table1.to_pandas())
step = CHUNK_T1 if n1 > CHUNK_T1 else n1
start = 0
while start < n1:
    end = min(start + step, n1)
    ids_pd = table1[start:end, ['primaryid']].to_pandas() if hasattr(table1, '__getitem__') else table1.to_pandas()[['primaryid']]
    if 'primaryid' not in ids_pd.columns:
        raise RuntimeError("to_pandas() result missing 'primaryid'.")
    id_set.update(ids_pd['primaryid'].dropna().tolist())
    try:
        print(f"[AF-EXCL FAERS] collected IDs: {len(id_set):,}  ({end:,}/{n1:,})")
    except Exception:
        pass
    start = end

# ---- stream table and exclude matches ----
try:
    n0 = nrows_msip(table)
except Exception:
    n0 = len(table.to_pandas())
cols = list(table.colnames) if hasattr(table, 'colnames') else list(table.to_pandas().columns)
result_accum = None
kept_total = removed_total = processed = 0

step = CHUNK_T0 if n0 > CHUNK_T0 else n0
start = 0
while start < n0:
    end = min(start + step, n0)
    part_pd = table[start:end, cols].to_pandas() if hasattr(table, '__getitem__') else table.to_pandas().iloc[start:end, :]
    mask_keep = ~part_pd['primaryid'].isin(id_set)  # exclude matches
    kept_pd = part_pd.loc[mask_keep]

    kept_cnt = int(mask_keep.sum())
    removed_cnt = (end - start) - kept_cnt
    kept_total += kept_cnt
    removed_total += removed_cnt
    processed += (end - start)

    if kept_cnt > 0:
        msip_part = pandas_to_dataframe(kept_pd)
        result_accum = msip_part if result_accum is None else rbind(result_accum, msip_part)

    try:
        print(f"[AF-EXCL FAERS] rows {start:,}:{end:,} -> kept={kept_cnt:,}, removed={removed_cnt:,}")
    except Exception:
        pass
    start = end

# ---- finalize ----
if result_accum is None:
    empty_pd = pd.DataFrame(columns=cols)
    result = pandas_to_dataframe(empty_pd)
else:
    result = result_accum

try:
    print(f"[AF-EXCL FAERS] total: {n0:,} -> kept={kept_total:,} (removed={removed_total:,})")
except Exception:
    pass
