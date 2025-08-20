# JADER — OAB standardize
**Purpose**: Normalize OAB generic names (Japanese → ASCII tokens).
**Input**: DRUG(一般名), mapping in raw_code/jader/01_oab_standardize.py
**Operation (MSIP)**: Map to {oxybutynin,…,vibegron}; produce (j_id, drug_of_interest).
**Output (logical)**: J_OAB_STD(j_id, drug_of_interest)
**Downstream**: j20_counts2x2.md, j40_plid_timeseries.md
-- J10_OAB_STD (JADER) 窶・normalize OAB generics to ASCII tokens
-- Input: DRUG("隴伜挨逡ｪ蜿ｷ", "蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・)
-- Output: OAB_STD_J(j_id, drug_of_interest)

WITH DRUG_STD AS (
  SELECT
    d."隴伜挨逡ｪ蜿ｷ" AS j_id,
    d."蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・ AS jp_generic
  FROM DRUG d
  WHERE d."隴伜挨逡ｪ蜿ｷ" IS NOT NULL
    AND d."蛹ｻ阮ｬ蜩・ｼ井ｸ闊ｬ蜷搾ｼ・ IS NOT NULL
),
OAB_STD_J AS (
  SELECT DISTINCT
    j_id,
    CASE
      WHEN jp_generic LIKE '%繧ｽ繝ｪ繝輔ぉ繝翫す繝ｳ%'   THEN 'solifenacin'
      WHEN jp_generic LIKE '%繝溘Λ繝吶げ繝ｭ繝ｳ%'     THEN 'mirabegron'
      WHEN jp_generic LIKE '%繧ｪ繧ｭ繧ｷ繝悶メ繝九Φ%'   THEN 'oxybutynin'
      WHEN jp_generic LIKE '%繝励Ο繝斐・繝ｪ繝ｳ%'     THEN 'propiverine'
      WHEN jp_generic LIKE '%繧､繝溘ム繝輔ぉ繝翫す繝ｳ%' THEN 'imidafenacin'
      WHEN jp_generic LIKE '%繝医Ν繝・Ο繧ｸ繝ｳ%'     THEN 'tolterodine'
      WHEN jp_generic LIKE '%繝輔ぉ繧ｽ繝・Ο繧ｸ繝ｳ%'   THEN 'fesoterodine'
      WHEN jp_generic LIKE '%繝薙・繧ｰ繝ｭ繝ｳ%'       THEN 'vibegron'
      ELSE NULL
    END AS drug_of_interest
  FROM DRUG_STD
)
SELECT *
FROM OAB_STD_J
WHERE drug_of_interest IS NOT NULL;

