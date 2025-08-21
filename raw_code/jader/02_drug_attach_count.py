
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JADER DRUG — attach per-case drug count
- Group by 識別番号 (fallback: j_id, primaryid), count 医薬品連番 (fallback: drug_seq)
- Output columns include both '服薬数' and 'drug_count' for downstream compatibility
- MSIP mode and CLI mode supported
"""
import argparse
import pandas as pd

try:
    from msi.common.dataframe import pandas_to_dataframe as to_msi_df
except Exception:
    to_msi_df = None

def _col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    raise KeyError(f"None of the columns {names} exist. Available: {list(df.columns)}")

def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Resolve key columns
    col_id  = _col(df, "識別番号", "j_id", "primaryid")
    col_seq = _col(df, "医薬品連番", "drug_seq")

    # Drop rows without id
    df = df[df[col_id].notna()].copy()

    # Count per id
    cnt = df.groupby(col_id)[col_seq].count().reset_index()
    cnt = cnt.rename(columns={col_seq: "服薬数"})
    cnt["drug_count"] = cnt["服薬数"]  # ASCII alias

    # Merge back (left)
    merged = df.merge(cnt, on=col_id, how="left")

    return merged

def main():
    g = globals()
    if "table" in g:
        df = g["table"].to_pandas()
        out_df = transform(df)
        if to_msi_df is not None:
            g["result"] = to_msi_df(out_df)
        else:
            g["result"] = out_df
        return

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--out", dest="out_csv", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.in_csv)
    out_df = transform(df)
    out_df.to_csv(args.out_csv, index=False)
    print(f"[WRITE] {args.out_csv}")

if __name__ == "__main__":
    main()
