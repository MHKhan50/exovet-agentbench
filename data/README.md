# Dataset handling

The NASA Kepler Q1-Q17 DR25 KOI dataset is **not bundled** with this repository. Download it directly from the NASA Exoplanet Archive using:

```bash
python -m exovet_agentbench download --output data/raw/koi_dr25.csv
python -m exovet_agentbench prepare --input data/raw/koi_dr25.csv --output data/processed/koi_prepared.csv
```

The downloader writes a sidecar manifest with the exact query, retrieval timestamp, row count and SHA-256 checksum. Preserve that manifest with every experiment. The archive is periodically updated; a future download may not be byte-identical.

No synthetic astronomy observations are included. Unit tests create temporary in-memory fixtures solely to verify software behaviour; they are not research data and must not be reported as scientific results.
