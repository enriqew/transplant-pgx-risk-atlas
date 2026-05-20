"""Gold: compute transplant PGx exposure — % recipients expected to need dose adjustment."""
from __future__ import annotations

import duckdb
from pathlib import Path


# Map 1000 Genomes population codes to country ISO3
POPULATION_COUNTRY_MAP = {
    "MXL": "MEX",
    "PEL": "PER",
    "CLM": "COL",
    "PUR": "PRI",
}


def build_gold(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
    CREATE OR REPLACE TABLE gold_transplant_pgx_exposure AS
    WITH latest_transplants AS (
        SELECT
            country_iso3,
            country_name,
            transplants_pmp,
            total_transplants,
            year,
            ROW_NUMBER() OVER (PARTITION BY country_iso3 ORDER BY year DESC) AS rn
        FROM silver_transplant_volumes
    ),
    pgx_by_pop AS (
        SELECT
            population_code,
            drug_name,
            gene_symbol,
            percentage_requiring_change,
            baseline_ceu_percentage,
            delta_vs_baseline,
            classification_strength
        FROM silver_pgx_drug_impact
    )
    SELECT
        lt.country_iso3,
        lt.country_name,
        lt.transplants_pmp,
        lt.total_transplants,
        lt.year AS data_year,
        p.population_code,
        p.drug_name,
        p.gene_symbol,
        p.percentage_requiring_change,
        p.baseline_ceu_percentage,
        p.delta_vs_baseline,
        p.classification_strength,
        -- Exposure = transplant volume × PGx risk rate
        ROUND(lt.total_transplants * p.percentage_requiring_change / 100, 0) AS estimated_recipients_needing_adjustment
    FROM latest_transplants lt
    JOIN pgx_by_pop p
        ON lt.country_iso3 = p.population_code
    WHERE lt.rn = 1
    """)
