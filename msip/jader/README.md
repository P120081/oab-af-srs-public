# MSIP — JADER pipeline (polished)

This folder documents the JADER MSIP nodes used in the manuscript. It preserves your original content and adds **QA checklists** and **public-export mapping** for reproducibility.

## Execution order (conceptual)
1. j00 — PLID build → **J_PLID**
2. j02 — Attach drug_count → **J_PLID(+ drug_count)**
3. j10/j11 — OAB standardize (**J_OAB_STD**) and AF extract (**J_AF**)
4. j20 — 2×2 counts per drug → **J_COUNTS2x2**
5. j30 — Strata base → **J_STRATA_BASE**
6. j40 — PLID time-series (start_date × event_date) → **J_PLID_TS**
7. j45 — Compute TTO (days) → **J_TTO**
8. j50 — PS-only PLID (scenario) → **J_PLID_PS**
9. j60 — AF-excluded PLID (scenario) → **J_PLID_NO_AF**

## Public exports (used by `data/derived/`)
- **Figure 2**: from **J_COUNTS2x2** → `data/derived/figure2_source.csv`
- **Figure 3**: join **J_STRATA_BASE** × per-drug counts → `data/derived/figure3_stratified.csv`
- **Figure 4**: per-drug stratified metrics → `data/derived/volcano_<drug>.csv`
- **Figure 5**: per (DB, drug) TTO lists from **J_TTO** → `data/derived/tto_<DB>_<drug>.csv`
- **Figure 6**: merged TTO (DB + drug) from **J_TTO** → `data/derived/figure6_km_source.csv`

## Conventions
- **ASCII-only** public headers (`chi2`, `p_value`) to avoid mojibake.
- **Drop `n11 < 3`** before computing/plotting metrics.
- **No ad-hoc TTO truncation** for supplemental S5; plots may show ≤2 years in the main text for readability.

_Generated 2025-08-21._
