"""Smoke tests for silver/gold transformations."""
import pytest
import duckdb


@pytest.fixture
def conn():
    return duckdb.connect(":memory:")


def test_silver_views_accept_empty_input(conn):
    conn.execute("""
    CREATE TABLE t (
        country_iso3 VARCHAR, country_name VARCHAR, year INTEGER,
        total_transplants INTEGER, transplants_pmp DOUBLE,
        deceased_donors INTEGER, living_donors INTEGER, source VARCHAR
    )
    """)
    conn.execute("CREATE OR REPLACE VIEW silver_transplant_volumes AS SELECT * FROM t")
    result = conn.execute("SELECT count(*) FROM silver_transplant_volumes").fetchone()
    assert result[0] == 0


def test_population_map_completeness():
    from src.transplant_pgx.transformations.gold_exposure import POPULATION_COUNTRY_MAP
    expected = {"MXL", "PEL", "CLM", "PUR"}
    assert set(POPULATION_COUNTRY_MAP.keys()) == expected
