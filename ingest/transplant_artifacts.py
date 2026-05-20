"""Download transplant-atlas artifacts from GitHub."""
from __future__ import annotations

from pathlib import Path
import requests
from ._common import snapshot_dir, sha256_file, write_meta

BASE_URL = "https://raw.githubusercontent.com/enriqew/transplant-atlas/main/data/exports"
ARTIFACTS = [
    "world-transplants.json",
    "mexico-transplants.json",
    "meta.json",
]


def ingest(snapshot_date: str | None = None) -> None:
    repo_root = Path(__file__).parents[1]
    out_dir = snapshot_dir(repo_root, "transplant_artifacts", snapshot_date)
    files_meta = []

    for name in ARTIFACTS:
        url = f"{BASE_URL}/{name}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        dest = out_dir / name
        dest.write_bytes(resp.content)
        files_meta.append({
            "name": name,
            "url": url,
            "sha256": sha256_file(dest),
            "bytes": dest.stat().st_size,
        })
        print(f"  {name}: {dest.stat().st_size:,} bytes")

    write_meta(out_dir, "transplant_artifacts", files_meta)
    print(f"transplant_artifacts snapshot: {out_dir}")


if __name__ == "__main__":
    ingest()
