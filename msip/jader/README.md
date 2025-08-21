# MSIP — JADER pipeline

This README documents the JADER MSIP nodes used in the manuscript. It reflects the finalized public code and your last pipeline changes (BMI derivation and per‑case drug count) so that others can reproduce Figures 2–6 from the derived CSVs.

## Execution order (conceptual)

1. **j00 — PLID build & merge (MSIP)** → `J_PLID`
   - Merge **DEMO + DRUG + HIST** (DEMO as base; left joins by the JADER identifier).
   - **Python pre‑steps (DEMO)**:
     - Convert **age / height / weight** to numeric (treat strings like “未満” as 0, otherwise extract digits).
     - Add **BMI = weight(kg) / (height(m))²** after a +5 correction applied to height and weight as in your original flow.
   - **Python pre‑step (DRUG)**:
     - Add per‑case **drug count** (服薬数) by counting DRUG rows per identifier and merge back.
2. **j02 — (kept for bookkeeping)** attach final drug count if not done in j00.
3. **j10 / j11 — OAB standardization and AF extract** → `J_OAB_STD`, `J_AF`
4. **j20 — 2×2 counts per drug** → `J_COUNTS2x2`
5. **j30 — Strata base** → `J_STRATA_BASE`
6. **j40 — PLID time-series (start_date × event_date)** → `J_PLID_TS`
7. **j45 — Time-to-onset (TTO, days)** → `J_TTO`
8. **j50 — Primary-suspected–only PLID (scenario)** → `J_PLID_PS`
9. **j60 — Exclude prior AF PLID (scenario)** → `J_PLID_NO_AF`

## Public exports consumed by `raw_code/plots`

- **Figure 2 (forest)**: from `J_COUNTS2x2` → `data/derived/figure2_source.csv`
- **Figure 3 (stratified forest)**: from `J_STRATA_BASE` joined to per‑drug metrics → `data/derived/figure3_stratified.csv`
- **Figure 4 (volcano)**: per‑drug stratified metrics → `data/derived/volcano_<drug>.csv`
- **Figure 5 (TTO dist)**: per (DB, drug) TTO lists from `J_TTO` → `data/derived/tto_JADER_<drug>.csv`
- **Figure 6 (KM)**: merged TTO (DB + drug) from `J_TTO` → `data/derived/figure6_km_source.csv`

## Conventions

- **ASCII-only headers** in public CSVs (`chi2`, `p_value`) to avoid mojibake.
- Drop strata with **`n11 < 3`** before metrics/plots.
- Volcano y-axis computes **−log10(p)** from numeric p; scientific strings like `5.54E-18` are parsed to float before transform.
- TTO plots may cap the visual y‑axis to **0–730 days** in the main text; the export keeps full values (see S5).

## QA checklist (quick)

- [ ] DEMO numeric fields present: `AGE`, `HEIGHT`, `WEIGHT`, and derived `BMI`.
- [ ] DRUG has per‑identifier **服薬数**.
- [ ] `figure3_stratified.csv` contains `Subgroup`, `DB`, `n11`, `ROR`, `p_value`.
- [ ] TTO CSVs: single numeric column of days; no negative or zero days.

_Generated: 2025‑08‑22 (JST)_
