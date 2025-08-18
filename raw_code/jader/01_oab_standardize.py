"""
JADER OAB name standardization
- Input columns: '識別番号', '医薬品（一般名）' (from JADER DRUG)
- Output columns: 'j_id', 'drug_of_interest' (ASCII tokens)
"""

import pandas as pd
from msi.common.dataframe import pandas_to_dataframe

def normalize_oab_jader(table) -> "msi.DataFrame":
    df = table.to_pandas()
    df = df[df['識別番号'].notna() & df['医薬品（一般名）'].notna()].copy()

    # handle spelling variants (substring match) in Japanese generics
    yure_dict = {
        "オキシブチニン":"オキシブチニン",
        "プロピベリン":"プロピベリン",
        "ソリフェナシン":"ソリフェナシン",
        "イミダフェナシン":"イミダフェナシン",
        "トルテロジン":"トルテロジン",
        "フェソテロジン":"フェソテロジン",
        "ミラベグロン":"ミラベグロン",
        "ビベグロン":"ビベグロン",
    }
    def norm_jp(s: str) -> str:
        for k, canon in yure_dict.items():
            if k in s:
                return canon
        return s

    df['__jp_norm'] = df['医薬品（一般名）'].astype(str).map(norm_jp)

    # map to ASCII tokens for downstream uniformity
    jp_to_ascii = {
        "オキシブチニン":"oxybutynin",
        "プロピベリン":"propiverine",
        "ソリフェナシン":"solifenacin",
        "イミダフェナシン":"imidafenacin",
        "トルテロジン":"tolterodine",
        "フェソテロジン":"fesoterodine",
        "ミラベグロン":"mirabegron",
        "ビベグロン":"vibegron",
    }
    df['drug_of_interest'] = df['__jp_norm'].map(jp_to_ascii)

    out = (df.loc[df['drug_of_interest'].notna(), ['識別番号','drug_of_interest']]
             .drop_duplicates()
             .rename(columns={'識別番号':'j_id'}))

    return pandas_to_dataframe(out)
