"""
Disproportionality metrics from 2x2 counts (logic copied from user's raw code)

Inputs (MSIP variables):
- table   : one-row DataFrame -> [N (n++), nplus1 (n+1)]
- table1  : per-DOI DataFrame -> [label, n1plus, n11]

Outputs:
- result (MSIP): table1 first column (as 'drug_of_interest') + metrics DataFrame
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from msi.common.dataframe import pandas_to_dataframe

def compute_metrics(table, table1):
    # --- to pandas ---
    totals = table.to_pandas()
    detail = table1.to_pandas()

    # --- extract counts (same indexing as your code) ---
    n11 = detail.iloc[:, 2]
    N = totals.iat[0, 0]         # n++
    n1plus = detail.iloc[:, 1]   # n1+
    n2plus = N - n1plus          # n2+
    nplus1 = totals.iat[0, 1]    # n+1
    nplus2 = N - nplus1          # n+2
    n12 = n1plus - n11
    n21 = nplus1 - n11
    n22 = nplus2 - n12

    # --- Fisher's exact (two-sided) p-values ---
    p_values = []
    for i in range(len(detail)):
        ct = [[n11[i], n12[i]], [n21[i], n22[i]]]
        _, p = stats.fisher_exact(ct)
        p_values.append(p)

    # format p-values for display
    p_values_fmt = []
    for p in p_values:
        if p < 0.001: p_values_fmt.append("<0.001")
        elif p < 0.05: p_values_fmt.append("<0.05")
        else: p_values_fmt.append(f"{p:.3f}")

    # --- ROR (odds ratio) with 95% CI (Woolf; identical to your code) ---
    with np.errstate(divide="ignore", invalid="ignore"):
         ROR = (n11 * n22) / (n12 * n21)
         se_logROR = np.sqrt(1/n11 + 1/n12 + 1/n21 + 1/n22)
         logROR = np.log(ROR)
         ROR025 = np.exp(logROR - 1.96 * se_logROR)
         ROR975 = np.exp(logROR + 1.96 * se_logROR)
    ROR = np.nan_to_num(ROR, nan=0, posinf=np.inf, neginf=0)
    ROR025 = np.nan_to_num(ROR025, nan=0, posinf=np.inf, neginf=0)
    ROR975 = np.nan_to_num(ROR975, nan=0, posinf=np.inf, neginf=0)

    # --- PRR with 95% CI (identical to your code) ---
    PRR = (n11 * n2plus) / (n1plus * n21)
    with np.errstate(divide="ignore", invalid="ignore"):
        logPRR = np.log(PRR)
        se_logPRR = np.sqrt((1/n11) - (1/n1plus) + (1/n21) - (1/n2plus))
        PRR025 = np.exp(logPRR - 1.96 * se_logPRR)
        PRR975 = np.exp(logPRR + 1.96 * se_logPRR)

    # NaN/Inf handling (same policy as your code)
    PRR = np.nan_to_num(PRR, nan=0, posinf=np.inf, neginf=0)
    PRR025 = np.nan_to_num(PRR025, nan=0, posinf=np.inf, neginf=0)
    PRR975 = np.nan_to_num(PRR975, nan=0, posinf=np.inf, neginf=0)

    # --- Chi-square (expected counts, same formulas) ---
    n11EXP = (n1plus * nplus1) / N
    n12EXP = (n1plus * nplus2) / N
    n21EXP = (n2plus * nplus1) / N
    n22EXP = (n2plus * nplus2) / N
    chi2 = ((n11 - n11EXP)**2 / n11EXP) + ((n12 - n12EXP)**2 / n12EXP) \
         + ((n21 - n21EXP)**2 / n21EXP) + ((n22 - n22EXP)**2 / n22EXP)

    # --- BCPNN IC with 95% CI (your code; ASCII vars) ---
    alpha = beta = 2
    alpha1 = beta1 = 1
    gamma11 = 1
    ln2_sq = 1 / (np.log(2))**2

    IC, IC025, IC975 = [], [], []
    for i in range(len(n11)):
        a = n11[i]
        a1 = n1plus[i]
        a2 = nplus1

        numerator = (N + alpha) * (N + beta)
        denominator = (a1 + alpha1) * (a2 + beta1)
        gamma_total = gamma11 * numerator / denominator

        num_eic = (a + gamma11) * (N + alpha) * (N + beta)
        den_eic = (N + gamma_total) * (a1 + alpha1) * (a2 + beta1)
        e_ic = np.log2(num_eic / den_eic)

        v1 = (N - a + gamma_total - gamma11) / ((a + gamma11) * (N + gamma_total))
        v2 = (N - a1 + alpha - alpha1) / ((a1 + alpha1) * (N + alpha))
        v3 = (N - a2 + beta - beta1) / ((a2 + beta1) * (N + beta))
        v_ic = ln2_sq * (v1 + v2 + v3)

        sd = np.sqrt(v_ic)
        ic025 = e_ic - 2 * sd
        ic975 = e_ic + 2 * sd

        IC.append(round(e_ic, 3))
        IC025.append(round(ic025, 3))
        IC975.append(round(ic975, 3))

    # --- build output (ASCII column names) ---
    result_df = pd.DataFrame({
    "n11": n11, "n12": n12, "n21": n21, "n22": n22,
    "ROR": ROR, "ROR025": ROR025, "ROR975": ROR975,
    "p": p_values,                 # ← 追加：数値の p
    "p_value": p_values_fmt,       # 表示用（"<0.05" 等）
    "PRR": PRR, "PRR025": PRR025, "PRR975": PRR975,
    "chi2": chi2,
    "IC": IC, "IC025": IC025, "IC975": IC975,
    })

    # thresholds (identical to your logic)
    n = n11.values if isinstance(n11, pd.Series) else n11
    p_values_num = np.asarray(p_values, dtype=float)

    ic_strength = np.select(
        [
            (np.array(IC025) <= 0),
            (np.array(IC025) > 0) & (np.array(IC025) < 1.5),
            (np.array(IC025) >= 1.5) & (np.array(IC025) < 3),
            (np.array(IC025) >= 3),
        ],
        ["none", "weak", "medium", "strong"],
        default="none",
    )

    met_ROR = np.where((n >= 3) & (p_values_num < 0.05) & (result_df["ROR025"] > 1), "Yes", "No")
    met_PRR = np.where((n >= 3) & (result_df["chi2"] > 4) & (result_df["PRR025"] > 2), "Yes", "No")
    met_IC  = np.where((n >= 3) & (result_df["IC025"] > 0), "Yes", "No")

    result_df["IC_strength"] = ic_strength
    result_df["met_ROR"] = met_ROR
    result_df["met_PRR"] = met_PRR
    result_df["met_IC"] = met_IC

    # prepend label column from table1 as 'drug_of_interest'
    labels = detail.iloc[:, 0].rename("drug_of_interest")
    result_concat = pd.concat([labels, result_df], axis=1)
    return result_concat

# --- MSIP adapter: make this the node output ---
result = pandas_to_dataframe(compute_metrics(table, table1))
