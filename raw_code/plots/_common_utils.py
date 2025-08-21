
# raw_code/plots/_common_utils.py
import pandas as pd

OKABE_ITO = {
    "Orange":  "#E69F00",
    "SkyBlue": "#56B4E9",
    "Bluish":  "#0072B2",
    "Reddish": "#D55E00",
    "Green":   "#009E73",
    "Yellow":  "#F0E442",
}

def load_table_like(path_or_df, expected=None, prefer_numeric_p=True):
    """
    Load a pandas DataFrame from either:
      - MSIP 'table' object (already DataFrame-like), or
      - CSV path / DataFrame
    Normalize common columns to ASCII names used publicly.
    """
    if hasattr(path_or_df, "to_pandas"):  # MSIP table
        df = path_or_df.to_pandas().copy()
    elif isinstance(path_or_df, pd.DataFrame):
        df = path_or_df.copy()
    else:
        df = pd.read_csv(str(path_or_df))

    # normalize header variants
    rename = {}
    # p-value variants
    if "p" not in df.columns:
        for cand in ["p_value","p-value","p value","P","P-value","P value"]:
            if cand in df.columns:
                rename[cand] = "p"
                break
    # chi2 variants
    for cand in ["χ^2","χ²","chi^2","x2","X2"]:
        if cand in df.columns:
            rename[cand] = "chi2"
            break
    # Subgroup normalize ≥ to >=
    if "Subgroup" in df.columns:
        df["Subgroup"] = df["Subgroup"].astype(str).str.replace("≥", ">=")
    if rename:
        df = df.rename(columns=rename)

    # Optionally coerce numeric p from display strings
    if "p" in df.columns and prefer_numeric_p:
        df["p"] = (
            df["p"].astype(str)
            .str.replace("<", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    return df
