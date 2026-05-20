{{ config(materialized='view') }}

SELECT
    drug_name,
    gene_symbol,
    population_code,
    population_total::INTEGER AS population_total,
    percentage_requiring_change::DOUBLE AS percentage_requiring_change,
    baseline_ceu_percentage::DOUBLE AS baseline_ceu_percentage,
    delta_vs_baseline::DOUBLE AS delta_vs_baseline,
    classification_strength
FROM read_json_auto('{{ env_var("PGX_RAW_PATH", "../data/raw/pgx_artifacts/*/drug_impact_summary.json") }}')
WHERE drug_name IN ('tacrolimus', 'azathioprine')
