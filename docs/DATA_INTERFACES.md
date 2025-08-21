# Data Interfaces (Public Repro)

This document defines the **schemas** expected by the public plotting scripts in `raw_code/plots`. Column names are **case‑sensitive** unless aliases are explicitly listed.

> Numeric fields accept strings that can be parsed as numbers, including **scientific notation** (e.g., `5.54E-18`).

---

## A. `figure2_source.csv` — Fig.2 (single‑drug forest)

| Column              | Type    | Required | Notes |
|---------------------|---------|---------:|------|
| `DB`                | string  | ✓ | One of `FAERS` / `JADER` |
| `drug_of_interest`  | string  | ✓ | Display label for the drug |
| `Subgroup`          | string  | – | Optional subgroup label (overall / strata) |
| `n11`               | int     | ✓ | Target‑drug + AF reports count |
| `ROR`               | float   | ✓ | Reporting odds ratio |
| `ROR025`            | float   | ✓ | Lower 95% CI of ROR |
| `ROR975`            | float   | ✓ | Upper 95% CI of ROR |
| `p-value`           | float   | ✓* | Aliases: `p`, `p_value` |
| `PRR025`            | float   | – | Optional for PRR highlighting |
| `χ^2`               | float   | – | Aliases: `chi2`, `x2` |
| `IC025`             | float   | – | BCPNN information component (lower bound) |

Signal rules (used for ✓ markers):  
ROR: `n11 ≥ 3` & `p-value < 0.05` & `ROR025 > 1` · PRR: `χ^2 > 4` & `PRR025 > 2` · IC: `IC025 > 0`.

---

## B. `figure3_stratified.csv` — Fig.3 (multi‑drug forest)

Same as **A**, plus the following are **required**: `Subgroup` (stratum label) and `drug_of_interest` is used to group sections.

---

## C. `volcano_*.csv` — Fig.4 (per‑drug volcano)

| Column      | Type   | Required | Notes |
|-------------|--------|---------:|------|
| `DB`        | string | ✓ | `FAERS` / `JADER` |
| `Subgroup`  | string | ✓ | Stratum label shown in text |
| `n11`       | int    | ✓ | Target‑drug + AF reports count (used for point size) |
| `ROR`       | float  | ✓ | X uses `lnROR = ln(ROR)` |
| `p-value`   | float or numeric string | ✓ | Y uses `-log10(p)`; scientific notation okay |

The script **drops** rows where `n11 < 3` or any of `ROR`, `p-value` are missing/invalid.

---

## D. `tto_*.csv` — Fig.5 (TTO distribution)

Single column of **positive** TTO values in days. The script auto-detects the 3rd column if unnamed; safest is a header named `tto_days` or `days` with one value per row.

Optional flags: `--ymax` (e.g., `730`), `--binwidth` (default `5`), `--hist-max` (auto if omitted).

---

## E. `figure6_km_source.csv` — Fig.6 (KM curve)

| Column (any one of…) | Role     | Required | Notes |
|----------------------|----------|---------:|------|
| `db`                 | DB       | ✓ | `FAERS`/`JADER` or codes `1`/`2` |
| `prod_ai`/`drug`/`product` | Drug | ✓ | Use standardized generic names |
| `tto`/`days`/`time`/`time_to_onset` | Time (days) | ✓ | Non‑numeric/negative dropped |

The plot draws **four curves**: (`FAERS`/`JADER`) × (`MIRABEGRON`/`SOLIFENACIN`).

---

## F. File encodings and delimiters

- CSVs should be UTF‑8 with comma delimiters and a header row.
- Decimal separator: `.` (dot). Thousands separators should not appear.
- Missing values: empty cells preferred.

If your columns differ slightly, the scripts implement **lenient renaming** for common aliases (see above). If you hit a parsing error, check the exact header strings.