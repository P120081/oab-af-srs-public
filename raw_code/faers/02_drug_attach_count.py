
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAERS DRUG — attach drug count per primaryid.
- Count `drug_seq` per `primaryid`, rename to `number_of_drug`, left-merge.
- MSIP mode and CLI mode supported.
"""
import argparse
import pandas as pd

try:
    from msi.common.dataframe import pandas_to_dataframe as to_msi_df
except Exception:
    to_msi_df = None

def transform(df: pd.DataFrame) -> pd.DataFrame:
    if "primaryid" not in df.columns:
        raise KeyError("Missing required column: primaryid")
    if "drug_seq" not in df.columns:
        raise KeyError("Missing required column: drug_seq")

    df = df[df["primaryid"].notna()].copy()
    cnt = df.groupby("primaryid")["drug_seq"].count().reset_index()
    cnt = cnt.rename(columns={"drug_seq": "number_of_drug"})
    merged = df.merge(cnt, on="primaryid", how="left")
    return merged

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
