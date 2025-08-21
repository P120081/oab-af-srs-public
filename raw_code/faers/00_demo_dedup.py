
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAERS DEMO — deduplicate to latest caseversion per caseid.
- MSIP mode: consumes global `table`, produces `result`
- CLI mode:  --in CSV --out CSV
"""
import argparse
import pandas as pd

try:
    from msi.common.dataframe import pandas_to_dataframe as to_msi_df
except Exception:
    to_msi_df = None

def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure numeric caseversion for correct ordering
    if "caseversion" in df.columns:
        df["caseversion"] = pd.to_numeric(df["caseversion"], errors="coerce")
    else:
        raise KeyError("Missing required column: caseversion")

    if "caseid" not in df.columns:
        raise KeyError("Missing required column: caseid")

    # idx of max caseversion per caseid
    idx = df.groupby("caseid")["caseversion"].idxmax()
    out = df.loc[idx].reset_index(drop=True)
    return out

def main():
    g = globals()
    if "table" in g:
        df = g["table"].to_pandas()
        out_df = transform(df)
        g["result"] = to_msi_df(out_df) if to_msi_df else out_df
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
