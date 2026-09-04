# transplant-pgx-risk-atlas

**Live demo:** [eredonda.com/projects/transplant-pgx-risk-atlas](https://eredonda.com/projects/transplant-pgx-risk-atlas?utm_source=github&utm_medium=referral)

Integration layer that crosses global transplant volumes with pharmacogenomic risk profiles for immunosuppressants, quantifying what percentage of LATAM transplant recipients would require tacrolimus or azathioprine dose adjustment under standard European-derived CPIC guidelines.

## What This Repo Does

This repository contains the **integration pipeline** — it joins outputs from upstream domain-specific pipelines into a unified risk estimate. It does NOT re-run raw data ingestion; it consumes curated artifacts from the repos listed below.

## Upstream Data Sources

| Pipeline repo | Data produced | Role in this pipeline |
|---|---|---|
| `transplant-atlas` | `world-transplants.json`, `mexico-transplants.json` | Transplant volumes by country/year (IRODaT/GODT) |
| `transplant-waitlist-atlas` | `world-waitlist.json`, `us-fate-distribution.json` | Waitlist size and fate distribution by organ |
| `pgx-latam-atlas` | `drug_impact_summary.json`, `actionability_ranking.json`, `allele_frequencies.json` | Pharmacogenomic risk per drug-gene-population pair |

Data artifacts consumed by this integration layer are committed directly into the portfolio repo (`data-dive-design-hub/src/data/`). To refresh, pull updated JSON from the upstream repos and copy them over.

## Architecture (Medallion)

```
bronze/
  raw_irodat/          ← IRODaT country-year transplant counts (from transplant-atlas)
  raw_1kg_phase3/      ← 1000 Genomes Phase 3 VCF/diplotype tables (from pgx-latam-atlas)
  raw_cpic/            ← CPIC guideline recommendation tables

silver/
  transplant_volumes/  ← Cleaned, normalised transplant volumes with ISO3 keys
  pgx_risk_by_pop/     ← Per-population risk estimates for CYP3A5, TPMT, NUDT15
  cpic_thresholds/     ← Actionable thresholds per drug-gene pair

gold/
  transplant_pgx_risk/ ← Joined table: transplant_volume × pgx_risk_pct × population_match
  drug_impact_summary/ ← % requiring dose change per drug × gene × population
  actionability_ranking/ ← Ranked divergences vs CEU baseline for immunosuppressants
```

## Planned Stack

| Tool | Purpose |
|---|---|
| Python 3.11+ | Orchestration, data wrangling, CPIC table parsing |
| DuckDB | Local medallion transformations (bronze → silver → gold) |
| dbt-duckdb | SQL models for silver/gold layer; lineage documentation |
| AWS Step Functions | Pipeline orchestration for scheduled refreshes |
| AWS Glue + Athena | Optional: cloud execution of bronze ingestion jobs |
| Apache Iceberg | Table format for gold-layer outputs (future) |

## Key Drugs and Genes

- **Tacrolimus / CYP3A5** — calcineurin inhibitor used in kidney, liver, and heart transplants. CYP3A5 Extensive Metabolizers (*1 carriers) require significantly higher doses; CYP3A5*1 frequency varies substantially across LATAM populations vs European baseline.
- **Azathioprine / TPMT** — thiopurine immunosuppressant. TPMT Poor Metabolizers face severe myelotoxicity at standard doses.
- **Azathioprine / NUDT15** — NUDT15*3 (rs116855232) is markedly more prevalent in East Asian and Latin American populations. Standard CPIC tables calibrated on European data systematically underestimate NUDT15-driven risk in LATAM recipients.

## Notes

- Data artifacts consumed from upstream pipeline repos; this repo contains the integration layer only.
- Source code for raw ingestion lives in `transplant-atlas`, `transplant-waitlist-atlas`, and `pgx-latam-atlas` respectively.
- The React visualisation component (`TransplantPgxRiskAtlasPage.tsx`) and processed JSON outputs live in the portfolio repo `data-dive-design-hub`.

## Methodological limits

The cohorts are not the patients. 1000 Genomes panels (MXL, PEL, CLM, PUR
against CEU) are population samples of genetic ancestry, not transplant
recipients, and IRODaT reports no recipient ancestry. The country-to-cohort
mapping in `POPULATION_COUNTRY_MAP` is a geographic proxy: PEL stands in for
Peru rather than describing Peru's actual transplant population. What comes out
is a population-level, ecological estimate of expected dosing burden, not a
measurement of any patient group.

Cohort sizes are 61 to 113 individuals, so a percentage point is a handful of
people. None of this is clinical guidance; CPIC guidelines are the clinical
reference.

## Data & licenses

- **IRODaT** and **GODT**: used with attribution, aggregated rows only.
- **1000 Genomes Project** Phase 3: open access. **PharmGKB**: CC BY-SA 4.0.
  **CPIC**: open-access guidelines.
- Code: MIT, see [LICENSE](LICENSE).
