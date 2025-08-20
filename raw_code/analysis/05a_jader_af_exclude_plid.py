# -*- coding: utf-8 -*-
# JADER — AF-excluded PLID (Scenario 3)
# MSIP Python node: remove rows from `table` whose case ID appears in `table1`.
#
# Inputs
# - table   : full PLID (must contain column '識別番号')
# - table1  : AF-in-INDICATION ID list (must contain column '識別番号')
#
# Behavior
# - Normalizes IDs with NFKC (full-width to half-width), trims whitespace.
# - Excludes rows in `table` whose normalized ID exists in `table1`.
# - Returns the filtered PLID to MSIP.

import pandas as pd
import unicodedata
from msi.common.dataframe import pandas_to_dataframe

ID_COL = "識別番号"  # case ID column name in JADER

def _normalize_id(x):
    if pd.isna(x):
        return None
    return unicodedata.normalize("NFKC", str(x).strip())

# --- Load inputs ---
df_main = table.to_pandas().copy()
df_ref  = table1.to_pandas().copy()

# --- Build set of IDs to remove ---
ids_to_remove = set(df_ref[ID_COL].map(_normalize_id).dropna().unique())

# --- Normalize IDs in main and exclude matches ---
df_main["_norm_id"] = df_main[ID_COL].map(_normalize_id)
df_out = df_main.loc[~df_main["_norm_id"].isin(ids_to_remove)].copy()
df_out.drop(columns=["_norm_id"], inplace=True)

# --- Return to MSIP ---
result = pandas_to_dataframe(df_out)

removed = len(df_main) - len(df_out)
print(f"[AF-EXCL JADER] unique ref IDs: {len(ids_to_remove)} | removed rows: {removed} | output rows: {len(df_out)}")
