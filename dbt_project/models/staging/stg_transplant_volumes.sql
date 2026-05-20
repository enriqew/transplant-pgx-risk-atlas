{{ config(materialized='view') }}

SELECT
    country_iso3,
    country_name,
    year::INTEGER AS year,
    total_transplants::INTEGER AS total_transplants,
    transplants_pmp::DOUBLE AS transplants_pmp,
    deceased_donors::INTEGER AS deceased_donors,
    living_donors::INTEGER AS living_donors,
    source
FROM read_json_auto('{{ env_var("TRANSPLANT_RAW_PATH", "../data/raw/transplant_artifacts/*/world-transplants.json") }}')
WHERE transplants_pmp IS NOT NULL
