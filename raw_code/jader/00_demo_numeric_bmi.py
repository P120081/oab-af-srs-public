
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JADER DEMO cleaner — numeric AGE/HEIGHT/WEIGHT + BMI
- MSIP mode: read global `table`, write `result` (msi DataFrame)
- CLI mode:  --in CSV --out CSV
"""
import argparse
import pandas as pd

# MSIP bridge (optional)
try:
    from msi.common.dataframe import DataFrame as MSIDataFrame
except Exception:
    MSIDataFrame = None

def extract_numeric_or_zero(val: object):
    import pandas as _pd
    if _pd.isna(val):
        return None
    s = str(val).strip()
    if s == "":
        return None
    # treat "未満" as 0
    if "未満" in s:
        return 0
    # pick first integer in the string
    m = _pd.Series([s]).str.extract(r"(\d+)")
    return int(m.iloc[0,0]) if _pd.notnull(m.iloc[0,0]) else None

def calculate_bmi(weight, height_cm):
    import pandas as _pd
    if _pd.isna(weight) or _pd.isna(height_cm) or float(height_cm) == 0.0:
        return None
    h_m = float(height_cm) / 100.0
    return round(float(weight) / (h_m**2), 2)

def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Column aliases (Japanese -> internal); fallbacks are no-op if not present
    col_weight = "体重"
    col_height = "身長"
    col_age    = "年齢"

    # Safe-string views
    for col in [col_weight, col_height, col_age]:
        if col in df.columns:
            df[f"{col}_str"] = df[col].apply(lambda x: str(x) if pd.notnull(x) else "")
        else:
            # create empty if missing
            df[f"{col}_str"] = ""

    # Extract numerics
    df["体重数値"] = df["体重_str"].apply(extract_numeric_or_zero)
    df["身長数値"] = df["身長_str"].apply(extract_numeric_or_zero)
    df["年齢数値"] = df["年齢_str"].apply(extract_numeric_or_zero)

    # +5 only to weight/height, age is no offset
    df["WEIGHT"] = pd.to_numeric(df["体重数値"], errors="coerce") + 5
    df["HEIGHT"] = pd.to_numeric(df["身長数値"], errors="coerce") + 5
    df["AGE"]    = pd.to_numeric(df["年齢数値"], errors="coerce")

    # BMI
    df["BMI"] = df.apply(lambda r: calculate_bmi(r.get("WEIGHT"), r.get("HEIGHT")), axis=1)

    return df

def main():
    # MSIP mode?
    g = globals()
    if "table" in g:
        df = g["table"].to_pandas()
        out_df = transform(df)
        if MSIDataFrame is not None:
            # keep types as object to be safe with MSIP
            result_df = out_df.astype(object)
            g["result"] = MSIDataFrame(result_df.to_dict(orient="list"))
        else:
            g["result"] = out_df
        return

    # CLI mode
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
