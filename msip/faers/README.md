# MSIP — FAERS pipeline (polished)

This folder documents the FAERS MSIP nodes used in the manuscript. It preserves your original content and adds **QA checklists** and **public-export mapping** for reproducibility.

## Execution order (conceptual)
1. f00 — PLID de-duplication → **F_PLID**
2. f02 — Attach number_of_drug → **F_PLID(+ number_of_drug)**
3. f10/f11 — OAB normalization (**F_OAB_STD**) and AF extract (**F_AF**)
4. f20 — 2×2 counts per drug → **F_COUNTS2x2**
5. f30 — Strata base → **F_STRATA_BASE**
6. f40 — PLID time-series (start_dt × event_dt) → **F_PLID_TS**
7. f45 — Compute TTO (days) → **F_TTO**
8. f50 — PS-only PLID (scenario) → **F_PLID_PS**
9. f60 — AF-excluded PLID (scenario) → **F_PLID_NO_AF**

## Public exports (used by `data/derived/`)
- **Figure 2**: from **F_COUNTS2x2** → `data/derived/figure2_source.csv`
- **Figure 3**: join **F_STRATA_BASE** × per-drug counts → `data/derived/figure3_stratified.csv`
- **Figure 4**: per-drug stratified metrics → `data/derived/volcano_<drug>.csv`
- **Figure 5**: per (DB, drug) TTO lists from **F_TTO** → `data/derived/tto_<DB>_<drug>.csv`
- **Figure 6**: merged TTO (DB + drug) from **F_TTO** → `data/derived/figure6_km_source.csv`

## Conventions
- **ASCII-only** public headers (`chi2`, `p_value`) to avoid mojibake.
- **Drop `n11 < 3`** before computing/plotting metrics.
- **No ad-hoc TTO truncation** for supplemental S5; plots may show ≤2 years in the main text for readability.

_Generated 2025-08-21._
