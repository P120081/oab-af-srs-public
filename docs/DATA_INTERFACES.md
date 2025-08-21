# Data Interfaces (Final)

This document defines the **contract between the derived CSV files** and the **public plotting/analysis scripts**.
It reflects the latest changes:
- JADER: DEMO numericization (+BMI), DRUG with **concomitant medication count**.
- FAERS: DEMO **de-duplication by `caseid` → max `caseversion`**, DRUG with **`number_of_drug`**.
- Volcano: accepts **`p-value`, `p_value`, _or_ `p`**, including scientific notation (e.g., `5.54E-18`). Values are coerced to float and floored internally.
- Figure 5 (TTO): vertical axis capped at **730 days** (2 years) to match the manuscript figure.

---

## 1) Column naming conventions (ASCII for public CSV)
Public-facing CSVs should prefer ASCII headers. The code normalizes these automatically:
- *p-value*: any of `p-value`, `p_value`, or `p` → normalized internally to `p`.
- *chi-square*: any of `χ^2`, `chi2`, `Chi2` → normalized internally to `chi2`.
- Drug label columns: `drug_of_interest` (Fig.2), `Subgroup` (Fig.3/4).

## 2) Expected inputs (data/derived/*.csv)

### a. Figure 2 — Primary screening
**File**: `data/derived/figure2_source.csv`  
**Required columns**:
```
DB, drug_of_interest, n11, ROR, ROR025, ROR975,
p-value|p_value|p, PRR025 (optional), χ^2|chi2 (optional), IC025 (optional)
```
Used by: `raw_code/plots/forest_plot.py`

### b. Figure 3 — Stratified (per drug × DB)
**File**: `data/derived/figure3_stratified.csv`  
**Required columns**:
```
DB, drug_of_interest, Subgroup, n11, ROR, ROR025, ROR975, p-value|p_value|p,
PRR025 (optional), χ^2|chi2 (optional), IC025 (optional)
```
Used by: `raw_code/plots/forest_plot_multidrug.py`

### c. Figure 4 — Volcano (per drug)
**Files**:  
- `data/derived/volcano_mirabegron.csv`  
- `data/derived/volcano_solifenacin.csv`  
**Required columns**:
```
DB, Subgroup, n11, ROR, p-value|p_value|p
```
Used by: `raw_code/plots/volcano_plot.py`  
Notes: p may be scientific notation; script computes `lnROR` and `-log10(p)`.

### d. Figure 5 — TTO distribution + histogram + boxplot
**Files** (one column = time-to-onset days column is the **3rd** column):
- `data/derived/tto_FAERS_mirabegron.csv`
- `data/derived/tto_JADER_solifenacin.csv`
The script reads **3rd column** as TTO (float), and renders with **y-range [0, 730]** by default.  
Used by: `raw_code/plots/figure5_tto_distribution.py`

### e. Figure 6 — KM curves (raw)
**File**: `data/derived/figure6_km_source.csv`  
**Typical columns**:
```
time (days), event (0/1), group (label), ... 
```
Used by: `raw_code/plots/kaplan_meier_raw.py`

---

## 3) Outputs (docs/*.png|.tif)
Scripts save to `docs/`. For Fig.2, both PNG and TIFF are emitted; others PNG (and optional TIFF when supported).

---

## 4) Upstream (MSIP) notes

### JADER
- DEMO: numericize **年齢/身長/体重 → AGE/HEIGHT/WEIGHT** and compute **BMI** (`raw_code/jader/00_demo_numeric_bmi.py`).
- DRUG: attach per-識別番号 **服薬数** (`raw_code/jader/02_drug_attach_count.py`).
- Merge in MSIP: **DEMO (anchor) ← DRUG ← HIST** (left joins).

### FAERS
- DEMO: de-duplicate by `caseid` with max `caseversion` (`raw_code/faers/00_demo_dedup.py`).
- DRUG: attach per-`primaryid` **number_of_drug** (`raw_code/faers/02_drug_attach_count.py`).
- Merge in MSIP: **DEMO (anchor) ← DRUG ← OUTC ← INDI** on `primaryid`.

---

## 5) Validation checklist
- [ ] Column names follow above contract (ASCII where public).
- [ ] No `n11 < 3` rows in published CSVs used for screening plots.
- [ ] Volcano inputs have p-values parsable as float (including scientific notation).
- [ ] TTO CSV 3rd column is strictly positive.
- [ ] Re-run `raw_code/analysis/make_figures.py` without errors.
