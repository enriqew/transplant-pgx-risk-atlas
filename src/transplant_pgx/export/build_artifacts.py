"""Export gold tables to JSON artifacts for portfolio consumption."""
from __future__ import annotations

import json
import duckdb
from pathlib import Path
from datetime import datetime, timezone


def export_artifacts(db_path: str | None = None) -> None:
    repo_root = Path(__file__).parents[3]
    db_path = db_path or str(repo_root / "data" / "duckdb" / "transplant_pgx.duckdb")
    artifacts_dir = repo_root / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    conn = duckdb.connect(db_path, read_only=True)

    rows = conn.execute("SELECT * FROM gold_transplant_pgx_exposure ORDER BY country_iso3, drug_name, population_code").fetchall()
    columns = [d[0] for d in conn.description]
    data = [dict(zip(columns, row)) for row in rows]

    out = artifacts_dir / "transplant-pgx-exposure.json"
    out.write_text(json.dumps(data, indent=2, default=str))
    print(f"Exported {len(data):,} rows → {out}")

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "0.1.0",
        "artifact_row_counts": {"transplant_pgx_exposure": len(data)},
    }
    (artifacts_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    conn.close()


if __name__ == "__main__":
    export_artifacts()
