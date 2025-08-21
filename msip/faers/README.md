# MSIP — FAERS pipeline

This README documents the FAERS MSIP nodes used in the manuscript. It reflects the finalized public code and your last pipeline changes (merge keys, dedup logic, and added features) so that others can reproduce Figures 2–6 from the derived CSVs.

## Execution order (conceptual)

1. **f00 — PLID build & merge (MSIP)** → `F_PLID`
   - Merge **DEMO + DRUG + OUTC + INDI** by `primaryid` (left joins in MSIP; DEMO as base).
   - **Python post-step (DEMO dedup)**: keep, per `caseid`, only the row with the **maximum `caseversion`**.
2. **f02 — Add `number_of_drug` (Python)** → `F_PLID(+ number_of_drug)`
   - Count `drug_seq` per `primaryid`, rename to **`number_of_drug`**, and left-join back to DRUG rows.
3. **f10 / f11 — OAB standardization and AF extract** → `F_OAB_STD`, `F_AF`
4. **f20 — 2×2 counts per drug** → `F_COUNTS2x2`
5. **f30 — Strata base** → `F_STRATA_BASE`
6. **f40 — PLID time-series (start_dt × event_dt)** → `F_PLID_TS`
7. **f45 — Time-to-onset (TTO, days)** → `F_TTO`
8. **f50 — Primary-suspected–only PLID (scenario)** → `F_PLID_PS`
9. **f60 — Exclude prior/indication AF PLID (scenario)** → `F_PLID_NO_AF`

> **Notes**
> - “Primary‑suspected only” and “history/indication exclusion” correspond to sensitivity scenarios used in Supplementary Data S5.

## Public exports consumed by `raw_code/plots`

- **Figure 2 (forest)**: from `F_COUNTS2x2` → `data/derived/figure2_source.csv`
- **Figure 3 (stratified forest)**: from `F_STRATA_BASE` joined to per‑drug metrics → `data/derived/figure3_stratified.csv`
- **Figure 4 (volcano)**: per‑drug stratified metrics → `data/derived/volcano_<drug>.csv`
- **Figure 5 (TTO dist)**: per (DB, drug) TTO lists from `F_TTO` → `data/derived/tto_FAERS_<drug>.csv`
- **Figure 6 (KM)**: merged TTO (DB + drug) from `F_TTO` → `data/derived/figure6_km_source.csv`

## Conventions

- **ASCII-only headers** in public CSVs (`chi2`, `p_value`) to avoid mojibake.
- Drop strata with **`n11 < 3`** before metrics/plots.
- Volcano y-axis computes **−log10(p)** from numeric p; scientific strings like `5.54E-18` are parsed to float before transform.
- TTO plots may cap the visual y‑axis to **0–730 days** in the main text; the export keeps full values (see S5).

## QA checklist (quick)

- [ ] After `f00`: one row per (`caseid`, max `caseversion`).
- [ ] After `f02`: `number_of_drug` present and non‑null for DRUG rows.
- [ ] `figure2_source.csv`: includes `ROR`, `ROR025`, `ROR975`, `p_value`, `chi2`, `IC025`, `DB`, `drug_of_interest`, `n11`.
- [ ] Volcano CSVs: include `Subgroup`, `DB`, `n11`, `ROR`, `p_value`.
- [ ] TTO CSVs: single numeric column of days; no negative or zero days.

_Generated: 2025‑08‑22 (JST)_
