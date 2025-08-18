"""
FAERS OAB name standardization (generics only)

Goal
-----
Normalize FAERS DRUG entries to ASCII lowercase tokens for OAB drugs.

Inputs (table must contain 'primaryid' and either column below):
- 'drug_of_interest' (pre-filled by an upstream step)  OR
- 'prod_ai' (ingredient text from FAERS DRUG table)

Output
------
OAB_STD_F with two columns:
- primaryid
- drug_of_interest   # ASCII lowercase: oxybutynin, propiverine, solifenacin,
                     # imidafenacin, tolterodine, fesoterodine, mirabegron, vibegron
"""

from msi.common.dataframe import pandas_to_dataframe
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

def standardize_oab_faers(table) -> "msi.DataFrame":
    df = table.to_pandas().copy()
    # keep rows with a valid primaryid
    df = df[df["primaryid"].notna()]

    # choose the source text to normalize
    if "drug_of_interest" in df.columns:
        src = df["drug_of_interest"].astype(str).str.lower()
    elif "prod_ai" in df.columns:
        src = df["prod_ai"].astype(str).str.lower()
    else:
        # no usable source column; return empty schema
        empty = pd.DataFrame(columns=["primaryid", "drug_of_interest"])
        return pandas_to_dataframe(empty)

    # map any substring hit to the canonical lowercase token
    def to_token(txt: str):
        for tok in GENERIC_TOKENS:
            if tok in txt:
                return tok
        return None

    df["drug_of_interest"] = src.map(to_token)

    out = (
        df.loc[df["drug_of_interest"].notna(), ["primaryid", "drug_of_interest"]]
          .drop_duplicates()
    )
    return pandas_to_dataframe(out)

# In MSIP, set:
# result = standardize_oab_faers(table)
