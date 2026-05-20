"""Silver: join transplant volumes with PGx drug impact data."""
from __future__ import annotations

import duckdb
from pathlib import Path


TRANSPLANT_DRUGS = {"tacrolimus", "azathioprine"}
TRANSPLANT_ORGANS = {"kidney", "liver", "heart"}


def build_silver(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
    CREATE OR REPLACE VIEW silver_transplant_volumes AS
    SELECT
        country_iso3,
        country_name,
        year,
        total_transplants,
        transplants_pmp,
        deceased_donors,
        living_donors,
        source
    FROM read_json_auto('../data/raw/transplant_artifacts/*/world-transplants.json')
    WHERE transplants_pmp IS NOT NULL
    """)

    conn.execute("""
    CREATE OR REPLACE VIEW silver_pgx_drug_impact AS
    SELECT
        drug_name,
        gene_symbol,
        population_code,
        population_total,
        individuals_requiring_change,
        percentage_requiring_change,
        baseline_ceu_percentage,
        delta_vs_baseline,
        classification_strength
    FROM read_json_auto('../data/raw/pgx_artifacts/*/drug_impact_summary.json')
    WHERE drug_name IN ('tacrolimus', 'azathioprine')
    """)
