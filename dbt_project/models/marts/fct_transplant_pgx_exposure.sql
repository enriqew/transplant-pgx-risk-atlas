{{ config(materialized='table') }}

WITH latest_transplants AS (
    SELECT
        country_iso3,
        country_name,
        transplants_pmp,
        total_transplants,
        year,
        ROW_NUMBER() OVER (PARTITION BY country_iso3 ORDER BY year DESC) AS rn
    FROM {{ ref('stg_transplant_volumes') }}
),
pop_map AS (
    SELECT * FROM (VALUES
        ('MXL', 'MEX'),
        ('PEL', 'PER'),
        ('CLM', 'COL'),
        ('PUR', 'PRI')
    ) AS t(population_code, country_iso3)
)
SELECT
    lt.country_iso3,
    lt.country_name,
    lt.transplants_pmp,
    lt.total_transplants,
    lt.year AS data_year,
    d.population_code,
    d.drug_name,
    d.gene_symbol,
    d.percentage_requiring_change,
    d.baseline_ceu_percentage,
    d.delta_vs_baseline,
    d.classification_strength,
    ROUND(lt.total_transplants * d.percentage_requiring_change / 100, 0) AS estimated_recipients_needing_adjustment
FROM latest_transplants lt
JOIN pop_map pm ON lt.country_iso3 = pm.country_iso3
JOIN {{ ref('stg_pgx_drug_impact') }} d ON d.population_code = pm.population_code
WHERE lt.rn = 1
