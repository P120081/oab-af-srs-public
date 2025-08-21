#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
01_oab_standardize.py — FAERS OAB name standardization

Dual interface:
  (A) MSIP node: expects a global 'table' and returns msi.DataFrame via pandas_to_dataframe.
  (B) CLI: read CSV with ['primaryid', ('drug_of_interest' or 'prod_ai')] and write 'primaryid,drug_of_interest'.

Usage (CLI):
  python raw_code/faers/01_oab_standardize.py \
    --in data/faers_DRUG.csv \
    --out data/derived/faers_oab_standardized.csv
"""
import argparse, sys, unicodedata
import pandas as pd

# canonical OAB tokens to search (lowercase)
GENERIC_TOKENS = [
    "oxybutynin",
    "propiverine",
    "solifenacin",
    "imidafenacin",
    "tolterodine",
    "fesoterodine",
    "mirabegron",
    "vibegron",
]

def _normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)
    s = unicodedata.normalize("NFKC", s)  # normalize half/full width
    return s.strip().lower()

def _map_token(txt: str):
    s = _normalize_text(txt)
    for tok in GENERIC_TOKENS:
        if tok in s:
            return tok
    return None

def _standardize_df(df: pd.DataFrame) -> pd.DataFrame:
    if "primaryid" not in df.columns:
        raise ValueError("Input must contain 'primaryid'")
    # choose source column
    src_col = None
    for c in ["drug_of_interest","prod_ai"]:
        if c in df.columns:
            src_col = c; break
    if src_col is None:
        raise ValueError("Input must contain 'drug_of_interest' or 'prod_ai'")
    tmp = df.loc[df["primaryid"].notna() & df[src_col].notna(), ["primaryid", src_col]].copy()
    tmp["drug_of_interest"] = tmp[src_col].map(_map_token)
    out = (tmp.loc[tmp["drug_of_interest"].notna(), ["primaryid","drug_of_interest"]]
             .drop_duplicates()
             .reset_index(drop=True))
    return out

# ---- MSIP entrypoint ----
def standardize_oab_faers(table) -> "msi.DataFrame":
    """MSIP node entrypoint: input is msi.DataFrame, output the same type."""
    from msi.common.dataframe import pandas_to_dataframe
    df = table.to_pandas().copy()
    out = _standardize_df(df)
    return pandas_to_dataframe(out)

# ---- CLI ----
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in",  dest="inp",  required=False, help="Input CSV (FAERS DRUG)")
    ap.add_argument("--out", dest="outp", required=False, help="Output CSV [primaryid,drug_of_interest]")
    args = ap.parse_args()

    if args.inp is None and "table" in globals():
        out = standardize_oab_faers(globals()["table"])
        print(out)
        return

    if args.inp is None or args.outp is None:
        ap.error("CLI mode requires --in and --out")

    df = pd.read_csv(args.inp)
    out = _standardize_df(df)
    out.to_csv(args.outp, index=False, encoding="utf-8")
    print(f"[01_oab_standardize_FAERS] wrote {len(out):,} rows -> {args.outp}")

if __name__ == "__main__":
    main()
